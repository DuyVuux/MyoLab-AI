"""Day 32 — Grouped cross-validation with leakage detection.

Implements StratifiedGroupKFold with explicit group-overlap checks
to prevent subject leakage between train and validation folds.

Reference: Execution Plan §4.2 (Primary regime — cross-subject grouped CV).
"""
from __future__ import annotations

import numpy as np
from sklearn.model_selection import StratifiedGroupKFold


def make_grouped_folds(
    y,
    groups,
    n_splits: int,
    seed: int = 3201,
) -> list[dict]:
    """Create stratified group-aware CV folds with leakage guard.

    Parameters
    ----------
    y : array-like
        Target labels.
    groups : array-like
        Subject/group identifiers. No subject may appear in both
        train and validation within a single fold.
    n_splits : int
        Number of outer folds.
    seed : int
        Random state for reproducibility.

    Returns
    -------
    list[dict]
        Each dict contains fold_id, train_indices, validation_indices,
        train_groups, and validation_groups.

    Raises
    ------
    ValueError
        If there are fewer unique groups than requested splits.
    RuntimeError
        If group leakage is detected (defensive — should never happen
        with StratifiedGroupKFold, but checked as a safety net).
    """
    y = np.asarray(y)
    groups = np.asarray(groups)

    if len(np.unique(groups)) < n_splits:
        raise ValueError(
            f"Not enough groups ({len(np.unique(groups))}) "
            f"for requested splits ({n_splits})"
        )

    splitter = StratifiedGroupKFold(
        n_splits=n_splits, shuffle=True, random_state=seed
    )
    dummy_X = np.zeros((len(y), 1))
    folds = []

    for fold_id, (train_idx, valid_idx) in enumerate(
        splitter.split(dummy_X, y, groups)
    ):
        train_groups = set(groups[train_idx].tolist())
        valid_groups = set(groups[valid_idx].tolist())
        overlap = sorted(train_groups & valid_groups)
        if overlap:
            raise RuntimeError(f"GROUP_LEAKAGE:{overlap}")
        folds.append({
            "fold_id": fold_id,
            "train_indices": train_idx.tolist(),
            "validation_indices": valid_idx.tolist(),
            "train_groups": sorted(train_groups),
            "validation_groups": sorted(valid_groups),
        })

    return folds
