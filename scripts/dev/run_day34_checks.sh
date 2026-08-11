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

echo "[1/6] Regenerate DAY34 analysis evidence"
"$PYTHON" scripts/dev/day34_analysis_runner.py

echo "[2/6] DAY34 contract validator"
"$PYTHON" scripts/dev/day34_contract_validator.py

echo "[3/6] DAY34 focused research tests"
"$PYTHON" -m pytest -q qa-validation/automated-tests/research/test_day34_weak_label_analysis.py

echo "[4/6] DAY33 upstream corpus regression"
"$PYTHON" -m pytest -q qa-validation/automated-tests/research/test_day33_research_corpus.py

echo "[5/6] QC/property regression (historical DAY21 anti-future-scope guard deselected)"
"$PYTHON" -m pytest -q qa-validation/automated-tests/qc qa-validation/property-tests \
  -k 'not test_43_no_day22_window_implementation'

echo "[6/6] DAY34 artifact integrity"
"$PYTHON" scripts/dev/check_day34_artifacts.py

echo "DAY34 MASTER CHECK PASS"

