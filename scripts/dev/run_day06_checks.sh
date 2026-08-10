#!/usr/bin/env bash
    set -euo pipefail
    ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
    export PYTHONDONTWRITEBYTECODE=1
    cd "$ROOT"
    python3 scripts/dev/validate_day06_evidence_inventory.py
    python3 scripts/dev/check_day06_artifacts.py
