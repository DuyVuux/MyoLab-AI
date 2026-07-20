from __future__ import annotations

import numpy as np
import pytest

from semg_core.qc import (
    compute_flatline_stats,
    low_frequency_motion_ratio,
    nonfinite_ratio,
    powerline_contamination_ratio,
    repeated_extrema_fraction,
)


def test_nonfinite_ratio() -> None:
    values = np.array([1.0, np.nan, 2.0, np.inf])
    assert nonfinite_ratio(values) == pytest.approx(0.5)


def test_flatline_stats_detect_long_constant_run() -> None:
    fs = 1000.0
    values = np.sin(2 * np.pi * 80 * np.arange(2000) / fs)
    values[500:1000] = 7.0
    stats = compute_flatline_stats(
        values,
        sampling_rate_hz=fs,
        minimum_contiguous_duration_ms=250,
    )
    assert stats.longest_run_samples >= 500
    assert stats.total_fraction >= 0.25


def test_repeated_extrema_fraction_is_small_for_continuous_signal() -> None:
    rng = np.random.default_rng(42)
    values = rng.normal(size=10000)
    assert repeated_extrema_fraction(values) < 0.001


def test_repeated_extrema_fraction_detects_pinned_values() -> None:
    rng = np.random.default_rng(42)
    values = rng.normal(size=10000)
    values[:100] = 10.0
    values[100:200] = -10.0
    assert repeated_extrema_fraction(values) >= 0.02


def test_powerline_ratio_increases_with_50hz_component() -> None:
    fs = 1000.0
    t = np.arange(10000) / fs
    base = 20.0 * np.sin(2 * np.pi * 100.0 * t)
    contaminated = base + 100.0 * np.sin(2 * np.pi * 50.0 * t)
    base_ratio = powerline_contamination_ratio(
        base,
        sampling_rate_hz=fs,
        line_frequency_hz=50.0,
        integration_half_width_hz=1.0,
        analysis_band_hz=(20.0, 400.0),
    ).ratio
    contaminated_ratio = powerline_contamination_ratio(
        contaminated,
        sampling_rate_hz=fs,
        line_frequency_hz=50.0,
        integration_half_width_hz=1.0,
        analysis_band_hz=(20.0, 400.0),
    ).ratio
    assert contaminated_ratio > base_ratio
    assert contaminated_ratio > 0.5


def test_motion_ratio_increases_with_5hz_component() -> None:
    fs = 1000.0
    t = np.arange(10000) / fs
    base = 20.0 * np.sin(2 * np.pi * 100.0 * t)
    contaminated = base + 100.0 * np.sin(2 * np.pi * 5.0 * t)
    ratio = low_frequency_motion_ratio(
        contaminated,
        sampling_rate_hz=fs,
        low_band_hz=(0.5, 20.0),
        analysis_band_hz=(20.0, 400.0),
    ).ratio
    assert ratio > 1.0
