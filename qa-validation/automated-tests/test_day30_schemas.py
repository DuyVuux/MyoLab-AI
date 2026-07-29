from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]

EXPECTED_SCHEMAS = {
    "day30-channel-decision.v1.schema.json",
    "day30-common-ontology.v1.schema.json",
    "day30-dataset-view-registry.v1.schema.json",
    "day30-harmonization-run.v1.schema.json",
    "day30-preflight.v1.schema.json",
    "day30-readiness-decision.v1.schema.json",
    "day30-window-index.v1.schema.json",
}


def test_day30_schemas_are_present_strict_and_valid() -> None:
    schema_root = ROOT / "packages/common-schemas/json"
    paths = {
        path.name: path for path in schema_root.glob("day30-*.schema.json")
    }
    assert EXPECTED_SCHEMAS <= set(paths)
    for name in EXPECTED_SCHEMAS:
        schema = json.loads(paths[name].read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        assert schema["$schema"].endswith("2020-12/schema")
        assert schema.get("additionalProperties") is False
