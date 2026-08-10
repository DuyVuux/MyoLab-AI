from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[5]
ADAPTERS = ROOT / "services/signal-ingestion-service/src/adapters"
sys.path.insert(0, str(ADAPTERS))

from adapters.mr4 import parser_separated as separated  # noqa: E402
from adapters.mr4.models import Mr4ParseError, sha256_file  # noqa: E402

FIXTURES = ROOT / "qa-validation/test-data/synthetic/day17"
PROFILE_PATH = (
    ROOT
    / "services/signal-ingestion-service/contracts/noraxon/mr4-separated-layout-profile.synthetic.v0.1.yaml"
)
SITE_TEMPLATE = (
    ROOT
    / "services/signal-ingestion-service/contracts/noraxon/mr4-separated-layout-profile.site.template.yaml"
)


def profile():
    return separated.load_layout_profile(PROFILE_PATH)


def test_01_parser_identity_is_versioned():
    assert separated.PARSER_ID == "noraxon-mr4-separated-csv"
    assert separated.PARSER_VERSION == "0.1.0"


def test_02_explicit_synthetic_profile_loads():
    p = profile()
    assert p.info_layout == "HORIZONTAL_HEADER_VALUE"
    assert p.site_verified is False


def test_03_site_template_refuses_unverified_layout():
    with pytest.raises(Mr4ParseError) as caught:
        separated.load_layout_profile(SITE_TEMPLATE)
    assert caught.value.code == "INFO_LAYOUT_NOT_VERIFIED"


def test_04_assembler_refuses_missing_profile():
    with pytest.raises(Mr4ParseError) as caught:
        separated.assemble_separated_export(
            FIXTURES / "base_record",
            layout_profile=None,
        )
    assert caught.value.code == "INFO_LAYOUT_NOT_VERIFIED"


def test_05_base_record_assembles():
    record = separated.assemble_separated_export(
        FIXTURES / "base_record",
        layout_profile=profile(),
    )
    assert len(record.signals) == 2
    assert not record.unknown_signals


def test_06_mixed_sampling_rates_are_preserved():
    record = separated.assemble_separated_export(
        FIXTURES / "base_record",
        layout_profile=profile(),
    )
    assert {signal.frequency_hz for signal in record.signals} == {2000.0, 100.0}


def test_07_signal_and_signal2d_shapes_are_distinct():
    record = separated.assemble_separated_export(
        FIXTURES / "base_record",
        layout_profile=profile(),
    )
    by_type = {signal.signal_type: signal for signal in record.signals}
    assert by_type["signal"].columns == ("time", "value")
    assert by_type["signal_2d"].columns == ("time", "x", "y")


def test_08_per_signal_units_are_preserved():
    record = separated.assemble_separated_export(
        FIXTURES / "base_record",
        layout_profile=profile(),
    )
    units = {signal.vendor_name: signal.unit for signal in record.signals}
    assert units["Ultium_EMG-LT_BICEPS_FEM."] == "uV"
    assert units["Pressure_Platform-Contacts-Foot_LT-LT_COP"] == "mm"


def test_09_each_signal_has_own_source_linkage():
    record = separated.assemble_separated_export(
        FIXTURES / "base_record",
        layout_profile=profile(),
    )
    assert len({signal.source.source_id for signal in record.signals}) == 2
    assert all(signal.source.sha256 for signal in record.signals)


def test_10_record_has_all_file_lineage():
    record = separated.assemble_separated_export(
        FIXTURES / "base_record",
        layout_profile=profile(),
    )
    assert len(record.source_files) == 3
    assert {x.source_name for x in record.source_files} == {"info.csv", "emg.csv", "cop.csv"}


def test_11_unknown_signal_type_is_preserved_not_dropped():
    record = separated.assemble_separated_export(
        FIXTURES / "unknown_type_record",
        layout_profile=profile(),
    )
    assert len(record.unknown_signals) == 1
    unknown = record.unknown_signals[0]
    assert unknown.declared_type == "signal_3d"
    assert unknown.reason_code == "UNSUPPORTED_SIGNAL_TYPE_PRESERVED"


def test_12_orphan_missing_name_is_preserved_and_warned():
    record = separated.assemble_separated_export(
        FIXTURES / "orphan_record",
        layout_profile=profile(),
    )
    orphan = next(signal for signal in record.signals if signal.vendor_name is None)
    assert "ORPHAN_SIGNAL_MISSING_NAME_PRESERVED" in orphan.warnings
    assert orphan.source.source_name == "orphan.csv"


def test_13_unknown_unit_fails_closed_without_inference():
    with pytest.raises(Mr4ParseError) as caught:
        separated.assemble_separated_export(
            FIXTURES / "unknown_unit_record",
            layout_profile=profile(),
        )
    assert caught.value.code == "UNIT_MISMATCH"
    assert caught.value.details["unit"] == "mV?"


def test_14_signal2d_wrong_shape_fails_closed():
    with pytest.raises(Mr4ParseError) as caught:
        separated.assemble_separated_export(
            FIXTURES / "bad_shape_record",
            layout_profile=profile(),
        )
    assert caught.value.code == "INGEST_SCHEMA_ERROR"


def test_15_count_mismatch_fails_closed():
    with pytest.raises(Mr4ParseError) as caught:
        separated.assemble_separated_export(
            FIXTURES / "count_mismatch_record",
            layout_profile=profile(),
        )
    assert caught.value.code == "COUNT_MISMATCH"


def test_16_deterministic_replay_is_equal():
    first = separated.assemble_separated_export(
        FIXTURES / "base_record",
        layout_profile=profile(),
    )
    second = separated.assemble_separated_export(
        FIXTURES / "base_record",
        layout_profile=profile(),
    )
    assert first == second
    assert first.assembly_id == second.assembly_id


def test_17_source_hashes_are_unchanged_after_assembly():
    directory = FIXTURES / "base_record"
    before = {p.name: sha256_file(p) for p in directory.glob("*.csv")}
    separated.assemble_separated_export(directory, layout_profile=profile())
    after = {p.name: sha256_file(p) for p in directory.glob("*.csv")}
    assert before == after


def test_18_missing_info_csv_fails_closed(tmp_path: Path):
    (tmp_path / "signal.csv").write_text(
        "type,name,frequency,count,units\nsignal,X,100,1,N\n\ntime,value\n0,1\n",
        encoding="utf-8",
    )
    with pytest.raises(Mr4ParseError) as caught:
        separated.assemble_separated_export(tmp_path, layout_profile=profile())
    assert caught.value.code == "MISSING_REQUIRED_METADATA"


def test_19_no_signal_files_fails_closed(tmp_path: Path):
    (tmp_path / "info.csv").write_text("type,record_name\nrecord,SYNTHETIC\n", encoding="utf-8")
    with pytest.raises(Mr4ParseError) as caught:
        separated.assemble_separated_export(tmp_path, layout_profile=profile())
    assert caught.value.code == "MISSING_REQUIRED_METADATA"


def test_20_unknown_info_field_is_preserved(tmp_path: Path):
    base = FIXTURES / "base_record"
    for source in base.glob("*.csv"):
        (tmp_path / source.name).write_bytes(source.read_bytes())
    info = tmp_path / "info.csv"
    text = info.read_text(encoding="utf-8")
    lines = text.splitlines()
    lines[0] += ",future_info"
    lines[1] += ",opaque"
    info.write_text("\n".join(lines) + "\n", encoding="utf-8")
    record = separated.assemble_separated_export(tmp_path, layout_profile=profile())
    observed = [(x.name, x.raw_value) for x in record.unknown_info_metadata]
    assert observed == [("future_info", "opaque")]


def test_21_missing_frequency_is_warning_not_synthesized(tmp_path: Path):
    base = FIXTURES / "base_record"
    for source in base.glob("*.csv"):
        (tmp_path / source.name).write_bytes(source.read_bytes())
    emg = tmp_path / "emg.csv"
    text = emg.read_text(encoding="utf-8").replace(",2000,3,uV\n", ",,3,uV\n")
    emg.write_text(text, encoding="utf-8")
    record = separated.assemble_separated_export(tmp_path, layout_profile=profile())
    signal = next(x for x in record.signals if x.source.source_name == "emg.csv")
    assert signal.frequency_hz is None
    assert "SAMPLING_RATE_METADATA_UNAVAILABLE" in signal.warnings


def test_22_missing_unit_is_warning_not_synthesized(tmp_path: Path):
    base = FIXTURES / "base_record"
    for source in base.glob("*.csv"):
        (tmp_path / source.name).write_bytes(source.read_bytes())
    emg = tmp_path / "emg.csv"
    text = emg.read_text(encoding="utf-8").replace(",2000,3,uV\n", ",2000,3,\n")
    emg.write_text(text, encoding="utf-8")
    record = separated.assemble_separated_export(tmp_path, layout_profile=profile())
    signal = next(x for x in record.signals if x.source.source_name == "emg.csv")
    assert signal.unit is None
    assert "UNIT_METADATA_UNAVAILABLE" in signal.warnings


def test_23_duplicate_timestamp_fails(tmp_path: Path):
    base = FIXTURES / "base_record"
    for source in base.glob("*.csv"):
        (tmp_path / source.name).write_bytes(source.read_bytes())
    emg = tmp_path / "emg.csv"
    text = emg.read_text(encoding="utf-8").replace("0.00050,13.1", "0.00000,13.1")
    emg.write_text(text, encoding="utf-8")
    with pytest.raises(Mr4ParseError) as caught:
        separated.assemble_separated_export(tmp_path, layout_profile=profile())
    assert caught.value.code == "TIMESTAMP_INVALID"


def test_24_parser_has_no_ai_or_ood_execution():
    parser_path = ADAPTERS / "mr4" / "parser_separated.py"
    text = parser_path.read_text(encoding="utf-8").lower()
    for token in ("torch", "tensorflow", "sklearn", ".fit(", "ood_score", "onnx"):
        assert token not in text


def test_25_parser_has_no_resample_or_interpolation_call():
    parser_path = ADAPTERS / "mr4" / "parser_separated.py"
    text = parser_path.read_text(encoding="utf-8").lower()
    assert "resample(" not in text
    assert "interpolate(" not in text


def test_26_assembly_id_changes_when_one_source_changes(tmp_path: Path):
    base = FIXTURES / "base_record"
    for source in base.glob("*.csv"):
        (tmp_path / source.name).write_bytes(source.read_bytes())
    first = separated.assemble_separated_export(tmp_path, layout_profile=profile())
    emg = tmp_path / "emg.csv"
    changed = emg.read_text(encoding="utf-8").replace("12.5", "12.6", 1)
    emg.write_text(changed, encoding="utf-8")
    second = separated.assemble_separated_export(tmp_path, layout_profile=profile())
    assert first.assembly_id != second.assembly_id


def test_27_signal_id_is_source_linkage_sensitive(tmp_path: Path):
    base = FIXTURES / "base_record"
    for source in base.glob("*.csv"):
        (tmp_path / source.name).write_bytes(source.read_bytes())
    first = separated.assemble_separated_export(tmp_path, layout_profile=profile())
    emg = tmp_path / "emg.csv"
    changed = emg.read_text(encoding="utf-8").replace("12.5", "12.6", 1)
    emg.write_text(changed, encoding="utf-8")
    second = separated.assemble_separated_export(tmp_path, layout_profile=profile())
    first_emg = next(
        x for x in first.signals if x.vendor_name == "Ultium_EMG-LT_BICEPS_FEM."
    )
    second_emg = next(
        x for x in second.signals if x.vendor_name == "Ultium_EMG-LT_BICEPS_FEM."
    )
    assert first_emg.signal_id != second_emg.signal_id


def test_28_info_values_remain_raw_source_text():
    record = separated.assemble_separated_export(
        FIXTURES / "base_record",
        layout_profile=profile(),
    )
    measurement = next(x for x in record.info_metadata if x.name == "measurement_date")
    assert measurement.raw_value == "2025-08-26T17:29:12.325+07:00"
