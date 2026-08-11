#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
python3 scripts/dev/day37_error_analysis_runner.py
python3 -m pytest -q qa-validation/automated-tests/research/test_day37_error_analysis.py
