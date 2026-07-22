#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$ROOT"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONPATH="$ROOT/ai-core/pipelines:$ROOT/packages/semg-core:$ROOT/services/signal-ingestion-service/src:$ROOT/services/quality-gate-service/src:$ROOT/services/preprocessing-service/src:$ROOT/services/feature-extraction-service/src:$ROOT/services/inference-service/src${PYTHONPATH:+:$PYTHONPATH}"
if [[ "${DAY15_FULL_REGRESSION:-0}" == "1" ]]; then echo '[1/10] Full Day 14 regression'; bash scripts/dev/run_day14_checks.sh; else echo '[1/10] Bỏ qua full Day 14 regression'; fi
echo '[2/10] Pipeline unit/integration tests'
pytest -q qa-validation/automated-tests/test_offline_analysis_pipeline.py
echo '[3/10] Prepare fixtures and clean evidence dirs'
python qa-validation/test-data/synthetic/generate_qc_fixtures.py --source-manifest data-platform/synthetic-data/golden_signal_01.manifest.json --output-dir qa-validation/test-data/synthetic --overwrite >/dev/null
rm -rf qa-validation/evidence/day15-golden-run qa-validation/evidence/day15-golden-rerun qa-validation/evidence/day15-warning-run qa-validation/evidence/day15-abstained-run
echo '[4/10] Golden run'
python ai-core/pipelines/run_offline_analysis.py --manifest data-platform/synthetic-data/golden_signal_01.manifest.json --output-dir qa-validation/evidence/day15-golden-run --expect-status completed --expect-conclusion supported_pattern
echo '[5/10] Golden deterministic rerun'
python ai-core/pipelines/run_offline_analysis.py --manifest data-platform/synthetic-data/golden_signal_01.manifest.json --output-dir qa-validation/evidence/day15-golden-rerun --expect-status completed --expect-conclusion supported_pattern --quiet
echo '[6/10] Warning run'
python ai-core/pipelines/run_offline_analysis.py --manifest qa-validation/test-data/synthetic/qc_warning_powerline.manifest.json --output-dir qa-validation/evidence/day15-warning-run --expect-status completed_with_warnings --quiet
echo '[7/10] Abstention run'
python ai-core/pipelines/run_offline_analysis.py --manifest qa-validation/test-data/synthetic/qc_fail_flatline.manifest.json --output-dir qa-validation/evidence/day15-abstained-run --expect-status abstained --expect-conclusion abstained --quiet
echo '[8/10] Verify package integrity'
python scripts/data/verify_offline_analysis_package.py --analysis-dir qa-validation/evidence/day15-golden-run --json-out qa-validation/evidence/day15-package-verification.json
echo '[9/10] Validate and register'
python scripts/dev/validate_day15_outputs.py
python scripts/dev/register_offline_analysis_mvp0.py
echo '[10/10] Artifact check'
python scripts/dev/check_day15_artifacts.py
echo 'All Day 15 checks passed.'
