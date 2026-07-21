#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

export PYTHONPATH="$ROOT/packages/semg-core:$ROOT/services/quality-gate-service/src:$ROOT/services/preprocessing-service/src:$ROOT/services/feature-extraction-service/src${PYTHONPATH:+:$PYTHONPATH}"

if [[ "${DAY7_FULL_REGRESSION:-0}" == "1" ]]; then
  if [[ -x scripts/dev/run_day6_checks.sh ]]; then
    echo "[1/8] Chạy full regression Day 6"
    bash scripts/dev/run_day6_checks.sh
  else
    echo "CẢNH BÁO: không tìm thấy scripts/dev/run_day6_checks.sh; bỏ qua full regression"
  fi
else
  echo "[1/8] Bỏ qua full regression Day 6; đặt DAY7_FULL_REGRESSION=1 để bật"
fi

echo "[2/8] Chạy unit, analytical và pipeline tests Day 7"
pytest -q \
  packages/semg-core/tests/test_windowing.py \
  services/feature-extraction-service/tests/test_windowing_pipeline.py \
  qa-validation/automated-tests/test_windowing_analytical.py

echo "[3/8] Kiểm chứng geometry tính tay cho hai profile"
python scripts/data/verify_window_geometry.py \
  --config services/feature-extraction-service/configs/windowing_v0.1.yaml \
  --json-out qa-validation/evidence/day7-window-geometry.json \
  --markdown-out qa-validation/evidence/day7-windowing-evidence.md

echo "[4/8] Chạy end-to-end golden fixture lần 1"
python scripts/data/run_signal_windowing.py \
  --manifest data-platform/synthetic-data/golden_signal_01.manifest.json \
  --summary-out qa-validation/evidence/day7-windowing-result.json \
  --expect-status completed \
  --expect-time-window-count 239 \
  --expect-frequency-window-count 119 \
  --expect-time-valid-window-count 239 \
  --expect-frequency-valid-window-count 119

echo "[5/8] Chạy end-to-end golden fixture lần 2"
python scripts/data/run_signal_windowing.py \
  --manifest data-platform/synthetic-data/golden_signal_01.manifest.json \
  --summary-out qa-validation/evidence/day7-windowing-result-rerun.json \
  --expect-status completed \
  --expect-time-window-count 239 \
  --expect-frequency-window-count 119 \
  --expect-time-valid-window-count 239 \
  --expect-frequency-valid-window-count 119 \
  --quiet

echo "[6/8] Validate JSON Schema và plan hash determinism"
python - <<'PY'
import json
from pathlib import Path
from jsonschema import Draft202012Validator

root = Path.cwd()
schema = json.loads((root / "packages/common-schemas/json/windowing-result.schema.json").read_text(encoding="utf-8"))
first = json.loads((root / "qa-validation/evidence/day7-windowing-result.json").read_text(encoding="utf-8"))
second = json.loads((root / "qa-validation/evidence/day7-windowing-result-rerun.json").read_text(encoding="utf-8"))
Draft202012Validator.check_schema(schema)
Draft202012Validator(schema).validate(first)
Draft202012Validator(schema).validate(second)
h1 = first["plan"]["plan_hash_sha256"]
h2 = second["plan"]["plan_hash_sha256"]
if h1 != h2:
    raise SystemExit(f"Plan hash không deterministic: {h1} != {h2}")
serialized = json.dumps(first, ensure_ascii=False)
if "samples_uV" in serialized:
    raise SystemExit("Raw samples xuất hiện trong JSON")
profiles = {item["profile_id"]: item for item in first["plan"]["profiles"]}
assert profiles["time_domain"]["windowing"]["window_count"] == 239
assert profiles["frequency_domain"]["windowing"]["window_count"] == 119
print(f"JSON Schema PASS; deterministic plan hash={h1}")
PY

echo "[7/8] Kiểm tra artifact và safety invariants"
python scripts/dev/check_day7_artifacts.py

echo "[8/8] Hoàn tất"
echo "All Day 7 checks passed."
