"""Day 32 — Grouped CV tests.

Verifies:
  • No group overlap between train and validation in any fold
  • Correct number of folds created
  • ValueError on insufficient groups
  • Fold stability (same seed → same folds)
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "modeling"))

import numpy as np
import pytest

from day32.grouped_cv import make_grouped_folds


def test_no_group_overlap():
    y = np.array(["a", "a", "b", "b"] * 6)
    groups = np.repeat([f"S{i}" for i in range(12)], 2)
    folds = make_grouped_folds(y, groups, n_splits=3)
    for fold in folds:
        assert set(fold["train_groups"]).isdisjoint(fold["validation_groups"])


def test_correct_fold_count():
    y = np.array(["a", "a", "b", "b"] * 6)
    groups = np.repeat([f"S{i}" for i in range(12)], 2)
    folds = make_grouped_folds(y, groups, n_splits=3)
    assert len(folds) == 3


def test_fold_count_five():
    y = np.array(["a", "b"] * 10)
    groups = np.repeat([f"S{i}" for i in range(10)], 2)
    folds = make_grouped_folds(y, groups, n_splits=5)
    assert len(folds) == 5
    for fold in folds:
        assert set(fold["train_groups"]).isdisjoint(fold["validation_groups"])


def test_insufficient_groups_raises():
    y = np.array(["a", "b"])
    groups = np.array(["S1", "S2"])
    with pytest.raises(ValueError, match="Not enough groups"):
        make_grouped_folds(y, groups, n_splits=5)


def test_fold_stability():
    """Same seed must produce identical folds."""
    y = np.array(["a", "a", "b", "b"] * 6)
    groups = np.repeat([f"S{i}" for i in range(12)], 2)
    folds1 = make_grouped_folds(y, groups, n_splits=3, seed=3201)
    folds2 = make_grouped_folds(y, groups, n_splits=3, seed=3201)
    for f1, f2 in zip(folds1, folds2):
        assert f1["train_indices"] == f2["train_indices"]
        assert f1["validation_indices"] == f2["validation_indices"]


def test_all_indices_covered():
    """Union of all train/validation indices must cover all samples."""
    y = np.array(["a", "a", "b", "b"] * 6)
    groups = np.repeat([f"S{i}" for i in range(12)], 2)
    folds = make_grouped_folds(y, groups, n_splits=3)
    all_valid = set()
    for fold in folds:
        all_valid.update(fold["validation_indices"])
    assert all_valid == set(range(len(y)))
