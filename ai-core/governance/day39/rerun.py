from typing import List, Dict, Any
from .models import RerunStatusEnum, RerunComparison

def compare_predictions(original: List[Any], rerun: List[Any]) -> Dict[str, Any]:
    """
    Compares two lists of predictions and returns exact match status.
    """
    if len(original) != len(rerun):
        return {
            "status": RerunStatusEnum.MISMATCH, 
            "reason": "ROW_COUNT_MISMATCH"
        }
    
    mismatches = sum(a != b for a, b in zip(original, rerun))
    
    status = RerunStatusEnum.EXACT_MATCH if mismatches == 0 else RerunStatusEnum.MISMATCH
    
    return {
        "status": status,
        "prediction_mismatch_count": mismatches
    }

def compare_metric(name: str, original: float, rerun: float, tolerance: float = 1e-10) -> RerunComparison:
    """
    Compares two floating-point metrics within a strict predefined tolerance contract.
    """
    delta = abs(float(original) - float(rerun))
    within_tolerance = delta <= tolerance
    
    return RerunComparison(
        metric_name=name,
        absolute_delta=delta,
        within_tolerance=within_tolerance,
        tolerance_applied=tolerance
    )
