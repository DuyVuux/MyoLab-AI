"""DAY42 explicit notch filtering with preserved pre-notch evidence."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Any, Mapping

import numpy as np
from scipy import signal


class NotchError(ValueError):
    """Base class for notch processing failures."""


class NotchConfigurationError(NotchError):
    """Raised when notch configuration is incomplete or contradictory."""


@dataclass(frozen=True)
class NotchSpec:
    enabled: bool
    mains_frequency_hz: float | None = None
    q_factor: float | None = None
    bandwidth_hz: float | None = None
    harmonics: tuple[int, ...] = (1,)
    phase_mode: str = "ZERO_PHASE"
    version: str = "day42-notch.v0.1.0"

    def validate(self, fs_hz: float) -> None:
        if fs_hz <= 0:
            raise NotchConfigurationError("SAMPLING_RATE_REQUIRED_POSITIVE")
        if not self.enabled:
            if self.mains_frequency_hz is not None:
                raise NotchConfigurationError(
                    "DISABLED_NOTCH_MUST_NOT_CARRY_MAINS"
                )
            return
        if self.mains_frequency_hz is None:
            raise NotchConfigurationError("NO_SILENT_DEFAULT_MAINS_FREQUENCY")
        if not 0 < self.mains_frequency_hz < fs_hz / 2:
            raise NotchConfigurationError("MAINS_FREQUENCY_OUT_OF_RANGE")
        if (self.q_factor is None) == (self.bandwidth_hz is None):
            raise NotchConfigurationError(
                "EXACTLY_ONE_OF_Q_OR_BANDWIDTH_REQUIRED"
            )
        if self.q_factor is not None and self.q_factor <= 0:
            raise NotchConfigurationError("Q_FACTOR_REQUIRED_POSITIVE")
        if self.bandwidth_hz is not None and self.bandwidth_hz <= 0:
            raise NotchConfigurationError("BANDWIDTH_REQUIRED_POSITIVE")
        if not self.harmonics or any(int(item) < 1 for item in self.harmonics):
            raise NotchConfigurationError("INVALID_HARMONICS")
        if self.phase_mode != "ZERO_PHASE":
            raise NotchConfigurationError(
                "DAY42_RESEARCH_NOTCH_REQUIRES_ZERO_PHASE"
            )


@dataclass(frozen=True)
class NotchResult:
    values: np.ndarray
    mask: np.ndarray
    metadata: Mapping[str, Any]


def _hash_array(values: np.ndarray) -> str:
    array = np.ascontiguousarray(values)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode())
    digest.update(str(array.shape).encode())
    digest.update(array.tobytes())
    return digest.hexdigest()


def _spectral_summary(
    values: np.ndarray,
    fs_hz: float,
    target_frequencies: list[float],
) -> dict[str, dict[str, float]]:
    frequencies, powers = signal.periodogram(values, fs=fs_hz, scaling="spectrum")
    summary: dict[str, dict[str, float]] = {}
    for target in target_frequencies:
        index = int(np.argmin(abs(frequencies - target)))
        summary[f"{target:g}Hz"] = {
            "bin_hz": float(frequencies[index]),
            "power": float(powers[index]),
        }
    return summary


def _evidence_ref(summary: Mapping[str, Any]) -> str:
    payload = json.dumps(
        summary,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return "spev_sha256_" + hashlib.sha256(payload).hexdigest()


def _notch_ba(
    frequency_hz: float,
    fs_hz: float,
    q_factor: float | None,
    bandwidth_hz: float | None,
) -> tuple[np.ndarray, np.ndarray]:
    effective_q = q_factor
    if effective_q is None:
        effective_q = frequency_hz / float(bandwidth_hz)
    return signal.iirnotch(frequency_hz, effective_q, fs=fs_hz)


def _valid_segments(valid: np.ndarray):
    indexes = np.flatnonzero(valid)
    if indexes.size == 0:
        return
    start = indexes[0]
    previous = indexes[0]
    for index in indexes[1:]:
        if index != previous + 1:
            yield start, previous + 1
            start = index
        previous = index
    yield start, previous + 1


def apply_notch(
    values: np.ndarray,
    fs_hz: float,
    spec: NotchSpec,
    *,
    mask: np.ndarray | None = None,
    source_window_id: str,
    profile_id: str,
) -> NotchResult:
    signal_values = np.asarray(values, dtype=float)
    spec.validate(fs_hz)
    if signal_values.ndim != 1:
        raise NotchConfigurationError("NOTCH_REQUIRES_1D_SIGNAL")

    if mask is None:
        processing_mask = np.zeros_like(signal_values, dtype=bool)
    else:
        processing_mask = np.asarray(mask, dtype=bool).copy()
    if processing_mask.shape != signal_values.shape:
        raise NotchConfigurationError("MASK_SHAPE_MISMATCH")

    raw_hash = _hash_array(signal_values)
    valid = (~processing_mask) & np.isfinite(signal_values)
    valid_values = signal_values[valid]

    target_frequencies: list[float] = []
    if spec.enabled:
        target_frequencies = [
            float(spec.mains_frequency_hz) * harmonic
            for harmonic in spec.harmonics
            if float(spec.mains_frequency_hz) * harmonic < fs_hz / 2
        ]
    pre_summary = (
        _spectral_summary(valid_values, fs_hz, target_frequencies)
        if target_frequencies and valid_values.size
        else {}
    )
    pre_evidence_ref = _evidence_ref(pre_summary)

    if not spec.enabled:
        output = signal_values.copy()
        post_summary: dict[str, dict[str, float]] = {}
        attenuation_db: dict[str, float] = {}
    else:
        output = signal_values.copy()
        output[processing_mask] = np.nan
        for start, end in _valid_segments(valid):
            segment = output[start:end]
            if len(segment) < 64:
                output[start:end] = np.nan
                continue
            for frequency_hz in target_frequencies:
                numerator, denominator = _notch_ba(
                    frequency_hz,
                    fs_hz,
                    spec.q_factor,
                    spec.bandwidth_hz,
                )
                segment = signal.filtfilt(numerator, denominator, segment)
            output[start:end] = segment
        post_summary = _spectral_summary(
            output[np.isfinite(output)],
            fs_hz,
            target_frequencies,
        )
        attenuation_db = {
            key: float(
                10
                * np.log10(
                    max(pre_summary[key]["power"], 1e-30)
                    / max(post_summary[key]["power"], 1e-30)
                )
            )
            for key in pre_summary
        }

    if _hash_array(signal_values) != raw_hash:
        raise RuntimeError("RAW_MUTATION_DETECTED")

    metadata = {
        "processor": "DAY42_NOTCH",
        "processor_version": spec.version,
        "source_window_id": source_window_id,
        "profile_id": profile_id,
        "config": asdict(spec),
        "input_hash": raw_hash,
        "output_hash": _hash_array(output),
        "pre_notch_spectral_evidence_ref": pre_evidence_ref,
        "pre_notch_spectral_summary": pre_summary,
        "post_notch_spectral_summary": post_summary,
        "attenuation_db": attenuation_db,
        "mains_was_explicit": (
            spec.mains_frequency_hz is not None if spec.enabled else True
        ),
        "mask_preserved": True,
    }
    return NotchResult(output, processing_mask, metadata)
