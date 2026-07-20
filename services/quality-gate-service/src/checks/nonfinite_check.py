"""Per-channel non-finite ratio check."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from semg_core.io import NormalizedSignal
from semg_core.qc import nonfinite_ratio

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
            "structural_checks",
            "nonfinite_ratio",
            "warning_fraction",
            default=0.001,
        )
    )
    fail_fraction = float(
        get_nested(
            config,
            "structural_checks",
            "nonfinite_ratio",
            "fail_fraction",
            default=0.01,
        )
    )
    ratios = {
        channel_id: nonfinite_ratio(values)
        for channel_id, values in active_channel_samples(signal, protocol).items()
    }
    maximum_ratio = max(ratios.values(), default=1.0)
    details: dict[str, Any] = {
        "scope": "active_phase",
        "channel_nonfinite_ratios": ratios,
        "maximum_nonfinite_ratio": float(maximum_ratio),
        "warning_fraction": warning_fraction,
        "fail_fraction": fail_fraction,
    }
    if maximum_ratio >= fail_fraction:
        return CheckResult(
            check_id="nonfinite_ratio",
            status="fail",
            severity="critical",
            reason_codes=("NONFINITE_RATIO_EXCESSIVE",),
            details=details,
        )
    if maximum_ratio >= warning_fraction:
        return CheckResult(
            check_id="nonfinite_ratio",
            status="warning",
            severity="warning",
            reason_codes=("NONFINITE_RATIO_WARNING",),
            details=details,
        )
    return CheckResult(
        check_id="nonfinite_ratio",
        status="pass",
        severity="critical",
        details=details,
    )
