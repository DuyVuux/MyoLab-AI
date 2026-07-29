from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "semg-core"))
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day31.pipeline import (  # noqa: E402
    PartitionAccessError,
    extract_window_index,
)
from semg_core.day31_features.long_format import (  # noqa: E402
    REQUIRED_METADATA,
    to_long_rows,
)
from semg_core.day31_features import extract_feature_set_14  # noqa: E402


def _row(
    *,
    partition: str = "train",
    signal_path: str = "/zone2/train/record-1.npy",
    dataset_id: str = "mendeley-4channel-hand-gesture-v2",
    channel_policy_id: str = "mendeley-ch123-primary-v1",
) -> dict[str, object]:
    return {
        "window_id": "a" * 24,
        "dataset_id": dataset_id,
        "record_id": "record-1",
        "subject_id": "subject-1",
        "day_id": "day-1",
        "session_id": "session-1",
        "repetition_id": "rep-1",
        "canonical_label": "rest",
        "partition": partition,
        "signal_path": signal_path,
        "source_file_sha256": "a" * 64,
        "split_version": "split-v1",
        "label_mapping_version": "labels-v1",
        "start_sample": 0,
        "end_sample_exclusive": 400,
        "record_n_samples": 400,
        "sampling_rate_hz": 2_000.0,
        "window_ms": 200,
        "hop_ms": 100,
        "channel_policy_id": channel_policy_id,
        "preprocessing_policy_id": "per-record-channel-mean-v1",
    }


def _metadata() -> dict[str, object]:
    row = _row()
    return {
        "dataset_id": row["dataset_id"],
        "dataset_view_id": "mendeley_core4_primary_v1",
        "split_name": row["partition"],
        "subject_id": row["subject_id"],
        "day_id": row["day_id"],
        "session_id": row["session_id"],
        "repetition_id": row["repetition_id"],
        "record_id": row["record_id"],
        "window_id": row["window_id"],
        "channel_id": "EMG_Raw_CH1",
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


def test_long_rows_have_exact_contract_and_json_safe_nulls() -> None:
    result = extract_feature_set_14(np.zeros(400), 2_000.0)
    rows = to_long_rows(_metadata(), result)

    assert len(rows) == 14
    assert tuple(rows[0]) == REQUIRED_METADATA + (
        "feature_id",
        "feature_value",
        "feature_version",
        "qc_flags",
    )
    assert rows[0]["qc_flags"] == sorted(result.qc_flags)
    assert next(row for row in rows if row["feature_id"] == "mdf_hz")[
        "feature_value"
    ] is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("source_file_sha256", "not-a-sha"),
        ("sampling_rate_hz", float("nan")),
        ("window_ms", 0),
        ("hop_ms", 0),
        ("split_name", "TRAIN"),
        ("dataset_view_id", ""),
    ],
)
def test_long_row_metadata_is_strictly_validated(
    field: str, value: object
) -> None:
    metadata = _metadata()
    metadata[field] = value
    with pytest.raises((ValueError, PermissionError)):
        to_long_rows(
            metadata,
            extract_feature_set_14(np.arange(400.0), 2_000.0),
        )


@pytest.mark.parametrize(
    ("partition", "path"),
    [
        ("test", "/zone2/test/a.npy"),
        ("sealed_test", "/zone2/data/a.npy"),
        ("outer_test", "/zone2/data/a.npy"),
        ("unknown", "/zone2/data/a.npy"),
        ("validation", "/zone2/sealed-test/a.npy"),
        ("validation", "/zone2/outer_test/a.npy"),
        ("TRAIN", "/zone2/train/a.npy"),
    ],
)
def test_partition_attacks_are_blocked_before_reader_io(
    partition: str, path: str
) -> None:
    calls = 0

    def reader(_: dict[str, object]) -> tuple[np.ndarray, tuple[str, ...]]:
        nonlocal calls
        calls += 1
        return np.ones((400, 3)), (
            "EMG_Raw_CH1",
            "EMG_RAW_CH2",
            "EMG_RAW_CH3",
        )

    with pytest.raises(PartitionAccessError):
        extract_window_index(
            [_row(partition=partition, signal_path=path)],
            dataset_view_id="mendeley_core4_primary_v1",
            source_reader=reader,
        )
    assert calls == 0


def test_batch_preflight_prevents_partial_reads() -> None:
    calls = 0

    def reader(_: dict[str, object]) -> tuple[np.ndarray, tuple[str, ...]]:
        nonlocal calls
        calls += 1
        return np.ones((400, 3)), (
            "EMG_Raw_CH1",
            "EMG_RAW_CH2",
            "EMG_RAW_CH3",
        )

    with pytest.raises(PartitionAccessError):
        extract_window_index(
            [
                _row(),
                _row(
                    partition="validation",
                    signal_path="/zone2/sealed-test/attack.npy",
                ),
            ],
            dataset_view_id="mendeley_core4_primary_v1",
            source_reader=reader,
        )
    assert calls == 0


def test_mendeley_primary_extracts_exact_channel_layout() -> None:
    def reader(_: dict[str, object]) -> tuple[np.ndarray, tuple[str, ...]]:
        time = np.arange(400) / 2_000.0
        signal = np.column_stack(
            [
                np.sin(2 * np.pi * 50 * time),
                np.sin(2 * np.pi * 75 * time),
                np.sin(2 * np.pi * 100 * time),
                np.zeros(400),
            ]
        )
        return signal, (
            "EMG_Raw_CH1",
            "EMG_RAW_CH2",
            "EMG_RAW_CH3",
            "EMG_RAW_CH4",
        )

    batch = extract_window_index(
        [_row()],
        dataset_view_id="mendeley_core4_primary_v1",
        source_reader=reader,
    )

    assert len(batch.feature_rows) == 42
    assert {row["channel_id"] for row in batch.feature_rows} == {
        "EMG_Raw_CH1",
        "EMG_RAW_CH2",
        "EMG_RAW_CH3",
    }
    assert batch.windows_processed == 1
    assert batch.channels_processed == 3
    assert batch.test_signal_rows_read == 0
    assert batch.training_executed is False


def test_channel_policy_mismatch_fails_closed() -> None:
    def reader(_: dict[str, object]) -> tuple[np.ndarray, tuple[str, ...]]:
        return np.ones((400, 2)), ("EMG_Raw_CH1", "EMG_RAW_CH2")

    with pytest.raises(ValueError, match="missing required channels"):
        extract_window_index(
            [_row()],
            dataset_view_id="mendeley_core4_primary_v1",
            source_reader=reader,
        )

