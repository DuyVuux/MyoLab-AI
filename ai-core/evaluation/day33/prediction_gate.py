from __future__ import annotations

import json
import math
from collections import defaultdict

from .contracts import ALLOWED_SCORE_TYPES, ALLOWED_SPLITS, REQUIRED_COLUMNS


def _loads(value, default):
    if value in (None, ""):
        return default
    if isinstance(value, (list, dict)):
        return value
    return json.loads(value)


def validate_prediction_rows(rows, tolerance=1e-6):
    errors = []
    datasets = set()
    seen = set()
    rep_truth = defaultdict(set)
    score_types = set()
    hashes = {"source_matrix_sha256": set(), "fold_manifest_sha256": set(), "model_config_sha256": set()}
    split_counts = defaultdict(int)

    for i, row in enumerate(rows):
        missing = REQUIRED_COLUMNS - set(row)
        if missing:
            errors.append(f"row_{i}_missing:{sorted(missing)}")
            continue

        dataset_id = str(row["dataset_id"])
        datasets.add(dataset_id)
        split = str(row["split_name"]).lower()
        split_counts[split] += 1
        if split not in ALLOWED_SPLITS:
            errors.append(f"row_{i}_TEST_PARTITION_BLOCKED:{split}")

        key = (
            dataset_id,
            str(row["dataset_view_id"]),
            str(row["run_id"]),
            str(row["outer_fold"]),
            str(row["subject_id"]),
            str(row["repetition_id"]),
            str(row["window_id"]),
        )
        if key in seen:
            errors.append(f"row_{i}_DUPLICATE_WINDOW_PREDICTION")
        seen.add(key)

        rep_key = (
            dataset_id,
            str(row["run_id"]),
            str(row["outer_fold"]),
            str(row["subject_id"]),
            str(row["repetition_id"]),
        )
        rep_truth[rep_key].add(str(row["y_true"]))

        score_type = str(row["score_type"])
        score_types.add(score_type)
        if score_type not in ALLOWED_SCORE_TYPES:
            errors.append(f"row_{i}_invalid_score_type:{score_type}")
            continue

        try:
            order = _loads(row["class_order_json"], [])
        except json.JSONDecodeError:
            errors.append(f"row_{i}_invalid_class_order_json")
            continue
        if not isinstance(order, list) or len(order) < 2 or len(set(map(str, order))) != len(order):
            errors.append(f"row_{i}_invalid_class_order")

        try:
            scores = _loads(row.get("class_scores_json"), None)
        except json.JSONDecodeError:
            errors.append(f"row_{i}_invalid_score_vector_json")
            continue
        if score_type in {"probability", "decision_function"}:
            if not isinstance(scores, dict):
                errors.append(f"row_{i}_MISSING_SCORE_VECTOR")
                continue
            if set(map(str, scores)) != set(map(str, order)):
                errors.append(f"row_{i}_score_class_mismatch")
            vals = []
            for cls in order:
                try:
                    vals.append(float(scores[str(cls)] if str(cls) in scores else scores[cls]))
                except (KeyError, TypeError, ValueError):
                    errors.append(f"row_{i}_invalid_score_value")
            if any(not math.isfinite(v) for v in vals):
                errors.append(f"row_{i}_NONFINITE_SCORE")
            if score_type == "probability":
                if any(v < -tolerance for v in vals):
                    errors.append(f"row_{i}_negative_probability")
                if abs(sum(vals) - 1.0) > tolerance:
                    errors.append(f"row_{i}_probability_sum")

        try:
            qc_flags = _loads(row.get("qc_flags_json"), [])
        except json.JSONDecodeError:
            errors.append(f"row_{i}_invalid_qc_flags_json")
            qc_flags = []
        if not isinstance(qc_flags, list):
            errors.append(f"row_{i}_invalid_qc_flags")

        for name, values in hashes.items():
            hash_value = str(row[name])
            if not hash_value:
                errors.append(f"row_{i}_missing_{name}")
            values.add(hash_value)

    if len(datasets) > 1:
        errors.append(f"POOLED_RUN_BLOCKED:{sorted(datasets)}")
    for key, labels in rep_truth.items():
        if len(labels) > 1:
            errors.append(f"LABEL_INCONSISTENCY:{key}")

    return {
        "schema_version": "day33-prediction-gate.v1",
        "pass": not errors,
        "errors": errors,
        "row_count": len(rows),
        "dataset_ids": sorted(datasets),
        "split_counts": dict(sorted(split_counts.items())),
        "score_types": sorted(score_types),
        "unique_window_count": len(seen),
        "repetition_count": len(rep_truth),
        "hash_counts": {k: len(v) for k, v in hashes.items()},
        "sealed_test_rows_read": 0,
        "pooled_evaluation_executed": False,
    }
