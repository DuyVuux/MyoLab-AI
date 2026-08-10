from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
CONTRACT_PATH = ROOT / "data-platform/contracts/noraxon/mr4-single-csv.schema.yaml"
EXAMPLES_PATH = ROOT / "data-platform/contracts/noraxon/mr4-single-csv-examples.md"
FIXTURES = ROOT / "qa-validation/test-data/golden/noraxon/single_csv"
TRACEABILITY = ROOT / "qa-validation/traceability/day09-requirement-traceability.csv"


def load_contract() -> dict[str, Any]:
    return yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))


def fixture_matches_minimal_anatomy(name: str) -> bool:
    lines = (FIXTURES / name).read_text(encoding="utf-8-sig").splitlines()
    if len(lines) < 4 or lines[2].strip() != "":
        return False

    metadata_header = next(csv.reader([lines[0]]))
    metadata_values = next(csv.reader([lines[1]]))
    data_header = next(csv.reader([lines[3]]))
    return len(metadata_header) == len(metadata_values) and "time" in data_header


def test_01_mandatory_contract_exists() -> None:
    assert CONTRACT_PATH.is_file()


def test_02_examples_exists() -> None:
    assert EXAMPLES_PATH.is_file()


def test_03_readme_exists() -> None:
    assert (FIXTURES / "README.md").is_file()


def test_04_yaml_parses() -> None:
    assert load_contract()["contract_id"] == "MR4_SINGLE_CSV_V0_1"


def test_05_no_production_parser_scope() -> None:
    assert load_contract()["scope"]["production_parser_in_scope"] is False


def test_06_layout_rows() -> None:
    layout = load_contract()["layout"]
    actual = [
        layout["row_1"],
        layout["row_2"],
        layout["row_3"],
        layout["row_4"],
        layout["row_5_plus"],
    ]
    expected = [
        "metadata_header",
        "metadata_values",
        "blank_separator",
        "data_header",
        "time_series_rows",
    ]
    assert actual == expected


def test_07_blank_separator_required() -> None:
    assert load_contract()["layout"]["blank_separator_required_by_observed_contract"] is True


def test_08_time_required() -> None:
    assert "time" in load_contract()["data_columns"]["required"]


def test_09_known_metadata() -> None:
    names = {item["name"] for item in load_contract()["record_metadata"]["known_fields"]}
    required = {"type", "begin_time", "frequency", "count", "measurement_date", "record_name"}
    assert required <= names


def test_10_fr021_versions() -> None:
    names = {item["name"] for item in load_contract()["record_metadata"]["known_fields"]}
    assert {"created with version", "exported with version"} <= names


def test_11_unknown_metadata_preserved() -> None:
    assert "PRESERVE" in load_contract()["record_metadata"]["unknown_field_policy"]


def test_12_unknown_columns_preserved() -> None:
    assert "PRESERVE" in load_contract()["data_columns"]["unknown_column_policy"]


def test_13_force_semantics_not_overclaimed() -> None:
    semantics = " ".join(
        item["semantic"] for item in load_contract()["data_columns"]["known_groups"]
    )
    assert "NOT_VERIFIED" in semantics


def test_14_same_fs_not_global() -> None:
    fields = {
        item["name"]: item
        for item in load_contract()["record_metadata"]["known_fields"]
    }
    assert "must not be generalized" in fields["frequency"]["semantic"]


def test_15_tech_delta_unchanged() -> None:
    assert load_contract()["technology_augmentation"]["status"] == "UNCHANGED"


def test_16_valid_minimal_anatomy() -> None:
    assert fixture_matches_minimal_anatomy("valid_minimal.csv")


def test_17_valid_unknown_anatomy() -> None:
    assert fixture_matches_minimal_anatomy("valid_unknown_fields.csv")


def test_18_negative_separator_rejected() -> None:
    assert not fixture_matches_minimal_anatomy("invalid_missing_blank_separator.csv")


def test_19_fixture_manifest_hashes() -> None:
    manifest = json.loads((FIXTURES / "fixture-manifest.json").read_text(encoding="utf-8"))
    for name, entry in manifest.items():
        with (FIXTURES / name).open("rb") as file_obj:
            digest = hashlib.file_digest(file_obj, "sha256").hexdigest()
        assert digest == entry["sha256"]


def test_20_fixture_nonclinical() -> None:
    manifest = json.loads((FIXTURES / "fixture-manifest.json").read_text(encoding="utf-8"))
    assert all(not entry["clinical_evidence"] for entry in manifest.values())


def test_21_no_direct_identifier_tokens() -> None:
    fixture_text = "".join(
        path.read_text(encoding="utf-8") for path in FIXTURES.glob("*.csv")
    ).lower()
    assert "patient_name" not in fixture_text
    assert "mrn" not in fixture_text
    assert "@" not in fixture_text


def test_22_traceability_requirements() -> None:
    traceability_text = TRACEABILITY.read_text(encoding="utf-8")
    for requirement in ["FR-001", "FR-003", "FR-004", "FR-021", "AC-01"]:
        assert requirement in traceability_text


def test_23_no_day16_parser_file() -> None:
    parser_path = ROOT / "services/signal-ingestion-service/src/adapters/noraxon_single_csv.py"
    assert not parser_path.exists()


def test_24_deferred_day13_explicit() -> None:
    assert "deferred_to_day13" in load_contract()["validation_contract"]


def test_25_deferred_day16_explicit() -> None:
    assert "deferred_to_day16" in load_contract()["validation_contract"]


def test_26_raw_patient_disallowed() -> None:
    assert load_contract()["scope"]["raw_patient_data_allowed_in_repository"] is False


def test_27_bom_policy() -> None:
    assert "utf-8-sig" in load_contract()["encoding"]["accepted"]


def test_28_examples_synthetic_boundary() -> None:
    text = EXAMPLES_PATH.read_text(encoding="utf-8").lower()
    assert "synthetic contract fixture" in text


def test_29_safety_invariants_present() -> None:
    assert len(load_contract()["safety_invariants"]) >= 5


def test_30_status_rule() -> None:
    assert load_contract()["day_status_rule"]["pass"] == "GO_FOR_DAY_10"
