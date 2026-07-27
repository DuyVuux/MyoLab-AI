#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from integrations.devices.noraxon.site_export_audit import audit_site_evidence

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--evidence",
        default="integrations/devices/noraxon/site-export-evidence-bundle.template.json",
    )
    parser.add_argument(
        "--output",
        default="qa-validation/evidence/day25-noraxon-site-audit.json",
    )
    args = parser.parse_args()

    bundle = json.loads((ROOT / args.evidence).read_text(encoding="utf-8"))
    report = audit_site_evidence(bundle)
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(report["status"], ", ".join(report["blockers"]))
    # NOT_VERIFIED is the expected Day 25 result, not a script failure.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
