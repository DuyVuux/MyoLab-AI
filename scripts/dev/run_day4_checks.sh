#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

printf '\n[1/9] Verify Day 3 prerequisite and source hash\n'
python data-platform/synthetic-data/generate_synthetic_semg.py \
  --output-dir data-platform/synthetic-data \
  --verify-existing >/tmp/day4-day3-hash.json
cat /tmp/day4-day3-hash.json
if [[ "${DAY4_FULL_REGRESSION:-0}" == "1" ]]; then
  echo "DAY4_FULL_REGRESSION=1: running the complete Day 3 checker."
  bash scripts/dev/run_day3_checks.sh
else
  echo "INFO: Day 1-3 unit/integration tests are included in step 3."
fi

printf '\n[2/9] Generate deterministic Day 4 QC fixtures\n'
python qa-validation/test-data/synthetic/generate_qc_fixtures.py \
  --source-manifest data-platform/synthetic-data/golden_signal_01.manifest.json \
  --output-dir qa-validation/test-data/synthetic \
  --overwrite >/tmp/day4-qc-fixtures.json
cat /tmp/day4-qc-fixtures.json

printf '\n[3/9] Run QC/core/ingestion tests\n'
PYTHONPATH="packages/semg-core:services/signal-ingestion-service/src:services/quality-gate-service/src${PYTHONPATH:+:$PYTHONPATH}" \
  python -m pytest -q \
  packages/semg-core/tests \
  services/signal-ingestion-service/tests \
  services/quality-gate-service/tests

mkdir -p qa-validation/evidence

printf '\n[4/9] Golden session must pass basic QC while MFCV remains unavailable\n'
python scripts/data/run_signal_qc.py \
  --manifest data-platform/synthetic-data/golden_signal_01.manifest.json \
  --expect-status pass \
  --expect-mfcv-reason MFCV_LINEAR_ARRAY_NOT_CONFIRMED \
  --output qa-validation/evidence/day4-qc-pass.json \
  --quiet

printf '\n[5/9] Critical negative fixtures must abstain\n'
python scripts/data/run_signal_qc.py \
  --manifest qa-validation/test-data/synthetic/qc_fail_nonfinite.manifest.json \
  --expect-status fail \
  --expect-reason NONFINITE_RATIO_EXCESSIVE \
  --output qa-validation/evidence/day4-qc-fail-nonfinite.json \
  --quiet
python scripts/data/run_signal_qc.py \
  --manifest qa-validation/test-data/synthetic/qc_fail_flatline.manifest.json \
  --expect-status fail \
  --expect-reason FLATLINE_EXCESSIVE \
  --output qa-validation/evidence/day4-qc-fail-flatline.json \
  --quiet
python scripts/data/run_signal_qc.py \
  --manifest qa-validation/test-data/synthetic/qc_fail_short_duration.manifest.json \
  --expect-status fail \
  --expect-reason ACTIVE_DURATION_TOO_SHORT \
  --output qa-validation/evidence/day4-qc-fail-short-duration.json \
  --quiet

printf '\n[6/9] Provisional heuristic fixtures must remain warning-only\n'
python scripts/data/run_signal_qc.py \
  --manifest qa-validation/test-data/synthetic/qc_warning_clipping.manifest.json \
  --expect-status warning \
  --expect-reason CLIPPING_SUSPECTED \
  --output qa-validation/evidence/day4-qc-warning-clipping.json \
  --quiet
python scripts/data/run_signal_qc.py \
  --manifest qa-validation/test-data/synthetic/qc_warning_powerline.manifest.json \
  --expect-status warning \
  --expect-reason POWERLINE_NOISE_HIGH \
  --output qa-validation/evidence/day4-qc-warning-powerline.json \
  --quiet
python scripts/data/run_signal_qc.py \
  --manifest qa-validation/test-data/synthetic/qc_warning_motion_artifact.manifest.json \
  --expect-status warning \
  --expect-reason MOTION_ARTIFACT_HIGH \
  --output qa-validation/evidence/day4-qc-warning-motion.json \
  --quiet

printf '\n[7/9] Validate every generated QC JSON against the shared schema\n'
python - <<'PY'
import json
from pathlib import Path
from jsonschema import Draft202012Validator

schema = json.loads(Path("packages/common-schemas/json/qc-result.schema.json").read_text())
validator = Draft202012Validator(schema)
paths = sorted(Path("qa-validation/evidence").glob("day4-qc-*.json"))
if not paths:
    raise SystemExit("No Day 4 QC evidence JSON files found")
for path in paths:
    payload = json.loads(path.read_text())
    errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.path))
    if errors:
        print(f"SCHEMA FAIL: {path}")
        for error in errors:
            print(f"- {list(error.path)}: {error.message}")
        raise SystemExit(1)
    if payload["analysis_allowed"] is False and payload["abstention"]["required"] is not True:
        raise SystemExit(f"Abstention invariant failed: {path}")
print(f"PASS: {len(paths)} QC evidence files match qc-result.v0.1")
PY

printf '\n[8/9] Check artifact inventory and safety markers\n'
python scripts/dev/check_day4_artifacts.py

printf '\n[9/9] Summary\n'
python - <<'PY'
import json
from pathlib import Path
for path in sorted(Path("qa-validation/evidence").glob("day4-qc-*.json")):
    payload = json.loads(path.read_text())
    print(
        f"{path.name}: status={payload['status']} "
        f"analysis_allowed={payload['analysis_allowed']} "
        f"reasons={payload['reason_codes']} "
        f"mfcv={payload['mfcv']['eligible']}"
    )
PY

printf '\nAll Day 4 checks passed.\n'
