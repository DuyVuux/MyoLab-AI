from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[2]

def test_matrix_is_not_run_and_unique():
    d=yaml.safe_load((ROOT/'ai-core/configs/experiment_matrix.draft.yaml').read_text(encoding='utf-8'))
    assert d['trainingAllowed'] is False
    assert d['outer_test_opened'] is False
    ids=[r['id'] for r in d['experiments']]
    assert len(ids)==len(set(ids))
    assert all(r['result_status']=='NOT_RUN' for r in d['experiments'])
    assert {r['task'] for r in d['experiments']}=={'TaskA','TaskB','TaskC'}

def test_evaluation_contract():
    d=yaml.safe_load((ROOT/'ai-core/configs/evaluation_regimes.research.yaml').read_text(encoding='utf-8'))
    assert d['classification_metrics']['primary']['metric_id']=='subject_macro_repetition_macro_f1'
    assert d['non_negotiable_rules']['random_window_split_allowed'] is False
    assert d['statistical_reporting']['confidence_interval']['resample_unit']=='subject'
    assert d['selective_prediction']['threshold_selection']['source']=='grouped_inner_validation_cross_fitted_predictions_only'
