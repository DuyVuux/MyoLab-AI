#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

printf '\n[1/9] Kiểm tra prerequisite Day 4 và tạo lại fixture deterministic\n'
python data-platform/synthetic-data/generate_synthetic_semg.py \
  --output-dir data-platform/synthetic-data \
  --verify-existing >/tmp/day5-day3-hash.json
cat /tmp/day5-day3-hash.json
python qa-validation/test-data/synthetic/generate_qc_fixtures.py \
  --source-manifest data-platform/synthetic-data/golden_signal_01.manifest.json \
  --output-dir qa-validation/test-data/synthetic \
  --overwrite >/tmp/day5-qc-fixtures.json

if [[ "${DAY5_FULL_REGRESSION:-0}" == "1" ]]; then
  echo "DAY5_FULL_REGRESSION=1: chạy toàn bộ checker Day 4."
  bash scripts/dev/run_day4_checks.sh
fi

printf '\n[2/9] Chạy unit/integration tests Day 1-5\n'
PYTHONPATH="packages/semg-core:services/signal-ingestion-service/src:services/quality-gate-service/src:services/preprocessing-service/src${PYTHONPATH:+:$PYTHONPATH}" \
  python -m pytest -q \
  packages/semg-core/tests \
  services/signal-ingestion-service/tests \
  services/quality-gate-service/tests \
  services/preprocessing-service/tests

mkdir -p qa-validation/evidence

printf '\n[3/9] Verify đáp ứng tần số lý thuyết\n'
python scripts/data/verify_preprocessing_response.py \
  --output qa-validation/evidence/day5-frequency-response.json >/tmp/day5-frequency-response.stdout
cat /tmp/day5-frequency-response.stdout

printf '\n[4/9] Golden session: band-pass áp dụng, notch bỏ qua\n'
python scripts/data/run_signal_preprocessing.py \
  --manifest data-platform/synthetic-data/golden_signal_01.manifest.json \
  --expect-status completed \
  --expect-step mean_center \
  --expect-step butterworth_bandpass \
  --expect-skipped-step conditional_powerline_notch \
  --summary-out qa-validation/evidence/day5-preprocess-golden.json \
  --npz-out qa-validation/evidence/day5-preprocess-golden.npz \
  --quiet

printf '\n[5/9] Power-line warning: notch 50 Hz phải được áp dụng\n'
python scripts/data/run_signal_preprocessing.py \
  --manifest qa-validation/test-data/synthetic/qc_warning_powerline.manifest.json \
  --expect-status completed \
  --expect-step conditional_powerline_notch \
  --summary-out qa-validation/evidence/day5-preprocess-powerline.json \
  --quiet

printf '\n[6/9] QC fail: preprocessing phải bị block\n'
python scripts/data/run_signal_preprocessing.py \
  --manifest qa-validation/test-data/synthetic/qc_fail_flatline.manifest.json \
  --expect-status blocked \
  --expect-reason PREPROCESSING_BLOCKED_BY_QC \
  --summary-out qa-validation/evidence/day5-preprocess-blocked.json \
  --quiet

printf '\n[7/9] Validate ba JSON result theo schema\n'
python - <<'PYSCHEMA'
import json
from pathlib import Path
from jsonschema import Draft202012Validator

schema = json.loads(Path('packages/common-schemas/json/preprocessing-result.schema.json').read_text(encoding='utf-8'))
validator = Draft202012Validator(schema)
for name in (
    'qa-validation/evidence/day5-preprocess-golden.json',
    'qa-validation/evidence/day5-preprocess-powerline.json',
    'qa-validation/evidence/day5-preprocess-blocked.json',
):
    payload = json.loads(Path(name).read_text(encoding='utf-8'))
    errors = sorted(validator.iter_errors(payload), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f'{name}: schema validation failed: {errors[0].message}')
    print(f'PASS schema: {name}')
PYSCHEMA

printf '\n[8/9] Kiểm tra output hash deterministic\n'
python scripts/data/run_signal_preprocessing.py \
  --manifest data-platform/synthetic-data/golden_signal_01.manifest.json \
  --summary-out /tmp/day5-preprocess-rerun.json \
  --quiet
python - <<'PYHASH'
import json
from pathlib import Path
first = json.loads(Path('qa-validation/evidence/day5-preprocess-golden.json').read_text(encoding='utf-8'))
second = json.loads(Path('/tmp/day5-preprocess-rerun.json').read_text(encoding='utf-8'))
a = first['signal_summary']['combined_output_hash_sha256']
b = second['signal_summary']['combined_output_hash_sha256']
if a != b:
    raise SystemExit(f'Output hash mismatch: {a} != {b}')
print('PASS deterministic hash:', a)
PYHASH

printf '\n[9/9] Artifact check\n'
python scripts/dev/check_day5_artifacts.py

printf '\nAll Day 5 checks passed.\n'
