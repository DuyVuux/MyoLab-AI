from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RecordMeta:
    record_id: str
    subject_id: str
    day_id: str
    session_id: str
    repetition_id: str
    source_label: str
    canonical_label: str
    partition: str
    signal_path: Path
    sampling_rate_hz: float
    signal_unit: str
    channel_count: int
    channel_columns: tuple[str, ...] = ()
    source_file_sha256: str | None = None
    adapter_id: str | None = None
    adapter_version: str | None = None
    mapping_profile_version: str | None = None


REQUIRED_INDEX_COLUMNS = {
    "record_id",
    "subject_id",
    "day_id",
    "session_id",
    "repetition_id",
    "source_label",
    "canonical_label",
    "partition",
    "signal_path",
    "sampling_rate_hz",
    "signal_unit",
    "channel_count",
}
