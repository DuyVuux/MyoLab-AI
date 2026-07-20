"""Typed result objects for Signal Quality Gate v0.1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping


_ALLOWED_CHECK_STATUSES = {"pass", "warning", "fail", "not_run", "not_applicable"}
_ALLOWED_SEVERITIES = {"info", "warning", "critical"}
_ALLOWED_QC_STATUSES = {"pass", "warning", "fail", "import_rejected"}


@dataclass(frozen=True, slots=True)
class CheckResult:
    check_id: str
    status: str
    severity: str
    reason_codes: tuple[str, ...] = ()
    details: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.status not in _ALLOWED_CHECK_STATUSES:
            raise ValueError(f"Unsupported check status: {self.status}")
        if self.severity not in _ALLOWED_SEVERITIES:
            raise ValueError(f"Unsupported severity: {self.severity}")
        if not self.check_id:
            raise ValueError("check_id is required")

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "status": self.status,
            "severity": self.severity,
            "reason_codes": list(dict.fromkeys(self.reason_codes)),
            "details": dict(self.details or {}),
        }


@dataclass(frozen=True, slots=True)
class MFCVEligibilityResult:
    eligible: bool
    reason_codes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "eligible": bool(self.eligible),
            "reason_codes": list(dict.fromkeys(self.reason_codes)),
        }


@dataclass(frozen=True, slots=True)
class AbstentionResult:
    required: bool
    reason: str | None

    def to_dict(self) -> dict[str, Any]:
        return {"required": bool(self.required), "reason": self.reason}


@dataclass(frozen=True, slots=True)
class QCResult:
    session_id: str
    status: str
    analysis_allowed: bool
    checks: tuple[CheckResult, ...]
    reason_codes: tuple[str, ...]
    mfcv: MFCVEligibilityResult
    abstention: AbstentionResult
    schema_version: str = "qc-result.v0.1"

    def __post_init__(self) -> None:
        if self.status not in _ALLOWED_QC_STATUSES:
            raise ValueError(f"Unsupported QC status: {self.status}")
        if not self.session_id:
            raise ValueError("session_id is required")
        if not self.analysis_allowed and not self.abstention.required:
            raise ValueError("analysis_allowed=false requires abstention.required=true")

    @property
    def failed_checks(self) -> tuple[CheckResult, ...]:
        return tuple(check for check in self.checks if check.status == "fail")

    @property
    def warning_checks(self) -> tuple[CheckResult, ...]:
        return tuple(check for check in self.checks if check.status == "warning")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "session_id": self.session_id,
            "status": self.status,
            "analysis_allowed": bool(self.analysis_allowed),
            "checks": [check.to_dict() for check in self.checks],
            "reason_codes": list(dict.fromkeys(self.reason_codes)),
            "mfcv": self.mfcv.to_dict(),
            "abstention": self.abstention.to_dict(),
        }


def collect_reason_codes(
    checks: Iterable[CheckResult],
    *,
    include_not_applicable: bool = False,
) -> tuple[str, ...]:
    codes: list[str] = []
    for check in checks:
        if check.status in {"pass", "not_run"}:
            continue
        if check.status == "not_applicable" and not include_not_applicable:
            continue
        codes.extend(check.reason_codes)
    return tuple(dict.fromkeys(codes))
