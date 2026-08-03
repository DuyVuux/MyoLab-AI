from __future__ import annotations

from collections import defaultdict

from sklearn.metrics import balanced_accuracy_score, f1_score, recall_score


def evaluate_by_day(rows):
    buckets = defaultdict(list)
    for row in rows:
        day_id = row.get("day_id", "")
        session_id = row.get("session_id", "")
        if day_id or session_id:
            buckets[(row.get("model_id", ""), row.get("feature_arm", ""), day_id, session_id)].append(row)
    out = []
    for (model_id, feature_arm, day_id, session_id), group in sorted(buckets.items()):
        order = group[0]["class_order"]
        y_true = [row["y_true"] for row in group]
        y_pred = [row["y_pred"] for row in group]
        recalls = recall_score(y_true, y_pred, labels=order, average=None, zero_division=0)
        out.append({
            "model_id": model_id,
            "feature_arm": feature_arm,
            "day_id": day_id,
            "session_id": session_id,
            "macro_f1": float(f1_score(y_true, y_pred, labels=order, average="macro", zero_division=0)),
            "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
            "per_class_recall": {cls: float(recalls[i]) for i, cls in enumerate(order)},
            "subject_count": len({row["subject_id"] for row in group}),
            "repetition_count": len(group),
            "fatigue_inference_allowed": False,
        })
    return out
