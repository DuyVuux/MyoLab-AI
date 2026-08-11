
"""DAY27 motion-artifact / low-frequency contamination weak-label indicator.

Extracts evidence only. It never high-pass filters, baseline-subtracts, resamples,
or rewrites raw samples to resemble healthy physiology.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import numpy as np
from semg_core.qc_windowing import WindowIdentity

class MotionArtifactDetectorError(ValueError):
    pass

@dataclass(frozen=True)
class MotionArtifactConfig:
    config_version: str = "0.1.0"
    rule_version: str = "0.1.0"
    registry_version: str = "0.1"
    low_band_high_hz: float = 15.0
    total_band_high_hz: float = 450.0
    warning_low_ratio: float = 0.22
    high_low_ratio: float = 0.45
    drift_warning_normalized: float = 0.20
    transient_warning_z: float = 6.0
    min_samples: int = 64

    def __post_init__(self) -> None:
        if not 0 < self.low_band_high_hz < self.total_band_high_hz:
            raise MotionArtifactDetectorError("invalid frequency bands")
        if self.warning_low_ratio < 0 or self.high_low_ratio < self.warning_low_ratio:
            raise MotionArtifactDetectorError("invalid low-frequency thresholds")
        if self.min_samples < 16:
            raise MotionArtifactDetectorError("min_samples too small")


def _lf_output(*, lf_id: str, reason_code: str, label_candidate: str, severity: str, supportability: str, evidence_strength: str, window: WindowIdentity, registry_version: str, rule_version: str, config_version: str, evidence_types: tuple[str, ...], extra_refs: tuple[str, ...] = ()) -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "lf_id": lf_id,
        "lf_version": rule_version,
        "reason_code": reason_code,
        "label_candidate": label_candidate,
        "evidence_type": list(evidence_types),
        "severity": severity,
        "qc_supportability": supportability,
        "evidence_strength": evidence_strength,
        "evidence_refs": [window.window_id, *extra_refs],
        "ground_truth_claim": False,
        "expert_label_claim": False,
        "provenance": {
            "registry_version": registry_version,
            "rule_version": rule_version,
            "config_version": config_version,
        },
    }

def _features(core: np.ndarray, fs: float, config: MotionArtifactConfig) -> tuple[float, float, float]:
    x = core.astype(float, copy=False)
    centered = x - float(np.median(x))
    taper = np.hanning(x.size)
    spec = np.fft.rfft(centered * taper)
    power = np.abs(spec) ** 2
    freqs = np.fft.rfftfreq(x.size, d=1.0 / fs)
    high = min(config.total_band_high_hz, fs / 2.0)
    total_mask = (freqs > 0) & (freqs <= high)
    low_mask = (freqs > 0) & (freqs <= min(config.low_band_high_hz, high))
    total = float(np.sum(power[total_mask]))
    low_ratio = float(np.sum(power[low_mask])) / total if total > 0 else 0.0
    t = np.arange(x.size, dtype=float) / fs
    slope = float(np.polyfit(t, x, 1)[0]) if x.size >= 2 else 0.0
    robust_scale = float(np.median(np.abs(x - np.median(x)))) * 1.4826
    robust_scale = max(robust_scale, 1e-12)
    drift_norm = abs(slope) * (x.size / fs) / robust_scale
    diffs = np.diff(x)
    transient_z = float(np.max(np.abs(diffs))) / robust_scale if diffs.size else 0.0
    return low_ratio, drift_norm, transient_z

def evaluate_motion_artifact(signal_array: np.ndarray, window: WindowIdentity, config: MotionArtifactConfig = MotionArtifactConfig()) -> dict[str, Any]:
    values = np.asarray(signal_array)
    if values.ndim != 1:
        raise MotionArtifactDetectorError("motion-artifact detector expects one channel")
    if window.end_sample_exclusive > values.shape[0]:
        raise MotionArtifactDetectorError("WindowIdentity exceeds raw channel length")
    core = values[window.start_sample:window.end_sample_exclusive]
    if core.size < config.min_samples or not np.all(np.isfinite(core)):
        return _lf_output(lf_id="LF_MOTION_ARTIFACT", reason_code="INSUFFICIENT_QC_EVIDENCE", label_candidate="ABSTAIN", severity="UNKNOWN", supportability="NOT_EVALUATED", evidence_strength="UNKNOWN", window=window, registry_version=config.registry_version, rule_version=config.rule_version, config_version=config.config_version, evidence_types=("LOW_FREQUENCY_BAND",))
    low_ratio, drift_norm, transient_z = _features(core, float(window.sampling_rate_hz), config)
    refs = (f"low-ratio:{low_ratio:.8f}", f"drift-normalized:{drift_norm:.8f}", f"transient-z:{transient_z:.8f}")
    strong = low_ratio >= config.high_low_ratio or drift_norm >= 2.0 * config.drift_warning_normalized or transient_z >= 2.0 * config.transient_warning_z
    ambiguous = low_ratio >= config.warning_low_ratio or drift_norm >= config.drift_warning_normalized or transient_z >= config.transient_warning_z
    if strong:
        return _lf_output(lf_id="LF_MOTION_ARTIFACT", reason_code="MOTION_ARTIFACT_SUSPECTED", label_candidate="WARNING_CANDIDATE", severity="HIGH", supportability="REVIEW_REQUIRED", evidence_strength="MODERATE", window=window, registry_version=config.registry_version, rule_version=config.rule_version, config_version=config.config_version, evidence_types=("LOW_FREQUENCY_BAND", "BASELINE_EXCURSION", "TRANSIENT_ENERGY"), extra_refs=refs)
    if ambiguous:
        return _lf_output(lf_id="LF_MOTION_ARTIFACT", reason_code="MOTION_ARTIFACT_SUSPECTED", label_candidate="WARNING_CANDIDATE", severity="MODERATE", supportability="REVIEW_REQUIRED", evidence_strength="LOW", window=window, registry_version=config.registry_version, rule_version=config.rule_version, config_version=config.config_version, evidence_types=("LOW_FREQUENCY_BAND", "BASELINE_EXCURSION", "TRANSIENT_ENERGY"), extra_refs=refs)
    return _lf_output(lf_id="LF_MOTION_ARTIFACT", reason_code="MOTION_ARTIFACT_NOT_OBSERVED", label_candidate="PASS_CANDIDATE", severity="INFO", supportability="SUPPORTABLE", evidence_strength="MODERATE", window=window, registry_version=config.registry_version, rule_version=config.rule_version, config_version=config.config_version, evidence_types=("LOW_FREQUENCY_BAND", "BASELINE_EXCURSION", "TRANSIENT_ENERGY"), extra_refs=refs)
