#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
mkdir -p qa-validation/evidence
{
  echo "[1/7] Python syntax"
  python3 -m compileall -q ai-core/experiments scripts/ml scripts/dev
  echo "[2/7] Artifact/safety checker"
  python3 scripts/dev/check_day26_research_artifacts.py
  echo "[3/7] Blueprint validation"
  python3 scripts/ml/validate_day26_blueprint.py --root . --output qa-validation/evidence/day26-blueprint-validation.json
  echo "[4/7] Experiment matrix render"
  python3 scripts/ml/render_day26_experiment_matrix.py --config ai-core/configs/experiment_matrix.draft.yaml --csv qa-validation/evidence/day26-experiment-matrix.csv --json qa-validation/evidence/day26-experiment-matrix.json
  echo "[5/7] Test seal template"
  python3 scripts/ml/seal_test_manifest.py --template mlops/experiments/test-seal-manifest.template.yaml --output qa-validation/evidence/day26-test-set-seal.template.json
  echo "[6/7] Source hash ledger"
  python3 scripts/ml/generate_hash_ledger.py --root docs/research/day26 --output qa-validation/evidence/day26-source-hash-ledger.json
  echo "[7/7] Pytest"
  pytest -q qa-validation/automated-tests
} 2>&1 | tee qa-validation/evidence/day26-check-run.log
