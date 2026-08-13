#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core/evaluation"))

from day33.aggregation import aggregate_predictions
from day33.bootstrap import subject_cluster_bootstrap
from day33.cross_day import evaluate_by_day
from day33.failure_cases import (
    extract_failure_cases,
    summarize_failures,
    top_confusion_pairs,
)
from day33.io import read_csv, write_csv, write_json
from day33.metrics import (
    confusion_rows,
    evaluate_repetitions,
    per_class_rows,
    subject_class_recall_rows,
    subject_metric_rows,
)
from day33.prediction_gate import validate_prediction_rows


def main():
    parser = argparse.ArgumentParser(description="Run repetition/subject prediction evaluation and error analysis.")
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--bootstrap-iterations", type=int, default=500)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    rows = read_csv(args.predictions)
    gate = validate_prediction_rows(rows)
    write_json(output_dir / "prediction-gate.json", gate)
    if not gate["pass"]:
        raise SystemExit(2)

    repetitions = aggregate_predictions(rows)
    metrics = evaluate_repetitions(repetitions)
    bootstrap = subject_cluster_bootstrap(repetitions, args.bootstrap_iterations)
    confusion_pairs = top_confusion_pairs(repetitions)
    systematic_pairs = {(row["y_true"], row["y_pred"]) for row in confusion_pairs[:3]}
    failures = extract_failure_cases(repetitions, systematic_pairs=systematic_pairs)
    day_metrics = evaluate_by_day(repetitions)

    write_csv(output_dir / "repetition-predictions.csv", repetitions)
    write_json(output_dir / "aggregation-audit.json", {
        "schema_version": "prediction-aggregation-audit.v1",
        "input_prediction_rows": len(rows),
        "output_repetition_rows": len(repetitions),
        "aggregation_methods": sorted({row["aggregation_method"] for row in repetitions}),
        "sealed_test_rows_read": 0,
    })
    write_json(output_dir / "evaluation-metrics.json", metrics)
    write_json(output_dir / "repetition-metrics.json", metrics["repetition_metrics"])
    write_csv(output_dir / "per-class-metrics.csv", per_class_rows(metrics))
    write_csv(output_dir / "confusion-matrix.csv", confusion_rows(metrics))
    write_csv(output_dir / "subject-metrics.csv", subject_metric_rows(metrics))
    write_json(output_dir / "subject-summary.json", metrics["subject_summary"])
    write_csv(output_dir / "worst-subjects.csv", sorted(subject_metric_rows(metrics), key=lambda row: row["macro_f1"])[:10])
    write_csv(output_dir / "subject-class-recall.csv", subject_class_recall_rows(metrics))
    write_csv(output_dir / "fold-metrics.csv", metrics["fold_metrics"])
    write_json(output_dir / "bootstrap-primary-metric.json", bootstrap)
    write_csv(output_dir / "failure-cases.csv", failures)
    write_json(output_dir / "failure-summary.json", summarize_failures(failures))
    write_csv(output_dir / "top-confusion-pairs.csv", confusion_pairs)
    write_csv(output_dir / "high-confidence-errors.csv", [
        row for row in failures if "HIGH_CONFIDENCE_ERROR" in row["reason_codes"]
    ])
    write_csv(output_dir / "high-disagreement-errors.csv", [
        row for row in failures if "HIGH_WINDOW_DISAGREEMENT" in row["reason_codes"]
    ])
    write_csv(output_dir / "qc-associated-errors.csv", [
        row for row in failures if "QC_ASSOCIATED_ERROR" in row["reason_codes"]
    ])
    write_csv(output_dir / "day-metrics.csv", day_metrics)

    mode = "TOOLING_VALIDATION" if all(row["dataset_id"].startswith("synthetic") for row in repetitions) else "REAL_DEVELOPMENT_EVALUATION"
    summary = {
        "schema_version": "day33-evaluation-run.v1",
        "mode": mode,
        "dataset_ids": sorted({row["dataset_id"] for row in repetitions}),
        "run_ids": sorted({row["run_id"] for row in repetitions}),
        "prediction_rows": len(rows),
        "repetition_rows": len(repetitions),
        "subject_count": metrics["subject_summary"]["subject_count"],
        "primary_metric": metrics["subject_summary"]["subject_macro_repetition_macro_f1"],
        "bootstrap_ci": [bootstrap["ci_low"], bootstrap["ci_high"]],
        "failure_case_count": len(failures),
        "sealed_test_rows_read": 0,
        "pooled_evaluation_executed": False,
        "synthetic_results_are_benchmark": False,
        "fatigue_inference_allowed": False,
    }
    write_json(output_dir / "run-summary.json", summary)
    print(summary)


if __name__ == "__main__":
    main()
