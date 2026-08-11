"""DAY26 power-line interference weak-label indicator.

Measures spectral evidence on DAY22 windows without notch filtering, resampling,
or autonomous session blocking. Power-line evidence is not equivalent to unusable signal.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import numpy as np
from semg_core.qc_windowing import WindowIdentity


class PowerlineDetectorError(ValueError):
    pass


@dataclass(frozen=True)
class PowerlineConfig:
    config_version: str = "0.1.0"
    rule_version: str = "0.1.0"
    registry_version: str = "0.1"
    mains_frequency_hz: float | None = None
    site_config_status: str = "NOT_VERIFIED"
    total_band_low_hz: float = 20.0
    total_band_high_hz: float = 450.0
    line_half_width_hz: float = 3.0
    harmonics: tuple[int, ...] = (1, 2, 3)
    warning_ratio: float = 0.08
    high_ratio: float = 0.20
    min_samples: int = 64

    def __post_init__(self) -> None:
        if self.site_config_status not in {"VERIFIED", "NOT_VERIFIED", "UNKNOWN"}:
            raise PowerlineDetectorError("invalid site_config_status")
        if self.site_config_status == "VERIFIED" and self.mains_frequency_hz not in {50.0, 60.0}:
            raise PowerlineDetectorError("verified mains frequency must be 50 or 60 Hz")
        if self.warning_ratio < 0 or self.high_ratio < self.warning_ratio:
            raise PowerlineDetectorError("invalid ratio thresholds")
        if self.min_samples < 16:
            raise PowerlineDetectorError("min_samples too small")


def _lf(
    window: WindowIdentity,
    config: PowerlineConfig,
    *,
    reason: str,
    candidate: str,
    severity: str,
    supportability: str,
    strength: str,
    evidence_types: tuple[str, ...],
    extra_refs: tuple[str, ...] = (),
) -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "lf_id": "LF_POWERLINE",
        "lf_version": config.rule_version,
        "reason_code": reason,
        "label_candidate": candidate,
        "evidence_type": list(evidence_types),
        "severity": severity,
        "qc_supportability": supportability,
        "evidence_strength": strength,
        "evidence_refs": [window.window_id, *extra_refs],
        "ground_truth_claim": False,
        "expert_label_claim": False,
        "provenance": {
            "registry_version": config.registry_version,
            "rule_version": config.rule_version,
            "config_version": config.config_version,
        },
    }


def _band_power(freqs: np.ndarray, psd: np.ndarray, low: float, high: float) -> float:
    mask = (freqs >= low) & (freqs <= high)
    return float(np.sum(psd[mask]))


def evaluate_powerline(
    signal_array: np.ndarray, window: WindowIdentity, config: PowerlineConfig = PowerlineConfig()
) -> dict[str, Any]:
    values = np.asarray(signal_array)
    if values.ndim != 1:
        raise PowerlineDetectorError("power-line detector expects one channel")
    if window.end_sample_exclusive > values.shape[0]:
        raise PowerlineDetectorError("WindowIdentity exceeds raw channel length")
    core = values[window.start_sample:window.end_sample_exclusive]
    if core.size < config.min_samples or not np.all(np.isfinite(core)):
        return _lf(
            window,
            config,
            reason="INSUFFICIENT_QC_EVIDENCE",
            candidate="ABSTAIN",
            severity="UNKNOWN",
            supportability="NOT_EVALUATED",
            strength="UNKNOWN",
            evidence_types=("SPECTRAL_DENSITY",),
        )
    if config.site_config_status != "VERIFIED" or config.mains_frequency_hz is None:
        return _lf(
            window,
            config,
            reason="POWERLINE_SITE_FREQUENCY_NOT_VERIFIED",
            candidate="ABSTAIN",
            severity="UNKNOWN",
            supportability="NOT_EVALUATED",
            strength="UNKNOWN",
            evidence_types=("SPECTRAL_DENSITY",),
        )
    fs = float(window.sampling_rate_hz)
    if fs <= 2.0 * config.total_band_low_hz:
        return _lf(
            window,
            config,
            reason="INSUFFICIENT_QC_EVIDENCE",
            candidate="ABSTAIN",
            severity="UNKNOWN",
            supportability="NOT_EVALUATED",
            strength="UNKNOWN",
            evidence_types=("SPECTRAL_DENSITY",),
        )
    x = core.astype(float, copy=False)
    x = x - float(np.mean(x))
    taper = np.hanning(x.size)
    spec = np.fft.rfft(x * taper)
    psd = (np.abs(spec) ** 2) / max(float(np.sum(taper ** 2)) * fs, 1e-30)
    freqs = np.fft.rfftfreq(x.size, d=1.0 / fs)
    high = min(config.total_band_high_hz, fs / 2.0)
    total = _band_power(freqs, psd, config.total_band_low_hz, high)
    if total <= 0:
        return _lf(
            window,
            config,
            reason="INSUFFICIENT_QC_EVIDENCE",
            candidate="ABSTAIN",
            severity="UNKNOWN",
            supportability="NOT_EVALUATED",
            strength="UNKNOWN",
            evidence_types=("SPECTRAL_DENSITY",),
        )
    line = 0.0
    for harmonic in config.harmonics:
        target = config.mains_frequency_hz * harmonic
        if target >= high:
            continue
        line += _band_power(freqs, psd, target - config.line_half_width_hz, target + config.line_half_width_hz)
    ratio = line / total
    metric_ref = f"powerline-ratio:{ratio:.8f}"
    if ratio >= config.high_ratio:
        return _lf(
            window,
            config,
            reason="POWERLINE_INTERFERENCE_SUSPECTED",
            candidate="WARNING_CANDIDATE",
            severity="HIGH",
            supportability="REVIEW_REQUIRED",
            strength="HIGH",
            evidence_types=("SPECTRAL_DENSITY", "BAND_POWER_RATIO"),
            extra_refs=(metric_ref,),
        )
    if ratio >= config.warning_ratio:
        return _lf(
            window,
            config,
            reason="POWERLINE_INTERFERENCE_SUSPECTED",
            candidate="WARNING_CANDIDATE",
            severity="MODERATE",
            supportability="REVIEW_REQUIRED",
            strength="MODERATE",
            evidence_types=("SPECTRAL_DENSITY", "BAND_POWER_RATIO"),
            extra_refs=(metric_ref,),
        )
    return _lf(
        window,
        config,
        reason="POWERLINE_INTERFERENCE_NOT_OBSERVED",
        candidate="PASS_CANDIDATE",
        severity="INFO",
        supportability="SUPPORTABLE",
        strength="MODERATE",
        evidence_types=("SPECTRAL_DENSITY", "BAND_POWER_RATIO"),
        extra_refs=(metric_ref,),
    )
