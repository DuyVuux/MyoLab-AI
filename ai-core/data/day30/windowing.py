from __future__ import annotations

import re
from hashlib import sha256
from math import isfinite

from .contracts import ALLOWED_PARTITIONS, PROJECT_CLASS_ORDER
from .sample_rate import samples_for_ms

REQUIRED_RECORD_FIELDS = frozenset(
    {
        "dataset_id",
        "record_id",
        "subject_id",
        "canonical_label",
        "partition",
        "signal_path",
        "source_file_sha256",
        "split_version",
        "label_mapping_version",
        "sampling_rate_hz",
        "n_samples",
    }
)
SHA256_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")
FORBIDDEN_PATH_COMPONENTS = frozenset(
    {"test", "sealed-test", "sealed_test", "outer-test", "outer_test"}
)


def window_slices(
    n_samples: int,
    sampling_rate_hz: float,
    window_ms: int,
    hop_ms: int,
) -> list[tuple[int, int]]:
    if isinstance(n_samples, bool) or not isinstance(n_samples, int) or n_samples < 0:
        raise ValueError("n_samples must be a non-negative integer")
    window = samples_for_ms(sampling_rate_hz, window_ms)
    hop = samples_for_ms(sampling_rate_hz, hop_ms)
    if n_samples < window:
        return []
    return [
        (start, start + window)
        for start in range(0, n_samples - window + 1, hop)
    ]


def _assert_record_visible(record: dict) -> str:
    missing = sorted(REQUIRED_RECORD_FIELDS - set(record))
    if missing:
        raise ValueError(f"Missing record fields: {missing}")
    partition = str(record["partition"]).strip().lower()
    if partition not in ALLOWED_PARTITIONS:
        raise PermissionError(f"Partition not visible to Day 30: {partition}")
    path_components = {
        component.lower()
        for component in re.split(r"[\\/]+", str(record["signal_path"]))
        if component
    }
    if path_components & FORBIDDEN_PATH_COMPONENTS:
        raise PermissionError("Signal path contains a forbidden test partition")
    return partition


def _validate_record(record: dict) -> None:
    n_samples = record["n_samples"]
    if isinstance(n_samples, bool) or not isinstance(n_samples, (int, str)):
        raise ValueError("n_samples must be a non-negative integer")
    try:
        parsed_n_samples = int(n_samples)
    except (TypeError, ValueError) as error:
        raise ValueError("n_samples must be a non-negative integer") from error
    if parsed_n_samples < 0 or str(parsed_n_samples) != str(n_samples).strip():
        raise ValueError("n_samples must be a non-negative integer")
    sampling_rate = float(record["sampling_rate_hz"])
    if not isfinite(sampling_rate) or sampling_rate <= 0:
        raise ValueError("sampling_rate_hz must be finite and positive")
    canonical_label = str(record["canonical_label"]).strip().lower()
    if canonical_label not in PROJECT_CLASS_ORDER:
        raise ValueError("canonical_label must be an eligible supervised label")
    if not SHA256_PATTERN.fullmatch(str(record["source_file_sha256"])):
        raise ValueError("source_file_sha256 must be a 64-character sha256")
    for field in (
        "dataset_id",
        "record_id",
        "subject_id",
        "split_version",
        "label_mapping_version",
    ):
        if not str(record[field]).strip():
            raise ValueError(f"{field} must be non-empty")


def build_window_rows(
    record: dict,
    window_ms: int,
    hop_ms: int,
    channel_policy_id: str,
    preprocessing_policy_id: str,
) -> list[dict]:
    if not isinstance(record, dict):
        raise TypeError("record must be a mapping")
    partition = _assert_record_visible(record)
    _validate_record(record)
    if not channel_policy_id or not preprocessing_policy_id:
        raise ValueError("policy identifiers must be non-empty")

    n_samples = int(record["n_samples"])
    slices = window_slices(
        n_samples,
        float(record["sampling_rate_hz"]),
        window_ms,
        hop_ms,
    )
    rows: list[dict] = []
    for start, end in slices:
        token = "|".join(
            [
                str(record["dataset_id"]),
                str(record["record_id"]),
                str(record["source_file_sha256"]).lower(),
                str(record["split_version"]),
                str(start),
                str(end),
                str(window_ms),
                str(hop_ms),
                channel_policy_id,
                preprocessing_policy_id,
            ]
        )
        rows.append(
            {
                "window_id": sha256(token.encode("utf-8")).hexdigest()[:24],
                "dataset_id": str(record["dataset_id"]),
                "record_id": str(record["record_id"]),
                "subject_id": str(record["subject_id"]),
                "day_id": str(record.get("day_id", "")),
                "session_id": str(record.get("session_id", "")),
                "repetition_id": str(record.get("repetition_id", "")),
                "canonical_label": str(record["canonical_label"]).strip().lower(),
                "partition": partition,
                "signal_path": str(record["signal_path"]),
                "source_file_sha256": str(record["source_file_sha256"]).lower(),
                "split_version": str(record["split_version"]),
                "label_mapping_version": str(record["label_mapping_version"]),
                "start_sample": start,
                "end_sample_exclusive": end,
                "record_n_samples": n_samples,
                "sampling_rate_hz": float(record["sampling_rate_hz"]),
                "window_ms": int(window_ms),
                "hop_ms": int(hop_ms),
                "channel_policy_id": channel_policy_id,
                "preprocessing_policy_id": preprocessing_policy_id,
            }
        )
    return rows

