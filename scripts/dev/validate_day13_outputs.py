#!/usr/bin/env python3
"""Validate schemas, deterministic hash và prohibited outputs của Day 13."""
from __future__ import annotations
import json
from pathlib import Path
import jsonschema

ROOT = Path(__file__).resolve().parents[2]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    result_schema = load(ROOT / "packages/common-schemas/json/fatigue-rule-result.schema.json")
    verify_schema = load(ROOT / "packages/common-schemas/json/fatigue-rule-verification.schema.json")
    main_result = load(ROOT / "qa-validation/evidence/day13-fatigue-rule.json")
    rerun = load(ROOT / "qa-validation/evidence/day13-fatigue-rule-rerun.json")
    abstained = load(ROOT / "qa-validation/evidence/day13-fatigue-rule-abstained.json")
    verification = load(ROOT / "qa-validation/evidence/day13-rule-verification.json")
    for payload in (main_result, rerun, abstained):
        jsonschema.validate(payload, result_schema)
    jsonschema.validate(verification, verify_schema)
    assert main_result["result_hash_sha256"] == rerun["result_hash_sha256"]
    assert main_result["overall"]["technical_conclusion"] == "supported_pattern"
    assert abstained["overall"]["technical_conclusion"] == "abstained"
    serialized = json.dumps(main_result, ensure_ascii=False).lower()
    prohibited = ["fatigue_detected", "no_fatigue", "probability_of_fatigue", "stop_exercise", "return_to_play_ready"]
    assert not any(term in serialized for term in prohibited)
    assert main_result["config"]["outputs_probability"] is False
    assert main_result["config"]["outputs_frs"] is False
    assert main_result["config"]["outputs_diagnosis"] is False
    print("Day 13 outputs: schema/hash/safety PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
