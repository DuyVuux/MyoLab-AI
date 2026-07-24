import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]


def test_schemas():
    for rel in [
        'packages/common-schemas/json/longitudinal-compatibility.v0.1.schema.json',
        'packages/common-schemas/json/uc2-quantitative-assessment.v0.1.schema.json',
    ]:
        schema = json.loads((ROOT / rel).read_text(encoding='utf-8'))
        jsonschema.Draft202012Validator.check_schema(schema)
