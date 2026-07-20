"""Low-frequency motion-artifact warning check."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
import math

from semg_core.io import NormalizedSignal
from semg_core.qc import low_frequency_motion_ratio

from result_models import CheckResult
from checks.common import active_channel_samples, get_nested


def run(
    signal: NormalizedSignal,
    protocol: Mapping[str, Any],
    config: Mapping[str, Any],
) -> CheckResult:
    low_band_raw = get_nested(
        config,
        "signal_heuristics",
        "low_frequency_motion_artifact",
        "low_band_hz",
        default=[0.5, 20.0],
    )
    analysis_band_raw = get_nested(
        config,
        "signal_heuristics",
        "low_frequency_motion_artifact",
        "analysis_band_hz",
        default=[20.0, 400.0],
    )
    low_band = (float(low_band_raw[0]), float(low_band_raw[1]))
    analysis_band = (
        float(analysis_band_raw[0]),
        min(float(analysis_band_raw[1]), signal.sampling_rate_hz / 2.0 * 0.98),
    )
    warning_ratio = float(
        get_nested(
            config,
            "signal_heuristics",
            "low_frequency_motion_artifact",
            "warning_power_ratio",
            default=0.30,
        )
    )
    fail_candidate = float(
        get_nested(
            config,
            "signal_heuristics",
            "low_frequency_motion_artifact",
            "fail_candidate_power_ratio",
            default=0.60,
        )
    )

    channel_details: dict[str, Any] = {}
    maximum_ratio = 0.0
    for channel_id, samples in active_channel_samples(signal, protocol).items():
        result = low_frequency_motion_ratio(
            samples,
            sampling_rate_hz=signal.sampling_rate_hz,
            low_band_hz=low_band,
            analysis_band_hz=analysis_band,
        )
        channel_details[channel_id] = {
            "ratio": result.ratio if math.isfinite(result.ratio) else None,
            "ratio_is_infinite": not math.isfinite(result.ratio),
            "low_band_power": result.numerator_power,
            "analysis_band_power": result.denominator_power,
            "low_band_hz": list(result.numerator_band_hz),
            "analysis_band_hz": list(result.denominator_band_hz),
        }
        maximum_ratio = max(maximum_ratio, result.ratio)

    details = {
        "scope": "active_phase",
        "maximum_motion_ratio": float(maximum_ratio) if math.isfinite(maximum_ratio) else None,
        "maximum_motion_ratio_is_infinite": not math.isfinite(maximum_ratio),
        "warning_power_ratio": warning_ratio,
        "fail_candidate_power_ratio": fail_candidate,
        "status_policy": "warning_only_in_qc_v0.1",
        "channels": channel_details,
    }
    if maximum_ratio >= warning_ratio:
        return CheckResult(
            check_id="low_frequency_motion_artifact",
            status="warning",
            severity="warning",
            reason_codes=("MOTION_ARTIFACT_HIGH",),
            details=details,
        )
    return CheckResult(
        check_id="low_frequency_motion_artifact",
        status="pass",
        severity="warning",
        details=details,
    )
