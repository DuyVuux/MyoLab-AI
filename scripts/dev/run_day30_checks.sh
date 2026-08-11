#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(pwd)}"
export PYTHONDONTWRITEBYTECODE=1
cd "$ROOT"
echo "[1/4] DAY30 contract validation"
python3 scripts/dev/day30_contract_validator.py --repo-root "$ROOT"
echo "[2/4] DAY30 focused tests"
python3 -m pytest -q -p no:cacheprovider qa-validation/automated-tests/qc/test_qc_aggregation.py
echo "[3/4] Full QC suite available in current repository"
python3 -m pytest -q -p no:cacheprovider qa-validation/automated-tests/qc/
echo "[4/4] DAY30 artifact integrity"
python3 scripts/dev/check_day30_artifacts.py --repo-root "$ROOT"
echo "All DAY30 checks passed."
