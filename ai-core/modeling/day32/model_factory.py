"""Day 32 — Model factory for core and optional classical baselines.

Implements Execution Plan §1 (Model Scope) and §6 (Model Contract).
All hyperparameters match the fixed smoke configurations exactly.
"""
from __future__ import annotations

from sklearn.discriminant_analysis import (
    LinearDiscriminantAnalysis,
    QuadraticDiscriminantAnalysis,
)
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC, LinearSVC

# ---------------------------------------------------------------------------
# Allowlists & Blocklists  (Execution Plan §1)
# ---------------------------------------------------------------------------

CORE_MODEL_IDS = (
    "dummy_majority",
    "dummy_stratified",
    "lda_shrinkage",
    "logistic_regression",
    "linear_svm",
    "random_forest",
)

OPTIONAL_MODEL_IDS = (
    "knn",
    "qda_regularized",
    "rbf_svm",
    "gradient_boosting",
)

PROHIBITED_DAY32 = (
    "cnn",
    "lstm",
    "transformer",
    "automl",
    "online_learning",
    "domain_adaptation",
    "fatigue_classifier",
    "pooled_cross_dataset",
)

# ---------------------------------------------------------------------------
# Tiny controlled grids  (Execution Plan §6.2)
# ---------------------------------------------------------------------------

TINY_GRIDS: dict[str, dict[str, list]] = {
    "logistic_regression": {"model__C": [0.1, 1.0, 10.0]},
    "linear_svm": {"model__C": [0.1, 1.0, 10.0]},
    "random_forest": {"max_depth": [None, 12], "min_samples_leaf": [1, 5]},
}


# ---------------------------------------------------------------------------
# Factory functions  (Execution Plan §6.1)
# ---------------------------------------------------------------------------

def build_core_models(seed: int = 3201) -> dict[str, object]:
    """Return the six mandatory core classifiers.

    Scalers are embedded inside Pipeline objects for models that require
    scaling (LDA, Logistic Regression, Linear SVM). This ensures scaling
    parameters are always fitted only on training data within each fold.
    """
    return {
        "dummy_majority": DummyClassifier(strategy="most_frequent"),
        "dummy_stratified": DummyClassifier(
            strategy="stratified", random_state=seed
        ),
        "lda_shrinkage": Pipeline([
            ("scaler", StandardScaler()),
            ("model", LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto")),
        ]),
        "logistic_regression": Pipeline([
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(
                C=1.0,
                solver="lbfgs",
                class_weight="balanced",
                max_iter=2000,
                random_state=seed,
            )),
        ]),
        "linear_svm": Pipeline([
            ("scaler", StandardScaler()),
            ("model", LinearSVC(
                C=1.0,
                class_weight="balanced",
                dual="auto",
                random_state=seed,
            )),
        ]),
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced_subsample",
            max_features="sqrt",
            random_state=seed,
            n_jobs=1,
        ),
    }


def build_optional_models(seed: int = 3201) -> dict[str, object]:
    """Return optional classifiers gated behind core gate pass.

    Each optional model has its own eligibility gate (§6.4, §6.5).
    """
    return {
        "knn": Pipeline([
            ("scaler", StandardScaler()),
            ("model", KNeighborsClassifier(
                n_neighbors=5, weights="distance", metric="euclidean"
            )),
        ]),
        "qda_regularized": Pipeline([
            ("scaler", StandardScaler()),
            ("model", QuadraticDiscriminantAnalysis(reg_param=0.1)),
        ]),
        "rbf_svm": Pipeline([
            ("scaler", StandardScaler()),
            ("model", SVC(
                C=1.0, gamma="scale", kernel="rbf",
                probability=False, random_state=seed,
            )),
        ]),
        "gradient_boosting": GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=2,
            random_state=seed,
        ),
    }
