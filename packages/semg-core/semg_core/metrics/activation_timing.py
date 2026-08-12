"""DAY48 research-only activation-timing eligibility and explicit-threshold estimator."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True, slots=True)
class TimingRequest:
    fs_hz: float
    event_sample: int | None
    sync_status: str
    processing_permission: str
    threshold: float | None
    min_consecutive_samples: int = 5
    filter_delay_samples: float | None = 0.0


@dataclass(frozen=True, slots=True)
class TimingResult:
    status: str
    onset_sample: float | None
    onset_time_s: float | None
    relative_to_event_s: float | None
    reason_codes: tuple[str, ...]


def evaluate_activation_timing(values: np.ndarray, req: TimingRequest) -> TimingResult:
    """Evaluate activation timing with explicit threshold and filter delay correction."""
    reasons: list[str] = []
    x = np.asarray(values, dtype=float)

    if req.processing_permission != "ALLOW_PROFILED_PROCESSING":
        reasons.append("METRIC_NOT_ELIGIBLE")
    if req.event_sample is None:
        reasons.append("EVENT_MARKER_REQUIRED")
    if req.sync_status != "VERIFIED":
        reasons.append("MULTIMODAL_SYNC_NOT_VERIFIED")
    if req.fs_hz <= 0:
        reasons.append("FS_INVALID")
    if req.threshold is None:
        reasons.append("EXPLICIT_THRESHOLD_REQUIRED")
    if req.filter_delay_samples is None:
        reasons.append("FILTER_DELAY_UNKNOWN")
    if req.min_consecutive_samples < 1:
        reasons.append("MIN_CONSECUTIVE_INVALID")
    if x.ndim != 1 or not np.isfinite(x).all():
        reasons.append("SIGNAL_INVALID")

    if reasons:
        return TimingResult("NOT_AVAILABLE", None, None, None, tuple(sorted(set(reasons))))

    above = np.abs(x) >= float(req.threshold)
    run = 0
    idx: int | None = None
    for i, v in enumerate(above):
        run = run + 1 if v else 0
        if run >= req.min_consecutive_samples:
            idx = i - req.min_consecutive_samples + 1
            break

    if idx is None:
        return TimingResult("NOT_AVAILABLE", None, None, None, ("ONSET_NOT_DETECTED",))

    corrected = float(idx) - float(req.filter_delay_samples)
    t = corrected / req.fs_hz
    rel = (corrected - float(req.event_sample)) / req.fs_hz

    return TimingResult("ACTIVATION_TIMING_RESEARCH_ONLY", corrected, t, rel, ())
