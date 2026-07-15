#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

printf '\n[1/7] Verify Day 2 baseline when available\n'
if [[ -x scripts/dev/run_day2_checks.sh ]]; then
  bash scripts/dev/run_day2_checks.sh
else
  echo "INFO: scripts/dev/run_day2_checks.sh not found; continuing with Day 3 checks."
fi

printf '\n[2/7] Verify deterministic synthetic fixture and source hash\n'
python data-platform/synthetic-data/generate_synthetic_semg.py \
  --output-dir data-platform/synthetic-data \
  --verify-existing

printf '\n[3/7] Re-run Day 2 protocol compatibility check on the full fixture\n'
if [[ -f scripts/data/validate_signal_file.py ]]; then
  python scripts/data/validate_signal_file.py \
    --manifest data-platform/synthetic-data/golden_signal_01.manifest.json \
    --mode protocol \
    --protocol clinical/protocols/quad-isometric-60s.v0.1.yaml
else
  echo "INFO: Day 2 validator not present; protocol check skipped."
fi

printf '\n[4/7] Import full fixture into canonical representation\n'
python scripts/data/import_signal_session.py \
  --manifest data-platform/synthetic-data/golden_signal_01.manifest.json \
  --summary-out qa-validation/evidence/day3-normalized-summary.json

printf '\n[5/7] Validate normalized JSON summary schema\n'
python - <<'PY'
import json
from pathlib import Path
from jsonschema import Draft202012Validator

payload = json.loads(Path("qa-validation/evidence/day3-normalized-summary.json").read_text())
summary = payload["normalized_signal"]
schema = json.loads(Path("packages/common-schemas/json/normalized-signal-summary.schema.json").read_text())
errors = sorted(Draft202012Validator(schema).iter_errors(summary), key=lambda e: list(e.path))
if errors:
    for error in errors:
        print(error.message)
    raise SystemExit(1)
print("PASS: normalized signal summary matches JSON Schema")
PY

printf '\n[6/7] Run ingestion/core tests\n'
PYTHONPATH="packages/semg-core:services/signal-ingestion-service/src${PYTHONPATH:+:$PYTHONPATH}" \
  python -m pytest -q \
  services/signal-ingestion-service/tests \
  packages/semg-core/tests

printf '\n[7/7] Check Day 3 artifact inventory and safety markers\n'
python scripts/dev/check_day3_artifacts.py

printf '\nAll Day 3 checks passed.\n'
