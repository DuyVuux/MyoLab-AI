#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
required=['packages/semg-core/semg_core/quantitative_metrics.py','packages/common-schemas/json/uc2-quantitative-assessment.v0.1.schema.json','services/api-server/src/services/longitudinal_service.py','services/api-server/src/mock_api/day23_app.py','apps/web-portal/src/app/uc2/assessment/Day23UC2AssessmentPage.tsx','apps/web-portal/src/components/uc2/SessionCompatibilityTable.tsx','docs/plans/DAY23_EXECUTION_PLAN.md']
missing=[p for p in required if not(ROOT/p).is_file()]
if missing:print('Thiếu artifact Day 23:',*missing,sep='\n- ',file=sys.stderr);raise SystemExit(1)
for p in required:
 t=(ROOT/p).read_text(encoding='utf-8')
 if any(x in t for x in ['scoreIsProbability:true','clinicalUseAllowed:true','rawSamplesIncluded:true']):print('Safety fail:',p,file=sys.stderr);raise SystemExit(1)
print('Day 23 artifact check passed.')
