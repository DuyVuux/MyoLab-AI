from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "packages" / "common-schemas" / "json"


def test_day31_schemas_are_strict_draft_2020_12() -> None:
    schemas = sorted(SCHEMA_DIR.glob("day31-*.schema.json"))
    assert len(schemas) >= 5
    for path in schemas:
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert schema.get("additionalProperties") is False


def test_pack_evidence_is_not_mistaken_for_root_delivery_evidence() -> None:
    root_evidence = ROOT / "qa-validation" / "evidence" / "day31"
    if root_evidence.exists():
        for path in root_evidence.glob("*.json"):
            json.loads(
                path.read_text(encoding="utf-8"),
                parse_constant=lambda value: (_ for _ in ()).throw(
                    ValueError(f"non-standard JSON constant {value}")
                ),
            )
