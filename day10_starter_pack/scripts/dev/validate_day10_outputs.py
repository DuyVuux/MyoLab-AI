#!/usr/bin/env python3
"""Validate Day 10 JSON outputs, schemas và invariants."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(payload: dict, schema_path: Path) -> None:
    schema = load(schema_path)
    Draft202012Validator(schema).validate(payload)


def main() -> int:
    evidence = ROOT / "qa-validation/evidence"
    verification = load(evidence / "day10-mdf-mnf-verification.json")
    result = load(evidence / "day10-frequency-features.json")
    rerun = load(evidence / "day10-frequency-features-rerun.json")
    blocked = load(evidence / "day10-frequency-features-blocked.json")
    schemas = ROOT / "packages/common-schemas/json"
    validate(verification, schemas / "frequency-feature-verification.schema.json")
    validate(result, schemas / "frequency-feature-extraction-result.schema.json")
    validate(rerun, schemas / "frequency-feature-extraction-result.schema.json")
    validate(blocked, schemas / "frequency-feature-extraction-result.schema.json")
    if verification["status"] != "passed":
        raise SystemExit("Verification chưa pass")
    if result["result_hash_sha256"] != rerun["result_hash_sha256"]:
        raise SystemExit("Deterministic hash không khớp")
    if result["summary"]["computed_row_count"] != 119:
        raise SystemExit("Golden result phải có 119 computed rows")
    if blocked["status"] != "blocked" or blocked["rows"]:
        raise SystemExit("Blocked result phải không có rows")
    for row in result["rows"]:
        if row["status"] != "computed":
            continue
        mdf = row["features"]["mdf"]["value"]
        mnf = row["features"]["mnf"]["value"]
        if not (20.0 <= mdf <= 400.0 and 20.0 <= mnf <= 400.0):
            raise SystemExit("MDF/MNF nằm ngoài analysis band")
        if "psd" in row["features"]:
            raise SystemExit("Frequency feature output không được chứa PSD vector")
    print("Day 10 outputs: schema/hash/invariants PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
