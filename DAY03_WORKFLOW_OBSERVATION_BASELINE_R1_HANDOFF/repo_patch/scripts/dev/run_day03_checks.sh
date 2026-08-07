#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
REPORT="${PROJECT_ROOT}/qa-validation/evidence/day03-validation-report.json"

export PYTHONDONTWRITEBYTECODE=1

echo "[DAY03] Validate contracts and evidence state"
python3 "${SCRIPT_DIR}/validate_day03_workflow_observation.py"

echo "[DAY03] Verify managed artifact hashes"
python3 "${SCRIPT_DIR}/check_day03_artifacts.py"

echo "[DAY03] Run automated governance tests"
set +e
python3 -m pytest \
  -q \
  -p no:cacheprovider \
  "${PROJECT_ROOT}/qa-validation/automated-tests/governance/test_day03_workflow_observation.py"
PYTEST_RC=$?
set -e

python3 - <<'PY' "${REPORT}" "${PYTEST_RC}"
import json
import sys
from pathlib import Path

report_path = Path(sys.argv[1])
pytest_rc = int(sys.argv[2])
report = json.loads(report_path.read_text(encoding="utf-8"))
report["tests_expected"] = 20
report["tests_passed"] = 20 if pytest_rc == 0 else 0
report["pytest_return_code"] = pytest_rc
report["engineering_validation_passed"] = pytest_rc == 0 and not report["validation_failures"]
report_path.write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
PY

if [[ "${PYTEST_RC}" -ne 0 ]]; then
  echo "[DAY03] Automated tests failed"
  exit "${PYTEST_RC}"
fi

echo "[DAY03] Gate report"
python3 - <<'PY' "${REPORT}"
import json
import sys
from pathlib import Path

report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(json.dumps(report, ensure_ascii=False, indent=2))

if report["status"] == "BLOCKED_WITH_EVIDENCE":
    print(
        "[DAY03] Engineering PASS; evidence gate remains BLOCKED_WITH_EVIDENCE "
        "until reviewed site observations are added."
    )
elif report["status"] == "GO_FOR_DAY_04":
    print("[DAY03] GO_FOR_DAY_04")
else:
    raise SystemExit("Unexpected DAY03 gate status")
PY
