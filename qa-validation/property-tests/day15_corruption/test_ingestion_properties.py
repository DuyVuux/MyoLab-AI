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
HARNESS_PATH = ROOT / "qa-validation/property-tests/day15_corruption/ingestion_property_harness.py"
INVARIANTS = ROOT / "qa-validation/property-tests/day15_corruption/ingestion-invariants.v0.1.yaml"
FIXTURE_ROOT = ROOT / "qa-validation/test-data/synthetic/day15-corruption"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


factory = load_module("day15_factory_for_properties", FACTORY_PATH)
harness = load_module("day15_ingestion_property_harness", HARNESS_PATH)
MANIFEST = json.loads(
    (FIXTURE_ROOT / "fixture-manifest.json").read_text(encoding="utf-8")
)
FIXED = MANIFEST["fixed_fixtures"]


def to_case(item: dict[str, object]):
    return harness.PropertyCase(
        case_id=str(item["fixture_id"]),
        path=FIXTURE_ROOT / str(item["relative_path"]),
        fixture_class=str(item["fixture_class"]),
        mutation=str(item["mutation"]) if item["mutation"] else None,
        expected_status=str(item["expected_status"]),
        expected_reason=(
            str(item["expected_reason"]) if item["expected_reason"] else None
        ),
    )


def test_01_invariant_contract_exists():
    assert INVARIANTS.is_file()


def test_02_four_critical_invariants_are_present():
    payload = yaml.safe_load(INVARIANTS.read_text(encoding="utf-8"))
    names = {item["name"] for item in payload["critical_invariants"]}
    assert names == {
        "RAW_IMMUTABLE",
        "UNKNOWN_UNIT_NEVER_INFERRED",
        "NO_SILENT_CRASH",
        "FAIL_CLOSED",
    }


def test_03_property_contract_is_not_claimed_clinically_validated():
    payload = yaml.safe_load(INVARIANTS.read_text(encoding="utf-8"))
    assert payload["clinical_validation"] is False
    assert payload["production_parser_bound"] is False


@pytest.mark.parametrize("item", FIXED, ids=lambda item: item["fixture_id"])
def test_04_fixed_fixture_obeys_all_safety_properties(item):
    case = to_case(item)
    observation = harness.assert_safety_properties(case, harness.Day15ContractProbe())
    assert observation.final_looking_output is False


def test_05_unknown_unit_is_rejected_without_inference():
    item = next(item for item in FIXED if item["mutation"] == "UNKNOWN_UNIT")
    observation = harness.assert_safety_properties(
        to_case(item),
        harness.Day15ContractProbe(),
    )
    assert observation.reason_code == "UNIT_MISMATCH"
    assert observation.inferred_unit is None


def test_06_mixed_fs_is_accepted_and_rates_remain_distinct():
    item = next(item for item in FIXED if item["mutation"] == "MIXED_FS")
    observation = harness.assert_safety_properties(
        to_case(item),
        harness.Day15ContractProbe(),
    )
    assert observation.status is harness.AdapterStatus.ACCEPTED
    assert len(set(observation.sampling_rates_hz)) > 1


def test_07_utf8_bom_is_accepted():
    item = next(item for item in FIXED if item["mutation"] == "UTF8_BOM")
    observation = harness.assert_safety_properties(
        to_case(item),
        harness.Day15ContractProbe(),
    )
    assert observation.status is harness.AdapterStatus.ACCEPTED


def test_08_missing_value_remains_missing():
    item = next(
        item for item in FIXED if item["mutation"] == "MISSING_VALUE_PRESERVED"
    )
    observation = harness.assert_safety_properties(
        to_case(item),
        harness.Day15ContractProbe(),
    )
    assert observation.missing_values_preserved is True


def test_09_unknown_field_is_preserved_by_probe():
    item = next(
        item for item in FIXED if item["mutation"] == "UNKNOWN_FIELD_PRESERVED"
    )
    observation = harness.assert_safety_properties(
        to_case(item),
        harness.Day15ContractProbe(),
    )
    assert observation.unknown_fields_preserved is True


def _materialize_case(tmp_path: Path, case: dict[str, object], index: int) -> Path:
    mutation = factory.Mutation(str(case["mutation"]))
    rng = random.Random(int(case["seed"]) + index)
    if mutation in {
        factory.Mutation.UNKNOWN_UNIT,
        factory.Mutation.SIGNAL_2D_WRONG_SHAPE,
        factory.Mutation.MIXED_FS,
    }:
        path = tmp_path / f"case-{index:04d}.yaml"
        payload = factory.build_logical_fixture(mutation, rng)
        path.write_text(
            yaml.safe_dump(payload, sort_keys=False),
            encoding="utf-8",
        )
        return path
    path = tmp_path / f"case-{index:04d}.csv"
    payload = factory.mutate_single_csv(factory.BASE_SINGLE_CSV, mutation, rng)
    path.write_bytes(payload)
    return path


def test_10_constrained_property_cases_obey_invariants(tmp_path):
    cases = factory.generate_property_cases(seed=20260810, count=128)
    adapter = harness.Day15ContractProbe()
    for index, item in enumerate(cases):
        path = _materialize_case(tmp_path, item, index)
        case = harness.PropertyCase(
            case_id=str(item["case_id"]),
            path=path,
            fixture_class=str(item["fixture_class"]),
            mutation=str(item["mutation"]),
            expected_status=str(item["expected_status"]),
            expected_reason=(
                str(item["expected_reason"]) if item["expected_reason"] else None
            ),
        )
        observation = harness.assert_safety_properties(case, adapter)
        assert observation.final_looking_output is False


def test_11_deterministic_replay_returns_same_observation():
    adapter = harness.Day15ContractProbe()
    for item in FIXED:
        case = to_case(item)
        first = harness.assert_safety_properties(case, adapter)
        second = harness.assert_safety_properties(case, adapter)
        assert first == second


def test_12_fail_closed_invalids_never_return_accepted():
    adapter = harness.Day15ContractProbe()
    invalid = [
        item
        for item in FIXED
        if item["fixture_class"] == "INVALID_MUST_FAIL_CLOSED"
    ]
    for item in invalid:
        observation = harness.assert_safety_properties(to_case(item), adapter)
        assert observation.status is harness.AdapterStatus.REJECTED
        assert observation.final_looking_output is False


def test_13_valid_edges_are_not_false_blocked():
    adapter = harness.Day15ContractProbe()
    valid = [
        item
        for item in FIXED
        if item["fixture_class"] in {"VALID_EDGE_MUST_ACCEPT", "GOLDEN_CONTROL"}
    ]
    for item in valid:
        observation = harness.assert_safety_properties(to_case(item), adapter)
        assert observation.status is harness.AdapterStatus.ACCEPTED


def test_14_raw_hash_does_not_change_after_repeated_probe():
    adapter = harness.Day15ContractProbe()
    for item in FIXED:
        path = FIXTURE_ROOT / item["relative_path"]
        before = harness.sha256_file(path)
        for _ in range(5):
            adapter.ingest(path)
        assert harness.sha256_file(path) == before


class ExplodingAdapter:
    def ingest(self, path: Path):
        raise RuntimeError(f"unexpected raw exception for {path.name}")


def test_15_unhandled_exception_is_detected_as_no_silent_crash_violation():
    case = to_case(FIXED[0])
    with pytest.raises(AssertionError, match="NO_SILENT_CRASH"):
        harness.assert_safety_properties(case, ExplodingAdapter())


class MutatingAdapter:
    def ingest(self, path: Path):
        path.write_bytes(path.read_bytes() + b"X")
        return harness.SafetyObservation(
            status=harness.AdapterStatus.REJECTED,
            reason_code="INGEST_SCHEMA_ERROR",
            final_looking_output=False,
        )


def test_16_source_mutation_is_detected(tmp_path):
    path = tmp_path / "copy.csv"
    path.write_bytes(factory.BASE_SINGLE_CSV)
    case = harness.PropertyCase(
        case_id="MUTATION-DETECTION",
        path=path,
        fixture_class="INVALID_MUST_FAIL_CLOSED",
        mutation="MALFORMED_HEADER",
        expected_status="REJECTED",
        expected_reason=None,
    )
    with pytest.raises(AssertionError, match="RAW_IMMUTABLE"):
        harness.assert_safety_properties(case, MutatingAdapter())


class FalseSuccessAdapter:
    def ingest(self, path: Path):
        return harness.SafetyObservation(
            status=harness.AdapterStatus.ACCEPTED,
            reason_code=None,
            final_looking_output=True,
        )


def test_17_invalid_input_false_success_is_detected():
    item = next(
        item
        for item in FIXED
        if item["fixture_class"] == "INVALID_MUST_FAIL_CLOSED"
    )
    with pytest.raises(AssertionError, match="FAIL_CLOSED"):
        harness.assert_safety_properties(to_case(item), FalseSuccessAdapter())


class UnitGuessingAdapter:
    def ingest(self, path: Path):
        return harness.SafetyObservation(
            status=harness.AdapterStatus.REJECTED,
            reason_code="UNIT_MISMATCH",
            final_looking_output=False,
            inferred_unit="uV",
        )


def test_18_unknown_unit_guessing_is_detected():
    item = next(item for item in FIXED if item["mutation"] == "UNKNOWN_UNIT")
    with pytest.raises(AssertionError, match="UNKNOWN_UNIT_NEVER_INFERRED"):
        harness.assert_safety_properties(to_case(item), UnitGuessingAdapter())


def test_19_binary_garbage_does_not_escape_as_unhandled_exception():
    item = next(item for item in FIXED if item["mutation"] == "BINARY_GARBAGE")
    observation = harness.assert_safety_properties(
        to_case(item),
        harness.Day15ContractProbe(),
    )
    assert observation.reason_code == "INGEST_SCHEMA_ERROR"


def test_20_property_harness_has_no_model_or_training_dependency():
    text = HARNESS_PATH.read_text(encoding="utf-8").lower()
    for token in ("torch", "tensorflow", "sklearn", ".fit(", "onnx"):
        assert token not in text


def test_21_invariant_yaml_explicitly_defers_production_parser():
    text = INVARIANTS.read_text(encoding="utf-8")
    assert "DAY16/DAY17" in text
    assert "production MR4 single CSV parser implementation" in text


def test_22_invariant_yaml_maps_raw_immutability_to_nfr003():
    payload = yaml.safe_load(INVARIANTS.read_text(encoding="utf-8"))
    raw = next(
        item
        for item in payload["critical_invariants"]
        if item["name"] == "RAW_IMMUTABLE"
    )
    assert "NFR-003" in raw["requirement_links"]


def test_23_invariant_yaml_maps_fail_closed_to_nfr012():
    payload = yaml.safe_load(INVARIANTS.read_text(encoding="utf-8"))
    closed = next(
        item
        for item in payload["critical_invariants"]
        if item["name"] == "FAIL_CLOSED"
    )
    assert "NFR-012" in closed["requirement_links"]


def test_24_invariant_yaml_requires_heterogeneous_fs_support():
    payload = yaml.safe_load(INVARIANTS.read_text(encoding="utf-8"))
    names = {item["name"] for item in payload["boundary_invariants"]}
    assert "HETEROGENEOUS_FS_ALLOWED" in names


def test_25_no_ood_or_ssl_capability_is_added_on_day15():
    text = INVARIANTS.read_text(encoding="utf-8").lower()
    assert "ood detector" in text
    assert "model training" in text
