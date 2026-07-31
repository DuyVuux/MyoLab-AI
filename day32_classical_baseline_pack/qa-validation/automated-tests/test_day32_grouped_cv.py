import numpy as np
from day32.grouped_cv import make_grouped_folds

def test_no_group_overlap():
    y = np.array(["a","a","b","b"] * 6)
    groups = np.repeat([f"S{i}" for i in range(12)], 2)
    folds = make_grouped_folds(y, groups, n_splits=3)
    for fold in folds:
        assert set(fold["train_groups"]).isdisjoint(fold["validation_groups"])
