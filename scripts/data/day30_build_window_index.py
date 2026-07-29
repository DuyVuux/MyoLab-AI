#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day30.storage_contract import validate_window_rows
from day30.windowing import build_window_rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata-index", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--window-ms", type=int, default=200)
    parser.add_argument("--hop-ms", type=int, default=100)
    parser.add_argument("--channel-policy-id", default="fixture-policy")
    parser.add_argument("--preprocessing-policy-id", default="dc-mean-v1")
    args = parser.parse_args()
    try:
        rows: list[dict] = []
        with Path(args.metadata_index).open(
            newline="", encoding="utf-8"
        ) as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise ValueError("metadata index has no header")
            for record in reader:
                rows.extend(
                    build_window_rows(
                        record,
                        args.window_ms,
                        args.hop_ms,
                        args.channel_policy_id,
                        args.preprocessing_policy_id,
                    )
                )
        validation = validate_window_rows(rows)
        if not validation["pass"]:
            raise ValueError("; ".join(validation["errors"]))
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.suffix.lower() == ".json":
            output.write_text(
                json.dumps(
                    {"validation": validation, "rows": rows},
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
        else:
            fieldnames = list(rows[0]) if rows else []
            with output.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                if fieldnames:
                    writer.writeheader()
                    writer.writerows(rows)
        print(json.dumps(validation, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, TypeError, KeyError, PermissionError) as error:
        print(f"day30 window index failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
