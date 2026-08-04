#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)";cd "$ROOT"
python -m compileall -q ai-core/context/day36
pytest -q qa-validation/automated-tests/test_day36.py
echo DAY36_CHECKS_PASS
