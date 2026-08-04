#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)";cd "$ROOT"
python -m compileall -q ai-core/personalization/day34
python - <<'PY'
import json
json.load(open("notebooks/Day34_Personalization_FewShot.ipynb"))
print("NOTEBOOK_JSON_PASS")
PY
pytest -q qa-validation/automated-tests/test_day34.py
echo DAY34_CHECKS_PASS
