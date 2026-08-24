#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-.}"
cd "$ROOT"

if [ -z "${PYTHON:-}" ]; then
  if [ -x ".venv/bin/python" ]; then
    PY=".venv/bin/python"
  else
    PY="python3"
  fi
else
  PY="$PYTHON"
fi

$PY scripts/dev/continue_phase7r_locked_validation.py . --freeze-only

$PY -m pytest -q \
  qa-validation/automated-tests/test_phase7r_entry.py \
  qa-validation/automated-tests/test_phase7r_lock.py \
  qa-validation/automated-tests/test_phase7r_release_guard.py

$PY scripts/dev/continue_phase7r_locked_validation.py .
