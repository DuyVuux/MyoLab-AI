"""Day 32 — Metric contract implementation.

Implements Execution Plan §7 (Metric Contract):
  Primary:  subject_macro_repetition_macro_f1
  Secondary: repetition-level macro-F1, balanced accuracy, per-class metrics,
             confusion matrix, worst-subject macro-F1, worst-class recall.
"""
from __future__ import annotations

from collections import defaultdict

import numpy as np
from sklearn.metrics import (
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)


def repetition_metrics(
    rows: list[dict],
    class_order: list[str],
) -> dict:
    """Compute repetition-level metrics from aggregated prediction rows.

    Parameters
    ----------
    rows : list[dict]
        Each dict must have ``y_true`` and ``y_pred`` keys.
    class_order : list[str]
        Canonical class label ordering.

    Returns
    -------
    dict
        Contains repetition_macro_f1, balanced_accuracy, per_class metrics,
        confusion_matrix, and worst_class_recall.
    """
    y_true = [r["y_true"] for r in rows]
    y_pred = [r["y_pred"] for r in rows]

    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=class_order, zero_division=0
    )

    per_class = {
        label: {
            "precision": float(precision[i]),
            "recall": float(recall[i]),
            "f1": float(f1[i]),
            "support": int(support[i]),
        }
        for i, label in enumerate(class_order)
    }

    recalls = [per_class[c]["recall"] for c in class_order if per_class[c]["support"] > 0]

    return {
        "repetition_macro_f1": float(
            f1_score(y_true, y_pred, labels=class_order, average="macro", zero_division=0)
        ),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "per_class": per_class,
        "confusion_matrix": confusion_matrix(
            y_true, y_pred, labels=class_order
        ).tolist(),
        "worst_class_recall": float(min(recalls)) if recalls else float("nan"),
    }


def subject_macro_repetition_macro_f1(
    rows: list[dict],
    class_order: list[str],
) -> dict:
    """Compute the primary Day 32 metric: subject-macro repetition-macro F1.

    Each subject has equal weight, preventing subjects with many windows
    from dominating the aggregate score.

    Parameters
    ----------
    rows : list[dict]
        Aggregated repetition-level predictions with ``subject_id``,
        ``y_true``, and ``y_pred``.
    class_order : list[str]
        Canonical class label ordering.

    Returns
    -------
    dict
        Contains the headline metric, per-subject scores,
        worst-subject macro-F1, mean, and std.
    """
    by_subject: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_subject[row["subject_id"]].append(row)

    scores: dict[str, float] = {}
    for subject_id, subject_rows in by_subject.items():
        y_true = [r["y_true"] for r in subject_rows]
        y_pred = [r["y_pred"] for r in subject_rows]
        scores[subject_id] = float(
            f1_score(
                y_true, y_pred,
                labels=class_order, average="macro", zero_division=0,
            )
        )

    values = list(scores.values())
    return {
        "subject_macro_repetition_macro_f1": float(np.mean(values)) if values else float("nan"),
        "subject_scores": scores,
        "worst_subject_macro_f1": float(min(values)) if values else float("nan"),
        "subject_count": len(scores),
        "fold_mean": float(np.mean(values)) if values else float("nan"),
        "fold_std": float(np.std(values)) if values else float("nan"),
    }
