import json
from pathlib import Path
import jsonschema

ROOT=Path(__file__).resolve().parents[2]

def test_analysis_job_schema_is_valid() -> None:
    schema=json.loads((ROOT/'packages/common-schemas/json/analysis-job.v0.1.schema.json').read_text(encoding='utf-8'))
    jsonschema.Draft202012Validator.check_schema(schema)
