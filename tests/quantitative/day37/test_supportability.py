import pytest
from day37.supportability import (
    create_metric_result,
    map_error_to_supportability,
)
from day37.types import (
    ConstantVectorError,
    NonFiniteInputError,
    ZeroNormVectorError,
)


def test_map_error_to_supportability():
    state, reason = map_error_to_supportability(NonFiniteInputError())
    assert state == "QUALITY_BLOCKED"
    assert reason == "NONFINITE_VALUES"
    
    state, reason = map_error_to_supportability(ZeroNormVectorError())
    assert state == "ZERO_NORM_VECTOR"
    
    state, reason = map_error_to_supportability(ConstantVectorError())
    assert state == "CONSTANT_VECTOR"

def test_create_metric_result_blocks_invalid_state():
    with pytest.raises(ValueError, match="UNKNOWN_SUPPORTABILITY"):
        create_metric_result("fam", "id", 1.0, "INVALID_STATE", [], {})

def test_create_metric_result_blocks_zero_sentinel():
    with pytest.raises(ValueError, match="INELIGIBLE_VALUE_MUST_NOT_BE_ZERO_SENTINEL"):
        create_metric_result("fam", "id", 0.0, "CONSTANT_VECTOR", [], {})

def test_create_metric_result_allows_valid_zero():
    res = create_metric_result("fam", "id", 0.0, "SUPPORTED", [], {})
    assert res.value == 0.0
