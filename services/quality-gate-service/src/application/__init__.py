"""Application-level quality eligibility gate for downstream metric handoff."""

from application.quality_gate import (
    CalibrationStatus,
    DistributionSupport,
    DistributionSupportContractError,
    DistributionSupportStatus,
    MetricHandoffRequest,
    MetricHandoffStatus,
    OodMethodStatus,
    ProcessingPermission,
    QualityEligibility,
    QualityGateContractError,
    RuleConfidenceLevel,
    UncertaintyContractError,
    UncertaintyHandoff,
    UncertaintyType,
    evaluate_quality_handoff,
    validate_quality_eligibility,
)

__all__ = [
    "CalibrationStatus",
    "DistributionSupport",
    "DistributionSupportContractError",
    "DistributionSupportStatus",
    "MetricHandoffRequest",
    "MetricHandoffStatus",
    "OodMethodStatus",
    "ProcessingPermission",
    "QualityEligibility",
    "QualityGateContractError",
    "RuleConfidenceLevel",
    "UncertaintyContractError",
    "UncertaintyHandoff",
    "UncertaintyType",
    "evaluate_quality_handoff",
    "validate_quality_eligibility",
]
