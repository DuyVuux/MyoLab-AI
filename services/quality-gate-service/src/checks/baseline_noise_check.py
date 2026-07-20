"""Baseline-noise placeholder with explicit non-fabrication behavior."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from semg_core.io import NormalizedSignal

from result_models import CheckResult
from checks.common import get_nested


def run(
    signal: NormalizedSignal,
    protocol: Mapping[str, Any],
    config: Mapping[str, Any],
) -> CheckResult:
    del protocol
    phase_id = str(
        get_nested(
            config,
            "signal_heuristics",
            "baseline_noise",
            "requires_phase",
            default="baseline_rest",
        )
    )
    absolute_enabled = bool(
        get_nested(
            config,
            "signal_heuristics",
            "baseline_noise",
            "absolute_threshold_enabled",
            default=False,
        )
    )
    phase_available = any(marker.phase_id == phase_id for marker in signal.phase_markers)
    return CheckResult(
        check_id="baseline_noise",
        status="not_run" if phase_available else "not_applicable",
        severity="warning",
        details={
            "required_phase_id": phase_id,
            "phase_available": phase_available,
            "absolute_threshold_enabled": absolute_enabled,
            "reason": (
                "Absolute/device-calibrated baseline-noise threshold is disabled in qc_v0.1; "
                "no SNR or pass/fail value is fabricated."
            ),
        },
    )
