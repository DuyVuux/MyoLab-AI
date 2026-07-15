from __future__ import annotations

import numpy as np
import pytest

from normalizers.unit_normalizer import normalize_to_uV


def test_uv_is_identity() -> None:
    source = np.array([1.0, -2.5, np.nan])
    result = normalize_to_uV(source, "uV")
    np.testing.assert_allclose(result[:2], source[:2])
    assert np.isnan(result[2])


def test_mv_to_uv() -> None:
    source = np.array([0.001, -0.25, 1.5])
    result = normalize_to_uV(source, "mV")
    np.testing.assert_allclose(result, np.array([1.0, -250.0, 1500.0]))


def test_v_to_uv() -> None:
    source = np.array([1e-6, -2e-6])
    result = normalize_to_uV(source, "V")
    np.testing.assert_allclose(result, np.array([1.0, -2.0]))


def test_unknown_unit_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported signal unit"):
        normalize_to_uV(np.array([1.0]), "arbitrary")
