from __future__ import annotations

import csv
import gzip
import json
import sys
from hashlib import sha256
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "semg-core"))
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day31.io import (
    CanonicalWindowReader,
    SourceIntegrityError,
    dump_json_strict,
    write_feature_rows_csv_gzip,
)
from semg_core.day31_features import extract_feature_set_14
from semg_core.day31_features.long_format import to_long_rows


def _sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _row(path: Path, source_hash: str) -> dict[str, object]:
    return {
        "window_id": "a" * 24,
        "dataset_id": "mendeley-4channel-hand-gesture-v2",
        "record_id": "record-1",
        "subject_id": "subject-1",
        "day_id": "day-1",
        "session_id": "session-1",
        "repetition_id": "rep-1",
        "canonical_label": "rest",
        "partition": "train",
        "signal_path": str(path),
        "source_file_sha256": source_hash,
        "split_version": "split-v1",
        "label_mapping_version": "labels-v1",
        "start_sample": 10,
        "end_sample_exclusive": 30,
        "record_n_samples": 40,
        "sampling_rate_hz": 2_000.0,
        "window_ms": 10,
        "hop_ms": 5,
        "channel_policy_id": "mendeley-ch123-primary-v1",
        "preprocessing_policy_id": "fixture-v1",
    }


def test_csv_reader_slices_window_and_verifies_hash(tmp_path: Path) -> None:
    source = tmp_path / "signal.csv"
    with source.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["sample", "EMG_Raw_CH1", "EMG_RAW_CH2", "EMG_RAW_CH3", "EMG_RAW_CH4"]
        )
        for index in range(40):
            writer.writerow([index, index, index + 1, index + 2, index + 3])

    reader = CanonicalWindowReader(tmp_path)
    signal, channel_ids = reader(_row(source, _sha(source)))

    assert signal.shape == (20, 4)
    assert signal[0].tolist() == [10.0, 11.0, 12.0, 13.0]
    assert channel_ids == (
        "EMG_Raw_CH1",
        "EMG_RAW_CH2",
        "EMG_RAW_CH3",
        "EMG_RAW_CH4",
    )
    assert reader.verified_source_count == 1


def test_npy_reader_requires_explicit_channel_map(tmp_path: Path) -> None:
    source = tmp_path / "signal.npy"
    np.save(source, np.arange(160.0).reshape(40, 4))
    row = _row(source, _sha(source))

    with pytest.raises(ValueError, match="channel identifiers"):
        CanonicalWindowReader(tmp_path)(row)

    reader = CanonicalWindowReader(
        tmp_path,
        channel_map={
            "record-1": [
                "EMG_Raw_CH1",
                "EMG_RAW_CH2",
                "EMG_RAW_CH3",
                "EMG_RAW_CH4",
            ]
        },
    )
    signal, channel_ids = reader(row)
    assert signal.shape == (20, 4)
    assert len(channel_ids) == 4


def test_reader_rejects_path_escape_and_hash_mismatch(tmp_path: Path) -> None:
    inside = tmp_path / "inside"
    inside.mkdir()
    outside = tmp_path / "outside.npy"
    np.save(outside, np.ones((40, 4)))
    outside_row = _row(outside, _sha(outside))

    with pytest.raises(PermissionError, match="outside data root"):
        CanonicalWindowReader(inside)(outside_row)

    inside_source = inside / "signal.npy"
    np.save(inside_source, np.ones((40, 4)))
    mismatch = _row(inside_source, "0" * 64)
    with pytest.raises(SourceIntegrityError, match="SHA-256"):
        CanonicalWindowReader(
            inside,
            channel_map={"record-1": ["a", "b", "c", "d"]},
        )(mismatch)


def test_csv_gzip_writer_round_trips_qc_flags(tmp_path: Path) -> None:
    metadata = {
        "dataset_id": "synthetic",
        "dataset_view_id": "mendeley_core4_primary_v1",
        "split_name": "train",
        "subject_id": "subject-1",
        "day_id": "day-1",
        "session_id": "session-1",
        "repetition_id": "rep-1",
        "record_id": "record-1",
        "window_id": "a" * 24,
        "channel_id": "EMG_Raw_CH1",
        "canonical_label": "rest",
        "sampling_rate_hz": 2_000.0,
        "window_ms": 200,
        "hop_ms": 100,
        "preprocessing_policy_id": "fixture-v1",
        "channel_policy_id": "mendeley-ch123-primary-v1",
        "source_file_sha256": "a" * 64,
        "split_version": "split-v1",
        "label_mapping_version": "labels-v1",
    }
    rows = to_long_rows(
        metadata,
        extract_feature_set_14(np.zeros(400), 2_000.0),
    )
    output = tmp_path / "features.csv.gz"
    result = write_feature_rows_csv_gzip(rows, output)

    assert result["row_count"] == 14
    assert result["sha256"] == _sha(output)
    with gzip.open(output, "rt", encoding="utf-8", newline="") as handle:
        restored = list(csv.DictReader(handle))
    assert len(restored) == 14
    assert json.loads(restored[0]["qc_flags"]) == rows[0]["qc_flags"]
    mdf = next(row for row in restored if row["feature_id"] == "mdf_hz")
    assert mdf["feature_value"] == ""


def test_strict_json_dump_rejects_non_standard_nan(tmp_path: Path) -> None:
    output = tmp_path / "evidence.json"
    with pytest.raises(ValueError):
        dump_json_strict(output, {"value": float("nan")})
    dump_json_strict(output, {"value": None, "pass": True})
    assert json.loads(output.read_text(encoding="utf-8"))["value"] is None

