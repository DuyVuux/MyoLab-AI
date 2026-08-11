from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import sys
import jsonschema
import numpy as np
import pytest
import yaml
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'packages' / 'semg-core'))
from semg_core.qc_windowing import CanonicalChannelTimeline, WindowingProfile, build_window_identities
from decimal import Decimal

def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod
D = load(ROOT / 'services/quality-gate-service/src/detectors/dropout.py', 'day23_dropout')
F = load(ROOT / 'qa-validation/test-data/synthetic/generators/semg_dropout_factory.py', 'day23_factory')
SCHEMA = json.loads((ROOT / 'packages/common-schemas/json/labeling-function-output.schema.json').read_text())

def window(sample_count=400, fs=2000):
    timeline = CanonicalChannelTimeline(session_id='ses_23', channel_id='ch_23', source_id='src_23', sample_count=sample_count, sampling_rate_hz=Decimal(str(fs)), protocol_context_ref='protocol://synthetic/day23')
    profile = WindowingProfile(profile_id='day23-test', version='0.1', requested_duration_seconds=Decimal('0.05'), requested_step_seconds=Decimal('0.05'), rounding_policy='HALF_UP', boundary_policy='KEEP_PARTIAL', context_before_seconds=Decimal('0.01'), context_after_seconds=Decimal('0.01'), context_boundary_policy='CLIP_TO_SIGNAL')
    items = build_window_identities(timeline, profile)
    return items[min(1, len(items) - 1)]

def validate(o):
    jsonschema.validate(o, SCHEMA)
    assert o['evidence_refs'] == [o['evidence_refs'][0]]
    assert o['ground_truth_claim'] is False
    assert o['expert_label_claim'] is False

def test_01_factory_deterministic():
    a = F.build_fixture('MISSING', seed=7)
    b = F.build_fixture('MISSING', seed=7)
    assert np.array_equal(a.samples, b.samples, equal_nan=True)
    assert a.fixture_id == b.fixture_id

@pytest.mark.parametrize('scenario', ['CLEAN', 'MISSING', 'ZERO_DROPOUT', 'FLATLINE'])
def test_02_05_factory_marks_synthetic_truth(scenario):
    x = F.build_fixture(scenario)
    assert x.truth_is_synthetic_known_truth is True
    assert x.clinical_evidence is False

def test_06_missing_fail_candidate():
    x = F.build_fixture('MISSING', start_sample=100, duration_samples=100)
    o = D.evaluate_dropout_missing(x.samples, window())
    validate(o)
    assert o['label_candidate'] == 'FAIL_CANDIDATE'
    assert o['reason_code'] == 'MISSING_DROPOUT'

def test_07_zero_dropout_fail_candidate():
    x = F.build_fixture('ZERO_DROPOUT', start_sample=100, duration_samples=100)
    o = D.evaluate_dropout_missing(x.samples, window())
    validate(o)
    assert o['label_candidate'] == 'FAIL_CANDIDATE'

def test_08_flatline_fail_candidate():
    x = F.build_fixture('FLATLINE', start_sample=100, duration_samples=100)
    o = D.evaluate_flatline(x.samples, window())
    validate(o)
    assert o['reason_code'] == 'FLATLINE_DETECTED'

def test_09_clean_dropout_pass_candidate():
    x = F.build_fixture('CLEAN')
    o = D.evaluate_dropout_missing(x.samples, window())
    validate(o)
    assert o['label_candidate'] == 'PASS_CANDIDATE'

def test_10_clean_flatline_pass_candidate():
    x = F.build_fixture('CLEAN')
    o = D.evaluate_flatline(x.samples, window())
    validate(o)
    assert o['label_candidate'] == 'PASS_CANDIDATE'

def test_11_window_id_reused_exactly():
    x = F.build_fixture('MISSING')
    w = window()
    assert D.evaluate_dropout_missing(x.samples, w)['evidence_refs'] == [w.window_id]

def test_12_raw_not_mutated_missing():
    x = F.build_fixture('MISSING')
    before = x.samples.copy()
    D.evaluate_dropout_missing(x.samples, window())
    assert np.array_equal(x.samples, before, equal_nan=True)

def test_13_raw_not_mutated_flatline():
    x = F.build_fixture('FLATLINE')
    before = x.samples.copy()
    D.evaluate_flatline(x.samples, window())
    assert np.array_equal(x.samples, before, equal_nan=True)

def test_14_mask_never_deletes_raw():
    x = F.build_fixture('FLATLINE')
    w = window()
    o = D.evaluate_flatline(x.samples, w)
    m = D.mask_from_candidate(o, w, D.DropoutDetectorConfig())
    assert m.raw_deleted is False and m.masked is True

def test_15_short_window_abstains():
    x = np.arange(5, dtype=float)
    w = window(sample_count=5, fs=100)
    o = D.evaluate_dropout_missing(x, w)
    assert o['label_candidate'] == 'ABSTAIN'

def test_16_non_1d_typed_failure():
    with pytest.raises(D.DropoutDetectorError):
        D.evaluate_dropout_missing(np.zeros((4, 4)), window())

def test_17_bad_window_bounds_typed_failure():
    w = window()
    with pytest.raises(D.DropoutDetectorError):
        D.evaluate_dropout_missing(np.zeros(10), w)

@pytest.mark.parametrize('field,value', [('missing_warning_fraction', -0.1), ('missing_fail_fraction', 1.1), ('zero_run_warning_fraction', -0.1), ('zero_run_fail_fraction', 1.1)])
def test_18_21_invalid_fraction_config(field, value):
    kwargs = {field: value}
    with pytest.raises(D.DropoutDetectorError):
        D.DropoutDetectorConfig(**kwargs)

def test_22_invalid_threshold_order():
    with pytest.raises(D.DropoutDetectorError):
        D.DropoutDetectorConfig(missing_warning_fraction=0.8, missing_fail_fraction=0.2)

def test_23_manifest_is_synthetic_only():
    m = yaml.safe_load((ROOT / 'qa-validation/test-data/golden/qc/dropout/manifest.yaml').read_text())
    assert m['status'] == 'SYNTHETIC_KNOWN_TRUTH_ONLY'
    assert m['clinical_evidence'] is False
    assert m['rules']['interpolation_forbidden'] is True

def test_24_registry_delta_has_both_lfs():
    m = yaml.safe_load((ROOT / 'clinical/labels/day23-qc-labeling-function-registry-delta.v0.1.yaml').read_text())
    ids = {x['lf_id'] for x in m['updates']}
    assert ids == {'LF_MISSING_DROPOUT', 'LF_FLATLINE'}

def test_25_reason_delta_has_flatline():
    m = yaml.safe_load((ROOT / 'services/quality-gate-service/configs/day23-reason-code-delta.v0.1.yaml').read_text())
    assert 'FLATLINE_DETECTED' in {x['code'] for x in m['reason_codes']}

def test_26_traceability():
    m = yaml.safe_load((ROOT / 'qa-validation/traceability/day23-requirement-impact.yaml').read_text())
    assert set(m['requirements']) == {'FR-031', 'FR-037', 'FR-040', 'AC-03'}

@pytest.mark.parametrize('seed', range(10))
def test_27_36_deterministic_candidate(seed):
    x = F.build_fixture('CLEAN', seed=seed)
    w = window()
    a = D.evaluate_dropout_missing(x.samples, w)
    b = D.evaluate_dropout_missing(x.samples, w)
    assert a == b

@pytest.mark.parametrize('scenario', ['MISSING', 'ZERO_DROPOUT', 'FLATLINE', 'CLEAN'])
def test_37_40_every_output_never_claims_ground_truth(scenario):
    x = F.build_fixture(scenario)
    w = window()
    fn = D.evaluate_flatline if scenario == 'FLATLINE' else D.evaluate_dropout_missing
    o = fn(x.samples, w)
    validate(o)

def test_41_no_final_session_qc_symbols():
    text = (ROOT / 'services/quality-gate-service/src/detectors/dropout.py').read_text()
    assert 'final_signal_quality' not in text
    assert 'summarize_session_coverage' not in text

def test_42_no_interpolation_resampling():
    text = (ROOT / 'services/quality-gate-service/src/detectors/dropout.py').read_text().lower()
    assert 'np.interp' not in text
    assert 'resample(' not in text
