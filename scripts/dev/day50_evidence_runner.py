from __future__ import annotations
import importlib.util
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]

try:
    from services.evidence_service.src import build_bundle as b
except ImportError:
    spec = importlib.util.spec_from_file_location(
        'b', ROOT / 'services/evidence-service/src/build_bundle.py'
    )
    b = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(b)

line_file = ROOT / 'qa-validation/evidence/day45-processing-lineage-evidence.json'
ev46_file = ROOT / 'qa-validation/evidence/day46-rms-mav-evidence.json'
ev47_file = ROOT / 'qa-validation/evidence/day47-spectral-known-answer.json'

if not line_file.exists():
    line_file = ROOT / 'DAY50_COMPLETE/upstream-evidence/qa-validation/evidence/day45-processing-lineage-evidence.json'
if not ev46_file.exists():
    ev46_file = ROOT / 'DAY50_COMPLETE/upstream-evidence/qa-validation/evidence/day46-rms-mav-evidence.json'
if not ev47_file.exists():
    ev47_file = ROOT / 'DAY50_COMPLETE/upstream-evidence/qa-validation/evidence/day47-spectral-known-answer.json'

line = json.loads(line_file.read_text())
man = line['manifest']
ev46 = json.loads(ev46_file.read_text())
ev47 = json.loads(ev47_file.read_text())

manifest_id = man['manifest_id']
source_id = man['source']['source_id']
art = man['final_artifact']['artifact_id']
run = man['processing_run_id']

metrics = [
    {
        'metric_id': ev46['metric_ids'][0],
        'metric_name': 'RMS',
        'status': 'AVAILABLE',
        'value': ev46['rms'],
        'units': 'uV',
        'reason_codes': [],
        'manifest_id': manifest_id,
        'evidence_class': 'ANALYTICAL_RESEARCH',
    },
    {
        'metric_id': ev46['metric_ids'][1],
        'metric_name': 'MAV',
        'status': 'AVAILABLE',
        'value': ev46['mav'],
        'units': 'uV',
        'reason_codes': [],
        'manifest_id': manifest_id,
        'evidence_class': 'ANALYTICAL_RESEARCH',
    },
    {
        'metric_id': 'metric_day47_mdf',
        'metric_name': 'MDF',
        'status': 'AVAILABLE',
        'value': ev47['mdf_hz'],
        'units': 'Hz',
        'reason_codes': [],
        'manifest_id': manifest_id,
        'evidence_class': 'ANALYTICAL_RESEARCH',
    },
    {
        'metric_id': 'metric_day47_mnf',
        'metric_name': 'MNF',
        'status': 'AVAILABLE',
        'value': ev47['mnf_hz'],
        'units': 'Hz',
        'reason_codes': [],
        'manifest_id': manifest_id,
        'evidence_class': 'ANALYTICAL_RESEARCH',
    },
    {
        'metric_id': 'metric_day48_activation',
        'metric_name': 'ACTIVATION_TIMING',
        'status': 'NOT_AVAILABLE',
        'value': None,
        'units': 's',
        'reason_codes': ['REAL_ALIGNED_EVENT_COHORT_NOT_AVAILABLE'],
        'manifest_id': manifest_id,
        'evidence_class': 'NOT_VERIFIED',
    },
    {
        'metric_id': 'metric_day49_mfcv',
        'metric_name': 'MFCV',
        'status': 'UNSUPPORTED',
        'value': None,
        'units': 'm/s',
        'reason_codes': ['SITE_GEOMETRY_NOT_VERIFIED'],
        'manifest_id': manifest_id,
        'evidence_class': 'NOT_VERIFIED',
    },
]

bundle = b.build_session_evidence_bundle(
    session_id=man['window']['session_id'],
    source_refs=[source_id],
    qc={
        'signal_quality': 'PASS',
        'supportability': 'SUPPORTABLE',
        'evaluation_status': 'EVALUATED',
        'reason_codes': ['REFERENCE_RESEARCH_QC_PASS'],
        'evidence_refs': ['DAY30_AGGREGATION', 'DAY31_ELIGIBILITY'],
    },
    processing={
        'manifest_id': manifest_id,
        'processing_run_id': run,
        'processed_artifact_id': art,
        'profile_id': man['profile']['profile_id'],
        'profile_fingerprint': man['profile']['config_fingerprint'],
        'outcome': 'COMPLETED',
    },
    metrics=metrics,
    distribution_support={
        'status': 'UNKNOWN',
        'method_status': 'INFORMATIONAL_RESEARCH_ONLY',
        'score': None,
        'reason_codes': ['NO_VALIDATED_OOD_METHOD'],
    },
    uncertainty={
        'uncertainty_type': 'RULE_CONFIDENCE',
        'calibration_status': 'NOT_APPLICABLE',
        'rule_confidence_level': 'UNKNOWN',
        'calibrated_probability': None,
        'conformal_set': None,
        'calibration_ref': None,
        'abstention': False,
        'abstention_reason': None,
    },
    unsupported_capabilities=[
        {
            'capability': 'ACTIVATION_TIMING_REAL_COHORT',
            'status': 'NOT_AVAILABLE',
            'reason_codes': ['REAL_ALIGNED_EVENT_COHORT_NOT_AVAILABLE'],
        },
        {'capability': 'MFCV_SITE', 'status': 'NOT_VERIFIED', 'reason_codes': ['SITE_GEOMETRY_NOT_VERIFIED']},
        {
            'capability': 'CALIBRATED_PROBABILITY',
            'status': 'NOT_AVAILABLE',
            'reason_codes': ['NO_PROBABILISTIC_MODEL'],
        },
        {'capability': 'OOD_SCORE', 'status': 'NOT_AVAILABLE', 'reason_codes': ['NO_VALIDATED_OOD_METHOD']},
    ],
    limitations=[
        'Research-only evidence bundle; no clinical/site validation.',
        'Activation timing synthetic mechanics are not a real session measurement.',
        'MFCV synthetic known-delay mechanics are not a site measurement.',
    ],
    event_correlation_id=line['events'][0]['correlation_id'],
    evidence_refs=[
        'DAY45_PROCESSING_LINEAGE',
        'DAY46_RMS_MAV',
        'DAY47_MDF_MNF',
        'DAY48_ACTIVATION_TIMING',
        'DAY49_MFCV',
    ],
)

out_json = ROOT / 'qa-validation/evidence/day50-session-evidence-bundle.reference.json'
out_md = ROOT / 'qa-validation/evidence/day50-session-evidence-bundle.reference.md'

out_json.write_text(json.dumps(bundle, indent=2) + '\n')
out_md.write_text(b.render_human_summary(bundle))
print("Generated Day 50 evidence bundle:", bundle['bundle_id'])
