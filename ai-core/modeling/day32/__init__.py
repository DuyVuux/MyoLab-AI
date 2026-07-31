"""Day 32 — Classical Baseline Modeling modules.

Public API for model construction, validation gates, metrics,
grouped cross-validation, and authorization checks.
"""

from .model_factory import (
    build_core_models,
    build_optional_models,
    CORE_MODEL_IDS,
    OPTIONAL_MODEL_IDS,
    PROHIBITED_DAY32,
)
from .authorization import (
    sha256_file,
    load_authorization,
    validate_real_authorization,
    synthetic_smoke_authorized,
)
from .matrix_gate import validate_matrix, EXPECTED_DIMENSIONS
from .grouped_cv import make_grouped_folds
from .aggregation import aggregate_window_labels, aggregate_window_probabilities
from .metrics import repetition_metrics, subject_macro_repetition_macro_f1
from .smoke_runner import run_synthetic_core_smoke
from .core_gate import decide_core_gate
