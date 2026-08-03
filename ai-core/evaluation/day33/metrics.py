from __future__ import annotations

from collections import defaultdict

import numpy as np
from sklearn.metrics import (
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)


def _calc(y_true, y_pred, order):
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=order, zero_division=0
    )
    return {
        "macro_f1": float(f1_score(y_true, y_pred, labels=order, average="macro", zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "per_class": {
            cls: {
                "precision": float(precision[i]),
                "recall": float(recall[i]),
                "f1": float(f1[i]),
                "support": int(support[i]),
            }
            for i, cls in enumerate(order)
        },
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=order).tolist(),
    }


def _summary(values):
    arr = np.asarray(values, dtype=float)
    return {
        "mean": float(arr.mean()),
        "median": float(np.median(arr)),
        "std": float(arr.std(ddof=1)) if len(arr) > 1 else 0.0,
        "p10": float(np.quantile(arr, 0.1)),
        "minimum": float(arr.min()),
        "maximum": float(arr.max()),
    }


def evaluate_repetitions(rows):
    if not rows:
        raise ValueError("no_rows")
    order = rows[0]["class_order"]
    repetition = _calc([r["y_true"] for r in rows], [r["y_pred"] for r in rows], order)

    buckets = defaultdict(list)
    for row in rows:
        buckets[row["subject_id"]].append(row)

    subjects = []
    for subject_id, subject_rows in sorted(buckets.items()):
        metrics = _calc([r["y_true"] for r in subject_rows], [r["y_pred"] for r in subject_rows], order)
        subjects.append({
            "subject_id": subject_id,
            "repetition_count": len(subject_rows),
            "class_coverage": sorted({r["y_true"] for r in subject_rows}),
            "macro_f1": metrics["macro_f1"],
            "balanced_accuracy": metrics["balanced_accuracy"],
            "per_class": metrics["per_class"],
            "error_count": sum(r["y_true"] != r["y_pred"] for r in subject_rows),
            "high_disagreement_count": sum(r["window_disagreement"] >= 0.45 for r in subject_rows),
            "high_confidence_error_count": sum(
                r["y_true"] != r["y_pred"]
                and r["score_type"] == "probability"
                and r["probability_confidence"] is not None
                and r["probability_confidence"] >= 0.8
                for r in subject_rows
            ),
        })

    subject_values = [s["macro_f1"] for s in subjects]
    subject_summary = _summary(subject_values)
    subject_summary.update({
        "subject_macro_repetition_macro_f1": subject_summary["mean"],
        "worst_subject_id": min(subjects, key=lambda item: item["macro_f1"])["subject_id"],
        "bottom_quartile_subject_ids": [
            s["subject_id"] for s in sorted(subjects, key=lambda item: item["macro_f1"])[: max(1, int(np.ceil(len(subjects) * 0.25)))]
        ],
        "subject_count": len(subjects),
    })

    fold_buckets = defaultdict(list)
    for row in rows:
        fold_buckets[row.get("outer_fold", 0)].append(row)
    fold_metrics = []
    for fold, fold_rows in sorted(fold_buckets.items()):
        metrics = _calc([r["y_true"] for r in fold_rows], [r["y_pred"] for r in fold_rows], order)
        fold_metrics.append({
            "outer_fold": fold,
            "macro_f1": metrics["macro_f1"],
            "balanced_accuracy": metrics["balanced_accuracy"],
            "subject_count": len({r["subject_id"] for r in fold_rows}),
            "class_coverage": sorted({r["y_true"] for r in fold_rows}),
            "repetition_count": len(fold_rows),
        })
    fold_values = [f["macro_f1"] for f in fold_metrics]
    fold_summary = _summary(fold_values) if fold_values else {}

    return {
        "schema_version": "day33-evaluation-result.v1",
        "class_order": order,
        "repetition_metrics": repetition,
        "subject_metrics": subjects,
        "subject_summary": subject_summary,
        "fold_metrics": fold_metrics,
        "fold_summary": fold_summary,
        "repetition_count": len(rows),
        "invalid_repetition_count": 0,
    }


def per_class_rows(metrics):
    return [
        {"class_label": cls, **values}
        for cls, values in metrics["repetition_metrics"]["per_class"].items()
    ]


def confusion_rows(metrics):
    order = metrics["class_order"]
    rows = []
    for i, true_label in enumerate(order):
        for j, pred_label in enumerate(order):
            rows.append({
                "y_true": true_label,
                "y_pred": pred_label,
                "count": metrics["repetition_metrics"]["confusion_matrix"][i][j],
            })
    return rows


def subject_metric_rows(metrics):
    rows = []
    for item in metrics["subject_metrics"]:
        rows.append({
            "subject_id": item["subject_id"],
            "repetition_count": item["repetition_count"],
            "class_coverage": item["class_coverage"],
            "macro_f1": item["macro_f1"],
            "balanced_accuracy": item["balanced_accuracy"],
            "error_count": item["error_count"],
            "high_disagreement_count": item["high_disagreement_count"],
            "high_confidence_error_count": item["high_confidence_error_count"],
        })
    return rows


def subject_class_recall_rows(metrics):
    rows = []
    for item in metrics["subject_metrics"]:
        for cls, values in item["per_class"].items():
            rows.append({
                "subject_id": item["subject_id"],
                "class_label": cls,
                "recall": values["recall"],
                "support": values["support"],
            })
    return rows
