#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-$ROOT/.venv/bin/python3}"
if [ ! -f "$PYTHON" ]; then
  PYTHON="python3"
fi

export PYTHONPATH="${DAY38_TEST_SUPPORT_PATH:-$ROOT/packages/semg-core}:$ROOT/services/quality-gate-service/src:$ROOT/services/signal-ingestion-service/src${PYTHONPATH:+:$PYTHONPATH}"

"$PYTHON" -m pytest -q qa-validation/property-tests/test_qc_state_properties_v0_2.py
"$PYTHON" -m pytest -q qa-validation/automated-tests/qc qa-validation/property-tests --deselect qa-validation/automated-tests/qc/test_day21_qc_taxonomy.py::test_43_no_day22_window_implementation
"$PYTHON" - <<'PY'
from pathlib import Path
import hashlib, json
root = Path('.')
f = json.loads((root/'qa-validation/evidence/day38-qc-freeze-manifest.v0.2.json').read_text())
for x in f['items']:
    p = root / x['path']
    assert hashlib.sha256(p.read_bytes()).hexdigest() == x['sha256'], f"Mismatch on {x['path']}"
print('DAY38 HASH FREEZE PASS', len(f['items']))
PY
