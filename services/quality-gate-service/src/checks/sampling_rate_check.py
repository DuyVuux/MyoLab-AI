"""Sampling-rate compatibility check."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from semg_core.io import NormalizedSignal
from semg_core.validation import infer_sampling_rate_hz, relative_timing_jitter

from result_models import CheckResult
from checks.common import get_nested


def run(
    signal: NormalizedSignal,
    protocol: Mapping[str, Any],
    config: Mapping[str, Any],
) -> CheckResult:
    minimum_fs = float(get_nested(protocol, "acquisition", "minimum_sampling_rate_hz", default=0.0))
    tolerance = float(
        get_nested(
            config,
            "structural_checks",
            "sampling_rate",
            "relative_tolerance",
            default=0.01,
        )
    )
    inferred_fs = infer_sampling_rate_hz(signal.time_s)
    relative_error = abs(inferred_fs - signal.sampling_rate_hz) / signal.sampling_rate_hz
    jitter = relative_timing_jitter(signal.time_s)
    details = {
        "declared_sampling_rate_hz": float(signal.sampling_rate_hz),
        "inferred_sampling_rate_hz": float(inferred_fs),
        "protocol_minimum_sampling_rate_hz": minimum_fs,
        "relative_error": float(relative_error),
        "configured_relative_tolerance": tolerance,
        "relative_timing_jitter_median": float(jitter),
    }

    reasons: list[str] = []
    if signal.sampling_rate_hz < minimum_fs:
        reasons.append("SAMPLING_RATE_BELOW_PROTOCOL_MIN")
    if relative_error > tolerance:
        reasons.append("SAMPLING_RATE_MISMATCH")

    if reasons:
        return CheckResult(
            check_id="sampling_rate",
            status="fail",
            severity="critical",
            reason_codes=tuple(reasons),
            details=details,
        )
    return CheckResult(
        check_id="sampling_rate",
        status="pass",
        severity="critical",
        details=details,
    )
