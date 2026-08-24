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

$PY scripts/dev/finish_phase7r_critical_path.py .
