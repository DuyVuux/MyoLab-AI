#!/usr/bin/env python3
"""CLI for Generic CSV Day 3 ingestion and canonical-summary export."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SEMGC_PATH = ROOT / "packages" / "semg-core"
INGESTION_PATH = ROOT / "services" / "signal-ingestion-service" / "src"
for path in (SEMGC_PATH, INGESTION_PATH):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from importers.csv_importer import CSVImporter  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path)
    parser.add_argument("--json-output", action="store_true")
    parser.add_argument(
        "--sampling-rate-tolerance",
        type=float,
        default=0.01,
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    importer = CSVImporter(
        sampling_rate_relative_tolerance=args.sampling_rate_tolerance
    )
    result = importer.import_session(args.manifest)
    payload = {
        "ok": result.ok,
        "blocking_codes": list(result.blocking_codes),
        "warning_codes": list(result.warning_codes),
        "issues": [issue.to_dict() for issue in result.issues],
        "normalized_signal": result.signal.to_summary() if result.signal else None,
    }

    if args.summary_out is not None:
        args.summary_out.parent.mkdir(parents=True, exist_ok=True)
        args.summary_out.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    if args.json_output:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        status = "PASS" if result.ok else "FAIL"
        print(f"{status}: Generic CSV ingestion")
        print(f"blocking_codes={list(result.blocking_codes)}")
        print(f"warning_codes={list(result.warning_codes)}")
        if result.signal:
            summary = result.signal.to_summary()
            print(
                f"session={summary['session_id']} samples={summary['sample_count']} "
                f"channels={summary['channel_count']} Fs={summary['sampling_rate_hz']}Hz "
                f"hash={summary['source_hash_sha256']}"
            )
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
