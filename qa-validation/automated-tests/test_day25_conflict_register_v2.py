from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTER = ROOT / "docs/05-data/day25-research/research-conflict-register.csv"


def test_critical_conflicts_are_explicit() -> None:
    with REGISTER.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) >= 8
    topics = " ".join(row["topic"] for row in rows).lower()
    assert "json" in topics
    assert "mfcv" in topics
    assert "capgmyo" in topics
    assert "mr3 export" in topics
    for row in rows:
        assert row["required_evidence"].strip()
        assert row["operational_resolution"].strip()
