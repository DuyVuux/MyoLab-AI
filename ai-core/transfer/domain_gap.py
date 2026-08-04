import numpy as np
import numpy.typing as npt
from typing import Tuple, Optional
from scipy.stats import wasserstein_distance
from scipy.spatial.distance import cdist

def standardized_mean_difference(
    s: npt.NDArray[np.float64], 
    t: npt.NDArray[np.float64], 
    epsilon: float = 1e-12
) -> npt.NDArray[np.float64]:
    """
    Computes the Standardized Mean Difference (SMD) between source and target domains.
    Handles numerical instability via epsilon to avoid DivisionByZero.
    """
    s = np.asarray(s, dtype=np.float64)
    t = np.asarray(t, dtype=np.float64)
    
    if s.ndim != 2 or t.ndim != 2:
        raise ValueError("Inputs must be 2D arrays (samples, features).")
    
    if s.shape[1] != t.shape[1]:
        raise ValueError(f"Feature mismatch: source {s.shape[1]} vs target {t.shape[1]}")
        
    pooled = np.sqrt((np.var(s, axis=0, ddof=1) + np.var(t, axis=0, ddof=1)) / 2)
    return (np.mean(s, axis=0) - np.mean(t, axis=0)) / (pooled + epsilon)

def per_feature_wasserstein(
    s: npt.NDArray[np.float64], 
    t: npt.NDArray[np.float64]
) -> npt.NDArray[np.float64]:
    """
    Computes 1D Wasserstein distance for each feature independently.
    """
    s = np.asarray(s, dtype=np.float64)
    t = np.asarray(t, dtype=np.float64)
    
    if s.ndim != 2 or t.ndim != 2:
        raise ValueError("Inputs must be 2D arrays (samples, features).")
        
    if s.shape[1] != t.shape[1]:
        raise ValueError(f"Feature mismatch: source {s.shape[1]} vs target {t.shape[1]}")
        
    return np.asarray([wasserstein_distance(s[:, j], t[:, j]) for j in range(s.shape[1])])

def rbf_mmd(
    s: npt.NDArray[np.float64], 
    t: npt.NDArray[np.float64], 
    gamma: Optional[float] = None
) -> Tuple[float, float]:
    """
    Computes Maximum Mean Discrepancy (MMD) using an RBF kernel.
    If gamma is not provided, uses median heuristic over source distances.
    Warning: O(N^2) memory complexity due to cdist.
    """
    s = np.asarray(s, dtype=np.float64)
    t = np.asarray(t, dtype=np.float64)
    
    if s.ndim != 2 or t.ndim != 2:
        raise ValueError("Inputs must be 2D arrays (samples, features).")
        
    if s.shape[1] != t.shape[1]:
        raise ValueError(f"Feature mismatch: source {s.shape[1]} vs target {t.shape[1]}")
        
    if s.shape[0] == 0 or t.shape[0] == 0:
        raise ValueError("Source and target arrays must not be empty.")
        
    if gamma is None:
        d = cdist(s, s, metric="sqeuclidean")
        positive = d[d > 0]
        gamma = 1.0 / ((np.median(positive) if len(positive) > 0 else 1.0) + 1e-12)
        
    term_ss = np.mean(np.exp(-gamma * cdist(s, s, metric="sqeuclidean")))
    term_tt = np.mean(np.exp(-gamma * cdist(t, t, metric="sqeuclidean")))
    term_st = np.mean(np.exp(-gamma * cdist(s, t, metric="sqeuclidean")))
    
    mmd_val = float(term_ss + term_tt - 2 * term_st)
    return max(0.0, mmd_val), float(gamma)
