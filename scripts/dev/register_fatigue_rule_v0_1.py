#!/usr/bin/env python3
"""Đăng ký metadata rule engine v0.1 vào registry."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    config_path = ROOT / "services/inference-service/rules/fatigue_rule_v0.1.yaml"
    code_path = ROOT / "services/inference-service/src/rule_engine.py"
    evidence_path = ROOT / "qa-validation/evidence/day13-rule-verification.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if evidence.get("passed") is not True:
        raise SystemExit("Không đăng ký rule chưa pass verification")
    payload = {
        "schema_version": "rule-engine-registry.v0.1",
        "rule_engines": [{
            "config_id": "fatigue_rule_v0.1",
            "lifecycle_status": "verified_for_mvp0_synthetic_only",
            "clinical_validation_status": "not_validated",
            "config_sha256": sha(config_path),
            "implementation_sha256": sha(code_path),
            "verification_artifact": str(evidence_path.relative_to(ROOT)),
            "outputs_probability": False,
            "outputs_frs": False,
            "outputs_diagnosis": False,
        }],
    }
    target = ROOT / "mlops/registry/rule_engines.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print("Registered fatigue_rule_v0.1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
