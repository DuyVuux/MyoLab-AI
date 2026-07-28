from __future__ import annotations
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core"))

from jsonschema import Draft202012Validator


def test_all_schemas_are_valid():
    for path in (ROOT/"packages/common-schemas/json").glob("*.schema.json"):
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue  # skip legacy empty stubs from prior days
        schema = json.loads(content)
        Draft202012Validator.check_schema(schema)
