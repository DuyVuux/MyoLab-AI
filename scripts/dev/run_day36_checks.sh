#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PYTHON_BIN="${ROOT}/.venv/bin/python3"
if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

export PYTHONPATH="${ROOT}/packages/semg-core:${ROOT}/services/quality-gate-service/src:${ROOT}/qa-validation/lib${PYTHONPATH:+:$PYTHONPATH}"
cd "$ROOT"

"$PYTHON_BIN" scripts/dev/day36_challenge_runner.py
"$PYTHON_BIN" -m pytest -q qa-validation/automated-tests/qc/test_preserve_physiology_stress.py
