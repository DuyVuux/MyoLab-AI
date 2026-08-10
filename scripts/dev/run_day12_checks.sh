#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

run_python() {
  if command -v uv >/dev/null 2>&1 && [[ -f pyproject.toml ]]; then
    uv run python "$@"
  else
    python3 "$@"
  fi
}

run_pytest() {
  if command -v uv >/dev/null 2>&1 && [[ -f pyproject.toml ]]; then
    uv run pytest "$@"
  else
    python3 -m pytest "$@"
  fi
}

printf '[DAY12] project root: %s\n' "$PROJECT_ROOT"

run_python scripts/dev/validate_day12_contracts.py
run_pytest -q qa-validation/automated-tests/contracts/test_day12_canonical_session.py

# Regression is mandatory after integration, but this standalone handoff does not
# bundle previous-day code. Run every upstream suite that exists in the target repo.
for test_file in \
  qa-validation/automated-tests/provenance/test_day11_source_ledger.py \
  qa-validation/automated-tests/contracts/test_day10_mr4_separated_contract.py \
  qa-validation/automated-tests/contracts/test_day09_mr4_single_contract.py
 do
  if [[ -f "$test_file" ]]; then
    printf '[DAY12] regression: %s\n' "$test_file"
    run_pytest -q "$test_file"
  fi
done

run_python scripts/dev/check_day12_artifacts.py

printf '[PASS] DAY12 engineering checks complete.\n'
printf '[INFO] GO_FOR_DAY_13 still requires integrated-repo upstream acceptance + human review.\n'
