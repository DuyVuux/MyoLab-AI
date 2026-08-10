#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

if [[ -f pyproject.toml ]] && command -v uv >/dev/null 2>&1; then
  PY=(uv run python)
  PYTEST=(uv run pytest)
else
  PY=(python3)
  PYTEST=(python3 -m pytest)
fi

"${PY[@]}" scripts/dev/validate_day13_time_count_unit.py
"${PYTEST[@]}" -q qa-validation/automated-tests/ingestion/test_time_count_unit.py

for previous in \
  qa-validation/automated-tests/contracts/test_day09_mr4_single_contract.py \
  qa-validation/automated-tests/contracts/test_day10_mr4_separated_contract.py \
  qa-validation/automated-tests/provenance/test_day11_source_ledger.py \
  qa-validation/automated-tests/contracts/test_day12_canonical_session.py
  do
    if [[ -f "$previous" ]]; then
      "${PYTEST[@]}" -q "$previous"
    fi
  done

echo "DAY13 checks PASS"
