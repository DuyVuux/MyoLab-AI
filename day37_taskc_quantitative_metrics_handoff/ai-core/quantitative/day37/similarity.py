from __future__ import annotations
import numpy as np

EPS = 1e-12

def _vectors(x, y):
    a = np.asarray(x, dtype=float)
    b = np.asarray(y, dtype=float)
    if a.shape != b.shape or a.ndim != 1:
        raise ValueError("VECTOR_SHAPE_MISMATCH")
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("NONFINITE_VECTOR")
    return a, b

def cosine_similarity(x, y, epsilon: float = EPS):
    a, b = _vectors(x, y)
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denominator <= epsilon:
        return None, "ZERO_NORM_VECTOR"
    return float(np.dot(a, b) / denominator), None

def pearson_similarity(x, y, epsilon: float = EPS):
    a, b = _vectors(x, y)
    if float(np.std(a)) <= epsilon or float(np.std(b)) <= epsilon:
        return None, "CONSTANT_VECTOR"
    return float(np.corrcoef(a, b)[0, 1]), None

def normalized_euclidean(x, y):
    a, b = _vectors(x, y)
    return float(np.linalg.norm(a - b) / np.sqrt(len(a)))

def template_distance(query, template):
    return normalized_euclidean(query, template)
