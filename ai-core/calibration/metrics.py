import numpy as np
from typing import Tuple, List, Dict, Union

def multiclass_brier(y_index: np.ndarray, proba: np.ndarray) -> float:
    """
    Calculate the multiclass Brier score.
    
    Args:
        y_index: Ground truth class indices.
        proba: Predicted probabilities for each class.
        
    Returns:
        The multiclass Brier score (mean squared difference).
    """
    p = np.asarray(proba, dtype=float)
    y = np.asarray(y_index, dtype=int)
    
    # Create one-hot encoding of ground truth
    one_hot = np.zeros_like(p)
    one_hot[np.arange(len(y)), y] = 1.0
    
    return float(np.mean(np.sum((p - one_hot) ** 2, axis=1)))


def expected_calibration_error(
    y_index: np.ndarray, 
    proba: np.ndarray, 
    n_bins: int = 15
) -> Tuple[float, List[Dict[str, Union[int, float]]]]:
    """
    Calculate the Expected Calibration Error (ECE) using equal-width bins.
    
    Args:
        y_index: Ground truth class indices.
        proba: Predicted probabilities for each class.
        n_bins: Number of equal-width bins between 0 and 1.
        
    Returns:
        A tuple containing:
        - The ECE scalar value.
        - A list of dictionaries detailing statistics per bin.
    """
    p = np.asarray(proba, dtype=float)
    y = np.asarray(y_index, dtype=int)
    
    # Confidence is the maximum probability across classes
    conf = p.max(axis=1)
    pred = p.argmax(axis=1)
    
    edges = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    bins_info = []
    
    for i in range(n_bins):
        # Determine elements falling into the current bin
        if i < n_bins - 1:
            mask = (conf >= edges[i]) & (conf < edges[i+1])
        else:
            mask = (conf >= edges[i]) & (conf <= edges[i+1])
            
        n = int(mask.sum())
        if n == 0:
            bins_info.append({
                "bin": i,
                "count": 0,
                "accuracy": 0.0,
                "confidence": 0.0
            })
            continue
            
        acc = float(np.mean(pred[mask] == y[mask]))
        c = float(np.mean(conf[mask]))
        
        # ECE accumulation weighted by bin size
        ece += (n / len(y)) * abs(acc - c)
        
        bins_info.append({
            "bin": i,
            "count": n,
            "accuracy": acc,
            "confidence": c
        })
        
    return float(ece), bins_info


def coverage_risk(
    y_index: np.ndarray, 
    proba: np.ndarray, 
    thresholds: List[float]
) -> List[Dict[str, float]]:
    """
    Calculate coverage and selective risk across a range of confidence thresholds.
    
    Args:
        y_index: Ground truth class indices.
        proba: Predicted probabilities for each class.
        thresholds: List of confidence thresholds to evaluate.
        
    Returns:
        A list of dictionaries with threshold, coverage, accuracy, and risk.
    """
    p = np.asarray(proba, dtype=float)
    y = np.asarray(y_index, dtype=int)
    
    conf = p.max(axis=1)
    pred = p.argmax(axis=1)
    rows = []
    
    for t in thresholds:
        accept = conf >= t
        coverage = float(np.mean(accept))
        
        if accept.any():
            acc = float(np.mean(pred[accept] == y[accept]))
            risk = 1.0 - acc
        else:
            # Handle edge case where no predictions meet the threshold
            acc = float("nan")
            risk = float("nan")
            
        rows.append({
            "threshold": float(t),
            "coverage": coverage,
            "selective_accuracy": acc,
            "selective_risk": risk
        })
        
    return rows
