#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[2]
items=[
 ('qa-validation/evidence/day17-golden-api-summary.json','packages/common-schemas/json/session-analysis-summary.schema.json'),
 ('qa-validation/evidence/day17-abstained-api-summary.json','packages/common-schemas/json/session-analysis-summary.schema.json'),
 ('docs/04-api/examples/session-import.response.json','packages/common-schemas/json/session-import-response.schema.json'),
 ('docs/04-api/examples/analysis-job.response.json','packages/common-schemas/json/analysis-job.schema.json'),
 ('docs/04-api/examples/problem-details.response.json','packages/common-schemas/json/problem-details.schema.json'),
]
for data_rel,schema_rel in items:
    data=json.loads((ROOT/data_rel).read_text(encoding='utf-8'))
    schema=json.loads((ROOT/schema_rel).read_text(encoding='utf-8'))
    errors=list(Draft202012Validator(schema).iter_errors(data))
    if errors:
        for e in errors: print(data_rel,'/'.join(map(str,e.path)),e.message)
        raise SystemExit(1)
print('DAY 17 JSON SCHEMAS: PASS')
