import numpy as np
import time
import sys
from transfer.domain_gap import rbf_mmd
from transfer.representation import channel_summary_representation

def stress_test_mmd():
    print("Stress Testing MMD (O(N^2) memory complexity)...")
    # 2000 samples, 40 features is large enough to test speed, small enough not to blow up smaller machines
    N = 2000
    s = np.random.rand(N, 40)
    t = np.random.rand(N, 40)
    
    start = time.time()
    try:
        mmd, gamma = rbf_mmd(s, t)
        duration = time.time() - start
        print(f"PASS: MMD calculated in {duration:.4f} seconds for N={N}. Value={mmd:.4f}")
        assert duration < 5.0, "MMD computation is too slow"
    except MemoryError:
        print("FAIL: Memory explosion detected in cdist.")
        sys.exit(1)
        
def stress_test_representation_zeros_and_extremes():
    print("Stress Testing Channel Representation...")
    # All zeros
    x_zeros = np.zeros((1000, 392, 14))
    res = channel_summary_representation(x_zeros)
    assert np.all(np.isfinite(res)), "Zero array produced non-finite values."
    
    # Large numbers
    x_large = np.ones((1000, 392, 14)) * 1e10
    res2 = channel_summary_representation(x_large)
    assert np.all(np.isfinite(res2)), "Large array produced non-finite values."
    print("PASS: Channel Representation handles extremes.")

def stress_test_mmd_empty():
    print("Stress Testing MMD with empty arrays...")
    s = np.empty((0, 40))
    t = np.random.rand(10, 40)
    try:
        rbf_mmd(s, t)
        print("FAIL: Empty array check failed.")
        sys.exit(1)
    except ValueError as e:
        if "must not be empty" in str(e):
            print("PASS: Empty array correctly raises ValueError.")
        else:
            print("FAIL: Wrong ValueError raised.")
            sys.exit(1)

if __name__ == "__main__":
    print("--- STARTING TRANSFER MODULE STRESS TESTS ---")
    stress_test_mmd()
    stress_test_representation_zeros_and_extremes()
    stress_test_mmd_empty()
    print("--- ALL STRESS TESTS PASSED ---")
