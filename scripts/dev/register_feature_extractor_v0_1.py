#!/usr/bin/env python3
"""Đăng ký features_semg_v0.1 vào registry bằng evidence Day 8.

Script không tuyên bố clinical validation. Nó chỉ ghi lại config/code/schema hash,
analytical verification và golden synthetic E2E status để tái lập MVP-0.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Đăng ký feature extractor RMS/MAV v0.1")
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("mlops/registry/feature_extractors.yaml"),
    )
    parser.add_argument(
        "--verification",
        type=Path,
        default=Path("qa-validation/evidence/day8-time-domain-feature-verification.json"),
    )
    parser.add_argument(
        "--golden-result",
        type=Path,
        default=Path("qa-validation/evidence/day8-time-domain-features.json"),
    )
    return parser.parse_args()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON phải là object: {path}")
    return payload


def main() -> int:
    args = parse_args()
    verification = _load_json(args.verification)
    golden = _load_json(args.golden_result)
    if verification.get("verification_status") != "passed":
        raise SystemExit("Không đăng ký: analytical verification chưa passed")
    if golden.get("status") not in {"completed", "completed_with_exclusions"}:
        raise SystemExit("Không đăng ký: golden E2E chưa completed")
    if golden.get("downstream_allowed") is not True:
        raise SystemExit("Không đăng ký: golden E2E không downstream_allowed")

    config_path = ROOT / "services/feature-extraction-service/configs/features_semg_v0.1.yaml"
    core_path = ROOT / "packages/semg-core/semg_core/features.py"
    extractor_path = ROOT / "services/feature-extraction-service/src/extractor.py"
    row_schema_path = ROOT / "packages/common-schemas/json/feature-row.schema.json"
    result_schema_path = ROOT / "packages/common-schemas/json/time-domain-feature-result.schema.json"

    entry = {
        "config_id": "features_semg_v0.1",
        "schema_version": "feature-extractor-registry-entry.v0.1",
        "lifecycle_status": "implemented_for_mvp0",
        "analytical_verification_status": "passed",
        "clinical_validation_status": "not_validated",
        "implemented_features": ["rms", "mav"],
        "input_profile_id": "time_domain",
        "canonical_amplitude_unit": "uV",
        "normalization": "none",
        "mvc_normalized": False,
        "cross_session_amplitude_comparison_allowed": False,
        "cross_subject_amplitude_comparison_allowed": False,
        "fatigue_inference_in_scope": False,
        "ml_training_in_scope": False,
        "artifacts": {
            "config": {
                "path": _relative(config_path),
                "sha256": _sha256(config_path),
            },
            "core": {
                "path": _relative(core_path),
                "sha256": _sha256(core_path),
            },
            "extractor": {
                "path": _relative(extractor_path),
                "sha256": _sha256(extractor_path),
            },
            "row_schema": {
                "path": _relative(row_schema_path),
                "sha256": _sha256(row_schema_path),
            },
            "result_schema": {
                "path": _relative(result_schema_path),
                "sha256": _sha256(result_schema_path),
            },
        },
        "evidence": {
            "analytical_verification": _relative(args.verification),
            "golden_e2e": _relative(args.golden_result),
            "golden_result_hash_sha256": golden.get("result_hash_sha256"),
            "golden_computed_row_count": golden.get("summary", {}).get(
                "computed_row_count"
            ),
        },
        "limitations": [
            "Chỉ RMS/MAV theo từng time-domain window 500 ms.",
            "Không có MVC/baseline normalization.",
            "Không tạo fatigue status, FRS hoặc khuyến nghị lâm sàng.",
            "Evidence hiện tại là synthetic/software verification, không phải clinical validation.",
        ],
    }

    registry_path = args.registry
    if not registry_path.is_absolute():
        registry_path = ROOT / registry_path
    if registry_path.exists():
        loaded = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        registry = dict(loaded) if isinstance(loaded, dict) else {}
    else:
        registry = {}
    entries = registry.get("feature_extractors", [])
    if not isinstance(entries, list):
        raise SystemExit("feature_extractors trong registry phải là list")
    entries = [
        item
        for item in entries
        if not (isinstance(item, dict) and item.get("config_id") == "features_semg_v0.1")
    ]
    entries.append(entry)
    entries.sort(key=lambda item: str(item.get("config_id", "")))
    registry = {
        "schema_version": "feature-extractor-registry.v0.1",
        "feature_extractors": entries,
    }
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(
        yaml.safe_dump(registry, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    print(f"Registered features_semg_v0.1 -> {registry_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
