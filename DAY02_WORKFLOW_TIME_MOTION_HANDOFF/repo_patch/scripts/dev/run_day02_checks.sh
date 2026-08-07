#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
export PYTHONDONTWRITEBYTECODE=1

printf '%s\n' '[DAY02] 1/4 Validate workflow/time-motion contracts'
python scripts/dev/validate_day02_workflow_time_motion.py > /tmp/day02_validate.json
cat /tmp/day02_validate.json

python - <<'PY'
import json
from pathlib import Path
root=Path.cwd()
report={
  'version':'0.1','day':'DAY02','status':'PENDING_VALIDATION',
  'meaning':'DAY02 validation is in progress; no baseline is claimed.',
  'tests_expected':20,'tests_passed':0,'pytest_return_code':None,
  'mandatory_roadmap_outputs':3,'traceability_items':13,
  'baseline_measured':False,'sixty_minute_value_status':'TEAM_ESTIMATE_NOT_BASELINE',
  'fifty_percent_target_status':'RESEARCH_TARGET_NOT_COMMITTED',
  'key_open_questions_closed':0,'training_executed':False,'raw_patient_data_read':False,
  'synthetic_fixture_baseline_eligible':False,
  'mfcv_site_eligibility':'NOT_VERIFIED','knee_algorithm_authorized':False,
  'validation_failures':[],
}
(root/'qa-validation/evidence/day02-validation-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
PY

printf '%s\n' '[DAY02] 2/4 Run 20 governance tests'
set +e
PYTEST_OUTPUT="$(pytest -q qa-validation/automated-tests/governance/test_day02_workflow_time_motion.py -p no:cacheprovider 2>&1)"
PYTEST_RC=$?
set -e
printf '%s\n' "$PYTEST_OUTPUT"

printf '%s\n' '[DAY02] 3/4 Finalize validation report'
python - "$PYTEST_RC" "$PYTEST_OUTPUT" <<'PY'
import json, re, sys
from pathlib import Path
root=Path.cwd(); rc=int(sys.argv[1]); out=sys.argv[2]
m=re.search(r'(\d+) passed', out); passed=int(m.group(1)) if m else 0
report={
  'version':'0.1','day':'DAY02',
  'status':'GO_FOR_DAY_03' if rc==0 and passed==20 else 'BLOCKED_WITH_EVIDENCE',
  'meaning':'Measurement design is ready for controlled DAY03 observation; no MotionLab baseline is claimed.',
  'tests_expected':20,'tests_passed':passed,'pytest_return_code':rc,
  'mandatory_roadmap_outputs':3,'traceability_items':13,
  'baseline_measured':False,'sixty_minute_value_status':'TEAM_ESTIMATE_NOT_BASELINE',
  'fifty_percent_target_status':'RESEARCH_TARGET_NOT_COMMITTED',
  'key_open_questions_closed':0,'training_executed':False,'raw_patient_data_read':False,
  'synthetic_fixture_baseline_eligible':False,
  'mfcv_site_eligibility':'NOT_VERIFIED','knee_algorithm_authorized':False,
  'validation_failures':[] if rc==0 and passed==20 else [out],
}
(root/'qa-validation/evidence/day02-validation-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if report['status']!='GO_FOR_DAY_03': raise SystemExit(2)
PY

printf '%s\n' '[DAY02] 4/4 Verify static artifact manifest'
python scripts/dev/check_day02_artifacts.py
printf '%s\n' '[DAY02] PASS — GO_FOR_DAY_03'
