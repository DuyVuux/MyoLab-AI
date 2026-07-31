"""Day 32 — Authorization tests.

Verifies:
  • Real authorization fails closed when flags are missing
  • Sealed test access is blocked
  • Pooled training is blocked
  • Synthetic smoke authorization is correctly narrow
  • Full real authorization passes with correct flags
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "modeling"))

import pytest

from day32.authorization import (
    synthetic_smoke_authorized,
    validate_real_authorization,
)


def test_real_authorization_fails_closed():
    """Empty auth must raise PermissionError."""
    with pytest.raises(PermissionError, match="AUTHORIZATION_MISSING"):
        validate_real_authorization({}, "m", "F-TD8", "lda_shrinkage")


def test_sealed_test_must_be_false():
    """Auth with sealed_test_access_allowed=True must be blocked."""
    auth = {
        "training_allowed": True,
        "model_fitting_allowed": True,
        "scaler_fitting_allowed": True,
        "feature_matrix_pivot_allowed": True,
        "day32_authorization_present": True,
        "sealed_test_access_allowed": True,
        "pooled_training_allowed": False,
        "locked_inputs": {
            "dataset_views": ["m"],
            "feature_arms": ["F-TD8"],
            "model_allowlist": ["lda_shrinkage"],
        },
    }
    with pytest.raises(PermissionError, match="SEALED_TEST"):
        validate_real_authorization(auth, "m", "F-TD8", "lda_shrinkage")


def test_pooled_training_must_be_false():
    """Auth with pooled_training_allowed=True must be blocked."""
    auth = {
        "training_allowed": True,
        "model_fitting_allowed": True,
        "scaler_fitting_allowed": True,
        "feature_matrix_pivot_allowed": True,
        "day32_authorization_present": True,
        "sealed_test_access_allowed": False,
        "pooled_training_allowed": True,
        "locked_inputs": {
            "dataset_views": ["m"],
            "feature_arms": ["F-TD8"],
            "model_allowlist": ["lda_shrinkage"],
        },
    }
    with pytest.raises(PermissionError, match="POOLED"):
        validate_real_authorization(auth, "m", "F-TD8", "lda_shrinkage")


def test_real_authorization_passes_with_correct_flags():
    """Full authorization with all correct flags must not raise."""
    auth = {
        "training_allowed": True,
        "model_fitting_allowed": True,
        "scaler_fitting_allowed": True,
        "feature_matrix_pivot_allowed": True,
        "day32_authorization_present": True,
        "sealed_test_access_allowed": False,
        "pooled_training_allowed": False,
        "locked_inputs": {
            "dataset_views": ["mendeley_core4_primary_v1"],
            "feature_arms": ["F-TD8"],
            "model_allowlist": ["lda_shrinkage"],
        },
    }
    # Should not raise
    validate_real_authorization(
        auth, "mendeley_core4_primary_v1", "F-TD8", "lda_shrinkage"
    )


def test_unauthorized_model_is_blocked():
    """Model not in allowlist must be blocked."""
    auth = {
        "training_allowed": True,
        "model_fitting_allowed": True,
        "scaler_fitting_allowed": True,
        "feature_matrix_pivot_allowed": True,
        "day32_authorization_present": True,
        "sealed_test_access_allowed": False,
        "pooled_training_allowed": False,
        "locked_inputs": {
            "dataset_views": ["m"],
            "feature_arms": ["F-TD8"],
            "model_allowlist": ["lda_shrinkage"],
        },
    }
    with pytest.raises(PermissionError, match="Model not authorized"):
        validate_real_authorization(auth, "m", "F-TD8", "random_forest")


def test_synthetic_authorization_is_narrow():
    auth = {
        "scope": "SYNTHETIC_TOOLING_SMOKE",
        "synthetic_smoke_fitting_allowed": True,
        "real_data_allowed": False,
        "sealed_test_access_allowed": False,
        "pooled_training_allowed": False,
    }
    assert synthetic_smoke_authorized(auth)


def test_synthetic_authorization_rejects_real_data():
    auth = {
        "scope": "SYNTHETIC_TOOLING_SMOKE",
        "synthetic_smoke_fitting_allowed": True,
        "real_data_allowed": True,  # <-- should fail
        "sealed_test_access_allowed": False,
        "pooled_training_allowed": False,
    }
    assert not synthetic_smoke_authorized(auth)
