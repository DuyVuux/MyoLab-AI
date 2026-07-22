#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$ROOT"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONPATH="$ROOT/packages/semg-core:$ROOT/services/signal-ingestion-service/src:$ROOT/services/quality-gate-service/src:$ROOT/services/preprocessing-service/src:$ROOT/services/feature-extraction-service/src:$ROOT/services/inference-service/src${PYTHONPATH:+:$PYTHONPATH}"
if [[ "${DAY14_FULL_REGRESSION:-0}" == "1" ]]; then echo '[1/9] Full Day 13 regression'; bash scripts/dev/run_day13_checks.sh; else echo '[1/9] Bỏ qua full Day 13 regression'; fi
echo '[2/9] Unit/config/formatter tests'
pytest -q packages/semg-core/tests/test_technical_confidence.py packages/semg-core/tests/test_safety_wording.py services/inference-service/tests/test_confidence_config.py services/inference-service/tests/test_inference_formatter.py
echo '[3/9] Formula and wording verification'
python scripts/data/verify_technical_confidence.py
echo '[4/9] Golden E2E'
python scripts/data/run_explainable_inference.py --manifest data-platform/synthetic-data/golden_signal_01.manifest.json --json-out qa-validation/evidence/day14-explainable-inference.json --expect-status completed --expect-conclusion supported_pattern
echo '[5/9] Deterministic rerun'
python scripts/data/run_explainable_inference.py --manifest data-platform/synthetic-data/golden_signal_01.manifest.json --json-out qa-validation/evidence/day14-explainable-inference-rerun.json --expect-status completed --expect-conclusion supported_pattern --quiet
echo '[6/9] QC warning propagation'
python qa-validation/test-data/synthetic/generate_qc_fixtures.py --source-manifest data-platform/synthetic-data/golden_signal_01.manifest.json --output-dir qa-validation/test-data/synthetic --overwrite >/dev/null
python scripts/data/run_explainable_inference.py --manifest qa-validation/test-data/synthetic/qc_warning_powerline.manifest.json --json-out qa-validation/evidence/day14-explainable-inference-warning.json --expect-status completed_with_warnings --quiet
echo '[7/9] Abstention propagation'
python scripts/data/run_explainable_inference.py --manifest qa-validation/test-data/synthetic/qc_fail_flatline.manifest.json --json-out qa-validation/evidence/day14-explainable-inference-abstained.json --expect-status abstained --expect-conclusion abstained --expect-reason INFERENCE_ABSTAINED_BY_RULE --quiet
echo '[8/9] Validate and register'
python scripts/dev/validate_day14_outputs.py
python scripts/dev/register_technical_confidence_v0_1.py
echo '[9/9] Artifact check'
python scripts/dev/check_day14_artifacts.py
echo 'All Day 14 checks passed.'
