#!/usr/bin/env python3
"""Generate the machine-readable registry from the locked YAML contract."""

from __future__ import annotations

import argparse
import json
import sys
from hashlib import sha256
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "semg-core"))
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day31.io import dump_json_strict
from semg_core.day31_features import FEATURE_ORDER, FEATURE_VERSION


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", required=True)
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args()
    try:
        contract_path = Path(arguments.contract)
        raw = contract_path.read_bytes()
        contract = yaml.safe_load(raw)
        if not isinstance(contract, dict):
            raise TypeError("feature contract root must be an object")
        order = contract.get("feature_order")
        features = contract.get("features")
        passed = (
            contract.get("contract_version") == FEATURE_VERSION
            and tuple(order or ()) == FEATURE_ORDER
            and isinstance(features, list)
            and len(features) == 14
        )
        registry = {
            "schema_version": "day31-feature-registry.v1",
            "contract_version": contract.get("contract_version"),
            "feature_count": len(features) if isinstance(features, list) else 0,
            "feature_order": order,
            "features": features,
            "contract_sha256": sha256(raw).hexdigest(),
            "pass": passed,
        }
        dump_json_strict(arguments.output, registry)
        print(json.dumps(registry, ensure_ascii=False, indent=2))
        return 0 if passed else 2
    except (OSError, TypeError, ValueError, yaml.YAMLError) as error:
        print(f"day31 registry generation failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
