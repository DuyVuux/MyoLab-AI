#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

export PYTHONPATH="${REPO_ROOT}/packages/semg-core:${REPO_ROOT}/services/quality-gate-service/src:${PYTHONPATH:-}"

echo "=== STEP 1: Running DAY46 RMS/MAV Amplitude Metric Tests ==="
python3 -m pytest -v "${REPO_ROOT}/qa-validation/automated-tests/metrics/test_day46_amplitude_metrics.py"

echo "=== STEP 2: Running DAY47 Welch PSD & MDF/MNF Spectral Metric Tests ==="
python3 -m pytest -v "${REPO_ROOT}/qa-validation/automated-tests/metrics/test_day47_spectral.py"

echo "=== STEP 3: Running DAY48 Activation Timing Metric Tests ==="
python3 -m pytest -v "${REPO_ROOT}/qa-validation/automated-tests/metrics/test_day48_activation_timing.py"

echo "=== STEP 4: Running DAY49 MFCV Feasibility & Gate Tests ==="
python3 -m pytest -v "${REPO_ROOT}/qa-validation/automated-tests/metrics/test_day49_mfcv.py"

echo "=== STEP 5: Running Upstream DAY45 Lineage Regression Suite ==="
python3 -m pytest -v "${REPO_ROOT}/qa-validation/automated-tests/processing/test_processing_lineage.py"

echo "=== STEP 6: Verifying Artifact Integrity Across DAY46-49 ==="
# DAY46
test -f "${REPO_ROOT}/packages/semg-core/semg_core/metrics/amplitude.py"
test -f "${REPO_ROOT}/configs/metrics/metric-registry.v0.1.yaml"
test -f "${REPO_ROOT}/qa-validation/evidence/day46-rms-mav-evidence.json"

# DAY47
test -f "${REPO_ROOT}/packages/semg-core/semg_core/metrics/spectral.py"
test -f "${REPO_ROOT}/configs/metrics/psd.v0.1.yaml"
test -f "${REPO_ROOT}/qa-validation/evidence/day47-spectral-known-answer.json"

# DAY48
test -f "${REPO_ROOT}/packages/semg-core/semg_core/metrics/activation_timing.py"
test -f "${REPO_ROOT}/packages/common-schemas/json/activation-timing-eligibility.schema.json"
test -f "${REPO_ROOT}/qa-validation/evidence/day48-activation-timing-known-answer.json"

# DAY49
test -f "${REPO_ROOT}/services/quality-gate-service/src/application/mfcv_eligibility.py"
test -f "${REPO_ROOT}/clinical/mfcv/mfcv-eligibility-research-v0.2.yaml"
test -f "${REPO_ROOT}/qa-validation/evidence/day49-synthetic-known-delay-evidence.json"

echo "=== ALL DAY46–49 BATCH CHECKS PASSED SUCCESSFULLY ==="
