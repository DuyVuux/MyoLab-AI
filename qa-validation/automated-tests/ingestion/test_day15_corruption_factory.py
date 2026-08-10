from __future__ import annotations

import importlib.util
import json
import random
import sys
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[3]
FACTORY_PATH = (
    ROOT
    / "qa-validation/test-data/synthetic/generators/noraxon_corruption_factory.py"
)
STATIC_FIXTURES = ROOT / "qa-validation/test-data/synthetic/day15-corruption"


def load_module():
    spec = importlib.util.spec_from_file_location("day15_corruption_factory", FACTORY_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def mod():
    return load_module()


def test_01_factory_exists():
    assert FACTORY_PATH.is_file()


def test_02_factory_version_is_pinned(mod):
    assert mod.FACTORY_VERSION == "day15-noraxon-corruption-factory.v0.1.0"


def test_03_fixed_catalog_contains_required_roadmap_mutations(mod):
    mutations = {item[0] for item in mod._fixed_specifications() if item[0]}
    required = {
        mod.Mutation.MALFORMED_HEADER,
        mod.Mutation.COUNT_MISMATCH,
        mod.Mutation.DUPLICATE_TIMESTAMP,
        mod.Mutation.OUT_OF_ORDER_TIMESTAMP,
        mod.Mutation.MISSING_ROW,
        mod.Mutation.UNKNOWN_UNIT,
        mod.Mutation.MIXED_FS,
        mod.Mutation.UTF8_BOM,
        mod.Mutation.SIGNAL_2D_WRONG_SHAPE,
    }
    assert required <= mutations


def test_04_mixed_fs_is_valid_edge_not_corruption(mod):
    lookup = {item[0]: item[1] for item in mod._fixed_specifications()}
    assert lookup[mod.Mutation.MIXED_FS] is mod.FixtureClass.VALID_EDGE_MUST_ACCEPT


def test_05_utf8_bom_is_valid_edge_not_corruption(mod):
    lookup = {item[0]: item[1] for item in mod._fixed_specifications()}
    assert lookup[mod.Mutation.UTF8_BOM] is mod.FixtureClass.VALID_EDGE_MUST_ACCEPT


def test_06_source_bytes_never_mutated_in_memory(mod):
    source = bytes(mod.BASE_SINGLE_CSV)
    before = mod.sha256_bytes(source)
    _ = mod.mutate_single_csv(
        source,
        mod.Mutation.COUNT_MISMATCH,
        random.Random(15),
    )
    assert mod.sha256_bytes(source) == before


def test_07_source_seed_file_never_mutated(mod, tmp_path):
    seed = tmp_path / "seed.csv"
    seed.write_bytes(mod.BASE_SINGLE_CSV)
    before = mod.sha256_file(seed)
    output = tmp_path / "generated"
    mod.generate_fixed_fixtures(
        output,
        overwrite=True,
        single_seed_path=seed,
    )
    assert mod.sha256_file(seed) == before


def test_08_same_seed_generates_same_manifest(mod, tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    one = mod.build_package_fixture_set(first, seed=1501, overwrite=True)
    two = mod.build_package_fixture_set(second, seed=1501, overwrite=True)
    normalized_one = [
        {key: value for key, value in item.items() if key != "relative_path"}
        for item in one["fixed_fixtures"]
    ]
    normalized_two = [
        {key: value for key, value in item.items() if key != "relative_path"}
        for item in two["fixed_fixtures"]
    ]
    assert normalized_one == normalized_two
    assert one["property_cases_sha256"] == two["property_cases_sha256"]


def test_09_property_case_generation_is_deterministic(mod):
    first = mod.generate_property_cases(seed=99, count=50)
    second = mod.generate_property_cases(seed=99, count=50)
    assert first == second


def test_10_invalid_property_case_count_is_typed_failure(mod):
    with pytest.raises(mod.FactoryError, match=">= 1"):
        mod.generate_property_cases(seed=1, count=0)


def test_11_output_path_traversal_is_rejected(mod, tmp_path):
    with pytest.raises(mod.FactoryError, match="escapes"):
        mod._safe_output_path(tmp_path / "safe", "../escape.csv")


def test_12_overwrite_guard_is_fail_closed(mod, tmp_path):
    output = tmp_path / "out"
    mod.build_package_fixture_set(output, overwrite=True)
    with pytest.raises(mod.FactoryError, match="refusing to overwrite"):
        mod.build_package_fixture_set(output, overwrite=False)


def test_13_malformed_header_changes_header_value_arity(mod):
    payload = mod.mutate_single_csv(
        mod.BASE_SINGLE_CSV,
        mod.Mutation.MALFORMED_HEADER,
        random.Random(1),
    )
    rows = mod._csv_rows(payload)
    assert len(rows[0]) != len(rows[1])


def test_14_count_mismatch_changes_declared_count(mod):
    payload = mod.mutate_single_csv(
        mod.BASE_SINGLE_CSV,
        mod.Mutation.COUNT_MISMATCH,
        random.Random(1),
    )
    rows = mod._csv_rows(payload)
    count_index = rows[0].index("count")
    assert int(rows[1][count_index]) != len(rows[4:])


def test_15_duplicate_timestamp_is_created(mod):
    payload = mod.mutate_single_csv(
        mod.BASE_SINGLE_CSV,
        mod.Mutation.DUPLICATE_TIMESTAMP,
        random.Random(1),
    )
    rows = mod._csv_rows(payload)
    assert rows[4][0] == rows[5][0]


def test_16_out_of_order_timestamp_is_created(mod):
    payload = mod.mutate_single_csv(
        mod.BASE_SINGLE_CSV,
        mod.Mutation.OUT_OF_ORDER_TIMESTAMP,
        random.Random(1),
    )
    rows = mod._csv_rows(payload)
    assert float(rows[5][0]) < float(rows[4][0])


def test_17_missing_row_preserves_declared_count(mod):
    payload = mod.mutate_single_csv(
        mod.BASE_SINGLE_CSV,
        mod.Mutation.MISSING_ROW,
        random.Random(1),
    )
    rows = mod._csv_rows(payload)
    count_index = rows[0].index("count")
    assert int(rows[1][count_index]) > len(rows[4:])


def test_18_utf8_bom_is_present(mod):
    payload = mod.mutate_single_csv(
        mod.BASE_SINGLE_CSV,
        mod.Mutation.UTF8_BOM,
        random.Random(1),
    )
    assert payload.startswith(b"\xef\xbb\xbf")


def test_19_missing_value_is_not_interpolated(mod):
    payload = mod.mutate_single_csv(
        mod.BASE_SINGLE_CSV,
        mod.Mutation.MISSING_VALUE_PRESERVED,
        random.Random(1),
    )
    rows = mod._csv_rows(payload)
    assert rows[5][3] == ""


def test_20_unknown_fields_are_present_for_preservation_test(mod):
    payload = mod.mutate_single_csv(
        mod.BASE_SINGLE_CSV,
        mod.Mutation.UNKNOWN_FIELD_PRESERVED,
        random.Random(1),
    )
    rows = mod._csv_rows(payload)
    assert "future_vendor_field" in rows[0]
    assert "FutureSensor-A" in rows[3]


def test_21_unknown_unit_literal_is_preserved_not_normalized(mod):
    payload = mod.build_logical_fixture(mod.Mutation.UNKNOWN_UNIT, random.Random(3))
    assert payload["metadata"]["units"] not in mod.KNOWN_UNITS


def test_22_signal_2d_wrong_shape_is_actually_wrong(mod):
    payload = mod.build_logical_fixture(
        mod.Mutation.SIGNAL_2D_WRONG_SHAPE,
        random.Random(3),
    )
    assert payload["metadata"]["type"] == "signal_2d"
    assert payload["columns"] != ["time", "x", "y"]


def test_23_mixed_fs_contains_distinct_sampling_rates(mod):
    payload = mod.build_logical_fixture(mod.Mutation.MIXED_FS, random.Random(3))
    rates = [signal["metadata"]["frequency"] for signal in payload["signals"]]
    assert len(set(rates)) == 2


def test_24_binary_garbage_is_not_utf8_csv(mod):
    payload = mod.mutate_single_csv(
        mod.BASE_SINGLE_CSV,
        mod.Mutation.BINARY_GARBAGE,
        random.Random(1),
    )
    with pytest.raises(UnicodeDecodeError):
        payload.decode("utf-8")


def test_25_static_fixture_manifest_exists():
    assert (STATIC_FIXTURES / "fixture-manifest.json").is_file()


def test_26_static_fixture_manifest_is_synthetic_only():
    payload = json.loads(
        (STATIC_FIXTURES / "fixture-manifest.json").read_text(encoding="utf-8")
    )
    assert payload["data_class"] == "SYNTHETIC_ONLY"
    assert payload["clinical_evidence"] is False
    assert payload["site_verified"] is False


def test_27_static_fixture_manifest_does_not_claim_parser_binding():
    payload = json.loads(
        (STATIC_FIXTURES / "fixture-manifest.json").read_text(encoding="utf-8")
    )
    assert payload["production_parser_bound"] is False


def test_28_static_fixture_hashes_match():
    payload = json.loads(
        (STATIC_FIXTURES / "fixture-manifest.json").read_text(encoding="utf-8")
    )
    for item in payload["fixed_fixtures"]:
        path = STATIC_FIXTURES / item["relative_path"]
        with path.open("rb") as file_obj:
            digest = __import__("hashlib").file_digest(file_obj, "sha256").hexdigest()
        assert digest == item["sha256"]


def test_29_every_invalid_fixed_fixture_has_reason():
    payload = json.loads(
        (STATIC_FIXTURES / "fixture-manifest.json").read_text(encoding="utf-8")
    )
    invalid = [
        item
        for item in payload["fixed_fixtures"]
        if item["fixture_class"] == "INVALID_MUST_FAIL_CLOSED"
    ]
    assert invalid
    assert all(item["expected_reason"] for item in invalid)


def test_30_no_fixed_fixture_is_clinical_evidence():
    payload = json.loads(
        (STATIC_FIXTURES / "fixture-manifest.json").read_text(encoding="utf-8")
    )
    assert all(item["clinical_evidence"] is False for item in payload["fixed_fixtures"])
    assert all(item["site_verified"] is False for item in payload["fixed_fixtures"])


def test_31_factory_has_no_training_dependencies():
    text = FACTORY_PATH.read_text(encoding="utf-8").lower()
    for token in ("torch", "tensorflow", "sklearn", ".fit(", "xgboost"):
        assert token not in text


def test_32_factory_does_not_implement_production_parser():
    text = FACTORY_PATH.read_text(encoding="utf-8")
    assert "production MR4 parser" in text or "production MR4" in text
    assert "class MR4Parser" not in text


def test_33_factory_uses_local_rng_not_global_random_state():
    text = FACTORY_PATH.read_text(encoding="utf-8")
    assert "random.Random(seed)" in text
    assert "random.seed(" not in text


def test_34_generation_report_explicitly_says_no_patient_data():
    payload = json.loads(
        (STATIC_FIXTURES / "generation-report.json").read_text(encoding="utf-8")
    )
    assert payload["patient_data_used"] is False
    assert payload["training_executed"] is False


def test_35_logical_yaml_fixtures_parse_cleanly():
    for path in sorted(STATIC_FIXTURES.rglob("*.yaml")):
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(payload, dict)
