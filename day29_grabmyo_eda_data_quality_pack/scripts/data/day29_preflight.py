#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ai-core" / "data"))

from day29.manifest_io import dump_json, load_metadata_index, load_yaml  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Day29 GRABMyo preflight")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    config = load_yaml(args.config)
    dataset_root = Path(config["dataset_root"])
    metadata_index = Path(config["metadata_index"])
    blockers: list[str] = []

    if config.get("training_allowed") is not False:
        blockers.append("TRAINING_MUST_REMAIN_DISABLED")
    if config.get("test_signal_access_allowed") is not False:
        blockers.append("TEST_SIGNAL_ACCESS_MUST_REMAIN_DISABLED")

    for name in config.get("required_governance_files", []):
        if not (dataset_root / name).exists():
            blockers.append(f"MISSING_GOVERNANCE_FILE:{name}")

    record_count = 0
    partitions: list[str] = []
    if not metadata_index.exists():
        blockers.append("METADATA_INDEX_MISSING")
    else:
        try:
            records = load_metadata_index(metadata_index)
            record_count = len(records)
            partitions = sorted({row.partition for row in records})
            forbidden = sorted(set(partitions) & set(config.get("forbidden_partitions", [])))
            if forbidden:
                blockers.append(f"METADATA_INDEX_CONTAINS_FORBIDDEN_PARTITIONS:{forbidden}")
        except Exception as exc:  # preflight must surface, not hide
            blockers.append(f"METADATA_INDEX_INVALID:{exc}")

    result = {
        "schema_version": "day29-preflight.v1",
        "dataset_id": config.get("dataset_id"),
        "mode": "READY_FOR_REAL_EDA" if not blockers else "TOOLING_ONLY_BLOCKED",
        "training_allowed": False,
        "test_signal_access_allowed": False,
        "metadata_record_count": record_count,
        "observed_partitions": partitions,
        "blockers": blockers,
    }
    dump_json(args.output, result)
    print(result["mode"])
    return 0 if not blockers else 2


if __name__ == "__main__":
    raise SystemExit(main())
