from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from frequency_domain import SpectralPowerTooLow, compute_spectral_window
from spectral_config import load_spectral_config


ROOT = Path(__file__).resolve().parents[3]
CONFIG = ROOT / "services/feature-extraction-service/configs/spectral_estimation_v0.1.yaml"


def test_compute_known_80_hz_window() -> None:
    config = load_spectral_config(CONFIG)
    fs = 1000.0
    t = np.arange(1000, dtype=np.float64) / fs
    signal = 10.0 * np.sin(2.0 * np.pi * 80.0 * t)
    axis, values, metadata = compute_spectral_window(
        signal,
        sampling_rate_hz=fs,
        config=config,
    )
    assert axis.size == 381
    assert axis[0] == pytest.approx(20.0)
    assert axis[-1] == pytest.approx(400.0)
    assert values.peak_frequency_hz == pytest.approx(80.0)
    assert values.band_power_uV2 == pytest.approx(50.0, rel=1e-10)
    assert values.parseval_ratio == pytest.approx(1.0, rel=1e-10)
    assert metadata["frequency_bin_spacing_hz"] == pytest.approx(1.0)
    assert metadata["rayleigh_resolution_hz"] == pytest.approx(1.0)
    assert metadata["frequency_bin_count"] == 381


def test_zero_power_is_not_computable() -> None:
    config = load_spectral_config(CONFIG)
    with pytest.raises(SpectralPowerTooLow):
        compute_spectral_window(
            np.zeros(1000),
            sampling_rate_hz=1000.0,
            config=config,
        )
