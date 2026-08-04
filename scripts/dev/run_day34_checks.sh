#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)";cd "$ROOT"
uv run python -m compileall -q ai-core/personalization/day34
uv run python - <<'PY'
import json
json.load(open("notebooks/GRABMyo_Personalization_FewShot_Standalone_v2.ipynb"))
json.load(open("notebooks/Medeley_Personalization_FewShot_Standalone_v2.ipynb"))
print("NOTEBOOK_JSON_PASS")
PY
uv run pytest -q qa-validation/automated-tests/test_day34.py
echo DAY34_CHECKS_PASS
