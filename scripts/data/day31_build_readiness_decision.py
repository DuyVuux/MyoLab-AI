#!/usr/bin/env python3
"""Build the Day 31 Feature Engineering Gate decision."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "semg-core"))
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day31.io import dump_json_strict
from day31.readiness import decide_feature_gate


def _load(path: str) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON root must be an object: {path}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", required=True)
    parser.add_argument("--contract-validation", required=True)
    parser.add_argument("--smoke", required=True)
    parser.add_argument("--quality", required=True)
    parser.add_argument("--stress", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--full-materialization-complete", action="store_true")
    parser.add_argument("--dependency-lock-resolved", action="store_true")
    parser.add_argument(
        "--day32-training-authorization-present",
        action="store_true",
    )
    arguments = parser.parse_args()
    try:
        preflight = _load(arguments.preflight)
        contract = _load(arguments.contract_validation)
        smoke = _load(arguments.smoke)
        quality = _load(arguments.quality)
        stress = _load(arguments.stress)
        manifest = _load(arguments.manifest)
        views = smoke.get("views", {})
        if not isinstance(views, dict):
            raise TypeError("smoke evidence views must be an object")
        evidence = {
            "preflight": preflight,
            "contract_validation": contract,
            "golden_tests": smoke.get("golden_tests"),
            "mendeley_smoke": views.get("mendeley_core4_primary_v1"),
            "grabmyo_smoke": views.get(
                "grabmyo_project_subset_native28_v1"
            ),
            "quality": quality,
            "stress": stress,
            "manifest": manifest,
            "test_signal_rows_read": max(
                int(smoke.get("test_signal_rows_read", -1)),
                int(stress.get("test_signal_rows_read", -1)),
                int(manifest.get("test_signal_rows_read", -1)),
            ),
            "training_executed": any(
                item.get("training_executed") is not False
                for item in (smoke, quality, stress, manifest)
            ),
            "model_fitting_executed": any(
                item.get("model_fitting_executed") is not False
                for item in (smoke, stress, manifest)
            ),
            "pooled_training_executed": any(
                item.get("pooled_training_executed") is not False
                for item in (smoke, stress, manifest)
            ),
            "full_materialization_complete": (
                arguments.full_materialization_complete
            ),
            "dependency_lock_resolved": arguments.dependency_lock_resolved,
            "day32_training_authorization_present": (
                arguments.day32_training_authorization_present
            ),
        }
        decision = decide_feature_gate(evidence)
        dump_json_strict(arguments.output, decision)
        print(json.dumps(decision, ensure_ascii=False, indent=2))
        return 0 if decision["pass"] else 2
    except (OSError, TypeError, ValueError) as error:
        print(f"day31 readiness build failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
