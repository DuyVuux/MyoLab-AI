"""DAY44 fail-closed normalization-reference eligibility.

This module deliberately does not compute normalized values. It only decides whether
an explicit normalization request has a compatible, traceable reference and whether
using that reference would violate partition/domain policy.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any, Iterable, Mapping


class NormalizationStatus(StrEnum):
    ELIGIBLE = "ELIGIBLE"
    UNAVAILABLE = "UNAVAILABLE"
    BLOCKED = "BLOCKED"


class NormalizationMethod(StrEnum):
    NONE = "NONE"
    MVC_PERCENT = "MVC_PERCENT"
    REFERENCE_RATIO = "REFERENCE_RATIO"


class ReferenceType(StrEnum):
    MVC = "MVC"
    REFERENCE_CONTRACTION = "REFERENCE_CONTRACTION"


class NormalizationEligibilityError(ValueError):
    """Raised when normalization request/reference metadata is malformed."""


@dataclass(frozen=True)
class NormalizationReference:
    reference_id: str
    reference_type: ReferenceType
    sha256: str
    version: str
    protocol_id: str
    domain_id: str
    partition: str
    units: str

    def __post_init__(self) -> None:
        if not self.reference_id or not self.protocol_id or not self.domain_id:
            raise NormalizationEligibilityError("REFERENCE_METADATA_REQUIRED")
        if len(self.sha256) != 64:
            raise NormalizationEligibilityError("REFERENCE_SHA256_REQUIRED")
        if any(char not in "0123456789abcdef" for char in self.sha256):
            raise NormalizationEligibilityError("REFERENCE_SHA256_REQUIRED")


@dataclass(frozen=True)
class NormalizationRequest:
    source_window_id: str
    method: NormalizationMethod
    protocol_id: str
    domain_id: str
    partition: str
    units: str
    distribution_support_status: str
    explicit_reference_id: str | None = None


@dataclass(frozen=True)
class NormalizationEligibility:
    schema_version: str
    status: NormalizationStatus
    method: NormalizationMethod
    source_window_id: str
    metric_value: None
    reason_codes: tuple[str, ...]
    reference: NormalizationReference | None
    provenance: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["status"] = self.status.value
        payload["method"] = self.method.value
        if self.reference is not None:
            payload["reference"]["reference_type"] = (
                self.reference.reference_type.value
            )
        payload["reason_codes"] = list(self.reason_codes)
        return payload


def _result(
    request: NormalizationRequest,
    status: NormalizationStatus,
    reasons: Iterable[str],
    reference: NormalizationReference | None = None,
) -> NormalizationEligibility:
    return NormalizationEligibility(
        schema_version="0.1",
        status=status,
        method=request.method,
        source_window_id=request.source_window_id,
        metric_value=None,
        reason_codes=tuple(sorted(set(reasons))),
        reference=reference,
        provenance={
            "policy_version": "day44-normalization-eligibility.v0.1",
            "selection_policy": "EXPLICIT_ID_OR_UNIQUE_COMPATIBLE_MATCH",
            "claim_scope": "RESEARCH_ONLY",
            "locked_set_fitting_allowed": False,
        },
    )


def evaluate_normalization_eligibility(
    request: NormalizationRequest,
    references: Iterable[NormalizationReference],
) -> NormalizationEligibility:
    if not request.source_window_id:
        raise NormalizationEligibilityError("SOURCE_WINDOW_ID_REQUIRED")
    if request.method == NormalizationMethod.NONE:
        return _result(request, NormalizationStatus.ELIGIBLE, ())
    if request.partition == "benchmark-locked":
        return _result(
            request,
            NormalizationStatus.BLOCKED,
            ("LOCKED_EVALUATION_NORMALIZATION_FITTING_FORBIDDEN",),
        )
    if request.distribution_support_status in {
        "SHIFTED",
        "UNKNOWN",
        "NOT_EVALUATED",
    }:
        return _result(
            request,
            NormalizationStatus.UNAVAILABLE,
            ("DISTRIBUTION_SUPPORT_INSUFFICIENT_FOR_NORMALIZATION",),
        )

    required_reference_type = (
        ReferenceType.MVC
        if request.method == NormalizationMethod.MVC_PERCENT
        else ReferenceType.REFERENCE_CONTRACTION
    )
    candidates = list(references)
    if request.explicit_reference_id is not None:
        candidates = [
            item
            for item in candidates
            if item.reference_id == request.explicit_reference_id
        ]
        if not candidates:
            return _result(
                request,
                NormalizationStatus.UNAVAILABLE,
                ("NORMALIZATION_REFERENCE_NOT_FOUND",),
            )

    compatible = [
        item
        for item in candidates
        if item.reference_type == required_reference_type
        and item.protocol_id == request.protocol_id
        and item.domain_id == request.domain_id
        and item.units == request.units
        and item.partition != "benchmark-locked"
    ]
    if not compatible:
        reasons = ["NORMALIZATION_REFERENCE_UNAVAILABLE_OR_INCOMPATIBLE"]
        if candidates and all(
            item.protocol_id != request.protocol_id for item in candidates
        ):
            reasons.append("NORMALIZATION_PROTOCOL_MISMATCH")
        if candidates and all(
            item.domain_id != request.domain_id for item in candidates
        ):
            reasons.append("NORMALIZATION_DOMAIN_MISMATCH")
        if candidates and all(item.units != request.units for item in candidates):
            reasons.append("NORMALIZATION_UNIT_MISMATCH")
        return _result(
            request,
            NormalizationStatus.UNAVAILABLE,
            reasons,
        )

    compatible = sorted(compatible, key=lambda item: item.reference_id)
    if request.explicit_reference_id is None and len(compatible) > 1:
        return _result(
            request,
            NormalizationStatus.UNAVAILABLE,
            ("AMBIGUOUS_NORMALIZATION_REFERENCE_REQUIRE_EXPLICIT_ID",),
        )

    return _result(
        request,
        NormalizationStatus.ELIGIBLE,
        (),
        compatible[0],
    )
