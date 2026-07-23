from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
for path in (
    ROOT / "services/api-server/src",
    ROOT / "services/api-server/src/mock_api",
):
    sys.path.insert(0, str(path))

from day20_store import reset_store as reset_day20
from day21_app import app, repository

client = TestClient(app)


def prepare_session(*, quality_scenario: str = "golden_intake_pass") -> str:
    reset_day20(); repository.reset()
    payload = {
        "subjectRef":"SUBJ-D21", "useCaseId":"uc1",
        "protocol":{"protocolId":"upper-limb-gesture","protocolVersion":"v0.1"},
        "affectedSide":"right", "referenceSide":"left",
        "targetMuscles":["Flexor carpi radialis","Extensor carpi radialis"],
        "sessionType":"baseline", "operatorRef":"KTV-HASH",
        "consent":{"qualityImprovement":True,"modelTraining":False,"researchExport":False},
        "dataSourceIntent":"generic_csv_manifest",
    }
    sid = client.post('/v1/sessions', json=payload, headers={'Idempotency-Key':'d21-session'}).json()['sessionId']
    imp = client.post(f'/v1/sessions/{sid}/imports', json={'scenario_id':'golden_intake_pass'}).json()
    mappings = [
      {"sourceChannel":f"Sensor {i}","canonicalChannelId":f"CH{i:02d}","muscle":"M","side":"right","unit":"uV","functionalRole":"flexor" if i==1 else "other"}
      for i in range(1,5)
    ]
    assert client.put(f"/v1/imports/{imp['importId']}/mapping",json={'mappings':mappings}).status_code == 200
    assert client.post(f'/v1/sessions/{sid}/calibrations',json={'scenario_id':'golden_intake_pass'}).status_code == 201
    assert client.get(f'/v1/sessions/{sid}/quality',params={'scenario_id':quality_scenario}).status_code == 200
    if quality_scenario == 'qc_warning_powerline':
        assert client.post(f'/v1/sessions/{sid}/quality/acknowledgements',json={'reviewer_ref':'KTV-HASH','reason':'Đã kiểm tra setup'}).status_code == 200
    assert client.post(f'/v1/sessions/{sid}/analyses').status_code == 202
    return sid


def advance_to_terminal(analysis_id: str) -> dict:
    job = client.get(f'/v1/analyses/{analysis_id}').json()
    while job['status'] in {'queued','running'}:
        response = client.post(f'/v1/analyses/{analysis_id}/advance', json={'expectedCurrentStage': job['currentStage']})
        assert response.status_code == 200, response.text
        job = response.json()
    return job


def test_golden_job_and_idempotency() -> None:
    sid = prepare_session()
    body = {'scenarioId':'golden_completed'}
    first = client.post(f'/v1/sessions/{sid}/analysis-jobs',json=body,headers={'Idempotency-Key':'same'}).json()
    second = client.post(f'/v1/sessions/{sid}/analysis-jobs',json=body,headers={'Idempotency-Key':'same'}).json()
    assert first['analysisId'] == second['analysisId']
    terminal = advance_to_terminal(first['analysisId'])
    assert terminal['status'] == 'completed'
    assert len(terminal['completedStages']) == 11
    assert client.get(terminal['resultLinks']['summary']).status_code == 200
    assert terminal['safety']['scoreIsProbability'] is False


def test_warning_propagates() -> None:
    sid = prepare_session(quality_scenario='qc_warning_powerline')
    job = client.post(f'/v1/sessions/{sid}/analysis-jobs',json={'scenarioId':'warning_completed'},headers={'Idempotency-Key':'warning'}).json()
    terminal = advance_to_terminal(job['analysisId'])
    assert terminal['status'] == 'completed_with_warnings'
    assert 'POWERLINE_NOISE_HIGH' in terminal['warningCodes']


def test_qc_fail_abstains_without_runtime() -> None:
    sid = prepare_session(quality_scenario='qc_fail_flatline')
    job = client.post(f'/v1/sessions/{sid}/analysis-jobs',json={'scenarioId':'qc_abstained'},headers={'Idempotency-Key':'abstain'}).json()
    assert job['status'] == 'abstained'
    assert job['resultLinks']['summary'] is None
    assert job['error'] is None


def test_runtime_failure_is_not_abstention() -> None:
    sid = prepare_session()
    job = client.post(f'/v1/sessions/{sid}/analysis-jobs',json={'scenarioId':'runtime_failed'},headers={'Idempotency-Key':'failure'}).json()
    terminal = advance_to_terminal(job['analysisId'])
    assert terminal['status'] == 'failed'
    assert terminal['error']['retryable'] is True
    assert terminal['error']['traceId'].startswith('TRACE-')
