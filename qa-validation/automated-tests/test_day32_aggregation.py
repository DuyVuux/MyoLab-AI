"""Day 32 — Aggregation tests.

Verifies:
  • Majority vote aggregation produces correct repetition rows
  • Probability aggregation selects correct class
  • Deterministic tie-breaking by class_order position
  • Subject-level metric computation
  • aggregation_method field is set correctly
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "modeling"))

import numpy as np

from day32.aggregation import (
    aggregate_window_labels,
    aggregate_window_probabilities,
    deterministic_majority_vote,
)
from day32.metrics import subject_macro_repetition_macro_f1


def test_repetition_aggregation_and_subject_metric():
    rows = aggregate_window_labels(
        predictions=["a", "a", "b", "b", "a", "b"],
        repetition_ids=["r1", "r1", "r2", "r2", "r3", "r3"],
        subject_ids=["s1", "s1", "s1", "s1", "s2", "s2"],
        true_labels=["a", "a", "b", "b", "a", "a"],
        class_order=["a", "b"],
    )
    result = subject_macro_repetition_macro_f1(rows, ["a", "b"])
    assert len(rows) == 3
    assert 0 <= result["subject_macro_repetition_macro_f1"] <= 1
    assert all(r["aggregation_method"] == "majority_vote" for r in rows)


def test_deterministic_tie_breaking():
    """When tied, earlier class_order wins."""
    result = deterministic_majority_vote(["a", "b"], ["a", "b"])
    assert result == "a"  # "a" is earlier in class_order


def test_tie_breaking_respects_order():
    """When tied with different ordering, order matters."""
    result = deterministic_majority_vote(["a", "b"], ["b", "a"])
    assert result == "b"  # "b" is earlier in this class_order


def test_probability_aggregation():
    """Mean probability path selects the class with highest mean prob."""
    class_order = ["rest", "hand_close", "wrist_flexion"]
    proba = np.array([
        [0.8, 0.1, 0.1],  # window 1: rest
        [0.6, 0.3, 0.1],  # window 2: rest
    ])
    rows = aggregate_window_probabilities(
        probabilities=proba,
        repetition_ids=["r1", "r1"],
        subject_ids=["s1", "s1"],
        true_labels=["rest", "rest"],
        class_order=class_order,
    )
    assert len(rows) == 1
    assert rows[0]["y_pred"] == "rest"
    assert rows[0]["aggregation_method"] == "mean_probability"
    assert "mean_probabilities" in rows[0]
    assert rows[0]["mean_probabilities"]["rest"] > 0.5


def test_probability_aggregation_multi_repetition():
    class_order = ["a", "b"]
    proba = np.array([
        [0.9, 0.1],  # r1
        [0.8, 0.2],  # r1
        [0.2, 0.8],  # r2
        [0.3, 0.7],  # r2
    ])
    rows = aggregate_window_probabilities(
        probabilities=proba,
        repetition_ids=["r1", "r1", "r2", "r2"],
        subject_ids=["s1", "s1", "s1", "s1"],
        true_labels=["a", "a", "b", "b"],
        class_order=class_order,
    )
    assert len(rows) == 2
    preds = {r["repetition_id"]: r["y_pred"] for r in rows}
    assert preds["r1"] == "a"
    assert preds["r2"] == "b"
