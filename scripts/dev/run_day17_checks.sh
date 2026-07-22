#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$ROOT"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONPATH="$ROOT/ai-core/pipelines:$ROOT/packages/semg-core:$ROOT/services/signal-ingestion-service/src:$ROOT/services/quality-gate-service/src:$ROOT/services/preprocessing-service/src:$ROOT/services/feature-extraction-service/src:$ROOT/services/inference-service/src:$ROOT/services/api-server/src/schemas${PYTHONPATH:+:$PYTHONPATH}"
if [[ "${DAY17_FULL_REGRESSION:-0}" == "1" ]]; then
  echo '[1/9] Full Day 16 regression'; bash scripts/dev/run_day16_checks.sh
else
  echo '[1/9] Bỏ qua full Day 16 regression'
fi
echo '[2/9] Generate fixtures'
python qa-validation/test-data/synthetic/generate_qc_fixtures.py --source-manifest data-platform/synthetic-data/golden_signal_01.manifest.json --output-dir qa-validation/test-data/synthetic --overwrite >/dev/null
echo '[3/9] Contract tests'
pytest -q qa-validation/automated-tests/test_api_contract_day17.py
echo '[4/9] Build analysis packages'
rm -rf qa-validation/evidence/day17-golden-analysis qa-validation/evidence/day17-abstained-analysis
python ai-core/pipelines/run_offline_analysis.py --manifest data-platform/synthetic-data/golden_signal_01.manifest.json --output-dir qa-validation/evidence/day17-golden-analysis --expect-status completed --quiet
python ai-core/pipelines/run_offline_analysis.py --manifest qa-validation/test-data/synthetic/qc_fail_flatline.manifest.json --output-dir qa-validation/evidence/day17-abstained-analysis --expect-status abstained --quiet
echo '[5/9] Build canonical summaries'
python scripts/data/build_analysis_api_summary.py --analysis-dir qa-validation/evidence/day17-golden-analysis --output qa-validation/evidence/day17-golden-api-summary.json
python scripts/data/build_analysis_api_summary.py --analysis-dir qa-validation/evidence/day17-abstained-analysis --output qa-validation/evidence/day17-abstained-api-summary.json
echo '[6/9] Generate examples'
python scripts/dev/generate_day17_api_examples.py
echo '[7/9] Validate JSON schemas'
python scripts/dev/validate_day17_outputs.py
echo '[8/9] Validate OpenAPI'
python scripts/dev/validate_openapi_contract.py --openapi openapi.yaml
echo '[9/9] Artifact check'
python scripts/dev/check_day17_artifacts.py
echo 'All Day 17 checks passed.'
