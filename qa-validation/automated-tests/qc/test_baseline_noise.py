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

if str(ROOT / 'packages/semg-core') not in sys.path:
    sys.path.insert(0, str(ROOT / 'packages/semg-core'))
if str(ROOT / 'services/quality-gate-service/src') not in sys.path:
    sys.path.insert(0, str(ROOT / 'services/quality-gate-service/src'))
if str(ROOT / 'qa-validation/test-data/synthetic/generators') not in sys.path:
    sys.path.insert(0, str(ROOT / 'qa-validation/test-data/synthetic/generators'))

from semg_core.qc_windowing import (
    CanonicalChannelTimeline,
    WindowingProfile,
    build_window_identities,
)
import detectors.baseline_noise as D
import baseline_noise_fixture_factory as F

SCHEMA = json.loads(
    (ROOT / 'packages/common-schemas/json/labeling-function-output.schema.json').read_text()
)


def win(n=400):
    t = CanonicalChannelTimeline(
        's25',
        'c25',
        'src25',
        n,
        Decimal('2000'),
        protocol_context_ref='protocol://synthetic/day25/rest',
    )
    p = WindowingProfile(
        'p25',
        '0.1',
        Decimal('0.05'),
        Decimal('0.05'),
        'HALF_UP',
        'KEEP_PARTIAL',
        Decimal('0.01'),
        Decimal('0.01'),
        'CLIP_TO_SIGNAL',
    )
    return build_window_identities(t, p)[1]


def profile(
    status='SYNTHETIC_ENGINEERING_ONLY',
    rms=0.0002,
    mad=0.0001,
    ref='protocol://synthetic/day25/rest',
):
    return D.ProtocolNoiseProfile(
        protocol_ref=ref,
        config_version='cfg25',
        threshold_status=status,
        rms_warning_threshold=rms,
        mad_warning_threshold=mad,
    )


def ref(status='VERIFIED_ELIGIBLE', role='REST', p='protocol://synthetic/day25/rest'):
    return D.ReferenceRegionEvidence(
        p, role, status, 'marker://rest1' if status == 'VERIFIED_ELIGIBLE' else None
    )


def validate(o, w, p):
    jsonschema.validate(o, SCHEMA)
    assert o['evidence_refs'][0] == w.window_id
    assert o['evidence_refs'][1] == p.protocol_ref
    assert o['ground_truth_claim'] is False
    assert o['expert_label_claim'] is False


def test_01_low_noise_pass():
    x = F.build_fixture(2e-05)
    w = win()
    p = profile()
    d, o = D.evaluate_baseline_noise(x.samples, w, ref(), p)
    validate(o, w, p)
    assert d and o['label_candidate'] == 'PASS_CANDIDATE'


def test_02_high_noise_warning():
    x = F.build_fixture(0.001)
    w = win()
    p = profile()
    d, o = D.evaluate_baseline_noise(x.samples, w, ref(), p)
    validate(o, w, p)
    assert d and o['label_candidate'] == 'WARNING_CANDIDATE'


def test_03_missing_reference_abstains():
    x = F.build_fixture(1e-05)
    w = win()
    p = profile()
    d, o = D.evaluate_baseline_noise(x.samples, w, ref('NOT_VERIFIED'), p)
    assert (
        d is None
        and o['reason_code'] == 'INSUFFICIENT_REFERENCE'
        and o['label_candidate'] == 'ABSTAIN'
    )


def test_04_low_amplitude_not_inferred_as_rest():
    x = F.build_fixture(1e-07)
    w = win()
    p = profile()
    d, o = D.evaluate_baseline_noise(x.samples, w, ref('NOT_VERIFIED', role='UNKNOWN'), p)
    assert d is None and o['label_candidate'] == 'ABSTAIN'


def test_05_unverified_threshold_returns_unknown():
    x = F.build_fixture(1e-05)
    w = win()
    p = profile('NOT_VERIFIED', None, None)
    d, o = D.evaluate_baseline_noise(x.samples, w, ref(), p)
    assert (
        d
        and o['label_candidate'] == 'UNKNOWN'
        and o['reason_code'] == 'BASELINE_NOISE_THRESHOLD_NOT_VERIFIED'
    )


def test_06_protocol_mismatch_fails_closed():
    with pytest.raises(D.BaselineNoiseError):
        D.evaluate_baseline_noise(
            F.build_fixture(0.1).samples, win(), ref(), profile(ref='protocol://other')
        )


def test_07_verified_reference_requires_marker():
    with pytest.raises(D.BaselineNoiseError):
        D.ReferenceRegionEvidence('p', 'REST', 'VERIFIED_ELIGIBLE', None)


def test_08_not_verified_profile_cannot_hide_threshold():
    with pytest.raises(D.BaselineNoiseError):
        profile('NOT_VERIFIED', 0.1, 0.1)


def test_09_approved_requires_thresholds():
    with pytest.raises(D.BaselineNoiseError):
        profile('APPROVED', None, None)


def test_10_raw_immutable():
    x = F.build_fixture(0.0001)
    b = x.samples.copy()
    D.evaluate_baseline_noise(x.samples, win(), ref(), profile())
    assert np.array_equal(x.samples, b)


def test_11_descriptors_robust_fields():
    d = D.compute_descriptors(F.build_fixture(0.0001).samples, win())
    assert d.sample_count > 0 and d.mad >= 0 and d.rms >= 0 and d.p95 >= d.p05


def test_12_nonfinite_reference_abstains():
    x = F.build_fixture(0.0001)
    x.samples[100] = np.nan
    d, o = D.evaluate_baseline_noise(x.samples, win(), ref(), profile())
    assert d is None and o['label_candidate'] == 'ABSTAIN'


def test_13_non1d_fails():
    with pytest.raises(D.BaselineNoiseError):
        D.compute_descriptors(np.zeros((3, 3)), win())


def test_14_bounds_fails():
    with pytest.raises(D.BaselineNoiseError):
        D.compute_descriptors(np.zeros(2), win())


def test_15_config_no_global_threshold():
    m = yaml.safe_load((ROOT / 'configs/qc/baseline-noise.v0.1.yaml').read_text())
    assert m['rules']['global_threshold_forbidden'] is True


def test_16_config_forbids_infer_rest():
    m = yaml.safe_load((ROOT / 'configs/qc/baseline-noise.v0.1.yaml').read_text())
    assert m['rules']['infer_rest_from_low_amplitude_forbidden'] is True


def test_17_registry_requires_protocol():
    m = yaml.safe_load(
        (
            ROOT / 'clinical/labels/day25-qc-labeling-function-registry-delta.v0.1.yaml'
        ).read_text()
    )
    assert m['updates'][0]['protocol_reference_required'] is True


def test_18_traceability():
    m = yaml.safe_load(
        (ROOT / 'qa-validation/traceability/day25-requirement-impact.yaml').read_text()
    )
    assert set(m['requirements']) == {'FR-033', 'FR-037', 'FR-023'}


@pytest.mark.parametrize('sigma', [0, 1e-05, 2e-05, 5e-05, 0.0001, 0.0002, 0.0005, 0.001])
def test_19_26_descriptors_deterministic(sigma):
    x = F.build_fixture(sigma)
    w = win()
    assert D.compute_descriptors(x.samples, w) == D.compute_descriptors(x.samples, w)


@pytest.mark.parametrize('seed', range(8))
def test_27_34_output_schema(seed):
    x = F.build_fixture(2e-05, seed=seed)
    w = win()
    p = profile()
    _, o = D.evaluate_baseline_noise(x.samples, w, ref(), p)
    validate(o, w, p)


def test_35_same_signal_different_protocol_profiles_can_differ():
    x = F.build_fixture(0.00015)
    w = win()
    p1 = profile(rms=5e-05, mad=3e-05)
    p2 = profile(rms=0.001, mad=0.001)
    assert (
        D.evaluate_baseline_noise(x.samples, w, ref(), p1)[1]['label_candidate']
        != D.evaluate_baseline_noise(x.samples, w, ref(), p2)[1]['label_candidate']
    )


def test_36_protocol_ref_in_evidence_refs():
    x = F.build_fixture(2e-05)
    w = win()
    p = profile()
    o = D.evaluate_baseline_noise(x.samples, w, ref(), p)[1]
    assert p.protocol_ref in o['evidence_refs']


def test_37_no_final_session_qc():
    txt = (ROOT / 'services/quality-gate-service/src/detectors/baseline_noise.py').read_text()
    assert 'final_signal_quality' not in txt


def test_38_no_filter_or_resample():
    txt = (
        ROOT / 'services/quality-gate-service/src/detectors/baseline_noise.py'
    ).read_text().lower()
    assert 'resample(' not in txt and 'filtfilt' not in txt and 'np.interp' not in txt


def test_39_no_diagnosis_terms_in_decision_logic():
    txt = (
        ROOT / 'services/quality-gate-service/src/detectors/baseline_noise.py'
    ).read_text().lower()
    assert 'stroke' not in txt and 'pathology' not in txt


def test_40_site_template_thresholds_null():
    m = yaml.safe_load((ROOT / 'configs/qc/baseline-noise.v0.1.yaml').read_text())
    site = [p for p in m['profiles'] if p['threshold_status'] == 'NOT_VERIFIED'][0]
    assert site['rms_warning_threshold'] is None and site['mad_warning_threshold'] is None
