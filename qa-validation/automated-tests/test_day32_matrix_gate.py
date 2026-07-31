"""Day 32 — Matrix gate tests.

Verifies:
  • Valid matrices pass
  • Pooled datasets are blocked
  • Non-finite values are blocked
  • Dimension mismatches are blocked
  • Insufficient groups/classes are blocked
  • F-NO-MOMENTS12 dimensions are recognized
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "modeling"))

import numpy as np

from day32.matrix_gate import EXPECTED_DIMENSIONS, validate_matrix


def test_valid_mendeley_td8_matrix():
    X = np.ones((20, 24))
    y = np.array(["a", "b"] * 10)
    groups = np.array([f"S{i // 2}" for i in range(20)])
    datasets = np.array(["mendeley"] * 20)
    result = validate_matrix(
        X, y, groups, datasets, "mendeley_core4_primary_v1", "F-TD8"
    )
    assert result["pass"]
    assert result["feature_count"] == 24
    assert result["errors"] == []


def test_pooled_dataset_is_blocked():
    X = np.ones((4, 24))
    y = np.array(["a", "b", "a", "b"])
    groups = np.array(["s1", "s2", "s3", "s4"])
    datasets = np.array(["m", "m", "g", "g"])
    result = validate_matrix(
        X, y, groups, datasets, "mendeley_core4_primary_v1", "F-TD8"
    )
    assert not result["pass"]
    assert any("POOLED_DATASET_BLOCKED" in e for e in result["errors"])


def test_nonfinite_matrix_is_blocked():
    X = np.ones((4, 24))
    X[0, 0] = np.nan
    result = validate_matrix(
        X,
        np.array(["a", "b", "a", "b"]),
        np.array(["s1", "s2", "s3", "s4"]),
        np.array(["m"] * 4),
        "mendeley_core4_primary_v1",
        "F-TD8",
    )
    assert any("NONFINITE_MATRIX" in e for e in result["errors"])


def test_inf_matrix_is_blocked():
    X = np.ones((4, 24))
    X[1, 2] = np.inf
    result = validate_matrix(
        X,
        np.array(["a", "b", "a", "b"]),
        np.array(["s1", "s2", "s3", "s4"]),
        np.array(["m"] * 4),
        "mendeley_core4_primary_v1",
        "F-TD8",
    )
    assert not result["pass"]
    assert any("NONFINITE_MATRIX" in e for e in result["errors"])


def test_dimension_mismatch_is_blocked():
    X = np.ones((4, 10))  # Expected 24, got 10
    result = validate_matrix(
        X,
        np.array(["a", "b", "a", "b"]),
        np.array(["s1", "s2", "s3", "s4"]),
        np.array(["m"] * 4),
        "mendeley_core4_primary_v1",
        "F-TD8",
    )
    assert not result["pass"]
    assert any("MATRIX_DIMENSION_MISMATCH" in e for e in result["errors"])


def test_insufficient_groups_is_blocked():
    X = np.ones((4, 24))
    result = validate_matrix(
        X,
        np.array(["a", "b", "a", "b"]),
        np.array(["s1", "s1", "s1", "s1"]),  # Only 1 group
        np.array(["m"] * 4),
        "mendeley_core4_primary_v1",
        "F-TD8",
    )
    assert not result["pass"]
    assert "insufficient_groups" in result["errors"]


def test_insufficient_classes_is_blocked():
    X = np.ones((4, 24))
    result = validate_matrix(
        X,
        np.array(["a", "a", "a", "a"]),  # Only 1 class
        np.array(["s1", "s2", "s3", "s4"]),
        np.array(["m"] * 4),
        "mendeley_core4_primary_v1",
        "F-TD8",
    )
    assert not result["pass"]
    assert "insufficient_classes" in result["errors"]


def test_f_no_moments12_dimensions_recognized():
    """F-NO-MOMENTS12 must be in EXPECTED_DIMENSIONS for both datasets."""
    assert ("mendeley_core4_primary_v1", "F-NO-MOMENTS12") in EXPECTED_DIMENSIONS
    assert EXPECTED_DIMENSIONS[("mendeley_core4_primary_v1", "F-NO-MOMENTS12")] == 36
    assert ("grabmyo_project_subset_native28_v1", "F-NO-MOMENTS12") in EXPECTED_DIMENSIONS
    assert EXPECTED_DIMENSIONS[("grabmyo_project_subset_native28_v1", "F-NO-MOMENTS12")] == 336


def test_grabmyo_all14_dimension():
    X = np.ones((10, 392))
    y = np.array(["a", "b"] * 5)
    groups = np.array([f"S{i}" for i in range(10)])
    datasets = np.array(["grabmyo"] * 10)
    result = validate_matrix(
        X, y, groups, datasets,
        "grabmyo_project_subset_native28_v1", "F-ALL14",
    )
    assert result["pass"]
    assert result["feature_count"] == 392
