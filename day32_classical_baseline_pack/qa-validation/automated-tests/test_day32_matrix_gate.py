import numpy as np
from day32.matrix_gate import validate_matrix

def test_valid_mendeley_td8_matrix():
    X = np.ones((20, 24))
    y = np.array(["a", "b"] * 10)
    groups = np.array([f"S{i//2}" for i in range(20)])
    datasets = np.array(["mendeley"] * 20)
    result = validate_matrix(X, y, groups, datasets, "mendeley_core4_primary_v1", "F-TD8")
    assert result["pass"]

def test_pooled_dataset_is_blocked():
    X = np.ones((4, 24))
    y = np.array(["a", "b", "a", "b"])
    groups = np.array(["s1", "s2", "s3", "s4"])
    datasets = np.array(["m", "m", "g", "g"])
    result = validate_matrix(X, y, groups, datasets, "mendeley_core4_primary_v1", "F-TD8")
    assert not result["pass"]
    assert any("POOLED_DATASET_BLOCKED" in e for e in result["errors"])

def test_nonfinite_matrix_is_blocked():
    X = np.ones((4, 24)); X[0, 0] = np.nan
    result = validate_matrix(
        X, np.array(["a","b","a","b"]),
        np.array(["s1","s2","s3","s4"]),
        np.array(["m"]*4),
        "mendeley_core4_primary_v1", "F-TD8"
    )
    assert "NONFINITE_MATRIX" in result["errors"]
