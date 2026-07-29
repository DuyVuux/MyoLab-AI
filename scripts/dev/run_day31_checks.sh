#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

if [[ -n "${PYTHON_BIN:-}" ]]; then
  :
elif [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python)"
else
  echo "No Python interpreter found" >&2
  exit 127
fi

EVIDENCE_DIR="qa-validation/evidence/day31"
mkdir -p "$EVIDENCE_DIR"
LOG="$EVIDENCE_DIR/day31-check-run.log"
: > "$LOG"
PYCACHE_ROOT="$(mktemp -d)"
trap 'rm -rf "$PYCACHE_ROOT"' EXIT

run() {
  echo "+ $*" | tee -a "$LOG"
  "$@" 2>&1 | tee -a "$LOG"
}

run env PYTHONDONTWRITEBYTECODE=1 "$PYTHON_BIN" -m pytest -q \
  -p no:cacheprovider qa-validation/automated-tests/test_day30_*.py
run "$PYTHON_BIN" scripts/dev/check_day30_artifacts.py
run env PYTHONPYCACHEPREFIX="$PYCACHE_ROOT" "$PYTHON_BIN" -m compileall -q -f \
  packages/semg-core/semg_core/day31_features \
  ai-core/data/day31 \
  scripts/data/day31_preflight.py \
  scripts/data/day31_validate_feature_contract.py \
  scripts/data/day31_generate_feature_registry.py \
  scripts/data/day31_extract_smoke.py \
  scripts/data/day31_extract_features.py \
  scripts/data/day31_feature_quality_smoke.py \
  scripts/data/day31_build_feature_manifest.py \
  scripts/data/day31_build_readiness_decision.py \
  scripts/dev/stress_test_day31.py \
  scripts/dev/check_day31_artifacts.py
run "$PYTHON_BIN" -m ruff check \
  packages/semg-core/semg_core/day31_features \
  ai-core/data/day31 \
  scripts/data/day31_*.py \
  scripts/dev/*day31*.py \
  qa-validation/automated-tests/test_day31_*.py
run "$PYTHON_BIN" scripts/data/day31_preflight.py \
  --config ai-core/configs/day31_feature_engineering.research.yaml \
  --day30-readiness qa-validation/evidence/day30/day30-readiness-decision.json \
  --output "$EVIDENCE_DIR/day31-preflight.json"
run "$PYTHON_BIN" scripts/data/day31_generate_feature_registry.py \
  --contract ai-core/configs/day31_feature_contract.v1.yaml \
  --output "$EVIDENCE_DIR/day31-feature-registry.json"
run "$PYTHON_BIN" scripts/data/day31_validate_feature_contract.py \
  --contract ai-core/configs/day31_feature_contract.v1.yaml \
  --spectral-contract ai-core/configs/day31_spectral_contract.v1.yaml \
  --output "$EVIDENCE_DIR/day31-feature-contract-validation.json"
run "$PYTHON_BIN" scripts/data/day31_extract_smoke.py \
  --output "$EVIDENCE_DIR/day31-golden-feature-results.json"
run "$PYTHON_BIN" scripts/data/day31_feature_quality_smoke.py \
  --windows 256 \
  --output "$EVIDENCE_DIR/day31-feature-quality-smoke.json"
run "$PYTHON_BIN" scripts/dev/stress_test_day31.py \
  --windows 512 \
  --channels 28 \
  --output "$EVIDENCE_DIR/day31-stress-test.json"
run env PYTHONDONTWRITEBYTECODE=1 "$PYTHON_BIN" -m pytest -q \
  -p no:cacheprovider \
  --cov=packages/semg-core/semg_core/day31_features \
  --cov=ai-core/data/day31 \
  --cov-report=term-missing \
  --cov-report=json:"$EVIDENCE_DIR/day31-coverage.json" \
  --cov-fail-under=80 \
  qa-validation/automated-tests/test_day31_*.py
run "$PYTHON_BIN" scripts/data/day31_build_feature_manifest.py \
  --window-index qa-validation/evidence/day30/day30-window-index.fixture.json \
  --contract ai-core/configs/day31_feature_contract.v1.yaml \
  --source-manifest qa-validation/evidence/day30/day30-source-hash-ledger.json \
  --registry "$EVIDENCE_DIR/day31-feature-registry.json" \
  --smoke "$EVIDENCE_DIR/day31-golden-feature-results.json" \
  --quality "$EVIDENCE_DIR/day31-feature-quality-smoke.json" \
  --stress "$EVIDENCE_DIR/day31-stress-test.json" \
  --output "$EVIDENCE_DIR/day31-feature-manifest.json"
run "$PYTHON_BIN" scripts/data/day31_build_readiness_decision.py \
  --preflight "$EVIDENCE_DIR/day31-preflight.json" \
  --contract-validation "$EVIDENCE_DIR/day31-feature-contract-validation.json" \
  --smoke "$EVIDENCE_DIR/day31-golden-feature-results.json" \
  --quality "$EVIDENCE_DIR/day31-feature-quality-smoke.json" \
  --stress "$EVIDENCE_DIR/day31-stress-test.json" \
  --manifest "$EVIDENCE_DIR/day31-feature-manifest.json" \
  --output "$EVIDENCE_DIR/day31-readiness-decision.json"
run "$PYTHON_BIN" scripts/dev/check_day31_artifacts.py

echo "DAY31_CHECKS_PASS" | tee -a "$LOG"
