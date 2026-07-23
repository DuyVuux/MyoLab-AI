#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

export PYTHONPATH="$ROOT/services/api-server/src/mock_api:${PYTHONPATH:-}"
mkdir -p qa-validation/evidence

echo "[1/4] TypeScript/TSX syntax and strict contract check"
npm --prefix apps/web-portal run type-check

echo "[2/4] FastAPI and contract tests"
.venv/bin/pytest -q \
  qa-validation/automated-tests/test_day19_mock_api.py \
  qa-validation/automated-tests/test_day19_contracts.py

echo "[3/4] Capture deterministic mock API evidence"
.venv/bin/python - <<'PYSMOKE'
import json, sys
from pathlib import Path
from fastapi.testclient import TestClient
root = Path.cwd()
sys.path.insert(0, str(root / 'services/api-server/src/mock_api'))
from day19_app import app
client = TestClient(app)
evidence = {
    'health': client.get('/health').json(),
    'dashboard': client.get('/v1/dashboard').json(),
    'use_cases': client.get('/v1/use-cases').json(),
}
(root / 'qa-validation/evidence/day19-mock-api-smoke.json').write_text(
    json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8'
)
print('Evidence written')
PYSMOKE

echo "[4/4] Artifact and safety check"
.venv/bin/python scripts/dev/check_day19_artifacts.py

echo "All Day 19 checks passed."
