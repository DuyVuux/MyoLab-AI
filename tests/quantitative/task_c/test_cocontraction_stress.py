import numpy as np
import pytest
from day37.cocontraction import (
    cocontraction_eligibility,
    cocontraction_metrics,
)
from day37.types import (
    AnatomicalMappingUnverifiedError,
    Day37DomainError,
    InsufficientActiveSignalError,
    InvalidEnvelopeValueError,
)


def test_cocontraction_eligibility_mendeley_grabmyo():
    with pytest.raises(AnatomicalMappingUnverifiedError):
        cocontraction_eligibility({"dataset_id": "mendeley"})
        
    with pytest.raises(AnatomicalMappingUnverifiedError):
        cocontraction_eligibility({"dataset_id": "grabmyo"})

def test_cocontraction_eligibility_missing_fields():
    with pytest.raises(Day37DomainError, match="NOT_ELIGIBLE_UNSYNCHRONIZED"):
        cocontraction_eligibility({
            "verified_agonist_antagonist_mapping": True,
            "same_side": True,
            "compatible_envelope_units": True,
            "active_phase_present": True,
            # Missing synchronized_time_base
        })

def test_cocontraction_negative_envelope():
    with pytest.raises(InvalidEnvelopeValueError):
        cocontraction_metrics([1.0, -1.0], [1.0, 1.0], 0.1)

def test_cocontraction_zero_envelopes():
    with pytest.raises(InsufficientActiveSignalError):
        cocontraction_metrics([0.0, 0.0], [0.0, 0.0], 0.1)

@pytest.mark.performance
@pytest.mark.slow
def test_cocontraction_performance_1M_samples():
    arr1 = np.abs(np.random.rand(1_000_000)) + 0.1
    arr2 = np.abs(np.random.rand(1_000_000)) + 0.1
    res = cocontraction_metrics(arr1, arr2, dt_seconds=0.01)
    assert "mean_cci" in res
    assert "overlap_area_ratio" in res
