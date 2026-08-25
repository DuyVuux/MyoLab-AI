from pathlib import Path
import hashlib, importlib.util, sys
import pytest

ROOT = Path(__file__).resolve().parents[2]
ADAPTERS = ROOT / 'data-platform/adapters/public'
FIX = ROOT / 'qa-validation/test-data/public-format-fixtures'
sys.path.insert(0, str(ADAPTERS.parent.parent.parent))

# Load public adapter package from hyphenated project path without changing canonical location.
import types
pkg = types.ModuleType('public_adapters'); pkg.__path__ = [str(ADAPTERS)]
sys.modules['public_adapters'] = pkg
for modname in ['common','wfdb16','grabmyo','hyser']:
    spec = importlib.util.spec_from_file_location(f'public_adapters.{modname}', ADAPTERS / f'{modname}.py')
    mod = importlib.util.module_from_spec(spec); sys.modules[f'public_adapters.{modname}']=mod; spec.loader.exec_module(mod)

grab = sys.modules['public_adapters.grabmyo'].adapt_grabmyo
hyser = sys.modules['public_adapters.hyser'].adapt_hyser
wfdb = sys.modules['public_adapters.wfdb16']

def test_grabmyo_golden_parse_and_explicit_mv_to_v():
    h=FIX/'session1_participant1_gesture10_trial1.hea'; d=FIX/'session1_participant1_gesture10_trial1.dat'
    before=hashlib.sha256(d.read_bytes()).hexdigest(); r=grab(h,d); after=hashlib.sha256(d.read_bytes()).hexdigest()
    assert before == after == r.source_sha256
    assert r.fs_hz == 2048
    assert set(r.units) == {'V'}
    assert r.transforms[0].source_unit == 'mV' and r.transforms[0].factor == 1e-3
    assert r.canonical_task is None

def test_hyser_golden_parse_preserves_v():
    h=FIX/'dynamic_raw_sample1.hea'; d=FIX/'dynamic_raw_sample1.dat'
    r=hyser(h,d,'subject19_session2')
    assert r.subject_id == 'hyser_subject_19'
    assert r.session_id == 'hyser_session_2'
    assert r.fs_hz == 2048 and set(r.units)=={'V'} and not r.transforms

def test_unknown_task_is_not_invented():
    r=grab(FIX/'session1_participant1_gesture10_trial1.hea',FIX/'session1_participant1_gesture10_trial1.dat')
    assert r.canonical_task is None
    assert 'PRESERVED' in r.task_reason

def test_generic_parser_accepts_mixed_sampling_rates_without_default():
    a=wfdb.read_wfdb16(FIX/'dynamic_raw_sample1.hea',FIX/'dynamic_raw_sample1.dat')
    b=wfdb.read_wfdb16(FIX/'generic_1259hz.hea',FIX/'generic_1259hz.dat')
    assert {a.fs_hz,b.fs_hz} == {2048.0,1259.0}

def test_bad_binary_count_fails_closed(tmp_path):
    h=FIX/'generic_1259hz.hea'; bad=tmp_path/'bad.dat'; bad.write_bytes(b'\x00\x00')
    with pytest.raises(wfdb.WFDBContractError): wfdb.read_wfdb16(h,bad)

def test_raw_hash_changes_if_and_only_if_bytes_change(tmp_path):
    src=FIX/'dynamic_raw_sample1.dat'; cp=tmp_path/'copy.dat'; cp.write_bytes(src.read_bytes())
    h=FIX/'dynamic_raw_sample1.hea'; r1=wfdb.read_wfdb16(h,cp); blob=bytearray(cp.read_bytes()); blob[0]^=1; cp.write_bytes(blob); r2=wfdb.read_wfdb16(h,cp)
    assert r1.source_sha256 != r2.source_sha256

def test_day13_semantics_validate_canonical_v_sampling():
    modpath = ROOT / 'services/signal-ingestion-service/src/validation/time_count_unit.py'
    spec = importlib.util.spec_from_file_location('day13_validator', modpath)
    m = importlib.util.module_from_spec(spec)
    sys.modules['day13_validator'] = m
    spec.loader.exec_module(m)
    reg = m.load_unit_registry(ROOT / 'data-platform/contracts/unit-registry.v0.1.yaml')
    r=grab(FIX/'session1_participant1_gesture10_trial1.hea',FIX/'session1_participant1_gesture10_trial1.dat')
    n=len(r.values); ts=tuple(i/r.fs_hz for i in range(n)); sig='sig_'+hashlib.sha256(b'F1').hexdigest()[:32]
    inp=m.SignalValidationInput(source_record_id='src_sha256_'+r.source_sha256,signal_id=sig,timestamps_seconds=ts,metadata_count=n,begin_time_seconds=0.0,sampling_rate_hz=r.fs_hz,unit='V')
    report=m.validate_signal(inp, registry=reg)
    assert report.overall_status.value == 'PASS'
