from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import jsonschema


REQUIRED_REQUIREMENTS = {"FR-030", "FR-040", "FR-041", "FR-054"}


def _load_yaml_like(path: Path):
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            import yaml
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                f"{path} is not JSON-compatible YAML and PyYAML is unavailable"
            ) from exc
        return yaml.safe_load(text)


def _collect_requirement_ids(value) -> set[str]:
    ids: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(key, str) and key.startswith(("FR-", "NFR-", "AC-")):
                ids.add(key)
            ids.update(_collect_requirement_ids(item))
    elif isinstance(value, list):
        for item in value:
            ids.update(_collect_requirement_ids(item))
    elif isinstance(value, str) and value.startswith(("FR-", "NFR-", "AC-")):
        ids.add(value)
    return ids


def validate(repo_root: Path) -> dict[str, object]:
    windowing_path = repo_root / "packages/semg-core/semg_core/qc_windowing.py"
    aggregation_path = (
        repo_root
        / "services/quality-gate-service/src/aggregation/qc_aggregation.py"
    )
    config_path = repo_root / "configs/qc/windowing.v0.1.yaml"
    schema_path = (
        repo_root
        / "packages/common-schemas/json/qc-window-identity.schema.json"
    )
    impact_path = (
        repo_root
        / "qa-validation/traceability/day22-requirement-impact.yaml"
    )
    required = [windowing_path, aggregation_path, config_path, schema_path]
    if impact_path.exists():
        required.append(impact_path)

    missing = [str(path.relative_to(repo_root)) for path in required if not path.exists()]
    if missing:
        raise RuntimeError(f"missing DAY22 artifacts: {missing}")

    config = _load_yaml_like(config_path)
    if len(config.get("profiles", [])) < 2:
        raise RuntimeError("DAY22 requires >=2 profiles to prevent global-window freeze")
    if config["invariants"]["one_global_window_size_for_all_protocols"] is not False:
        raise RuntimeError("global window size invariant violated")
    if config["invariants"]["final_qc_aggregation_implemented"] is not False:
        raise RuntimeError("DAY30 final aggregation was pulled into DAY22")

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    if schema["properties"]["annotation_unit_type"].get("const") != "QC_WINDOW_WITH_CONTEXT":
        raise RuntimeError("Active Learning annotation unit lost required context")

    impact_ids = REQUIRED_REQUIREMENTS
    if impact_path.exists():
        impact = _load_yaml_like(impact_path)
        impact_ids = {item["id"] for item in impact["requirements"]}
        if impact_ids != REQUIRED_REQUIREMENTS:
            raise RuntimeError(
                f"requirement impact mismatch: expected {REQUIRED_REQUIREMENTS}, got {impact_ids}"
            )

    manifest_path = repo_root / "qa-validation/traceability/requirements-manifest.yaml"
    manifest_status = "NOT_PRESENT_IN_PACKAGE"
    if manifest_path.exists():
        manifest = _load_yaml_like(manifest_path)
        manifest_ids = _collect_requirement_ids(manifest)
        missing_ids = REQUIRED_REQUIREMENTS.difference(manifest_ids)
        if missing_ids:
            raise RuntimeError(
                f"live requirements-manifest missing DAY22 IDs: {sorted(missing_ids)}"
            )
        manifest_status = "RECONCILED"

    return {
        "status": "PASS",
        "profiles": len(config["profiles"]),
        "requirement_ids": sorted(impact_ids),
        "requirements_manifest": manifest_status,
        "active_learning_unit": "QC_WINDOW_WITH_CONTEXT",
        "final_qc_aggregation": "DEFERRED_TO_DAY30",
        "site_window_thresholds_frozen": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        report = validate(args.repo_root.resolve())
    except Exception as exc:
        print(f"DAY22 CONTRACT VALIDATOR: FAIL: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("DAY22 CONTRACT VALIDATOR: PASS")
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
