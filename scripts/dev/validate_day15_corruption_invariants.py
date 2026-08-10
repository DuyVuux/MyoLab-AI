#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
INVARIANTS = ROOT / "qa-validation/property-tests/day15_corruption/ingestion-invariants.v0.1.yaml"
FIXTURE_ROOT = ROOT / "qa-validation/test-data/synthetic/day15-corruption"
MANIFEST = FIXTURE_ROOT / "fixture-manifest.json"


def main() -> int:
    failures: list[str] = []
    payload = yaml.safe_load(INVARIANTS.read_text(encoding="utf-8"))
    critical = {item["name"] for item in payload.get("critical_invariants", [])}
    required = {
        "RAW_IMMUTABLE",
        "UNKNOWN_UNIT_NEVER_INFERRED",
        "NO_SILENT_CRASH",
        "FAIL_CLOSED",
    }
    missing = sorted(required - critical)
    if missing:
        failures.append(f"missing critical invariants: {missing}")
    if payload.get("production_parser_bound") is not False:
        failures.append("DAY15 must not claim production parser binding")
    if payload.get("clinical_validation") is not False:
        failures.append("DAY15 must not claim clinical validation")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("data_class") != "SYNTHETIC_ONLY":
        failures.append("fixture manifest must be synthetic-only")
    if manifest.get("production_parser_bound") is not False:
        failures.append("fixture manifest must not claim parser binding")
    mutations = {
        item.get("mutation")
        for item in manifest.get("fixed_fixtures", [])
        if item.get("mutation")
    }
    for mutation in (
        "MALFORMED_HEADER",
        "COUNT_MISMATCH",
        "DUPLICATE_TIMESTAMP",
        "OUT_OF_ORDER_TIMESTAMP",
        "MISSING_ROW",
        "UNKNOWN_UNIT",
        "MIXED_FS",
        "UTF8_BOM",
        "SIGNAL_2D_WRONG_SHAPE",
    ):
        if mutation not in mutations:
            failures.append(f"required mutation missing: {mutation}")

    class_by_mutation = {
        item.get("mutation"): item.get("fixture_class")
        for item in manifest.get("fixed_fixtures", [])
    }
    for legal_edge in ("MIXED_FS", "UTF8_BOM"):
        if class_by_mutation.get(legal_edge) != "VALID_EDGE_MUST_ACCEPT":
            failures.append(f"{legal_edge} must be a valid edge, not a corrupted failure")

    print(
        json.dumps(
            {
                "critical_invariants": sorted(critical),
                "fixed_fixtures": len(manifest.get("fixed_fixtures", [])),
                "property_cases": manifest.get("property_case_count"),
                "production_parser_bound": False,
                "failures": failures,
                "status": "PASS" if not failures else "FAIL",
            },
            indent=2,
        )
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
