"""Day 32 — Schema validation tests.

Verifies evidence JSON files conform to their JSON schemas:
  • day32-preflight.v1.schema.json
  • day32-core-gate.v1.schema.json
  • day32-execution-authorization.v1.schema.json
  • day32-synthetic-core-smoke.v1.schema.json
"""
from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "modeling"))

import pytest

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

SCHEMA_DIR = ROOT / "packages" / "common-schemas" / "json"


def _load_schema(name: str) -> dict:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema not installed")
def test_preflight_schema():
    schema = _load_schema("day32-preflight.v1.schema.json")
    valid = {
        "schema_version": "day32-preflight.v1",
        "pass": True,
        "errors": [],
        "sealed_test_opened": False,
        "pooled_training_allowed": False,
    }
    jsonschema.validate(valid, schema)


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema not installed")
def test_preflight_schema_rejects_sealed_test():
    schema = _load_schema("day32-preflight.v1.schema.json")
    invalid = {
        "schema_version": "day32-preflight.v1",
        "pass": True,
        "errors": [],
        "sealed_test_opened": True,  # Must be false
        "pooled_training_allowed": False,
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(invalid, schema)


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema not installed")
def test_core_gate_schema():
    schema = _load_schema("day32-core-gate.v1.schema.json")
    valid = {
        "schema_version": "day32-core-gate.v1",
        "status": "CORE_GATE_PASS",
        "missing_models": [],
        "failed_models": [],
        "optional_models_may_run": True,
    }
    jsonschema.validate(valid, schema)


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema not installed")
def test_schema_files_exist():
    expected = [
        "day32-core-gate.v1.schema.json",
        "day32-execution-authorization.v1.schema.json",
        "day32-preflight.v1.schema.json",
        "day32-synthetic-core-smoke.v1.schema.json",
    ]
    for name in expected:
        assert (SCHEMA_DIR / name).exists(), f"Missing schema: {name}"
