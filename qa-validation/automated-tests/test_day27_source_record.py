from __future__ import annotations
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core"))

from data.day27.source_record import validate_source_record


def test_verified_fixture_passes():
    record = json.loads((ROOT/"qa-validation/test-data/day27/source-record.synthetic-verified.json").read_text())
    assert validate_source_record(record)["status"] == "VERIFIED"


def test_template_fails_closed():
    record = {"schemaVersion": "public-source-record.v1"}
    report = validate_source_record(record)
    assert report["status"] == "INVALID"
    assert report["errors"]

