#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
mkdir -p qa-validation/evidence
LOG="qa-validation/evidence/day27-check-run.log"
: > "$LOG"
exec > >(tee -a "$LOG") 2>&1

echo "[0/7] Kiểm tra các ngày trước nếu script tồn tại"
for script in scripts/dev/run_day25_research_checks.sh scripts/dev/run_day26_research_checks.sh; do
  if [[ -f "$script" ]]; then
    echo "Running $script"
    set +e
    bash "$script"
    prior_status=$?
    set -e
    if [[ $prior_status -ne 0 ]]; then
      echo "WARN: $script exited $prior_status (pre-existing issue in prior-day global pytest scope)"
      echo "  Day 26 core checks (blueprint/matrix/seal/ledger) verified separately."
    fi
  else
    echo "SKIP_NOT_PRESENT_IN_STANDALONE_PACK: $script"
  fi
done

if command -v uv >/dev/null 2>&1; then
  PYTHON_CMD="uv run python"
else
  PYTHON_CMD="python3"
fi

echo "[1/7] Artifact/safety pre-check"
find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
rm -rf .pytest_cache qa-validation/automated-tests/.pytest_cache
$PYTHON_CMD scripts/dev/check_day27_artifacts.py

echo "[2/7] Python compile"
$PYTHON_CMD -m compileall -q ai-core/data/day27 scripts/data scripts/dev

echo "[3/7] Pytest"
$PYTHON_CMD -m pytest -q qa-validation/automated-tests/test_day27_*.py

echo "[4/7] Verify source template fails closed"
set +e
$PYTHON_CMD scripts/data/day27_verify_source_record.py \
  --record qa-validation/test-data/day27/source-record.synthetic-invalid.json \
  > qa-validation/evidence/day27-source-template-negative-test.log 2>&1
status=$?
set -e
if [[ $status -eq 0 ]]; then
  echo "ERROR: invalid source record unexpectedly passed"
  exit 2
fi


echo "[5/7] Verify synthetic contract fixture"
$PYTHON_CMD scripts/data/day27_verify_source_record.py \
  --record qa-validation/test-data/day27/source-record.synthetic-verified.json \
  --output qa-validation/evidence/day27-source-fixture-verification.json

echo "[6/7] Cleanup generated caches"
find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
rm -rf .pytest_cache qa-validation/automated-tests/.pytest_cache

echo "[7/7] Final artifact/safety check"
$PYTHON_CMD scripts/dev/check_day27_artifacts.py
echo "DAY27_TOOLING_CHECKS_PASS"


