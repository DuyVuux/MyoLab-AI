#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
import tempfile
from pathlib import Path

import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ai-core" / "data"))

from day29.cross_day_drift import build_drift_summary  # noqa: E402
from day29.descriptive_stats import channel_statistics  # noqa: E402
from day29.hierarchy_audit import audit_hierarchy  # noqa: E402
from day29.manifest_io import load_metadata_index  # noqa: E402
from day29.partition_guard import filter_visible_records  # noqa: E402
from day29.signal_loader import load_signal  # noqa: E402


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="day29-contract-fixture-") as temp:
        root = Path(temp)
        index_path = root / "metadata-index.csv"
        headers = [
            "record_id", "subject_id", "day_id", "session_id", "repetition_id",
            "source_label", "canonical_label", "partition", "signal_path",
            "sampling_rate_hz", "signal_unit", "channel_count", "channel_columns",
        ]
        rows = []
        rng = np.random.default_rng(2901)
        for day_index, day in enumerate(["D1", "D2"], start=1):
            for repetition in ["R1", "R2"]:
                path = root / f"S01_{day}_{repetition}.csv"
                signal = rng.normal(0.0, 1.0 + 0.1 * day_index, size=(256, 2))
                with path.open("w", encoding="utf-8", newline="") as handle:
                    writer = csv.writer(handle)
                    writer.writerow(["ch01", "ch02"])
                    writer.writerows(signal.tolist())
                rows.append({
                    "record_id": f"S01-{day}-{repetition}",
                    "subject_id": "S01",
                    "day_id": day,
                    "session_id": day,
                    "repetition_id": repetition,
                    "source_label": "gesture_a",
                    "canonical_label": "hand_close",
                    "partition": "train" if repetition == "R1" else "validation",
                    "signal_path": str(path),
                    "sampling_rate_hz": "2048",
                    "signal_unit": "uV",
                    "channel_count": "2",
                    "channel_columns": "ch01;ch02",
                })
        with index_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

        records = filter_visible_records(load_metadata_index(index_path))
        hierarchy = audit_hierarchy(records)
        features = []
        for record in records:
            signal, names = load_signal(record)
            for index, name in enumerate(names):
                features.append({
                    "subject_id": record.subject_id,
                    "day_id": record.day_id,
                    "canonical_label": record.canonical_label,
                    "channel_id": name,
                    **channel_statistics(signal[:, index]),
                })
        drift = build_drift_summary(features, "rms", minimum_records_per_day=2)
        result = {
            "schema_version": "day29-tooling-validation.v1",
            "pack_valid": hierarchy["status"] in {"VERIFIED", "PARTIAL"},
            "synthetic_contract_fixture_only": True,
            "fixture_is_not_grabmyo": True,
            "record_count": len(records),
            "drift_rows": len(drift),
            "training_execution_allowed": False,
            "test_signal_rows_read": 0,
        }
        output = REPO_ROOT / "qa-validation/evidence/day29-tooling-validation.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["pack_valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
