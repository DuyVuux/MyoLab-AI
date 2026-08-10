#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="${PROJECT_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
cd "$PROJECT_ROOT"
python3 scripts/dev/validate_day09_single_contract.py
python3 -m pytest -q qa-validation/automated-tests/contracts/test_day09_mr4_single_contract.py
python3 scripts/dev/check_day09_artifacts.py
