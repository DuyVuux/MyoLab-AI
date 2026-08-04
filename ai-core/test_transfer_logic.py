import pytest
import numpy as np
from transfer.domain_gap import standardized_mean_difference, rbf_mmd, per_feature_wasserstein
from transfer.guards import validate_zero_shot_manifest, ZeroShotViolationError
from transfer.representation import channel_summary_representation

def test_smd_calculation():
    s = np.array([[1.0, 2.0], [3.0, 4.0]])
    t = np.array([[1.0, 2.0], [3.0, 4.0]])
    smd = standardized_mean_difference(s, t)
    assert np.allclose(smd, [0.0, 0.0])
    
    t_diff = np.array([[5.0, 6.0], [7.0, 8.0]])
    smd_diff = standardized_mean_difference(s, t_diff)
    assert not np.allclose(smd_diff, [0.0, 0.0])

def test_smd_dimension_mismatch():
    s = np.array([[1.0, 2.0]])
    t = np.array([[1.0, 2.0, 3.0]])
    with pytest.raises(ValueError, match="Feature mismatch"):
        standardized_mean_difference(s, t)

def test_rbf_mmd_identical():
    s = np.array([[1.0, 2.0], [3.0, 4.0]])
    mmd, gamma = rbf_mmd(s, s)
    assert mmd == 0.0
    
def test_channel_summary():
    # shape: 2 samples, 3 channels, 4 features
    x = np.ones((2, 3, 4))
    res = channel_summary_representation(x)
    assert res.shape == (2, 20) # 4 features * 5 stats (mean, std, min, max, median)
    
def test_channel_summary_invalid_dims():
    x = np.ones((2, 4)) # 2D array
    with pytest.raises(ValueError, match="EXPECTED_ROWS_CHANNELS_FEATURES"):
        channel_summary_representation(x)
        
def test_channel_summary_non_finite():
    x = np.ones((2, 3, 4))
    x[0, 0, 0] = np.nan
    with pytest.raises(ValueError, match="NONFINITE_FEATURES"):
        channel_summary_representation(x)

def test_guards_valid():
    manifest = {
        "target_scaler_fit": False,
        "target_model_fit": False,
        "target_calibrator_fit": False,
        "target_threshold_fit": False,
        "pooled_training": False,
        "sealed_test_opened": False,
        "some_other_key": True
    }
    assert validate_zero_shot_manifest(manifest) == True
    
def test_guards_invalid():
    manifest = {"target_scaler_fit": True, "pooled_training": False}
    with pytest.raises(ZeroShotViolationError, match="ZERO_SHOT_VIOLATION"):
        validate_zero_shot_manifest(manifest)
