#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

python3 -m py_compile services/signal-ingestion-service/src/provenance/source_ledger.py
python3 scripts/dev/validate_day11_source_ledger.py
pytest -q qa-validation/automated-tests/provenance/test_day11_source_ledger.py

# Previous-day regressions are required when those tests exist in the integrated repo.
if [[ -f qa-validation/automated-tests/contracts/test_day09_mr4_single_contract.py ]]; then
  pytest -q qa-validation/automated-tests/contracts/test_day09_mr4_single_contract.py
fi
if [[ -f qa-validation/automated-tests/contracts/test_day10_mr4_separated_contract.py ]]; then
  pytest -q qa-validation/automated-tests/contracts/test_day10_mr4_separated_contract.py
fi

python3 scripts/dev/check_day11_artifacts.py
printf '%s\n' "DAY11 checks: PASS"
