from __future__ import annotations
from collections import defaultdict
import numpy as np
from sklearn.metrics import (
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)

def repetition_metrics(rows: list[dict], class_order: list[str]) -> dict:
    y_true = [r["y_true"] for r in rows]
    y_pred = [r["y_pred"] for r in rows]
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=class_order, zero_division=0
    )
    return {
        "repetition_macro_f1": float(f1_score(y_true, y_pred, labels=class_order, average="macro", zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "per_class": {
            label: {
                "precision": float(precision[i]),
                "recall": float(recall[i]),
                "f1": float(f1[i]),
                "support": int(support[i]),
            }
            for i, label in enumerate(class_order)
        },
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=class_order).tolist(),
    }

def subject_macro_repetition_macro_f1(rows: list[dict], class_order: list[str]) -> dict:
    by_subject = defaultdict(list)
    for row in rows:
        by_subject[row["subject_id"]].append(row)
    scores = {}
    for subject_id, subject_rows in by_subject.items():
        y_true = [r["y_true"] for r in subject_rows]
        y_pred = [r["y_pred"] for r in subject_rows]
        scores[subject_id] = float(
            f1_score(y_true, y_pred, labels=class_order, average="macro", zero_division=0)
        )
    values = list(scores.values())
    return {
        "subject_macro_repetition_macro_f1": float(np.mean(values)) if values else float("nan"),
        "subject_scores": scores,
        "worst_subject_macro_f1": float(min(values)) if values else float("nan"),
    }
