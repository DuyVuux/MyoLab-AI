#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PYTHONDONTWRITEBYTECODE=1
cd "$ROOT"
python3 scripts/dev/validate_day05_privacy_gate.py
python3 scripts/dev/check_day05_artifacts.py
