#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

if [[ -x scripts/dev/run_day36_checks.sh ]]; then
  bash scripts/dev/run_day36_checks.sh
else
  echo "Day36 regression: SKIPPED_NOT_PRESENT_IN_PORTABLE_PACK"
fi

python -m compileall -q ai-core/quantitative/day37 ai-core/pipelines
python scripts/dev/check_day37_artifacts.py
python ai-core/pipelines/day37_run_synthetic_validation.py
pytest -q -p no:cacheprovider qa-validation/automated-tests/test_day37_*.py
echo DAY37_CHECKS_PASS
