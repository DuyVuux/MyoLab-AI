#!/usr/bin/env bash
set -euo pipefail

REPO="${1:-.}"
cd "$REPO"

PYTHON="${PYTHON:-}"
if [[ -z "$PYTHON" ]]; then
  if [[ -x ".venv/bin/python" ]]; then PYTHON=".venv/bin/python"; else PYTHON="python3"; fi
fi

echo "== UI-I2: core binding audit =="
"$PYTHON" scripts/dev/audit_ui_i2_core_bindings.py .

echo "== UI-I2: backend contract audit/promotion =="
set +e
"$PYTHON" scripts/dev/audit_and_promote_ui_i2_contracts.py .
CONTRACT_RC=$?
set -e

echo "== UI-I2: explicit live binding evidence =="
set +e
"$PYTHON" scripts/dev/verify_ui_i2_live_binding.py .
BINDING_RC=$?
set -e

echo "== UI-I2: API boundary tests =="
"$PYTHON" -m pytest -q \
  qa-validation/automated-tests/test_ui_i2_api_boundary.py \
  qa-validation/automated-tests/test_ui_i2_package_contract.py

echo "== UI-I2: frontend type-check =="
pnpm --dir apps/web-portal type-check

echo "== UI-I2: targeted Jest =="
pnpm --dir apps/web-portal exec jest --runInBand \
  src/features/auto-data-intake/__tests__/flow.test.ts \
  src/data/automation/__tests__/ui-i2-contracts.test.ts

echo "== UI-I2: production build =="
pnpm --dir apps/web-portal build

if [[ "$CONTRACT_RC" -ne 0 ]]; then
  echo "BLOCKED_BACKEND_BINDING: required UI-I2 endpoints are not all VERIFIED."
  exit 4
fi

if [[ "$BINDING_RC" -ne 0 ]]; then
  echo "BLOCKED_BACKEND_BINDING: route existence is insufficient; live canonical binding evidence is required."
  exit 5
fi

echo "PASS: AUTO_DATA_INGEST_QC_READY"
