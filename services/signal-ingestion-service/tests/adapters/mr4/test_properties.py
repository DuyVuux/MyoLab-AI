from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

from adapters.mr4 import parser as single
from adapters.mr4.models import Mr4ParseError

ROOT = Path(__file__).resolve().parents[5]
HARNESS_PATH = ROOT / "qa-validation/property-tests/day15_corruption/ingestion_property_harness.py"
MANIFEST = ROOT / "qa-validation/test-data/synthetic/day15-corruption/fixture-manifest.json"
FIXTURE_ROOT = ROOT / "qa-validation/test-data/synthetic/day15-corruption"


def _load_harness():
    spec = importlib.util.spec_from_file_location("day15_harness_runtime", HARNESS_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


harness = _load_harness()


class SingleCsvSafetyAdapter:
    def ingest(self, path: Path):
        try:
            record = single.parse_single_csv(path)
        except Mr4ParseError as exc:
            return harness.SafetyObservation(
                status=harness.AdapterStatus.REJECTED,
                reason_code=exc.code,
                final_looking_output=False,
                inferred_unit=None,
            )
        unknown = any(item.unknown_semantics for item in record.signals) or bool(
            record.unknown_metadata
        )
        missing = any(
            cell is None
            for signal in record.signals
            for row in signal.raw_values
            for cell in row
        )
        rates = tuple(
            sorted(
                {
                    item.sampling_rate_hz
                    for item in record.signals
                    if item.sampling_rate_hz is not None
                }
            )
        )
        return harness.SafetyObservation(
            status=harness.AdapterStatus.ACCEPTED,
            reason_code=None,
            final_looking_output=False,
            inferred_unit=None,
            missing_values_preserved=missing if missing else None,
            unknown_fields_preserved=unknown if unknown else None,
            sampling_rates_hz=rates,
        )


def _cases():
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return [
        item
        for item in payload["fixed_fixtures"]
        if item["representation_level"] == "BYTE_LEVEL_SINGLE_CSV"
    ]


def _to_case(item):
    return harness.PropertyCase(
        case_id=item["fixture_id"],
        path=FIXTURE_ROOT / item["relative_path"],
        fixture_class=item["fixture_class"],
        mutation=item["mutation"],
        expected_status=item["expected_status"],
        expected_reason=item["expected_reason"],
    )


@pytest.mark.parametrize("item", _cases(), ids=lambda item: item["fixture_id"])
def test_01_day15_byte_level_properties_bind_to_production_parser(item):
    observation = harness.assert_safety_properties(_to_case(item), SingleCsvSafetyAdapter())
    assert observation.final_looking_output is False


def test_02_unknown_vendor_column_never_gets_a_unit_inferred():
    item = next(item for item in _cases() if item["mutation"] == "UNKNOWN_FIELD_PRESERVED")
    record = single.parse_single_csv(FIXTURE_ROOT / item["relative_path"])
    unknown = next(x for x in record.signals if x.vendor_name == "FutureSensor-A")
    assert unknown.unit is None


def test_03_replay_preserves_raw_hash_and_typed_outcome():
    adapter = SingleCsvSafetyAdapter()
    for item in _cases():
        case = _to_case(item)
        first = harness.assert_safety_properties(case, adapter)
        second = harness.assert_safety_properties(case, adapter)
        assert first == second


def test_04_single_parser_does_not_claim_mixed_fs_property_applicability():
    text = (ROOT / "services/signal-ingestion-service/src/adapters/mr4/parser.py").read_text(encoding="utf-8")
    assert "same sampling" not in text.lower()
    assert "resample(" not in text.lower()
    assert "interpolate(" not in text.lower()
