#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

export PYTHONUNBUFFERED=1
# Giới hạn BLAS/OpenMP threads để checker ổn định trên laptop/CI nhỏ.
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export MALLOC_ARENA_MAX=2
export PYTHONPATH="$ROOT/packages/semg-core:$ROOT/services/signal-ingestion-service/src:$ROOT/services/quality-gate-service/src:$ROOT/services/preprocessing-service/src:$ROOT/services/feature-extraction-service/src${PYTHONPATH:+:$PYTHONPATH}"

if [[ "${DAY9_FULL_REGRESSION:-0}" == "1" ]]; then
  if [[ -x scripts/dev/run_day8_checks.sh ]]; then
    echo "[1/11] Chạy full regression Day 8"
    bash scripts/dev/run_day8_checks.sh
  else
    echo "CẢNH BÁO: không tìm thấy scripts/dev/run_day8_checks.sh; bỏ qua full regression"
  fi
else
  echo "[1/11] Bỏ qua full regression Day 8; đặt DAY9_FULL_REGRESSION=1 để bật"
fi

echo "[2/11] Chạy core, config, service và analytical tests Day 9"
pytest -q \
  packages/semg-core/tests/test_spectral.py \
  services/feature-extraction-service/tests/test_spectral_config.py \
  services/feature-extraction-service/tests/test_frequency_domain.py \
  services/feature-extraction-service/tests/test_spectral_estimator.py \
  qa-validation/automated-tests/test_spectral_estimation_analytical.py

echo "[3/11] Kiểm chứng DFT/FFT/PSD/Hann/Parseval/scale bằng synthetic signals"
python scripts/data/verify_spectral_estimation.py \
  --json-output qa-validation/evidence/day9-spectral-verification.json \
  --evidence-md qa-validation/evidence/day9-spectral-verification.md \
  --validation-md ai-core/validation-reports/analytical_validation_spectral_estimation_v0.1.md

COMMON_EXPECTATIONS=(
  --expect-status completed
  --expect-total-row-count 119
  --expect-computed-row-count 119
  --expect-not-computed-row-count 0
  --expect-frequency-bin-count 381
)

echo "[4/11] Chạy golden E2E đến Welch PSD lần 1"
python scripts/data/run_spectral_estimation.py \
  --manifest data-platform/synthetic-data/golden_signal_01.manifest.json \
  --json-out qa-validation/evidence/day9-spectral-estimation.json \
  --csv-out qa-validation/evidence/day9-spectral-estimation.csv \
  "${COMMON_EXPECTATIONS[@]}"

echo "[5/11] Chạy golden E2E lần 2 để kiểm tra deterministic hash"
python scripts/data/run_spectral_estimation.py \
  --manifest data-platform/synthetic-data/golden_signal_01.manifest.json \
  --json-out qa-validation/evidence/day9-spectral-estimation-rerun.json \
  "${COMMON_EXPECTATIONS[@]}" \
  --quiet

echo "[6/11] Tạo fixture fail và xác nhận upstream block spectral stage"
python qa-validation/test-data/synthetic/generate_qc_fixtures.py \
  --source-manifest data-platform/synthetic-data/golden_signal_01.manifest.json \
  --output-dir qa-validation/test-data/synthetic \
  --overwrite >/dev/null
python scripts/data/run_spectral_estimation.py \
  --manifest qa-validation/test-data/synthetic/qc_fail_flatline.manifest.json \
  --json-out qa-validation/evidence/day9-spectral-blocked.json \
  --expect-status blocked \
  --expect-total-row-count 0 \
  --expect-computed-row-count 0 \
  --expect-not-computed-row-count 0 \
  --expect-reason SPECTRAL_ESTIMATION_BLOCKED_BY_WINDOWING \
  --quiet

echo "[7/11] Validate JSON Schemas, shared axis và deterministic result hash"
python scripts/dev/validate_day9_outputs.py

echo "[8/11] Spectral invariants đã được kiểm tra trong validate_day9_outputs.py"

echo "[9/11] Đăng ký spectral_estimation_v0.1 vào registry"
python scripts/dev/register_spectral_estimator_v0_1.py

echo "[10/11] Kiểm tra artifact và safety invariants"
python scripts/dev/check_day9_artifacts.py

echo "[11/11] Hoàn tất"
echo "All Day 9 checks passed."
