from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "semg-core"))
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day31.contracts import (
    expected_arm_dimensions,
    resolve_feature_arms,
)
from semg_core.day31_features import FEATURE_ORDER
from semg_core.day31_features.quality import (
    correlation_pairs,
    cross_channel_summary,
    summarize_feature,
)


def test_quality_summary_has_stable_schema_for_all_missing_values() -> None:
    summary = summarize_feature([math.nan, math.inf, -math.inf])

    assert tuple(summary) == (
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
    assert summary["count"] == 3
    assert summary["finite_count"] == 0
    assert summary["finite_ratio"] == 0.0
    assert summary["median"] is None


def test_quality_summary_robust_outlier_and_near_constant_behavior() -> None:
    values = [1.0] * 100 + [100.0]
    summary = summarize_feature(values)

    assert summary["near_constant"] is True
    assert summary["outlier_rate_robust_z5"] == pytest.approx(1 / 101)
    assert summary["q90"] == pytest.approx(1.0)


def test_correlations_report_pearson_and_spearman_pairwise_complete() -> None:
    x = np.arange(20.0)
    matrix = np.column_stack(
        [
            x,
            3 * x,
            x**2,
            np.where(x == 5, math.nan, -x),
        ]
    )
    pairs = correlation_pairs(
        matrix,
        ["linear", "scaled", "quadratic", "negative"],
        threshold=0.95,
    )

    indexed = {
        (pair["feature_a"], pair["feature_b"], pair["method"]): pair
        for pair in pairs
    }
    assert indexed[("linear", "scaled", "pearson")]["correlation"] == pytest.approx(
        1.0
    )
    assert indexed[("linear", "quadratic", "spearman")][
        "correlation"
    ] == pytest.approx(1.0)
    assert indexed[("linear", "negative", "pearson")][
        "pairwise_count"
    ] == 19


def test_cross_channel_summary_is_exactly_70_dimensions() -> None:
    matrix = np.arange(4 * 14, dtype=float).reshape(4, 14)
    summary = cross_channel_summary(
        matrix,
        feature_names=FEATURE_ORDER,
        active_channel_mask=np.array([True, True, False, True]),
    )

    assert len(summary) == 70
    assert tuple(summary)[:5] == (
        "rms__median",
        "rms__iqr",
        "rms__q90",
        "rms__maximum",
        "rms__active_channel_fraction",
    )
    assert summary["rms__active_channel_fraction"] == pytest.approx(0.75)


def test_feature_arms_resolve_without_alias_or_cycles() -> None:
    config = {
        "arms": {
            "F-TD8": {"feature_ids": list(FEATURE_ORDER[:8]), "window_ms": 200},
            "F-SP6": {"feature_ids": list(FEATURE_ORDER[8:]), "window_ms": 200},
            "F-ALL14": {
                "feature_ids": list(FEATURE_ORDER),
                "window_ms": 200,
            },
            "F-NO-MOMENTS12": {
                "excludes": [
                    "skewness_unbiased",
                    "kurtosis_fisher_unbiased",
                ],
                "window_ms": 200,
            },
            "F-TD8-W250": {"inherits": "F-TD8", "window_ms": 250},
        }
    }

    resolved = resolve_feature_arms(config)
    assert len(resolved["F-NO-MOMENTS12"].feature_ids) == 12
    assert resolved["F-TD8-W250"].feature_ids == resolved["F-TD8"].feature_ids
    assert resolved["F-TD8-W250"].window_ms == 250
    assert expected_arm_dimensions(resolved, channel_count=28)["F-ALL14"] == 392

    cyclic = {
        "arms": {
            "a": {"inherits": "b"},
            "b": {"inherits": "a"},
        }
    }
    with pytest.raises(ValueError, match="cycle"):
        resolve_feature_arms(cyclic)

