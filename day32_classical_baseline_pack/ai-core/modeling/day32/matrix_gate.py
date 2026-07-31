from __future__ import annotations
import numpy as np

EXPECTED_DIMENSIONS = {
    ("mendeley_core4_primary_v1", "F-TD8"): 24,
    ("mendeley_core4_primary_v1", "F-SP6"): 18,
    ("mendeley_core4_primary_v1", "F-ALL14"): 42,
    ("grabmyo_project_subset_native28_v1", "F-TD8"): 224,
    ("grabmyo_project_subset_native28_v1", "F-SP6"): 168,
    ("grabmyo_project_subset_native28_v1", "F-ALL14"): 392,
}

def validate_matrix(
    X: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    dataset_ids: np.ndarray,
    dataset_view_id: str,
    feature_arm: str,
) -> dict:
    errors: list[str] = []
    X = np.asarray(X)
    y = np.asarray(y)
    groups = np.asarray(groups)
    dataset_ids = np.asarray(dataset_ids)
    if X.ndim != 2:
        errors.append("X_not_2d")
    if len({len(y), len(groups), len(dataset_ids), X.shape[0]}) != 1:
        errors.append("row_count_mismatch")
    expected = EXPECTED_DIMENSIONS.get((dataset_view_id, feature_arm))
    if expected is None:
        errors.append("unknown_view_arm")
    elif X.shape[1] != expected:
        errors.append(f"MATRIX_DIMENSION_MISMATCH:{X.shape[1]}!={expected}")
    if not np.isfinite(X).all():
        errors.append("NONFINITE_MATRIX")
    unique_datasets = sorted(set(dataset_ids.tolist()))
    if len(unique_datasets) != 1:
        errors.append(f"POOLED_DATASET_BLOCKED:{unique_datasets}")
    if len(set(groups.tolist())) < 2:
        errors.append("insufficient_groups")
    if len(set(y.tolist())) < 2:
        errors.append("insufficient_classes")
    return {
        "pass": not errors,
        "errors": errors,
        "row_count": int(X.shape[0]) if X.ndim == 2 else 0,
        "feature_count": int(X.shape[1]) if X.ndim == 2 else 0,
        "dataset_ids": unique_datasets,
        "group_count": len(set(groups.tolist())),
        "class_count": len(set(y.tolist())),
    }
