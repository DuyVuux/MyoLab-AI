"""Numerically guarded periodogram-power feature helpers."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class SpectralResult:
    """One-sided periodogram power proxy and its frequency bins."""

    frequencies_hz: np.ndarray
    power: np.ndarray
    qc_flags: tuple[str, ...]


def _validate_frequency_rate(sampling_rate_hz: float) -> float:
    try:
        sampling_rate = float(sampling_rate_hz)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("sampling_rate_hz must be positive and finite") from error
    if not math.isfinite(sampling_rate) or sampling_rate <= 0.0:
        raise ValueError("sampling_rate_hz must be positive and finite")
    return sampling_rate


def periodogram_power_proxy(
    signal: Sequence[float] | np.ndarray,
    sampling_rate_hz: float,
) -> SpectralResult:
    """Return ``abs(rfft(x))**2 / N`` without one-sided bin doubling.

    Power values that cannot be represented in float64 are converted to NaN
    and marked with ``numeric_overflow``. The function never emits infinity.
    """

    values = np.asarray(signal, dtype=np.float64)
    sampling_rate = _validate_frequency_rate(sampling_rate_hz)
    if values.ndim != 1 or values.size == 0:
        raise ValueError("signal must be a non-empty one-dimensional vector")
    if not bool(np.isfinite(values).all()):
        raise ValueError("signal must be finite")

    amplitude_scale = float(np.max(np.abs(values)))
    normalized = values if amplitude_scale == 0.0 else values / amplitude_scale
    spectrum = np.fft.rfft(normalized, n=values.size)
    relative_power = np.square(np.abs(spectrum)) / float(values.size)
    flags: set[str] = set()

    if amplitude_scale == 0.0:
        power = relative_power
    else:
        maximum_relative = float(np.max(relative_power))
        maximum_float = np.finfo(np.float64).max
        if (
            maximum_relative > 0.0
            and amplitude_scale
            > math.sqrt(maximum_float / maximum_relative)
        ):
            power = np.where(relative_power == 0.0, 0.0, math.nan)
            flags.add("numeric_overflow")
        else:
            power = relative_power * amplitude_scale * amplitude_scale

    if power.size < 2:
        flags.add("insufficient_spectral_bins")
    if amplitude_scale == 0.0:
        flags.add("zero_power_window")
    return SpectralResult(
        frequencies_hz=np.fft.rfftfreq(
            values.size,
            d=1.0 / sampling_rate,
        ),
        power=np.asarray(power, dtype=np.float64),
        qc_flags=tuple(sorted(flags)),
    )


def _validated_power_vectors(
    power: Sequence[float] | np.ndarray,
    frequencies_hz: Sequence[float] | np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray(power, dtype=np.float64)
    frequencies = np.asarray(frequencies_hz, dtype=np.float64)
    if (
        values.ndim != 1
        or frequencies.ndim != 1
        or values.size == 0
        or values.size != frequencies.size
    ):
        raise ValueError("power and frequencies must be aligned non-empty vectors")
    if not bool(np.isfinite(values).all()) or bool(np.any(values < 0.0)):
        raise ValueError("power must contain finite non-negative values")
    if not bool(np.isfinite(frequencies).all()):
        raise ValueError("frequencies must be finite")
    if bool(np.any(np.diff(frequencies) < 0.0)):
        raise ValueError("frequencies must be monotonically non-decreasing")
    return values, frequencies


def spectral_features(
    power: Sequence[float] | np.ndarray,
    frequencies_hz: Sequence[float] | np.ndarray,
) -> tuple[dict[str, float], tuple[str, ...]]:
    """Calculate the six locked spectral features from aligned vectors."""

    values, frequencies = _validated_power_vectors(power, frequencies_hz)
    flags: set[str] = set()
    spectral_std = (
        float(np.std(values, ddof=1)) if values.size >= 2 else math.nan
    )
    if values.size < 2:
        flags.add("insufficient_spectral_bins")

    total_power = float(np.sum(values))
    if total_power <= 0.0:
        flags.add("zero_power_window")
        median_frequency = math.nan
        mean_frequency = math.nan
        entropy = math.nan
    else:
        cumulative = np.cumsum(values)
        median_index = int(
            np.searchsorted(cumulative, 0.5 * total_power, side="left")
        )
        median_frequency = float(
            frequencies[min(median_index, frequencies.size - 1)]
        )
        mean_frequency = float(
            np.sum(frequencies * values) / total_power
        )
        positive_probabilities = values[values > 0.0] / total_power
        entropy = float(
            -np.sum(
                positive_probabilities * np.log2(positive_probabilities)
            )
        )

    return (
        {
            "spectral_min_power": float(np.min(values)),
            "spectral_max_power": float(np.max(values)),
            "spectral_std_power_ddof1": spectral_std,
            "mdf_hz": median_frequency,
            "mnf_hz": mean_frequency,
            "spectral_entropy_bits": entropy,
        },
        tuple(sorted(flags)),
    )


def extract_spectral_features(
    signal: Sequence[float] | np.ndarray,
    sampling_rate_hz: float,
) -> tuple[dict[str, float], tuple[str, ...]]:
    """Extract stable spectral features while preserving the locked scaling."""

    values = np.asarray(signal, dtype=np.float64)
    sampling_rate = _validate_frequency_rate(sampling_rate_hz)
    if values.ndim != 1 or values.size == 0:
        raise ValueError("signal must be a non-empty one-dimensional vector")
    if not bool(np.isfinite(values).all()):
        raise ValueError("signal must be finite")

    amplitude_scale = float(np.max(np.abs(values)))
    normalized = values if amplitude_scale == 0.0 else values / amplitude_scale
    relative_spectrum = np.fft.rfft(normalized, n=values.size)
    relative_power = np.square(np.abs(relative_spectrum)) / float(values.size)
    frequencies = np.fft.rfftfreq(
        values.size,
        d=1.0 / sampling_rate,
    )
    result, base_flags = spectral_features(relative_power, frequencies)
    flags = set(base_flags)

    if amplitude_scale == 0.0:
        power_scale = 0.0
    elif amplitude_scale > math.sqrt(np.finfo(np.float64).max):
        power_scale = math.inf
    else:
        power_scale = amplitude_scale * amplitude_scale

    for name in (
        "spectral_min_power",
        "spectral_max_power",
        "spectral_std_power_ddof1",
    ):
        relative_value = result[name]
        if relative_value == 0.0:
            result[name] = 0.0
        elif not math.isfinite(power_scale):
            result[name] = math.nan
            flags.add("numeric_overflow")
        else:
            scaled_value = relative_value * power_scale
            if math.isfinite(scaled_value):
                result[name] = scaled_value
            else:
                result[name] = math.nan
                flags.add("numeric_overflow")
    if amplitude_scale == 0.0:
        flags.add("zero_power_window")
    return result, tuple(sorted(flags))
