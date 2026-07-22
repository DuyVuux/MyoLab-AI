#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    config = ROOT / "services/inference-service/confidence/technical_confidence_v0.1.yaml"
    code = ROOT / "services/inference-service/src/confidence.py"
    verification_path = ROOT / "qa-validation/evidence/day14-confidence-verification.json"
    verification = json.loads(verification_path.read_text(encoding="utf-8"))
    if verification.get("passed") is not True:
        raise SystemExit("Confidence verification chưa pass")
    payload = {
        "schema_version": "confidence-engine-registry.v0.1",
        "confidence_engines": [{
            "config_id": "technical_confidence_v0.1",
            "lifecycle_status": "verified_for_mvp0_synthetic_only",
            "clinical_calibration_status": "not_calibrated",
            "clinical_validation_status": "not_validated",
            "config_sha256": sha(config),
            "implementation_sha256": sha(code),
            "verification_artifact": str(verification_path.relative_to(ROOT)),
            "score_is_probability": False,
            "clinical_use_allowed": False,
        }],
    }
    target = ROOT / "mlops/registry/confidence_engines.yaml"
    target.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print("Registered technical_confidence_v0.1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
