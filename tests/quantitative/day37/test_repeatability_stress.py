import numpy as np
import pytest
from day37.repeatability import (
    bland_altman,
    pair_repeatability,
    within_subject_cv,
)
from day37.types import (
    Day37DomainError,
    InsufficientRepetitionsError,
    NonFiniteInputError,
)


def test_pair_repeatability_zero_denominator():
    with pytest.raises(Day37DomainError, match="Denominator near zero"):
        pair_repeatability(0.0, 0.0)

def test_within_subject_cv_insufficient():
    with pytest.raises(InsufficientRepetitionsError):
        within_subject_cv([1.0, 2.0], True)

def test_within_subject_cv_nonfinite():
    with pytest.raises(NonFiniteInputError):
        within_subject_cv([1.0, np.nan, 3.0], True)

def test_within_subject_cv_negative():
    with pytest.raises(Day37DomainError, match="Values must be non-negative"):
        within_subject_cv([1.0, -2.0, 3.0], True)

def test_within_subject_cv_not_ratio_scale():
    with pytest.raises(Day37DomainError, match="Metric not positive ratio scale"):
        within_subject_cv([1.0, 2.0, 3.0], False)

def test_bland_altman_output_schema():
    res = bland_altman([1.0, 2.0], [1.1, 1.9])
    assert "bias" in res
    assert "loa_low" in res
    assert "loa_high" in res
    assert "bias_ci_low" in res
    assert res["bias_ci_low"] is None  # Check that CI fields are present but empty

@pytest.mark.performance
@pytest.mark.slow
def test_repeatability_performance_1M_samples():
    """Stress test with large arrays to ensure it scales reasonably without OOM or extreme time."""
    arr1 = np.random.rand(1_000_000)
    arr2 = np.random.rand(1_000_000)
    # pair_repeatability works on scalars normally in the metric logic, but if passed arrays...
    # wait, pair_repeatability expects float. We'll stress Bland-Altman instead.
    res = bland_altman(arr1, arr2)
    assert res["n_pairs"] == 1_000_000
    assert "bias" in res
