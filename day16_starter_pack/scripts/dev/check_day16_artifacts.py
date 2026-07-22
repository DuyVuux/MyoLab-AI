#!/usr/bin/env python3
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
required=[
 'docs/plans/DAY16_EXECUTION_PLAN.md',
 'docs/06-ai-signal-processing/mvp0-regression-and-validation-spec.md',
 'docs/08-validation-qa/day16-golden-regression-test-plan.md',
 'qa-validation/configs/mvp0_regression_v0.1.yaml',
 'qa-validation/evidence/day16-mvp0-regression-report.json',
 'qa-validation/evidence/day16-mvp0-regression-report.md',
 'qa-validation/baselines/mvp0_baseline_v0.1.json',
 'ai-core/validation-reports/analytical_validation_mvp0.md',
 'packages/common-schemas/json/mvp0-regression-report.schema.json',
 'scripts/data/run_mvp0_regression.py',
 'scripts/data/compare_regression_runs.py',
 'scripts/dev/freeze_mvp0_baseline_v0_1.py',
]
missing=[x for x in required if not (ROOT/x).is_file()]
if missing: raise SystemExit('Thiếu artifact:\n'+'\n'.join(missing))
report=json.loads((ROOT/'qa-validation/evidence/day16-mvp0-regression-report.json').read_text(encoding='utf-8'))
baseline=json.loads((ROOT/'qa-validation/baselines/mvp0_baseline_v0.1.json').read_text(encoding='utf-8'))
assert report['passed'] is True
assert report['clinical_validation_status']=='not_validated'
assert baseline['clinical_validation_status']=='not_validated'
assert len(report['scenarios'])==7
for rel in ['docs/plans/DAY16_EXECUTION_PLAN.md','docs/06-ai-signal-processing/mvp0-regression-and-validation-spec.md','docs/08-validation-qa/day16-golden-regression-test-plan.md','ai-core/validation-reports/analytical_validation_mvp0.md']:
    text=(ROOT/rel).read_text(encoding='utf-8').lower()
    if 'clinical validation passed' in text or 'đã được xác nhận lâm sàng' in text:
        raise SystemExit(f'Overclaim trong {rel}')
print('DAY 16 ARTIFACT CHECK: PASS')
