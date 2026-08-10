from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import jsonschema
import yaml


MANDATORY_OUTPUTS = [
    "data-platform/contracts/noraxon/contract-freeze-v1.0.md",
    "qa-validation/validation-reports/ingestion-real-data-validation-v1.0.md",
    "docs/00-executive/gates/GATE-B-real-data-readiness.md",
]

def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}")
    return data

def load_expected_requirements(root: Path) -> set[str]:
    manifest_path = root / "qa-validation/traceability/requirements-manifest.yaml"
    manifest = load_yaml(manifest_path)
    reqs = manifest.get("expected_requirements", {})
    expected = set()
    for cat_reqs in reqs.values():
        expected.update(cat_reqs)
    return expected

def validate_artifacts_and_requirements(root: Path):
    for rel in MANDATORY_OUTPUTS:
        p = root / rel
        if not p.is_file() or p.stat().st_size == 0:
            raise SystemExit(f"Missing mandatory artifact: {rel}")

    expected_reqs = load_expected_requirements(root)
    matrix = root / "qa-validation/traceability/day20-requirement-freeze-matrix.csv"
    with matrix.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    ids = {r["requirement_id"] for r in rows}
    
    if ids != expected_reqs or len(rows) != len(expected_reqs):
        raise SystemExit(
            f"Requirement denominator mismatch: rows={len(rows)} ids={sorted(ids)}"
        )

    freeze_path = root / "data-platform/contracts/gate-b-technology-freeze.v1.0.yaml"
    freeze = load_yaml(freeze_path)
    distribution = freeze["technology_freeze"]["distribution_ood"]
    if distribution["ood_model_required_for_gate_b"] is not False:
        raise SystemExit("OOD model must not be required at Gate B")
    if freeze["training_allowed"] is not False:
        raise SystemExit("Training must remain disabled at DAY20")


def criterion_passes(criterion: dict[str, Any]) -> bool:
    return criterion["status"] in set(criterion["pass_statuses"])

def evaluate_gate(data: dict[str, Any]) -> tuple[str, str, list[str]]:
    failed = [c for c in data["criteria"] if c["critical"] and not criterion_passes(c)]
    privacy = [f"{c['id']}: {c['status']}" for c in failed if c["category"] == "PRIVACY"]
    other = [f"{c['id']}: {c['status']}" for c in failed if c["category"] != "PRIVACY"]

    review_status = data["manual_review"]["status"]
    if review_status != "APPROVED":
        other.append(f"MANUAL_REVIEW: {review_status}")

    if privacy:
        return "BLOCKED_PRIVACY", "BLOCKED_WITH_EVIDENCE", privacy + other
    if other:
        return "BLOCKED_SCHEMA", "BLOCKED_WITH_EVIDENCE", other
    return "REAL_DATA_READY", "GO_FOR_DAY_21", []

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--write-report", type=Path)
    args = parser.parse_args()

    root: Path = args.project_root.resolve()
    
    # 1. Validation Logic
    validate_artifacts_and_requirements(root)

    # 2. Evaluation Logic
    default_evidence = root / "qa-validation/evidence/day20-gate-b-evidence.yaml"
    evidence_path = args.evidence.resolve() if args.evidence else default_evidence
    schema_path = root / "packages/common-schemas/json/gate-b-readiness.schema.json"
    
    data = load_yaml(evidence_path)
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(data)

    if len(data["criteria"]) != 13:
        raise SystemExit("Expected 13 Gate-B criteria")

    gate_decision, day_status, blockers = evaluate_gate(data)
    
    try:
        source_ref = str(evidence_path.relative_to(root))
    except ValueError:
        source_ref = evidence_path.name
        
    report = {
        "gate_decision": gate_decision,
        "day_status": day_status,
        "blockers": blockers,
        "source": source_ref,
        "day20_contract_validation": "PASS",
        "requirement_count": len(load_expected_requirements(root))
    }
    
    if args.write_report:
        report_path = args.write_report.resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        
    print(json.dumps(report, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
