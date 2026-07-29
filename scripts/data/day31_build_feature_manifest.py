#!/usr/bin/env python3
"""Build a reproducibility manifest from verified Day 31 artifacts."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "semg-core"))
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day31.io import dump_json_strict


def _hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON root must be an object: {path}")
    return value


def _git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--window-index", required=True)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--source-manifest")
    parser.add_argument("--registry", required=True)
    parser.add_argument("--smoke", required=True)
    parser.add_argument("--quality", required=True)
    parser.add_argument("--stress", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--run-type",
        choices=("portable_synthetic_validation", "zone2_feature_extraction"),
        default="portable_synthetic_validation",
    )
    arguments = parser.parse_args()
    try:
        paths = {
            "window_index": Path(arguments.window_index),
            "contract": Path(arguments.contract),
            "registry": Path(arguments.registry),
            "smoke": Path(arguments.smoke),
            "quality": Path(arguments.quality),
            "stress": Path(arguments.stress),
        }
        documents = {
            name: _load_json(path)
            for name, path in paths.items()
            if name in {"registry", "smoke", "quality", "stress"}
        }
        input_pass = all(
            documents[name].get("pass") is True
            for name in ("registry", "smoke", "quality", "stress")
        )
        smoke = documents["smoke"]
        views = smoke.get("views", {})
        feature_rows = (
            sum(
                int(view.get("feature_rows", 0))
                for view in views.values()
                if isinstance(view, dict)
            )
            if isinstance(views, dict)
            else 0
        )
        output_hashes = {
            name: _hash(path)
            for name, path in paths.items()
            if name in {"registry", "smoke", "quality", "stress"}
        }
        contract_hash = _hash(paths["contract"])
        run_id = (
            f"day31-{arguments.run_type}-"
            f"{contract_hash[:12]}-{output_hashes['stress'][:12]}"
        )
        source_manifest_hash = (
            _hash(Path(arguments.source_manifest))
            if arguments.source_manifest
            else None
        )
        manifest = {
            "schema_version": "day31-feature-manifest.v1",
            "run_id": run_id,
            "run_type": arguments.run_type,
            "created_at_utc": datetime.now(UTC).isoformat(),
            "git_commit": _git_commit(),
            "input_window_index_sha256": _hash(paths["window_index"]),
            "feature_contract_sha256": contract_hash,
            "source_manifest_sha256": source_manifest_hash,
            "preprocessing_policy_id": "per-record-channel-mean-v1",
            "channel_policy_ids": [
                "grabmyo-fw28-primary-v1",
                "mendeley-ch123-primary-v1",
            ],
            "dataset_views": [
                "grabmyo_project_subset_native28_v1",
                "mendeley_core4_primary_v1",
            ],
            "window_ms": 200,
            "hop_ms": 100,
            "sampling_mode": "native_rate",
            "feature_arms": [
                "F-TD8",
                "F-SP6",
                "F-ALL14",
                "F-NO-MOMENTS12",
                "F-TD8-W250",
                "F-SP6-W250",
                "F-SP6-W500-CONTEXT",
            ],
            "feature_rows": feature_rows,
            "failure_count": 0 if input_pass else 1,
            "output_hashes": output_hashes,
            "real_data_signal_rows_read": 0,
            "test_signal_rows_read": 0,
            "training_executed": False,
            "model_fitting_executed": False,
            "pooled_training_executed": False,
            "pass": input_pass,
        }
        dump_json_strict(arguments.output, manifest)
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0 if input_pass else 2
    except (
        OSError,
        TypeError,
        ValueError,
        subprocess.CalledProcessError,
    ) as error:
        print(f"day31 manifest build failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
