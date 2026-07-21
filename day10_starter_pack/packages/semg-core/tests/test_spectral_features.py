from __future__ import annotations

import numpy as np
import pytest

from semg_core.spectral_features import (
    FrequencyFeatureError,
    extract_frequency_features,
    mean_frequency_hz,
    median_frequency_hz,
)


def test_uniform_psd_has_midpoint_mdf_and_mnf() -> None:
    frequencies = np.arange(20.0, 401.0, 1.0)
    psd = np.ones_like(frequencies)
    values = extract_frequency_features(frequencies, psd)
    assert values.mdf_hz == pytest.approx(210.0, abs=1e-12)
    assert values.mnf_hz == pytest.approx(210.0, abs=1e-12)


def test_single_bin_mass_returns_bin_center() -> None:
    frequencies = np.arange(20.0, 401.0, 1.0)
    psd = np.zeros_like(frequencies)
    psd[np.where(frequencies == 80.0)[0][0]] = 10.0
    assert median_frequency_hz(frequencies, psd) == pytest.approx(80.0)
    assert mean_frequency_hz(frequencies, psd) == pytest.approx(80.0)


def test_weighted_centroid_known_answer() -> None:
    frequencies = np.array([50.0, 100.0, 150.0])
    psd = np.array([1.0, 2.0, 1.0])
    assert mean_frequency_hz(frequencies, psd) == pytest.approx(100.0)


def test_scale_invariance_of_mdf_mnf() -> None:
    frequencies = np.arange(20.0, 401.0, 1.0)
    psd = np.exp(-0.5 * ((frequencies - 95.0) / 20.0) ** 2)
    base = extract_frequency_features(frequencies, psd)
    scaled = extract_frequency_features(frequencies, psd * 7.5)
    assert scaled.mdf_hz == pytest.approx(base.mdf_hz, abs=1e-12)
    assert scaled.mnf_hz == pytest.approx(base.mnf_hz, abs=1e-12)
    assert scaled.band_power_uV2 == pytest.approx(base.band_power_uV2 * 7.5)


def test_nonuniform_axis_rejected() -> None:
    with pytest.raises(FrequencyFeatureError):
        extract_frequency_features([20.0, 21.0, 23.0], [1.0, 1.0, 1.0])


def test_zero_power_rejected() -> None:
    frequencies = np.arange(20.0, 401.0, 1.0)
    with pytest.raises(FrequencyFeatureError):
        extract_frequency_features(frequencies, np.zeros_like(frequencies))


def test_negative_psd_rejected() -> None:
    with pytest.raises(FrequencyFeatureError):
        extract_frequency_features([20.0, 21.0], [1.0, -0.1])
