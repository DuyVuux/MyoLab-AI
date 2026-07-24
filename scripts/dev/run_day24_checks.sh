#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

for file in \
  docs/plans/DAY24_EXECUTION_PLAN.md \
  services/api-server/src/schemas/day24_review_report_schema.py \
  services/report-generation-service/src/day24_report_builder.py
do
  [[ -f "$file" ]] || { echo "Thiếu artifact/prerequisite: $file" >&2; exit 1; }
done

export PYTHONPATH="$ROOT/services/api-server/src:$ROOT/services/api-server/src/mock_api:$ROOT/services/report-generation-service/src:$ROOT/services/inference-service/src:$ROOT/packages/semg-core:${PYTHONPATH:-}"

echo "[1/6] Python syntax"
.venv/bin/python -m compileall -q \
  services/api-server/src/schemas/day24_review_report_schema.py \
  services/api-server/src/services/day24_review_workflow_service.py \
  services/api-server/src/services/day24_feedback_adjudication_service.py \
  services/api-server/src/mock_api/day24_app.py \
  services/report-generation-service/src/day24_report_hash.py \
  services/report-generation-service/src/day24_report_builder.py

echo "[2/6] TypeScript strict"
npx --prefix apps/web-portal --no-install tsc -p qa-validation/configs/day24_tsconfig.json

echo "[3/6] Unit, schema và API tests"
.venv/bin/pytest -q \
  qa-validation/automated-tests/test_day24_review_workflow.py \
  qa-validation/automated-tests/test_day24_report_builder.py \
  qa-validation/automated-tests/test_day24_feedback_adjudication.py \
  qa-validation/automated-tests/test_day24_api.py \
  qa-validation/automated-tests/test_day24_schemas.py

echo "[4/6] Sinh evidence"
.venv/bin/python scripts/data/generate_day24_review_evidence.py

echo "[5/6] Playwright review/report UI regression"
(
  cd apps/web-portal
  PLAYWRIGHT_BASE_URL="${PLAYWRIGHT_BASE_URL:-http://127.0.0.1:3112}" \
  PLAYWRIGHT_WEB_SERVER_COMMAND="${PLAYWRIGHT_WEB_SERVER_COMMAND:-npx next dev --port 3112}" \
  PLAYWRIGHT_REUSE_EXISTING_SERVER="${PLAYWRIGHT_REUSE_EXISTING_SERVER:-false}" \
  npx --no-install playwright test e2e/day24-review-report-regression.spec.ts
)

echo "[6/6] Artifact/safety check"
.venv/bin/python scripts/dev/check_day24_artifacts.py

echo "All Day 24 checks passed."
