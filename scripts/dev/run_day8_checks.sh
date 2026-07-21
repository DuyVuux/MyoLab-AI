#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

export PYTHONPATH="$ROOT/packages/semg-core:$ROOT/services/quality-gate-service/src:$ROOT/services/preprocessing-service/src:$ROOT/services/feature-extraction-service/src${PYTHONPATH:+:$PYTHONPATH}"

if [[ "${DAY8_FULL_REGRESSION:-0}" == "1" ]]; then
  if [[ -x scripts/dev/run_day7_checks.sh ]]; then
    echo "[1/10] Chạy full regression Day 7"
    bash scripts/dev/run_day7_checks.sh
  else
    echo "CẢNH BÁO: không tìm thấy scripts/dev/run_day7_checks.sh; bỏ qua full regression"
  fi
else
  echo "[1/10] Bỏ qua full regression Day 7; đặt DAY8_FULL_REGRESSION=1 để bật"
fi

echo "[2/10] Chạy core, config, service và analytical tests Day 8"
pytest -q \
  packages/semg-core/tests/test_features.py \
  services/feature-extraction-service/tests/test_time_domain_features.py \
  services/feature-extraction-service/tests/test_feature_config.py \
  services/feature-extraction-service/tests/test_feature_extractor.py \
  qa-validation/automated-tests/test_time_domain_feature_analytical.py

echo "[3/10] Kiểm chứng RMS/MAV bằng vector có nghiệm biết trước"
python scripts/data/verify_time_domain_features.py \
  --json-output qa-validation/evidence/day8-time-domain-feature-verification.json \
  --evidence-md qa-validation/evidence/day8-time-domain-feature-verification.md \
  --validation-md ai-core/validation-reports/analytical_validation_time_domain_features_v0.1.md

echo "[4/10] Chạy golden E2E đến RMS/MAV lần 1"
python scripts/data/run_time_domain_features.py \
  --manifest data-platform/synthetic-data/golden_signal_01.manifest.json \
  --json-out qa-validation/evidence/day8-time-domain-features.json \
  --csv-out qa-validation/evidence/day8-time-domain-features.csv \
  --expect-status completed \
  --expect-total-row-count 239 \
  --expect-computed-row-count 239 \
  --expect-not-computed-row-count 0

echo "[5/10] Chạy golden E2E lần 2 để kiểm tra deterministic hash"
python scripts/data/run_time_domain_features.py \
  --manifest data-platform/synthetic-data/golden_signal_01.manifest.json \
  --json-out qa-validation/evidence/day8-time-domain-features-rerun.json \
  --expect-status completed \
  --expect-total-row-count 239 \
  --expect-computed-row-count 239 \
  --expect-not-computed-row-count 0 \
  --quiet

echo "[6/10] Validate schemas, row contract và deterministic hash"
python - <<'PY'
import json
from pathlib import Path
from jsonschema import Draft202012Validator

root = Path.cwd()
result_schema = json.loads((root / "packages/common-schemas/json/time-domain-feature-result.schema.json").read_text(encoding="utf-8"))
row_schema = json.loads((root / "packages/common-schemas/json/feature-row.schema.json").read_text(encoding="utf-8"))
verification_schema = json.loads((root / "packages/common-schemas/json/time-domain-feature-verification.schema.json").read_text(encoding="utf-8"))
first = json.loads((root / "qa-validation/evidence/day8-time-domain-features.json").read_text(encoding="utf-8"))
second = json.loads((root / "qa-validation/evidence/day8-time-domain-features-rerun.json").read_text(encoding="utf-8"))
verification = json.loads((root / "qa-validation/evidence/day8-time-domain-feature-verification.json").read_text(encoding="utf-8"))
for schema in (result_schema, row_schema, verification_schema):
    Draft202012Validator.check_schema(schema)
Draft202012Validator(result_schema).validate(first)
Draft202012Validator(result_schema).validate(second)
Draft202012Validator(verification_schema).validate(verification)
row_validator = Draft202012Validator(row_schema)
for row in first["rows"]:
    row_validator.validate(row)
h1 = first["result_hash_sha256"]
h2 = second["result_hash_sha256"]
if h1 != h2:
    raise SystemExit(f"Feature result hash không deterministic: {h1} != {h2}")
serialized = json.dumps(first, ensure_ascii=False)
if "samples_uV" in serialized or "raw_samples" in serialized:
    raise SystemExit("Raw samples xuất hiện trong feature JSON")
print(f"Schema PASS; deterministic feature result hash={h1}")
PY

echo "[7/10] Kiểm tra sanity trend của synthetic generator"
python - <<'PY'
import json
from pathlib import Path
import statistics

payload = json.loads(Path("qa-validation/evidence/day8-time-domain-features.json").read_text(encoding="utf-8"))
rows = [row for row in payload["rows"] if row["status"] == "computed"]
rms = [row["features"]["rms"]["value"] for row in rows]
mav = [row["features"]["mav"]["value"] for row in rows]
first_n = 20
last_n = 20
first_rms = statistics.fmean(rms[:first_n])
last_rms = statistics.fmean(rms[-last_n:])
first_mav = statistics.fmean(mav[:first_n])
last_mav = statistics.fmean(mav[-last_n:])
if not (last_rms > first_rms and last_mav > first_mav):
    raise SystemExit(
        "Synthetic amplitude sanity trend không đạt: "
        f"RMS {first_rms}->{last_rms}, MAV {first_mav}->{last_mav}"
    )
print(
    "Synthetic amplitude sanity PASS; "
    f"RMS first/last={first_rms:.6f}/{last_rms:.6f}; "
    f"MAV first/last={first_mav:.6f}/{last_mav:.6f}"
)
print("Lưu ý: sanity trend của generator không phải fatigue evidence.")
PY

echo "[8/10] Đăng ký feature extractor v0.1 vào registry"
python scripts/dev/register_feature_extractor_v0_1.py

echo "[9/10] Kiểm tra artifact và safety invariants"
python scripts/dev/check_day8_artifacts.py

echo "[10/10] Hoàn tất"
echo "All Day 8 checks passed."
