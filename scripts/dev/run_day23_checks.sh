#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(pwd)}"
export PYTHONDONTWRITEBYTECODE=1
export PYTEST_ADDOPTS="${PYTEST_ADDOPTS:-} -p no:cacheprovider"
python3 "$ROOT/scripts/dev/day23_contract_validator.py" --repo-root "$ROOT"
python3 -m pytest -q "$ROOT/qa-validation/automated-tests/qc/test_dropout_detector.py"
echo "DAY23 checks PASS"
