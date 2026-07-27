#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from data.evidence_catalog import load_catalog

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inventory",
        default="docs/05-data/day25-research/dataset-inventory-v0.2.csv",
    )
    args = parser.parse_args()
    rows = load_catalog(ROOT / args.inventory)
    from data.evidence_catalog import validate_catalog
    summary = validate_catalog(rows)
    print(
        "Dataset inventory PASS:",
        f"total={summary.total}",
        f"priority_free_core={summary.priority_free_core}",
        f"restricted={summary.restricted}",
        f"to_verify={summary.to_verify}",
        f"rejected={summary.rejected}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
