from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MetricResult:
    metric_family: str
    metric_id: str
    value: float | None
    supportability: str
    reason_codes: tuple[str, ...] = field(default_factory=tuple)
    provenance: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self):
        return {
            "metric_family": self.metric_family,
            "metric_id": self.metric_id,
            "value": self.value,
            "supportability": self.supportability,
            "reason_codes": list(self.reason_codes),
            "provenance": dict(self.provenance),
            "hard_fatigue_diagnosis_allowed": False
        }

# Core Domain Exceptions
class Day37DomainError(Exception):
    """Base exception for all Day 37 metric calculations."""
    def __init__(self, message: str, reason_code: str):
        super().__init__(message)
        self.reason_code = reason_code

class NonFiniteInputError(Day37DomainError):
    def __init__(self):
        super().__init__("Input contains non-finite values (NaN/Inf).", "NONFINITE_VALUES")

class ZeroNormVectorError(Day37DomainError):
    def __init__(self):
        super().__init__("Vector has zero norm.", "ZERO_NORM_VECTOR")

class ConstantVectorError(Day37DomainError):
    def __init__(self):
        super().__init__("Vector is constant (zero variance).", "CONSTANT_VECTOR")

class IncompatibleNormalizationError(Day37DomainError):
    def __init__(self):
        super().__init__("Incompatible or missing normalization.", "INCOMPATIBLE_NORMALIZATION")

class InsufficientRepetitionsError(Day37DomainError):
    def __init__(self):
        super().__init__("Not enough repetitions for this metric.", "INSUFFICIENT_REPETITIONS")

class AnatomicalMappingUnverifiedError(Day37DomainError):
    def __init__(self):
        super().__init__("Anatomical mapping is not verified (Mendeley/GRABMyo).", "NOT_ELIGIBLE_ANATOMICAL_MAPPING_UNVERIFIED")

class InvalidEnvelopeValueError(Day37DomainError):
    def __init__(self):
        super().__init__("Envelope value is invalid (e.g., negative).", "INVALID_ENVELOPE_VALUE")

class InsufficientActiveSignalError(Day37DomainError):
    def __init__(self):
        super().__init__("Insufficient active signal (e.g., all zeros).", "INSUFFICIENT_ACTIVE_SIGNAL")
