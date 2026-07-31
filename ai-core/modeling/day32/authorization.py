"""Day 32 — Authorization guard for model fitting.

Implements a fail-closed authorization model:
  • Real fitting requires ALL flags explicitly set.
  • Sealed test must be blocked.
  • Pooled training must be blocked.
  • Synthetic smoke has its own narrow scope.

Reference: Execution Plan §6 (Bước 6 — Authorization).
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import yaml


def sha256_file(path: str | Path) -> str:
    """Compute SHA-256 hex digest for a file (streaming, 1 MiB chunks)."""
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_authorization(path: str | Path) -> dict:
    """Load a YAML authorization document."""
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def validate_real_authorization(
    auth: dict,
    dataset_id: str,
    feature_arm: str,
    model_id: str,
) -> None:
    """Raise PermissionError if authorization is incomplete or unsafe.

    This is a fail-closed gate: every required flag must be explicitly True,
    and every prohibited flag must be explicitly False.
    """
    required_true = (
        "training_allowed",
        "model_fitting_allowed",
        "scaler_fitting_allowed",
        "feature_matrix_pivot_allowed",
        "day32_authorization_present",
    )
    missing = [key for key in required_true if auth.get(key) is not True]
    if missing:
        raise PermissionError(f"AUTHORIZATION_MISSING:{missing}")

    if auth.get("sealed_test_access_allowed") is not False:
        raise PermissionError("SEALED_TEST_ACCESS_BLOCKED")
    if auth.get("pooled_training_allowed") is not False:
        raise PermissionError("POOLED_DATASET_BLOCKED")

    locked = auth.get("locked_inputs", {})
    if dataset_id not in locked.get("dataset_views", []):
        raise PermissionError(f"Dataset not authorized: {dataset_id}")
    if feature_arm not in locked.get("feature_arms", []):
        raise PermissionError(f"Feature arm not authorized: {feature_arm}")
    if model_id not in locked.get("model_allowlist", []):
        raise PermissionError(f"Model not authorized: {model_id}")


def synthetic_smoke_authorized(auth: dict) -> bool:
    """Check whether the authorization allows synthetic tooling smoke only."""
    return (
        auth.get("scope") == "SYNTHETIC_TOOLING_SMOKE"
        and auth.get("synthetic_smoke_fitting_allowed") is True
        and auth.get("real_data_allowed") is False
        and auth.get("sealed_test_access_allowed") is False
        and auth.get("pooled_training_allowed") is False
    )
