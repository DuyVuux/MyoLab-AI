import json
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[2]

def test_all_json_schemas_are_valid():
    for p in (ROOT/'packages/common-schemas/json').glob('*.schema.json'):
        Draft202012Validator.check_schema(json.loads(p.read_text(encoding='utf-8')))
