from __future__ import annotations

import json
from collections import Counter, defaultdict


def _loads(value, default):
    if value in (None, ""):
        return default
    if isinstance(value, (list, dict)):
        return value
    return json.loads(value)


def _score_get(scores, cls):
    return scores[str(cls)] if str(cls) in scores else scores[cls]


def _argmax(scores, order):
    return max(order, key=lambda cls: (scores.get(str(cls), scores.get(cls, float("-inf"))), -order.index(cls)))


def _majority(labels, order):
    counts = Counter(labels)
    return max(order, key=lambda cls: (counts.get(str(cls), 0), -order.index(cls)))


def aggregate_predictions(rows):
    buckets = defaultdict(list)
    for row in rows:
        key = (
            row["dataset_id"],
            row["dataset_view_id"],
            row["run_id"],
            row["model_id"],
            row["feature_arm"],
            int(row["outer_fold"]),
            row["subject_id"],
            row.get("day_id", ""),
            row.get("session_id", ""),
            row["repetition_id"],
        )
        buckets[key].append(row)

    output = []
    for key, items in buckets.items():
        truths = {str(row["y_true"]) for row in items}
        if len(truths) != 1:
            raise ValueError("LABEL_INCONSISTENCY")
        types = {str(row["score_type"]) for row in items}
        if len(types) != 1:
            raise ValueError("mixed_score_type")
        score_type = next(iter(types))
        order = [str(cls) for cls in _loads(items[0]["class_order_json"], [])]
        window_preds = [str(row["y_pred"]) for row in items]
        confidence = None
        margin = None

        if score_type in {"probability", "decision_function"}:
            means = {cls: 0.0 for cls in order}
            for row in items:
                scores = _loads(row["class_scores_json"], {})
                for cls in order:
                    means[cls] += float(_score_get(scores, cls))
            for cls in order:
                means[cls] /= len(items)
            pred = str(_argmax(means, order))
            ranked = sorted(means.values(), reverse=True)
            margin = float(ranked[0] - ranked[1])
            if score_type == "probability":
                confidence = float(ranked[0])
            method = "mean_probability" if score_type == "probability" else "mean_decision_function"
        else:
            pred = str(_majority(window_preds, order))
            method = "deterministic_majority_vote"

        top = max(Counter(window_preds).values())
        disagreement = 1.0 - top / len(window_preds)
        qc = sorted({flag for row in items for flag in _loads(row.get("qc_flags_json"), [])})
        source_window_counts = []
        for row in items:
            raw = row.get("source_window_count")
            if raw not in (None, ""):
                source_window_counts.append(int(float(raw)))
        window_count = max(source_window_counts) if len(items) == 1 and source_window_counts else len(items)
        output.append({
            "dataset_id": key[0],
            "dataset_view_id": key[1],
            "run_id": key[2],
            "model_id": key[3],
            "feature_arm": key[4],
            "outer_fold": key[5],
            "subject_id": key[6],
            "day_id": key[7],
            "session_id": key[8],
            "repetition_id": key[9],
            "y_true": next(iter(truths)),
            "y_pred": pred,
            "aggregation_method": method,
            "window_count": window_count,
            "window_prediction_rows": len(items),
            "window_disagreement": disagreement,
            "probability_confidence": confidence,
            "top2_margin": margin,
            "score_type": score_type,
            "qc_flags": qc,
            "source_matrix_sha256": items[0]["source_matrix_sha256"],
            "fold_manifest_sha256": items[0]["fold_manifest_sha256"],
            "model_config_sha256": items[0]["model_config_sha256"],
            "class_order": order,
        })
    return sorted(output, key=lambda row: (row["run_id"], row["outer_fold"], row["subject_id"], row["repetition_id"]))
