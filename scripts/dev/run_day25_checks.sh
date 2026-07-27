#!/usr/bin/env bash
# Compatibility entry point for the revised research-grounded Day 25 pack.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exec bash "$ROOT/scripts/dev/run_day25_research_checks.sh"
