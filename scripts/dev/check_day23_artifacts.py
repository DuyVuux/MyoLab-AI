#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]

required = [
    'packages/semg-core/semg_core/quantitative_metrics.py',
    'packages/common-schemas/json/uc2-quantitative-assessment.v0.1.schema.json',
    'packages/common-schemas/json/longitudinal-compatibility.v0.1.schema.json',
    'services/api-server/src/schemas/uc2_schema.py',
    'services/api-server/src/services/longitudinal_service.py',
    'services/api-server/src/mock_api/day23_app.py',
    'apps/web-portal/src/schemas/uc2-assessment.schema.ts',
    'apps/web-portal/src/lib/uc2-assessment-client.ts',
    'apps/web-portal/src/components/uc2/SessionCompatibilityTable.tsx',
    'apps/web-portal/src/app/(authenticated)/uc2/assessment/[sessionId]/page.tsx',
    'apps/web-portal/src/app/(authenticated)/uc2/longitudinal/[subjectRef]/page.tsx',
    'apps/web-portal/src/app/uc2/assessment/Day23UC2AssessmentPage.tsx',
    'apps/web-portal/src/app/uc2/longitudinal/Day23UC2LongitudinalPage.tsx',
    'apps/web-portal/e2e/day23-uc2-regression.spec.ts',
    'docs/plans/DAY23_EXECUTION_PLAN.md',
]

missing = [p for p in required if not (ROOT / p).is_file()]
if missing:
    print('Thiếu artifact Day 23:', *missing, sep='\n- ', file=sys.stderr)
    raise SystemExit(1)

for p in required:
    text = (ROOT / p).read_text(encoding='utf-8')
    if any(x in text for x in [
        'scoreIsProbability:true',
        'clinicalUseAllowed:true',
        'rawSamplesIncluded:true',
    ]):
        print('Safety fail:', p, file=sys.stderr)
        raise SystemExit(1)


forbidden_ui_sources = [
    'apps/web-portal/src/app/(authenticated)/uc2',
    'apps/web-portal/src/app/uc2',
    'apps/web-portal/src/components/uc2',
]
forbidden_fragments = [
    'Khác biệt so với UC1',
    'Đa chiều',
    'Clinical Focus',
    '📊',
    '📈',
    '🔬',
]

violations = []
for rel in forbidden_ui_sources:
    source = ROOT / rel
    if source.is_file():
        candidates = [source]
    else:
        candidates = [p for p in source.rglob('*') if p.suffix in {'.tsx', '.ts', '.css'}]
    for candidate in candidates:
        text = candidate.read_text(encoding='utf-8')
        for fragment in forbidden_fragments:
            if fragment in text:
                violations.append(f'{candidate.relative_to(ROOT)}: forbidden UI fragment {fragment!r}')

if violations:
    print('Day 23 UI regression fail:', *violations, sep='\n- ', file=sys.stderr)
    raise SystemExit(1)

print('Day 23 artifact/UI check passed.')
