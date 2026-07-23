#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
required=[
 'packages/common-schemas/json/analysis-job.v0.1.schema.json',
 'services/api-server/src/schemas/analysis_job_schema.py',
 'services/api-server/src/services/analysis_job_service.py',
 'services/api-server/src/services/offline_analysis_runtime.py',
 'services/api-server/src/routes/analysis_jobs.py',
 'apps/web-portal/src/schemas/analysis-job.schema.ts',
 'apps/web-portal/src/lib/analysis-client.ts',
 'apps/web-portal/src/components/analysis/AnalysisJobTimeline.tsx',
 'docs/plans/DAY21_EXECUTION_PLAN.md',
]
missing=[x for x in required if not (ROOT/x).is_file()]
if missing:
 print('Thiếu artifact Day 21:',*missing,sep='\n- ',file=sys.stderr); raise SystemExit(1)
for path in required:
 text=(ROOT/path).read_text(encoding='utf-8')
 if path.endswith(('.py','.ts','.tsx','.json')) and any(token in text for token in ['fatigue probability','clinicalUseAllowed: true','rawSamplesIncluded: true']):
  print('Safety token không phù hợp:',path,file=sys.stderr); raise SystemExit(1)
print('Day 21 artifact check passed.')
