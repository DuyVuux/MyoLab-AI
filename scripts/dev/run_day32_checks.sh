#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$(pwd)}"
if command -v uv >/dev/null 2>&1; then
  PYTHON_BIN="${PYTHON:-uv run python}"
  PYTEST_BIN="${PYTEST:-uv run pytest}"
else
  PYTHON_BIN="${PYTHON:-python3}"
  PYTEST_BIN="${PYTEST:-pytest}"
fi
export PYTHONDONTWRITEBYTECODE=1
export PYTEST_ADDOPTS="${PYTEST_ADDOPTS:-} -p no:cacheprovider"

cd "$ROOT"

echo "[1/4] DAY32 contract validator"
$PYTHON_BIN scripts/dev/day32_annotation_contract_validator.py --repo-root "$ROOT"

echo "[2/4] DAY32 focused tests"
$PYTEST_BIN -q qa-validation/automated-tests/qc/test_day32_annotation_readiness.py

echo "[3/4] Optional upstream DAY31 regression"
if test -f qa-validation/automated-tests/qc/test_quality_handoff.py; then
  $PYTEST_BIN -q qa-validation/automated-tests/qc/test_quality_handoff.py
else
  echo "DAY31 focused tests not present in current tree; skipped."
fi
if test -f qa-validation/property-tests/test_day31_quality_handoff_properties.py; then
  $PYTEST_BIN -q qa-validation/property-tests/test_day31_quality_handoff_properties.py
else
  echo "DAY31 property tests not present in current tree; skipped."
fi

echo "[4/4] Artifact integrity"
$PYTHON_BIN scripts/dev/check_day32_artifacts.py --repo-root "$ROOT"

echo "All DAY32 checks passed."

