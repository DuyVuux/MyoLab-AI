#!/usr/bin/env python3
"""Validate the Day 30 to Day 31 authorization handoff."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "semg-core"))
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day31.io import dump_json_strict
from day31.preflight import validate_preflight


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--day30-readiness", required=True)
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args()
    try:
        config = yaml.safe_load(
            Path(arguments.config).read_text(encoding="utf-8")
        )
        readiness = json.loads(
            Path(arguments.day30_readiness).read_text(encoding="utf-8")
        )
        if not isinstance(config, dict) or not isinstance(readiness, dict):
            raise TypeError("config and readiness roots must be objects")
        result = validate_preflight(config, readiness)
        dump_json_strict(arguments.output, result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["pass"] else 2
    except (OSError, TypeError, ValueError, yaml.YAMLError) as error:
        print(f"day31 preflight failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
