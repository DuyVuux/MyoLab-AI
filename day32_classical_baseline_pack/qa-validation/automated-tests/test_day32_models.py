from sklearn.pipeline import Pipeline
from day32.model_factory import (
    build_core_models, build_optional_models,
    CORE_MODEL_IDS, OPTIONAL_MODEL_IDS, PROHIBITED_DAY32,
)

def test_exact_core_model_allowlist():
    models = build_core_models()
    assert tuple(models.keys()) == CORE_MODEL_IDS

def test_optional_model_allowlist():
    models = build_optional_models()
    assert tuple(models.keys()) == OPTIONAL_MODEL_IDS

def test_scalers_are_inside_required_pipelines():
    models = build_core_models()
    for model_id in ("lda_shrinkage", "logistic_regression", "linear_svm"):
        assert isinstance(models[model_id], Pipeline)
        assert "scaler" in models[model_id].named_steps

def test_prohibited_models_absent():
    all_ids = set(build_core_models()) | set(build_optional_models())
    assert not (all_ids & set(PROHIBITED_DAY32))
