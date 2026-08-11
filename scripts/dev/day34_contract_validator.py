from __future__ import annotations

import csv
import json
from pathlib import Path

import yaml


def rows(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    evidence = root / "qa-validation/evidence"
    summary = json.loads((evidence / "day34-analysis-summary.json").read_text())
    perf = rows(evidence / "lf-performance-synthetic-v0.1.csv")
    integrity = rows(evidence / "data-integrity-performance-synthetic-v0.1.csv")
    candidates = rows(evidence / "research-review-candidate-list-v0.1.csv")
    raw = rows(evidence / "day34-lf-window-outputs-v0.1.csv")
    manifest = yaml.safe_load(
        (evidence / "research-benchmark-corpus-v0.1.manifest.yaml").read_text()
    )
    locked_ids = {
        item["item_id"]
        for item in manifest["items"]
        if item["partition"] == "benchmark-locked"
    }
    assert summary["development_items"] == 12
    assert summary["locked_items_consumed"] == 0
    assert summary["family_output_rows"] == 72
    assert summary["truth_window_misaligned_items"] == 4
    assert summary["expert_agreement_status"] == "NOT_PERFORMED"
    assert summary["label_model_training"] is False
    assert summary["threshold_tuning"] is False
    assert summary["clinical_validation"] == "NOT_PERFORMED"
    assert len(perf) == 6
    by_family = {row["family_id"]: row for row in perf}
    assert by_family["LF_MISSING_DROPOUT"]["truth_localization_gap_count"] == "3"
    assert by_family["LF_CLIPPING_SATURATION"]["truth_localization_gap_count"] == "1"
    assert by_family["LF_BASELINE_NOISE"]["positive_unresolved"] == "1"
    assert by_family["LF_POWERLINE"]["tp"] == "1"
    assert by_family["LF_LOW_FREQUENCY_CONTAMINATION"]["tp"] == "2"
    assert by_family["LF_POOR_CONTACT"]["evaluated_binary_count"] == "0"
    assert integrity[0]["tp"] == "2" and integrity[0]["fn"] == "0"
    assert not locked_ids.intersection({row["item_id"] for row in raw})
    repair = [row for row in candidates if row["review_target"] == "ENGINEERING_CORPUS_REPAIR"]
    assert len(repair) == 4
    assert all(row["selected_for_future_review"] == "False" for row in repair)
    print(
        json.dumps(
            {
                "status": "PASS",
                "lf_families": len(perf),
                "development_items": summary["development_items"],
                "locked_items_consumed": 0,
                "truth_window_misaligned_items": 4,
                "engineering_corpus_repair_items": len(repair),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
