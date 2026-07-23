from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED = [
    "docs/plans/DAY20_EXECUTION_PLAN.md",
    "apps/web-portal/src/app/sessions/Day20SessionRoutes.tsx",
    "apps/web-portal/src/schemas/session-intake.schema.ts",
    "apps/web-portal/src/schemas/import-workflow.schema.ts",
    "apps/web-portal/src/schemas/channel-mapping.schema.ts",
    "apps/web-portal/src/schemas/preflight.schema.ts",
    "apps/web-portal/src/schemas/calibration.schema.ts",
    "apps/web-portal/src/schemas/quality-gate.schema.ts",
    "apps/web-portal/src/schemas/analysis-handoff.schema.ts",
    "apps/web-portal/src/lib/session-intake-client.ts",
    "services/api-server/src/mock_api/day20_app.py",
    "qa-validation/requirements/day20-acceptance-criteria.md",
]
missing = [relative for relative in REQUIRED if not (ROOT / relative).is_file()]
if missing:
    raise SystemExit("Thiếu artifact Day 20:\n- " + "\n- ".join(missing))

for path in (ROOT / "qa-validation/test-data/frontend/day20").glob("*.json"):
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("contains_direct_identifier") is not False:
        raise SystemExit(f"Fixture có direct identifier flag không an toàn: {path}")
    if data.get("raw_samples_included") is not False:
        raise SystemExit(f"Fixture có raw samples: {path}")
    if data.get("automatic_retraining") is not False:
        raise SystemExit(f"Fixture bật auto retraining: {path}")

source_text = "\n".join(
    path.read_text(encoding="utf-8")
    for base in [ROOT / "apps/web-portal/src", ROOT / "services/api-server/src/mock_api"]
    for path in base.rglob("*")
    if path.is_file() and path.suffix in {".ts", ".tsx", ".py"}
).lower()

for token in ["patient_name", "medical_record_number", "raw_signal_samples"]:
    if token in source_text:
        raise SystemExit(f"Phát hiện key không an toàn: {token}")

for forbidden in [
    "xác suất bệnh nhân bị mỏi",
    "kết nối noraxon trực tiếp",
    "bắt đầu điều khiển chi giả",
    "enableautomaticretraining: true",
]:
    if forbidden in source_text:
        raise SystemExit(f"Phát hiện wording/config bị cấm: {forbidden}")

print("DAY 20 ARTIFACT CHECK PASSED")
