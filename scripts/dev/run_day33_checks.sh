#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/packages/semg-core${PYTHONPATH:+:$PYTHONPATH}"

if [[ -f "$ROOT/.venv/bin/python" ]]; then
  PYTHON="$ROOT/.venv/bin/python"
else
  PYTHON="python3"
fi

echo "[1/6] DAY33 contract validator"
"$PYTHON" scripts/dev/day33_corpus_contract_validator.py --repo-root "$ROOT"

echo "[2/6] DAY33 focused tests"
"$PYTHON" -m pytest -q qa-validation/automated-tests/research/test_day33_research_corpus.py

echo "[3/6] DAY32 focused regression when present"
if [[ -f qa-validation/automated-tests/qc/test_day32_annotation_readiness.py ]]; then
  "$PYTHON" -m pytest -q qa-validation/automated-tests/qc/test_day32_annotation_readiness.py
else
  echo "DAY32 focused test not present in standalone handoff; skipped."
fi

echo "[4/6] Full live QC + property regression when present"
REGRESSION_PATHS=()
[[ -d qa-validation/automated-tests/qc ]] && REGRESSION_PATHS+=(qa-validation/automated-tests/qc)
[[ -d qa-validation/property-tests ]] && REGRESSION_PATHS+=(qa-validation/property-tests)
if (( ${#REGRESSION_PATHS[@]} )); then
  "$PYTHON" -m pytest -q "${REGRESSION_PATHS[@]}"
else
  echo "No upstream regression directories present; skipped."
fi

echo "[5/6] Artifact integrity"
"$PYTHON" scripts/dev/check_day33_artifacts.py

echo "[6/6] Cache hygiene cleanup/check"
find . -type f -name '*.pyc' -delete 2>/dev/null || true
find qa-validation packages/semg-core services/quality-gate-service ai-core scripts -type d \( -name __pycache__ -o -name .pytest_cache \) -prune -exec rm -rf {} + 2>/dev/null || true
rm -rf .pytest_cache
if find . -type f -name '*.pyc' -print -quit | grep -q .; then
  echo "Unexpected .pyc remains" >&2
  exit 1
fi

echo "DAY33 CHECKS PASS"
