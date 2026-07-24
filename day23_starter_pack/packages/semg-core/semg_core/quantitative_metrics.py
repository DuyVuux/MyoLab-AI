from __future__ import annotations

from math import isfinite, sqrt
from statistics import mean, pstdev


class MetricNotComputable(ValueError):
    pass


def _finite_nonnegative(value: float, name: str) -> float:
    if not isfinite(value) or value < 0:
        raise MetricNotComputable(f"{name}_INVALID")
    return value


def safe_percent_change(current: float, baseline: float, *, epsilon: float = 1e-9) -> float:
    if not isfinite(current) or not isfinite(baseline):
        raise MetricNotComputable("PERCENT_CHANGE_NONFINITE")
    if abs(baseline) <= epsilon:
        raise MetricNotComputable("BASELINE_TOO_CLOSE_TO_ZERO")
    return 100.0 * (current - baseline) / abs(baseline)


def symmetry_ratio_percent(affected: float, reference: float, *, epsilon: float = 1e-9) -> float:
    _finite_nonnegative(affected, "AFFECTED")
    _finite_nonnegative(reference, "REFERENCE")
    if abs(reference) <= epsilon:
        raise MetricNotComputable("REFERENCE_TOO_CLOSE_TO_ZERO")
    return 100.0 * affected / reference


def coefficient_of_variation_percent(values: list[float], *, epsilon: float = 1e-9) -> float:
    if len(values) < 2:
        raise MetricNotComputable("AT_LEAST_TWO_REPETITIONS_REQUIRED")
    if not all(isfinite(value) for value in values):
        raise MetricNotComputable("REPETITION_VALUE_NONFINITE")
    mu = mean(values)
    if abs(mu) <= epsilon:
        raise MetricNotComputable("MEAN_TOO_CLOSE_TO_ZERO")
    return 100.0 * pstdev(values) / abs(mu)


def co_contraction_index_percent(agonist: float, antagonist: float, *, epsilon: float = 1e-9) -> float:
    _finite_nonnegative(agonist, "AGONIST")
    _finite_nonnegative(antagonist, "ANTAGONIST")
    denominator = agonist + antagonist
    if denominator <= epsilon:
        raise MetricNotComputable("ACTIVATION_SUM_TOO_LOW")
    return 200.0 * min(agonist, antagonist) / denominator


def cosine_similarity(a: list[float], b: list[float], *, epsilon: float = 1e-12) -> float:
    if len(a) != len(b) or not a:
        raise MetricNotComputable("VECTOR_LENGTH_MISMATCH")
    if not all(isfinite(value) for value in [*a, *b]):
        raise MetricNotComputable("VECTOR_NONFINITE")
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = sqrt(sum(x * x for x in a)); norm_b = sqrt(sum(y * y for y in b))
    if norm_a <= epsilon or norm_b <= epsilon:
        raise MetricNotComputable("VECTOR_NORM_TOO_LOW")
    return dot / (norm_a * norm_b)
