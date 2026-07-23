from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED = [
    "docs/plans/DAY19_EXECUTION_PLAN.md",
    "apps/web-portal/src/app/AppRouter.tsx",
    "apps/web-portal/src/components/layout/AppShell.tsx",
    "apps/web-portal/src/config/useCaseRoutes.ts",
    "apps/web-portal/src/config/routePermissions.ts",
    "apps/web-portal/src/lib/mock-api-client.ts",
    "services/api-server/src/mock_api/day19_app.py",
    "docs/04-api/openapi-day19-ui-mock.fragment.yaml",
    "qa-validation/requirements/day19-acceptance-criteria.md",
]

missing = [relative for relative in REQUIRED if not (ROOT / relative).is_file()]
if missing:
    raise SystemExit("Thiếu artifact Day 19:\n- " + "\n- ".join(missing))

source_text = "\n".join(
    path.read_text(encoding="utf-8")
    for base in [ROOT / "apps/web-portal/src", ROOT / "services/api-server/src/mock_api"]
    for path in base.rglob("*")
    if path.is_file() and path.suffix in {".ts", ".tsx", ".py"}
)

for token in ["patient_name", "medical_record_number", "raw_signal_samples"]:
    if token in source_text.lower():
        raise SystemExit(f"Phát hiện key không an toàn: {token}")

if 'enableAutomaticRetraining: true' in source_text:
    raise SystemExit("Automatic retraining không được bật")
if 'enableLiveDeviceStream: true' in source_text:
    raise SystemExit("Live device stream không được bật")

print("DAY 19 ARTIFACT CHECK PASSED")
