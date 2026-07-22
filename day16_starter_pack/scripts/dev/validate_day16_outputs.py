#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[2]
report=json.loads((ROOT/'qa-validation/evidence/day16-mvp0-regression-report.json').read_text(encoding='utf-8'))
schema=json.loads((ROOT/'packages/common-schemas/json/mvp0-regression-report.schema.json').read_text(encoding='utf-8'))
errors=sorted(Draft202012Validator(schema).iter_errors(report),key=lambda e:list(e.path))
if errors:
    for e in errors: print('/'.join(map(str,e.path)),e.message)
    raise SystemExit(1)
if report['clinical_validation_status']!='not_validated': raise SystemExit('clinical_validation_status sai')
if report['passed'] is not True: raise SystemExit('report chưa PASS')
print('DAY 16 OUTPUT SCHEMA: PASS')
