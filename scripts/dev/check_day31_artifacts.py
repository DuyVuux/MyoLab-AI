#!/usr/bin/env python3
"""Audit required Day 31 artifacts, safety flags, schemas, and evidence."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "semg-core"))
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day31.io import dump_json_strict

REQUIRED = (
    "docs/plans/version01/DAY31_EXECUTION_PLAN.md",
    "docs/06-ai-signal-processing/day31/README.md",
    "ai-core/configs/day31_feature_contract.v1.yaml",
    "ai-core/configs/day31_spectral_contract.v1.yaml",
    "ai-core/configs/day31_quality_thresholds.provisional.yaml",
    "packages/semg-core/semg_core/day31_features/feature_set_14_v1.py",
    "packages/semg-core/semg_core/day31_features/spectral_v1.py",
    "packages/semg-core/semg_core/day31_features/long_format.py",
    "packages/semg-core/semg_core/day31_features/quality.py",
    "ai-core/data/day31/pipeline.py",
    "ai-core/data/day31/io.py",
    "scripts/data/day31_extract_features.py",
    "scripts/dev/stress_test_day31.py",
    "scripts/dev/run_day31_checks.sh",
    "qa-validation/requirements/day31-acceptance-criteria.md",
    "qa-validation/test-plans/day31-feature-engineering-test-plan.md",
    "qa-validation/traceability/day31-requirement-test-traceability.csv",
)
SAFETY_KEYS = {
    "training_allowed",
    "model_fitting_allowed",
    "scaler_fitting_allowed",
    "pooled_training_allowed",
    "test_signal_access_allowed",
    "test_set_opened",
    "fatigue_inference_allowed",
    "clinical_use_allowed",
    "training_executed",
    "model_fitting_executed",
    "pooled_training_executed",
}
PROHIBITED_SUFFIXES = {
    ".pkl",
    ".pickle",
    ".joblib",
    ".onnx",
    ".pt",
    ".pth",
    ".mat",
    ".dat",
    ".parquet",
    ".npy",
    ".npz",
}
SCHEMA_MAP = {
    "day31-preflight.json": "day31-preflight.v1.schema.json",
    "day31-feature-registry.json": "day31-feature-registry.v1.schema.json",
    "day31-feature-contract-validation.json": (
        "day31-feature-contract-validation.v1.schema.json"
    ),
    "day31-stress-test.json": "day31-stress-test.v1.schema.json",
    "day31-feature-manifest.json": "day31-feature-manifest.v1.schema.json",
    "day31-readiness-decision.json": "day31-readiness-decision.v1.schema.json",
}


def _unsafe_values(
    value: Any,
    path: str = "$",
) -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            child = f"{path}.{key}"
            if key in SAFETY_KEYS and item is not False:
                findings.append(child)
            findings.extend(_unsafe_values(item, child))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(_unsafe_values(item, f"{path}[{index}]"))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--evidence-dir",
        default="qa-validation/evidence/day31",
    )
    parser.add_argument(
        "--output",
        default="qa-validation/evidence/day31/day31-artifact-check.json",
    )
    arguments = parser.parse_args()
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    prohibited: list[str] = []
    scan_roots = (
        ROOT / "ai-core" / "data" / "day31",
        ROOT / "data-platform" / "contracts" / "day31",
        ROOT / "packages" / "semg-core" / "semg_core" / "day31_features",
    )
    for scan_root in scan_roots:
        if scan_root.exists():
            prohibited.extend(
                str(path.relative_to(ROOT))
                for path in scan_root.rglob("*")
                if path.is_file() and path.suffix.lower() in PROHIBITED_SUFFIXES
            )

    unsafe: list[str] = []
    config_paths = sorted((ROOT / "ai-core" / "configs").glob("day31_*.yaml"))
    evidence_dir = ROOT / arguments.evidence_dir
    evidence_paths = sorted(evidence_dir.glob("*.json")) if evidence_dir.exists() else []
    for path in (*config_paths, *evidence_paths):
        try:
            if path.suffix == ".json":
                document = json.loads(
                    path.read_text(encoding="utf-8"),
                    parse_constant=lambda constant: (_ for _ in ()).throw(
                        ValueError(f"non-standard JSON constant {constant}")
                    ),
                )
            else:
                document = yaml.safe_load(path.read_text(encoding="utf-8"))
            unsafe.extend(
                f"{path.relative_to(ROOT)}:{finding}"
                for finding in _unsafe_values(document)
            )
        except (OSError, TypeError, ValueError, yaml.YAMLError) as error:
            unsafe.append(f"{path.relative_to(ROOT)}:parse_error:{error}")

    schema_errors: list[str] = []
    schema_root = ROOT / "packages" / "common-schemas" / "json"
    for evidence_name, schema_name in SCHEMA_MAP.items():
        evidence_path = evidence_dir / evidence_name
        if not evidence_path.exists():
            schema_errors.append(f"missing_evidence:{evidence_name}")
            continue
        try:
            instance = json.loads(evidence_path.read_text(encoding="utf-8"))
            schema = json.loads((schema_root / schema_name).read_text(encoding="utf-8"))
            errors = sorted(
                Draft202012Validator(schema).iter_errors(instance),
                key=lambda error: list(error.absolute_path),
            )
            schema_errors.extend(
                f"{evidence_name}:{'/'.join(map(str, error.absolute_path))}:{error.message}"
                for error in errors
            )
        except (OSError, TypeError, ValueError) as error:
            schema_errors.append(f"{evidence_name}:validation_error:{error}")

    source_patterns = (
        re.compile(r"\.fit\s*\("),
        re.compile(r"\.train\s*\("),
        re.compile(r"fit_transform\s*\("),
    )
    prohibited_calls: list[str] = []
    source_files = [
        *sorted((ROOT / "ai-core" / "data" / "day31").glob("*.py")),
        *sorted((ROOT / "scripts" / "data").glob("day31_*.py")),
        *sorted((ROOT / "scripts" / "dev").glob("*day31*.py")),
    ]
    for path in source_files:
        text = path.read_text(encoding="utf-8")
        for pattern in source_patterns:
            if pattern.search(text):
                prohibited_calls.append(
                    f"{path.relative_to(ROOT)}:{pattern.pattern}"
                )

    manifest_errors: list[str] = []
    manifest_path = ROOT / "qa-validation/evidence/day31-artifact-manifest.json"
    if manifest_path.exists():
        import hashlib
        try:
            raw_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            for item in raw_manifest.get("artifacts", []):
                item_path = ROOT / item["path"]
                if not item_path.exists():
                    manifest_errors.append(f"manifest_missing:{item['path']}")
                    continue
                digest = hashlib.sha256(item_path.read_bytes()).hexdigest()
                if digest != item["sha256"]:
                    manifest_errors.append(f"manifest_hash_mismatch:{item['path']}")
        except (json.JSONDecodeError, OSError, KeyError, TypeError, ValueError) as error:
            manifest_errors.append(f"manifest_parse_error:{error}")

    result = {
        "schema_version": "day31-artifact-check.v1",
        "missing": missing,
        "prohibited_artifacts": sorted(prohibited),
        "unsafe_flags": sorted(unsafe),
        "schema_errors": sorted(schema_errors),
        "manifest_errors": sorted(manifest_errors),
        "prohibited_training_calls": sorted(prohibited_calls),
        "pass": not (
            missing
            or prohibited
            or unsafe
            or schema_errors
            or manifest_errors
            or prohibited_calls
        ),
    }
    dump_json_strict(ROOT / arguments.output, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
