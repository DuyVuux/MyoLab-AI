from pathlib import Path
import sys
from fastapi.testclient import TestClient
ROOT=Path(__file__).resolve().parents[2]
for p in [ROOT/'services/api-server/src',ROOT/'services/api-server/src/mock_api',ROOT/'packages/semg-core',ROOT/'services/inference-service/src']:sys.path.insert(0,str(p))
from day23_app import app
from services.longitudinal_service import build_assessment
c=TestClient(app)
def test_golden_assessment():
 a=build_assessment('golden_uc2_longitudinal');assert a.status=='completed_with_warnings';assert a.compatibility.conclusionAllowed;assert any(m.metricId=='symmetry_ratio' and m.value==80 for m in a.metrics)
def test_protocol_mismatch_blocks():
 a=build_assessment('uc2_protocol_incompatible');assert a.status=='blocked';assert not a.compatibility.conclusionAllowed;assert 'PROTOCOLVERSION_MISMATCH' in a.compatibility.reasonCodes
def test_missing_and_bilateral_semantics():
 a=build_assessment('uc2_missing_baseline');assert a.metrics[0].status=='not_available' and a.metrics[0].value is None
 b=build_assessment('uc2_bilateral_unavailable');m=next(x for x in b.metrics if x.metricId=='symmetry_ratio');assert m.status=='not_available' and m.value is None
def test_api_roundtrip():
 r=c.post('/v1/uc2/assessments',json={'scenarioId':'golden_uc2_longitudinal'});assert r.status_code==201;a=r.json();assert c.get(f"/v1/uc2/assessments/{a['assessmentId']}").status_code==200;assert a['safety']['scoreIsProbability'] is False
