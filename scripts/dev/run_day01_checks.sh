#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
export PYTHONDONTWRITEBYTECODE=1

echo "[DAY01] 1/5 requirement/schema/governance validation"
python3 "${SCRIPT_DIR}/validate_day01_requirements.py" --repo-root "${REPO_ROOT}"

echo "[DAY01] 2/5 generate deterministic artifact manifest"
python3 "${SCRIPT_DIR}/check_day01_artifacts.py" --repo-root "${REPO_ROOT}" --write-manifest

echo "[DAY01] 3/5 pytest acceptance controls"
python3 -m pytest -q -p no:cacheprovider \
  "${REPO_ROOT}/qa-validation/automated-tests/governance/test_day01_requirements_rebaseline.py"

echo "[DAY01] 4/5 finalize validation report"
python3 "${SCRIPT_DIR}/validate_day01_requirements.py" --repo-root "${REPO_ROOT}" --tests-passed

echo "[DAY01] 5/5 verify artifact manifest"
python3 "${SCRIPT_DIR}/check_day01_artifacts.py" --repo-root "${REPO_ROOT}" --verify-manifest

echo "[DAY01] PASS"
