from pathlib import Path
import sys
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
for p in [
    ROOT / 'services/api-server/src',
    ROOT / 'services/api-server/src/mock_api',
    ROOT / 'packages/semg-core',
    ROOT / 'services/inference-service/src',
]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day23_app import app
from services.longitudinal_service import build_assessment

client = TestClient(app)


def test_golden_assessment():
    result = build_assessment('golden_uc2_longitudinal')
    assert result.status == 'completed_with_warnings'
    assert result.compatibility.conclusionAllowed
    assert any(
        metric.metricId == 'symmetry_ratio' and metric.value == 80
        for metric in result.metrics
    )


def test_protocol_mismatch_blocks():
    result = build_assessment('uc2_protocol_incompatible')
    assert result.status == 'blocked'
    assert not result.compatibility.conclusionAllowed
    assert 'PROTOCOLVERSION_MISMATCH' in result.compatibility.reasonCodes


def test_missing_and_bilateral_semantics():
    missing = build_assessment('uc2_missing_baseline')
    assert missing.metrics[0].status == 'not_available'
    assert missing.metrics[0].value is None

    bilateral = build_assessment('uc2_bilateral_unavailable')
    metric = next(
        (item for item in bilateral.metrics if item.metricId == 'symmetry_ratio'),
        None,
    )
    assert metric is not None
    assert metric.status == 'not_available'
    assert metric.value is None


def test_api_roundtrip():
    response = client.post('/v1/uc2/assessments', json={'scenarioId': 'golden_uc2_longitudinal'})
    assert response.status_code == 201
    payload = response.json()
    follow = client.get(f"/v1/uc2/assessments/{payload['assessmentId']}")
    assert follow.status_code == 200
    assert payload['safety']['scoreIsProbability'] is False
