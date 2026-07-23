from __future__ import annotations

import pytest

from semg_core.latency_metrics import (
    LatencyMetricsError,
    nearest_rank_percentile,
    total_latency_ms,
)


LATENCY_FIXTURE_MS = [100.0, 200.0, 300.0, 400.0]


@pytest.mark.parametrize(
    ("percentile", "expected_ms"),
    [
        pytest.param(0.50, 200.0, id="p50"),
        pytest.param(0.95, 400.0, id="p95"),
    ],
)
def test_nearest_rank_percentile_known_answers(
    percentile: float,
    expected_ms: float,
) -> None:
    assert nearest_rank_percentile(LATENCY_FIXTURE_MS, percentile) == expected_ms


def test_nearest_rank_percentile_sorts_without_mutating_input() -> None:
    values = [400.0, 100.0, 300.0, 200.0]

    result = nearest_rank_percentile(values, 0.50)

    assert (result, values) == (200.0, [400.0, 100.0, 300.0, 200.0])


def test_total_latency_known_answer_is_270_ms() -> None:
    assert total_latency_ms(10.0, 200.0, 18.0, 14.0, 28.0) == 270.0


def test_nearest_rank_percentile_rejects_empty_values() -> None:
    with pytest.raises(LatencyMetricsError):
        nearest_rank_percentile([], 0.95)


@pytest.mark.parametrize(
    "percentile",
    [
        pytest.param(0.0, id="zero"),
        pytest.param(-0.1, id="negative"),
        pytest.param(1.1, id="above-one"),
        pytest.param(float("nan"), id="nan"),
        pytest.param(float("inf"), id="infinity"),
        pytest.param(True, id="boolean"),
    ],
)
def test_nearest_rank_percentile_rejects_invalid_percentile(
    percentile: float,
) -> None:
    with pytest.raises(LatencyMetricsError):
        nearest_rank_percentile(LATENCY_FIXTURE_MS, percentile)


@pytest.mark.parametrize(
    "values_ms",
    [
        pytest.param([-0.1, 1.0], id="negative"),
        pytest.param([float("nan"), 1.0], id="nan"),
        pytest.param([float("inf"), 1.0], id="positive-infinity"),
        pytest.param([float("-inf"), 1.0], id="negative-infinity"),
        pytest.param([True, 1.0], id="boolean"),
        pytest.param(["10", 20.0], id="non-numeric"),
    ],
)
def test_nearest_rank_percentile_rejects_invalid_values(
    values_ms: list[object],
) -> None:
    with pytest.raises(LatencyMetricsError):
        nearest_rank_percentile(values_ms, 0.50)  # type: ignore[arg-type]


def test_total_latency_rejects_empty_components() -> None:
    with pytest.raises(LatencyMetricsError):
        total_latency_ms()


@pytest.mark.parametrize(
    "component",
    [
        pytest.param(-0.1, id="negative"),
        pytest.param(float("nan"), id="nan"),
        pytest.param(float("inf"), id="positive-infinity"),
        pytest.param(float("-inf"), id="negative-infinity"),
        pytest.param(True, id="boolean"),
        pytest.param("10", id="non-numeric"),
    ],
)
def test_total_latency_rejects_invalid_component(component: object) -> None:
    with pytest.raises(LatencyMetricsError):
        total_latency_ms(10.0, component, 20.0)  # type: ignore[arg-type]
