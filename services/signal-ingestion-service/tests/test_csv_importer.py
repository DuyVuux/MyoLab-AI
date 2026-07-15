from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import numpy as np

from importers.csv_importer import CSVImporter


ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = ROOT / "data-platform" / "synthetic-data"
MANIFEST = FIXTURE_DIR / "golden_signal_01.manifest.json"
EXPECTED = FIXTURE_DIR / "golden_signal_01.expected_ingestion_summary.json"


def test_full_protocol_fixture_imports_to_canonical_object() -> None:
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    result = CSVImporter().import_session(MANIFEST)
    assert result.ok, [issue.to_dict() for issue in result.issues]
    signal = result.require_signal()

    assert signal.schema_version == expected["schema_version"]
    assert signal.session_id == expected["session_id"]
    assert signal.sampling_rate_hz == expected["sampling_rate_hz"]
    assert signal.sample_count == expected["sample_count"]
    assert signal.channel_count == expected["channel_count"]
    assert signal.source_hash_sha256 == expected["source_hash_sha256"]

    active = signal.phase_slice("active_contraction")
    assert active.stop - active.start == expected["active_phase_sample_count"]

    channel = signal.channels["VL_R_01"]
    assert channel.canonical_unit == expected["canonical_unit"]
    assert channel.samples_uV.shape == signal.time_s.shape
    assert not channel.samples_uV.flags.writeable
    assert not signal.time_s.flags.writeable
    assert np.isfinite(channel.samples_uV).all()


def test_json_summary_omits_raw_arrays() -> None:
    signal = CSVImporter().import_session(MANIFEST).require_signal()
    summary = signal.to_summary()
    serialized = json.dumps(summary)
    assert "samples_uV" not in serialized
    assert "time_s" not in serialized
    assert summary["sample_count"] == 70_000


def test_declared_hash_mismatch_blocks_import(tmp_path: Path) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["signal_file"] = str((FIXTURE_DIR / "golden_signal_01.csv").resolve())
    manifest["source_hash_sha256"] = "0" * 64
    modified = tmp_path / "bad-hash.manifest.json"
    modified.write_text(json.dumps(manifest), encoding="utf-8")

    result = CSVImporter().import_session(modified)
    assert not result.ok
    assert "SOURCE_HASH_MISMATCH" in result.blocking_codes


def test_mv_source_is_converted_to_uv(tmp_path: Path) -> None:
    csv_path = tmp_path / "small.csv"
    csv_path.write_text(
        "time_s,CH1\n0.000,0.001\n0.001,-0.002\n0.002,0.003\n",
        encoding="utf-8",
    )
    source_hash = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    manifest = {
        "schema_version": "semg-session-manifest.v0.1",
        "session_id": "UNIT_CONVERSION",
        "data_source": "synthetic",
        "signal_file": csv_path.name,
        "source_hash_sha256": source_hash,
        "sampling_rate_hz": 1000,
        "time_column": "time_s",
        "protocol": {"id": "test", "version": "0.0.1"},
        "channels": [
            {
                "column": "CH1",
                "channel_id": "CH1",
                "muscle": "test_muscle",
                "side": "right",
                "unit": "mV",
                "role": "bipolar_semg",
            }
        ],
        "phase_markers": [
            {"phase_id": "active", "start_s": 0.0, "end_s": 0.003}
        ],
        "processing_history": {"raw_export": True},
    }
    manifest_path = tmp_path / "small.manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = CSVImporter().import_session(manifest_path)
    assert result.ok, [issue.to_dict() for issue in result.issues]
    samples = result.require_signal().channels["CH1"].samples_uV
    np.testing.assert_allclose(samples, np.array([1.0, -2.0, 3.0]))


def test_non_monotonic_time_blocks_import(tmp_path: Path) -> None:
    csv_path = tmp_path / "bad-time.csv"
    csv_path.write_text(
        "time_s,CH1\n0.000,1\n0.002,2\n0.001,3\n",
        encoding="utf-8",
    )
    source_hash = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["session_id"] = "BAD_TIME"
    manifest["signal_file"] = csv_path.name
    manifest["source_hash_sha256"] = source_hash
    manifest["channels"] = [
        {
            "column": "CH1",
            "channel_id": "CH1",
            "muscle": "test_muscle",
            "side": "right",
            "unit": "uV",
            "role": "bipolar_semg",
        }
    ]
    manifest["phase_markers"] = [
        {"phase_id": "active", "start_s": 0.0, "end_s": 0.003}
    ]
    path = tmp_path / "bad-time.manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")

    result = CSVImporter().import_session(path)
    assert not result.ok
    assert "TIME_NOT_MONOTONIC" in result.blocking_codes
