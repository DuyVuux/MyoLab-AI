from __future__ import annotations

from fractions import Fraction
from math import floor, isfinite

import numpy as np


SAMPLE_ROUNDING_POLICY = "round_half_up"


def samples_for_ms(sampling_rate_hz: float, duration_ms: float) -> int:
    if (
        not isfinite(float(sampling_rate_hz))
        or not isfinite(float(duration_ms))
        or sampling_rate_hz <= 0
        or duration_ms <= 0
    ):
        raise ValueError("sampling_rate_hz and duration_ms must be finite and positive")
    return int(floor(float(sampling_rate_hz) * float(duration_ms) / 1000.0 + 0.5))


def rational_resample_factors(source_hz: int, target_hz: int) -> tuple[int, int]:
    if (
        isinstance(source_hz, bool)
        or isinstance(target_hz, bool)
        or not isinstance(source_hz, int)
        or not isinstance(target_hz, int)
        or source_hz <= 0
        or target_hz <= 0
    ):
        raise ValueError("sampling rates must be positive integers")
    fraction = Fraction(target_hz, source_hz)
    return fraction.numerator, fraction.denominator


def resample_polyphase(
    signal: np.ndarray,
    source_hz: int,
    target_hz: int,
    axis: int = 0,
) -> np.ndarray:
    source = np.asarray(signal)
    if source.ndim == 0 or source.size == 0:
        raise ValueError("signal must be a non-empty array")
    if not np.issubdtype(source.dtype, np.number) or not np.isfinite(source).all():
        raise ValueError("signal must contain only finite numeric values")
    if not -source.ndim <= axis < source.ndim:
        raise ValueError("axis is out of bounds")
    if source_hz == target_hz:
        return source.copy()
    from scipy.signal import resample_poly

    up, down = rational_resample_factors(source_hz, target_hz)
    result = resample_poly(source, up=up, down=down, axis=axis)
    if not np.isfinite(result).all():
        raise ValueError("resampling produced non-finite values")
    return result

