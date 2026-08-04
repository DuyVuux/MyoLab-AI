import sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "quantitative"))
from day37.similarity import cosine_similarity, pearson_similarity, normalized_euclidean

def test_same_direction():
    value, reason = cosine_similarity([1,2,3], [2,4,6])
    assert reason is None and abs(value - 1.0) < 1e-12

def test_zero_norm_blocked():
    value, reason = cosine_similarity([0,0], [1,2])
    assert value is None and reason == "ZERO_NORM_VECTOR"

def test_constant_pearson_blocked():
    value, reason = pearson_similarity([1,1,1], [1,2,3])
    assert value is None and reason == "CONSTANT_VECTOR"

def test_normalized_euclidean():
    assert normalized_euclidean([0,0], [1,1]) == 1.0
