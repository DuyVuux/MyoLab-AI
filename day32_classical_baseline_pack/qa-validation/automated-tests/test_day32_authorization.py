import pytest
from day32.authorization import validate_real_authorization, synthetic_smoke_authorized

def test_real_authorization_fails_closed():
    with pytest.raises(PermissionError):
        validate_real_authorization({}, "m", "F-TD8", "lda_shrinkage")

def test_synthetic_authorization_is_narrow():
    auth = {
        "scope":"SYNTHETIC_TOOLING_SMOKE",
        "synthetic_smoke_fitting_allowed":True,
        "real_data_allowed":False,
        "sealed_test_access_allowed":False,
        "pooled_training_allowed":False,
    }
    assert synthetic_smoke_authorized(auth)
