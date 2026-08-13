from pathlib import Path
import csv, hashlib, importlib.util, yaml, pytest
ROOT=Path(__file__).resolve().parents[2]
SPLIT=ROOT/'qa-validation/evidence/public-benchmark-splits-v1.0.csv'
PROT=ROOT/'ai-core/configs/public-benchmark-protocol.v1.0.yaml'

def rows():
    with SPLIT.open() as f: return list(csv.DictReader(f))

def test_subjects_are_unique_and_have_one_split():
    seen={}
    for r in rows():
        key=(r['dataset_id'],r['subject_id'])
        assert key not in seen
        seen[key]=r['split']

def test_both_datasets_have_development_and_locked_subjects():
    for ds in {'GRABMYO_V1_1_0','HYSER_V2_0_0'}:
        vals={r['split'] for r in rows() if r['dataset_id']==ds}
        assert vals == {'DEVELOPMENT','LOCKED_EVALUATION'}

def test_all_sessions_remain_with_subject_row():
    assert all(r['sessions'] for r in rows())

def test_split_hash_matches_frozen_protocol():
    p=yaml.safe_load(PROT.read_text())
    assert hashlib.sha256(SPLIT.read_bytes()).hexdigest()==p['split_manifest_sha256']

def test_locked_set_tuning_is_rejected():
    path=ROOT/'ai-core/governance/locked_set_guard.py'
    spec=importlib.util.spec_from_file_location('guard',path); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    for purpose in m.FORBIDDEN_ON_LOCKED:
        with pytest.raises(m.LockedSetAccessError): m.assert_access('LOCKED_EVALUATION',purpose)

def test_development_tuning_is_not_blocked_by_locked_guard():
    path=ROOT/'ai-core/governance/locked_set_guard.py'
    spec=importlib.util.spec_from_file_location('guard2',path); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    m.assert_access('DEVELOPMENT','threshold_tuning')

def test_no_accuracy_is_preregistered_without_reference_truth():
    p=yaml.safe_load(PROT.read_text())
    assert 'accuracy' in p['forbidden_qc_outputs_without_reference']
    assert 'accuracy' not in p['preregistered_qc_outputs']
