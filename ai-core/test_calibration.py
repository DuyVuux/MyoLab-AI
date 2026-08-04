import sys
import os
import numpy as np

# Ensure ai-core can import its own modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from calibration import TemperatureScaler, PlattOVR, IsotonicOVR
from calibration import decide_abstention
from calibration import multiclass_brier, expected_calibration_error, coverage_risk

def main():
    print("Testing Calibration Module...")
    
    # Dummy data
    np.random.seed(42)
    y_true = np.random.randint(0, 3, size=100)
    logits = np.random.randn(100, 3)
    
    # Test TemperatureScaler
    ts = TemperatureScaler()
    ts.fit(logits, y_true)
    probs_ts = ts.predict_proba(logits)
    print(f"TemperatureScaler T: {ts.temperature_:.4f}")
    assert probs_ts.shape == (100, 3)
    
    # Test PlattOVR
    platt = PlattOVR()
    platt.fit(logits, y_true)
    probs_platt = platt.predict_proba(logits)
    print("PlattOVR fitting successful.")
    assert probs_platt.shape == (100, 3)
    assert np.allclose(probs_platt.sum(axis=1), 1.0)
    
    # Test IsotonicOVR
    iso = IsotonicOVR()
    iso.fit(probs_ts, y_true) # Fit on probabilities to be safe
    probs_iso = iso.predict_proba(probs_ts)
    print("IsotonicOVR fitting successful.")
    assert probs_iso.shape == (100, 3)
    assert np.allclose(probs_iso.sum(axis=1), 1.0)
    
    # Test Metrics
    brier = multiclass_brier(y_true, probs_platt)
    ece, bins = expected_calibration_error(y_true, probs_platt, n_bins=5)
    cov_risk = coverage_risk(y_true, probs_platt, thresholds=[0.0, 0.5, 0.9])
    
    print(f"Brier: {brier:.4f}, ECE: {ece:.4f}")
    print(f"Coverage Risk at 0.5: {cov_risk[1]}")
    
    # Test Abstention
    qualities = ["pass", "warning", "fail", "pass"]
    confidences = [0.9, 0.85, 0.99, 0.4]
    decisions = decide_abstention(qualities, confidences, threshold=0.8, warning_delta=0.1)
    
    print("Abstention decisions:", decisions)
    expected_decisions = ["accept", "abstain_low_quality_confidence", "abstain_quality_fail", "abstain_low_confidence"]
    assert decisions == expected_decisions, f"Expected {expected_decisions}, got {decisions}"
    
    print("\nAll tests passed successfully!")

if __name__ == "__main__":
    main()
