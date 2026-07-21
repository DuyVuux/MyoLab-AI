from __future__ import annotations

import math

import numpy as np
import pytest

from semg_core.features import (
    FeatureExtractionError,
    extract_time_domain_features,
    mean_absolute_value,
    root_mean_square,
)


def test_hand_calculated_vector() -> None:
    values = np.array([-3.0, -1.0, 1.0, 3.0])
    assert root_mean_square(values) == pytest.approx(math.sqrt(5.0), abs=1e-12)
    assert mean_absolute_value(values) == pytest.approx(2.0, abs=1e-12)


def test_constant_magnitude_has_equal_rms_and_mav() -> None:
    values = np.array([-5.0, 5.0, -5.0, 5.0])
    assert root_mean_square(values) == pytest.approx(5.0)
    assert mean_absolute_value(values) == pytest.approx(5.0)


def test_zero_signal_returns_zero() -> None:
    result = extract_time_domain_features(np.zeros(500))
    assert result.rms == 0.0
    assert result.mav == 0.0
    assert result.sample_count == 500
    assert result.amplitude_unit == "uV"


def test_sign_inversion_does_not_change_features() -> None:
    values = np.array([-2.0, -1.0, 0.5, 4.0])
    assert root_mean_square(values) == pytest.approx(root_mean_square(-values))
    assert mean_absolute_value(values) == pytest.approx(mean_absolute_value(-values))


def test_scaling_property_uses_absolute_scale() -> None:
    values = np.array([-3.0, -1.0, 1.0, 3.0])
    scale = -2.5
    assert root_mean_square(scale * values) == pytest.approx(
        abs(scale) * root_mean_square(values)
    )
    assert mean_absolute_value(scale * values) == pytest.approx(
        abs(scale) * mean_absolute_value(values)
    )


def test_rms_is_not_less_than_mav() -> None:
    rng = np.random.default_rng(42)
    for _ in range(20):
        values = rng.normal(size=1000)
        assert root_mean_square(values) + 1e-12 >= mean_absolute_value(values)


def test_sine_wave_matches_known_rms_and_mav() -> None:
    fs = 1000.0
    amplitude = 100.0
    frequency_hz = 80.0
    t = np.arange(int(fs)) / fs
    values = amplitude * np.sin(2.0 * np.pi * frequency_hz * t)
    assert root_mean_square(values) == pytest.approx(
        amplitude / math.sqrt(2), rel=1e-12
    )
    assert mean_absolute_value(values) == pytest.approx(
        2.0 * amplitude / math.pi, rel=2e-3
    )


def test_large_values_do_not_overflow() -> None:
    values = np.array([1e300, -1e300, 1e300, -1e300])
    assert math.isfinite(root_mean_square(values))
    assert math.isfinite(mean_absolute_value(values))
    assert root_mean_square(values) == pytest.approx(1e300)
    assert mean_absolute_value(values) == pytest.approx(1e300)


@pytest.mark.parametrize(
    "values",
    [
        np.array([]),
        np.array([1.0, np.nan]),
        np.array([1.0, np.inf]),
        np.ones((2, 2)),
    ],
)
def test_invalid_input_is_rejected(values: np.ndarray) -> None:
    with pytest.raises(FeatureExtractionError):
        extract_time_domain_features(values)
