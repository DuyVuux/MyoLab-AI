#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export PYTHONPATH="$ROOT/packages/semg-core:$ROOT/services/signal-ingestion-service/src:$ROOT/services/quality-gate-service/src:$ROOT/services/preprocessing-service/src:$ROOT/services/feature-extraction-service/src${PYTHONPATH:+:$PYTHONPATH}"

if [[ "${DAY10_FULL_REGRESSION:-0}" == "1" ]]; then
  echo "[1/9] Chạy full regression Day 9"
  bash scripts/dev/run_day9_checks.sh
else
  echo "[1/9] Bỏ qua full regression Day 9; đặt DAY10_FULL_REGRESSION=1 để bật"
fi

echo "[2/9] Chạy core/config/extractor tests"
pytest -q \
  packages/semg-core/tests/test_spectral_features.py \
  services/feature-extraction-service/tests/test_frequency_feature_config.py \
  services/feature-extraction-service/tests/test_frequency_feature_extractor.py

echo "[3/9] Kiểm chứng known-answer MDF/MNF"
python scripts/data/verify_mdf_mnf.py

echo "[4/9] Golden E2E lần 1"
python scripts/data/run_frequency_features.py \
  --manifest data-platform/synthetic-data/golden_signal_01.manifest.json \
  --json-out qa-validation/evidence/day10-frequency-features.json \
  --csv-out qa-validation/evidence/day10-frequency-features.csv \
  --expect-status completed \
  --expect-total-row-count 119 \
  --expect-computed-row-count 119 \
  --expect-not-computed-row-count 0

echo "[5/9] Golden E2E lần 2"
python scripts/data/run_frequency_features.py \
  --manifest data-platform/synthetic-data/golden_signal_01.manifest.json \
  --json-out qa-validation/evidence/day10-frequency-features-rerun.json \
  --expect-status completed \
  --expect-total-row-count 119 \
  --expect-computed-row-count 119 \
  --expect-not-computed-row-count 0 \
  --quiet

echo "[6/9] Upstream fail phải block"
python qa-validation/test-data/synthetic/generate_qc_fixtures.py \
  --source-manifest data-platform/synthetic-data/golden_signal_01.manifest.json \
  --output-dir qa-validation/test-data/synthetic \
  --overwrite >/dev/null
python scripts/data/run_frequency_features.py \
  --manifest qa-validation/test-data/synthetic/qc_fail_flatline.manifest.json \
  --json-out qa-validation/evidence/day10-frequency-features-blocked.json \
  --expect-status blocked \
  --expect-total-row-count 0 \
  --expect-computed-row-count 0 \
  --expect-not-computed-row-count 0 \
  --expect-reason FREQ_FEATURE_BLOCKED_BY_SPECTRAL \
  --quiet

echo "[7/9] Validate schemas/hash/invariants"
python scripts/dev/validate_day10_outputs.py

echo "[8/9] Đăng ký feature extractor"
python scripts/dev/register_frequency_features_v0_1.py

echo "[9/9] Artifact/safety checker"
python scripts/dev/check_day10_artifacts.py

echo "All Day 10 checks passed."
