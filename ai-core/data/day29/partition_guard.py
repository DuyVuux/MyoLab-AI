from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .contracts import RecordMeta

ALLOWED_EDA_PARTITIONS = {"train", "validation"}
FORBIDDEN_PATH_TOKENS = {"test", "sealed-test", "sealed_test", "outer-test", "outer_test"}


def assert_record_visible(record: RecordMeta) -> None:
    if record.partition not in ALLOWED_EDA_PARTITIONS:
        raise PermissionError(
            f"Day29 EDA không được đọc partition={record.partition!r} "
            f"cho record={record.record_id}"
        )
    path_tokens = {part.lower() for part in record.signal_path.parts}
    forbidden = sorted(path_tokens & FORBIDDEN_PATH_TOKENS)
    if forbidden:
        raise PermissionError(
            f"Signal path chứa token sealed-test {forbidden}: {record.signal_path}"
        )


def filter_visible_records(records: Iterable[RecordMeta]) -> list[RecordMeta]:
    visible: list[RecordMeta] = []
    for record in records:
        assert_record_visible(record)
        visible.append(record)
    return visible
