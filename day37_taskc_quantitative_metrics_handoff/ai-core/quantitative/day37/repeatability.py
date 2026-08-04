from __future__ import annotations
import numpy as np

EPS = 1e-12

def pair_repeatability(x1: float, x2: float, epsilon: float = EPS) -> dict:
    x1 = float(x1); x2 = float(x2)
    absolute_difference = abs(x1 - x2)
    denominator = abs(x1) + abs(x2)
    if denominator <= epsilon:
        srd = None
        reason = "NEAR_ZERO_DENOMINATOR"
    else:
        srd = 2.0 * absolute_difference / denominator
        reason = None
    return {
        "absolute_difference": absolute_difference,
        "symmetric_relative_difference": srd,
        "reason_code": reason,
    }

def within_subject_cv(values, positive_ratio_scale: bool, epsilon: float = EPS):
    x = np.asarray(values, dtype=float)
    if len(x) < 3:
        return None, "INSUFFICIENT_REPETITIONS"
    if not np.isfinite(x).all():
        return None, "NONFINITE_VALUES"
    if not positive_ratio_scale:
        return None, "METRIC_NOT_POSITIVE_RATIO_SCALE"
    mean = float(np.mean(x))
    if mean <= epsilon:
        return None, "MEAN_NEAR_ZERO"
    return float(100.0 * np.std(x, ddof=1) / mean), None

def robust_mad_ratio(values, epsilon: float = EPS):
    x = np.asarray(values, dtype=float)
    if len(x) < 3:
        return None, "INSUFFICIENT_REPETITIONS"
    if not np.isfinite(x).all():
        return None, "NONFINITE_VALUES"
    median = float(np.median(x))
    mad = float(np.median(np.abs(x - median)))
    denominator = abs(median)
    if denominator <= epsilon:
        return None, "MEDIAN_NEAR_ZERO"
    return float(1.4826 * mad / denominator), None

def bland_altman(values_a, values_b):
    a = np.asarray(values_a, dtype=float)
    b = np.asarray(values_b, dtype=float)
    if a.shape != b.shape or a.ndim != 1 or len(a) < 2:
        raise ValueError("Bland-Altman requires paired 1D arrays with n>=2")
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("NONFINITE_VALUES")
    diff = b - a
    bias = float(np.mean(diff))
    sd = float(np.std(diff, ddof=1))
    return {
        "bias": bias,
        "loa_low": bias - 1.96 * sd,
        "loa_high": bias + 1.96 * sd,
        "pair_count": len(a),
    }
