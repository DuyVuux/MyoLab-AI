"""Domain errors for ingestion."""

class IngestionError(Exception):
    """Base exception for all ingestion errors."""
    
    def __init__(self, message: str, code: str):
        super().__init__(message)
        self.code = code

class RawMutationError(IngestionError):
    """Raised when source files are mutated during parsing."""
    def __init__(self, message: str = "Source mutation detected during parsing"):
        super().__init__(message, "RAW_MUTATION_DETECTED")

VALIDATION_REASON_CODES = frozenset(
    {
        "COUNT_MISMATCH",
        "TIMESTAMP_INVALID",
        "UNIT_MISMATCH",
        "SAMPLING_INTERVAL_MISMATCH",
        "MISSING_REQUIRED_METADATA",
        "INFO_LAYOUT_NOT_VERIFIED",
        "MULTIMODAL_ALIGNMENT_INVALID",
        "RAW_MUTATION_DETECTED",
    }
)
