from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "services/api-server/src/mock_api"))

from day20_app import app  # noqa: E402
from day20_store import reset_store  # noqa: E402


@pytest.fixture(autouse=True)
def reset() -> None:
    reset_store()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def session_payload(use_case: str = "uc1", session_type: str = "baseline") -> dict:
    return {
        "subjectRef": "SUBJ-D20-001",
        "useCaseId": use_case,
        "protocol": {"protocolId": "upper-limb-gesture", "protocolVersion": "v0.1"},
        "affectedSide": "right",
        "referenceSide": "left",
        "targetMuscles": ["Flexor carpi radialis", "Extensor carpi radialis"],
        "sessionType": session_type,
        "operatorRef": "KTV-HASH-001",
        "consent": {"qualityImprovement": True, "modelTraining": False, "researchExport": False},
        "dataSourceIntent": "generic_csv_manifest",
    }


def create_session(client: TestClient) -> str:
    response = client.post("/v1/sessions", json=session_payload(), headers={"Idempotency-Key": "d20-session-001"})
    assert response.status_code == 201
    return response.json()["sessionId"]


def mappings() -> list[dict]:
    return [
        {"sourceChannel": "Sensor 1", "canonicalChannelId": "CH01", "muscle": "Flexor carpi radialis", "side": "right", "unit": "uV", "functionalRole": "flexor"},
        {"sourceChannel": "Sensor 2", "canonicalChannelId": "CH02", "muscle": "Extensor carpi radialis", "side": "right", "unit": "uV", "functionalRole": "extensor"},
        {"sourceChannel": "Sensor 3", "canonicalChannelId": "CH03", "muscle": "Biceps brachii", "side": "right", "unit": "uV", "functionalRole": "compensation"},
        {"sourceChannel": "Sensor 4", "canonicalChannelId": "CH04", "muscle": "Upper trapezius", "side": "right", "unit": "uV", "functionalRole": "compensation"},
    ]


def prepare_ready_session(client: TestClient) -> str:
    session_id = create_session(client)
    imported = client.post(f"/v1/sessions/{session_id}/imports", json={"scenario_id": "golden_intake_pass"})
    assert imported.status_code == 201
    import_id = imported.json()["importId"]
    mapped = client.put(f"/v1/imports/{import_id}/mapping", json={"mappings": mappings()})
    assert mapped.status_code == 200
    assert mapped.json()["state"] == "qc_ready"
    preflight = client.get(f"/v1/sessions/{session_id}/preflight")
    assert preflight.json()["state"] == "ready"
    return session_id


def test_idempotent_session_creation(client: TestClient) -> None:
    first = client.post("/v1/sessions", json=session_payload(), headers={"Idempotency-Key": "same-key"})
    second = client.post("/v1/sessions", json=session_payload(), headers={"Idempotency-Key": "same-key"})
    assert first.json()["sessionId"] == second.json()["sessionId"]


def test_missing_unit_requires_mapping(client: TestClient) -> None:
    session_id = create_session(client)
    imported = client.post(f"/v1/sessions/{session_id}/imports", json={"scenario_id": "import_missing_unit"})
    assert imported.json()["state"] == "mapping_required"
    assert imported.json()["detectedMetadata"]["signalUnit"] is None


def test_corrupt_import_blocks_preflight(client: TestClient) -> None:
    session_id = create_session(client)
    imported = client.post(f"/v1/sessions/{session_id}/imports", json={"scenario_id": "import_rejected_corrupt_file"})
    assert imported.json()["state"] == "import_rejected"
    assert client.get(f"/v1/sessions/{session_id}/preflight").json()["state"] == "import_blocked"


def test_duplicate_channel_mapping_is_rejected(client: TestClient) -> None:
    session_id = create_session(client)
    imported = client.post(f"/v1/sessions/{session_id}/imports", json={"scenario_id": "golden_intake_pass"})
    import_id = imported.json()["importId"]
    duplicate = mappings()
    duplicate[1]["canonicalChannelId"] = "CH01"
    response = client.put(f"/v1/imports/{import_id}/mapping", json={"mappings": duplicate})
    assert response.status_code == 422
    assert "DUPLICATE_CANONICAL_CHANNEL" in response.text


def test_positive_flow_creates_queued_analysis(client: TestClient) -> None:
    session_id = prepare_ready_session(client)
    calibration = client.post(f"/v1/sessions/{session_id}/calibrations", json={"scenario_id": "golden_intake_pass"})
    assert calibration.json()["state"] == "pass"
    quality = client.get(f"/v1/sessions/{session_id}/quality", params={"scenario_id": "golden_intake_pass"})
    assert quality.json()["status"] == "pass"
    handoff = client.post(f"/v1/sessions/{session_id}/analyses")
    assert handoff.status_code == 202
    assert handoff.json()["status"] == "queued"
    assert handoff.json()["scoreIsProbability"] is False
    assert handoff.json()["rawSamplesIncluded"] is False


def test_warning_requires_acknowledgement(client: TestClient) -> None:
    session_id = prepare_ready_session(client)
    client.post(f"/v1/sessions/{session_id}/calibrations", json={"scenario_id": "golden_intake_pass"})
    quality = client.get(f"/v1/sessions/{session_id}/quality", params={"scenario_id": "qc_warning_powerline"})
    assert quality.json()["status"] == "warning"
    blocked = client.post(f"/v1/sessions/{session_id}/analyses")
    assert blocked.status_code == 409
    ack = client.post(f"/v1/sessions/{session_id}/quality/acknowledgements", json={"reviewer_ref": "KTV-HASH-001", "reason": "Đã kiểm tra setup prototype."})
    assert ack.status_code == 200
    handoff = client.post(f"/v1/sessions/{session_id}/analyses")
    assert handoff.json()["status"] == "queued_with_warnings"


def test_qc_fail_returns_abstained_not_server_error(client: TestClient) -> None:
    session_id = prepare_ready_session(client)
    client.post(f"/v1/sessions/{session_id}/calibrations", json={"scenario_id": "golden_intake_pass"})
    client.get(f"/v1/sessions/{session_id}/quality", params={"scenario_id": "qc_fail_flatline"})
    handoff = client.post(f"/v1/sessions/{session_id}/analyses")
    assert handoff.status_code == 202
    assert handoff.json()["status"] == "abstained"
    assert handoff.json()["nextRoute"] is None


def test_uc3_clinical_session_type_is_rejected(client: TestClient) -> None:
    response = client.post("/v1/sessions", json=session_payload(use_case="uc3", session_type="baseline"), headers={"Idempotency-Key": "uc3-bad"})
    assert response.status_code == 422
