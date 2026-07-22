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
    config = ROOT / "ai-core/configs/offline_analysis_mvp0.yaml"
    code = ROOT / "ai-core/pipelines/offline_analysis.py"
    verification_path = ROOT / "qa-validation/evidence/day15-package-verification.json"
    verification = json.loads(verification_path.read_text(encoding="utf-8"))
    if verification.get("passed") is not True:
        raise SystemExit("Package verification chưa pass")
    golden_manifest = json.loads((ROOT / "qa-validation/evidence/day15-golden-run/11-analysis-manifest.json").read_text(encoding="utf-8"))
    payload = {
        "schema_version": "analysis-pipeline-registry.v0.1",
        "pipelines": [{
            "config_id": "offline_analysis_mvp0",
            "lifecycle_status": "verified_for_mvp0_synthetic_only",
            "clinical_validation_status": "not_validated",
            "config_sha256": sha(config),
            "implementation_sha256": sha(code),
            "golden_analysis_fingerprint_sha256": golden_manifest["analysis_fingerprint_sha256"],
            "verification_artifact": str(verification_path.relative_to(ROOT)),
            "clinical_use_allowed": False,
            "outputs_probability": False,
            "outputs_frs": False,
        }],
    }
    target = ROOT / "mlops/registry/analysis_pipelines.yaml"
    target.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print("Registered offline_analysis_mvp0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
