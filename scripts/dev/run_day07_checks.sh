#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

export PYTHONDONTWRITEBYTECODE=1

python3 -m pytest -q -p no:cacheprovider \
  qa-validation/automated-tests/governance/test_day07_legacy_asset_audit.py

python3 scripts/dev/validate_day07_legacy_assets.py --tests-passed
python3 scripts/dev/check_day07_artifacts.py --write
python3 scripts/dev/check_day07_artifacts.py --verify

echo "DAY07_CHECKS_COMPLETE"
