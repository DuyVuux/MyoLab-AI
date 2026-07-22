#!/usr/bin/env python3
"""Validate schema, hash, confidence semantics và wording Day 14."""
from __future__ import annotations
import json
from pathlib import Path
import jsonschema

ROOT = Path(__file__).resolve().parents[2]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    schema = load(ROOT / "packages/common-schemas/json/explainable-inference-result.schema.json")
    verify_schema = load(ROOT / "packages/common-schemas/json/technical-confidence-verification.schema.json")
    golden = load(ROOT / "qa-validation/evidence/day14-explainable-inference.json")
    rerun = load(ROOT / "qa-validation/evidence/day14-explainable-inference-rerun.json")
    warning = load(ROOT / "qa-validation/evidence/day14-explainable-inference-warning.json")
    abstained = load(ROOT / "qa-validation/evidence/day14-explainable-inference-abstained.json")
    verification = load(ROOT / "qa-validation/evidence/day14-confidence-verification.json")
    for payload in (golden, rerun, warning, abstained):
        jsonschema.validate(payload, schema)
    jsonschema.validate(verification, verify_schema)
    assert golden["result_hash_sha256"] == rerun["result_hash_sha256"]
    assert golden["technical_confidence"]["score_is_probability"] is False
    assert golden["technical_confidence"]["clinical_calibration_status"] == "not_calibrated"
    assert 0 <= golden["technical_confidence"]["final_score_0_to_1"] <= 1
    assert warning["status"] == "completed_with_warnings"
    assert abstained["technical_confidence"]["final_score_0_to_1"] is None
    assert golden["explainability"]["wording_guard"]["status"] == "passed"
    assert golden["config"]["clinical_use_allowed"] is False
    serialized = json.dumps(golden, ensure_ascii=False).lower()
    prohibited = ["fatigue_detected", "no_fatigue", "return_to_play_ready", "stop_exercise"]
    assert not any(term in serialized for term in prohibited)
    print("Day 14 outputs: schema/hash/confidence/wording PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
