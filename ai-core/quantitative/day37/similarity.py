
import numpy as np

from .types import (
    ConstantVectorError,
    Day37DomainError,
    NonFiniteInputError,
    ZeroNormVectorError,
)

EPS = 1e-12

def _vectors(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    a = np.asarray(x, dtype=float)
    b = np.asarray(y, dtype=float)
    if a.shape != b.shape or a.ndim != 1:
        raise Day37DomainError("Vector shape mismatch.", "VECTOR_SHAPE_MISMATCH")
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise NonFiniteInputError()
    return a, b

def cosine_similarity(x: np.ndarray, y: np.ndarray, epsilon: float = EPS) -> float:
    a, b = _vectors(x, y)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    if norm_a <= epsilon or norm_b <= epsilon:
        raise ZeroNormVectorError()
        
    denominator = float(norm_a * norm_b)
    return float(np.dot(a, b) / denominator)

def pearson_similarity(x: np.ndarray, y: np.ndarray, epsilon: float = EPS) -> float:
    a, b = _vectors(x, y)
    if float(np.std(a)) <= epsilon or float(np.std(b)) <= epsilon:
        raise ConstantVectorError()
        
    return float(np.corrcoef(a, b)[0, 1])

def normalized_euclidean(x: np.ndarray, y: np.ndarray, scaler_hash: str | None = None) -> float:
    # Day 37 contract requires a scaler_hash to prove it's using a frozen scaler.
    if not scaler_hash:
        raise Day37DomainError("Scaler hash is required for normalized Euclidean.", "MISSING_SCALER_PROVENANCE")
        
    a, b = _vectors(x, y)
    return float(np.linalg.norm(a - b) / np.sqrt(len(a)))

def template_distance(query: np.ndarray, template: np.ndarray, template_source: str | None = None) -> float:
    if not template_source:
        raise Day37DomainError("Template source must be explicitly declared.", "MISSING_TEMPLATE_PROVENANCE")
    a, b = _vectors(query, template)
    return float(np.linalg.norm(a - b) / np.sqrt(len(a)))
