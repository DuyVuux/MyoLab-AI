#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-.}"
cd "$ROOT"
if [[ -x .venv/bin/python ]]; then
  PY=.venv/bin/python
elif command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  PY=python
fi

echo "[UI-I1] backend contract discovery"
"$PY" scripts/dev/audit_ui_i1_backend_contracts.py .

echo "[UI-I1] foundation pytest"
"$PY" -m pytest qa-validation/automated-tests/test_ui_i1_integration_foundation.py -q

if command -v pnpm >/dev/null 2>&1; then
  echo "[UI-I1] frontend type-check"
  pnpm --dir apps/web-portal type-check
  echo "[UI-I1] frontend build"
  pnpm --dir apps/web-portal build
  echo "[UI-I1] frontend jest"
  pnpm --dir apps/web-portal exec jest --runInBand
else
  echo "[UI-I1] BLOCKED: pnpm not available; frontend compile/build/test not executed" >&2
  exit 4
fi

echo "[UI-I1] PASS: AUTO_DATA_CONTRACT_READY"
