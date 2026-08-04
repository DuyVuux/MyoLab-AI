import sys
import os
import time
import numpy as np

# Ensure ai-core can import its own modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from calibration import TemperatureScaler, PlattOVR, IsotonicOVR
from calibration import decide_abstention
from calibration import multiclass_brier, expected_calibration_error, coverage_risk

def run_stress_test():
    print("="*50)
    print("DAY 35 STRESS TEST: CALIBRATION & ABSTENTION")
    print("="*50)
    
    # ---------------------------------------------------------
    # TEST 1: Large Scale Data (Performance & Memory Stress)
    # ---------------------------------------------------------
    print("\n[TEST 1] Large Scale Data (500,000 samples, 5 classes)")
    N = 500_000
    C = 5
    np.random.seed(99)
    y_large = np.random.randint(0, C, size=N)
    logits_large = np.random.randn(N, C) * 5.0 # Large variance
    
    start_t = time.time()
    ts = TemperatureScaler()
    ts.fit(logits_large, y_large)
    preds_ts = ts.predict_proba(logits_large)
    dur_ts = time.time() - start_t
    print(f"  TemperatureScaler Fit+Predict: {dur_ts:.3f} seconds (T={ts.temperature_:.4f})")
    
    start_t = time.time()
    platt = PlattOVR()
    platt.fit(logits_large, y_large)
    preds_platt = platt.predict_proba(logits_large)
    dur_platt = time.time() - start_t
    print(f"  PlattOVR Fit+Predict: {dur_platt:.3f} seconds")
    
    start_t = time.time()
    iso = IsotonicOVR()
    # Fit iso on probs to simulate real pipeline
    iso.fit(preds_ts, y_large)
    preds_iso = iso.predict_proba(preds_ts)
    dur_iso = time.time() - start_t
    print(f"  IsotonicOVR Fit+Predict: {dur_iso:.3f} seconds")
    
    # Verify sums to 1
    assert np.allclose(preds_platt.sum(axis=1), 1.0), "PlattOVR probabilities do not sum to 1"
    assert np.allclose(preds_iso.sum(axis=1), 1.0), "IsotonicOVR probabilities do not sum to 1"
    print("  -> Passed: Scalability and normalization OK.")

    # ---------------------------------------------------------
    # TEST 2: Extreme Probabilities & Math Stability
    # ---------------------------------------------------------
    print("\n[TEST 2] Extreme Probabilities (log(0) and division by zero stress)")
    logits_extreme = np.array([
        [1000.0, -1000.0, -1000.0],
        [-1000.0, 1000.0, -1000.0],
        [-1000.0, -1000.0, 1000.0]
    ])
    y_extreme = np.array([0, 1, 2])
    ts_ext = TemperatureScaler().fit(logits_extreme, y_extreme)
    probs_ext = ts_ext.predict_proba(logits_extreme)
    
    brier = multiclass_brier(y_extreme, probs_ext)
    print(f"  Extreme Brier (should be 0.0): {brier}")
    assert not np.isnan(brier), "Brier score returned NaN"
    print("  -> Passed: No log(0) or overflow/underflow crashes.")

    # ---------------------------------------------------------
    # TEST 3: Edge Case Metrics (Empty Bins & Zero Accepted)
    # ---------------------------------------------------------
    print("\n[TEST 3] Edge Case Metrics (Zero Accepted & Empty Bins)")
    # Probs all perfectly 0.33, true is 0, so confidence is exactly 0.33
    probs_empty = np.array([[0.33, 0.33, 0.34]] * 100)
    y_empty = np.zeros(100, dtype=int)
    
    # ECE with many bins (most will be empty)
    ece, bins = expected_calibration_error(y_empty, probs_empty, n_bins=20)
    empty_bin_count = sum(1 for b in bins if b['count'] == 0)
    print(f"  ECE: {ece:.4f}, Empty bins handled: {empty_bin_count}/20")
    assert empty_bin_count > 0, "Expected empty bins but found none"
    assert not np.isnan(ece), "ECE returned NaN"
    
    # Coverage risk with unreachable threshold
    cr = coverage_risk(y_empty, probs_empty, thresholds=[0.0, 0.5, 0.99])
    print(f"  Coverage Risk at 0.99 (should have NaN accuracy/risk): {cr[2]}")
    import math
    assert math.isnan(cr[2]['selective_accuracy']), "Did not return NaN for 0 accepted cases"
    print("  -> Passed: Safe division mechanisms work properly.")

    # ---------------------------------------------------------
    # TEST 4: Abstention Logic Vectorization & Types
    # ---------------------------------------------------------
    print("\n[TEST 4] Abstention Logic Stress")
    N_abs = 100_000
    qualities = np.random.choice(["pass", "warning", "fail"], size=N_abs)
    confidences = np.random.rand(N_abs)
    
    start_t = time.time()
    decisions = decide_abstention(qualities, confidences, threshold=0.7, warning_delta=0.1)
    dur_abs = time.time() - start_t
    
    assert len(decisions) == N_abs, "Abstention returned wrong shape"
    print(f"  Abstention processed {N_abs} rows in {dur_abs:.3f} seconds")
    
    # Quick sanity check on logic
    fail_idx = np.where(qualities == "fail")[0][0]
    assert decisions[fail_idx] == "abstain_quality_fail"
    print("  -> Passed: Abstention vectorization and mapping OK.")

    print("\n" + "="*50)
    print("ALL STRESS TESTS PASSED WITHOUT EXCEPTION.")
    print("="*50)


if __name__ == "__main__":
    run_stress_test()
