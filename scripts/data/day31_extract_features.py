#!/usr/bin/env python3
"""Extract Day 31 features from a sealed Day 30 window index."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from hashlib import sha256
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "semg-core"))
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day31.io import (
    CanonicalWindowReader,
    SourceIntegrityError,
    dump_json_strict,
    write_feature_rows_csv_gzip,
)
from day31.pipeline import PartitionAccessError, extract_window_index


def _load_window_rows(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".json":
        value = json.loads(path.read_text(encoding="utf-8"))
        rows = value.get("rows") if isinstance(value, dict) else None
        if not isinstance(rows, list) or not all(
            isinstance(row, dict) for row in rows
        ):
            raise ValueError("JSON window index must contain an object rows array")
        validation = value.get("validation")
        if isinstance(validation, dict) and validation.get("pass") is not True:
            raise ValueError("upstream window index validation did not pass")
        return rows
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV window index has no header")
        rows = [dict(row) for row in reader]
    integer_fields = {
        "start_sample",
        "end_sample_exclusive",
        "record_n_samples",
        "window_ms",
        "hop_ms",
    }
    for row in rows:
        for field in integer_fields:
            row[field] = int(row[field])
        row["sampling_rate_hz"] = float(row["sampling_rate_hz"])
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--window-index", required=True)
    parser.add_argument("--dataset-view", required=True)
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--channel-map")
    parser.add_argument("--output", required=True)
    parser.add_argument("--evidence-output", required=True)
    arguments = parser.parse_args()
    try:
        window_index_path = Path(arguments.window_index)
        window_rows = _load_window_rows(window_index_path)
        channel_map: dict[str, list[str]] = {}
        if arguments.channel_map:
            raw_map = json.loads(
                Path(arguments.channel_map).read_text(encoding="utf-8")
            )
            if not isinstance(raw_map, dict):
                raise ValueError("channel map root must be an object")
            channel_map = raw_map
        reader = CanonicalWindowReader(
            arguments.data_root,
            channel_map=channel_map,
        )
        batch = extract_window_index(
            window_rows,
            dataset_view_id=arguments.dataset_view,
            source_reader=reader,
        )
        write_result = write_feature_rows_csv_gzip(
            batch.feature_rows,
            arguments.output,
        )
        evidence = {
            "schema_version": "day31-zone2-extraction.v1",
            "pass": True,
            "dataset_view_id": arguments.dataset_view,
            "input_window_index_sha256": sha256(
                window_index_path.read_bytes()
            ).hexdigest(),
            "windows_processed": batch.windows_processed,
            "channels_processed": batch.channels_processed,
            "signal_samples_read": batch.signal_samples_read,
            "feature_rows": len(batch.feature_rows),
            "verified_source_count": reader.verified_source_count,
            "output_format": write_result["format"],
            "output_sha256": write_result["sha256"],
            "test_signal_rows_read": batch.test_signal_rows_read,
            "training_executed": batch.training_executed,
            "model_fitting_executed": batch.model_fitting_executed,
            "pooled_training_executed": batch.pooled_training_executed,
        }
        dump_json_strict(arguments.evidence_output, evidence)
        print(json.dumps(evidence, ensure_ascii=False, indent=2))
        return 0
    except (
        OSError,
        TypeError,
        ValueError,
        PermissionError,
        PartitionAccessError,
        SourceIntegrityError,
    ) as error:
        print(f"day31 extraction failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
