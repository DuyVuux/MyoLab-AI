from __future__ import annotations

import argparse
import json
from pathlib import Path

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "data-platform/catalog/legacy-asset-inventory.v1.0.yaml"
INVENTORY_SCHEMA = ROOT / "packages/common-schemas/json/legacy-asset-inventory.schema.json"
REGRESSION = ROOT / "qa-validation/regression/legacy-regression-scope.v1.0.yaml"
REGRESSION_SCHEMA = ROOT / "packages/common-schemas/json/legacy-regression-scope.schema.json"
TRACEABILITY = ROOT / "docs/03-architecture/traceability/day07-legacy-asset-traceability.v1.0.csv"
REPORT = ROOT / "qa-validation/evidence/day07-validation-report.json"
REPO_SCAN = ROOT / "qa-validation/evidence/day07-repo-scan.json"
HUMAN_REVIEW = ROOT / "qa-validation/evidence/day07-human-review.yaml"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def validate_schema(instance_path: Path, schema_path: Path) -> dict:
    instance = load_yaml(instance_path)
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(instance)
    return instance


def repo_confirmation() -> tuple[bool, dict[str, object] | None]:
    if not REPO_SCAN.exists():
        return False, None
    data = json.loads(REPO_SCAN.read_text(encoding="utf-8"))
    confirmed = bool(data.get("repo_confirmation_complete"))
    return confirmed, data


def human_confirmation() -> tuple[bool, dict[str, object] | None]:
    if not HUMAN_REVIEW.exists():
        return False, None
    data = load_yaml(HUMAN_REVIEW)
    approved = bool(data.get("approved")) and data.get("critical_unresolved_count") == 0
    return approved, data


def determine_status(repo_ok: bool, human_ok: bool) -> str:
    if repo_ok and human_ok:
        return "GO_FOR_DAY_08"
    return "READY_WITH_LIMITATIONS"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tests-passed", action="store_true")
    args = parser.parse_args()

    inventory = validate_schema(INVENTORY, INVENTORY_SCHEMA)
    regression = validate_schema(REGRESSION, REGRESSION_SCHEMA)

    ids = [item["id"] for item in inventory["asset_families"]]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate legacy asset family ID")

    if any(suite.get("clinical_claim_allowed") is not False for suite in regression["suites"]):
        raise ValueError("Legacy regression suite cannot authorize clinical claim")

    trace_text = TRACEABILITY.read_text(encoding="utf-8")
    for required in ("PRD_PRODUCT_PRINCIPLES", "NFR-001", "NFR-011"):
        if required not in trace_text:
            raise ValueError(f"Missing traceability: {required}")

    repo_ok, repo_data = repo_confirmation()
    human_ok, human_data = human_confirmation()
    status = determine_status(repo_ok, human_ok)

    report = {
        "schema_version": "1.0",
        "day": "DAY07",
        "engineering_validation": "PASS",
        "tests_passed": bool(args.tests_passed),
        "asset_family_count": len(inventory["asset_families"]),
        "regression_suite_count": len(regression["suites"]),
        "repo_confirmation_complete": repo_ok,
        "repo_scan_present": repo_data is not None,
        "human_review_complete": human_ok,
        "human_review_present": human_data is not None,
        "training_executed": False,
        "raw_patient_data_read": False,
        "site_validation_claimed": False,
        "final_status": status,
        "limitations": [] if status == "GO_FOR_DAY_08" else [
            "Current post-DAY06 repository path confirmation and/or human semantic review remains required before GO_FOR_DAY_08."
        ],
    }
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
