"""Window-index integration with a mandatory partition guard before I/O."""

from __future__ import annotations

import math
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
from semg_core.day31_features import extract_feature_set_14
from semg_core.day31_features.long_format import to_long_rows

ALLOWED_PARTITIONS = frozenset({"train", "validation"})
FORBIDDEN_PATH_TOKENS = frozenset(
    {"test", "sealed-test", "sealed_test", "outer-test", "outer_test"}
)
_WINDOW_ID = re.compile(r"^[0-9a-f]{24}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class PartitionAccessError(PermissionError):
    """Raised before source I/O when a window is not visible to Day 31."""


@dataclass(frozen=True, slots=True)
class DatasetView:
    view_id: str
    dataset_ids: frozenset[str]
    channel_policy_id: str
    channel_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ExtractionBatch:
    feature_rows: tuple[dict[str, Any], ...]
    windows_processed: int
    channels_processed: int
    signal_samples_read: int
    test_signal_rows_read: int = 0
    training_executed: bool = False
    model_fitting_executed: bool = False
    pooled_training_executed: bool = False


VIEW_CONTRACTS = {
    "mendeley_core4_primary_v1": DatasetView(
        view_id="mendeley_core4_primary_v1",
        dataset_ids=frozenset({"mendeley-4channel-hand-gesture-v2"}),
        channel_policy_id="mendeley-ch123-primary-v1",
        channel_ids=("EMG_Raw_CH1", "EMG_RAW_CH2", "EMG_RAW_CH3"),
    ),
    "mendeley_core4_ch4_sensitivity_v1": DatasetView(
        view_id="mendeley_core4_ch4_sensitivity_v1",
        dataset_ids=frozenset({"mendeley-4channel-hand-gesture-v2"}),
        channel_policy_id="mendeley-ch1234-sensitivity-v1",
        channel_ids=(
            "EMG_Raw_CH1",
            "EMG_RAW_CH2",
            "EMG_RAW_CH3",
            "EMG_RAW_CH4",
        ),
    ),
    "grabmyo_project_subset_native28_v1": DatasetView(
        view_id="grabmyo_project_subset_native28_v1",
        dataset_ids=frozenset({"grabmyo-v1.1.0"}),
        channel_policy_id="grabmyo-fw28-primary-v1",
        channel_ids=tuple(
            [f"F{index}" for index in range(1, 17)]
            + [f"W{index}" for index in range(1, 13)]
        ),
    ),
}


def assert_window_visible(row: Mapping[str, Any]) -> None:
    """Enforce the exact partition allowlist and reject sealed path tokens."""

    partition = row.get("partition")
    if partition not in ALLOWED_PARTITIONS:
        raise PartitionAccessError(
            f"source_partition_forbidden: {partition!r}"
        )
    signal_path = row.get("signal_path")
    if not isinstance(signal_path, str) or not signal_path:
        raise ValueError("signal_path must be a non-empty string")
    path_tokens = {
        token.lower()
        for token in re.split(r"[\\/]+", signal_path)
        if token
    }
    forbidden = sorted(path_tokens & FORBIDDEN_PATH_TOKENS)
    if forbidden:
        raise PartitionAccessError(
            f"source_path_forbidden: {forbidden}"
        )


def _validate_window_row(row: Mapping[str, Any], view: DatasetView) -> None:
    assert_window_visible(row)
    if row.get("dataset_id") not in view.dataset_ids:
        raise ValueError("dataset_id is not registered for dataset view")
    if row.get("channel_policy_id") != view.channel_policy_id:
        raise ValueError("channel_policy_id mismatch")
    window_id = row.get("window_id")
    if not isinstance(window_id, str) or _WINDOW_ID.fullmatch(window_id) is None:
        raise ValueError("window_id must be a 24-character lowercase hex value")
    source_hash = row.get("source_file_sha256")
    if not isinstance(source_hash, str) or _SHA256.fullmatch(source_hash) is None:
        raise ValueError("source_file_sha256 must be lowercase SHA-256")
    for field in (
        "dataset_id",
        "record_id",
        "subject_id",
        "canonical_label",
        "split_version",
        "label_mapping_version",
        "preprocessing_policy_id",
    ):
        value = row.get(field)
        if not isinstance(value, str) or not value:
            raise ValueError(f"{field} must be a non-empty string")
    for field in ("start_sample", "end_sample_exclusive", "record_n_samples"):
        value = row.get(field)
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{field} must be an integer")
    start = int(row["start_sample"])
    end = int(row["end_sample_exclusive"])
    record_samples = int(row["record_n_samples"])
    if start < 0 or end <= start or end > record_samples:
        raise ValueError("window sample bounds are invalid")
    sampling_rate = row.get("sampling_rate_hz")
    if (
        isinstance(sampling_rate, bool)
        or not isinstance(sampling_rate, (int, float))
        or not math.isfinite(float(sampling_rate))
        or float(sampling_rate) <= 0.0
    ):
        raise ValueError("sampling_rate_hz must be positive and finite")
    for field in ("window_ms", "hop_ms"):
        value = row.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{field} must be a positive integer")


def _channel_indices(
    observed_channel_ids: Sequence[str],
    required_channel_ids: Sequence[str],
) -> tuple[int, ...]:
    normalized: dict[str, int] = {}
    for index, channel_id in enumerate(observed_channel_ids):
        key = channel_id.casefold()
        if key in normalized:
            raise ValueError("duplicate channel identifiers after case folding")
        normalized[key] = index
    missing = [
        channel_id
        for channel_id in required_channel_ids
        if channel_id.casefold() not in normalized
    ]
    if missing:
        raise ValueError(f"missing required channels: {missing}")
    return tuple(normalized[channel_id.casefold()] for channel_id in required_channel_ids)


def _long_metadata(
    row: Mapping[str, Any],
    view: DatasetView,
    channel_id: str,
) -> dict[str, Any]:
    return {
        "dataset_id": row["dataset_id"],
        "dataset_view_id": view.view_id,
        "split_name": row["partition"],
        "subject_id": row["subject_id"],
        "day_id": row.get("day_id"),
        "session_id": row.get("session_id"),
        "repetition_id": row.get("repetition_id"),
        "record_id": row["record_id"],
        "window_id": row["window_id"],
        "channel_id": channel_id,
        "canonical_label": row["canonical_label"],
        "sampling_rate_hz": row["sampling_rate_hz"],
        "window_ms": row["window_ms"],
        "hop_ms": row["hop_ms"],
        "preprocessing_policy_id": row["preprocessing_policy_id"],
        "channel_policy_id": row["channel_policy_id"],
        "source_file_sha256": row["source_file_sha256"],
        "split_version": row["split_version"],
        "label_mapping_version": row["label_mapping_version"],
    }


def extract_window_index(
    rows: Sequence[Mapping[str, Any]],
    *,
    dataset_view_id: str,
    source_reader: Callable[
        [Mapping[str, Any]],
        tuple[np.ndarray, tuple[str, ...]],
    ],
) -> ExtractionBatch:
    """Extract all visible windows after an all-or-nothing preflight phase."""

    if dataset_view_id not in VIEW_CONTRACTS:
        raise ValueError(f"unknown dataset view: {dataset_view_id}")
    if not rows:
        raise ValueError("window index must not be empty")
    view = VIEW_CONTRACTS[dataset_view_id]
    seen_window_ids: set[str] = set()
    for row in rows:
        _validate_window_row(row, view)
        window_id = str(row["window_id"])
        if window_id in seen_window_ids:
            raise ValueError(f"duplicate window_id: {window_id}")
        seen_window_ids.add(window_id)

    output: list[dict[str, Any]] = []
    channels_processed = 0
    signal_samples_read = 0
    for row in rows:
        signal, observed_channel_ids = source_reader(row)
        values = np.asarray(signal, dtype=np.float64)
        if values.ndim != 2:
            raise ValueError("source reader must return [samples, channels]")
        expected_samples = int(row["end_sample_exclusive"]) - int(
            row["start_sample"]
        )
        if values.shape[0] != expected_samples:
            raise ValueError(
                "source reader returned an unexpected number of samples"
            )
        if values.shape[1] != len(observed_channel_ids):
            raise ValueError("signal width does not match channel identifiers")
        indices = _channel_indices(observed_channel_ids, view.channel_ids)
        for channel_id, channel_index in zip(
            view.channel_ids,
            indices,
            strict=True,
        ):
            result = extract_feature_set_14(
                values[:, channel_index],
                float(row["sampling_rate_hz"]),
            )
            output.extend(
                to_long_rows(
                    _long_metadata(row, view, channel_id),
                    result,
                )
            )
        channels_processed += len(indices)
        signal_samples_read += int(values.shape[0] * len(indices))
    return ExtractionBatch(
        feature_rows=tuple(output),
        windows_processed=len(rows),
        channels_processed=channels_processed,
        signal_samples_read=signal_samples_read,
    )
