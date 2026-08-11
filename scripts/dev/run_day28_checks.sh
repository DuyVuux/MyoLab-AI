#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
export PYTHONDONTWRITEBYTECODE=1
python3 scripts/dev/day28_contract_validator.py
python3 -m pytest -q -p no:cacheprovider qa-validation/automated-tests/qc/test_channel_abnormality.py
python3 scripts/dev/check_day28_artifacts.py
if [[ -f scripts/dev/run_day22_checks.sh ]]; then
  echo "DAY22 live regression runner present; run separately if its temporal guards require phase-aware selection."
fi
echo "DAY28 checks passed."
