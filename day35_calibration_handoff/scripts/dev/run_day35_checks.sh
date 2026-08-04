#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)";cd "$ROOT"
python -m compileall -q ai-core/calibration/day35
python - <<'PY'
import json
json.load(open("notebooks/Day35_Confidence_Calibration_Abstention.ipynb"))
print("NOTEBOOK_JSON_PASS")
PY
pytest -q qa-validation/automated-tests/test_day35.py
echo DAY35_CHECKS_PASS
