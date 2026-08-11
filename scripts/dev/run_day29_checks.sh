#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
ROOT="${1:-$(pwd)}"
cd "$ROOT"
PY="python3"
PYTEST=(pytest -q -p no:cacheprovider)
if command -v uv >/dev/null 2>&1 && [[ -f pyproject.toml ]]; then
  PYTEST=(uv run pytest -q -p no:cacheprovider)
  PY="uv run python"
fi

echo "[1/3] DAY29 contract validator"
$PY scripts/dev/day29_contract_validator.py --repo-root "$ROOT"

echo "[2/3] DAY29 focused tests"
"${PYTEST[@]}" qa-validation/automated-tests/qc/test_data_integrity_qc.py

echo "[3/3] Full QC regression suite"
"${PYTEST[@]}" qa-validation/automated-tests/qc/

echo "All DAY29 checks passed."
