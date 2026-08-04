from typing import Any

import numpy as np

from .types import Day37DomainError, InsufficientRepetitionsError, NonFiniteInputError

EPS = 1e-12

def pair_repeatability(x1: float, x2: float, epsilon: float = EPS) -> dict[str, Any]:
    x1 = float(x1)
    x2 = float(x2)
    absolute_difference = abs(x1 - x2)
    denominator = abs(x1) + abs(x2)
    if denominator <= epsilon:
        raise Day37DomainError("Denominator near zero.", "ZERO_DENOMINATOR")
    
    srd = 2.0 * absolute_difference / denominator
    return {
        "absolute_difference": absolute_difference,
        "symmetric_relative_difference": srd,
    }

def within_subject_cv(values: np.ndarray, positive_ratio_scale: bool, epsilon: float = EPS) -> float:
    x = np.asarray(values, dtype=float)
    if len(x) < 3:
        raise InsufficientRepetitionsError()
    if not np.isfinite(x).all():
        raise NonFiniteInputError()
    if not positive_ratio_scale:
        raise Day37DomainError("Metric not positive ratio scale.", "METRIC_NOT_POSITIVE_RATIO_SCALE")
    if (x < 0).any():
        raise Day37DomainError("Values must be non-negative for CV.", "NEGATIVE_VALUES_FOR_CV")
        
    mean = float(np.mean(x))
    if mean <= epsilon:
        raise Day37DomainError("Mean near zero.", "MEAN_NEAR_ZERO")
        
    return float(100.0 * np.std(x, ddof=1) / mean)

def robust_mad_ratio(values: np.ndarray, epsilon: float = EPS) -> float:
    x = np.asarray(values, dtype=float)
    if len(x) < 3:
        raise InsufficientRepetitionsError()
    if not np.isfinite(x).all():
        raise NonFiniteInputError()
        
    median = float(np.median(x))
    mad = float(np.median(np.abs(x - median)))
    denominator = abs(median)
    if denominator <= epsilon:
        raise Day37DomainError("Median near zero.", "MEDIAN_NEAR_ZERO")
        
    return float(1.4826 * mad / denominator)

def bland_altman(values_a: np.ndarray, values_b: np.ndarray) -> dict[str, Any]:
    a = np.asarray(values_a, dtype=float)
    b = np.asarray(values_b, dtype=float)
    if a.shape != b.shape or a.ndim != 1 or len(a) < 2:
        raise InsufficientRepetitionsError()
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise NonFiniteInputError()
        
    diff = b - a
    bias = float(np.mean(diff))
    sd = float(np.std(diff, ddof=1))
    
    return {
        "n_pairs": len(a),
        "bias": bias,
        "sd_difference": sd,
        "loa_low": bias - 1.96 * sd,
        "loa_high": bias + 1.96 * sd,
        "bias_ci_low": None,
        "bias_ci_high": None,
        "loa_low_ci_low": None,
        "loa_low_ci_high": None,
        "loa_high_ci_low": None,
        "loa_high_ci_high": None,
        "ci_method": None,
    }
