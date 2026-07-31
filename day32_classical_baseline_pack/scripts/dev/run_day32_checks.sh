#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
mkdir -p qa-validation/evidence
LOG="qa-validation/evidence/day32-check-run.log"
: > "$LOG"
run(){ echo "+ $*" | tee -a "$LOG"; "$@" 2>&1 | tee -a "$LOG"; }

if [[ -x scripts/dev/run_day31_checks.sh ]]; then
  run bash scripts/dev/run_day31_checks.sh
else
  echo "Day31 regression: SKIPPED_NOT_PRESENT_IN_PORTABLE_PACK" | tee -a "$LOG"
fi

run env PYTHONDONTWRITEBYTECODE=1 python -m compileall -q -f ai-core/modeling/day32 ai-core/pipelines scripts
run python scripts/dev/check_day32_artifacts.py
run python scripts/data/day32_generate_synthetic_matrix.py
run python scripts/data/day32_preflight.py \
  --day31-readiness qa-validation/fixtures/day31-readiness.fixture.json \
  --authorization qa-validation/fixtures/day32-synthetic-authorization.yaml \
  --output qa-validation/evidence/day32-preflight.json
run python scripts/dev/day32_tooling_smoke.py
run python ai-core/pipelines/day32_run_core_baselines.py \
  --matrix qa-validation/fixtures/day32-synthetic-matrix.npz \
  --authorization qa-validation/fixtures/day32-synthetic-authorization.yaml \
  --output qa-validation/evidence/day32-synthetic-core-smoke.json \
  --n-splits 3
run python ai-core/pipelines/day32_run_optional_baselines.py \
  --core-gate qa-validation/evidence/day32-synthetic-core-smoke.json \
  --output qa-validation/evidence/day32-optional-eligibility.json
run env PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider qa-validation/automated-tests
echo "DAY32_CHECKS_PASS" | tee -a "$LOG"
