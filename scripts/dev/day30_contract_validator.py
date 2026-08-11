from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import jsonschema
import yaml


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", "--root", dest="repo_root", default=".")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    config = yaml.safe_load((root / "configs/qc/aggregation.v0.1.yaml").read_text())
    schema_path = root / "packages/common-schemas/json/qc-aggregation-result.v0.1.schema.json"
    schema = json.loads(schema_path.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    site = config["profiles"]["site-template"]
    if site["threshold_status"] != "NOT_VERIFIED":
        raise SystemExit("site aggregation threshold must remain NOT_VERIFIED at DAY30")
    if site["channel_min_usable_window_ratio"] is not None:
        raise SystemExit("site usable-window threshold must remain null")
    if site["session_max_allowed_bad_channels"] is not None:
        raise SystemExit("site bad-channel threshold must remain null")
    impact = yaml.safe_load(
        (root / "qa-validation/traceability/day30-requirement-impact.yaml").read_text()
    )
    ids = {item["id"] for item in impact["requirements"]}
    required = {"FR-030", "FR-037", "FR-040", "FR-041", "AC-03"}
    if not required <= ids:
        raise SystemExit(f"missing traceability IDs: {sorted(required - ids)}")
    print("DAY30 contract validator: PASS")
    print("site thresholds: NOT_VERIFIED/null")
    print("three-layer isolation: REQUIRED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
