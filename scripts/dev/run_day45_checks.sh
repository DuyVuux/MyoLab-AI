#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/packages/semg-core${PYTHONPATH:+:$PYTHONPATH}"
python3 scripts/dev/day45_evidence_runner.py
python3 scripts/dev/day45_contract_validator.py
python3 -m pytest -q qa-validation/automated-tests/processing/test_processing_lineage.py
# Convergence regression: every sibling branch and frozen DAY40 contract.
python3 -m pytest -q \
  qa-validation/automated-tests/processing/test_day40_processing_profile_contract.py \
  qa-validation/automated-tests/processing/test_bandpass.py \
  qa-validation/automated-tests/processing/test_notch.py \
  qa-validation/automated-tests/processing/test_envelope_masking.py \
  qa-validation/automated-tests/processing/test_normalization_eligibility.py

python3 scripts/dev/check_day45_artifacts.py
