import sys
import time
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core/personalization"))

from day34.fewshot import make_fewshot_split, class_centroids, nearest_centroid_predict

def run_stress_test():
    print("Starting Day 34 Few-Shot Module Stress Test...")
    np.random.seed(42)
    
    # 1. Stress test make_fewshot_split
    print("\n--- Testing make_fewshot_split ---")
    N_SAMPLES = 100_000
    N_ITERATIONS = 100
    
    subjects = np.array([f"Subject_{i%50}" for i in range(N_SAMPLES)])
    labels = np.array([f"Class_{i%7}" for i in range(N_SAMPLES)])
    repetitions = np.array([f"Rep_{i%200}" for i in range(N_SAMPLES)])
    
    start_time = time.time()
    for i in range(N_ITERATIONS):
        # Pick a random subject
        subj = f"Subject_{i%50}"
        try:
            cal, eva = make_fewshot_split(subjects, labels, repetitions, subj, k=2, seed=i)
        except ValueError:
            # Might not have enough repetitions for all classes in this random distribution, that's fine
            pass
    split_time = time.time() - start_time
    print(f"make_fewshot_split completed {N_ITERATIONS} iterations on {N_SAMPLES} samples in {split_time:.4f} seconds.")

    # 2. Stress test nearest_centroid_predict
    print("\n--- Testing nearest_centroid_predict ---")
    N_VECTORS = 50_000
    N_FEATURES = 128
    N_CLASSES = 10
    
    X = np.random.rand(N_VECTORS, N_FEATURES)
    y = np.array([f"Class_{i%N_CLASSES}" for i in range(N_VECTORS)])
    
    start_time = time.time()
    centroids = class_centroids(X, y)
    centroid_time = time.time() - start_time
    print(f"class_centroids calculated for {N_VECTORS} vectors in {centroid_time:.4f} seconds.")
    
    X_test = np.random.rand(100_000, N_FEATURES)
    
    start_time = time.time()
    predictions = nearest_centroid_predict(X_test, centroids)
    predict_time = time.time() - start_time
    print(f"nearest_centroid_predict computed {len(X_test)} predictions in {predict_time:.4f} seconds.")
    
    print("\nStress Test Completed Successfully!")

if __name__ == "__main__":
    run_stress_test()
