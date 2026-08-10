from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

HERE = Path(__file__).resolve()
ROOT = next(parent for parent in HERE.parents if (parent / "data-platform").exists())
MODULE = ROOT / "services/signal-ingestion-service/src/validation/time_count_unit.py"
REGISTRY = ROOT / "data-platform/contracts/unit-registry.v0.1.yaml"
GOLDEN = ROOT / "qa-validation/test-data/golden/day13"
CORRUPTED = ROOT / "qa-validation/test-data/corrupted/day13"


def load_module():
    spec = importlib.util.spec_from_file_location("day13_time_count_unit", MODULE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


m = load_module()
registry = m.load_unit_registry(REGISTRY)
SRC = "src_sha256_" + "a" * 64
SIG = "sig_" + "b" * 32


def payload(name: str, *, corrupted: bool = False) -> dict:
    root = CORRUPTED if corrupted else GOLDEN
    return json.loads((root / name).read_text(encoding="utf-8"))


def inp(name: str = "golden-emg-2000hz.json", *, corrupted: bool = False):
    return m.SignalValidationInput.model_validate(payload(name, corrupted=corrupted))


def codes(report):
    return {finding.code.value: finding for finding in report.findings}


def test_01_registry_loads_and_is_versioned():
    assert registry.registry_id == "motionlab-unit-registry"
    assert registry.registry_version == "v0.1"


def test_02_registry_contains_v_and_uv():
    assert registry.has_unit("V")
    assert registry.has_unit("uV")


def test_03_happy_path_passes():
    report = m.validate_signal(inp(), registry=registry)
    assert report.overall_status is m.CheckStatus.PASS


def test_04_time_is_strictly_monotonic():
    report = m.validate_signal(inp(), registry=registry)
    assert codes(report)["TIME_OK"].status is m.CheckStatus.PASS


def test_05_duplicate_timestamp_fails():
    report = m.validate_signal(inp("duplicate-time.json", corrupted=True), registry=registry)
    assert codes(report)["TIME_DUPLICATE"].status is m.CheckStatus.FAIL


def test_06_out_of_order_timestamp_fails():
    report = m.validate_signal(inp("non-monotonic-time.json", corrupted=True), registry=registry)
    assert codes(report)["TIME_NON_MONOTONIC"].status is m.CheckStatus.FAIL


def test_07_count_match_passes():
    report = m.validate_signal(inp(), registry=registry)
    assert codes(report)["COUNT_MATCH"].observed == 4


def test_08_count_mismatch_fails():
    report = m.validate_signal(inp("count-mismatch.json", corrupted=True), registry=registry)
    assert codes(report)["COUNT_MISMATCH"].status is m.CheckStatus.FAIL


def test_09_missing_count_is_not_inferred():
    report = m.validate_signal(inp("golden-metadata-partial.json"), registry=registry)
    finding = codes(report)["COUNT_METADATA_UNAVAILABLE"]
    assert finding.status is m.CheckStatus.NOT_EVALUATED


def test_10_begin_time_match_passes():
    report = m.validate_signal(inp(), registry=registry)
    assert codes(report)["BEGIN_TIME_MATCH"].status is m.CheckStatus.PASS


def test_11_begin_time_mismatch_fails():
    report = m.validate_signal(inp("begin-time-mismatch.json", corrupted=True), registry=registry)
    assert codes(report)["BEGIN_TIME_MISMATCH"].status is m.CheckStatus.FAIL


def test_12_missing_begin_time_is_not_promoted_from_first_sample():
    report = m.validate_signal(inp("golden-metadata-partial.json"), registry=registry)
    assert codes(report)["BEGIN_TIME_METADATA_UNAVAILABLE"].status is m.CheckStatus.NOT_EVALUATED


def test_13_positive_declared_fs_passes():
    report = m.validate_signal(inp(), registry=registry)
    assert codes(report)["SAMPLING_RATE_VALID"].observed == 2000.0


def test_14_nonpositive_fs_is_typed_failure():
    report = m.validate_signal(
        inp("sampling-rate-invalid.json", corrupted=True),
        registry=registry,
    )
    assert codes(report)["SAMPLING_RATE_INVALID"].status is m.CheckStatus.FAIL


def test_15_sampling_interval_matches_declared_fs():
    report = m.validate_signal(inp(), registry=registry)
    assert codes(report)["SAMPLING_INTERVAL_MATCH"].status is m.CheckStatus.PASS


def test_16_sampling_interval_mismatch_fails():
    report = m.validate_signal(
        inp("sampling-interval-mismatch.json", corrupted=True),
        registry=registry,
    )
    assert codes(report)["SAMPLING_INTERVAL_MISMATCH"].status is m.CheckStatus.FAIL


def test_17_missing_fs_does_not_assume_common_rate():
    report = m.validate_signal(inp("golden-metadata-partial.json"), registry=registry)
    assert (
        codes(report)["SAMPLING_RATE_METADATA_UNAVAILABLE"].status
        is m.CheckStatus.NOT_EVALUATED
    )


def test_18_heterogeneous_rates_are_validated_independently():
    reports = m.validate_signals(
        [inp(), inp("golden-cop-100hz.json")],
        registry=registry,
    )
    assert [report.overall_status for report in reports] == [
        m.CheckStatus.PASS,
        m.CheckStatus.PASS,
    ]
    assert reports[0].provenance.signal_id != reports[1].provenance.signal_id


def test_19_v_is_known():
    report = m.validate_signal(inp("golden-emg-volts-2000hz.json"), registry=registry)
    assert codes(report)["UNIT_KNOWN"].observed == "V"


def test_20_uv_is_known():
    report = m.validate_signal(inp(), registry=registry)
    assert codes(report)["UNIT_KNOWN"].observed == "uV"


def test_21_unknown_unit_fails_closed():
    report = m.validate_signal(inp("unknown-unit.json", corrupted=True), registry=registry)
    assert codes(report)["UNIT_UNKNOWN"].status is m.CheckStatus.FAIL


def test_22_missing_unit_is_not_defaulted():
    report = m.validate_signal(inp("golden-metadata-partial.json"), registry=registry)
    assert codes(report)["UNIT_METADATA_UNAVAILABLE"].status is m.CheckStatus.NOT_EVALUATED


def test_23_v_to_uv_conversion_is_explicit():
    result = m.convert_values(
        [0.001], source_unit="V", target_unit="uV", registry=registry,
        source_record_id=SRC, signal_id=SIG,
    )
    assert result.values == (1000.0,)
    assert result.provenance.factor == 1_000_000.0


def test_24_uv_to_v_conversion_is_explicit():
    result = m.convert_values(
        [1000.0], source_unit="uV", target_unit="V", registry=registry,
        source_record_id=SRC, signal_id=SIG,
    )
    assert result.values == (0.001,)
    assert result.provenance.factor == 0.000001


def test_25_identity_conversion_is_explicit_copy():
    original = [1.0, 2.0]
    result = m.convert_values(
        original, source_unit="uV", target_unit="uV", registry=registry,
        source_record_id=SRC, signal_id=SIG,
    )
    assert result.values == (1.0, 2.0)
    assert result.provenance.factor == 1.0
    assert original == [1.0, 2.0]


def test_26_unsupported_conversion_raises():
    with pytest.raises(m.UnsupportedUnitConversionError):
        m.convert_values(
            [1.0], source_unit="N", target_unit="uV", registry=registry,
            source_record_id=SRC, signal_id=SIG,
        )


def test_27_conversion_provenance_is_complete():
    result = m.convert_values(
        [1.0], source_unit="V", target_unit="uV", registry=registry,
        source_record_id=SRC, signal_id=SIG,
    )
    p = result.provenance
    assert (
        p.registry_version,
        p.source_unit,
        p.target_unit,
        p.signal_id,
    ) == ("v0.1", "V", "uV", SIG)


def test_28_conversion_rejects_nonfinite_values():
    with pytest.raises(m.ValidationContractError):
        m.convert_values(
            [float("nan")], source_unit="V", target_unit="uV", registry=registry,
            source_record_id=SRC, signal_id=SIG,
        )


def test_29_report_is_deterministic():
    first = m.validate_signal(inp(), registry=registry)
    second = m.validate_signal(inp(), registry=registry)
    assert first == second
    assert first.validation_id == second.validation_id


def test_30_config_version_or_tolerance_changes_identity():
    signal = inp()
    first = m.validate_signal(signal, registry=registry)
    cfg = m.ValidationConfig(
        version="day13-validation-profile.v0.1.1",
        sampling_interval_abs_tolerance_seconds=1e-5,
    )
    second = m.validate_signal(signal, registry=registry, config=cfg)
    assert first.validation_id != second.validation_id


def test_31_invalid_source_id_rejected_at_runtime():
    p = payload("golden-emg-2000hz.json")
    p["source_record_id"] = "bad"
    with pytest.raises((ValidationError, m.ValidationContractError)):
        m.SignalValidationInput.model_validate(p)


def test_32_invalid_signal_id_rejected_at_runtime():
    p = payload("golden-emg-2000hz.json")
    p["signal_id"] = "sig_xyz"
    with pytest.raises((ValidationError, m.ValidationContractError)):
        m.SignalValidationInput.model_validate(p)


def test_33_nonfinite_timestamp_rejected_at_runtime():
    p = payload("golden-emg-2000hz.json")
    p["timestamps_seconds"][1] = float("nan")
    with pytest.raises(ValidationError):
        m.SignalValidationInput.model_validate(p)


def test_34_empty_series_fails_closed():
    report = m.validate_signal(inp("empty-time-series.json", corrupted=True), registry=registry)
    assert report.overall_status is m.CheckStatus.FAIL
    assert codes(report)["TIME_SERIES_EMPTY"].status is m.CheckStatus.FAIL


def test_35_report_json_round_trip_is_stable():
    report = m.validate_signal(inp(), registry=registry)
    encoded = report.model_dump_json()
    restored = m.ValidationReport.model_validate_json(encoded)
    assert restored == report


def test_36_module_does_not_parse_csv_or_import_dataframe_stack():
    text = MODULE.read_text(encoding="utf-8")
    assert "pandas" not in text
    assert "read_csv" not in text


def test_37_unit_registry_does_not_authorize_guessing_mv():
    assert not registry.has_unit("mV")
    with pytest.raises(m.UnsupportedUnitConversionError):
        registry.conversion_factor("mV", "uV")


def test_38_golden_fixtures_all_pass_or_explicitly_not_evaluated():
    for path in sorted(GOLDEN.glob("*.json")):
        signal = m.SignalValidationInput.model_validate(
            json.loads(path.read_text(encoding="utf-8"))
        )
        report = m.validate_signal(signal, registry=registry)
        assert report.overall_status is m.CheckStatus.PASS, path.name


def test_39_corrupted_fixtures_fail():
    for path in sorted(CORRUPTED.glob("*.json")):
        signal = m.SignalValidationInput.model_validate(
            json.loads(path.read_text(encoding="utf-8"))
        )
        report = m.validate_signal(signal, registry=registry)
        assert report.overall_status is m.CheckStatus.FAIL, path.name


def test_40_raw_fixture_bytes_are_not_modified_by_validation():
    path = GOLDEN / "golden-emg-2000hz.json"
    before = path.read_bytes()
    signal = m.SignalValidationInput.model_validate(json.loads(before))
    m.validate_signal(signal, registry=registry)
    assert path.read_bytes() == before
