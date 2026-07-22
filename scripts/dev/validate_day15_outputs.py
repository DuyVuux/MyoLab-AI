#!/usr/bin/env python3
"""Validate manifests, fingerprints và safety outputs Day 15."""
from __future__ import annotations
import json
from pathlib import Path
import jsonschema

ROOT = Path(__file__).resolve().parents[2]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    manifest_schema = load(ROOT / "packages/common-schemas/json/offline-analysis-manifest.schema.json")
    verify_schema = load(ROOT / "packages/common-schemas/json/offline-analysis-verification.schema.json")
    dirs = {
        "golden": ROOT / "qa-validation/evidence/day15-golden-run",
        "rerun": ROOT / "qa-validation/evidence/day15-golden-rerun",
        "warning": ROOT / "qa-validation/evidence/day15-warning-run",
        "abstained": ROOT / "qa-validation/evidence/day15-abstained-run",
    }
    manifests = {name: load(path / "11-analysis-manifest.json") for name, path in dirs.items()}
    for payload in manifests.values():
        jsonschema.validate(payload, manifest_schema)
    verification = load(ROOT / "qa-validation/evidence/day15-package-verification.json")
    jsonschema.validate(verification, verify_schema)
    assert manifests["golden"]["analysis_fingerprint_sha256"] == manifests["rerun"]["analysis_fingerprint_sha256"]
    assert manifests["golden"]["status"] == "completed"
    assert manifests["warning"]["status"] == "completed_with_warnings"
    assert manifests["abstained"]["status"] == "abstained"
    assert manifests["abstained"]["final"]["technical_conclusion"] == "abstained"
    assert all(payload["final"]["clinical_use_allowed"] is False for payload in manifests.values())
    assert verification["passed"] is True
    print("Day 15 outputs: schema/fingerprint/status/safety PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
