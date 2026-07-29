from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import yaml

from .contracts import REQUIRED_INDEX_COLUMNS, RecordMeta


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"YAML root phải là object: {path}")
    return value


def dump_yaml(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(value, handle, allow_unicode=True, sort_keys=False)


def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_metadata_index(path: Path) -> list[RecordMeta]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = set(reader.fieldnames or [])
        missing = sorted(REQUIRED_INDEX_COLUMNS - headers)
        if missing:
            raise ValueError(f"Metadata index thiếu cột: {missing}")

        records: list[RecordMeta] = []
        for row_number, row in enumerate(reader, start=2):
            try:
                channel_columns = tuple(
                    item.strip()
                    for item in (row.get("channel_columns") or "").split(";")
                    if item.strip()
                )
                records.append(
                    RecordMeta(
                        record_id=row["record_id"].strip(),
                        subject_id=row["subject_id"].strip(),
                        day_id=row["day_id"].strip(),
                        session_id=row["session_id"].strip(),
                        repetition_id=row["repetition_id"].strip(),
                        source_label=row["source_label"].strip(),
                        canonical_label=row["canonical_label"].strip(),
                        partition=row["partition"].strip().lower(),
                        signal_path=Path(row["signal_path"].strip()),
                        sampling_rate_hz=float(row["sampling_rate_hz"]),
                        signal_unit=row["signal_unit"].strip(),
                        channel_count=int(row["channel_count"]),
                        channel_columns=channel_columns,
                        source_file_sha256=(row.get("source_file_sha256") or "").strip() or None,
                        adapter_id=(row.get("adapter_id") or "").strip() or None,
                        adapter_version=(row.get("adapter_version") or "").strip() or None,
                        mapping_profile_version=(row.get("mapping_profile_version") or "").strip() or None,
                    )
                )
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"Metadata index lỗi tại dòng {row_number}: {exc}") from exc
    return records
