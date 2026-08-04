from __future__ import annotations
import numpy as np

EPS = 1e-12

def cocontraction_eligibility(metadata: dict) -> dict:
    required_true = (
        "verified_agonist_antagonist_mapping",
        "same_side",
        "synchronized_time_base",
        "compatible_envelope_units",
        "active_phase_present",
    )
    missing = [key for key in required_true if metadata.get(key) is not True]
    if metadata.get("quality_status") == "fail":
        return {"eligible": False, "state": "QUALITY_BLOCKED", "missing": missing}
    if "verified_agonist_antagonist_mapping" in missing:
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
    return {"eligible": state == "SUPPORTED", "state": state, "missing": missing}

def cocontraction_metrics(
    agonist,
    antagonist,
    dt_seconds: float,
    agonist_threshold: float | None = None,
    antagonist_threshold: float | None = None,
    epsilon: float = EPS,
):
    a = np.asarray(agonist, dtype=float)
    b = np.asarray(antagonist, dtype=float)
    if a.shape != b.shape or a.ndim != 1 or len(a) < 2:
        raise ValueError("ENVELOPE_SHAPE_MISMATCH")
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("NONFINITE_ENVELOPE")
    if (a < 0).any() or (b < 0).any():
        raise ValueError("ENVELOPE_MUST_BE_NONNEGATIVE")
    if dt_seconds <= 0:
        raise ValueError("INVALID_DT")

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
