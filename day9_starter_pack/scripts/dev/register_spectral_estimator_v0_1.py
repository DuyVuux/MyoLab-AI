#!/usr/bin/env python3
"""Đăng ký spectral_estimation_v0.1 vào feature extractor registry.

Registry entry chỉ ghi nhận analytical verification và synthetic golden E2E.
Nó không tuyên bố clinical validation, MDF/MNF hoặc fatigue inference.
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
    parser = argparse.ArgumentParser(description="Đăng ký Welch PSD estimator v0.1")
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("mlops/registry/feature_extractors.yaml"),
    )
    parser.add_argument(
        "--verification",
        type=Path,
        default=Path("qa-validation/evidence/day9-spectral-verification.json"),
    )
    parser.add_argument(
        "--golden-result",
        type=Path,
        default=Path("qa-validation/evidence/day9-spectral-estimation.json"),
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
        raise SystemExit("Không đăng ký: analytical spectral verification chưa passed")
    if verification.get("clinical_validation_status") != "not_validated":
        raise SystemExit("Không đăng ký: clinical validation status không an toàn")
    if golden.get("status") not in {"completed", "completed_with_exclusions"}:
        raise SystemExit("Không đăng ký: golden E2E chưa completed")
    if golden.get("downstream_allowed") is not True:
        raise SystemExit("Không đăng ký: golden E2E không downstream_allowed")
    if golden.get("config", {}).get("mdf_mnf_computed") is not False:
        raise SystemExit("Không đăng ký: Day 9 không được tính MDF/MNF")

    artifact_paths = {
        "config": ROOT
        / "services/feature-extraction-service/configs/spectral_estimation_v0.1.yaml",
        "core": ROOT / "packages/semg-core/semg_core/spectral.py",
        "frequency_domain": ROOT
        / "services/feature-extraction-service/src/frequency_domain.py",
        "extractor": ROOT
        / "services/feature-extraction-service/src/spectral_estimator.py",
        "row_schema": ROOT
        / "packages/common-schemas/json/spectral-window-row.schema.json",
        "result_schema": ROOT
        / "packages/common-schemas/json/spectral-estimation-result.schema.json",
    }
    for name, path in artifact_paths.items():
        if not path.exists():
            raise SystemExit(f"Thiếu artifact {name}: {path}")

    entry = {
        "config_id": "spectral_estimation_v0.1",
        "schema_version": "feature-extractor-registry-entry.v0.1",
        "lifecycle_status": "implemented_for_mvp0",
        "analytical_verification_status": "passed",
        "clinical_validation_status": "not_validated",
        "implemented_features": ["welch_psd"],
        "planned_features_not_implemented": ["mdf", "mnf", "spectral_slope"],
        "input_profile_id": "frequency_domain",
        "canonical_amplitude_unit": "uV",
        "psd_unit": "uV^2/Hz",
        "analysis_band_hz": [20.0, 400.0],
        "estimator": {
            "method": "welch",
            "taper": "hann",
            "detrend": "constant",
            "scaling": "density",
            "nperseg_policy": "full_outer_window",
            "noverlap_samples": 0,
            "nfft_policy": "equal_outer_window_length",
            "zero_padding_enabled": False,
        },
        "fatigue_inference_in_scope": False,
        "ml_training_in_scope": False,
        "artifacts": {
            name: {"path": _relative(path), "sha256": _sha256(path)}
            for name, path in artifact_paths.items()
        },
        "evidence": {
            "analytical_verification": _relative(args.verification),
            "golden_e2e": _relative(args.golden_result),
            "golden_result_hash_sha256": golden.get("result_hash_sha256"),
            "golden_computed_row_count": golden.get("summary", {}).get(
                "computed_row_count"
            ),
            "golden_frequency_bin_count": golden.get("frequency_axis", {}).get(
                "bin_count"
            ),
        },
        "limitations": [
            "Welch v0.1 dùng một full-window segment; chưa có variance reduction từ nhiều subsegments.",
            "Chưa tính MDF/MNF hoặc trend theo thời gian.",
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
        if not (
            isinstance(item, dict)
            and item.get("config_id") == "spectral_estimation_v0.1"
        )
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
    print(f"Registered spectral_estimation_v0.1 -> {registry_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
