from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema
import yaml


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping: {path}")
    return data


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected object: {path}")
    return data


def requirement_ids_from_manifest(path: Path) -> set[str]:
    data = load_yaml(path)
    ids: set[str] = set()

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key in {"id", "requirement_id"} and isinstance(child, str):
                    ids.add(child)
                walk(child)
        elif isinstance(value, list):
            for child in value:
                if isinstance(child, str):
                    ids.add(child)
                else:
                    walk(child)

    walk(data)
    return ids


def validate(root: Path) -> dict[str, Any]:
    paths = {
        "taxonomy": root / "clinical/quality/qc-taxonomy.v0.2.yaml",
        "reasons": root / "services/quality-gate-service/configs/reason-codes.v0.1.yaml",
        "qc_schema": root / "packages/common-schemas/json/qc-result.v0.2.schema.json",
        "lf_schema": root / "packages/common-schemas/json/labeling-function-output.schema.json",
        "lf_registry": root / "clinical/labels/qc-labeling-function-registry.v0.1.yaml",
        "impact": root / "qa-validation/traceability/day21-requirement-impact.yaml",
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        return {"status": "FAIL", "errors": [f"missing:{item}" for item in missing]}

    taxonomy = load_yaml(paths["taxonomy"])
    reasons = load_yaml(paths["reasons"])
    qc_schema = load_json(paths["qc_schema"])
    lf_schema = load_json(paths["lf_schema"])
    lf_registry = load_yaml(paths["lf_registry"])
    impact = load_yaml(paths["impact"])

    jsonschema.Draft202012Validator.check_schema(qc_schema)
    jsonschema.Draft202012Validator.check_schema(lf_schema)

    errors: list[str] = []
    codes = [entry["code"] for entry in reasons["reason_codes"]]
    if len(codes) != len(set(codes)):
        errors.append("duplicate_reason_code")

    semantic_classes = set(taxonomy["semantic_class_enum"])
    evidence_types = set(taxonomy["evidence_type_enum"])
    scopes = set(taxonomy["scope_enum"])
    actions = set(taxonomy["technical_action_enum"])

    by_code = {entry["code"]: entry for entry in reasons["reason_codes"]}
    for entry in reasons["reason_codes"]:
        if entry["semantic_class"] not in semantic_classes:
            errors.append(f"unknown_semantic_class:{entry['code']}")
        if not set(entry["allowed_scopes"]).issubset(scopes):
            errors.append(f"invalid_scope:{entry['code']}")
        if not set(entry["evidence_type_candidates"]).issubset(evidence_types):
            errors.append(f"invalid_evidence_type:{entry['code']}")
        if entry["technical_action_default"] not in actions:
            errors.append(f"invalid_action:{entry['code']}")
        if any(key in entry for key in ("diagnosis", "disease", "pathology_code")):
            errors.append(f"diagnosis_field_forbidden:{entry['code']}")
        for key, value in entry.items():
            if "threshold" in key.lower() and isinstance(value, (int, float)):
                errors.append(f"numeric_threshold_forbidden:{entry['code']}:{key}")

    registry_ids: set[str] = set()
    for lf in lf_registry["labeling_functions"]:
        if lf["lf_id"] in registry_ids:
            errors.append(f"duplicate_lf:{lf['lf_id']}")
        registry_ids.add(lf["lf_id"])
        code = lf["reason_code"]
        if code not in by_code:
            errors.append(f"lf_unknown_reason:{lf['lf_id']}")
        elif by_code[code]["labeling_function_candidate"] is not True:
            errors.append(f"lf_reason_not_candidate:{lf['lf_id']}")

    non_candidates = set(lf_registry["non_candidates"])
    for code in non_candidates:
        if code not in by_code:
            errors.append(f"non_candidate_unknown:{code}")
        elif by_code[code]["labeling_function_candidate"] is not False:
            errors.append(f"non_candidate_marked_candidate:{code}")

    if lf_registry["ground_truth_policy"]["weak_label_is_expert_ground_truth"]:
        errors.append("weak_label_ground_truth_forbidden")
    if lf_registry["ground_truth_policy"]["label_model_training_authorized"]:
        errors.append("label_model_training_not_authorized_day21")
    if taxonomy["threshold_policy"]["numeric_thresholds_frozen"]:
        errors.append("day21_numeric_threshold_freeze_forbidden")

    impact_ids = {row["requirement_id"] for row in impact["requirements"]}
    authoritative_manifest = root / "qa-validation/traceability/requirements-manifest.yaml"
    manifest_check = "NOT_PRESENT_IN_PACKAGE"
    if authoritative_manifest.is_file():
        authoritative_ids = requirement_ids_from_manifest(authoritative_manifest)
        missing_ids = sorted(impact_ids - authoritative_ids)
        if missing_ids:
            errors.append(
                "requirements_missing_from_authoritative_manifest:"
                + ",".join(missing_ids)
            )
        manifest_check = "PASS" if not missing_ids else "FAIL"

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "reason_code_count": len(codes),
        "labeling_function_registry_count": len(lf_registry["labeling_functions"]),
        "requirement_impact_count": len(impact_ids),
        "authoritative_manifest_check": manifest_check,
        "weak_supervision_maturity": "CONTRACT_AND_REGISTRY_ONLY",
        "label_model_trained": False,
        "active_learning_selection_running": False,
        "site_thresholds_frozen": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--write-report", type=Path)
    args = parser.parse_args()
    report = validate(args.root.resolve())
    if args.write_report:
        path = args.write_report
        if not path.is_absolute():
            path = args.root / path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
