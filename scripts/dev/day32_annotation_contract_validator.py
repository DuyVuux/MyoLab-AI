from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import jsonschema
import yaml


def _load_semantics(root: Path):
    path = root / "qa-validation/lib/day32_annotation_semantics.py"
    spec = importlib.util.spec_from_file_location("day32_annotation_semantics", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load DAY32 semantics")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate(root: Path) -> dict[str, int | str]:
    contract_path = root / "clinical/labels/qc-annotation-schema.v0.2-research.yaml"
    acquisition_path = root / "clinical/labels/annotation-acquisition-policy.v0.2-research.yaml"
    readiness_path = root / "qa-validation/evidence/day32-data-readiness.template.yaml"
    schema_path = (
        root / "packages/common-schemas/json/qc-annotation-item.research.v0.2.schema.json"
    )

    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    acquisition = yaml.safe_load(acquisition_path.read_text(encoding="utf-8"))
    readiness = yaml.safe_load(readiness_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator(schema)
    semantics = _load_semantics(root)

    tiers = [x["id"] for x in contract["evidence_tiers"]]
    expected = [
        "SYNTHETIC_KNOWN_TRUTH",
        "WEAK_LABEL_CANDIDATE",
        "EXPERT_ANNOTATION",
        "ADJUDICATED_REFERENCE",
    ]
    if tiers != expected:
        raise ValueError(f"unexpected evidence tier ladder: {tiers}")
    if contract["automatic_promotion_forbidden"] is not True:
        raise ValueError("automatic evidence promotion must be forbidden")
    if acquisition["selection_unit"] != "QC_WINDOW_WITH_CONTEXT":
        raise ValueError("acquisition unit must be DAY22 WindowIdentity")
    if acquisition["random_crop_forbidden"] is not True:
        raise ValueError("random crop must be forbidden")
    if any(x["hard_quota"] is not None for x in acquisition["selection_strata"]):
        raise ValueError("DAY32 may not hard-code annotation quotas")
    if readiness["clinical_claims_allowed"] is not False:
        raise ValueError("DAY32 readiness cannot allow clinical claims")

    fixture_dir = root / "qa-validation/test-data/day32"
    positives = sorted(fixture_dir.glob("valid-*.json"))
    negatives = sorted(fixture_dir.glob("invalid-*.json"))
    for path in positives:
        item = json.loads(path.read_text(encoding="utf-8"))
        validator.validate(item)
        semantics.validate_item_semantics(item)
    rejected = 0
    for path in negatives:
        item = json.loads(path.read_text(encoding="utf-8"))
        schema_errors = list(validator.iter_errors(item))
        try:
            semantics.validate_item_semantics(item)
            semantic_error = False
        except Exception:
            semantic_error = True
        if not schema_errors and not semantic_error:
            raise ValueError(f"negative fixture unexpectedly accepted: {path.name}")
        rejected += 1

    return {
        "status": "PASS",
        "evidence_tiers": len(tiers),
        "acquisition_strata": len(acquisition["selection_strata"]),
        "positive_fixtures": len(positives),
        "negative_fixtures_rejected": rejected,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", "--root", dest="repo_root", default=".")
    args = parser.parse_args()
    result = validate(Path(args.repo_root).resolve())
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
