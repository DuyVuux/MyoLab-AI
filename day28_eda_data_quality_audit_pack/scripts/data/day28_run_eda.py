#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ai-core" / "data"))

from day28.label_audit import audit_labels, summary_to_dict
from day28.preflight import result_to_dict, run_preflight
from day28.quality_rules import apply_rules, load_rules
from day28.structural_eda import load_profile, run_structural_eda


def main() -> int:
    parser = argparse.ArgumentParser(description="Run train/validation-only Day 28 EDA")
    parser.add_argument("--manifest-dir", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--metadata-index", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--partitions", nargs="+", default=["train", "validation"])
    parser.add_argument("--quality-rules", type=Path, default=REPO_ROOT / "ai-core/configs/day28_quality_rules.provisional.yaml")
    args = parser.parse_args()

    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    preflight = run_preflight(args.manifest_dir)
    (output / "day28-preflight.json").write_text(json.dumps(result_to_dict(preflight), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not preflight.ready_for_real_eda:
        decision = {
            "schema_version": "day28-readiness-decision.v1",
            "status": "BLOCKED_WITH_EVIDENCE",
            "training_execution_allowed": False,
            "blockers": preflight.blockers,
        }
        (output / "day28-readiness-decision.yaml").write_text(
            "schema_version: day28-readiness-decision.v1\nstatus: BLOCKED_WITH_EVIDENCE\ntraining_execution_allowed: false\nblockers:\n" +
            "".join(f"  - {item!r}\n" for item in preflight.blockers),
            encoding="utf-8",
        )
        return 2

    metadata = pd.read_csv(args.metadata_index)
    if "partition" not in metadata.columns:
        raise ValueError("metadata index must contain partition")
    selected = metadata[metadata["partition"].isin(args.partitions)].copy()
    if (metadata["partition"] == "test").any() and (selected["partition"] == "test").any():
        raise ValueError("Sealed test selected for EDA")

    label_summary = audit_labels(selected, args.partitions)
    (output / "label-coverage-summary.json").write_text(json.dumps(summary_to_dict(label_summary), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    profile = load_profile(args.manifest_dir / "canonical-mapping-draft.yaml")
    file_stats, channel_stats = run_structural_eda(args.data_root, selected, profile)
    file_stats.to_csv(output / "file-level-statistics.csv", index=False)
    channel_stats.to_csv(output / "channel-level-statistics.csv", index=False)

    class_distribution = selected.groupby(["partition", "source_label", "canonical_label"], dropna=False).size().reset_index(name="record_count")
    class_distribution.to_csv(output / "class-distribution.csv", index=False)
    subject_support = selected.groupby(["subject_id", "canonical_label"], dropna=False).size().reset_index(name="record_count")
    subject_support.to_csv(output / "subject-class-support.csv", index=False)
    excluded = selected[selected["canonical_label"] == "unknown"].copy()
    excluded["exclusion_reason"] = "OUT_OF_SCOPE_LABEL"
    excluded.to_csv(output / "excluded-label-audit.csv", index=False)

    rules = load_rules(args.quality_rules)
    flags = apply_rules(channel_stats, rules)
    flags.to_csv(output / "signal-quality-flags.csv", index=False)

    critical_count = int((flags.get("severity", pd.Series(dtype=str)) == "fail").sum()) if not flags.empty else 0
    status = "GO_FOR_DAY29_TRAINING_PREFLIGHT" if critical_count == 0 and not label_summary.core_classes_missing else "BLOCKED_WITH_EVIDENCE"
    decision = {
        "schema_version": "day28-readiness-decision.v1",
        "status": status,
        "public_dataset_engineering_ready": status.startswith("GO_"),
        "public_baseline_training_eligible": status.startswith("GO_"),
        "training_execution_allowed": False,
        "test_set_sealed": True,
        "supported_class_count": 4,
        "hand_open_supported": False,
        "motion_lab_transfer_verified": False,
        "clinical_use_allowed": False,
        "critical_quality_flag_count": critical_count,
        "core_classes_missing": label_summary.core_classes_missing,
    }
    import yaml
    (output / "day28-readiness-decision.yaml").write_text(yaml.safe_dump(decision, sort_keys=False, allow_unicode=True), encoding="utf-8")
    (output / "dataset-quality-summary.json").write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if status.startswith("GO_") else 3


if __name__ == "__main__":
    raise SystemExit(main())
