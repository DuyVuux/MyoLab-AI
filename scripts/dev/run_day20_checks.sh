#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

for prerequisite in \
  apps/web-portal/src/schemas/role.schema.ts \
  apps/web-portal/src/schemas/analysis-envelope.schema.ts \
  apps/web-portal/src/components/ui/Alert.tsx \
  qa-validation/configs/day19_vendor_stubs.d.ts; do
  if [[ ! -f "$prerequisite" ]]; then
    echo "Thiếu prerequisite Day 19: $prerequisite" >&2
    exit 1
  fi
done

export PYTHONPATH="$ROOT/services/api-server/src/mock_api:${PYTHONPATH:-}"
TSC="$ROOT/apps/web-portal/node_modules/.bin/tsc"
PYTEST="$ROOT/.venv/bin/pytest"
PYTHON="$ROOT/.venv/bin/python"
mkdir -p qa-validation/evidence
rm -rf .day20-build

echo "[1/5] TypeScript/TSX strict check"
"$TSC" -p qa-validation/configs/day20_tsconfig.json

echo "[2/5] Compile and run workflow runtime tests"
"$TSC" -p qa-validation/configs/day20_workflow_tsconfig.json
node qa-validation/automated-tests/day20_workflow_runtime.test.cjs

echo "[3/5] FastAPI integration and frontend contract tests"
"$PYTEST" -q \
  qa-validation/automated-tests/test_day20_mock_api.py \
  qa-validation/automated-tests/test_day20_frontend_contracts.py

echo "[4/5] Capture deterministic evidence"
"$PYTHON" - <<'PY_EVIDENCE'
import json, sys
from pathlib import Path
from fastapi.testclient import TestClient
root = Path.cwd()
sys.path.insert(0, str(root / 'services/api-server/src/mock_api'))
from day20_app import app
from day20_store import reset_store
reset_store()
client = TestClient(app)
payload = {
  "subjectRef": "SUBJ-D20-EVIDENCE",
  "useCaseId": "uc1",
  "protocol": {"protocolId": "upper-limb-gesture", "protocolVersion": "v0.1"},
  "affectedSide": "right",
  "referenceSide": "left",
  "targetMuscles": ["Flexor carpi radialis", "Extensor carpi radialis"],
  "sessionType": "baseline",
  "operatorRef": "KTV-HASH-EVIDENCE",
  "consent": {"qualityImprovement": True, "modelTraining": False, "researchExport": False},
  "dataSourceIntent": "generic_csv_manifest"
}
session = client.post('/v1/sessions', json=payload, headers={'Idempotency-Key': 'day20-evidence'}).json()
sid = session['sessionId']
imp = client.post(f'/v1/sessions/{sid}/imports', json={'scenario_id':'golden_intake_pass'}).json()
mappings = [
 {"sourceChannel":"Sensor 1","canonicalChannelId":"CH01","muscle":"Flexor carpi radialis","side":"right","unit":"uV","functionalRole":"flexor"},
 {"sourceChannel":"Sensor 2","canonicalChannelId":"CH02","muscle":"Extensor carpi radialis","side":"right","unit":"uV","functionalRole":"extensor"},
 {"sourceChannel":"Sensor 3","canonicalChannelId":"CH03","muscle":"Biceps brachii","side":"right","unit":"uV","functionalRole":"compensation"},
 {"sourceChannel":"Sensor 4","canonicalChannelId":"CH04","muscle":"Upper trapezius","side":"right","unit":"uV","functionalRole":"compensation"},
]
client.put(f"/v1/imports/{imp['importId']}/mapping", json={'mappings':mappings})
preflight = client.get(f'/v1/sessions/{sid}/preflight').json()
calibration = client.post(f'/v1/sessions/{sid}/calibrations', json={'scenario_id':'golden_intake_pass'}).json()
quality = client.get(f'/v1/sessions/{sid}/quality', params={'scenario_id':'golden_intake_pass'}).json()
handoff = client.post(f'/v1/sessions/{sid}/analyses').json()
evidence = {"session":session,"import":imp,"preflight":preflight,"calibration":calibration,"quality":quality,"analysis_handoff":handoff}
(root/'qa-validation/evidence/day20-golden-intake-evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
print('Evidence written')
PY_EVIDENCE

echo "[5/5] Artifact and safety check"
"$PYTHON" scripts/dev/check_day20_artifacts.py
rm -rf .day20-build

echo "All Day 20 checks passed."
