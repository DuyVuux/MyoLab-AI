#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
fi

export PYTHONPATH="packages/semg-core:services/signal-ingestion-service/src:services/quality-gate-service/src:services/preprocessing-service/src${PYTHONPATH:+:$PYTHONPATH}"

printf '\n[1/8] Kiểm tra prerequisite Day 5\n'
if [[ "${DAY6_FULL_REGRESSION:-0}" == "1" ]]; then
  bash scripts/dev/run_day5_checks.sh
else
  python -m pytest -q \
    packages/semg-core/tests/test_preprocessing.py \
    services/preprocessing-service/tests
fi

printf '\n[2/8] Chạy analytical tests Day 6\n'
python -m pytest -q qa-validation/automated-tests/test_preprocessing_analytical.py

mkdir -p qa-validation/evidence ai-core/validation-reports mlops/registry

printf '\n[3/8] Sinh verification report JSON/Markdown\n'
python scripts/data/verify_preprocess_v0_1.py \
  --config services/preprocessing-service/configs/preprocess_v0.1.yaml \
  --profile qa-validation/configs/preprocess_verification_v0.1.yaml \
  --json-output qa-validation/evidence/day6-preprocessing-verification.json \
  --evidence-md qa-validation/evidence/day6-filter-verification.md \
  --validation-md ai-core/validation-reports/analytical_validation_preprocessing_v0.1.md

printf '\n[4/8] Validate verification JSON theo schema\n'
python - <<'PYSCHEMA'
import json
from pathlib import Path
from jsonschema import Draft202012Validator

schema = json.loads(Path('packages/common-schemas/json/preprocessing-verification-report.schema.json').read_text(encoding='utf-8'))
payload = json.loads(Path('qa-validation/evidence/day6-preprocessing-verification.json').read_text(encoding='utf-8'))
errors = sorted(Draft202012Validator(schema).iter_errors(payload), key=lambda e: list(e.path))
if errors:
    raise SystemExit(f'Schema validation failed: {errors[0].message}')
print('PASS preprocessing-verification-report schema')
PYSCHEMA

printf '\n[5/8] Capture DSP environment\n'
python scripts/dev/capture_dsp_environment.py \
  --output qa-validation/evidence/day6-dsp-environment.json

printf '\n[6/8] Freeze preprocess_v0.1 vào registry\n'
python scripts/dev/freeze_preprocess_v0_1.py \
  --verification qa-validation/evidence/day6-preprocessing-verification.json \
  --environment qa-validation/evidence/day6-dsp-environment.json \
  --registry mlops/registry/preprocessing_configs.yaml

printf '\n[7/8] Xác minh config chưa thay đổi sau freeze\n'
python - <<'PYFREEZE'
from pathlib import Path
import hashlib
import yaml

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

registry = yaml.safe_load(Path('mlops/registry/preprocessing_configs.yaml').read_text(encoding='utf-8'))
entry = next(item for item in registry['preprocessing_configs'] if item['config_id'] == 'preprocess_v0.1')
actual = sha(entry['config']['path'])
if actual != entry['config']['sha256']:
    raise SystemExit(f'Config hash mismatch after freeze: {actual} != {entry["config"]["sha256"]}')
print('PASS frozen config hash:', actual)
PYFREEZE

printf '\n[8/8] Artifact and safety check\n'
python scripts/dev/check_day6_artifacts.py

printf '\nAll Day 6 checks passed.\n'
