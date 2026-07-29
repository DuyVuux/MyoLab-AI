from __future__ import annotations

import numpy as np


PROHIBITED_SCALING = frozenset(
    {
        "global_dataset_zscore",
        "global_dataset_robust_scaler",
        "per_trial_zscore_primary",
    }
)
ALLOWED_FEATURE_SCALING = frozenset(
    {
        "none",
        "training_fold_per_feature_zscore",
        "training_fold_robust_scaler",
    }
)


def remove_dc_mean(signal: np.ndarray, axis: int = 0) -> np.ndarray:
    source = np.asarray(signal, dtype=float)
    if source.ndim == 0 or source.size == 0:
        raise ValueError("signal must be a non-empty array")
    if not np.isfinite(source).all():
        raise ValueError("signal must contain only finite values")
    if not -source.ndim <= axis < source.ndim:
        raise ValueError("axis is out of bounds")
    return source - np.mean(source, axis=axis, keepdims=True)


def validate_scaling_policy(policy_id: str) -> None:
    if policy_id in PROHIBITED_SCALING:
        raise ValueError(f"Prohibited scaling policy: {policy_id}")
    if policy_id not in ALLOWED_FEATURE_SCALING:
        raise ValueError(f"Unknown scaling policy: {policy_id}")

