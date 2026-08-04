from typing import List, Union
import numpy as np

def decide_abstention(
    quality_status: Union[str, List[str], np.ndarray],
    confidence: Union[float, List[float], np.ndarray],
    threshold: float,
    warning_delta: float = 0.05
) -> Union[str, List[str]]:
    """
    Apply the abstention policy based on signal quality and model confidence.
    
    Args:
        quality_status: The signal quality status ("pass", "warning", "fail").
                        Can be a single string or a list/array of strings.
        confidence: The confidence score from the model. 
                    Can be a single float or a list/array of floats.
        threshold: The confidence threshold required to accept the prediction.
        warning_delta: Additional confidence margin required when quality is "warning".
        
    Returns:
        The decision string (e.g., "accept", "abstain_low_confidence", etc.)
        or a list of decisions if the input was an array/list.
    """
    
    def _decide_single(q: str, c: float) -> str:
        if q == "fail":
            return "abstain_quality_fail"
        
        required = threshold + warning_delta if q == "warning" else threshold
        
        if c < required:
            if q == "warning":
                return "abstain_low_quality_confidence"
            else:
                return "abstain_low_confidence"
                
        if q == "warning":
            return "accept_with_warning"
        
        return "accept"

    if isinstance(quality_status, (list, np.ndarray)):
        if len(quality_status) != len(confidence):
            raise ValueError("Length of quality_status and confidence must match.")
        return [_decide_single(q, c) for q, c in zip(quality_status, confidence)]
    
    return _decide_single(quality_status, confidence)
