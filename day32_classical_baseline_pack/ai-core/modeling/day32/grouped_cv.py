from __future__ import annotations
import numpy as np
from sklearn.model_selection import StratifiedGroupKFold

def make_grouped_folds(y, groups, n_splits: int, seed: int = 3201) -> list[dict]:
    y = np.asarray(y)
    groups = np.asarray(groups)
    if len(np.unique(groups)) < n_splits:
        raise ValueError("Not enough groups for requested splits")
    splitter = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    folds = []
    dummy_X = np.zeros((len(y), 1))
    for fold_id, (train_idx, valid_idx) in enumerate(splitter.split(dummy_X, y, groups)):
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
