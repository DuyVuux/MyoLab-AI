#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

export PYTHONPATH="${REPO_ROOT}/packages/semg-core:${PYTHONPATH:-}"

echo "=== STEP 1: Running DAY46 Metric Registry Tests ==="
python3 -m pytest -v "${REPO_ROOT}/qa-validation/automated-tests/metrics/test_day46_amplitude_metrics.py"

echo "=== STEP 2: Running DAY45 Processing Provenance Regression Tests ==="
python3 -m pytest -v "${REPO_ROOT}/qa-validation/automated-tests/processing/test_processing_lineage.py"

echo "=== STEP 3: Verifying DAY46 Artifact Integrity ==="
test -f "${REPO_ROOT}/packages/semg-core/semg_core/metrics/amplitude.py"
test -f "${REPO_ROOT}/packages/semg-core/semg_core/metrics/__init__.py"
test -f "${REPO_ROOT}/configs/metrics/metric-registry.v0.1.yaml"
test -f "${REPO_ROOT}/qa-validation/analytical/rms-mav-known-answer.md"
test -f "${REPO_ROOT}/qa-validation/evidence/day46-rms-mav-evidence.json"

echo "=== ALL DAY46 CHECKS PASSED ==="
