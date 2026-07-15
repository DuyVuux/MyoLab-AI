"""Explicit amplitude-unit conversion to the canonical unit microvolt (uV)."""

from __future__ import annotations

import numpy as np


_SCALE_TO_UV: dict[str, float] = {
    "uV": 1.0,
    "mV": 1_000.0,
    "V": 1_000_000.0,
}


def supported_units() -> frozenset[str]:
    return frozenset(_SCALE_TO_UV)


def normalize_to_uV(samples: np.ndarray, source_unit: str) -> np.ndarray:
    """Convert V/mV/uV samples to float64 microvolts.

    NaN/Inf values are preserved for the downstream quality gate. The function
    never guesses a unit from amplitude.
    """

    if source_unit not in _SCALE_TO_UV:
        raise ValueError(f"Unsupported signal unit: {source_unit!r}")
    values = np.asarray(samples, dtype=np.float64)
    if values.ndim != 1:
        raise ValueError("Signal samples must be one-dimensional")
    return np.ascontiguousarray(values * _SCALE_TO_UV[source_unit], dtype=np.float64)
