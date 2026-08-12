#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PYTHON_BIN="${PYTHON:-$ROOT/.venv/bin/python}"
if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

"$PYTHON_BIN" -m pytest -q qa-validation/automated-tests/release/test_day51_m3_freeze.py qa-validation/automated-tests/evidence/test_day50_session_evidence_bundle.py
"$PYTHON_BIN" - <<'PY'
import json, hashlib, pathlib
r = pathlib.Path('.')
m = json.loads((r / 'qa-validation/evidence/day51-phase3-freeze-manifest.v0.1.json').read_text())
for e in m['artifacts']:
    assert hashlib.sha256((r / e['path']).read_bytes()).hexdigest() == e['sha256'], f"Mismatch in {e['path']}"
print('FREEZE_HASH_PASS', len(m['artifacts']))
PY

if grep -RIE '(patient[_ -]?name|first_name|last_name|secret[_ -]?key|api[_ -]?key|/home/|/mnt/data/)' \
    "$ROOT/docs/00-executive/milestones/M3-R-processing-metric-engine.md" \
    "$ROOT/docs/00-executive/rebaseline/day51-evidence-index.md" \
    "$ROOT/qa-validation/validation-reports/processing-metric-freeze-v0.1.md" >/dev/null; then
    echo "HYGIENE_FAIL"
    exit 1
fi
echo DAY51_VERIFY_PASS
