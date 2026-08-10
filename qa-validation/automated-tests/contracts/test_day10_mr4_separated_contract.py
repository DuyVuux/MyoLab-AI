from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
SEPARATED_CONTRACT = ROOT / "data-platform/contracts/noraxon/mr4-separated.schema.yaml"
SIGNAL_CONTRACT = ROOT / "data-platform/contracts/noraxon/mr4-signal-file.schema.yaml"
DAY09_CONTRACT = ROOT / "data-platform/contracts/noraxon/mr4-single-csv.schema.yaml"
FIXTURES = ROOT / "qa-validation/test-data/golden/noraxon/separated_csv"
TRACEABILITY = ROOT / "qa-validation/traceability/day10-requirement-traceability.csv"


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_01_day09_upstream_exists() -> None:
    assert DAY09_CONTRACT.is_file()


def test_02_sep_exists() -> None:
    assert SEPARATED_CONTRACT.is_file()


def test_03_signal_exists() -> None:
    assert SIGNAL_CONTRACT.is_file()


def test_04_readme_exists() -> None:
    assert (FIXTURES / "README.md").is_file()


def test_05_technology_unchanged() -> None:
    assert load_yaml(SEPARATED_CONTRACT)["technology_augmentation"]["status"] == "UNCHANGED"


def test_06_no_production_parser_scope() -> None:
    assert load_yaml(SEPARATED_CONTRACT)["scope"]["production_parser_in_scope"] is False


def test_07_physical_layout_not_invented() -> None:
    status = load_yaml(SEPARATED_CONTRACT)["physical_layout"]["status"]
    assert status == "NOT_VERIFIED_FROM_AVAILABLE_DOCUMENTATION"


def test_08_info_known_fields() -> None:
    names = {
        item["name"]
        for item in load_yaml(SEPARATED_CONTRACT)["record_metadata"]["known_fields"]
    }
    expected = {
        "type",
        "created_with_version",
        "exported_with_version",
        "project",
        "last_name",
        "first_name",
        "born",
        "sex",
        "measurement_date",
        "record_name",
    }
    assert expected <= names


def test_09_direct_identifier_surface() -> None:
    fields = {
        item["name"]: item
        for item in load_yaml(SEPARATED_CONTRACT)["record_metadata"]["known_fields"]
    }
    assert fields["last_name"]["privacy_class"] == "DIRECT_IDENTIFIER"
    assert fields["first_name"]["privacy_class"] == "DIRECT_IDENTIFIER"


def test_10_free_text_risk() -> None:
    fields = {
        item["name"]: item
        for item in load_yaml(SEPARATED_CONTRACT)["record_metadata"]["known_fields"]
    }
    assert "POTENTIAL" in fields["record_name"]["privacy_class"]


def test_11_signal_types() -> None:
    assert set(load_yaml(SIGNAL_CONTRACT)["shapes"]) >= {"signal", "signal_2d", "unknown"}


def test_12_signal_shape() -> None:
    assert load_yaml(SIGNAL_CONTRACT)["shapes"]["signal"]["required_columns"] == [
        "time",
        "value",
    ]


def test_13_signal2d_shape() -> None:
    assert load_yaml(SIGNAL_CONTRACT)["shapes"]["signal_2d"]["required_columns"] == [
        "time",
        "x",
        "y",
    ]


def test_14_per_signal_frequency() -> None:
    fields = {
        item["name"]: item
        for item in load_yaml(SIGNAL_CONTRACT)["metadata"]["known_fields"]
    }
    assert "PER_SIGNAL" in fields["frequency"]["semantic"]


def test_15_per_signal_count() -> None:
    fields = {
        item["name"]: item
        for item in load_yaml(SIGNAL_CONTRACT)["metadata"]["known_fields"]
    }
    assert "PER_SIGNAL" in fields["count"]["semantic"]


def test_16_per_signal_units() -> None:
    fields = {
        item["name"]: item
        for item in load_yaml(SIGNAL_CONTRACT)["metadata"]["known_fields"]
    }
    assert "PER_SIGNAL" in fields["units"]["semantic"]


def test_17_same_fs_forbidden() -> None:
    assert load_yaml(SIGNAL_CONTRACT)["heterogeneous_sampling"]["same_fs_assumption_forbidden"] is True


def test_18_emg_2000_fixture() -> None:
    fixture = load_yaml(FIXTURES / "synthetic-emg-signal.yaml")
    assert fixture["metadata"]["frequency"] == 2000


def test_19_cop_100_fixture() -> None:
    fixture = load_yaml(FIXTURES / "synthetic-cop-signal2d.yaml")
    assert fixture["metadata"]["frequency"] == 100


def test_20_heterogeneous_fixture_rates() -> None:
    emg_frequency = load_yaml(FIXTURES / "synthetic-emg-signal.yaml")["metadata"]["frequency"]
    cop_frequency = load_yaml(FIXTURES / "synthetic-cop-signal2d.yaml")["metadata"]["frequency"]
    assert emg_frequency != cop_frequency


def test_21_negative_wrong_shape() -> None:
    fixture = load_yaml(FIXTURES / "invalid-signal2d-wrong-shape.yaml")
    assert fixture["columns"] != ["time", "x", "y"]


def test_22_unknown_signal_preserved() -> None:
    behavior = load_yaml(SEPARATED_CONTRACT)["assembly_contract"]["unknown_signal_type_behavior"]
    assert "PRESERVE" in behavior


def test_23_orphan_preserved() -> None:
    behavior = load_yaml(SEPARATED_CONTRACT)["assembly_contract"]["orphan_signal_behavior"]
    assert "PRESERVE" in behavior


def test_24_no_same_fs_in_day09_cross_rule() -> None:
    assert "MUST NOT" in load_yaml(SEPARATED_CONTRACT)["upstream"]["cross_day_rule"]


def test_25_fixture_hashes() -> None:
    manifest = json.loads((FIXTURES / "fixture-manifest.json").read_text(encoding="utf-8"))
    for name, entry in manifest.items():
        with (FIXTURES / name).open("rb") as file_obj:
            digest = hashlib.file_digest(file_obj, "sha256").hexdigest()
        assert digest == entry["sha256"]


def test_26_no_clinical_fixture() -> None:
    for path in FIXTURES.glob("*.yaml"):
        assert load_yaml(path).get("clinical_evidence") is False


def test_27_traceability() -> None:
    text = TRACEABILITY.read_text(encoding="utf-8")
    requirements = ["FR-002", "FR-003", "FR-004", "FR-021", "FR-025", "AC-01"]
    for requirement in requirements:
        assert requirement in text


def test_28_no_day17_parser() -> None:
    parser_path = ROOT / "services/signal-ingestion-service/src/adapters/noraxon_separated_csv.py"
    assert not parser_path.exists()


def test_29_day13_deferred() -> None:
    assert "day13" in load_yaml(SIGNAL_CONTRACT)["validation_ownership"]


def test_30_day17_deferred() -> None:
    assert "day17" in load_yaml(SIGNAL_CONTRACT)["validation_ownership"]


def test_31_day09_samefs_semantic_still_present() -> None:
    day09_contract = load_yaml(DAY09_CONTRACT)
    fields = {
        item["name"]: item
        for item in day09_contract["record_metadata"]["known_fields"]
    }
    assert "must not be generalized" in fields["frequency"]["semantic"]


def test_32_raw_patient_disallowed() -> None:
    assert load_yaml(SEPARATED_CONTRACT)["scope"]["raw_patient_data_allowed_in_repository"] is False
