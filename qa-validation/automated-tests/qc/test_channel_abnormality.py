from __future__ import annotations
import json
import sys
from decimal import Decimal
from pathlib import Path
import jsonschema
import numpy as np
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT / 'packages' / 'semg-core') not in sys.path:
    sys.path.insert(0, str(ROOT / 'packages' / 'semg-core'))
if str(ROOT / 'services' / 'quality-gate-service' / 'src') not in sys.path:
    sys.path.insert(0, str(ROOT / 'services' / 'quality-gate-service' / 'src'))

from semg_core.qc_windowing import CanonicalChannelTimeline, WindowingProfile, build_window_identities
import detectors.channel_abnormality as D

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

def signal(scale=1.0, n=1000):
    return scale * np.sin(2 * np.pi * 80 * np.arange(n) / 2000)

def ctx(**kw):
    return D.ChannelEvidenceContext(adjacent_channel_rms=(0.7, 0.8, 0.75), **kw)

def test_01_low_activation_alone_unknown_not_poor_contact():
    w = window()
    o = D.evaluate_channel_abnormality(signal(0.05), w, ctx())
    validate(o, w)
    assert o['reason_code'] == 'LOW_ACTIVATION_CAUSE_UNRESOLVED'
    assert o['label_candidate'] == 'UNKNOWN'

def test_02_low_plus_powerline_warns():
    w = window()
    o = D.evaluate_channel_abnormality(signal(0.05), w, ctx(powerline_suspected=True))
    validate(o, w)
    assert o['reason_code'] == 'POOR_CONTACT_SUSPECTED'
    assert o['label_candidate'] == 'WARNING_CANDIDATE'

def test_03_low_plus_dropout_warns():
    o = D.evaluate_channel_abnormality(signal(0.05), window(), ctx(dropout_suspected=True))
    assert o['label_candidate'] == 'WARNING_CANDIDATE'

def test_04_normal_channel_pass_candidate():
    o = D.evaluate_channel_abnormality(signal(1.0), window(), ctx())
    assert o['label_candidate'] == 'PASS_CANDIDATE'

def test_05_missing_peers_unknown_when_artifact_signal():
    c = D.ChannelEvidenceContext(powerline_suspected=True, adjacent_channel_rms=())
    o = D.evaluate_channel_abnormality(signal(0.05), window(), c)
    assert o['label_candidate'] == 'UNKNOWN'

def test_06_raw_immutable():
    x = signal(0.05)
    b = x.copy()
    D.evaluate_channel_abnormality(x, window(), ctx(powerline_suspected=True))
    assert np.array_equal(x, b)

def test_07_no_repair_interpolate():
    text = (ROOT / 'services/quality-gate-service/src/detectors/channel_abnormality.py').read_text().lower()
    forbidden = ['np.interp', 'interpolate(', 'resample(', 'zero out', 'repair_channel']
    assert not any((x in text for x in forbidden))

def test_08_window_link():
    w = window()
    o = D.evaluate_channel_abnormality(signal(0.05), w, ctx())
    assert o['evidence_refs'][0] == w.window_id

def test_09_short_abstain():
    w = window(sample_count=10)
    o = D.evaluate_channel_abnormality(np.zeros(10), w, ctx())
    assert o['label_candidate'] == 'ABSTAIN'

def test_10_non1d_failure():
    with pytest.raises(D.ChannelAbnormalityError):
        D.evaluate_channel_abnormality(np.zeros((2, 2)), window(), ctx())

def test_11_no_session_final():
    text = (ROOT / 'services/quality-gate-service/src/detectors/channel_abnormality.py').read_text()
    assert 'final_signal_quality' not in text

@pytest.mark.parametrize('scale', [0.01, 0.03, 0.05, 0.1, 0.5, 1.0])
def test_12_17_schema(scale):
    w = window()
    o = D.evaluate_channel_abnormality(signal(scale), w, ctx(powerline_suspected=scale < 0.1))
    validate(o, w)
    assert o['label_candidate'] != 'FAIL_CANDIDATE'

@pytest.mark.parametrize('seed', range(10))
def test_18_27_deterministic(seed):
    rng = np.random.default_rng(seed)
    x = signal(0.05) + 0.0001 * rng.normal(size=1000)
    w = window()
    c = ctx(powerline_suspected=True)
    assert D.evaluate_channel_abnormality(x, w, c) == D.evaluate_channel_abnormality(x, w, c)

def test_28_registry_delta():
    m = yaml.safe_load((ROOT / 'clinical/labels/day28-qc-labeling-function-registry-delta.v0.1.yaml').read_text())
    assert m['updates'][0]['lf_id'] == 'LF_CHANNEL_ABNORMALITY'

def test_29_reason_delta():
    m = yaml.safe_load((ROOT / 'services/quality-gate-service/configs/day28-reason-code-delta.v0.1.yaml').read_text())
    assert 'POOR_CONTACT_SUSPECTED' in {x['code'] for x in m['reason_codes']}

def test_30_traceability():
    m = yaml.safe_load((ROOT / 'qa-validation/traceability/day28-requirement-impact.yaml').read_text())
    assert set(m['requirements']) == {'FR-036', 'FR-037', 'PRD_PRESERVE_PHYSIOLOGY'}

def test_31_review_guide_preserve_physiology():
    t = (ROOT / 'clinical/quality/poor-contact-review-guide.v0.1.md').read_text().lower()
    assert 'low activation' in t and 'not' in t and ('auto-repair' in t)

def test_32_no_causal_claim():
    o = D.evaluate_channel_abnormality(signal(0.05), window(), ctx(powerline_suspected=True))
    assert o['reason_code'] == 'POOR_CONTACT_SUSPECTED'

def test_33_unverified_evidence_is_not_high():
    o = D.evaluate_channel_abnormality(signal(0.05), window(), ctx(powerline_suspected=True, evidence_status='NOT_VERIFIED'))
    assert o['evidence_strength'] != 'HIGH'

def test_34_verified_can_be_high():
    o = D.evaluate_channel_abnormality(signal(0.05), window(), ctx(powerline_suspected=True, evidence_status='VERIFIED'))
    assert o['evidence_strength'] == 'HIGH'

def test_35_no_ground_truth_claim():
    o = D.evaluate_channel_abnormality(signal(0.05), window(), ctx(powerline_suspected=True))
    assert not o['ground_truth_claim'] and (not o['expert_label_claim'])

def test_36_config_versioned():
    m = yaml.safe_load((ROOT / 'configs/qc/channel-abnormality.v0.1.yaml').read_text())
    assert m['config_version'] == '0.1.0'

def test_37_no_training():
    text = (ROOT / 'services/quality-gate-service/src/detectors/channel_abnormality.py').read_text().lower()
    assert '.fit(' not in text and 'torch' not in text

def test_38_low_activation_not_bad_electrode_regression():
    for s in [0.001, 0.01, 0.05]:
        assert D.evaluate_channel_abnormality(signal(s), window(), ctx())['reason_code'] == 'LOW_ACTIVATION_CAUSE_UNRESOLVED'
