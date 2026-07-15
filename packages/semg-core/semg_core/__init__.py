"""Pure, dependency-light sEMG core contracts for MVP-0."""

from .io import NormalizedChannel, NormalizedSignal, PhaseMarker, ProtocolRef
from .validation import ValidationIssue, validate_normalized_signal
from .version import NORMALIZED_SIGNAL_SCHEMA_VERSION, SEMGC_CORE_VERSION

__all__ = [
    "NormalizedChannel",
    "NormalizedSignal",
    "PhaseMarker",
    "ProtocolRef",
    "ValidationIssue",
    "validate_normalized_signal",
    "NORMALIZED_SIGNAL_SCHEMA_VERSION",
    "SEMGC_CORE_VERSION",
]
