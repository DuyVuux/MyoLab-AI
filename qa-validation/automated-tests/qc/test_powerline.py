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

from semg_core.qc_windowing import (
    CanonicalChannelTimeline,
    WindowingProfile,
    build_window_identities,
)
import detectors.powerline as D

SCHEMA = json.loads(
    (ROOT / 'packages/common-schemas/json/labeling-function-output.schema.json').read_text()
)


def window(sample_count=1000, fs=2000):
    t = CanonicalChannelTimeline(
        session_id='ses_qc',
        channel_id='ch_qc',
        source_id='src_qc',
        sample_count=sample_count,
        sampling_rate_hz=Decimal(str(fs)),
        protocol_context_ref='protocol://synthetic',
    )
    p = WindowingProfile(
        profile_id='qc-test',
        version='0.1',
        requested_duration_seconds=Decimal('0.25'),
        requested_step_seconds=Decimal('0.25'),
        rounding_policy='HALF_UP',
        boundary_policy='KEEP_PARTIAL',
        context_before_seconds=Decimal('0.05'),
        context_after_seconds=Decimal('0.05'),
        context_boundary_policy='CLIP_TO_SIGNAL',
    )
    return build_window_identities(t, p)[0]


def validate(o, w):
    jsonschema.validate(o, SCHEMA)
    assert o['evidence_refs'][0] == w.window_id
    assert o['ground_truth_claim'] is False
    assert o['expert_label_claim'] is False


def sig(freq=80, line=0.0, fs=2000, n=1000):
    t = np.arange(n) / fs
    return np.sin(2 * np.pi * freq * t) + line * np.sin(2 * np.pi * 50 * t)


def cfg():
    return D.PowerlineConfig(
        mains_frequency_hz=50.0,
        site_config_status='VERIFIED',
        warning_ratio=0.03,
        high_ratio=0.08,
    )


def test_01_unknown_mains_abstains():
    w = window()
    o = D.evaluate_powerline(sig(), w)
    validate(o, w)
    assert o['label_candidate'] == 'ABSTAIN'


def test_02_strong_line_warns_not_fails():
    w = window()
    o = D.evaluate_powerline(sig(line=4.0), w, cfg())
    validate(o, w)
    assert o['label_candidate'] == 'WARNING_CANDIDATE'
    assert o['reason_code'] == 'POWERLINE_INTERFERENCE_SUSPECTED'


def test_03_clean_pass_candidate():
    w = window()
    o = D.evaluate_powerline(sig(line=0.0), w, cfg())
    validate(o, w)
    assert o['label_candidate'] == 'PASS_CANDIDATE'


def test_04_raw_immutable():
    x = sig(line=2.0)
    b = x.copy()
    D.evaluate_powerline(x, window(), cfg())
    assert np.array_equal(x, b)


def test_05_no_notch_filter_source():
    text = (
        ROOT / 'services/quality-gate-service/src/detectors/powerline.py'
    ).read_text().lower()
    assert (
        'notch(' not in text and 'iirnotch' not in text and ('filtfilt' not in text)
    )


def test_06_no_session_blocking_symbols():
    text = (
        ROOT / 'services/quality-gate-service/src/detectors/powerline.py'
    ).read_text()
    assert (
        'final_signal_quality' not in text
        and 'summarize_session_coverage' not in text
    )


def test_07_window_link_exact():
    w = window()
    assert (
        D.evaluate_powerline(sig(), w, cfg())['evidence_refs'][0]
        == w.window_id
    )


def test_08_invalid_verified_frequency():
    with pytest.raises(D.PowerlineDetectorError):
        D.PowerlineConfig(
            mains_frequency_hz=55, site_config_status='VERIFIED'
        )


def test_09_non1d_typed_failure():
    with pytest.raises(D.PowerlineDetectorError):
        D.evaluate_powerline(np.zeros((2, 2)), window(), cfg())


def test_10_short_abstain():
    w = window(sample_count=20, fs=2000)
    o = D.evaluate_powerline(np.zeros(20), w, cfg())
    assert o['label_candidate'] == 'ABSTAIN'


@pytest.mark.parametrize('seed', range(12))
def test_11_22_deterministic(seed):
    rng = np.random.default_rng(seed)
    x = sig() + 0.001 * rng.normal(size=1000)
    w = window()
    assert D.evaluate_powerline(x, w, cfg()) == D.evaluate_powerline(
        x, w, cfg()
    )


def test_23_registry_delta():
    m = yaml.safe_load(
        (
            ROOT
            / 'clinical/labels/day26-qc-labeling-function-registry-delta.v0.1.yaml'
        ).read_text()
    )
    assert m['updates'][0]['lf_id'] == 'LF_POWERLINE'


def test_24_reason_delta():
    m = yaml.safe_load(
        (
            ROOT
            / 'services/quality-gate-service/configs/day26-reason-code-delta.v0.1.yaml'
        ).read_text()
    )
    assert 'POWERLINE_INTERFERENCE_SUSPECTED' in {
        x['code'] for x in m['reason_codes']
    }


def test_25_traceability():
    m = yaml.safe_load(
        (
            ROOT
            / 'qa-validation/traceability/day26-requirement-impact.yaml'
        ).read_text()
    )
    assert set(m['requirements']) == {'FR-034', 'FR-037', 'FR-041'}


def test_26_config_explicit_unknown():
    m = yaml.safe_load(
        (ROOT / 'configs/qc/powerline.v0.1.yaml').read_text()
    )
    assert m['site']['status'] == 'NOT_VERIFIED'
    assert m['site']['mains_frequency_hz'] is None


@pytest.mark.parametrize('line', [0.0, 0.1, 0.5, 1.0, 2.0, 4.0])
def test_27_32_schema(line):
    w = window()
    o = D.evaluate_powerline(sig(line=line), w, cfg())
    validate(o, w)
    assert o['label_candidate'] != 'FAIL_CANDIDATE'


def test_33_no_resampling():
    text = (
        ROOT / 'services/quality-gate-service/src/detectors/powerline.py'
    ).read_text().lower()
    assert 'resample(' not in text and 'np.interp' not in text


def test_34_no_ground_truth_literals_true():
    text = (
        ROOT / 'services/quality-gate-service/src/detectors/powerline.py'
    ).read_text()
    assert '"ground_truth_claim": True' not in text


def test_35_powerline_not_unusable_contract():
    o = D.evaluate_powerline(sig(line=5), window(), cfg())
    assert o['qc_supportability'] == 'REVIEW_REQUIRED'


def test_36_native_fs_used():
    w = window(fs=1000)
    x = sig(fs=1000)
    o = D.evaluate_powerline(
        x,
        w,
        D.PowerlineConfig(
            mains_frequency_hz=50.0,
            site_config_status='VERIFIED',
            warning_ratio=0.03,
            high_ratio=0.08,
        ),
    )
    validate(o, w)
