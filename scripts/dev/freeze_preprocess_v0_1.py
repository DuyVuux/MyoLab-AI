#!/usr/bin/env python3
"""Ghi registry freeze cho preprocess_v0.1 sau khi verification pass."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import yaml

ROOT = Path(__file__).resolve().parents[2]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError(f"JSON root phải là object: {path}")
    return dict(payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verification", type=Path, required=True)
    parser.add_argument("--environment", type=Path, required=True)
    parser.add_argument("--registry", type=Path, default=ROOT / "mlops/registry/preprocessing_configs.yaml")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    verification = load_json(args.verification)
    environment = load_json(args.environment)
    overall = verification.get("overall", {})
    if overall.get("all_passed") is not True:
        raise SystemExit("Không được freeze: verification chưa pass")
    if overall.get("clinical_validation_status") != "not_validated":
        raise SystemExit("Không được freeze với clinical claim không hợp lệ")

    implementation_paths = [
        ROOT / "packages/semg-core/semg_core/preprocessing.py",
        ROOT / "services/preprocessing-service/src/filters.py",
        ROOT / "services/preprocessing-service/src/pipeline.py",
        ROOT / "services/preprocessing-service/src/preprocess_config.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in implementation_paths if not path.is_file()]
    if missing:
        raise SystemExit(f"Thiếu implementation files: {missing}")

    config_path = ROOT / verification["config"]["path"]
    if file_sha256(config_path) != verification["config"]["sha256"]:
        raise SystemExit("Config đã thay đổi sau verification")

    registry_path = args.registry
    if registry_path.exists():
        raw = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
        registry = dict(raw) if isinstance(raw, Mapping) else {}
    else:
        registry = {}
    registry["schema_version"] = "preprocessing-config-registry.v0.1"
    entries = list(registry.get("preprocessing_configs", []))

    entry = {
        "config_id": verification["config"]["config_id"],
        "lifecycle_status": "frozen_for_mvp0",
        "analytically_verified_for_mvp0": True,
        "clinical_validation_status": "not_validated",
        "execution_mode": "offline_zero_phase",
        "realtime_compatible": False,
        "verified_sampling_rates_hz": [verification["profile"]["sampling_rate_hz"]],
        "config": {
            "path": verification["config"]["path"],
            "sha256": verification["config"]["sha256"],
        },
        "implementation_files": [
            {"path": str(path.relative_to(ROOT)), "sha256": file_sha256(path)}
            for path in implementation_paths
        ],
        "verification": {
            "report_path": str(args.verification.resolve().relative_to(ROOT)),
            "report_sha256": file_sha256(args.verification),
            "profile_id": verification["profile"]["profile_id"],
            "profile_sha256": verification["profile"]["sha256"],
        },
        "environment": {
            "report_path": str(args.environment.resolve().relative_to(ROOT)),
            "report_sha256": file_sha256(args.environment),
            "python_version": environment["python"]["version"],
            "numpy_version": environment["libraries"]["numpy"],
            "scipy_version": environment["libraries"]["scipy"],
        },
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "change_policy": (
            "Bất kỳ thay đổi hành vi nào sau đây đều phải tạo version mới, ví dụ preprocess_v0.2: "
            "cutoff; filter family; order; SOS/filtfilt behavior; notch policy; edge guard; resampling; dtype; cách xử lý NaN/Inf. "
            "Sửa typo trong Markdown không cần bump preprocessing version. Sửa code có thể thay output số học thì phải bump hoặc re-verify và ghi change decision."
        ),
        "limitations": verification.get("limitations", []),
    }

    entries = [item for item in entries if not (isinstance(item, Mapping) and item.get("config_id") == entry["config_id"])]
    entries.append(entry)
    registry["preprocessing_configs"] = entries
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(yaml.safe_dump(registry, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(json.dumps({
        "registry": str(registry_path),
        "config_id": entry["config_id"],
        "lifecycle_status": entry["lifecycle_status"],
        "clinical_validation_status": entry["clinical_validation_status"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
