#!/usr/bin/env python3
"""Đăng ký frequency_features_v0.1 vào feature extractor registry."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "mlops/registry/feature_extractors.yaml"


def sha(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main() -> int:
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}
    entries = list(data.setdefault("feature_extractors", []))
    result = json.loads((ROOT / "qa-validation/evidence/day10-frequency-features.json").read_text(encoding="utf-8"))
    entry = {
        "config_id": "frequency_features_v0.1",
        "schema_version": "feature-extractor-registry-entry.v0.1",
        "lifecycle_status": "implemented_for_mvp0",
        "analytical_verification_status": "passed",
        "clinical_validation_status": "not_validated",
        "implemented_features": ["mdf", "mnf"],
        "input_profile_id": "frequency_domain",
        "required_spectral_estimator_id": "spectral_estimation_v0.1",
        "frequency_unit": "Hz",
        "fatigue_inference_in_scope": False,
        "ml_training_in_scope": False,
        "artifacts": {
            "config": {"path": "services/feature-extraction-service/configs/frequency_features_v0.1.yaml", "sha256": sha("services/feature-extraction-service/configs/frequency_features_v0.1.yaml")},
            "core": {"path": "packages/semg-core/semg_core/spectral_features.py", "sha256": sha("packages/semg-core/semg_core/spectral_features.py")},
            "extractor": {"path": "services/feature-extraction-service/src/frequency_feature_extractor.py", "sha256": sha("services/feature-extraction-service/src/frequency_feature_extractor.py")},
            "result_schema": {"path": "packages/common-schemas/json/frequency-feature-extraction-result.schema.json", "sha256": sha("packages/common-schemas/json/frequency-feature-extraction-result.schema.json")},
        },
        "evidence": {
            "analytical_verification": "qa-validation/evidence/day10-mdf-mnf-verification.json",
            "golden_e2e": "qa-validation/evidence/day10-frequency-features.json",
            "golden_result_hash_sha256": result["result_hash_sha256"],
            "golden_computed_row_count": result["summary"]["computed_row_count"],
        },
        "limitations": [
            "MDF/MNF chỉ là feature theo từng cửa sổ; chưa có slope hoặc fatigue inference.",
            "Cấu hình chưa được xác nhận lâm sàng.",
        ],
    }
    entries = [item for item in entries if item.get("config_id") != entry["config_id"]]
    entries.append(entry)
    data["feature_extractors"] = entries
    REGISTRY.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print("Registered frequency_features_v0.1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
