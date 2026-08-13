from __future__ import annotations

FORBIDDEN_ON_LOCKED = {
    'threshold_tuning','algorithm_selection','normalization_fit','feature_selection','model_training'
}

class LockedSetAccessError(PermissionError):
    pass

def assert_access(split: str, purpose: str) -> None:
    if split == 'LOCKED_EVALUATION' and purpose in FORBIDDEN_ON_LOCKED:
        raise LockedSetAccessError(f'{purpose} forbidden on locked evaluation data')
