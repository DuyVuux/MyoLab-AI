from __future__ import annotations

import math

import numpy as np
import pytest

from semg_core.features import extract_time_domain_features


def test_closed_form_sine_properties() -> None:
    fs = 10000.0
    amplitude = 120.0
    frequency_hz = 10.0
    t = np.arange(int(fs), dtype=np.float64) / fs
    values = amplitude * np.sin(2.0 * np.pi * frequency_hz * t)
    result = extract_time_domain_features(values)
    assert result.rms == pytest.approx(amplitude / math.sqrt(2.0), rel=1e-12)
    assert result.mav == pytest.approx(2.0 * amplitude / math.pi, rel=1e-5)


def test_unit_scaling_from_millivolt_numbers_to_microvolt_numbers() -> None:
    samples_mV = np.array([-0.1, 0.1, -0.2, 0.2])
    samples_uV = samples_mV * 1000.0
    mv = extract_time_domain_features(samples_mV, amplitude_unit="mV")
    uv = extract_time_domain_features(samples_uV, amplitude_unit="uV")
    assert uv.rms == pytest.approx(mv.rms * 1000.0)
    assert uv.mav == pytest.approx(mv.mav * 1000.0)
