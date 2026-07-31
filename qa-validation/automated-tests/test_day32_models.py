"""Day 32 — Model factory tests.

Verifies:
  • Exact core model allowlist matches CORE_MODEL_IDS
  • Optional model allowlist matches OPTIONAL_MODEL_IDS
  • Prohibited models are absent
  • Required pipelines embed StandardScaler
  • Tree/dummy models do NOT have scalers
  • TINY_GRIDS keys match tunable models
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "modeling"))

from sklearn.pipeline import Pipeline

from day32.model_factory import (
    CORE_MODEL_IDS,
    OPTIONAL_MODEL_IDS,
    PROHIBITED_DAY32,
    TINY_GRIDS,
    build_core_models,
    build_optional_models,
)


def test_exact_core_model_allowlist():
    models = build_core_models()
    assert tuple(models.keys()) == CORE_MODEL_IDS


def test_optional_model_allowlist():
    models = build_optional_models()
    assert tuple(models.keys()) == OPTIONAL_MODEL_IDS


def test_scalers_are_inside_required_pipelines():
    """LDA, LR, LinearSVM must have scaler inside pipeline (§5.4)."""
    models = build_core_models()
    for model_id in ("lda_shrinkage", "logistic_regression", "linear_svm"):
        assert isinstance(models[model_id], Pipeline), f"{model_id} must be Pipeline"
        assert "scaler" in models[model_id].named_steps, f"{model_id} missing scaler"


def test_tree_and_dummy_have_no_scaler():
    """Random Forest and Dummy models must NOT be wrapped in pipeline."""
    models = build_core_models()
    for model_id in ("dummy_majority", "dummy_stratified", "random_forest"):
        assert not isinstance(models[model_id], Pipeline), (
            f"{model_id} should not be a Pipeline"
        )


def test_prohibited_models_absent():
    all_ids = set(build_core_models()) | set(build_optional_models())
    assert not (all_ids & set(PROHIBITED_DAY32))


def test_optional_models_have_scalers_where_required():
    """KNN, QDA, RBF SVM require scaling (§5.4)."""
    models = build_optional_models()
    for model_id in ("knn", "qda_regularized", "rbf_svm"):
        assert isinstance(models[model_id], Pipeline), f"{model_id} must be Pipeline"
        assert "scaler" in models[model_id].named_steps


def test_gradient_boosting_no_scaler():
    models = build_optional_models()
    assert not isinstance(models["gradient_boosting"], Pipeline)


def test_tiny_grids_cover_tunable_models():
    """TINY_GRIDS keys must be a subset of core model IDs."""
    assert set(TINY_GRIDS.keys()).issubset(set(CORE_MODEL_IDS))


def test_core_model_count_is_exactly_six():
    assert len(CORE_MODEL_IDS) == 6
    assert len(build_core_models()) == 6


def test_optional_model_count_is_exactly_four():
    assert len(OPTIONAL_MODEL_IDS) == 4
    assert len(build_optional_models()) == 4
