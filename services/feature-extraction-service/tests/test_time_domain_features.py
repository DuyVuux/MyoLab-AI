from __future__ import annotations

import math

import numpy as np
import pytest

from time_domain import compute_time_domain_window_features


def test_wrapper_preserves_microvolt_unit() -> None:
    result = compute_time_domain_window_features(
        np.array([-3.0, -1.0, 1.0, 3.0], dtype=np.float64)
    )
    assert result.rms == pytest.approx(math.sqrt(5.0))
    assert result.mav == pytest.approx(2.0)
    assert result.amplitude_unit == "uV"


def test_wrapper_does_not_modify_input() -> None:
    samples = np.array([-2.0, 1.0, 4.0], dtype=np.float64)
    before = samples.copy()
    compute_time_domain_window_features(samples)
    assert np.array_equal(samples, before)
