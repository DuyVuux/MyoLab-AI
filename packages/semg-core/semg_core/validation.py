"""Pure validation helpers for canonical sEMG arrays and metadata."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np

from .io import NormalizedSignal, PhaseMarker


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    code: str
    message: str
    blocking: bool = True

    def to_dict(self) -> dict[str, str | bool]:
        return {
            "code": self.code,
            "message": self.message,
            "blocking": self.blocking,
        }


def has_blocking_issues(issues: Iterable[ValidationIssue]) -> bool:
    return any(issue.blocking for issue in issues)


def infer_sampling_rate_hz(time_s: np.ndarray) -> float:
    time_axis = np.asarray(time_s, dtype=np.float64)
    if time_axis.ndim != 1 or time_axis.size < 2:
        raise ValueError("At least two timestamps are required")
    dt = np.diff(time_axis)
    median_dt = float(np.median(dt))
    if not math.isfinite(median_dt) or median_dt <= 0:
        raise ValueError("Median sample interval must be positive and finite")
    return 1.0 / median_dt


def relative_timing_jitter(time_s: np.ndarray) -> float:
    time_axis = np.asarray(time_s, dtype=np.float64)
    if time_axis.ndim != 1 or time_axis.size < 3:
        return 0.0
    dt = np.diff(time_axis)
    median_dt = float(np.median(dt))
    if not math.isfinite(median_dt) or median_dt <= 0:
        return float("inf")
    return float(np.median(np.abs(dt - median_dt)) / median_dt)


def validate_time_axis(
    time_s: np.ndarray,
    declared_sampling_rate_hz: float,
    *,
    relative_tolerance: float = 0.01,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    time_axis = np.asarray(time_s, dtype=np.float64)

    if time_axis.ndim != 1:
        return [ValidationIssue("TIME_AXIS_INVALID", "time_s must be one-dimensional")]
    if time_axis.size < 2:
        return [ValidationIssue("TIME_AXIS_INVALID", "At least two timestamps are required")]
    if not np.all(np.isfinite(time_axis)):
        issues.append(ValidationIssue("TIME_VALUE_NONFINITE", "All timestamps must be finite"))
        return issues

    dt = np.diff(time_axis)
    if np.any(dt <= 0):
        issues.append(
            ValidationIssue(
                "TIME_NOT_MONOTONIC",
                "Timestamps must be strictly increasing",
            )
        )
        return issues

    try:
        declared_fs = float(declared_sampling_rate_hz)
    except (TypeError, ValueError):
        declared_fs = float("nan")
    if not math.isfinite(declared_fs) or declared_fs <= 0:
        issues.append(
            ValidationIssue(
                "SAMPLING_RATE_INVALID",
                "Declared sampling rate must be positive and finite",
            )
        )
        return issues

    inferred_fs = infer_sampling_rate_hz(time_axis)
    relative_error = abs(inferred_fs - declared_fs) / declared_fs
    if relative_error > relative_tolerance:
        issues.append(
            ValidationIssue(
                "SAMPLING_RATE_MISMATCH",
                (
                    f"Inferred Fs={inferred_fs:.9g} Hz differs from "
                    f"declared Fs={declared_fs:.9g} Hz; "
                    f"relative_error={relative_error:.6g}"
                ),
            )
        )
    return issues


def validate_phase_markers(
    phase_markers: Iterable[PhaseMarker],
    *,
    recording_start_s: float,
    recording_end_exclusive_s: float,
    tolerance_s: float = 1e-9,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    markers = list(phase_markers)
    seen: set[str] = set()

    for marker in markers:
        if marker.phase_id in seen:
            issues.append(
                ValidationIssue(
                    "PHASE_MARKER_DUPLICATE",
                    f"Duplicate phase marker: {marker.phase_id}",
                )
            )
        seen.add(marker.phase_id)

        values = (marker.start_s, marker.end_s)
        if not all(math.isfinite(float(value)) for value in values):
            issues.append(
                ValidationIssue(
                    "PHASE_MARKER_INVALID",
                    f"Phase {marker.phase_id} contains non-finite boundaries",
                )
            )
            continue
        if marker.end_s <= marker.start_s:
            issues.append(
                ValidationIssue(
                    "PHASE_MARKER_INVALID",
                    f"Phase {marker.phase_id} must have end_s > start_s",
                )
            )
        if marker.start_s < recording_start_s - tolerance_s:
            issues.append(
                ValidationIssue(
                    "PHASE_MARKER_OUT_OF_RANGE",
                    f"Phase {marker.phase_id} starts before the recording",
                )
            )
        if marker.end_s > recording_end_exclusive_s + tolerance_s:
            issues.append(
                ValidationIssue(
                    "PHASE_MARKER_OUT_OF_RANGE",
                    f"Phase {marker.phase_id} ends after the recording span",
                )
            )

    ordered = sorted(markers, key=lambda item: (item.start_s, item.end_s))
    for left, right in zip(ordered, ordered[1:]):
        if right.start_s < left.end_s - tolerance_s:
            issues.append(
                ValidationIssue(
                    "PHASE_MARKER_OVERLAP",
                    f"Phases {left.phase_id} and {right.phase_id} overlap",
                    blocking=False,
                )
            )
    return issues


def validate_normalized_signal(signal: NormalizedSignal) -> list[ValidationIssue]:
    issues = validate_time_axis(signal.time_s, signal.sampling_rate_hz)

    if signal.sample_count == 0:
        issues.append(ValidationIssue("NO_SAMPLES", "Normalized signal has no samples"))
    if signal.channel_count == 0:
        issues.append(
            ValidationIssue("NO_USABLE_SIGNAL_CHANNEL", "At least one channel is required")
        )

    for channel_id, channel in signal.channels.items():
        if channel.sample_count != signal.sample_count:
            issues.append(
                ValidationIssue(
                    "CHANNEL_LENGTH_MISMATCH",
                    (
                        f"Channel {channel_id} has {channel.sample_count} samples; "
                        f"time axis has {signal.sample_count}"
                    ),
                )
            )
        if channel.canonical_unit != "uV":
            issues.append(
                ValidationIssue(
                    "CANONICAL_UNIT_INVALID",
                    f"Channel {channel_id} canonical unit must be uV",
                )
            )
        if channel.sample_count and channel.finite_ratio == 0.0:
            issues.append(
                ValidationIssue(
                    "NO_USABLE_SIGNAL_CHANNEL",
                    f"Channel {channel_id} contains no finite samples",
                )
            )
        elif channel.finite_ratio < 1.0:
            issues.append(
                ValidationIssue(
                    "NONFINITE_VALUES_PRESENT",
                    (
                        f"Channel {channel_id} finite ratio is "
                        f"{channel.finite_ratio:.6f}; downstream QC must decide usability"
                    ),
                    blocking=False,
                )
            )

    recording_start = float(signal.time_s[0]) if signal.sample_count else 0.0
    recording_end_exclusive = recording_start + signal.record_span_s
    issues.extend(
        validate_phase_markers(
            signal.phase_markers,
            recording_start_s=recording_start,
            recording_end_exclusive_s=recording_end_exclusive,
            tolerance_s=max(1e-9, 0.25 / signal.sampling_rate_hz),
        )
    )
    return issues
