"""Deterministic latency math shared by UC1 replay and presentation layers."""

from __future__ import annotations

from collections.abc import Iterable
import math
from numbers import Real


class LatencyMetricsError(ValueError):
    """Stable typed error raised for invalid latency inputs."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _nonnegative_finite_latency(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise LatencyMetricsError("LATENCY_VALUE_INVALID")
    numeric = float(value)
    if not math.isfinite(numeric) or numeric < 0.0:
        raise LatencyMetricsError("LATENCY_VALUE_INVALID")
    return numeric


def nearest_rank_percentile(
    values_ms: Iterable[float],
    percentile: float,
) -> float:
    """Return a percentile using the inclusive nearest-rank definition.

    ``percentile`` is expressed as a fraction in ``(0, 1]``.  The input is
    copied before sorting, so callers retain their original ordering.
    """

    if isinstance(percentile, bool) or not isinstance(percentile, Real):
        raise LatencyMetricsError("PERCENTILE_OUT_OF_RANGE")
    percentile_value = float(percentile)
    if not math.isfinite(percentile_value) or not 0.0 < percentile_value <= 1.0:
        raise LatencyMetricsError("PERCENTILE_OUT_OF_RANGE")

    try:
        raw_values = tuple(values_ms)
    except TypeError as exc:
        raise LatencyMetricsError("LATENCY_VALUES_INVALID") from exc
    if not raw_values:
        raise LatencyMetricsError("LATENCY_VALUES_EMPTY")

    try:
        ordered = sorted(_nonnegative_finite_latency(value) for value in raw_values)
    except LatencyMetricsError:
        raise
    except TypeError as exc:
        raise LatencyMetricsError("LATENCY_VALUE_INVALID") from exc

    rank = max(1, math.ceil(percentile_value * len(ordered)))
    return ordered[rank - 1]


def total_latency_ms(*components_ms: float) -> float:
    """Return the sum of one or more nonnegative finite latency components."""

    if not components_ms:
        raise LatencyMetricsError("LATENCY_COMPONENT_INVALID")
    try:
        components = tuple(
            _nonnegative_finite_latency(component) for component in components_ms
        )
    except LatencyMetricsError as exc:
        raise LatencyMetricsError("LATENCY_COMPONENT_INVALID") from exc
    return float(sum(components))


__all__ = [
    "LatencyMetricsError",
    "nearest_rank_percentile",
    "total_latency_ms",
]
