from __future__ import annotations
from pathlib import Path
import hashlib
import yaml

def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def load_authorization(path: str | Path) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))

def validate_real_authorization(auth: dict, dataset_id: str, feature_arm: str, model_id: str) -> None:
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
    return (
        auth.get("scope") == "SYNTHETIC_TOOLING_SMOKE"
        and auth.get("synthetic_smoke_fitting_allowed") is True
        and auth.get("real_data_allowed") is False
        and auth.get("sealed_test_access_allowed") is False
        and auth.get("pooled_training_allowed") is False
    )
