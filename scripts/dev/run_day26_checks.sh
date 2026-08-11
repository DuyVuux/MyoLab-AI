#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
export PYTHONDONTWRITEBYTECODE=1
PYTHON_BIN="$(command -v python3 || command -v python)"
"$PYTHON_BIN" scripts/dev/day26_contract_validator.py
"$PYTHON_BIN" -m pytest -q -p no:cacheprovider qa-validation/automated-tests/qc/test_powerline.py
"$PYTHON_BIN" scripts/dev/check_day26_artifacts.py
if [[ -f scripts/dev/run_day22_checks.sh ]]; then
  echo "DAY22 live regression runner present; run separately if its temporal guards require phase-aware selection."
fi
echo "DAY26 checks passed."
