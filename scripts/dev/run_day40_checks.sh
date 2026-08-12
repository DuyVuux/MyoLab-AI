#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/packages/semg-core:$ROOT/services/quality-gate-service/src:$ROOT/qa-validation/lib:$ROOT/packages${PYTHONPATH:+:$PYTHONPATH}"

PY_BIN="python3"
if [ -x "$ROOT/.venv/bin/python" ]; then
  PY_BIN="$ROOT/.venv/bin/python"
fi

echo "[1/5] DAY40 contract validator"
$PY_BIN scripts/dev/day40_contract_validator.py --repo-root "$ROOT"

echo "[2/5] DAY40 focused tests"
$PY_BIN -m pytest -q qa-validation/automated-tests/processing/test_day40_processing_profile_contract.py

echo "[3/5] cumulative QC/research/property regression"
$PY_BIN -m pytest -q \
  qa-validation/automated-tests/qc \
  qa-validation/automated-tests/research \
  qa-validation/property-tests \
  -k 'not test_43_no_day22_window_implementation'

echo "[4/5] Python/JSON/YAML parse checks"
$PY_BIN - <<'PY'
from pathlib import Path
import ast, json, yaml
root=Path.cwd()
for p in [
 root/'packages/semg-core/semg_core/processing/profile_contract.py',
 root/'scripts/dev/day40_contract_validator.py',
 root/'scripts/dev/check_day40_artifacts.py',
]: ast.parse(p.read_text(encoding='utf-8'))
json.loads((root/'packages/common-schemas/json/processing-profile.schema.json').read_text())
yaml.safe_load((root/'configs/processing/preprocessing-profiles.v0.1.yaml').read_text())
print('PARSE CHECK PASS')
PY

echo "[5/5] DAY40 artifact integrity"
$PY_BIN scripts/dev/check_day40_artifacts.py

echo "DAY40 MASTER CHECK PASS"
