#!/usr/bin/env python3
"""Day 32 — Preflight check before model fitting.

Validates that Day 31 readiness status permits Day 32 execution
and that authorization constraints are correctly set.

Reference: Execution Plan Bước 1 (Regression) + Bước 6 (Authorization).
"""
from pathlib import Path
import argparse
import json

import yaml


def main() -> int:
    p = argparse.ArgumentParser(
        description="Day 32 preflight — verify Day 31 readiness and authorization."
    )
    p.add_argument("--day31-readiness", required=True, help="Day 31 readiness JSON")
    p.add_argument("--authorization", required=True, help="Day 32 authorization YAML")
    p.add_argument("--output", required=True, help="Output preflight evidence path")
    args = p.parse_args()

    readiness = json.loads(Path(args.day31_readiness).read_text(encoding="utf-8"))
    auth = yaml.safe_load(Path(args.authorization).read_text(encoding="utf-8"))

    errors = []
    if readiness.get("status") not in {
        "GO_FOR_DAY32_SEPARATE_BASELINE_SMOKE",
        "GO_FOR_DAY32_SEPARATE_BASELINE_FULL",
    }:
        errors.append("day31_not_ready")
    if auth.get("sealed_test_access_allowed") is not False:
        errors.append("sealed_test_must_be_false")
    if auth.get("pooled_training_allowed") is not False:
        errors.append("pooled_training_must_be_false")

    result = {
        "schema_version": "day32-preflight.v1",
        "pass": not errors,
        "errors": errors,
        "day31_status": readiness.get("status"),
        "authorization_status": auth.get("status"),
        "real_training_allowed": False,
        "sealed_test_opened": False,
        "pooled_training_allowed": False,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
