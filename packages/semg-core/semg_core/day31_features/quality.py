"""Feature-quality, redundancy, and channel-summary utilities."""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

import numpy as np
from scipy.stats import rankdata

_SUMMARY_KEYS = (
    "count",
    "finite_count",
    "finite_ratio",
    "missing_ratio",
    "zero_ratio",
    "near_constant",
    "minimum",
    "q01",
    "q25",
    "median",
    "q75",
    "q90",
    "q99",
    "maximum",
    "iqr",
    "outlier_rate_robust_z5",
)


def summarize_feature(
    values: Sequence[float] | np.ndarray,
    *,
    near_constant_absolute_tolerance: float = 1e-12,
) -> dict[str, int | float | bool | None]:
    """Return a stable-schema robust summary for one feature group."""

    vector = np.asarray(values, dtype=np.float64)
    if vector.ndim != 1:
        raise ValueError("values must be one-dimensional")
    if near_constant_absolute_tolerance < 0.0:
        raise ValueError("near_constant_absolute_tolerance must be non-negative")
    finite = vector[np.isfinite(vector)]
    count = int(vector.size)
    finite_count = int(finite.size)
    finite_ratio = float(finite_count / count) if count else 0.0
    base: dict[str, int | float | bool | None] = {
        "count": count,
        "finite_count": finite_count,
        "finite_ratio": finite_ratio,
        "missing_ratio": float(1.0 - finite_ratio) if count else 1.0,
        "zero_ratio": None,
        "near_constant": False,
        "minimum": None,
        "q01": None,
        "q25": None,
        "median": None,
        "q75": None,
        "q90": None,
        "q99": None,
        "maximum": None,
        "iqr": None,
        "outlier_rate_robust_z5": None,
    }
    if finite_count == 0:
        return {name: base[name] for name in _SUMMARY_KEYS}

    quantiles = np.quantile(
        finite,
        [0.01, 0.25, 0.50, 0.75, 0.90, 0.99],
    )
    q01, q25, median, q75, q90, q99 = map(float, quantiles)
    iqr = q75 - q25
    median_absolute_deviation = float(
        np.median(np.abs(finite - median))
    )
    if median_absolute_deviation > 0.0:
        robust_z = (
            0.6744897501960817
            * (finite - median)
            / median_absolute_deviation
        )
        outlier_mask = np.abs(robust_z) > 5.0
    else:
        outlier_mask = np.abs(finite - median) > near_constant_absolute_tolerance

    base.update(
        {
            "zero_ratio": float(np.mean(finite == 0.0)),
            "near_constant": bool(
                iqr <= near_constant_absolute_tolerance
                or np.ptp(finite) <= near_constant_absolute_tolerance
            ),
            "minimum": float(np.min(finite)),
            "q01": q01,
            "q25": q25,
            "median": median,
            "q75": q75,
            "q90": q90,
            "q99": q99,
            "maximum": float(np.max(finite)),
            "iqr": iqr,
            "outlier_rate_robust_z5": float(np.mean(outlier_mask)),
        }
    )
    return {name: base[name] for name in _SUMMARY_KEYS}


def _correlation(left: np.ndarray, right: np.ndarray) -> float:
    if left.size < 3 or np.ptp(left) == 0.0 or np.ptp(right) == 0.0:
        return math.nan
    return float(np.corrcoef(left, right)[0, 1])


def correlation_pairs(
    matrix: np.ndarray,
    feature_names: Sequence[str],
    threshold: float = 0.95,
) -> list[dict[str, Any]]:
    """Report high Pearson and Spearman pairs using pairwise-complete rows."""

    values = np.asarray(matrix, dtype=np.float64)
    names = tuple(feature_names)
    if values.ndim != 2 or values.shape[1] != len(names):
        raise ValueError("matrix shape does not match feature_names")
    if len(set(names)) != len(names):
        raise ValueError("feature_names must be unique")
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be in [0, 1]")

    pairs: list[dict[str, Any]] = []
    for left_index, left_name in enumerate(names):
        for right_index in range(left_index + 1, len(names)):
            right_name = names[right_index]
            mask = np.isfinite(values[:, left_index]) & np.isfinite(
                values[:, right_index]
            )
            left = values[mask, left_index]
            right = values[mask, right_index]
            for method, method_left, method_right in (
                ("pearson", left, right),
                ("spearman", rankdata(left), rankdata(right)),
            ):
                coefficient = _correlation(method_left, method_right)
                if math.isfinite(coefficient) and abs(coefficient) >= threshold:
                    pairs.append(
                        {
                            "feature_a": left_name,
                            "feature_b": right_name,
                            "method": method,
                            "correlation": coefficient,
                            "pairwise_count": int(left.size),
                        }
                    )
    return pairs


def cross_channel_summary(
    channel_feature_matrix: np.ndarray,
    *,
    feature_names: Sequence[str],
    active_channel_mask: np.ndarray,
) -> dict[str, float | None]:
    """Create the registered five-statistic cross-source representation."""

    matrix = np.asarray(channel_feature_matrix, dtype=np.float64)
    names = tuple(feature_names)
    active = np.asarray(active_channel_mask)
    if matrix.ndim != 2 or matrix.shape[1] != len(names):
        raise ValueError("matrix shape does not match feature_names")
    if matrix.shape[0] == 0:
        raise ValueError("at least one channel is required")
    if active.ndim != 1 or active.size != matrix.shape[0]:
        raise ValueError("active_channel_mask must align with channels")
    if active.dtype != np.bool_:
        raise ValueError("active_channel_mask must be boolean")

    active_fraction = float(np.mean(active))
    summary: dict[str, float | None] = {}
    for index, name in enumerate(names):
        finite = matrix[np.isfinite(matrix[:, index]), index]
        if finite.size:
            q25, median, q75, q90 = np.quantile(
                finite,
                [0.25, 0.50, 0.75, 0.90],
            )
            values: tuple[float | None, ...] = (
                float(median),
                float(q75 - q25),
                float(q90),
                float(np.max(finite)),
                active_fraction,
            )
        else:
            values = (None, None, None, None, active_fraction)
        for suffix, value in zip(
            (
                "median",
                "iqr",
                "q90",
                "maximum",
                "active_channel_fraction",
            ),
            values,
            strict=True,
        ):
            summary[f"{name}__{suffix}"] = value
    return summary
