from __future__ import annotations
import importlib.util, json, sys
from pathlib import Path
from decimal import Decimal
import jsonschema, numpy as np, pytest, yaml
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'packages' / 'semg-core'))
from semg_core.qc_windowing import CanonicalChannelTimeline, WindowingProfile, build_window_identities

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod
SCHEMA = json.loads((ROOT / 'packages/common-schemas/json/labeling-function-output.schema.json').read_text())

def window(sample_count=1000, fs=2000):
    t = CanonicalChannelTimeline(session_id='ses_qc', channel_id='ch_qc', source_id='src_qc', sample_count=sample_count, sampling_rate_hz=Decimal(str(fs)), protocol_context_ref='protocol://synthetic')
    p = WindowingProfile(profile_id='qc-test', version='0.1', requested_duration_seconds=Decimal('0.25'), requested_step_seconds=Decimal('0.25'), rounding_policy='HALF_UP', boundary_policy='KEEP_PARTIAL', context_before_seconds=Decimal('0.05'), context_after_seconds=Decimal('0.05'), context_boundary_policy='CLIP_TO_SIGNAL')
    return build_window_identities(t, p)[0]

def validate(o, w):
    jsonschema.validate(o, SCHEMA)
    assert o['evidence_refs'][0] == w.window_id
    assert o['ground_truth_claim'] is False
    assert o['expert_label_claim'] is False
D = load(ROOT / 'services/quality-gate-service/src/detectors/motion_artifact.py', 'day27_motion')
F = load(ROOT / 'qa-validation/test-data/synthetic/generators/motion_artifact_factory.py', 'day27_factory')

def test_01_factory_deterministic():
    a = F.build_fixture('BASELINE_DRIFT', seed=7)
    b = F.build_fixture('BASELINE_DRIFT', seed=7)
    assert np.array_equal(a.samples, b.samples)
    assert a.fixture_id == b.fixture_id

@pytest.mark.parametrize('sc', ['CLEAN', 'BASELINE_DRIFT', 'MOVEMENT_TRANSIENT', 'AMBIGUOUS_SLOW_ACTIVITY'])
def test_02_05_synthetic_truth_only(sc):
    x = F.build_fixture(sc)
    assert x.truth_is_synthetic_known_truth and (not x.clinical_evidence)

def test_06_drift_warns():
    x = F.build_fixture('BASELINE_DRIFT')
    w = window()
    o = D.evaluate_motion_artifact(x.samples, w)
    validate(o, w)
    assert o['label_candidate'] == 'WARNING_CANDIDATE'

def test_07_ambiguous_never_fail():
    x = F.build_fixture('AMBIGUOUS_SLOW_ACTIVITY')
    w = window()
    o = D.evaluate_motion_artifact(x.samples, w)
    validate(o, w)
    assert o['label_candidate'] in {'WARNING_CANDIDATE', 'PASS_CANDIDATE'}
    assert o['label_candidate'] != 'FAIL_CANDIDATE'

def test_08_clean_pass():
    x = F.build_fixture('CLEAN')
    o = D.evaluate_motion_artifact(x.samples, window())
    assert o['label_candidate'] == 'PASS_CANDIDATE'

def test_09_raw_immutable():
    x = F.build_fixture('BASELINE_DRIFT')
    b = x.samples.copy()
    D.evaluate_motion_artifact(x.samples, window())
    assert np.array_equal(x.samples, b)

def test_10_no_cleaning_filtering():
    text = (ROOT / 'services/quality-gate-service/src/detectors/motion_artifact.py').read_text().lower()
    forbidden = ['highpass', 'filtfilt', 'butter(', 'sosfilt', 'np.interp', 'resample(']
    assert not any((t in text for t in forbidden))

def test_11_window_link():
    x = F.build_fixture('CLEAN')
    w = window()
    assert D.evaluate_motion_artifact(x.samples, w)['evidence_refs'][0] == w.window_id

def test_12_short_abstain():
    w = window(sample_count=20)
    o = D.evaluate_motion_artifact(np.zeros(20), w)
    assert o['label_candidate'] == 'ABSTAIN'

def test_13_non1d_failure():
    with pytest.raises(D.MotionArtifactDetectorError):
        D.evaluate_motion_artifact(np.zeros((2, 2)), window())

def test_14_no_session_final():
    text = (ROOT / 'services/quality-gate-service/src/detectors/motion_artifact.py').read_text()
    assert 'final_signal_quality' not in text

@pytest.mark.parametrize('seed', range(12))
def test_15_26_deterministic(seed):
    x = F.build_fixture('CLEAN', seed=seed)
    w = window()
    assert D.evaluate_motion_artifact(x.samples, w) == D.evaluate_motion_artifact(x.samples, w)

def test_27_registry_delta():
    m = yaml.safe_load((ROOT / 'clinical/labels/day27-qc-labeling-function-registry-delta.v0.1.yaml').read_text())
    assert m['updates'][0]['lf_id'] == 'LF_MOTION_ARTIFACT'

def test_28_reason_delta():
    m = yaml.safe_load((ROOT / 'services/quality-gate-service/configs/day27-reason-code-delta.v0.1.yaml').read_text())
    assert 'MOTION_ARTIFACT_SUSPECTED' in {x['code'] for x in m['reason_codes']}

def test_29_traceability():
    m = yaml.safe_load((ROOT / 'qa-validation/traceability/day27-requirement-impact.yaml').read_text())
    assert set(m['requirements']) == {'FR-035', 'FR-036', 'FR-037'}

@pytest.mark.parametrize('sc', ['CLEAN', 'BASELINE_DRIFT', 'MOVEMENT_TRANSIENT', 'AMBIGUOUS_SLOW_ACTIVITY'])
def test_30_33_schema(sc):
    x = F.build_fixture(sc)
    w = window()
    o = D.evaluate_motion_artifact(x.samples, w)
    validate(o, w)

def test_34_artifact_not_pathology_text():
    text = (ROOT / 'docs/00-executive/day27/DAY27_INTEGRATION_NOTES.md').read_text()
    assert 'artifact evidence != pathology' in text.lower()

def test_35_no_fail_candidate_from_detector():
    for sc in ['BASELINE_DRIFT', 'MOVEMENT_TRANSIENT', 'AMBIGUOUS_SLOW_ACTIVITY']:
        assert D.evaluate_motion_artifact(F.build_fixture(sc).samples, window())['label_candidate'] != 'FAIL_CANDIDATE'

def test_36_no_raw_mask_delete():
    text = (ROOT / 'services/quality-gate-service/src/detectors/motion_artifact.py').read_text()
    assert 'raw_deleted=True' not in text

def test_37_config_versioned():
    m = yaml.safe_load((ROOT / 'configs/qc/motion-artifact.v0.1.yaml').read_text())
    assert m['config_version'] == '0.1.0'

def test_38_no_training():
    text = (ROOT / 'services/quality-gate-service/src/detectors/motion_artifact.py').read_text().lower()
    assert '.fit(' not in text and 'torch' not in text
