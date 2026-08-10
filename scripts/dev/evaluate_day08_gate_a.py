from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema
import yaml


ALLOWED_PASS_STATUSES = {"VERIFIED_DOCUMENTED", "SITE_VERIFIED"}


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}")
    return data


def evaluate_gate(data: dict[str, Any]) -> tuple[str, str, list[str]]:
    blockers: list[str] = []
    for criterion in data["criteria"]:
        if criterion["critical"] and criterion["status"] not in ALLOWED_PASS_STATUSES:
            blockers.append(f"{criterion['id']}: {criterion['status']}")

    review_status = data["manual_review"]["status"]
    if review_status != "APPROVED":
        blockers.append(f"MANUAL_REVIEW: {review_status}")

    if blockers:
        return "BLOCKED_DISCOVERY", "BLOCKED_WITH_EVIDENCE", blockers
    return "REQUIREMENTS_READY", "GO_FOR_DAY_09", []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--write-report", type=Path)
    args = parser.parse_args()

    evidence_path = args.root / "qa-validation/evidence/day08-gate-a-evidence.yaml"
    schema_path = args.root / "packages/common-schemas/json/gate-a-readiness.schema.json"
    data = load_yaml(evidence_path)
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(data)

    gate_decision, day_status, blockers = evaluate_gate(data)
    report = {
        "gate_decision": gate_decision,
        "day_status": day_status,
        "blockers": blockers,
        "source": str(evidence_path),
    }
    if args.write_report:
        args.write_report.parent.mkdir(parents=True, exist_ok=True)
        args.write_report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
