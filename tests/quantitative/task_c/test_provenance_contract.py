import pytest
from day37.similarity import normalized_euclidean
from day37.types import Day37DomainError

def test_provenance_required_for_scaler():
    with pytest.raises(Day37DomainError) as excinfo:
        normalized_euclidean([1.0], [1.0], scaler_hash=None)
    assert excinfo.value.reason_code == "MISSING_SCALER_PROVENANCE"
        
    res = normalized_euclidean([1.0], [1.0], scaler_hash="valid_hash")
    assert isinstance(res, float)
