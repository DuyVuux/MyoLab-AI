from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core/evaluation"))

from day33.day32_adapters import adapt_grabmyo_oof_trials, adapt_mendeley_oof_windows
from day33.io import write_csv, write_json


def main():
    parser = argparse.ArgumentParser(description="Normalize baseline artifacts to the prediction contract.")
    parser.add_argument("--source-kind", choices=["mendeley-day32-oof", "grabmyo-day32-oof"], required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--ledger", required=True)
    args = parser.parse_args()

    if args.source_kind == "mendeley-day32-oof":
        rows = adapt_mendeley_oof_windows(args.source)
    else:
        rows = adapt_grabmyo_oof_trials(args.source)

    write_csv(args.output, rows)
    write_json(args.ledger, {
        "schema_version": "prediction-contract-input-ledger.v1",
        "source_kind": args.source_kind,
        "source": args.source,
        "output": args.output,
        "prediction_rows": len(rows),
        "dataset_ids": sorted({row["dataset_id"] for row in rows}),
        "run_ids": sorted({row["run_id"] for row in rows}),
        "sealed_test_rows_read": 0,
        "pooled_evaluation_executed": False,
    })


if __name__ == "__main__":
    main()
