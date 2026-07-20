"""Signal Quality Gate v0.1 orchestration.

Order:
1. deterministic structural/protocol checks;
2. numerical-integrity check;
3. signal heuristics when structural checks allow them;
4. MFCV capability eligibility, which never blocks basic sEMG by itself.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Callable

from semg_core.io import NormalizedSignal

from checks import (
    baseline_noise_check,
    channel_completeness_check,
    clipping_saturation_check,
    cv_eligibility_check,
    duration_check,
    flatline_check,
    motion_artifact_check,
    nonfinite_check,
    powerline_noise_check,
    protocol_compatibility_check,
    sampling_rate_check,
)
from result_models import (
    AbstentionResult,
    CheckResult,
    MFCVEligibilityResult,
    QCResult,
    collect_reason_codes,
)


CheckFunction = Callable[
    [NormalizedSignal, Mapping[str, Any], Mapping[str, Any]],
    CheckResult,
]


STRUCTURAL_CHECKS: tuple[CheckFunction, ...] = (
    protocol_compatibility_check.run,
    sampling_rate_check.run,
    duration_check.run,
    channel_completeness_check.run,
    nonfinite_check.run,
)

HEURISTIC_CHECKS: tuple[CheckFunction, ...] = (
    flatline_check.run,
    clipping_saturation_check.run,
    powerline_noise_check.run,
    motion_artifact_check.run,
    baseline_noise_check.run,
)

_HEURISTIC_IDS = (
    "flatline",
    "clipping_saturation",
    "powerline_noise",
    "low_frequency_motion_artifact",
    "baseline_noise",
)


class QualityGate:
    """Run configured quality checks on one canonical signal session."""

    def __init__(self, config: Mapping[str, Any]) -> None:
        self._config = dict(config)
        policy = self._config.get("policy", {})
        if not isinstance(policy, Mapping):
            raise ValueError("QC config policy must be an object")
        if policy.get("critical_failure_blocks_analysis") is not True:
            raise ValueError("qc_v0.1 requires critical_failure_blocks_analysis=true")
        if policy.get("mfcv_ineligibility_blocks_basic_semg") is not False:
            raise ValueError("MFCV ineligibility must not block basic sEMG in qc_v0.1")

    @property
    def config_id(self) -> str:
        return str(self._config.get("config_id", "unknown"))

    def run(
        self,
        signal: NormalizedSignal,
        protocol: Mapping[str, Any],
        *,
        diagnostic_mode: bool = False,
    ) -> QCResult:
        checks: list[CheckResult] = []

        for function in STRUCTURAL_CHECKS:
            checks.append(function(signal, protocol, self._config))

        structural_failed = any(check.status == "fail" for check in checks)
        if structural_failed and not diagnostic_mode:
            checks.extend(
                CheckResult(
                    check_id=check_id,
                    status="not_run",
                    severity="warning",
                    details={
                        "reason": "Skipped because a preceding critical structural check failed.",
                        "diagnostic_mode": False,
                    },
                )
                for check_id in _HEURISTIC_IDS
            )
        else:
            for function in HEURISTIC_CHECKS:
                checks.append(function(signal, protocol, self._config))

        mfcv_check, mfcv_result = cv_eligibility_check.run(
            signal,
            protocol,
            self._config,
        )
        checks.append(mfcv_check)

        basic_checks = [check for check in checks if check.check_id != "mfcv_eligibility"]
        failed = any(check.status == "fail" for check in basic_checks)
        warned = any(check.status == "warning" for check in basic_checks)

        if failed:
            status = "fail"
            analysis_allowed = False
            abstention = AbstentionResult(
                required=True,
                reason="signal_or_protocol_not_sufficient",
            )
        elif warned:
            status = "warning"
            analysis_allowed = True
            abstention = AbstentionResult(required=False, reason=None)
        else:
            status = "pass"
            analysis_allowed = True
            abstention = AbstentionResult(required=False, reason=None)

        return QCResult(
            session_id=signal.session_id,
            status=status,
            analysis_allowed=analysis_allowed,
            checks=tuple(checks),
            reason_codes=collect_reason_codes(basic_checks),
            mfcv=mfcv_result,
            abstention=abstention,
        )


def build_import_rejected_result(
    *,
    session_id: str,
    blocking_codes: tuple[str, ...],
    warning_codes: tuple[str, ...] = (),
    issue_details: list[dict[str, Any]] | None = None,
) -> QCResult:
    """Map ingestion rejection into the shared QC result contract."""

    check = CheckResult(
        check_id="ingestion",
        status="fail",
        severity="critical",
        reason_codes=tuple(dict.fromkeys((*blocking_codes, *warning_codes))),
        details={"issues": list(issue_details or [])},
    )
    return QCResult(
        session_id=session_id or "UNKNOWN_SESSION",
        status="import_rejected",
        analysis_allowed=False,
        checks=(check,),
        reason_codes=tuple(dict.fromkeys((*blocking_codes, *warning_codes))),
        mfcv=MFCVEligibilityResult(eligible=False, reason_codes=()),
        abstention=AbstentionResult(required=True, reason="import_rejected"),
    )
