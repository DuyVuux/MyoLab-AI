import sys
from pathlib import Path
import numpy as np
import pytest
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "quantitative"))
from day37.cocontraction import cocontraction_eligibility, cocontraction_metrics

def test_mapping_unverified_blocked():
    result = cocontraction_eligibility({
        "verified_agonist_antagonist_mapping": False,
        "same_side": True,
        "synchronized_time_base": True,
        "compatible_envelope_units": True,
        "active_phase_present": True,
        "normalization_method": "mvc",
        "quality_status": "pass",
    })
    assert not result["eligible"]
    assert result["state"] == "NOT_ELIGIBLE_ANATOMICAL_MAPPING_UNVERIFIED"

def test_quality_fail_blocked():
    result = cocontraction_eligibility({
        "verified_agonist_antagonist_mapping": True,
        "same_side": True,
        "synchronized_time_base": True,
        "compatible_envelope_units": True,
        "active_phase_present": True,
        "normalization_method": "mvc",
        "quality_status": "fail",
    })
    assert result["state"] == "QUALITY_BLOCKED"

def test_identical_envelopes_maximal_cci():
    a = np.ones(100)
    result = cocontraction_metrics(a, a, 0.01, 0.1, 0.1)
    assert result["mean_cci"] > 0.999
    assert result["overlap_area_ratio"] > 0.999
    assert result["simultaneous_activation_duration_fraction"] == 1.0

def test_negative_envelope_blocked():
    with pytest.raises(ValueError):
        cocontraction_metrics([1,-1], [1,1], 0.01)
