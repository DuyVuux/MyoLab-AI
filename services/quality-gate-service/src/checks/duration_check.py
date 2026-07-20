"""Required active-phase duration check."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from semg_core.io import NormalizedSignal

from result_models import CheckResult
from checks.common import active_phase_id, get_nested


def run(
    signal: NormalizedSignal,
    protocol: Mapping[str, Any],
    config: Mapping[str, Any],
) -> CheckResult:
    phase_id = active_phase_id(protocol)
    required_duration = float(get_nested(protocol, "task", "active_duration_s", default=0.0))
    minimum_fraction = float(
        get_nested(
            config,
            "structural_checks",
            "active_duration",
            "minimum_fraction_of_protocol_duration",
            default=0.90,
        )
    )
    minimum_duration = required_duration * minimum_fraction

    try:
        marker = signal.get_phase(phase_id)
    except (KeyError, ValueError):
        return CheckResult(
            check_id="active_duration",
            status="fail",
            severity="critical",
            reason_codes=("ACTIVE_PHASE_MISSING",),
            details={
                "active_phase_id": phase_id,
                "required_duration_s": required_duration,
                "minimum_fraction": minimum_fraction,
            },
        )

    phase_slice = signal.phase_slice(phase_id)
    sample_count = int((phase_slice.stop or 0) - (phase_slice.start or 0))
    sample_span = sample_count / signal.sampling_rate_hz
    details = {
        "active_phase_id": phase_id,
        "marker_duration_s": float(marker.duration_s),
        "active_sample_count": sample_count,
        "active_sample_span_s": float(sample_span),
        "required_duration_s": required_duration,
        "minimum_fraction": minimum_fraction,
        "minimum_accepted_duration_s": float(minimum_duration),
    }
    if marker.duration_s < minimum_duration or sample_span < minimum_duration:
        return CheckResult(
            check_id="active_duration",
            status="fail",
            severity="critical",
            reason_codes=("ACTIVE_DURATION_TOO_SHORT",),
            details=details,
        )
    return CheckResult(
        check_id="active_duration",
        status="pass",
        severity="critical",
        details=details,
    )
