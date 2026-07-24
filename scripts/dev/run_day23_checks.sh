#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

for f in \
  services/api-server/src/mock_api/day22_app.py \
  apps/web-portal/src/schemas/uc2-assessment.schema.ts \
  apps/web-portal/src/lib/uc2-assessment-client.ts \
  apps/web-portal/src/components/uc2/*.tsx \
  docs/plans/DAY23_EXECUTION_PLAN.md
 do
  [[ -f "$f" ]] || { echo "Thiếu prerequisite/artifact: $f" >&2; exit 1; }
done

export PYTHONPATH="$ROOT/services/api-server/src:$ROOT/services/api-server/src/mock_api:$ROOT/packages/semg-core:$ROOT/services/inference-service/src:${PYTHONPATH:-}"

rm -rf .day23-build

echo '[1/6] TypeScript strict'
npx --prefix apps/web-portal --no-install tsc -p qa-validation/configs/day23_tsconfig.json

echo '[2/6] TypeScript runtime'
npx --prefix apps/web-portal --no-install tsc -p qa-validation/configs/day23_runtime_tsconfig.json
node qa-validation/automated-tests/day23_metric_display.test.cjs

echo '[3/6] Python metrics/service/API/schema'
.venv/bin/pytest -q qa-validation/automated-tests/test_day23_metrics.py qa-validation/automated-tests/test_day23_service_api.py qa-validation/automated-tests/test_day23_schemas.py

echo '[4/6] Capture evidence'
.venv/bin/python - <<'PY'
import json
from pathlib import Path
import sys

root = Path.cwd()
sys.path[:0] = [
    str(root / 'services/api-server/src'),
    str(root / 'services/api-server/src/mock_api'),
    str(root / 'packages/semg-core'),
    str(root / 'services/inference-service/src'),
]

from services.longitudinal_service import build_assessment

root.joinpath('qa-validation/evidence').mkdir(parents=True, exist_ok=True)
assessment = build_assessment('golden_uc2_longitudinal').model_dump(mode='json')
(root / 'qa-validation/evidence/day23-uc2-assessment-evidence.json').write_text(
    json.dumps(assessment, ensure_ascii=False, indent=2),
    encoding='utf-8',
)
print(assessment['status'], assessment['assessmentId'])
PY

echo '[5/6] Playwright UC2 UI regression'
(
  cd apps/web-portal
  PLAYWRIGHT_BASE_URL="${PLAYWRIGHT_BASE_URL:-http://127.0.0.1:3111}" \
  PLAYWRIGHT_WEB_SERVER_COMMAND="${PLAYWRIGHT_WEB_SERVER_COMMAND:-npx next dev --port 3111}" \
  PLAYWRIGHT_REUSE_EXISTING_SERVER="${PLAYWRIGHT_REUSE_EXISTING_SERVER:-false}" \
  npx --no-install playwright test e2e/day23-uc2-regression.spec.ts
)

echo '[6/6] Artifact check'
.venv/bin/python scripts/dev/check_day23_artifacts.py

rm -rf .day23-build

echo 'All Day 23 checks passed.'
