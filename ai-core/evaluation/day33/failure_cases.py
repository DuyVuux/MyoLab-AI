from __future__ import annotations

from collections import Counter
from hashlib import sha256


def top_confusion_pairs(rows, limit=10):
    counts = Counter((r["y_true"], r["y_pred"]) for r in rows if r["y_true"] != r["y_pred"])
    return [
        {"y_true": true, "y_pred": pred, "error_count": count}
        for (true, pred), count in counts.most_common(limit)
    ]


def extract_failure_cases(
    rows,
    high_confidence=0.8,
    low_margin=0.1,
    high_disagreement=0.45,
    min_windows=2,
    systematic_pairs=None,
):
    systematic_pairs = set(systematic_pairs or [])
    out = []
    for row in rows:
        codes = []
        wrong = row["y_true"] != row["y_pred"]
        if wrong:
            codes.append("MISCLASSIFIED_REPETITION")
        if (row["y_true"], row["y_pred"]) in systematic_pairs:
            codes.append("SYSTEMATIC_CLASS_CONFUSION")
        if (
            wrong
            and row["score_type"] == "probability"
            and row["probability_confidence"] is not None
            and row["probability_confidence"] >= high_confidence
        ):
            codes.append("HIGH_CONFIDENCE_ERROR")
        if wrong and row["top2_margin"] is not None and row["top2_margin"] <= low_margin:
            codes.append("LOW_MARGIN_ERROR")
        if row["window_disagreement"] >= high_disagreement:
            codes.append("HIGH_WINDOW_DISAGREEMENT")
        if row["qc_flags"]:
            codes.append("QC_ASSOCIATED_ERROR" if wrong else "QC_ASSOCIATED_CASE")
        if row["window_count"] < min_windows:
            codes.append("INSUFFICIENT_WINDOWS")
        if not codes:
            continue
        token = "|".join([
            row["dataset_id"],
            row["run_id"],
            str(row["outer_fold"]),
            row["subject_id"],
            row["repetition_id"],
            ",".join(sorted(codes)),
        ])
        out.append({
            "case_id": sha256(token.encode()).hexdigest()[:20],
            "dataset_id": row["dataset_id"],
            "dataset_view_id": row["dataset_view_id"],
            "run_id": row["run_id"],
            "model_id": row["model_id"],
            "feature_arm": row["feature_arm"],
            "outer_fold": row["outer_fold"],
            "subject_id": row["subject_id"],
            "day_id": row["day_id"],
            "session_id": row["session_id"],
            "repetition_id": row["repetition_id"],
            "y_true": row["y_true"],
            "y_pred": row["y_pred"],
            "reason_codes": sorted(set(codes)),
            "probability_confidence": row["probability_confidence"],
            "decision_margin": row["top2_margin"],
            "window_disagreement": row["window_disagreement"],
            "window_count": row["window_count"],
            "qc_flags": row["qc_flags"],
            "source_matrix_sha256": row["source_matrix_sha256"],
            "fold_manifest_sha256": row["fold_manifest_sha256"],
            "model_config_sha256": row.get("model_config_sha256", ""),
            "review_status": "UNREVIEWED",
            "review_note": "",
        })
    return out


def summarize_failures(cases):
    reason_counts = Counter(code for case in cases for code in case["reason_codes"])
    return {
        "schema_version": "day33-failure-summary.v1",
        "failure_case_count": len(cases),
        "reason_code_counts": dict(sorted(reason_counts.items())),
        "review_status_counts": dict(Counter(case["review_status"] for case in cases)),
    }
