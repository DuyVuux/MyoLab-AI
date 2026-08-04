from typing import Dict, Any

class ZeroShotViolationError(Exception):
    """Raised when a protocol violation is detected in Zero-Shot Transfer configuration."""
    pass

def validate_zero_shot_manifest(manifest: Dict[str, Any]) -> bool:
    """
    Validates that the provided manifest strictly adheres to zero-shot transfer invariants.
    """
    invariant_keys = [
        "target_scaler_fit",
        "target_model_fit",
        "target_calibrator_fit",
        "target_threshold_fit",
        "pooled_training",
        "sealed_test_opened"
    ]
    
    violations = [k for k in invariant_keys if manifest.get(k) is not False]
    
    if violations:
        raise ZeroShotViolationError(f"ZERO_SHOT_VIOLATION: Invariants broken for {violations}")
        
    return True
