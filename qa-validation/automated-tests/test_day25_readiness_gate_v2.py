from __future__ import annotations

import csv
import json
from pathlib import Path

from data.readiness_gate_v2 import build_day25_gate

ROOT = Path(__file__).resolve().parents[2]


def csv_rows(relative: str) -> list[dict[str, str]]:
    with (ROOT / relative).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_day25_gate_is_conditional_and_training_disabled() -> None:
    site_audit = json.loads(
        (ROOT / "qa-validation/evidence/day25-noraxon-site-audit.json").read_text(
            encoding="utf-8"
        )
    )
    split = json.loads(
        (ROOT / "qa-validation/evidence/day25-subject-group-split-v0.2.json").read_text(
            encoding="utf-8"
        )
    )
    report = build_day25_gate(
        inventory_rows=csv_rows("docs/05-data/day25-research/dataset-inventory-v0.2.csv"),
        conflict_rows=csv_rows("docs/05-data/day25-research/research-conflict-register.csv"),
        source_rows=csv_rows("docs/05-data/day25-research/source-evidence-register.csv"),
        site_audit=site_audit,
        split=split,
    )
    assert report["status"] == "CONDITIONAL_READY"
    assert report["implementationAllowed"] is True
    assert report["trainingAllowed"] is False
    assert report["checks"]["nativeJsonExportVerified"] is False
    assert report["checks"]["mfcvEligibilityVerified"] is False


def test_prohibited_actions_include_training_and_mfcv() -> None:
    report = json.loads(
        (ROOT / "qa-validation/evidence/day25-data-readiness-gate-v0.2.json").read_text(
            encoding="utf-8"
        )
    )
    combined = " ".join(report["prohibitedActions"])
    assert "Train" in combined
    assert "MFCV" in combined
