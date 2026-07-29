#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ai-core" / "data"))

from day29.cross_day_drift import build_drift_summary  # noqa: E402
from day29.descriptive_stats import channel_statistics  # noqa: E402
from day29.hierarchy_audit import audit_hierarchy  # noqa: E402
from day29.label_audit import audit_labels  # noqa: E402
from day29.manifest_io import dump_json, dump_yaml, load_metadata_index, load_yaml  # noqa: E402
from day29.partition_guard import filter_visible_records  # noqa: E402
from day29.signal_loader import load_signal  # noqa: E402
from day29.signal_quality import evaluate_quality  # noqa: E402


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    headers = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Day29 descriptive EDA on train/validation")
    parser.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()

    config = load_yaml(args.config)
    quality_rules = load_yaml(REPO_ROOT / "ai-core/configs/day29_grabmyo_quality_rules.provisional.yaml")
    metadata_index = Path(config["metadata_index"])
    evidence_dir = Path(config["evidence_dir"])
    evidence_dir.mkdir(parents=True, exist_ok=True)

    records = filter_visible_records(load_metadata_index(metadata_index))
    hierarchy = audit_hierarchy(records)
    labels = audit_labels(records)

    feature_rows: list[dict[str, Any]] = []
    quality_rows: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []

    for record in records:
        try:
            signal, channel_names = load_signal(record)
            for channel_index, channel_name in enumerate(channel_names):
                stats = channel_statistics(signal[:, channel_index])
                row = {
                    "record_id": record.record_id,
                    "subject_id": record.subject_id,
                    "day_id": record.day_id,
                    "session_id": record.session_id,
                    "repetition_id": record.repetition_id,
                    "canonical_label": record.canonical_label,
                    "partition": record.partition,
                    "channel_id": channel_name,
                    "sampling_rate_hz": record.sampling_rate_hz,
                    "signal_unit": record.signal_unit,
                    **stats,
                }
                feature_rows.append(row)
                quality_rows.append({
                    "record_id": record.record_id,
                    "channel_id": channel_name,
                    "reason_codes": ";".join(evaluate_quality(stats, quality_rules)),
                })
        except Exception as exc:
            errors.append({"record_id": record.record_id, "error": str(exc)})

    drift_rows: list[dict[str, Any]] = []
    for feature in ["rms", "mav", "median", "mad", "std"]:
        drift_rows.extend(build_drift_summary(feature_rows, feature))

    dump_json(evidence_dir / "hierarchy-audit.json", hierarchy)
    write_csv(evidence_dir / "label-audit.csv", labels)
    write_csv(evidence_dir / "channel-level-statistics.csv", feature_rows)
    write_csv(evidence_dir / "signal-quality-flags.csv", quality_rows)
    write_csv(evidence_dir / "cross-day-drift-summary.csv", drift_rows)
    dump_json(evidence_dir / "signal-load-errors.json", errors)

    summary = {
        "schema_version": "day29-eda-summary.v1",
        "status": "COMPLETED_WITH_ERRORS" if errors else "COMPLETED",
        "records_attempted": len(records),
        "channel_stat_rows": len(feature_rows),
        "cross_day_comparison_rows": len(drift_rows),
        "signal_load_error_count": len(errors),
        "training_allowed": False,
        "test_signal_rows_read": 0,
        "fatigue_inference_allowed": False,
    }
    dump_json(evidence_dir / "dataset-quality-summary.json", summary)
    dump_yaml(evidence_dir / "day29-readiness-decision.yaml", {
        "schema_version": "day29-readiness-decision.v1",
        "status": "BLOCKED_WITH_EVIDENCE" if errors or hierarchy["status"] == "CONFLICTING" else "PENDING_MANUAL_GATE_REVIEW",
        "training_allowed": False,
        "test_set_opened": False,
        "manual_review_required": True,
    })
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
