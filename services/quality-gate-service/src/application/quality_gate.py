from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any, Iterable, Mapping, Sequence

from aggregation.session_quality import (
    EvaluationStatus,
    QcAggregationResult,
    SignalQuality,
    Supportability,
)

SCHEMA_VERSION = "0.1"
QUALITY_GATE_VERSION = "day31-quality-gate.v0.1.0"
QC_CONTRACT_VERSION = "DAY31-v0.1"


class DistributionSupportStatus(StrEnum):
    SUPPORTED = "SUPPORTED"
    SHIFTED = "SHIFTED"
    UNKNOWN = "UNKNOWN"
    NOT_EVALUATED = "NOT_EVALUATED"


class OodMethodStatus(StrEnum):
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    NOT_VALIDATED = "NOT_VALIDATED"
    VALIDATED = "VALIDATED"


class UncertaintyType(StrEnum):
    RULE_CONFIDENCE = "RULE_CONFIDENCE"
    CALIBRATED_PROBABILITY = "CALIBRATED_PROBABILITY"
    CONFORMAL_SET = "CONFORMAL_SET"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class CalibrationStatus(StrEnum):
    NOT_APPLICABLE = "NOT_APPLICABLE"
    CALIBRATED = "CALIBRATED"
    NOT_VALIDATED = "NOT_VALIDATED"


class RuleConfidenceLevel(StrEnum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"


class MetricHandoffStatus(StrEnum):
    ELIGIBLE = "ELIGIBLE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"
    ABSTAINED = "ABSTAINED"


class ProcessingPermission(StrEnum):
    ALLOW_PROFILED_PROCESSING = "ALLOW_PROFILED_PROCESSING"
    HOLD_FOR_REVIEW = "HOLD_FOR_REVIEW"
    BLOCK_UNSUPPORTED_METRIC = "BLOCK_UNSUPPORTED_METRIC"
    ABSTAIN = "ABSTAIN"


class QualityGateContractError(ValueError):
    """Raised when a DAY31 input or output violates the safety contract."""


class UncertaintyContractError(QualityGateContractError):
    """Raised when uncertainty semantics overclaim their evidence."""


class DistributionSupportContractError(QualityGateContractError):
    """Raised when distribution-support evidence is contradictory."""


@dataclass(frozen=True)
class DistributionSupport:
    status: DistributionSupportStatus
    support_basis: tuple[str, ...]
    reason_codes: tuple[str, ...]
    policy_version: str
    ood_method_status: OodMethodStatus = OodMethodStatus.NOT_IMPLEMENTED
    ood_score: float | None = None
    ood_method_ref: str | None = None

    def __post_init__(self) -> None:
        if not self.policy_version:
            raise DistributionSupportContractError("policy_version is required")
        if self.ood_score is not None:
            if self.ood_method_status != OodMethodStatus.VALIDATED:
                raise DistributionSupportContractError(
                    "ood_score requires a validated OOD method"
                )
            if self.ood_method_ref is None:
                raise DistributionSupportContractError(
                    "ood_score requires ood_method_ref provenance"
                )
            if not 0.0 <= self.ood_score <= 1.0:
                raise DistributionSupportContractError(
                    "normalized ood_score must be within [0,1]"
                )
        if self.ood_method_status != OodMethodStatus.VALIDATED:
            if self.ood_method_ref is not None:
                raise DistributionSupportContractError(
                    "unvalidated OOD method cannot carry method provenance as active evidence"
                )
        if self.status == DistributionSupportStatus.SUPPORTED:
            if not self.support_basis:
                raise DistributionSupportContractError(
                    "SUPPORTED requires explicit support_basis"
                )
        if self.status in {
            DistributionSupportStatus.SHIFTED,
            DistributionSupportStatus.UNKNOWN,
        } and not self.reason_codes:
            raise DistributionSupportContractError(
                "SHIFTED/UNKNOWN requires reason_codes"
            )


@dataclass(frozen=True)
class UncertaintyHandoff:
    uncertainty_type: UncertaintyType
    calibration_status: CalibrationStatus
    abstention: bool
    abstention_reason: str | None = None
    rule_confidence_level: RuleConfidenceLevel | None = None
    calibrated_probability: float | None = None
    conformal_set: tuple[str, ...] | None = None
    calibration_ref: str | None = None

    def __post_init__(self) -> None:
        if self.abstention and not self.abstention_reason:
            raise UncertaintyContractError(
                "abstention=true requires abstention_reason"
            )
        if not self.abstention and self.abstention_reason is not None:
            raise UncertaintyContractError(
                "abstention_reason is forbidden when abstention=false"
            )
        if self.uncertainty_type == UncertaintyType.NOT_APPLICABLE:
            if self.calibration_status != CalibrationStatus.NOT_APPLICABLE:
                raise UncertaintyContractError(
                    "NOT_APPLICABLE uncertainty requires NOT_APPLICABLE calibration"
                )
            if any(
                item is not None
                for item in (
                    self.rule_confidence_level,
                    self.calibrated_probability,
                    self.conformal_set,
                    self.calibration_ref,
                )
            ):
                raise UncertaintyContractError(
                    "NOT_APPLICABLE uncertainty cannot carry synthetic confidence"
                )
            return
        if self.uncertainty_type == UncertaintyType.RULE_CONFIDENCE:
            if self.rule_confidence_level is None:
                raise UncertaintyContractError(
                    "RULE_CONFIDENCE requires an ordinal rule_confidence_level"
                )
            if self.calibrated_probability is not None:
                raise UncertaintyContractError(
                    "rule confidence is not a calibrated probability"
                )
            if self.conformal_set is not None:
                raise UncertaintyContractError(
                    "rule confidence cannot carry a conformal set"
                )
            if self.calibration_status != CalibrationStatus.NOT_APPLICABLE:
                raise UncertaintyContractError(
                    "deterministic rule confidence uses NOT_APPLICABLE calibration"
                )
            if self.calibration_ref is not None:
                raise UncertaintyContractError(
                    "rule confidence must not invent a calibration reference"
                )
            return
        if self.uncertainty_type == UncertaintyType.CALIBRATED_PROBABILITY:
            if self.calibration_status != CalibrationStatus.CALIBRATED:
                raise UncertaintyContractError(
                    "probability requires CALIBRATED status"
                )
            if self.calibrated_probability is None or self.calibration_ref is None:
                raise UncertaintyContractError(
                    "calibrated probability requires value and calibration_ref"
                )
            if not 0.0 <= self.calibrated_probability <= 1.0:
                raise UncertaintyContractError(
                    "calibrated probability must be within [0,1]"
                )
            if self.rule_confidence_level is not None or self.conformal_set is not None:
                raise UncertaintyContractError(
                    "probability handoff cannot mix uncertainty representations"
                )
            return
        if self.uncertainty_type == UncertaintyType.CONFORMAL_SET:
            if self.calibration_status != CalibrationStatus.CALIBRATED:
                raise UncertaintyContractError(
                    "conformal set requires a validated calibration reference"
                )
            if not self.conformal_set or self.calibration_ref is None:
                raise UncertaintyContractError(
                    "conformal set requires a non-empty set and calibration_ref"
                )
            if self.rule_confidence_level is not None:
                raise UncertaintyContractError(
                    "conformal handoff cannot mix rule confidence"
                )
            if self.calibrated_probability is not None:
                raise UncertaintyContractError(
                    "conformal handoff cannot masquerade as probability"
                )


@dataclass(frozen=True)
class MetricHandoffRequest:
    metric_id: str
    requested_scope: str
    distribution_support_required: bool
    profile_id: str

    def __post_init__(self) -> None:
        if not self.metric_id or not self.profile_id:
            raise QualityGateContractError("metric_id and profile_id are required")
        if self.requested_scope not in {"SESSION", "CHANNEL", "WINDOW"}:
            raise QualityGateContractError("requested_scope is invalid")


@dataclass(frozen=True)
class QualityEligibility:
    schema_version: str
    qc_contract_version: str
    metric_id: str
    requested_scope: str
    session_id: str
    channel_id: str | None
    window_id: str | None
    qc_evaluation_status: str
    qc_signal_quality: str | None
    qc_supportability: str
    distribution_support_status: DistributionSupportStatus
    metric_handoff_status: MetricHandoffStatus
    processing_permission: ProcessingPermission
    reason_codes: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    distribution_support: DistributionSupport
    uncertainty: UncertaintyHandoff
    metric_value: None = None
    quality_gate_version: str = QUALITY_GATE_VERSION
    config_version: str = "quality-handoff.v0.1"

    def __post_init__(self) -> None:
        validate_quality_eligibility(self)

    def to_dict(self) -> dict[str, Any]:
        payload = _plain(asdict(self))
        payload["provenance"] = {
            "quality_gate_version": payload.pop("quality_gate_version"),
            "config_version": payload.pop("config_version"),
            "evidence_refs": payload.pop("evidence_refs"),
        }
        return payload


def _plain(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    if isinstance(value, StrEnum):
        return value.value
    return value


def _sorted_unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted(set(values)))


def _scope_matches(qc: QcAggregationResult, request: MetricHandoffRequest) -> None:
    hierarchy = qc.scope_hierarchy
    if hierarchy.target_scope != request.requested_scope:
        raise QualityGateContractError(
            "metric request scope must equal QC aggregation target scope"
        )


def _default_uncertainty() -> UncertaintyHandoff:
    return UncertaintyHandoff(
        uncertainty_type=UncertaintyType.NOT_APPLICABLE,
        calibration_status=CalibrationStatus.NOT_APPLICABLE,
        abstention=False,
    )


def evaluate_quality_handoff(
    *,
    qc: QcAggregationResult,
    request: MetricHandoffRequest,
    distribution_support: DistributionSupport,
    uncertainty: UncertaintyHandoff | None = None,
) -> QualityEligibility:
    """Create the DAY31 fail-closed handoff without computing any metric value."""
    _scope_matches(qc, request)
    hierarchy = qc.scope_hierarchy
    refs = _sorted_unique(
        list(qc.source_refs)
        + [f"qc://{hierarchy.target_scope.lower()}/{request.profile_id}"]
    )

    # P0: QC FAIL/BLOCKED always wins before distribution or uncertainty logic.
    if (
        qc.signal_quality == SignalQuality.FAIL
        or qc.qc_supportability == Supportability.BLOCKED
        or qc.critical_failure
    ):
        result = QualityEligibility(
            schema_version=SCHEMA_VERSION,
            qc_contract_version=QC_CONTRACT_VERSION,
            metric_id=request.metric_id,
            requested_scope=request.requested_scope,
            session_id=hierarchy.session_id,
            channel_id=hierarchy.channel_id,
            window_id=hierarchy.window_id,
            qc_evaluation_status=qc.evaluation_status.value,
            qc_signal_quality=qc.signal_quality.value if qc.signal_quality else None,
            qc_supportability=qc.qc_supportability.value,
            distribution_support_status=distribution_support.status,
            metric_handoff_status=MetricHandoffStatus.BLOCKED,
            processing_permission=ProcessingPermission.BLOCK_UNSUPPORTED_METRIC,
            reason_codes=_sorted_unique(
                list(qc.evidence_reasons)
                + list(qc.disposition_reasons)
                + ["QUALITY_BLOCKED", "QC_FAIL_BLOCKS_METRIC"]
            ),
            evidence_refs=refs,
            distribution_support=distribution_support,
            uncertainty=uncertainty or _default_uncertainty(),
        )
        return result

    # P1: Missing/insufficient QC evidence abstains. Missing evidence never passes.
    if (
        qc.evaluation_status != EvaluationStatus.EVALUATED
        or qc.signal_quality is None
        or qc.qc_supportability in {
            Supportability.UNKNOWN,
            Supportability.NOT_EVALUATED,
        }
    ):
        return QualityEligibility(
            schema_version=SCHEMA_VERSION,
            qc_contract_version=QC_CONTRACT_VERSION,
            metric_id=request.metric_id,
            requested_scope=request.requested_scope,
            session_id=hierarchy.session_id,
            channel_id=hierarchy.channel_id,
            window_id=hierarchy.window_id,
            qc_evaluation_status=qc.evaluation_status.value,
            qc_signal_quality=None,
            qc_supportability=qc.qc_supportability.value,
            distribution_support_status=distribution_support.status,
            metric_handoff_status=MetricHandoffStatus.ABSTAINED,
            processing_permission=ProcessingPermission.ABSTAIN,
            reason_codes=_sorted_unique(
                list(qc.evidence_reasons)
                + list(qc.disposition_reasons)
                + ["QUALITY_ELIGIBILITY_NOT_EVALUATED"]
            ),
            evidence_refs=refs,
            distribution_support=distribution_support,
            uncertainty=uncertainty or _default_uncertainty(),
        )

    # P2: QC WARNING always routes review. It never silently runs a metric.
    if (
        qc.signal_quality == SignalQuality.WARNING
        or qc.qc_supportability == Supportability.REVIEW_REQUIRED
    ):
        return QualityEligibility(
            schema_version=SCHEMA_VERSION,
            qc_contract_version=QC_CONTRACT_VERSION,
            metric_id=request.metric_id,
            requested_scope=request.requested_scope,
            session_id=hierarchy.session_id,
            channel_id=hierarchy.channel_id,
            window_id=hierarchy.window_id,
            qc_evaluation_status=qc.evaluation_status.value,
            qc_signal_quality=qc.signal_quality.value,
            qc_supportability=qc.qc_supportability.value,
            distribution_support_status=distribution_support.status,
            metric_handoff_status=MetricHandoffStatus.REVIEW_REQUIRED,
            processing_permission=ProcessingPermission.HOLD_FOR_REVIEW,
            reason_codes=_sorted_unique(
                list(qc.evidence_reasons)
                + list(qc.disposition_reasons)
                + ["QUALITY_REVIEW_REQUIRED"]
            ),
            evidence_refs=refs,
            distribution_support=distribution_support,
            uncertainty=uncertainty or _default_uncertainty(),
        )

    # P3: QC PASS means quality allows profiled processing. Distribution support is
    # an orthogonal gate that applies only when the downstream capability requires it.
    if qc.signal_quality != SignalQuality.PASS:
        raise QualityGateContractError("unhandled QC state")

    if request.distribution_support_required:
        if distribution_support.status == DistributionSupportStatus.SUPPORTED:
            pass
        elif distribution_support.status == DistributionSupportStatus.SHIFTED:
            return QualityEligibility(
                schema_version=SCHEMA_VERSION,
                qc_contract_version=QC_CONTRACT_VERSION,
                metric_id=request.metric_id,
                requested_scope=request.requested_scope,
                session_id=hierarchy.session_id,
                channel_id=hierarchy.channel_id,
                window_id=hierarchy.window_id,
                qc_evaluation_status=qc.evaluation_status.value,
                qc_signal_quality=qc.signal_quality.value,
                qc_supportability=qc.qc_supportability.value,
                distribution_support_status=distribution_support.status,
                metric_handoff_status=MetricHandoffStatus.REVIEW_REQUIRED,
                processing_permission=ProcessingPermission.HOLD_FOR_REVIEW,
                reason_codes=_sorted_unique(
                    list(qc.evidence_reasons)
                    + list(distribution_support.reason_codes)
                    + ["DISTRIBUTION_SHIFT_REVIEW_REQUIRED"]
                ),
                evidence_refs=refs,
                distribution_support=distribution_support,
                uncertainty=uncertainty or _default_uncertainty(),
            )
        else:
            return QualityEligibility(
                schema_version=SCHEMA_VERSION,
                qc_contract_version=QC_CONTRACT_VERSION,
                metric_id=request.metric_id,
                requested_scope=request.requested_scope,
                session_id=hierarchy.session_id,
                channel_id=hierarchy.channel_id,
                window_id=hierarchy.window_id,
                qc_evaluation_status=qc.evaluation_status.value,
                qc_signal_quality=qc.signal_quality.value,
                qc_supportability=qc.qc_supportability.value,
                distribution_support_status=distribution_support.status,
                metric_handoff_status=MetricHandoffStatus.ABSTAINED,
                processing_permission=ProcessingPermission.ABSTAIN,
                reason_codes=_sorted_unique(
                    list(qc.evidence_reasons)
                    + list(distribution_support.reason_codes)
                    + ["DISTRIBUTION_SUPPORT_NOT_EVALUATED"]
                ),
                evidence_refs=refs,
                distribution_support=distribution_support,
                uncertainty=uncertainty or _default_uncertainty(),
            )

    resolved_uncertainty = uncertainty or _default_uncertainty()
    if resolved_uncertainty.abstention:
        return QualityEligibility(
            schema_version=SCHEMA_VERSION,
            qc_contract_version=QC_CONTRACT_VERSION,
            metric_id=request.metric_id,
            requested_scope=request.requested_scope,
            session_id=hierarchy.session_id,
            channel_id=hierarchy.channel_id,
            window_id=hierarchy.window_id,
            qc_evaluation_status=qc.evaluation_status.value,
            qc_signal_quality=qc.signal_quality.value,
            qc_supportability=qc.qc_supportability.value,
            distribution_support_status=distribution_support.status,
            metric_handoff_status=MetricHandoffStatus.ABSTAINED,
            processing_permission=ProcessingPermission.ABSTAIN,
            reason_codes=_sorted_unique(
                list(qc.evidence_reasons)
                + [resolved_uncertainty.abstention_reason or "UNCERTAINTY_ABSTENTION"]
            ),
            evidence_refs=refs,
            distribution_support=distribution_support,
            uncertainty=resolved_uncertainty,
        )

    return QualityEligibility(
        schema_version=SCHEMA_VERSION,
        qc_contract_version=QC_CONTRACT_VERSION,
        metric_id=request.metric_id,
        requested_scope=request.requested_scope,
        session_id=hierarchy.session_id,
        channel_id=hierarchy.channel_id,
        window_id=hierarchy.window_id,
        qc_evaluation_status=qc.evaluation_status.value,
        qc_signal_quality=qc.signal_quality.value,
        qc_supportability=qc.qc_supportability.value,
        distribution_support_status=distribution_support.status,
        metric_handoff_status=MetricHandoffStatus.ELIGIBLE,
        processing_permission=ProcessingPermission.ALLOW_PROFILED_PROCESSING,
        reason_codes=_sorted_unique(qc.evidence_reasons),
        evidence_refs=refs,
        distribution_support=distribution_support,
        uncertainty=resolved_uncertainty,
    )


def validate_quality_eligibility(result: QualityEligibility) -> None:
    if result.metric_value is not None:
        raise QualityGateContractError(
            "DAY31 handoff cannot compute or emit metric values"
        )
    if not result.reason_codes:
        raise QualityGateContractError("quality eligibility requires reason_codes")
    if not result.evidence_refs:
        raise QualityGateContractError("quality eligibility requires evidence_refs")
    if result.metric_handoff_status == MetricHandoffStatus.BLOCKED:
        if result.processing_permission != ProcessingPermission.BLOCK_UNSUPPORTED_METRIC:
            raise QualityGateContractError("BLOCKED must block metric execution")
    if result.metric_handoff_status == MetricHandoffStatus.REVIEW_REQUIRED:
        if result.processing_permission != ProcessingPermission.HOLD_FOR_REVIEW:
            raise QualityGateContractError("REVIEW_REQUIRED must hold execution")
    if result.metric_handoff_status == MetricHandoffStatus.ABSTAINED:
        if result.processing_permission != ProcessingPermission.ABSTAIN:
            raise QualityGateContractError("ABSTAINED must abstain")
    if result.metric_handoff_status == MetricHandoffStatus.ELIGIBLE:
        if result.processing_permission != ProcessingPermission.ALLOW_PROFILED_PROCESSING:
            raise QualityGateContractError("ELIGIBLE must allow profiled processing")
        if result.qc_signal_quality != SignalQuality.PASS.value:
            raise QualityGateContractError("only QC PASS can be automatically ELIGIBLE")
        if result.uncertainty.abstention:
            raise QualityGateContractError("abstaining uncertainty cannot be ELIGIBLE")
    if result.qc_signal_quality == SignalQuality.FAIL.value:
        if result.metric_handoff_status != MetricHandoffStatus.BLOCKED:
            raise QualityGateContractError("QC FAIL must block metric handoff")
    if result.qc_signal_quality is None:
        if result.metric_handoff_status != MetricHandoffStatus.ABSTAINED:
            raise QualityGateContractError("unknown QC state must abstain")
    if "QUALITY_BLOCKED" in result.reason_codes:
        if result.metric_handoff_status != MetricHandoffStatus.BLOCKED:
            raise QualityGateContractError("QUALITY_BLOCKED cannot coexist with non-block")
