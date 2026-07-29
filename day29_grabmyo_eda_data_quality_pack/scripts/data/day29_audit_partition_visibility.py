#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ai-core" / "data"))

from day29.manifest_io import load_metadata_index  # noqa: E402
from day29.partition_guard import assert_record_visible  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata-index", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    records = load_metadata_index(args.metadata_index)
    counts = Counter(row.partition for row in records)
    errors: list[str] = []
    visible = 0
    for record in records:
        try:
            assert_record_visible(record)
            visible += 1
        except PermissionError as exc:
            errors.append(str(exc))

    result = {
        "schema_version": "day29-partition-visibility.v1",
        "partition_counts_from_manifest": dict(sorted(counts.items())),
        "visible_record_count": visible,
        "test_signal_rows_read": 0,
        "errors": errors,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
