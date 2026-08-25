#!/usr/bin/env bash
set -euo pipefail
cd "${1:-.}"
PYTHON="${PYTHON:-}"
[[ -n "$PYTHON" ]] || { [[ -x .venv/bin/python ]] && PYTHON=.venv/bin/python || PYTHON=python3; }

echo "== prerequisite UI-I2 =="; "$PYTHON" scripts/dev/verify_ui_i2_live_binding.py .
echo "== prerequisite UI-I3 =="; "$PYTHON" scripts/dev/verify_ui_i3_live_binding.py .

echo "== UI-I4 operations route =="; "$PYTHON" scripts/dev/audit_ui_i4_contracts.py .
echo "== UI-I4 operations real-mode smoke =="; "$PYTHON" scripts/dev/run_ui_i4_live_backend_smoke.py .
echo "== UI-I4 operations binding =="; "$PYTHON" scripts/dev/verify_ui_i4_live_binding.py .
echo "== UI-I4 real browser E2E evidence =="; "$PYTHON" scripts/dev/verify_ui_i4_golden_e2e.py .

echo "== UI-I4 API tests =="; "$PYTHON" -m pytest -q qa-validation/automated-tests/test_ui_i4_operations_boundary.py
echo "== frontend type-check =="; pnpm --dir apps/web-portal type-check
echo "== targeted Jest =="; pnpm --dir apps/web-portal exec jest --runInBand src/features/operations-dashboard/__tests__/operations.test.ts
echo "== production build =="; pnpm --dir apps/web-portal build

echo "== protected regressions =="
if [[ -f apps/web-portal/e2e/uc1-replay.spec.ts || -d apps/web-portal/e2e ]]; then
  echo "Existing Playwright regressions must remain green; integration agent should run the repo's established UC/review regression commands."
fi

echo "== final frontend freeze =="; "$PYTHON" scripts/dev/freeze_ui_frontend.py .
echo "PASS: UI_PORTFOLIO_READY"
