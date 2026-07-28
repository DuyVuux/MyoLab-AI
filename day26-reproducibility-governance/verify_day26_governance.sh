#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

PYTHONDONTWRITEBYTECODE=1 python scripts/validate_day26_governance.py
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider tests

echo "Verification complete: validation/VALIDATION_REPORT.md"
