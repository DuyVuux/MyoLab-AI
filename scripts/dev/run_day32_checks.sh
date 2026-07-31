#!/usr/bin/env bash
# Day 32 — Full check suite
# Runs: Day30-31 regression → compile → artifact check → synthetic matrix →
#       preflight → tooling smoke → core baselines → optional eligibility →
#       pytest suite
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

# Prefer project venv
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON="$ROOT/.venv/bin/python"
else
  PYTHON="python3"
fi

mkdir -p qa-validation/evidence/day32
LOG="qa-validation/evidence/day32/day32-check-run.log"
: > "$LOG"
run(){ echo "+ $*" | tee -a "$LOG"; "$@" 2>&1 | tee -a "$LOG"; }

echo "=== Day 32 Check Suite ===" | tee -a "$LOG"
echo "ROOT=$ROOT" | tee -a "$LOG"
echo "" | tee -a "$LOG"

# --- Day 30-31 regression ---
if [[ -x scripts/dev/run_day31_checks.sh ]]; then
  echo "--- Day 31 regression ---" | tee -a "$LOG"
  run bash scripts/dev/run_day31_checks.sh
else
  echo "Day31 regression: SKIPPED_NOT_PRESENT" | tee -a "$LOG"
fi

# --- Python compile ---
echo "" | tee -a "$LOG"
echo "--- Python compile ---" | tee -a "$LOG"
run env PYTHONDONTWRITEBYTECODE=1 $PYTHON -m compileall -q -f \
  ai-core/modeling/day32 \
  ai-core/pipelines \
  scripts/dev/check_day32_artifacts.py \
  scripts/dev/day32_tooling_smoke.py \
  scripts/data/day32_generate_synthetic_matrix.py \
  scripts/data/day32_preflight.py

# --- Artifact check ---
echo "" | tee -a "$LOG"
echo "--- Artifact check ---" | tee -a "$LOG"
run $PYTHON scripts/dev/check_day32_artifacts.py

# --- Generate synthetic matrix ---
echo "" | tee -a "$LOG"
echo "--- Generate synthetic matrix ---" | tee -a "$LOG"
run $PYTHON scripts/data/day32_generate_synthetic_matrix.py

# --- Preflight ---
echo "" | tee -a "$LOG"
echo "--- Preflight ---" | tee -a "$LOG"
run $PYTHON scripts/data/day32_preflight.py \
  --day31-readiness qa-validation/fixtures/day31-readiness.fixture.json \
  --authorization qa-validation/fixtures/day32-synthetic-authorization.yaml \
  --output qa-validation/evidence/day32/day32-preflight.json

# --- Tooling smoke ---
echo "" | tee -a "$LOG"
echo "--- Tooling smoke ---" | tee -a "$LOG"
run $PYTHON scripts/dev/day32_tooling_smoke.py

# --- Core baselines ---
echo "" | tee -a "$LOG"
echo "--- Core baselines ---" | tee -a "$LOG"
run $PYTHON ai-core/pipelines/day32_run_core_baselines.py \
  --matrix qa-validation/fixtures/day32-synthetic-matrix.npz \
  --authorization qa-validation/fixtures/day32-synthetic-authorization.yaml \
  --output qa-validation/evidence/day32/day32-synthetic-core-smoke.json \
  --n-splits 3

# --- Optional eligibility ---
echo "" | tee -a "$LOG"
echo "--- Optional eligibility ---" | tee -a "$LOG"
run $PYTHON ai-core/pipelines/day32_run_optional_baselines.py \
  --core-gate qa-validation/evidence/day32/day32-synthetic-core-smoke.json \
  --output qa-validation/evidence/day32/day32-optional-eligibility.json

# --- Pytest ---
echo "" | tee -a "$LOG"
echo "--- Pytest Day 32 ---" | tee -a "$LOG"
run env PYTHONDONTWRITEBYTECODE=1 $PYTHON -m pytest -q -p no:cacheprovider \
  qa-validation/automated-tests/test_day32_*.py

echo "" | tee -a "$LOG"
echo "DAY32_CHECKS_PASS" | tee -a "$LOG"
