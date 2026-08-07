from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = ROOT / "scripts/dev"
sys.path.insert(0, str(SCRIPT_DIR))

from day04_quality_taxonomy_utils import (  # noqa: E402
    aggregate_signal_quality,
    load_json,
    load_yaml,
    taxonomy_by_code,
    validate_reason_record,
)


TAXONOMY = ROOT / "clinical/quality/qc-taxonomy.v0.1.yaml"
GUIDANCE = ROOT / "clinical/quality/artifact-vs-physiology-guidance.v0.1.md"
REASON_SCHEMA = ROOT / "packages/common-schemas/json/quality-reason-codes.schema.json"
TAXONOMY_SCHEMA = ROOT / "packages/common-schemas/json/qc-taxonomy.schema.json"
FIXTURE = ROOT / "qa-validation/test-data/day04/synthetic-quality-reason-cases.v0.1.yaml"
REPORT = ROOT / "qa-validation/evidence/day04-validation-report.json"
UPSTREAM = ROOT / "qa-validation/evidence/day04-day03-handoff-snapshot.json"


def main() -> int:
    failures: list[str] = []

    try:
        taxonomy = load_yaml(TAXONOMY)
        reason_schema = load_json(REASON_SCHEMA)
        taxonomy_schema = load_json(TAXONOMY_SCHEMA)
        fixture = load_yaml(FIXTURE)

        jsonschema.Draft202012Validator(taxonomy_schema).validate(taxonomy)
        taxonomy_by_code(taxonomy)

        for case in fixture["cases"]:
            for record in case["reasons"]:
                validate_reason_record(record, reason_schema)
            actual = aggregate_signal_quality(case["reasons"], taxonomy)
            if actual != case["expected_quality"]:
                failures.append(
                    f"{case['case_id']}: expected {case['expected_quality']}, got {actual}"
                )

        text = GUIDANCE.read_text(encoding="utf-8").lower()
        required_phrases = [
            "stroke",
            "muscle-atrophy",
            "body-habitus",
            "not automatically an acquisition artifact",
            "no numerical clinical/site qc threshold is frozen",
        ]
        for phrase in required_phrases:
            if phrase not in text:
                failures.append(f"guidance missing phrase: {phrase}")

        if taxonomy["threshold_policy"]["numeric_thresholds_frozen"] is not False:
            failures.append("numeric threshold must not be frozen in DAY04")

        upstream = load_json(UPSTREAM)
        if upstream["day03_status"] != "GO_FOR_DAY_04":
            status = "BLOCKED_WITH_EVIDENCE_UPSTREAM_DAY03"
        elif failures:
            status = "BLOCKED_WITH_VALIDATION_FAILURE"
        else:
            status = "GO_FOR_DAY_05"

    except Exception as exc:  # fail closed for validator
        failures.append(f"validator exception: {type(exc).__name__}: {exc}")
        status = "BLOCKED_WITH_VALIDATION_FAILURE"

    report = {
        "version": "0.1",
        "day": "DAY04",
        "status": status,
        "taxonomy_designed": not failures,
        "taxonomy_site_validated": False,
        "numeric_thresholds_frozen": False,
        "training_executed": False,
        "raw_patient_data_read": False,
        "upstream_day03_required_status": "GO_FOR_DAY_04",
        "validation_failures": failures,
        "tests_expected": 20,
        "tests_passed": None,
        "pytest_return_code": None,
        "engineering_validation_passed": not failures,
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
