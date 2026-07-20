"""Repeated-extrema clipping heuristic."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from semg_core.io import NormalizedSignal
from semg_core.qc import repeated_extrema_fraction

from result_models import CheckResult
from checks.common import active_channel_samples, get_nested


def run(
    signal: NormalizedSignal,
    protocol: Mapping[str, Any],
    config: Mapping[str, Any],
) -> CheckResult:
    warning_fraction = float(
        get_nested(
            config,
            "signal_heuristics",
            "clipping",
            "repeated_extrema_warning_fraction",
            default=0.005,
        )
    )
    fail_candidate_fraction = float(
        get_nested(
            config,
            "signal_heuristics",
            "clipping",
            "repeated_extrema_fail_candidate_fraction",
            default=0.02,
        )
    )
    status_policy = str(
        get_nested(
            config,
            "signal_heuristics",
            "clipping",
            "status_in_v0_1",
            default="warning_only_until_device_calibrated",
        )
    )
    ratios = {
        channel_id: repeated_extrema_fraction(samples)
        for channel_id, samples in active_channel_samples(signal, protocol).items()
    }
    maximum_ratio = max(ratios.values(), default=1.0)
    details: dict[str, Any] = {
        "scope": "active_phase",
        "channel_repeated_extrema_fractions": ratios,
        "maximum_repeated_extrema_fraction": float(maximum_ratio),
        "warning_fraction": warning_fraction,
        "fail_candidate_fraction": fail_candidate_fraction,
        "status_policy": status_policy,
        "interpretation": "Vendor-neutral heuristic; ADC rail is unknown.",
    }
    if maximum_ratio >= warning_fraction:
        return CheckResult(
            check_id="clipping_saturation",
            status="warning",
            severity="warning",
            reason_codes=("CLIPPING_SUSPECTED",),
            details=details,
        )
    return CheckResult(
        check_id="clipping_saturation",
        status="pass",
        severity="warning",
        details=details,
    )
