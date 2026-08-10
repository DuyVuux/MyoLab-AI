from __future__ import annotations

import json
from pathlib import Path

import pytest

from adapters.mr4 import parser as single
from adapters.mr4.models import Mr4ParseError, sha256_file
from adapters.mr4.contracts import MR4_SINGLE_CSV_V0_1

ROOT = Path(__file__).resolve().parents[5]
D09 = ROOT / "qa-validation/test-data/golden/noraxon/single_csv"
D15 = ROOT / "qa-validation/test-data/synthetic/day15-corruption"

def test_01_parser_identity_is_versioned():
    assert single.PARSER_ID == "noraxon-mr4-single-csv"
    assert single.PARSER_VERSION == "0.1.0"
    assert MR4_SINGLE_CSV_V0_1.contract_id == "MR4_SINGLE_CSV_V0_1"

def test_02_valid_day09_fixture_parses():
    record = single.parse_single_csv(D09 / "valid_minimal.csv")
    assert len(record.raw_rows) == 3
    assert record.data_header[0] == "time"

def test_03_source_id_is_content_hash_based():
    path = D09 / "valid_minimal.csv"
    record = single.parse_single_csv(path)
    assert record.source.source_id == f"src_sha256_{sha256_file(path)}"

def test_04_source_path_is_preserved():
    path = D09 / "valid_minimal.csv"
    record = single.parse_single_csv(path)
    assert Path(record.source.source_path) == path.resolve()

def test_05_deterministic_replay_is_identical():
    path = D09 / "valid_minimal.csv"
    first = single.parse_single_csv(path)
    second = single.parse_single_csv(path)
    assert first == second
    assert first.provenance.run_id == second.provenance.run_id

def test_06_raw_bytes_are_not_mutated():
    path = D09 / "valid_minimal.csv"
    before = sha256_file(path)
    single.parse_single_csv(path)
    assert sha256_file(path) == before

def test_07_metadata_values_are_preserved_as_source_text():
    record = single.parse_single_csv(D09 / "valid_minimal.csv")
    assert record.metadata_value("frequency") == "2000"
    assert record.metadata_value("record_name") == "SYNTHETIC_TREADMILL_EMG"

def test_08_unknown_metadata_is_preserved():
    record = single.parse_single_csv(D09 / "valid_unknown_fields.csv")
    assert [(x.name, x.raw_value) for x in record.unknown_metadata] == [
        ("future_vendor_field", "opaque-value")
    ]

def test_09_unknown_data_column_is_preserved_without_unit_guess():
    record = single.parse_single_csv(D09 / "valid_unknown_fields.csv")
    future = next(item for item in record.signals if item.vendor_name == "FutureSensor-A")
    assert future.unknown_semantics is True
    assert future.unit is None
    assert future.unit_evidence == "UNKNOWN"

def test_10_missing_raw_value_becomes_none_only_in_typed_view():
    path = D15 / "golden/missing_value_preserved.csv"
    record = single.parse_single_csv(path)
    signal = next(item for item in record.signals if item.vendor_name == "LT BICEPS FEM.")
    assert signal.raw_values[1] == (None,)
    assert record.raw_rows[1][3] == ""

def test_11_utf8_bom_is_accepted_without_mutation():
    path = D15 / "golden/utf8_bom.csv"
    before = sha256_file(path)
    record = single.parse_single_csv(path)
    assert len(record.raw_rows) == 3
    assert sha256_file(path) == before

@pytest.mark.parametrize(
    ("name", "reason"),
    [
        ("malformed_header.csv", "INGEST_SCHEMA_ERROR"),
        ("count_mismatch.csv", "COUNT_MISMATCH"),
        ("duplicate_timestamp.csv", "TIMESTAMP_INVALID"),
        ("out_of_order_timestamp.csv", "TIMESTAMP_INVALID"),
        ("missing_row.csv", "COUNT_MISMATCH"),
        ("binary_garbage.csv", "INGEST_SCHEMA_ERROR"),
    ],
)
def test_12_day15_invalid_csvs_fail_closed(name: str, reason: str):
    with pytest.raises(Mr4ParseError) as caught:
        single.parse_single_csv(D15 / "corrupted" / name)
    assert caught.value.code == reason

def test_13_day09_missing_blank_separator_fails():
    with pytest.raises(Mr4ParseError) as caught:
        single.parse_single_csv(D09 / "invalid_missing_blank_separator.csv")
    assert caught.value.code == "INGEST_SCHEMA_ERROR"

def test_14_signal_descriptors_use_table_sampling_rate_only_for_single_csv():
    record = single.parse_single_csv(D09 / "valid_minimal.csv")
    rates = {item.sampling_rate_hz for item in record.signals}
    assert rates == {2000.0}

def test_15_event_columns_are_not_assigned_physical_units():
    record = single.parse_single_csv(D09 / "valid_minimal.csv")
    activity = next(item for item in record.signals if item.vendor_name == "Activity")
    marker = next(item for item in record.signals if item.vendor_name == "Marker")
    assert activity.unit is None and marker.unit is None

def test_16_emg_contract_pattern_has_uv_unit_evidence():
    record = single.parse_single_csv(D09 / "valid_minimal.csv")
    emg = next(item for item in record.signals if item.vendor_name == "LT BICEPS FEM.")
    assert emg.unit == "uV"
    assert emg.unit_evidence == "OBSERVED_CONTRACT_PATTERN"

def test_17_force_semantics_remain_generic_numeric_signal():
    record = single.parse_single_csv(D09 / "valid_minimal.csv")
    force = next(item for item in record.signals if item.vendor_name == "LT Force")
    assert force.semantic_role == "NUMERIC_SIGNAL"
    assert force.unit == "N"

def test_18_no_column_is_dropped():
    record = single.parse_single_csv(D09 / "valid_minimal.csv")
    assert len(record.signals) == len(record.data_header) - 1

def test_19_parser_has_no_ai_training_dependency():
    text = (ROOT / "services/signal-ingestion-service/src/adapters/mr4/parser.py").read_text(encoding="utf-8").lower()
    for token in ("torch", "tensorflow", "sklearn", ".fit(", "onnx", "ood_score"):
        assert token not in text

def test_20_parser_does_not_resample_interpolate_or_preprocess():
    text = (ROOT / "services/signal-ingestion-service/src/adapters/mr4/parser.py").read_text(encoding="utf-8").lower()
    for token in ("resample(", "interpolate(", "bandpass", "notch", "rectif"):
        assert token not in text

def test_21_invalid_frequency_is_typed_failure(tmp_path: Path):
    path = tmp_path / "bad.csv"
    path.write_text(
        "type,frequency,count\nrecord,0,1\n\ntime,value\n0.0,1\n",
        encoding="utf-8",
    )
    with pytest.raises(Mr4ParseError) as caught:
        single.parse_single_csv(path)
    assert caught.value.code == "INGEST_SCHEMA_ERROR"

def test_22_non_numeric_timestamp_is_typed_failure(tmp_path: Path):
    path = tmp_path / "bad.csv"
    path.write_text(
        "type,count\nrecord,1\n\ntime,value\nabc,1\n",
        encoding="utf-8",
    )
    with pytest.raises(Mr4ParseError) as caught:
        single.parse_single_csv(path)
    assert caught.value.code == "TIMESTAMP_INVALID"

def test_23_row_arity_mismatch_is_typed_failure(tmp_path: Path):
    path = tmp_path / "bad.csv"
    path.write_text(
        "type,count\nrecord,1\n\ntime,a,b\n0.0,1\n",
        encoding="utf-8",
    )
    with pytest.raises(Mr4ParseError) as caught:
        single.parse_single_csv(path)
    assert caught.value.code == "INGEST_SCHEMA_ERROR"

def test_24_duplicate_data_header_is_typed_failure(tmp_path: Path):
    path = tmp_path / "bad.csv"
    path.write_text(
        "type,count\nrecord,1\n\ntime,a,a\n0.0,1,2\n",
        encoding="utf-8",
    )
    with pytest.raises(Mr4ParseError):
        single.parse_single_csv(path)

def test_25_empty_timeseries_is_typed_failure(tmp_path: Path):
    path = tmp_path / "bad.csv"
    path.write_text("type,count\nrecord,0\n\ntime,a\n", encoding="utf-8")
    with pytest.raises(Mr4ParseError):
        single.parse_single_csv(path)

def test_26_source_hash_is_raw_bytes_not_decoded_text(tmp_path: Path):
    path = tmp_path / "bom.csv"
    payload = (
        b"\xef\xbb\xbf"
        b"type,count\nrecord,1\n\ntime,value\n0.0,1\n"
    )
    path.write_bytes(payload)
    record = single.parse_single_csv(path)
    import hashlib
    assert record.source.sha256 == hashlib.sha256(payload).hexdigest()

def test_27_run_id_changes_when_source_bytes_change(tmp_path: Path):
    p1 = tmp_path / "a.csv"
    p2 = tmp_path / "b.csv"
    p1.write_text("type,count\nrecord,1\n\ntime,value\n0.0,1\n", encoding="utf-8")
    p2.write_text("type,count\nrecord,1\n\ntime,value\n0.0,2\n", encoding="utf-8")
    first = single.parse_single_csv(p1).provenance.run_id
    second = single.parse_single_csv(p2).provenance.run_id
    assert first != second

def test_28_error_object_is_serializable_for_evidence(tmp_path: Path):
    path = tmp_path / "bad.csv"
    path.write_bytes(b"\xff")
    with pytest.raises(Mr4ParseError) as caught:
        single.parse_single_csv(path)
    payload = caught.value.to_dict()
    assert payload["code"] == "INGEST_SCHEMA_ERROR"
    json.dumps(payload)
