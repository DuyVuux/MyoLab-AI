#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ai-core" / "data"))

from day28.preflight import result_to_dict, run_preflight


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Day 27 manifests before Day 28 EDA")
    parser.add_argument("--manifest-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_preflight(args.manifest_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result_to_dict(result), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result_to_dict(result), ensure_ascii=False, indent=2))
    return 0 if result.ready_for_real_eda else 2


if __name__ == "__main__":
    raise SystemExit(main())
