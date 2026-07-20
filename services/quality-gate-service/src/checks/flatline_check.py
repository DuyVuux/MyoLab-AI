"""Near-constant/flatline segment check."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from semg_core.io import NormalizedSignal
from semg_core.qc import compute_flatline_stats

from result_models import CheckResult
from checks.common import active_channel_samples, get_nested


def run(
    signal: NormalizedSignal,
    protocol: Mapping[str, Any],
    config: Mapping[str, Any],
) -> CheckResult:
    minimum_ms = float(
        get_nested(
            config,
            "signal_heuristics",
            "flatline",
            "minimum_contiguous_duration_ms",
            default=250.0,
        )
    )
    warning_fraction = float(
        get_nested(
            config,
            "signal_heuristics",
            "flatline",
            "warning_total_fraction",
            default=0.01,
        )
    )
    fail_fraction = float(
        get_nested(
            config,
            "signal_heuristics",
            "flatline",
            "fail_total_fraction",
            default=0.05,
        )
    )

    channel_stats: dict[str, Any] = {}
    maximum_fraction = 0.0
    for channel_id, samples in active_channel_samples(signal, protocol).items():
        stats = compute_flatline_stats(
            samples,
            sampling_rate_hz=signal.sampling_rate_hz,
            minimum_contiguous_duration_ms=minimum_ms,
        )
        channel_stats[channel_id] = {
            "total_fraction": stats.total_fraction,
            "longest_run_samples": stats.longest_run_samples,
            "longest_run_duration_s": stats.longest_run_duration_s,
            "tolerance_uV": stats.tolerance_uV,
            "qualifying_run_count": stats.qualifying_run_count,
        }
        maximum_fraction = max(maximum_fraction, stats.total_fraction)

    details = {
        "scope": "active_phase",
        "minimum_contiguous_duration_ms": minimum_ms,
        "warning_total_fraction": warning_fraction,
        "fail_total_fraction": fail_fraction,
        "maximum_flatline_fraction": float(maximum_fraction),
        "channels": channel_stats,
        "threshold_status": get_nested(
            config,
            "signal_heuristics",
            "flatline",
            "amplitude_tolerance_policy",
            default="scale_aware_engineering_heuristic",
        ),
    }
    if maximum_fraction >= fail_fraction:
        return CheckResult(
            check_id="flatline",
            status="fail",
            severity="critical",
            reason_codes=("FLATLINE_EXCESSIVE",),
            details=details,
        )
    if maximum_fraction >= warning_fraction:
        return CheckResult(
            check_id="flatline",
            status="warning",
            severity="warning",
            reason_codes=("FLATLINE_SUSPECTED",),
            details=details,
        )
    return CheckResult(
        check_id="flatline",
        status="pass",
        severity="critical",
        details=details,
    )
