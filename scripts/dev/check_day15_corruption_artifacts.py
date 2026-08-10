#!/usr/bin/env python3
"""Check namespaced DAY15 corruption-safety artifacts in the live repo."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_SUFFIXES = {
    ".npz",
    ".npy",
    ".mat",
    ".c3d",
    ".joblib",
    ".pkl",
    ".pickle",
    ".pt",
    ".pth",
    ".onnx",
}
REQUIRED = [
    "docs/00-executive/decisions/day15-corruption-decision-log.md",
    "docs/00-executive/rebaseline/day15-corruption-property-safety-verification.md",
    "docs/03-architecture/traceability/day15-corruption-traceability.md",
    "qa-validation/automated-tests/ingestion/test_day15_corruption_factory.py",
    "qa-validation/property-tests/day15_corruption/ingestion-invariants.v0.1.yaml",
    "qa-validation/property-tests/day15_corruption/ingestion_property_harness.py",
    "qa-validation/property-tests/day15_corruption/test_ingestion_properties.py",
    "qa-validation/requirements/day15-corruption-acceptance-criteria.md",
    "qa-validation/test-data/synthetic/generators/noraxon_corruption_factory.py",
    "qa-validation/test-data/synthetic/day15-corruption/fixture-manifest.json",
    "qa-validation/test-data/synthetic/day15-corruption/property-cases.jsonl",
    "scripts/dev/validate_day15_corruption_invariants.py",
    "scripts/dev/run_day15_corruption_checks.sh",
]
PROTECTED_CURRENT_DAY15 = [
    "scripts/dev/run_day15_checks.sh",
    "scripts/dev/check_day15_artifacts.py",
    "qa-validation/requirements/day15-acceptance-criteria.md",
]


def main() -> int:
    failures: list[str] = []
    missing = [item for item in REQUIRED if not (ROOT / item).is_file()]
    failures.extend(f"missing: {item}" for item in missing)

    fixture_root = ROOT / "qa-validation/test-data/synthetic/day15-corruption"
    for path in fixture_root.rglob("*") if fixture_root.exists() else []:
        if path.is_file() and path.suffix.lower() in FORBIDDEN_SUFFIXES:
            failures.append(f"forbidden artifact suffix: {path.relative_to(ROOT)}")

    manifest_path = fixture_root / "fixture-manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("data_class") != "SYNTHETIC_ONLY":
            failures.append("fixture manifest must be SYNTHETIC_ONLY")
        if manifest.get("clinical_evidence") is not False:
            failures.append("fixture manifest must not claim clinical evidence")
        if manifest.get("site_verified") is not False:
            failures.append("fixture manifest must not claim site verification")
        if manifest.get("production_parser_bound") is not False:
            failures.append("fixture manifest must not claim production parser binding")
    else:
        failures.append("fixture manifest missing")

    for item in PROTECTED_CURRENT_DAY15:
        if not (ROOT / item).is_file():
            failures.append(f"current Day15 artifact unexpectedly missing: {item}")

    print(
        json.dumps(
            {
                "required": len(REQUIRED),
                "protected_current_day15": len(PROTECTED_CURRENT_DAY15),
                "failures": failures,
                "status": "PASS" if not failures else "FAIL",
            },
            indent=2,
        )
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
