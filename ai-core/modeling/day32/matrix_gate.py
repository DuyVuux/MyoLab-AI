"""Day 32 — Feature matrix validation gate.

Validates pivoted feature matrices before any model fitting:
  • Correct dimensionality per dataset_view × feature_arm
  • No non-finite values (NaN/Inf)
  • No pooled datasets (single dataset_id per matrix)
  • Minimum group and class counts

Reference: Execution Plan §5 (Matrix Materialization & Null Policy).
"""
from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# Expected column counts  (Execution Plan §3 + §5.2)
# ---------------------------------------------------------------------------

EXPECTED_DIMENSIONS: dict[tuple[str, str], int] = {
    # Mendeley — 3 channels (CH1, CH2, CH3)
    ("mendeley_core4_primary_v1", "F-TD8"): 24,
    ("mendeley_core4_primary_v1", "F-SP6"): 18,
    ("mendeley_core4_primary_v1", "F-ALL14"): 42,
    ("mendeley_core4_primary_v1", "F-NO-MOMENTS12"): 36,
    # GRABMyo — 28 channels (F1-F16 + W1-W12)
    ("grabmyo_project_subset_native28_v1", "F-TD8"): 224,
    ("grabmyo_project_subset_native28_v1", "F-SP6"): 168,
    ("grabmyo_project_subset_native28_v1", "F-ALL14"): 392,
    ("grabmyo_project_subset_native28_v1", "F-NO-MOMENTS12"): 336,
}


def validate_matrix(
    X: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    dataset_ids: np.ndarray,
    dataset_view_id: str,
    feature_arm: str,
) -> dict:
    """Validate a pivoted feature matrix against the Day 32 contract.

    Returns a dict with ``"pass"`` boolean, ``"errors"`` list, and
    summary statistics. Fails closed on any contract violation.
    """
    errors: list[str] = []
    X = np.asarray(X)
    y = np.asarray(y)
    groups = np.asarray(groups)
    dataset_ids = np.asarray(dataset_ids)

    # Shape checks
    if X.ndim != 2:
        errors.append("X_not_2d")
    if len({len(y), len(groups), len(dataset_ids), X.shape[0]}) != 1:
        errors.append("row_count_mismatch")

    # Dimension contract
    expected = EXPECTED_DIMENSIONS.get((dataset_view_id, feature_arm))
    if expected is None:
        errors.append("unknown_view_arm")
    elif X.ndim == 2 and X.shape[1] != expected:
        errors.append(f"MATRIX_DIMENSION_MISMATCH:{X.shape[1]}!={expected}")

    # Non-finite check  (§5.3 — no impute zero)
    if X.ndim == 2 and not np.isfinite(X).all():
        nan_count = int(np.isnan(X).sum())
        inf_count = int(np.isinf(X).sum())
        errors.append(f"NONFINITE_MATRIX:nan={nan_count},inf={inf_count}")

    # Pooled dataset guard
    unique_datasets = sorted(set(dataset_ids.tolist()))
    if len(unique_datasets) != 1:
        errors.append(f"POOLED_DATASET_BLOCKED:{unique_datasets}")

    # Minimum diversity
    n_groups = len(set(groups.tolist()))
    n_classes = len(set(y.tolist()))
    if n_groups < 2:
        errors.append("insufficient_groups")
    if n_classes < 2:
        errors.append("insufficient_classes")

    return {
        "pass": not errors,
        "errors": errors,
        "row_count": int(X.shape[0]) if X.ndim == 2 else 0,
        "feature_count": int(X.shape[1]) if X.ndim == 2 else 0,
        "dataset_ids": unique_datasets,
        "group_count": n_groups,
        "class_count": n_classes,
    }
