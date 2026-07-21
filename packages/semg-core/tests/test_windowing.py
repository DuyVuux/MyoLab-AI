from __future__ import annotations

import numpy as np
import pytest

from semg_core.windowing import (
    WindowingError,
    assess_window_validity,
    build_fixed_window_geometries,
    full_window_count,
    overlap_to_hop_samples,
    seconds_to_exact_samples,
    window_view,
)


def test_seconds_to_samples_and_hop_for_both_profiles() -> None:
    time_window = seconds_to_exact_samples(0.5, 1000.0)
    time_hop = overlap_to_hop_samples(time_window, 0.5)
    frequency_window = seconds_to_exact_samples(1.0, 1000.0)
    frequency_hop = overlap_to_hop_samples(frequency_window, 0.5)
    assert (time_window, time_hop) == (500, 250)
    assert (frequency_window, frequency_hop) == (1000, 500)


def test_60_second_phase_produces_expected_profile_counts() -> None:
    assert full_window_count(60_000, 500, 250) == 239
    assert full_window_count(60_000, 1000, 500) == 119


def test_geometry_uses_half_open_boundaries() -> None:
    fs = 1000.0
    time_s = np.arange(70_000, dtype=np.float64) / fs
    geometries = build_fixed_window_geometries(
        time_s=time_s,
        sampling_rate_hz=fs,
        phase_id="active_contraction",
        phase_start_sample=5_000,
        phase_end_sample_exclusive=65_000,
        window_size_samples=1000,
        hop_size_samples=500,
    )
    assert len(geometries) == 119
    first = geometries[0]
    last = geometries[-1]
    assert (first.start_sample, first.end_sample_exclusive) == (5000, 6000)
    assert first.start_time_s == pytest.approx(5.0)
    assert first.end_time_exclusive_s == pytest.approx(6.0)
    assert first.center_time_s == pytest.approx(5.5)
    assert (last.start_sample, last.end_sample_exclusive) == (64_000, 65_000)
    assert last.end_time_exclusive_s == pytest.approx(65.0)


def test_partial_final_window_is_not_created() -> None:
    assert full_window_count(1500, 1000, 700) == 1


def test_invalid_overlap_is_rejected() -> None:
    with pytest.raises(WindowingError):
        overlap_to_hop_samples(1000, 1.0)


def test_non_integer_sample_duration_is_rejected() -> None:
    with pytest.raises(WindowingError):
        seconds_to_exact_samples(0.3335, 1000.0)


def test_masked_sample_invalidates_overlapping_windows() -> None:
    fs = 1000.0
    time_s = np.arange(3000, dtype=np.float64) / fs
    geometries = build_fixed_window_geometries(
        time_s=time_s,
        sampling_rate_hz=fs,
        phase_id="active",
        phase_start_sample=0,
        phase_end_sample_exclusive=3000,
        window_size_samples=1000,
        hop_size_samples=500,
    )
    samples = np.ones(3000, dtype=np.float64)
    mask = np.ones(3000, dtype=np.bool_)
    mask[750] = False
    validity = assess_window_validity(
        samples=samples,
        valid_sample_mask=mask,
        geometries=geometries,
        minimum_valid_sample_ratio=1.0,
    )
    invalid_indices = [
        item.window_index for item in validity if item.status == "invalid"
    ]
    assert invalid_indices == [0, 1]
    assert "WINDOW_INTERSECTS_INVALID_SAMPLE_MASK" in validity[0].reason_codes


def test_window_view_is_read_only_and_correct_length() -> None:
    fs = 1000.0
    time_s = np.arange(2000, dtype=np.float64) / fs
    geometry = build_fixed_window_geometries(
        time_s=time_s,
        sampling_rate_hz=fs,
        phase_id="active",
        phase_start_sample=0,
        phase_end_sample_exclusive=2000,
        window_size_samples=1000,
        hop_size_samples=500,
    )[1]
    samples = np.arange(2000, dtype=np.float64)
    view = window_view(samples, geometry)
    assert view.size == 1000
    assert view[0] == 500
    assert view.flags.writeable is False
