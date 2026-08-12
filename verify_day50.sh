#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PYTHON_BIN="${PYTHON:-$ROOT/.venv/bin/python}"
if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

"$PYTHON_BIN" -m py_compile "$ROOT/services/evidence-service/src/build_bundle.py"
"$PYTHON_BIN" - <<'PY' "$ROOT/packages/common-schemas/json/session-evidence-bundle.v0.1.schema.json" "$ROOT/qa-validation/evidence/day50-session-evidence-bundle.reference.json"
import json, sys
from jsonschema import Draft202012Validator
s = json.load(open(sys.argv[1]))
x = json.load(open(sys.argv[2]))
Draft202012Validator(s).validate(x)
print('SCHEMA_PASS')
PY
PYTHONPATH="$ROOT/services/evidence-service/src:$ROOT/packages/semg-core${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_BIN" -m pytest -q qa-validation/automated-tests/evidence/test_day50_session_evidence_bundle.py
if grep -RIE '(patient[_ -]?name|first_name|last_name|secret[_ -]?key|api[_ -]?key|/home/|/mnt/data/)' "$ROOT/docs/00-executive/day50" "$ROOT/docs/03-architecture/evidence-bundle-technology-extension.v0.1.md" "$ROOT/services/evidence-service" >/dev/null; then echo 'HYGIENE_FAIL'; exit 1; fi
echo DAY50_VERIFY_PASS
