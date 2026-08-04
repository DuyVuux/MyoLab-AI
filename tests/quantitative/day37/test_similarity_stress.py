import numpy as np
import pytest
from day37.similarity import (
    cosine_similarity,
    normalized_euclidean,
    pearson_similarity,
    template_distance,
)
from day37.types import (
    ConstantVectorError,
    Day37DomainError,
    ZeroNormVectorError,
)


def test_cosine_similarity_zero_norm():
    with pytest.raises(ZeroNormVectorError):
        cosine_similarity([0.0, 0.0], [1.0, 2.0])

def test_pearson_similarity_constant_vector():
    with pytest.raises(ConstantVectorError):
        pearson_similarity([1.0, 1.0, 1.0], [1.0, 2.0, 3.0])

def test_normalized_euclidean_requires_scaler_hash():
    with pytest.raises(Day37DomainError, match="Scaler hash is required"):
        normalized_euclidean([1.0, 2.0], [1.1, 1.9])
    
    # With hash it should work
    res = normalized_euclidean([1.0, 2.0], [1.1, 1.9], scaler_hash="hash123")
    assert isinstance(res, float)

def test_template_distance_requires_provenance():
    with pytest.raises(Day37DomainError, match="Template source must be explicitly declared"):
        template_distance([1.0], [1.0])

@pytest.mark.performance
@pytest.mark.slow
def test_similarity_performance_1M_samples():
    arr1 = np.random.rand(1_000_000)
    arr2 = np.random.rand(1_000_000)
    res = cosine_similarity(arr1, arr2)
    assert isinstance(res, float)
