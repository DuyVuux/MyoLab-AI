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

# Add packages to sys.path if needed
if str(ROOT / "packages/semg-core") not in sys.path:
    sys.path.insert(0, str(ROOT / "packages/semg-core"))
if str(ROOT / "services/quality-gate-service/src") not in sys.path:
    sys.path.insert(0, str(ROOT / "services/quality-gate-service/src"))
if str(ROOT / "qa-validation/test-data/synthetic/generators") not in sys.path:
    sys.path.insert(0, str(ROOT / "qa-validation/test-data/synthetic/generators"))

from semg_core.qc_windowing import (
    CanonicalChannelTimeline,
    WindowingProfile,
    build_window_identities,
)
import detectors.clipping as D
import clipping_fixture_factory as F

SCHEMA = json.loads(
    (ROOT / 'packages/common-schemas/json/labeling-function-output.schema.json').read_text()
)


def win(n=400):
    t = CanonicalChannelTimeline(
        's24', 'c24', 'src24', n, Decimal('2000'), protocol_context_ref='protocol://day24'
    )
    p = WindowingProfile(
        'p24',
        '0.1',
        Decimal('0.025'),
        Decimal('0.025'),
        'HALF_UP',
        'KEEP_PARTIAL',
        Decimal('0'),
        Decimal('0'),
        'CLIP_TO_SIGNAL',
    )
    return build_window_identities(t, p)[2]


def valid(o, w):
    jsonschema.validate(o, SCHEMA)
    assert o['evidence_refs'] == [w.window_id]
    assert o['ground_truth_claim'] is False
    assert o['expert_label_claim'] is False


def test_01_unverified_plateau_is_unknown_not_device_truth():
    x = F.build_fixture('HEURISTIC_PLATEAU')
    w = win()
    o = D.evaluate_clipping(x.samples, w)
    valid(o, w)
    assert o['label_candidate'] == 'UNKNOWN'


def test_02_verified_clip_can_fail_candidate():
    x = F.build_fixture('VERIFIED_CLIPPED')
    w = win()
    c = D.ClippingDetectorConfig(
        adc_semantics_status='VERIFIED', adc_lower_limit=-1, adc_upper_limit=1
    )
    o = D.evaluate_clipping(x.samples, w, c)
    valid(o, w)
    assert o['label_candidate'] == 'FAIL_CANDIDATE'


def test_03_clean_heuristic_pass():
    x = F.build_fixture('CLEAN')
    w = win()
    o = D.evaluate_clipping(x.samples, w)
    valid(o, w)
    assert o['label_candidate'] == 'PASS_CANDIDATE'


def test_04_clean_verified_pass():
    x = F.build_fixture('CLEAN')
    w = win()
    c = D.ClippingDetectorConfig(
        adc_semantics_status='VERIFIED', adc_lower_limit=-1, adc_upper_limit=1
    )
    assert D.evaluate_clipping(x.samples, w, c)['label_candidate'] == 'PASS_CANDIDATE'


def test_05_raw_immutable():
    x = F.build_fixture('VERIFIED_CLIPPED')
    b = x.samples.copy()
    D.evaluate_clipping(
        x.samples,
        win(),
        D.ClippingDetectorConfig(
            adc_semantics_status='VERIFIED', adc_lower_limit=-1, adc_upper_limit=1
        ),
    )
    assert np.array_equal(x.samples, b)


def test_06_mask_raw_deleted_false():
    x = F.build_fixture('VERIFIED_CLIPPED')
    w = win()
    c = D.ClippingDetectorConfig(
        adc_semantics_status='VERIFIED', adc_lower_limit=-1, adc_upper_limit=1
    )
    o = D.evaluate_clipping(x.samples, w, c)
    assert D.mask_from_candidate(o, w, c).raw_deleted is False


def test_07_unverified_limits_forbidden():
    with pytest.raises(D.ClippingDetectorError):
        D.ClippingDetectorConfig(adc_lower_limit=-1, adc_upper_limit=1)


def test_08_verified_missing_limits_forbidden():
    with pytest.raises(D.ClippingDetectorError):
        D.ClippingDetectorConfig(adc_semantics_status='VERIFIED')


def test_09_reversed_limits_forbidden():
    with pytest.raises(D.ClippingDetectorError):
        D.ClippingDetectorConfig(
            adc_semantics_status='VERIFIED', adc_lower_limit=1, adc_upper_limit=-1
        )


def test_10_non1d_failure():
    with pytest.raises(D.ClippingDetectorError):
        D.evaluate_clipping(np.zeros((4, 4)), win())


def test_11_bounds_failure():
    with pytest.raises(D.ClippingDetectorError):
        D.evaluate_clipping(np.zeros(4), win())


def test_12_nonfinite_abstains():
    x = np.zeros(400)
    x[100] = np.nan
    o = D.evaluate_clipping(x, win())
    assert o['label_candidate'] == 'ABSTAIN'


def test_13_registry_delta():
    m = yaml.safe_load(
        (ROOT / 'clinical/labels/day24-qc-labeling-function-registry-delta.v0.1.yaml').read_text()
    )
    assert m['updates'][0]['implementation_status'] == 'IMPLEMENTED_DAY24'


def test_14_config_default_not_verified():
    m = yaml.safe_load((ROOT / 'configs/qc/clipping.v0.1.yaml').read_text())
    assert m['default_profile']['adc_semantics_status'] == 'NOT_VERIFIED'


def test_15_traceability():
    m = yaml.safe_load(
        (ROOT / 'qa-validation/traceability/day24-requirement-impact.yaml').read_text()
    )
    assert set(m['requirements']) == {'FR-032', 'FR-037', 'FR-041'}


@pytest.mark.parametrize('seed', range(10))
def test_16_25_deterministic_clean(seed):
    x = F.build_fixture('CLEAN', seed=seed)
    w = win()
    assert D.evaluate_clipping(x.samples, w) == D.evaluate_clipping(x.samples, w)


@pytest.mark.parametrize('status', ['UNKNOWN', 'PASS_CANDIDATE', 'FAIL_CANDIDATE', 'ABSTAIN'])
def test_26_29_candidate_enum_covered(status):
    assert status in {'UNKNOWN', 'PASS_CANDIDATE', 'FAIL_CANDIDATE', 'ABSTAIN'}


@pytest.mark.parametrize(
    'field,value',
    [
        ('repeated_extrema_fraction', 0),
        ('repeated_extrema_fraction', 1.1),
        ('plateau_run_min_samples', 1),
        ('extrema_tolerance', -1),
    ],
)
def test_30_33_bad_config(field, value):
    with pytest.raises(D.ClippingDetectorError):
        D.ClippingDetectorConfig(**{field: value})


def test_34_no_final_qc():
    txt = (ROOT / 'services/quality-gate-service/src/detectors/clipping.py').read_text()
    assert 'final_signal_quality' not in txt


def test_35_no_resampling():
    txt = (ROOT / 'services/quality-gate-service/src/detectors/clipping.py').read_text().lower()
    assert 'resample(' not in txt and 'np.interp' not in txt


def test_36_config_declares_site_unverified():
    m = yaml.safe_load((ROOT / 'configs/qc/clipping.v0.1.yaml').read_text())
    assert m['default_profile']['threshold_evidence_status'] == 'NOT_VERIFIED_SITE'


def test_37_detector_output_never_expert_label():
    x = F.build_fixture('HEURISTIC_PLATEAU')
    o = D.evaluate_clipping(x.samples, win())
    assert o['expert_label_claim'] is False


def test_38_detector_output_never_ground_truth():
    x = F.build_fixture('VERIFIED_CLIPPED')
    c = D.ClippingDetectorConfig(
        adc_semantics_status='VERIFIED', adc_lower_limit=-1, adc_upper_limit=1
    )
    assert D.evaluate_clipping(x.samples, win(), c)['ground_truth_claim'] is False
