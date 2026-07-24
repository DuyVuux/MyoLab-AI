from datetime import datetime, timezone
from fastapi.testclient import TestClient
from mock_api.day24_app import app

client = TestClient(app)
HASH = "a" * 64
RID = "b" * 64


def test_api_review_flow_and_final_report():
    case = client.post(
        "/v1/review-cases",
        json={
            "analysisId": "AN-API",
            "originalResultHash": HASH,
            "analysisStatus": "completed",
        },
    ).json()
    event = {
        "eventId": "REVT-12345678",
        "reviewType": "technical",
        "action": "approve",
        "reviewerRole": "ktv",
        "reviewerIdHash": RID,
        "sourceResultHash": HASH,
        "checklistVersion": "technical-review-checklist.v0.1",
        "checklistResponses": {"all": True},
        "reasonCodes": [],
        "comment": None,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "immutable": True,
    }
    case = client.post(
        f"/v1/review-cases/{case['caseId']}/events", json=event
    ).json()
    event.update(
        {
            "eventId": "REVT-87654321",
            "reviewType": "clinical",
            "reviewerRole": "physician",
            "checklistVersion": "clinical-review-checklist.v0.1",
        }
    )
    case = client.post(
        f"/v1/review-cases/{case['caseId']}/events", json=event
    ).json()
    assert case["state"] == "approved"
    payload = {
        "reviewCase": case,
        "analysisSummary": {
            "summaryVi": "Mẫu thay đổi kỹ thuật được quan sát.",
            "protocolVersion": "p.v0.1",
        },
        "finalize": True,
        "templateVersion": "clinical-report-v0.2-review-workflow",
    }
    response = client.post("/v1/reports/finalize", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "final"
