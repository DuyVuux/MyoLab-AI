from __future__ import annotations
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC, SVC

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
    "cnn", "lstm", "transformer", "automl", "online_learning",
    "domain_adaptation", "fatigue_classifier", "pooled_cross_dataset",
)

def build_core_models(seed: int = 3201) -> dict[str, object]:
    return {
        "dummy_majority": DummyClassifier(strategy="most_frequent"),
        "dummy_stratified": DummyClassifier(strategy="stratified", random_state=seed),
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
    return {
        "knn": Pipeline([
            ("scaler", StandardScaler()),
            ("model", KNeighborsClassifier(n_neighbors=5, weights="distance")),
        ]),
        "qda_regularized": Pipeline([
            ("scaler", StandardScaler()),
            ("model", QuadraticDiscriminantAnalysis(reg_param=0.1)),
        ]),
        "rbf_svm": Pipeline([
            ("scaler", StandardScaler()),
            ("model", SVC(C=1.0, gamma="scale", kernel="rbf", probability=False, random_state=seed)),
        ]),
        "gradient_boosting": GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=2,
            random_state=seed,
        ),
    }
