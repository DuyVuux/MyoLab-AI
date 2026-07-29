from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day30.storage_contract import validate_window_rows
from day30.windowing import build_window_rows, window_slices


def record(**overrides) -> dict:
    base = {
        "dataset_id": "mendeley-4channel-hand-gesture-v2",
        "record_id": "record-1",
        "subject_id": "subject-1",
        "day_id": "day-1",
        "session_id": "session-1",
        "repetition_id": "rep-1",
        "canonical_label": "rest",
        "partition": "train",
        "signal_path": "/zone2/train/record-1.mat",
        "source_file_sha256": "a" * 64,
        "split_version": "split-v1",
        "label_mapping_version": "mapping-v1",
        "sampling_rate_hz": 2000,
        "n_samples": 1000,
    }
    return base | overrides


def test_windows_are_bounded_deterministic_and_provenanced() -> None:
    first = build_window_rows(record(), 200, 100, "channels-v1", "dc-v1")
    second = build_window_rows(record(), 200, 100, "channels-v1", "dc-v1")
    assert first == second
    assert first[0]["start_sample"] == 0
    assert first[-1]["end_sample_exclusive"] <= 1000
    assert all(row["source_file_sha256"] == "a" * 64 for row in first)
    assert all(row["split_version"] == "split-v1" for row in first)
    assert all(row["label_mapping_version"] == "mapping-v1" for row in first)
    assert validate_window_rows(first)["pass"] is True


@pytest.mark.parametrize(
    ("partition", "signal_path"),
    [
        ("test", "/zone2/test/record.mat"),
        ("sealed_test", "/zone2/data/record.mat"),
        ("validation", "/zone2/sealed-test/record.mat"),
        ("validation", "/zone2/outer_test/record.mat"),
        ("unknown", "/zone2/data/record.mat"),
    ],
)
def test_partition_and_path_guards_fail_closed(
    partition: str, signal_path: str
) -> None:
    with pytest.raises(PermissionError):
        build_window_rows(
            record(partition=partition, signal_path=signal_path),
            200,
            100,
            "channels-v1",
            "dc-v1",
        )


def test_invalid_metadata_is_rejected_before_windowing() -> None:
    with pytest.raises(ValueError, match="n_samples"):
        build_window_rows(record(n_samples=-1), 200, 100, "c", "p")
    with pytest.raises(ValueError, match="canonical_label"):
        build_window_rows(record(canonical_label="unknown"), 200, 100, "c", "p")
    with pytest.raises(ValueError, match="sha256"):
        build_window_rows(record(source_file_sha256="not-a-hash"), 200, 100, "c", "p")


def test_storage_validation_detects_bounds_duplicates_and_subject_leakage() -> None:
    train = build_window_rows(record(), 200, 100, "c", "p")
    validation = build_window_rows(
        record(
            record_id="record-2",
            partition="validation",
            signal_path="/zone2/validation/record-2.mat",
        ),
        200,
        100,
        "c",
        "p",
    )
    result = validate_window_rows(train + validation)
    assert result["pass"] is False
    assert "subject_partition_overlap:subject-1" in result["errors"]

    duplicate = validate_window_rows(train + [dict(train[0])])
    assert duplicate["pass"] is False
    assert any("duplicate_window_id" in error for error in duplicate["errors"])

    out_of_bounds = [dict(train[0], end_sample_exclusive=1001)]
    invalid = validate_window_rows(out_of_bounds)
    assert any("exceeds_record" in error for error in invalid["errors"])


def test_window_slices_handle_short_and_exact_records() -> None:
    assert window_slices(399, 2000, 200, 100) == []
    assert window_slices(400, 2000, 200, 100) == [(0, 400)]
