from typing import Any

import numpy as np

from .types import (
    AnatomicalMappingUnverifiedError,
    Day37DomainError,
    InsufficientActiveSignalError,
    InvalidEnvelopeValueError,
    NonFiniteInputError,
)

EPS = 1e-12

def cocontraction_eligibility(metadata: dict[str, Any]) -> dict[str, Any]:
    dataset_id = metadata.get("dataset_id", "")
    
    # Mendeley and GRABMyo default blocked for co-contraction
    if dataset_id in ("mendeley", "grabmyo") and not metadata.get("verified_agonist_antagonist_mapping"):
        raise AnatomicalMappingUnverifiedError()
        
    required_true = (
        "verified_agonist_antagonist_mapping",
        "same_side",
        "synchronized_time_base",
        "compatible_envelope_units",
        "active_phase_present",
    )
    
    missing = [key for key in required_true if metadata.get(key) is not True]
    
    if metadata.get("quality_status") == "fail":
        state = "QUALITY_BLOCKED"
    elif "verified_agonist_antagonist_mapping" in missing:
        state = "NOT_ELIGIBLE_ANATOMICAL_MAPPING_UNVERIFIED"
    elif "synchronized_time_base" in missing:
        state = "NOT_ELIGIBLE_UNSYNCHRONIZED"
    elif "compatible_envelope_units" in missing:
        state = "NOT_ELIGIBLE_UNIT_MISMATCH"
    elif "active_phase_present" in missing:
        state = "NOT_ELIGIBLE_ACTIVE_PHASE_MISSING"
    elif missing:
        state = "NOT_ELIGIBLE_METADATA"
    elif not metadata.get("normalization_method"):
        state = "MISSING_NORMALIZATION_METHOD"
    else:
        state = "SUPPORTED"
        
    if state != "SUPPORTED":
        raise Day37DomainError(f"Eligibility failed: {state}", state)
        
    return {"eligible": True, "state": "SUPPORTED", "missing": []}

def cocontraction_metrics(
    agonist: np.ndarray,
    antagonist: np.ndarray,
    dt_seconds: float,
    agonist_threshold: float | None = None,
    antagonist_threshold: float | None = None,
    epsilon: float = EPS,
) -> dict[str, Any]:
    a = np.asarray(agonist, dtype=float)
    b = np.asarray(antagonist, dtype=float)
    
    if a.shape != b.shape or a.ndim != 1 or len(a) < 2:
        raise Day37DomainError("Envelope shape mismatch.", "ENVELOPE_SHAPE_MISMATCH")
        
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise NonFiniteInputError()
        
    if (a < 0).any() or (b < 0).any():
        raise InvalidEnvelopeValueError()
        
    if dt_seconds <= 0:
        raise Day37DomainError("Invalid time step (dt).", "INVALID_DT")
        
    # Check for zero envelopes (insufficient active signal)
    if np.sum(a) <= epsilon and np.sum(b) <= epsilon:
        raise InsufficientActiveSignalError()

    minimum = np.minimum(a, b)
    maximum = np.maximum(a, b)
    
    cci = 2.0 * minimum / (a + b + epsilon)
    
    overlap_area_ratio = float(
        np.sum(minimum) * dt_seconds /
        (np.sum(maximum) * dt_seconds + epsilon)
    )
    
    result = {
        "mean_cci": float(np.mean(cci)),
        "median_cci": float(np.median(cci)),
        "q90_cci": float(np.quantile(cci, 0.90)),
        "overlap_area_ratio": overlap_area_ratio,
        "coactivation_load": float(np.sum(minimum) * dt_seconds),
        "active_duration_seconds": float(len(a) * dt_seconds),
    }
    
    if agonist_threshold is None or antagonist_threshold is None:
        result["simultaneous_activation_duration_fraction"] = None
        result["threshold_reason_code"] = "THRESHOLD_SOURCE_MISSING"
    else:
        simultaneous = (a > agonist_threshold) & (b > antagonist_threshold)
        result["simultaneous_activation_duration_fraction"] = float(np.mean(simultaneous))
        result["threshold_reason_code"] = None
        
    return result
