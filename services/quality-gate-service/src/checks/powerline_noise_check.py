"""50/60 Hz contamination warning check."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
import math

from semg_core.io import NormalizedSignal
from semg_core.qc import powerline_contamination_ratio

from result_models import CheckResult
from checks.common import active_channel_samples, get_nested


def run(
    signal: NormalizedSignal,
    protocol: Mapping[str, Any],
    config: Mapping[str, Any],
) -> CheckResult:
    line_hz = float(
        get_nested(
            config,
            "signal_heuristics",
            "powerline_noise",
            "default_line_frequency_hz",
            default=50.0,
        )
    )
    half_width_hz = float(
        get_nested(
            config,
            "signal_heuristics",
            "powerline_noise",
            "integration_half_width_hz",
            default=1.0,
        )
    )
    warning_ratio = float(
        get_nested(
            config,
            "signal_heuristics",
            "powerline_noise",
            "warning_power_ratio",
            default=0.20,
        )
    )
    fail_candidate = float(
        get_nested(
            config,
            "signal_heuristics",
            "powerline_noise",
            "fail_candidate_power_ratio",
            default=0.40,
        )
    )
    analysis_band = (20.0, min(400.0, signal.sampling_rate_hz / 2.0 * 0.98))

    channel_details: dict[str, Any] = {}
    maximum_ratio = 0.0
    for channel_id, samples in active_channel_samples(signal, protocol).items():
        result = powerline_contamination_ratio(
            samples,
            sampling_rate_hz=signal.sampling_rate_hz,
            line_frequency_hz=line_hz,
            integration_half_width_hz=half_width_hz,
            analysis_band_hz=analysis_band,
        )
        channel_details[channel_id] = {
            "ratio": result.ratio if math.isfinite(result.ratio) else None,
            "ratio_is_infinite": not math.isfinite(result.ratio),
            "numerator_power": result.numerator_power,
            "denominator_power": result.denominator_power,
            "line_band_hz": list(result.numerator_band_hz),
            "analysis_band_hz": list(result.denominator_band_hz),
        }
        maximum_ratio = max(maximum_ratio, result.ratio)

    details = {
        "scope": "active_phase",
        "line_frequency_hz": line_hz,
        "integration_half_width_hz": half_width_hz,
        "maximum_powerline_ratio": float(maximum_ratio) if math.isfinite(maximum_ratio) else None,
        "maximum_powerline_ratio_is_infinite": not math.isfinite(maximum_ratio),
        "warning_power_ratio": warning_ratio,
        "fail_candidate_power_ratio": fail_candidate,
        "status_policy": "warning_only_in_qc_v0.1",
        "channels": channel_details,
    }
    if maximum_ratio >= warning_ratio:
        return CheckResult(
            check_id="powerline_noise",
            status="warning",
            severity="warning",
            reason_codes=("POWERLINE_NOISE_HIGH",),
            details=details,
        )
    return CheckResult(
        check_id="powerline_noise",
        status="pass",
        severity="warning",
        details=details,
    )
