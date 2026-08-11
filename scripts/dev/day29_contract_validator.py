from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

REQUIRED_IDS = {"FR-004", "FR-005", "FR-006", "FR-010", "FR-037", "FR-038", "NFR-012"}
MANDATORY = [
    "services/quality-gate-service/src/detectors/data_integrity.py",
    "packages/common-schemas/json/qc-data-quality-codes.schema.json",
    "qa-validation/automated-tests/qc/test_data_integrity_qc.py",
    "ai-core/configs/distribution-support-inputs.v0.1.yaml",
]
FORBIDDEN_OOD = {
    "ood_score", "ood_probability", "shift_threshold",
    "reference_distribution_fit", "automatic_domain_adaptation",
    "test_time_adaptation", "shared_embedding",
}


def parse_manifest_ids(raw: object) -> set[str]:
    ids: set[str] = set()
    if isinstance(raw, dict):
        for key, value in raw.items():
            if key in {"id", "requirement_id"} and isinstance(value, str):
                ids.add(value)
            ids.update(parse_manifest_ids(value))
    elif isinstance(raw, list):
        for item in raw:
            ids.update(parse_manifest_ids(item))
    elif isinstance(raw, str) and raw.startswith(("FR-", "NFR-", "AC-", "DR-")):
        ids.add(raw)
    return ids


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--strict-upstream", action="store_true")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()

    missing = [path for path in MANDATORY if not (root / path).exists()]
    if missing:
        raise SystemExit(f"Missing DAY29 mandatory artifacts: {missing}")

    schema = json.loads(
        (root / "packages/common-schemas/json/qc-data-quality-codes.schema.json")
        .read_text(encoding="utf-8")
    )
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        raise SystemExit("DAY29 schema must use JSON Schema Draft 2020-12")

    dist = yaml.safe_load(
        (root / "ai-core/configs/distribution-support-inputs.v0.1.yaml")
        .read_text(encoding="utf-8")
    )
    if dist.get("status") != "CONTEXT_ONLY_NO_OOD_SCORE":
        raise SystemExit("Distribution readiness must remain CONTEXT_ONLY_NO_OOD_SCORE")
    forbidden = set(dist.get("forbidden_outputs", []))
    if not FORBIDDEN_OOD.issubset(forbidden):
        raise SystemExit("DAY29 distribution contract does not forbid all overclaim fields")

    manifest = root / "qa-validation/traceability/requirements-manifest.yaml"
    if manifest.exists():
        ids = parse_manifest_ids(yaml.safe_load(manifest.read_text(encoding="utf-8")))
        missing_ids = REQUIRED_IDS - ids
        if missing_ids:
            raise SystemExit(
                "Option-B requirements manifest missing DAY29 IDs: "
                + ", ".join(sorted(missing_ids))
            )
    elif args.strict_upstream:
        raise SystemExit("Strict upstream mode requires requirements-manifest.yaml")

    if args.strict_upstream:
        required_upstream = [
            "packages/common-schemas/json/qc-result.v0.2.schema.json",
            "packages/common-schemas/json/qc-window-identity.schema.json",
            "clinical/labels/qc-labeling-function-registry.v0.1.yaml",
            "packages/common-schemas/json/multimodal-alignment-context.schema.json",
        ]
        absent = [path for path in required_upstream if not (root / path).exists()]
        if absent:
            raise SystemExit(f"Strict DAY29 entry missing upstream artifacts: {absent}")

    print("DAY29 contract validator: PASS")
    print("requirements:", ", ".join(sorted(REQUIRED_IDS)))
    print("distribution readiness: CONTEXT_ONLY_NO_OOD_SCORE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
