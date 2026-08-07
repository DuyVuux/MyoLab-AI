from __future__ import annotations

import csv
import json
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / 'qa-validation/evidence/day02-artifact-manifest.json'

def load_yaml(rel: str) -> dict:
    return yaml.safe_load((ROOT / rel).read_text(encoding='utf-8'))

def read_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding='utf-8')

OBS = 'clinical/studies/time-motion-observation-form.v0.1.yaml'
PROT = 'clinical/studies/time-motion-study-protocol.v0.1.md'
WF = 'clinical/workflows/motionlab-current-state.v0.1.md'
TRACE = 'docs/03-architecture/traceability/day02-workflow-time-motion-traceability.v0.1.csv'
OQ = 'docs/01-product/motionlab-rebaseline/day02-open-question-status-update.v0.1.yaml'
SYN = 'qa-validation/test-data/day02/synthetic-time-motion-observation.v0.1.yaml'
SCHEMA = 'packages/common-schemas/json/time-motion-observation.schema.json'
REPORT = 'qa-validation/evidence/day02-validation-report.json'

EVIDENCE = {
    'VERIFIED_DOCUMENTED', 'OBSERVED_SAMPLE_DATA', 'SITE_VERIFIED', 'INFERRED',
    'ASSUMPTION', 'UNKNOWN', 'TBD', 'NOT_VERIFIED', 'DISCOVERY_REQUIRED', 'CONFLICTING'
}


def trace_ids() -> set[str]:
    with (ROOT / TRACE).open(encoding='utf-8', newline='') as f:
        return {r['requirement_id'] for r in csv.DictReader(f)}


def get_managed_paths(root: Path) -> list[Path]:
    if not MANIFEST.is_file():
        return []
    manifest_data = json.loads(MANIFEST.read_text(encoding='utf-8'))
    return [root / item["path"] for item in manifest_data.get("files", [])]


def test_01_mandatory_artifacts_exist() -> None:
    for rel in [WF, PROT, OBS]:
        assert (ROOT / rel).is_file()


def test_02_observation_yaml_and_schema_validate() -> None:
    obs = load_yaml(OBS)
    schema = json.loads(read_text(SCHEMA))
    validator = jsonschema.Draft202012Validator(schema)
    validator.validate(obs)


def test_03_template_prohibits_phi_and_raw_signal() -> None:
    d = load_yaml(OBS)['data_policy']
    keys = ['direct_phi_allowed', 'raw_signal_allowed', 'screenshots_allowed', 'patient_name_allowed', 'mrn_allowed']
    assert all(d[k] is False for k in keys)


def test_04_event_contract_supports_required_fields() -> None:
    schema = json.loads(read_text(SCHEMA))
    req = set(schema['properties']['events']['items']['required'])
    expected = {'event_id', 'start_timestamp', 'end_timestamp', 'actor_role', 'activity_code', 'time_class', 'workflow_step_id', 'evidence_status'}
    assert expected <= req


def test_05_doctor_and_ktv_hands_on_are_separate() -> None:
    tc = set(load_yaml(OBS)['coding_dictionary']['time_classes'])
    assert {'CLINICIAN_DATA_HANDS_ON', 'TECHNICIAN_DATA_HANDS_ON'} <= tc


def test_06_system_and_waiting_are_separate_from_human() -> None:
    tc = set(load_yaml(OBS)['coding_dictionary']['time_classes'])
    assert {'SYSTEM_ACTIVE', 'WAITING_BLOCKED', 'CLINICIAN_DATA_HANDS_ON', 'TECHNICIAN_DATA_HANDS_ON'} <= tc


def test_07_remeasurement_is_explicit() -> None:
    prot = read_text(PROT)
    syn = load_yaml(SYN)
    
    assert 'remeasurement_episode_id' in prot
    assert any(e.get('remeasurement') for e in syn['events'])
    assert any(e.get('remeasurement_episode_id') for e in syn['events'] if e.get('remeasurement'))


def test_08_concurrency_and_interval_union_are_documented() -> None:
    prot = read_text(PROT)
    syn = load_yaml(SYN)
    
    assert 'union' in prot.lower()
    assert any(e.get('parallel_group_id') for e in syn['events'])


def test_09_sixty_minute_estimate_not_promoted_to_baseline() -> None:
    wf = read_text(WF)
    prot = read_text(PROT)
    obs = load_yaml(OBS)
    
    assert 'TEAM_ESTIMATE_NOT_BASELINE' in wf
    assert '**Baseline status:** `NOT_MEASURED`' in prot
    assert obs['baseline_eligible'] is False
    assert all(v is None for k, v in obs['case_summary'].items() if k.endswith('_sec'))


def test_10_fifty_percent_not_promoted_to_commitment() -> None:
    prot = read_text(PROT).lower()
    assert 'not a committed site-validated threshold' in prot


def test_11_evidence_statuses_are_frozen_values() -> None:
    assert set(load_yaml(OBS)['evidence_policy']['allowed_statuses']) == EVIDENCE


def test_12_workflow_is_candidate_not_site_verified() -> None:
    wf = read_text(WF)
    assert 'CANDIDATE_CURRENT_STATE_TO_VERIFY' in wf
    assert 'NOT SITE-VERIFIED' in wf
    assert wf.count('DISCOVERY_REQUIRED') >= 12


def test_13_traceability_covers_all_jtbds() -> None:
    ids = trace_ids()
    assert {f'JTBD-0{i}' for i in range(1, 6)} <= ids


def test_14_traceability_covers_all_prd_kpis() -> None:
    ids = trace_ids()
    assert {f'PRD-KPI-0{i}' for i in range(1, 8)} <= ids


def test_15_traceability_covers_ac10() -> None:
    assert 'AC-10' in trace_ids()


def test_16_key_open_questions_remain_open() -> None:
    oq_data = load_yaml(OQ)
    by = {x['question_id']: x for x in oq_data['updates']}
    
    for q in ['OQ-001', 'OQ-002', 'OQ-003', 'OQ-005']:
        assert by[q]['day02_status'] == 'OPEN'
        assert by[q]['may_close_on_day02'] is False
        assert by[q]['day02_evidence_status'] == 'UNKNOWN'


def test_17_synthetic_fixture_never_baseline_eligible() -> None:
    s = load_yaml(SYN)
    assert s['baseline_eligible'] is False
    assert s['observation']['observation_mode'] == 'SYNTHETIC_QA'
    assert s['template_is_clinical_evidence'] is False


def test_18_no_training_or_model_artifacts_introduced() -> None:
    managed_paths = get_managed_paths(ROOT)
    bad_suffixes = {'.joblib', '.pkl', '.pickle', '.pt', '.pth', '.onnx', '.npz', '.npy', '.h5', '.hdf5'}
    
    introduced_model_artifacts = [
        p for p in managed_paths
        if p.is_file() and p.suffix.lower() in bad_suffixes
    ]
    assert not introduced_model_artifacts


def test_19_no_raw_patient_or_phi_artifacts_introduced() -> None:
    managed_paths = get_managed_paths(ROOT)
    bad_suffixes = {'.mat', '.c3d'}
    bad = []
    
    for p in managed_paths:
        if not p.is_file():
            continue
        s = p.relative_to(ROOT).as_posix().lower()
        if p.suffix.lower() in bad_suffixes or '/raw/' in s or 'patient_raw' in s or 'mrn_' in s:
            bad.append(s)
            
    assert not bad


def test_20_validation_report_status_contract() -> None:
    r = json.loads(read_text(REPORT))
    
    assert r['day'] == 'DAY02'
    assert r['status'] in {'PENDING_VALIDATION', 'GO_FOR_DAY_03', 'BLOCKED_WITH_EVIDENCE'}
    assert r['tests_expected'] == 20
    assert r['baseline_measured'] is False
    assert r['training_executed'] is False
    assert r['raw_patient_data_read'] is False
