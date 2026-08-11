#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"
export PYTHONDONTWRITEBYTECODE=1
export PYTEST_ADDOPTS="${PYTEST_ADDOPTS:-} -p no:cacheprovider"

PY=(python3)
PYTEST=(python3 -m pytest)
if [[ -f pyproject.toml ]] && command -v uv >/dev/null 2>&1; then
  PY=(uv run python)
  PYTEST=(uv run pytest)
fi

echo "[1/4] DAY22 contract validator"
"${PY[@]}" scripts/dev/day22_windowing_contract_validator.py --repo-root "$ROOT"

echo "[2/4] DAY22 automated tests"
"${PYTEST[@]}" -q qa-validation/automated-tests/qc/test_day22_windowing.py

echo "[3/4] DAY22 Python compile"
"${PY[@]}" -m py_compile \
  packages/semg-core/semg_core/qc_windowing.py \
  services/quality-gate-service/src/aggregation/qc_aggregation.py \
  scripts/dev/day22_windowing_contract_validator.py

echo "[4/4] DAY21 phase-compatible regression when available"
DAY21_TEST="qa-validation/automated-tests/qc/test_day21_qc_taxonomy.py"
if [[ -f "$DAY21_TEST" ]]; then
  if grep -q "test_43_no_day22_window_implementation" "$DAY21_TEST"; then
    echo "Historical DAY21 anti-scope guard detected; deselecting only that guard."
    "${PYTEST[@]}" -q "$DAY21_TEST" -k "not test_43_no_day22_window_implementation"
  elif [[ -x scripts/dev/run_day21_checks.sh ]]; then
    bash scripts/dev/run_day21_checks.sh
  else
    "${PYTEST[@]}" -q "$DAY21_TEST"
  fi
else
  echo "DAY21 live tests not present in this isolated package; skipped."
fi

echo "All DAY22 checks passed."
