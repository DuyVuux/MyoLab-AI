from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_openapi_fragment_has_expected_paths() -> None:
    document = yaml.safe_load(read("docs/04-api/openapi-day19-ui-mock.fragment.yaml"))
    expected = {
        "/health",
        "/v1/use-cases",
        "/v1/dashboard",
        "/v1/sessions",
        "/v1/analyses",
        "/v1/feedback",
    }
    assert expected <= set(document["paths"])


def test_uc3_uc4_are_feasibility_only() -> None:
    content = read("apps/web-portal/src/config/useCaseRoutes.ts")
    assert content.count('commitment: "feasibility"') == 2
    assert "Không điều khiển actuator thật" in content
    assert "chưa dùng trong phòng mổ" in content


def test_admin_cannot_clinically_sign_off() -> None:
    content = read("apps/web-portal/src/config/routePermissions.ts")
    line = next(line for line in content.splitlines() if "clinical_signoff:" in line)
    assert '"physician"' in line
    assert '"admin"' not in line


def test_no_prohibited_clinical_probability_or_device_control_copy() -> None:
    source_files = list((ROOT / "apps/web-portal/src").rglob("*.ts")) + list(
        (ROOT / "apps/web-portal/src").rglob("*.tsx")
    )
    combined = "\n".join(path.read_text(encoding="utf-8").lower() for path in source_files)
    prohibited = [
        "xác suất bệnh nhân bị mỏi",
        "bắt đầu điều khiển chi giả",
        "bắt đầu sử dụng trong phòng mổ",
        "dịch ngôn ngữ ký hiệu ngay",
    ]
    for phrase in prohibited:
        assert phrase not in combined
