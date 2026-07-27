#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from data.readiness_gate_v2 import build_day25_gate, load_csv

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inventory",
        default="docs/05-data/day25-research/dataset-inventory-v0.2.csv",
    )
    parser.add_argument(
        "--conflicts",
        default="docs/05-data/day25-research/research-conflict-register.csv",
    )
    parser.add_argument(
        "--sources",
        default="docs/05-data/day25-research/source-evidence-register.csv",
    )
    parser.add_argument(
        "--site-audit",
        default="qa-validation/evidence/day25-noraxon-site-audit.json",
    )
    parser.add_argument(
        "--split",
        default="qa-validation/evidence/day25-subject-group-split-v0.2.json",
    )
    parser.add_argument(
        "--output",
        default="qa-validation/evidence/day25-data-readiness-gate-v0.2.json",
    )
    args = parser.parse_args()

    report = build_day25_gate(
        inventory_rows=load_csv(ROOT / args.inventory),
        conflict_rows=load_csv(ROOT / args.conflicts),
        source_rows=load_csv(ROOT / args.sources),
        site_audit=json.loads((ROOT / args.site_audit).read_text(encoding="utf-8")),
        split=json.loads((ROOT / args.split).read_text(encoding="utf-8")),
    )
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        "Readiness gate:", report["status"],
        "implementationAllowed=", report["implementationAllowed"],
        "trainingAllowed=", report["trainingAllowed"],
    )
    return 0 if report["status"] != "BLOCKED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
