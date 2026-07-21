from __future__ import annotations

import numpy as np
import pytest

from semg_core.spectral import (
    SpectralEstimationError,
    estimate_periodogram_psd,
    estimate_welch_psd,
    integrate_uniform_psd,
    one_sided_frequency_axis,
    rayleigh_resolution_hz,
    select_frequency_band,
)


def _tone(
    frequency_hz: float,
    *,
    amplitude: float = 100.0,
    fs: int = 1000,
    n: int = 1000,
    phase: float = 0.0,
) -> np.ndarray:
    t = np.arange(n, dtype=np.float64) / fs
    return amplitude * np.sin(2.0 * np.pi * frequency_hz * t + phase)


def _estimate(samples: np.ndarray):
    return estimate_welch_psd(
        samples,
        sampling_rate_hz=1000.0,
        taper="hann",
        detrend="constant",
        scaling="density",
        nperseg_samples=1000,
        noverlap_samples=0,
        nfft_samples=1000,
        average="mean",
    )


def test_one_sided_frequency_axis_even_nfft() -> None:
    axis = one_sided_frequency_axis(sampling_rate_hz=1000.0, nfft_samples=1000)
    assert axis.shape == (501,)
    assert axis[0] == pytest.approx(0.0)
    assert axis[-1] == pytest.approx(500.0)
    assert axis[1] - axis[0] == pytest.approx(1.0)
    assert axis.flags.writeable is False


def test_rayleigh_resolution_uses_segment_length_not_nfft() -> None:
    assert rayleigh_resolution_hz(
        sampling_rate_hz=1000.0,
        nperseg_samples=500,
    ) == pytest.approx(2.0)


def test_welch_tone_peak_and_units() -> None:
    estimate = _estimate(_tone(80.0))
    peak_index = int(np.argmax(estimate.psd_uV2_per_hz))
    assert estimate.frequencies_hz[peak_index] == pytest.approx(80.0, abs=1.0)
    assert estimate.frequencies_hz.shape == (501,)
    assert estimate.frequency_bin_spacing_hz == pytest.approx(1.0)
    assert estimate.rayleigh_resolution_hz == pytest.approx(1.0)
    assert estimate.nperseg_samples == 1000
    assert estimate.noverlap_samples == 0
    assert estimate.frequencies_hz.flags.writeable is False
    assert estimate.psd_uV2_per_hz.flags.writeable is False


def test_parseval_like_integrated_psd_matches_variance() -> None:
    x = _tone(80.0, amplitude=100.0) + _tone(140.0, amplitude=35.0)
    estimate = _estimate(x)
    assert estimate.parseval_ratio == pytest.approx(1.0, rel=0.03)
    assert estimate.full_power_uV2 == pytest.approx(
        estimate.time_domain_variance_uV2,
        rel=0.03,
    )


def test_scaling_signal_by_two_scales_power_by_four() -> None:
    x = _tone(80.0, amplitude=40.0) + _tone(125.0, amplitude=20.0)
    p1 = _estimate(x).full_power_uV2
    p2 = _estimate(2.0 * x).full_power_uV2
    assert p2 / p1 == pytest.approx(4.0, rel=1e-12)


def test_periodogram_returns_nonnegative_density() -> None:
    estimate = estimate_periodogram_psd(
        _tone(80.5),
        sampling_rate_hz=1000.0,
        taper="hann",
        detrend="constant",
        nfft_samples=1000,
    )
    assert np.all(estimate.psd_uV2_per_hz >= 0)
    assert integrate_uniform_psd(
        estimate.frequencies_hz,
        estimate.psd_uV2_per_hz,
    ) > 0


def test_select_frequency_band_is_inclusive() -> None:
    estimate = _estimate(_tone(80.0))
    frequencies, psd = select_frequency_band(
        estimate.frequencies_hz,
        estimate.psd_uV2_per_hz,
        low_hz=20.0,
        high_hz=400.0,
        include_endpoints=True,
    )
    assert frequencies[0] == pytest.approx(20.0)
    assert frequencies[-1] == pytest.approx(400.0)
    assert frequencies.size == 381
    assert psd.size == frequencies.size
    assert frequencies.flags.writeable is False
    assert psd.flags.writeable is False


@pytest.mark.parametrize(
    "samples",
    [np.array([]), np.array([1.0]), np.array([1.0, 2.0, 3.0]), np.array([1.0, np.nan, 2.0, 3.0])],
)
def test_invalid_vectors_are_rejected(samples: np.ndarray) -> None:
    with pytest.raises(SpectralEstimationError):
        _estimate(samples)


def test_invalid_welch_geometry_is_rejected() -> None:
    x = _tone(80.0)
    with pytest.raises(SpectralEstimationError):
        estimate_welch_psd(
            x,
            sampling_rate_hz=1000.0,
            nperseg_samples=1001,
            noverlap_samples=0,
            nfft_samples=1001,
        )
    with pytest.raises(SpectralEstimationError):
        estimate_welch_psd(
            x,
            sampling_rate_hz=1000.0,
            nperseg_samples=1000,
            noverlap_samples=1000,
            nfft_samples=1000,
        )


def test_analysis_band_must_fit_frequency_axis() -> None:
    estimate = _estimate(_tone(80.0))
    with pytest.raises(SpectralEstimationError):
        select_frequency_band(
            estimate.frequencies_hz,
            estimate.psd_uV2_per_hz,
            low_hz=20.0,
            high_hz=600.0,
        )


def test_repeat_is_deterministic() -> None:
    first = _estimate(_tone(80.0, phase=0.3))
    second = _estimate(_tone(80.0, phase=0.3))
    np.testing.assert_array_equal(first.frequencies_hz, second.frequencies_hz)
    np.testing.assert_array_equal(first.psd_uV2_per_hz, second.psd_uV2_per_hz)
