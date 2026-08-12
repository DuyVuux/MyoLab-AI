from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import jsonschema
import yaml


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.repo_root.resolve()

    semg_core = root / "packages/semg-core"
    sys.path.insert(0, str(semg_core))
    from semg_core.processing.profile_contract import validate_catalog_semantics

    schema = json.loads(
        (root / "packages/common-schemas/json/processing-profile.schema.json")
        .read_text(encoding="utf-8")
    )
    catalog = yaml.safe_load(
        (root / "configs/processing/preprocessing-profiles.v0.1.yaml")
        .read_text(encoding="utf-8")
    )
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(catalog)
    validate_catalog_semantics(catalog)

    gate_text = (
        root / "docs/00-executive/gates/GATE-C-R-qc-research-readiness.md"
    ).read_text(encoding="utf-8")
    if "QC_RESEARCH_CORE_READY" not in gate_text:
        raise RuntimeError("DAY40 requires QC_RESEARCH_CORE_READY")

    eligibility = json.loads(
        (root / "packages/common-schemas/json/quality-eligibility.schema.json")
        .read_text(encoding="utf-8")
    )
    permission_values = set(
        eligibility["properties"]["processing_permission"]["enum"]
    )
    expected = {
        "ALLOW_PROFILED_PROCESSING",
        "HOLD_FOR_REVIEW",
        "BLOCK_UNSUPPORTED_METRIC",
        "ABSTAIN",
    }
    if permission_values != expected:
        raise RuntimeError("DAY31 processing-permission contract changed unexpectedly")

    freeze = json.loads(
        (root / "qa-validation/evidence/day38-qc-freeze-manifest.v0.2.json")
        .read_text(encoding="utf-8")
    )
    mismatches: list[str] = []
    for item in freeze["items"]:
        path = root / item["path"]
        if not path.exists() or sha256_file(path) != item["sha256"]:
            mismatches.append(item["path"])
    if mismatches:
        raise RuntimeError(f"DAY38 frozen QC core mismatch: {mismatches}")

    active = [p for p in catalog["profiles"] if p["status"] == "ACTIVE_RESEARCH"]
    if not active:
        raise RuntimeError("at least one ACTIVE_RESEARCH profile is required")
    for profile in active:
        if profile["site_binding"] is not None:
            raise RuntimeError("active DAY40 profile cannot be site-bound")
        enabled = [
            profile["grid"]["resampling"]["enabled"],
            profile["steps"]["bandpass"]["enabled"],
            profile["steps"]["notch"]["enabled"],
            profile["steps"]["rectification"]["enabled"],
            profile["steps"]["smoothing"]["enabled"],
            profile["steps"]["normalization"]["enabled"],
        ]
        if any(enabled):
            raise RuntimeError(
                "DAY40 active entry profile must not enable unverified DSP transforms"
            )

    result = {
        "status": "PASS",
        "profiles": len(catalog["profiles"]),
        "active_profiles": len(active),
        "day38_frozen_hashes_verified": len(freeze["items"]),
        "site_specific_assumptions": 0,
        "enabled_unverified_transforms": 0,
    }
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
