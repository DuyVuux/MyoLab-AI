#!/usr/bin/env python3
"""CLI chính cho Offline Analysis Pipeline MVP-0."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from offline_analysis import run_offline_analysis


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--config", type=Path, default=Path("ai-core/configs/offline_analysis_mvp0.yaml"))
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--expect-status")
    p.add_argument("--expect-conclusion")
    p.add_argument("--quiet", action="store_true")
    return p.parse_args()


def main() -> int:
    a = parse_args()
    manifest = run_offline_analysis(
        manifest_path=a.manifest,
        output_dir=a.output_dir,
        config_path=a.config,
        overwrite=a.overwrite,
    )
    if not a.quiet:
        print(json.dumps({
            "analysis_id": manifest["analysis_id"],
            "status": manifest["status"],
            "technical_conclusion": manifest["final"]["technical_conclusion"],
            "confidence_category": manifest["final"]["engineering_confidence_category"],
            "fingerprint": manifest["analysis_fingerprint_sha256"],
            "output_dir": str(a.output_dir),
        }, indent=2, ensure_ascii=False))
    errors = []
    if a.expect_status and manifest["status"] != a.expect_status:
        errors.append("status mismatch")
    if a.expect_conclusion and manifest["final"]["technical_conclusion"] != a.expect_conclusion:
        errors.append("conclusion mismatch")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
