#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
for f in \
  services/api-server/src/mock_api/day20_app.py \
  apps/web-portal/src/schemas/analysis-envelope.schema.ts \
  docs/plans/DAY21_EXECUTION_PLAN.md; do
  [[ -f "$f" ]] || { echo "Thiếu prerequisite/artifact: $f" >&2; exit 1; }
done
export PYTHONPATH="$ROOT/services/api-server/src:$ROOT/services/api-server/src/mock_api:${PYTHONPATH:-}"
TSC="$ROOT/apps/web-portal/node_modules/.bin/tsc"
PYTEST="$ROOT/.venv/bin/pytest"
PYTHON="$ROOT/.venv/bin/python"
rm -rf .day21-build

echo '[1/5] TypeScript strict check'
"$TSC" -p qa-validation/configs/day21_tsconfig.json

echo '[2/5] TypeScript runtime utilities'
"$TSC" -p qa-validation/configs/day21_runtime_tsconfig.json
node qa-validation/automated-tests/day21_polling_runtime.test.cjs

echo '[3/5] Python API/state-machine tests'
"$PYTEST" -q qa-validation/automated-tests/test_day21_analysis_jobs.py qa-validation/automated-tests/test_day21_schema.py

echo '[4/5] Capture deterministic evidence'
"$PYTHON" - <<'PY_EVIDENCE'
import json,sys
from pathlib import Path
from fastapi.testclient import TestClient
root=Path.cwd(); sys.path[:0]=[str(root/'services/api-server/src'),str(root/'services/api-server/src/mock_api')]
from day20_store import reset_store
from day21_app import app,repository
reset_store(); repository.reset(); c=TestClient(app)
payload={"subjectRef":"SUBJ-D21-EVIDENCE","useCaseId":"uc1","protocol":{"protocolId":"upper-limb-gesture","protocolVersion":"v0.1"},"affectedSide":"right","referenceSide":"left","targetMuscles":["FCR","ECR"],"sessionType":"baseline","operatorRef":"KTV-HASH","consent":{"qualityImprovement":True,"modelTraining":False,"researchExport":False},"dataSourceIntent":"generic_csv_manifest"}
sid=c.post('/v1/sessions',json=payload,headers={'Idempotency-Key':'ev-session'}).json()['sessionId']
imp=c.post(f'/v1/sessions/{sid}/imports',json={'scenario_id':'golden_intake_pass'}).json()
m=[{"sourceChannel":f"Sensor {i}","canonicalChannelId":f"CH{i:02d}","muscle":"M","side":"right","unit":"uV","functionalRole":"other"} for i in range(1,5)]
c.put(f"/v1/imports/{imp['importId']}/mapping",json={'mappings':m}); c.post(f'/v1/sessions/{sid}/calibrations',json={'scenario_id':'golden_intake_pass'}); c.get(f'/v1/sessions/{sid}/quality'); c.post(f'/v1/sessions/{sid}/analyses')
job=c.post(f'/v1/sessions/{sid}/analysis-jobs',json={'scenarioId':'golden_completed'},headers={'Idempotency-Key':'ev-job'}).json()
while job['status'] in ('queued','running'):
 job=c.post(f"/v1/analyses/{job['analysisId']}/advance",json={'expectedCurrentStage':job['currentStage']}).json()
summary=c.get(job['resultLinks']['summary']).json()
out={'job':job,'summary':summary}
(root/'qa-validation/evidence').mkdir(parents=True,exist_ok=True)
(root/'qa-validation/evidence/day21-analysis-job-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(job['status'],job['analysisId'])
PY_EVIDENCE

echo '[5/5] Artifact and safety check'
"$PYTHON" scripts/dev/check_day21_artifacts.py
rm -rf .day21-build
echo 'All Day 21 checks passed.'
