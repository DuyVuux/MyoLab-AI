#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from data.group_split_v2 import SplitRatios, build_group_split

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--metadata",
        default="qa-validation/test-data/synthetic/day25-subject-session-metadata.json",
    )
    parser.add_argument(
        "--output",
        default="qa-validation/evidence/day25-subject-group-split-v0.2.json",
    )
    parser.add_argument("--dataset-id", default="SYNTHETIC_DAY25")
    parser.add_argument("--group-unit", choices=["subject", "session"], default="subject")
    parser.add_argument("--seed", type=int, default=2501)
    args = parser.parse_args()

    records = json.loads((ROOT / args.metadata).read_text(encoding="utf-8"))
    result = build_group_split(
        records,
        dataset_id=args.dataset_id,
        group_unit=args.group_unit,
        ratios=SplitRatios(),
        seed=args.seed,
    )
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        "Subject-safe split PASS:",
        result["counts"],
        "hash=", result["splitHashSha256"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
