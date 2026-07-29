#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
mkdir -p qa-validation/evidence
LOG="qa-validation/evidence/day29-check-run.log"
: > "$LOG"

run() {
  echo "+ $*" | tee -a "$LOG"
  "$@" 2>&1 | tee -a "$LOG"
}

if [[ -x scripts/dev/run_day28_checks.sh ]]; then
  run bash scripts/dev/run_day28_checks.sh
else
  echo "Day28 regression: SKIPPED_NOT_PRESENT_IN_THIS_PACK" | tee -a "$LOG"
fi

run env PYTHONDONTWRITEBYTECODE=1 python3 -m compileall -q -f ai-core/data/day29 scripts/data scripts/dev
run python3 scripts/dev/check_day29_artifacts.py
run python3 scripts/dev/day29_tooling_smoke.py
run env PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider qa-validation/automated-tests/test_day29*.py

echo "DAY29_CHECKS_PASS" | tee -a "$LOG"
