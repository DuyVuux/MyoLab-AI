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

printf '\n[DAY15-CORRUPTION 1/5] Validate invariant contract and static fixtures\n'
"${PY[@]}" scripts/dev/validate_day15_corruption_invariants.py

printf '\n[DAY15-CORRUPTION 2/5] Fixture factory unit/negative tests\n'
"${PYTEST[@]}" -q \
  qa-validation/automated-tests/ingestion/test_day15_corruption_factory.py

printf '\n[DAY15-CORRUPTION 3/5] Property-based safety verification\n'
"${PYTEST[@]}" -q qa-validation/property-tests/day15_corruption/test_ingestion_properties.py

printf '\n[DAY15-CORRUPTION 4/5] Upstream regression if present in integrated monorepo\n'
for previous in \
  qa-validation/automated-tests/contracts/test_day09_mr4_single_contract.py \
  qa-validation/automated-tests/contracts/test_day10_mr4_separated_contract.py \
  qa-validation/automated-tests/provenance/test_day11_source_ledger.py \
  qa-validation/automated-tests/contracts/test_day12_canonical_session.py \
  qa-validation/automated-tests/ingestion/test_time_count_unit.py \
  qa-validation/automated-tests/normalization/test_day14_channel_mapper.py
  do
    if [[ -f "$previous" ]]; then
      "${PYTEST[@]}" -q "$previous"
    fi
  done

printf '\n[DAY15-CORRUPTION 5/5] Namespaced artifact integrity\n'
"${PY[@]}" scripts/dev/check_day15_corruption_artifacts.py

echo "DAY15 corruption checks PASS"
