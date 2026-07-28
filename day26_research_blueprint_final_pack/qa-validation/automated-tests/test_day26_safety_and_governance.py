from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[2]

def test_registry_states_and_separation_of_duties():
    d=yaml.safe_load((ROOT/'ai-core/configs/model_registry_states.research.yaml').read_text(encoding='utf-8'))
    assert 'clinical-validated' not in d['states']
    assert d['single_operator_may_self_approve_pilot'] is False

def test_training_authorization_fails_closed():
    d=yaml.safe_load((ROOT/'ai-core/configs/training_authorization.research.yaml').read_text(encoding='utf-8'))
    assert d['trainingAllowed'] is False
    assert d['resolved_dependency_lock_present'] is False
    assert d['authorization_record_present'] is False

def test_mfcv_optional_and_fatigue_not_diagnosis():
    d=yaml.safe_load((ROOT/'ai-core/configs/fatigue_experiments.research.yaml').read_text(encoding='utf-8'))
    assert d['default_architecture']['hard_fatigue_diagnosis'] is False
    assert d['mfcv']['site_eligibility']=='NOT_VERIFIED'
