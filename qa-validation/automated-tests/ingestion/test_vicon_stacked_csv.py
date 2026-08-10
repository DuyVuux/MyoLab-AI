from __future__ import annotations

import dataclasses
import json
import sys
from pathlib import Path

import jsonschema
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "services/signal-ingestion-service/src"
sys.path.insert(0, str(SRC))

from adapters.vicon import vicon_stacked_csv as vicon  # noqa: E402
from adapters.vicon.vicon_models import ViconParseError  # noqa: E402
from adapters.common.provenance import sha256_file  # noqa: E402

GOLDEN = ROOT / "qa-validation/test-data/golden/day18/vicon_minimal_stacked.csv"
BOM = ROOT / "qa-validation/test-data/golden/day18/vicon_minimal_stacked_bom.csv"
BAD = ROOT / "qa-validation/test-data/corrupted/day18"
CONTRACT = ROOT / "data-platform/contracts/vicon/stacked-sections.v0.1.yaml"
SCHEMA = ROOT / "packages/common-schemas/json/multimodal-alignment-context.schema.json"


def parse():
    return vicon.parse_vicon_stacked_csv(GOLDEN)


def test_01_target_module_exists():
    assert Path(vicon.__file__).is_file()


def test_02_contract_loads():
    payload = yaml.safe_load(CONTRACT.read_text())
    assert payload["contract_id"] == "VICON_STACKED_SECTIONS_V0_1"


def test_03_four_supported_sections_parse():
    assert [x.section_name for x in parse().sections] == [
        "Events", "Devices", "Model Outputs", "Trajectories"
    ]


def test_04_gait_parameters_preserved_evidence_only():
    record = parse()
    assert record.evidence_only_sections[0].section_name == "Gait Cycle Parameters"
    assert "SECTION_PRESERVED_NOT_PARSED_IN_DAY18_SCOPE" == record.evidence_only_sections[0].reason


def test_05_devices_sampling_rate_preserved():
    assert parse().section("Devices").sampling_rate_hz == 2000.0


def test_06_model_output_sampling_rate_preserved():
    assert parse().section("Model Outputs").sampling_rate_hz == 100.0


def test_07_multirow_headers_preserved_exactly():
    section = parse().section("Devices")
    assert len(section.raw_header_rows) == 3
    assert section.raw_header_rows[0][2] == "Ultium EMG - LT Biceps"
    assert section.raw_header_rows[2][2] == "V"


def test_08_trajectory_units_preserved():
    section = parse().section("Trajectories")
    assert [c.unit_raw for c in section.columns[1:4]] == ["mm", "mm", "mm"]


def test_09_missing_marker_cells_preserved_as_none():
    section = parse().section("Trajectories")
    assert section.raw_rows[1][-1] == ""
    assert section.values[1][-1] is None
    assert section.values[1][-3:] == (None, None, None)


def test_10_x_y_z_are_component_labels_only():
    section = parse().section("Model Outputs")
    components = [c for c in section.columns if c.component_label]
    assert [c.component_label for c in components] == ["X", "Y", "Z"]
    assert all(c.anatomical_plane is None for c in components)
    assert all(c.anatomical_plane_evidence == "NOT_VERIFIED" for c in components)


def test_11_raw_source_is_immutable():
    before = sha256_file(GOLDEN)
    parse()
    after = sha256_file(GOLDEN)
    assert before == after


def test_12_source_hash_and_id_exist():
    source = parse().source
    assert len(source.sha256) == 64
    assert source.source_id == "src_sha256_" + source.sha256


def test_13_deterministic_replay():
    assert parse() == parse()


def test_14_bom_is_accepted():
    record = vicon.parse_vicon_stacked_csv(BOM)
    assert record.section("Events") is not None


def test_15_bad_frequency_fails_typed():
    with pytest.raises(ViconParseError) as exc:
        vicon.parse_vicon_stacked_csv(BAD / "bad_frequency.csv")
    assert exc.value.code == "INGEST_SCHEMA_ERROR"


def test_16_bad_multirow_header_width_fails():
    with pytest.raises(ViconParseError) as exc:
        vicon.parse_vicon_stacked_csv(BAD / "bad_header_width.csv")
    assert exc.value.code == "INGEST_SCHEMA_ERROR"


def test_17_unknown_section_fails_closed():
    with pytest.raises(ViconParseError) as exc:
        vicon.parse_vicon_stacked_csv(BAD / "unknown_section.csv")
    assert exc.value.code == "VICON_SECTION_NOT_IN_CONTRACT"


def test_18_duplicate_section_fails_closed():
    with pytest.raises(ViconParseError) as exc:
        vicon.parse_vicon_stacked_csv(BAD / "duplicate_events.csv")
    assert exc.value.code == "INGEST_SCHEMA_ERROR"


def test_19_default_alignment_is_not_verified():
    a = parse().alignment
    assert a.sync_status == "NOT_VERIFIED"
    assert a.offset_seconds is None
    assert a.drift_ppm is None
    assert a.quality == "NOT_VERIFIED"


def test_20_default_alignment_does_not_fake_zero_offset():
    assert parse().alignment.offset_seconds is None


def test_21_verified_alignment_requires_evidence():
    context = vicon.MultimodalAlignmentContext(sync_status="VERIFIED")
    with pytest.raises(ViconParseError) as exc:
        vicon.parse_vicon_stacked_csv(GOLDEN, alignment=context)
    assert exc.value.code == "MULTIMODAL_ALIGNMENT_INVALID"


def test_22_verified_alignment_can_carry_offset_and_drift():
    context = vicon.MultimodalAlignmentContext(
        sync_source="TTL_TRIGGER",
        sync_status="VERIFIED",
        offset_seconds=0.004,
        drift_ppm=2.5,
        quality="GOOD",
        evidence_refs=("synthetic://ttl-check",),
    )
    result = vicon.parse_vicon_stacked_csv(GOLDEN, alignment=context)
    assert result.alignment == context


def test_23_unverified_alignment_cannot_carry_offset():
    context = vicon.MultimodalAlignmentContext(offset_seconds=0.0)
    with pytest.raises(ViconParseError):
        vicon.parse_vicon_stacked_csv(GOLDEN, alignment=context)


def test_24_alignment_schema_accepts_default():
    schema = json.loads(SCHEMA.read_text())
    jsonschema.validate(json.loads(json.dumps(dataclasses.asdict(parse().alignment))), schema)


def test_25_alignment_schema_rejects_unknown_status():
    schema = json.loads(SCHEMA.read_text())
    payload = dataclasses.asdict(parse().alignment)
    payload["sync_status"] = "MAGIC"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, schema)


def test_26_no_shared_embedding_or_ml_dependency():
    text = Path(vicon.__file__).read_text().lower()
    for token in ("torch", "tensorflow", "sklearn", "embedding", "fit(", "predict("):
        assert token not in text


def test_27_no_resampling_or_interpolation():
    text = Path(vicon.__file__).read_text().lower()
    assert "resample(" not in text
    assert "interpolate(" not in text


def test_28_not_generic_vicon_replacement():
    payload = yaml.safe_load(CONTRACT.read_text())
    assert payload["scope"]["generic_vicon_replacement"] is False


def test_29_coordinate_mapping_explicitly_not_verified():
    payload = yaml.safe_load(CONTRACT.read_text())
    assert payload["invariants"]["x_y_z_to_anatomical_plane"] == "NOT_VERIFIED"


def test_30_frozen_context_objects():
    with pytest.raises(dataclasses.FrozenInstanceError):
        parse().alignment.quality = "GOOD"


def test_31_events_raw_time_is_preserved():
    events = parse().section("Events")
    assert events.raw_rows[0][3] == "0.41"


def test_32_events_are_context_not_clinical_interpretation():
    text = Path(vicon.__file__).read_text().lower()
    assert "diagnos" not in text
    assert "treatment" not in text


def test_33_record_provenance_is_versioned():
    p = parse().provenance
    assert p.parser_version == "0.1.0"
    assert p.contract_version == "0.1.0"


def test_34_run_id_is_stable():
    assert parse().provenance.run_id == parse().provenance.run_id
    assert parse().provenance.run_id.startswith("parse_sha256_")


def test_35_warning_exposes_evidence_only_section():
    assert "EVIDENCE_ONLY_SECTION:Gait Cycle Parameters" in parse().warnings


def test_36_section_lookup_missing_returns_none():
    assert parse().section("Not Supported") is None
