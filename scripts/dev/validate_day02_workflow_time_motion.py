#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / 'qa-validation/evidence/day02-artifact-manifest.json'

EVIDENCE = {
    'VERIFIED_DOCUMENTED', 'OBSERVED_SAMPLE_DATA', 'SITE_VERIFIED', 'INFERRED',
    'ASSUMPTION', 'UNKNOWN', 'TBD', 'NOT_VERIFIED', 'DISCOVERY_REQUIRED', 'CONFLICTING'
}

REQUIRED_TRACE = {
    'JTBD-01', 'JTBD-02', 'JTBD-03', 'JTBD-04', 'JTBD-05',
    'PRD-KPI-01', 'PRD-KPI-02', 'PRD-KPI-03', 'PRD-KPI-04', 'PRD-KPI-05', 'PRD-KPI-06', 'PRD-KPI-07', 'AC-10'
}


def sha256_file(path: Path) -> str:
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def load_yaml(rel: str) -> dict:
    return yaml.safe_load((ROOT / rel).read_text(encoding='utf-8'))


def fail(msg: str, failures: list[str]) -> None:
    failures.append(msg)


def get_managed_paths(root: Path, manifest: dict) -> list[Path]:
    return [root / item["path"] for item in manifest.get("files", [])]


def main() -> int:
    failures: list[str] = []
    
    obs_path = ROOT / 'clinical/studies/time-motion-observation-form.v0.1.yaml'
    schema_path = ROOT / 'packages/common-schemas/json/time-motion-observation.schema.json'
    workflow_path = ROOT / 'clinical/workflows/motionlab-current-state.v0.1.md'
    protocol_path = ROOT / 'clinical/studies/time-motion-study-protocol.v0.1.md'
    trace_path = ROOT / 'docs/03-architecture/traceability/day02-workflow-time-motion-traceability.v0.1.csv'
    oq_path = ROOT / 'docs/01-product/motionlab-rebaseline/day02-open-question-status-update.v0.1.yaml'
    synth_path = ROOT / 'qa-validation/test-data/day02/synthetic-time-motion-observation.v0.1.yaml'

    for p in [obs_path, schema_path, workflow_path, protocol_path, trace_path, oq_path, synth_path]:
        if not p.is_file():
            fail(f'Missing required artifact: {p.relative_to(ROOT)}', failures)
            
    if failures:
        print(json.dumps({'status': 'FAIL', 'failures': failures}, ensure_ascii=False, indent=2))
        return 2

    obs = load_yaml('clinical/studies/time-motion-observation-form.v0.1.yaml')
    schema = json.loads(schema_path.read_text(encoding='utf-8'))
    
    try:
        jsonschema.Draft202012Validator(schema).validate(obs)
    except Exception as e:
        fail(f'Observation schema validation failed: {e}', failures)

    dp = obs['data_policy']
    for k in ['direct_phi_allowed', 'raw_signal_allowed', 'screenshots_allowed', 'patient_name_allowed', 'mrn_allowed']:
        if dp.get(k) is not False:
            fail(f'{k} must be false', failures)

    allowed = set(obs['evidence_policy']['allowed_statuses'])
    if allowed != EVIDENCE:
        fail('Evidence status enum differs from frozen DAY01 taxonomy', failures)

    tc = set(obs['coding_dictionary']['time_classes'])
    required_time_classes = [
        'CLINICIAN_DATA_HANDS_ON', 'TECHNICIAN_DATA_HANDS_ON', 'SYSTEM_ACTIVE',
        'WAITING_BLOCKED', 'REMEASUREMENT', 'CLINICAL_INTERPRETATION'
    ]
    for item in required_time_classes:
        if item not in tc:
            fail(f'Missing time class {item}', failures)

    workflow = workflow_path.read_text(encoding='utf-8')
    protocol = protocol_path.read_text(encoding='utf-8')
    
    if 'CANDIDATE_CURRENT_STATE_TO_VERIFY' not in workflow or 'NOT SITE-VERIFIED' not in workflow:
        fail('Workflow must be explicitly candidate/not site-verified', failures)
    if 'TEAM_ESTIMATE_NOT_BASELINE' not in workflow:
        fail('60-minute estimate guard is missing', failures)
    if 'NOT_MEASURED' not in protocol:
        fail('Protocol must state baseline is not measured', failures)
    if 'not a committed site-validated threshold' not in protocol:
        fail('50% research target guard is missing', failures)

    with trace_path.open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    ids = {r['requirement_id'] for r in rows}
    
    if ids != REQUIRED_TRACE:
        fail(f'Traceability IDs mismatch. missing={sorted(REQUIRED_TRACE - ids)} extra={sorted(ids - REQUIRED_TRACE)}', failures)

    oq = load_yaml('docs/01-product/motionlab-rebaseline/day02-open-question-status-update.v0.1.yaml')
    by = {x['question_id']: x for x in oq['updates']}
    for q in ['OQ-001', 'OQ-002', 'OQ-003', 'OQ-005']:
        if q not in by or by[q]['day02_status'] != 'OPEN' or by[q]['may_close_on_day02'] is not False:
            fail(f'{q} was silently closed or missing', failures)

    syn = load_yaml('qa-validation/test-data/day02/synthetic-time-motion-observation.v0.1.yaml')
    if syn.get('baseline_eligible') is not False or syn['observation']['observation_mode'] != 'SYNTHETIC_QA':
        fail('Synthetic fixture must never be baseline eligible', failures)
    if not any(e.get('parallel_group_id') for e in syn['events']):
        fail('Synthetic fixture must exercise overlapping/parallel events', failures)
    if not any(e.get('remeasurement') for e in syn['events']):
        fail('Synthetic fixture must exercise remeasurement branch', failures)

    # Manifest driven check for forbidden suffixes inside DAY02 scope
    manifest_data = json.loads(MANIFEST.read_text(encoding='utf-8'))
    managed_paths = get_managed_paths(ROOT, manifest_data)
    
    DAY02_FORBIDDEN_SUFFIXES = {
        '.npz', '.npy', '.mat', '.c3d', '.joblib', 
        '.pkl', '.pickle', '.pt', '.pth', '.onnx', '.h5', '.hdf5'
    }
    
    for p in managed_paths:
        if p.is_file() and p.suffix.lower() in DAY02_FORBIDDEN_SUFFIXES:
            fail(f'DAY02 introduced forbidden artifact: {p.relative_to(ROOT)}', failures)

    result = {
        'status': 'PASS' if not failures else 'FAIL',
        'day': 'DAY02',
        'mandatory_artifacts': 3,
        'traceability_count': len(ids),
        'key_open_questions_still_open': all(by[q]['day02_status'] == 'OPEN' for q in ['OQ-001', 'OQ-002', 'OQ-003', 'OQ-005']),
        'baseline_measured': False,
        'training_executed': False,
        'raw_patient_data_read': False,
        'failures': failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 2

if __name__ == '__main__':
    raise SystemExit(main())
