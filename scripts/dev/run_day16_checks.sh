#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$ROOT"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONPATH="$ROOT/ai-core/pipelines:$ROOT/packages/semg-core:$ROOT/services/signal-ingestion-service/src:$ROOT/services/quality-gate-service/src:$ROOT/services/preprocessing-service/src:$ROOT/services/feature-extraction-service/src:$ROOT/services/inference-service/src${PYTHONPATH:+:$PYTHONPATH}"
if [[ "${DAY16_FULL_REGRESSION:-0}" == "1" ]]; then
  echo '[1/8] Full Day 15 regression'
  bash scripts/dev/run_day15_checks.sh
else
  echo '[1/8] Bỏ qua full Day 15 regression'
fi
echo '[2/8] Generate QC fixtures'
python qa-validation/test-data/synthetic/generate_qc_fixtures.py --source-manifest data-platform/synthetic-data/golden_signal_01.manifest.json --output-dir qa-validation/test-data/synthetic --overwrite >/dev/null
echo '[3/8] Day 16 tests'
pytest -q qa-validation/automated-tests/test_mvp0_regression_suite.py
echo '[4/8] Full regression matrix'
rm -rf qa-validation/evidence/day16-regression
python scripts/data/run_mvp0_regression.py \
  --profile qa-validation/configs/mvp0_regression_v0.1.yaml \
  --output-root qa-validation/evidence/day16-regression \
  --json-out qa-validation/evidence/day16-mvp0-regression-report.json \
  --markdown-out qa-validation/evidence/day16-mvp0-regression-report.md \
  --validation-report ai-core/validation-reports/analytical_validation_mvp0.md \
  --overwrite
echo '[5/8] Validate report schema'
python scripts/dev/validate_day16_outputs.py
echo '[6/8] Freeze baseline'
python scripts/dev/freeze_mvp0_baseline_v0_1.py --report qa-validation/evidence/day16-mvp0-regression-report.json --output qa-validation/baselines/mvp0_baseline_v0.1.json --overwrite
echo '[7/8] Compare candidate to baseline'
python scripts/data/compare_regression_runs.py --baseline qa-validation/baselines/mvp0_baseline_v0.1.json --candidate qa-validation/evidence/day16-mvp0-regression-report.json
echo '[8/8] Artifact check'
python scripts/dev/check_day16_artifacts.py
echo 'All Day 16 checks passed.'
