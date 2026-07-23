from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_required_frontend_files_exist() -> None:
    required = [
        "apps/web-portal/src/schemas/session-intake.schema.ts",
        "apps/web-portal/src/schemas/import-workflow.schema.ts",
        "apps/web-portal/src/schemas/channel-mapping.schema.ts",
        "apps/web-portal/src/schemas/preflight.schema.ts",
        "apps/web-portal/src/schemas/calibration.schema.ts",
        "apps/web-portal/src/schemas/quality-gate.schema.ts",
        "apps/web-portal/src/schemas/analysis-handoff.schema.ts",
        "apps/web-portal/src/lib/session-intake-client.ts",
        "apps/web-portal/src/app/sessions/Day20SessionRoutes.tsx",
    ]
    assert all((ROOT / path).is_file() for path in required)


def test_no_forbidden_frontend_wording() -> None:
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "apps/web-portal/src").rglob("*.tsx")
    ).lower()
    forbidden = [
        "xác suất bệnh nhân bị mỏi",
        "kết nối noraxon trực tiếp",
        "bắt đầu điều khiển chi giả",
        "dịch ngôn ngữ ký hiệu",
    ]
    assert not any(token in source for token in forbidden)


def test_safety_literals_present() -> None:
    schema = (ROOT / "apps/web-portal/src/schemas/analysis-handoff.schema.ts").read_text(encoding="utf-8")
    assert "scoreIsProbability: false" in schema
    assert "clinicalUseAllowed: false" in schema
    assert "rawSamplesIncluded: false" in schema
