#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
mkdir -p qa-validation/evidence/day33
LOG=qa-validation/evidence/day33-check-run.log
: > "$LOG"
run() { echo "+ $*" | tee -a "$LOG"; "$@" 2>&1 | tee -a "$LOG"; }

run env PYTHONDONTWRITEBYTECODE=1 python3 -m compileall -q -f ai-core/evaluation/day33 ai-core/pipelines/day33_build_prediction_contract.py ai-core/pipelines/day33_run_evaluation.py
run ./.venv/bin/python -m ruff check ai-core/evaluation/day33 ai-core/pipelines/day33_build_prediction_contract.py ai-core/pipelines/day33_run_evaluation.py qa-validation/automated-tests/test_day33.py
run python3 scripts/dev/check_day33_artifacts.py
run python3 scripts/data/day33_generate_synthetic_predictions.py
run python3 ai-core/pipelines/day33_validate_predictions.py --predictions qa-validation/fixtures/day33-synthetic-window-predictions.csv --output qa-validation/evidence/day33/day33-synthetic-prediction-gate.json
run python3 ai-core/pipelines/day33_run_evaluation.py --predictions qa-validation/fixtures/day33-synthetic-window-predictions.csv --output-dir qa-validation/evidence/day33/synthetic-evaluation --bootstrap-iterations 200
run python3 ai-core/pipelines/day33_build_prediction_contract.py --source-kind mendeley-day32-oof --source ai-core/experiments/mendeley-primary/day32-baseline-v1 --output qa-validation/evidence/day33/predictions/mendeley-day32-oof-window-contract.csv --ledger qa-validation/evidence/day33/input-day32/mendeley-day32-input-ledger.json
run python3 ai-core/pipelines/day33_run_evaluation.py --predictions qa-validation/evidence/day33/predictions/mendeley-day32-oof-window-contract.csv --output-dir qa-validation/evidence/day33/real-development/mendeley --bootstrap-iterations 500
run python3 ai-core/pipelines/day33_build_prediction_contract.py --source-kind grabmyo-day32-oof --source ai-core/experiments/grabmyo-primary4/baseline-v1/grabmyo-baseline-handoff.zip --output qa-validation/evidence/day33/predictions/grabmyo-day32-oof-trial-contract.csv --ledger qa-validation/evidence/day33/input-day32/grabmyo-day32-input-ledger.json
run python3 ai-core/pipelines/day33_run_evaluation.py --predictions qa-validation/evidence/day33/predictions/grabmyo-day32-oof-trial-contract.csv --output-dir qa-validation/evidence/day33/real-development/grabmyo --bootstrap-iterations 500
run python3 -m pytest -q qa-validation/automated-tests/test_day33.py
echo DAY33_CHECKS_PASS | tee -a "$LOG"
