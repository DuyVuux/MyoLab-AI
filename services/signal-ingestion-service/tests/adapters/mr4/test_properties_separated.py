from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[5]
ADAPTERS = ROOT / "services/signal-ingestion-service/src/adapters"
sys.path.insert(0, str(ADAPTERS))

from adapters.mr4 import parser_separated as separated  # noqa: E402
from adapters.mr4.models import Mr4ParseError, sha256_file  # noqa: E402

INVARIANTS = ROOT / "qa-validation/property-tests/day15_corruption/ingestion-invariants.v0.1.yaml"
FIXTURES = ROOT / "qa-validation/test-data/synthetic/day17"
PROFILE_PATH = (
    ROOT
    / "services/signal-ingestion-service/contracts/noraxon/mr4-separated-layout-profile.synthetic.v0.1.yaml"
)


def profile():
    return separated.load_layout_profile(PROFILE_PATH)


def invariant_names():
    payload = yaml.safe_load(INVARIANTS.read_text(encoding="utf-8"))
    return {
        item["name"]
        for group in ("critical_invariants", "boundary_invariants")
        for item in payload[group]
    }


def test_01_day15_invariant_contract_is_present():
    assert INVARIANTS.is_file()
    critical = {
        "RAW_IMMUTABLE",
        "UNKNOWN_UNIT_NEVER_INFERRED",
        "NO_SILENT_CRASH",
        "FAIL_CLOSED",
    }
    assert critical <= invariant_names()


def test_02_raw_immutable_across_entire_record():
    directory = FIXTURES / "base_record"
    before = {p.name: sha256_file(p) for p in directory.glob("*.csv")}
    separated.assemble_separated_export(directory, layout_profile=profile())
    after = {p.name: sha256_file(p) for p in directory.glob("*.csv")}
    assert before == after


def test_03_unknown_unit_never_inferred():
    with pytest.raises(Mr4ParseError) as caught:
        separated.assemble_separated_export(
            FIXTURES / "unknown_unit_record",
            layout_profile=profile(),
        )
    assert caught.value.code == "UNIT_MISMATCH"
    assert caught.value.details["unit"] == "mV?"


def test_04_mixed_fs_valid_edge_is_accepted():
    record = separated.assemble_separated_export(
        FIXTURES / "base_record",
        layout_profile=profile(),
    )
    rates = sorted(
        x.frequency_hz for x in record.signals if x.frequency_hz is not None
    )
    assert rates == [100.0, 2000.0]


def test_05_malformed_shape_fails_closed():
    with pytest.raises(Mr4ParseError) as caught:
        separated.assemble_separated_export(
            FIXTURES / "bad_shape_record",
            layout_profile=profile(),
        )
    assert caught.value.code == "INGEST_SCHEMA_ERROR"


def test_06_count_failure_is_typed():
    with pytest.raises(Mr4ParseError) as caught:
        separated.assemble_separated_export(
            FIXTURES / "count_mismatch_record",
            layout_profile=profile(),
        )
    assert caught.value.code == "COUNT_MISMATCH"
    assert caught.value.message


def test_07_deterministic_replay_property():
    directory = FIXTURES / "base_record"
    first = separated.assemble_separated_export(directory, layout_profile=profile())
    second = separated.assemble_separated_export(directory, layout_profile=profile())
    assert first == second


def test_08_unknown_signal_is_preserved_not_silent_drop():
    record = separated.assemble_separated_export(
        FIXTURES / "unknown_type_record",
        layout_profile=profile(),
    )
    assert record.unknown_signals
    assert "UNSUPPORTED_SIGNAL_TYPE_PRESERVED" in record.warnings


def test_09_orphan_signal_preserves_source_linkage():
    record = separated.assemble_separated_export(
        FIXTURES / "orphan_record",
        layout_profile=profile(),
    )
    orphan = next(x for x in record.signals if x.vendor_name is None)
    assert orphan.source.sha256
    assert orphan.signal_id.startswith("sig_")


def test_10_missing_value_not_interpolated(tmp_path: Path):
    source = FIXTURES / "base_record"
    for path in source.glob("*.csv"):
        (tmp_path / path.name).write_bytes(path.read_bytes())
    emg = tmp_path / "emg.csv"
    changed = emg.read_text(encoding="utf-8").replace(
        "0.00050,13.1",
        "0.00050,",
    )
    emg.write_text(changed, encoding="utf-8")
    record = separated.assemble_separated_export(tmp_path, layout_profile=profile())
    signal = next(
        x for x in record.signals if x.vendor_name == "Ultium_EMG-LT_BICEPS_FEM."
    )
    assert signal.values[1] == (None,)
    assert signal.raw_rows[1][1] == ""


def test_11_unverified_site_profile_fails_closed():
    site = (
        ROOT
        / "services/signal-ingestion-service/contracts/noraxon/mr4-separated-layout-profile.site.template.yaml"
    )
    with pytest.raises(Mr4ParseError) as caught:
        separated.load_layout_profile(site)
    assert caught.value.code == "INFO_LAYOUT_NOT_VERIFIED"


def test_12_same_fs_assumption_does_not_exist_in_code():
    text = Path(separated.__file__).read_text(encoding="utf-8").lower()
    tail = text.split("all(", 1)[-1][:120] if "all(" in text else ""
    assert "frequency_hz" not in tail
    assert "resample(" not in text


def test_13_no_silent_crash_on_binary_signal(tmp_path: Path):
    source = FIXTURES / "base_record"
    for path in source.glob("*.csv"):
        (tmp_path / path.name).write_bytes(path.read_bytes())
    (tmp_path / "emg.csv").write_bytes(b"\xff\xfe\x00")
    with pytest.raises(Mr4ParseError) as caught:
        separated.assemble_separated_export(tmp_path, layout_profile=profile())
    assert caught.value.code == "INGEST_SCHEMA_ERROR"


def test_14_source_lineage_count_matches_source_files():
    record = separated.assemble_separated_export(
        FIXTURES / "base_record",
        layout_profile=profile(),
    )
    expected = 1 + len(record.signals) + len(record.unknown_signals)
    assert len(record.source_files) == expected


def test_15_profile_identity_participates_in_assembly_identity(tmp_path: Path):
    p1 = profile()
    p2 = separated.SeparatedLayoutProfile(
        profile_id=p1.profile_id + "_ALT",
        version=p1.version,
        status=p1.status,
        evidence_status=p1.evidence_status,
        info_layout=p1.info_layout,
        signal_layout=p1.signal_layout,
        site_verified=p1.site_verified,
    )
    r1 = separated.assemble_separated_export(
        FIXTURES / "base_record",
        layout_profile=p1,
    )
    r2 = separated.assemble_separated_export(
        FIXTURES / "base_record",
        layout_profile=p2,
    )
    assert r1.assembly_id != r2.assembly_id
