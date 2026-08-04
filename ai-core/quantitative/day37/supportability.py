from .types import Day37DomainError, MetricResult

VALID_STATES = {
    "SUPPORTED",
    "SUPPORTED_WITH_WARNING",
    "INSUFFICIENT_REPETITIONS",
    "INCOMPATIBLE_PROTOCOL",
    "INCOMPATIBLE_NORMALIZATION",
    "ZERO_NORM_VECTOR",
    "CONSTANT_VECTOR",
    "MISSING_METADATA",
    "NOT_ELIGIBLE_ANATOMICAL_MAPPING_UNVERIFIED",
    "NOT_ELIGIBLE_UNSYNCHRONIZED",
    "QUALITY_BLOCKED",
    "INVALID_ENVELOPE_VALUE",
    "INSUFFICIENT_ACTIVE_SIGNAL"
}

def map_error_to_supportability(error: Day37DomainError) -> tuple[str, str]:
    """Maps a typed domain error to a valid Supportability state and reason code."""
    # Some reason codes are exactly the supportability state, some map to generic ones.
    state = error.reason_code
    if state not in VALID_STATES:
        state = "SUPPORTED_WITH_WARNING"  # fallback or map explicitly
        
    # Explicit overrides for supportability mapping if needed
    if error.reason_code == "NONFINITE_VALUES":
        state = "QUALITY_BLOCKED"
        
    return state, error.reason_code

def create_metric_result(metric_family: str, metric_id: str, value: float | None, 
                         supportability: str, reason_codes: list[str], provenance: dict) -> MetricResult:
    if supportability not in VALID_STATES:
        raise ValueError(f"UNKNOWN_SUPPORTABILITY: {supportability}")
        
    if supportability != "SUPPORTED" and supportability != "SUPPORTED_WITH_WARNING" and value == 0.0:
        raise ValueError("INELIGIBLE_VALUE_MUST_NOT_BE_ZERO_SENTINEL")
        
    return MetricResult(
        metric_family=metric_family,
        metric_id=metric_id,
        value=value,
        supportability=supportability,
        reason_codes=tuple(reason_codes),
        provenance=provenance
    )
