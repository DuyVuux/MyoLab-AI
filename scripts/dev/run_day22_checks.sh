#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

PYTHON="$ROOT/.venv/bin/python"
PYTEST="$ROOT/.venv/bin/pytest"
TSC="$ROOT/apps/web-portal/node_modules/.bin/tsc"

cleanup() {
  rm -rf \
    "$ROOT/.day20-build" \
    "$ROOT/.day21-build" \
    "$ROOT/.day22-build" \
    "$ROOT/apps/web-portal/.next" \
    "$ROOT/test-results"
}
trap cleanup EXIT INT TERM
cleanup

for executable in "$PYTHON" "$PYTEST" "$TSC"; do
  if [[ ! -x "$executable" ]]; then
    echo "Thiếu local executable: $executable" >&2
    exit 1
  fi
done

for prerequisite in \
  services/api-server/src/mock_api/day20_app.py \
  services/api-server/src/mock_api/day21_app.py \
  services/api-server/src/mock_api/day22_app.py \
  qa-validation/configs/day20_tsconfig.json \
  qa-validation/configs/day21_tsconfig.json \
  qa-validation/configs/day22_tsconfig.json \
  apps/web-portal/playwright.config.ts; do
  if [[ ! -f "$prerequisite" ]]; then
    echo "Thiếu prerequisite/artifact: $prerequisite" >&2
    exit 1
  fi
done

export PYTHONPATH="$ROOT/packages/semg-core:$ROOT/services/inference-service/src:$ROOT/services/api-server/src:$ROOT/services/api-server/src/mock_api:${PYTHONPATH:-}"

echo "[1/10] Day 20/21 regression tests (không ghi đè evidence lịch sử)"
"$PYTEST" -q \
  qa-validation/automated-tests/test_day20_mock_api.py \
  qa-validation/automated-tests/test_day20_frontend_contracts.py \
  qa-validation/automated-tests/test_day21_analysis_jobs.py \
  qa-validation/automated-tests/test_day21_schema.py
"$TSC" -p qa-validation/configs/day20_tsconfig.json
"$TSC" -p qa-validation/configs/day21_tsconfig.json
"$PYTHON" scripts/dev/check_day20_artifacts.py
"$PYTHON" scripts/dev/check_day21_artifacts.py

echo "[2/10] Core Activity Gate, latency và deterministic replay engine"
"$PYTEST" -q \
  packages/semg-core/tests \
  services/inference-service/tests

echo "[3/10] Day 22 schema, API, frontend contract và evidence tests"
"$PYTEST" -q \
  qa-validation/automated-tests/test_day22_schemas.py \
  qa-validation/automated-tests/test_day22_uc1_api.py \
  qa-validation/automated-tests/test_day22_frontend_contracts.py \
  qa-validation/automated-tests/test_day22_evidence.py

if rg -n \
  -e "pytest\\.(skip|xfail|importorskip)|pytest\\.mark\\.(skip|skipif|xfail)" \
  -e "unittest\\.(skip|skipIf|skipUnless|expectedFailure)" \
  -e "(^|[^[:alnum:]_])(test|it|describe)(\.describe)?\.(skip|fixme|fail|only)[[:space:]]*\(" \
  qa-validation/automated-tests/test_day22_*.py \
  qa-validation/automated-tests/day22_*.cjs \
  apps/web-portal/e2e/day22-uc1-replay.spec.ts; then
  echo "Day 22 không cho phép skip/xfail/focused acceptance tests." >&2
  exit 1
fi

echo "[4/10] Python syntax/import compilation"
"$PYTHON" -m compileall -q \
  packages/semg-core/semg_core \
  services/inference-service/src \
  services/api-server/src \
  scripts/dev/generate_day22_evidence.py \
  scripts/dev/check_day22_artifacts.py

echo "[5/10] Day 20/21 TypeScript runtime regression"
"$TSC" -p qa-validation/configs/day20_workflow_tsconfig.json
node qa-validation/automated-tests/day20_workflow_runtime.test.cjs
"$TSC" -p qa-validation/configs/day21_runtime_tsconfig.json
node qa-validation/automated-tests/day21_polling_runtime.test.cjs

echo "[6/10] Day 22 strict TypeScript và runtime parity"
"$TSC" -p qa-validation/configs/day22_tsconfig.json
"$TSC" -p qa-validation/configs/day22_runtime_tsconfig.json
node qa-validation/automated-tests/day22_frontend_runtime.test.cjs

echo "[7/10] Full web-portal type-check"
corepack pnpm --filter @myolab-ai/web-portal type-check

echo "[8/10] Full production web build"
corepack pnpm --filter @myolab-ai/web-portal build

echo "[9/10] Browser E2E cho UC1 replay và role-aware feedback"
PLAYWRIGHT_BASE_URL="http://127.0.0.1:32222" \
PLAYWRIGHT_WEB_SERVER_COMMAND="./node_modules/.bin/next dev --port 32222" \
PLAYWRIGHT_REUSE_EXISTING_SERVER="false" \
  corepack pnpm --filter @myolab-ai/web-portal exec playwright test \
  day22-uc1-replay.spec.ts

echo "[10/10] Chạy fail-closed artifact/freshness checker (không ghi đè evidence)"
"$PYTHON" scripts/dev/check_day22_artifacts.py
git diff --check

echo "All Day 22 checks passed."
