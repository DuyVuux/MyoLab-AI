from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
MOCK_DIR = ROOT / "services" / "api-server" / "src" / "mock_api"
sys.path.insert(0, str(MOCK_DIR))

from day19_app import app  # noqa: E402

client = TestClient(app)


def test_health_is_non_clinical_mock() -> None:
    payload = client.get("/health").json()
    assert payload == {
        "status": "ok",
        "mode": "deterministic_mock",
        "clinical_use": "disabled",
    }


def test_use_case_tiering_is_correct() -> None:
    payload = client.get("/v1/use-cases").json()
    assert [item["id"] for item in payload] == ["uc1", "uc2", "uc3", "uc4"]
    assert [item["commitment"] for item in payload] == ["mvp", "mvp", "feasibility", "feasibility"]
    assert all(item["clinical_use_allowed"] is False for item in payload)


def test_analysis_states_are_distinct_and_safe() -> None:
    payload = client.get("/v1/analyses").json()
    statuses = {item["status"] for item in payload}
    assert {"completed", "completed_with_warnings", "abstained", "failed"} <= statuses
    assert all(item["raw_samples_included"] is False for item in payload)


def test_dashboard_is_deterministic() -> None:
    first = client.get("/v1/dashboard").json()
    second = client.get("/v1/dashboard").json()
    assert first == second
