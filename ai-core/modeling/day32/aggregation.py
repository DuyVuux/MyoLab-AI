"""Day 32 — Window-to-repetition aggregation with three priority paths.

Implements Execution Plan §7.4 (Aggregation Prediction):
  1. Mean class probability  (predict_proba)
  2. Mean decision score     (decision_function)
  3. Deterministic majority vote (label only — fallback)

Tie-breaking is deterministic: uses class_order index as secondary key
so that ties always resolve to the same class regardless of platform.
"""
from __future__ import annotations

from collections import Counter, defaultdict

import numpy as np


# ---------------------------------------------------------------------------
# Deterministic majority vote  (Path 3 — fallback)
# ---------------------------------------------------------------------------

def deterministic_majority_vote(
    labels: list,
    class_order: list[str],
) -> str:
    """Pick the majority label, breaking ties by class_order position."""
    counts = Counter(labels)
    return max(
        class_order,
        key=lambda c: (counts.get(c, 0), -class_order.index(c)),
    )


# ---------------------------------------------------------------------------
# Window → repetition aggregation
# ---------------------------------------------------------------------------

def aggregate_window_labels(
    predictions: list,
    repetition_ids: list,
    subject_ids: list,
    true_labels: list,
    class_order: list[str],
) -> list[dict]:
    """Aggregate window-level label predictions to repetition level.

    Uses deterministic majority vote (Path 3).
    """
    buckets: dict[tuple, list] = defaultdict(list)
    truth: dict[tuple, str] = {}
    subject: dict[tuple, str] = {}

    for pred, rep, subj, true_label in zip(
        predictions, repetition_ids, subject_ids, true_labels
    ):
        key = (subj, rep)
        buckets[key].append(pred)
        truth[key] = true_label
        subject[key] = subj

    rows = []
    for key, values in buckets.items():
        rows.append({
            "subject_id": subject[key],
            "repetition_id": key[1],
            "y_true": truth[key],
            "y_pred": deterministic_majority_vote(values, class_order),
            "window_count": len(values),
            "aggregation_method": "majority_vote",
        })
    return rows


def aggregate_window_probabilities(
    probabilities: np.ndarray,
    repetition_ids: list,
    subject_ids: list,
    true_labels: list,
    class_order: list[str],
) -> list[dict]:
    """Aggregate window-level class probabilities to repetition level.

    Uses mean class probability (Path 1 — preferred).

    Parameters
    ----------
    probabilities : np.ndarray
        Shape (n_windows, n_classes). Each row is the probability
        distribution over classes for one window.
    """
    probabilities = np.asarray(probabilities)
    buckets: dict[tuple, list[int]] = defaultdict(list)
    truth: dict[tuple, str] = {}
    subject: dict[tuple, str] = {}

    for idx, (rep, subj, true_label) in enumerate(
        zip(repetition_ids, subject_ids, true_labels)
    ):
        key = (subj, rep)
        buckets[key].append(idx)
        truth[key] = true_label
        subject[key] = subj

    rows = []
    for key, indices in buckets.items():
        mean_proba = probabilities[indices].mean(axis=0)
        # Deterministic tie-breaking: argmax picks first occurrence
        pred_idx = int(np.argmax(mean_proba))
        rows.append({
            "subject_id": subject[key],
            "repetition_id": key[1],
            "y_true": truth[key],
            "y_pred": class_order[pred_idx],
            "window_count": len(indices),
            "aggregation_method": "mean_probability",
            "mean_probabilities": {
                c: float(mean_proba[i]) for i, c in enumerate(class_order)
            },
        })
    return rows
