#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

export PYTHONDONTWRITEBYTECODE=1

python3 scripts/dev/validate_day04_quality_taxonomy.py

set +e
python3 -m pytest -q -p no:cacheprovider \
  qa-validation/automated-tests/governance/test_day04_quality_taxonomy.py
PYTEST_RC=$?
set -e

python3 - "$PYTEST_RC" <<'PY'
from __future__ import annotations
import json
import sys
from pathlib import Path

rc = int(sys.argv[1])
path = Path('qa-validation/evidence/day04-validation-report.json')
report = json.loads(path.read_text(encoding='utf-8'))
report['pytest_return_code'] = rc
report['tests_passed'] = 21 if rc == 0 else None
report['engineering_validation_passed'] = report['engineering_validation_passed'] and rc == 0
if rc != 0:
    report['status'] = 'BLOCKED_WITH_VALIDATION_FAILURE'
path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
PY

python3 scripts/dev/check_day04_artifacts.py
cat qa-validation/evidence/day04-validation-report.json
