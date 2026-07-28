from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[2]

def load(rel): return yaml.safe_load((ROOT/rel).read_text(encoding='utf-8'))

def test_all_blueprint_configs_block_training():
    for p in (ROOT/'ai-core/configs').glob('*.yaml'):
        d=yaml.safe_load(p.read_text(encoding='utf-8'))
        if isinstance(d,dict) and 'trainingAllowed' in d:
            assert d['trainingAllowed'] is False, p

def test_task_separation():
    d=load('ai-core/configs/task_contracts.research.yaml')
    assert d['tasks']['TaskB']['hard_fatigue_classifier_default'] is False
    assert d['tasks']['TaskC']['classifier_required'] is False
    assert d['mfcv']['site_eligibility']=='NOT_VERIFIED'

def test_model_ladder_has_required_families_and_no_winner():
    d=load('ai-core/configs/model_ladder.research.yaml')
    ids={x['id'] for x in d['minimum_baseline_set']}
    assert {'dummy_majority','dummy_stratified','lda','logistic_regression','linear_svm','random_forest'} <= ids
    assert d['winner_selected'] is False
