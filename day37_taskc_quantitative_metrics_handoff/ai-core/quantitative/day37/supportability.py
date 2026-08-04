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
}

def metric_event(metric_family, metric_id, value, supportability, reason_codes, provenance):
    if supportability not in VALID_STATES:
        raise ValueError("UNKNOWN_SUPPORTABILITY")
    if supportability != "SUPPORTED" and value == 0:
        raise ValueError("INELIGIBLE_VALUE_MUST_NOT_BE_ZERO_SENTINEL")
    return {
        "metric_family": metric_family,
        "metric_id": metric_id,
        "value": value,
        "supportability": supportability,
        "reason_codes": list(reason_codes),
        "provenance": dict(provenance),
        "hard_fatigue_diagnosis_allowed": False,
    }
