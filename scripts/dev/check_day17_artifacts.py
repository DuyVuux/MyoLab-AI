#!/usr/bin/env python3
from pathlib import Path
import json,yaml
ROOT=Path(__file__).resolve().parents[2]
required=[
 'openapi.yaml','docs/04-api/openapi-v0.1.yaml','docs/04-api/api-overview.md','docs/04-api/offline-analysis-api-contract.md','docs/04-api/api-error-taxonomy.md',
 'docs/05-data/session-analysis-summary-contract.md','packages/common-schemas/json/session-analysis-summary.schema.json','packages/common-schemas/json/analysis-job.schema.json',
 'services/api-server/src/schemas/analysis_contract.py','scripts/data/build_analysis_api_summary.py','scripts/dev/validate_openapi_contract.py',
 'qa-validation/evidence/day17-golden-api-summary.json','qa-validation/evidence/day17-abstained-api-summary.json'
]
missing=[x for x in required if not (ROOT/x).is_file()]
if missing: raise SystemExit('Thiếu artifact:\n'+'\n'.join(missing))
if (ROOT/'openapi.yaml').read_bytes()!=(ROOT/'docs/04-api/openapi-v0.1.yaml').read_bytes():
    raise SystemExit('Root openapi.yaml chưa đồng bộ với canonical source')
for rel in ['qa-validation/evidence/day17-golden-api-summary.json','qa-validation/evidence/day17-abstained-api-summary.json']:
    p=json.loads((ROOT/rel).read_text(encoding='utf-8'))
    assert p['safety']['clinical_use_allowed'] is False
    assert p['safety']['human_review_required'] is True
    assert p['confidence']['score_is_probability'] is False
    text=json.dumps(p,ensure_ascii=False).lower()
    for token in ['patient_name','mrn','raw_samples','samples_uv']:
        if token in text: raise SystemExit(f'Forbidden token {token} trong {rel}')
print('DAY 17 ARTIFACT CHECK: PASS')
