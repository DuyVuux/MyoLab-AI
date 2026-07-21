from __future__ import annotations

from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SEMGC = ROOT / "packages" / "semg-core"
if str(SEMGC) not in sys.path:
    sys.path.insert(0, str(SEMGC))

from semg_core.windowing import (  # noqa: E402
    build_fixed_window_geometries,
    full_window_count,
    overlap_to_hop_samples,
    seconds_to_exact_samples,
)


def test_time_domain_reference_geometry_math() -> None:
    fs = 1000.0
    phase_samples = int(fs * 60.0)
    window_samples = seconds_to_exact_samples(0.5, fs)
    hop_samples = overlap_to_hop_samples(window_samples, 0.5)
    assert phase_samples == 60_000
    assert window_samples == 500
    assert hop_samples == 250
    assert full_window_count(phase_samples, window_samples, hop_samples) == 239


def test_frequency_domain_reference_geometry_math() -> None:
    fs = 1000.0
    phase_samples = int(fs * 60.0)
    window_samples = seconds_to_exact_samples(1.0, fs)
    hop_samples = overlap_to_hop_samples(window_samples, 0.5)
    assert phase_samples == 60_000
    assert window_samples == 1000
    assert hop_samples == 500
    assert full_window_count(phase_samples, window_samples, hop_samples) == 119


def test_both_profiles_respect_active_phase_boundaries() -> None:
    fs = 1000.0
    time_s = np.arange(70_000, dtype=np.float64) / fs
    for window_size, hop_size, expected_count in (
        (500, 250, 239),
        (1000, 500, 119),
    ):
        geometries = build_fixed_window_geometries(
            time_s=time_s,
            sampling_rate_hz=fs,
            phase_id="active_contraction",
            phase_start_sample=5000,
            phase_end_sample_exclusive=65000,
            window_size_samples=window_size,
            hop_size_samples=hop_size,
        )
        assert len(geometries) == expected_count
        assert geometries[0].start_sample == 5000
        assert geometries[-1].end_sample_exclusive == 65000
        for left, right in zip(geometries, geometries[1:]):
            assert right.start_sample - left.start_sample == hop_size
            assert right.start_sample < left.end_sample_exclusive
