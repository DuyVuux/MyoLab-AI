#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PYTHON_BIN="${PYTHON:-$ROOT/.venv/bin/python}"
if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

"$PYTHON_BIN" -m py_compile services/review-service/src/domain/state_machine.py
"$PYTHON_BIN" -m pytest -q qa-validation/automated-tests/review/test_day52_human_review_state_machine.py qa-validation/automated-tests/release/test_day51_m3_freeze.py qa-validation/automated-tests/evidence/test_day50_session_evidence_bundle.py
"$PYTHON_BIN" - <<'PY'
import yaml, json, hashlib, pathlib
r = pathlib.Path('.')
x = yaml.safe_load((r / 'packages/common-schemas/state-machines/human-review-state-machine.v0.2-research.yaml').read_text())
assert len(x['states']) == 8 and x['clinical_interpretation'] is False
f = json.loads((r / 'qa-validation/evidence/day51-phase3-freeze-manifest.v0.1.json').read_text())
for e in f['artifacts']:
    assert hashlib.sha256((r / e['path']).read_bytes()).hexdigest() == e['sha256'], f"Mismatch in {e['path']}"
print('M3R_FREEZE_INTACT', len(f['artifacts']))
PY

if grep -RIE '(patient[_ -]?name|first_name|last_name|secret[_ -]?key|api[_ -]?key|/home/|/mnt/data/)' "$ROOT/packages/common-schemas/state-machines" "$ROOT/services/review-service" "$ROOT/qa-validation/safety" >/dev/null; then
    echo "HYGIENE_FAIL"
    exit 1
fi
echo DAY52_VERIFY_PASS
