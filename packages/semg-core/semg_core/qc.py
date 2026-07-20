"""Dependency-light signal-quality helpers for MVP-0.

The functions in this module are deterministic engineering utilities.  They do
not define clinical thresholds and they do not infer muscle fatigue.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np


@dataclass(frozen=True, slots=True)
class FlatlineStats:
    """Summary of near-constant segments in one one-dimensional signal."""

    total_fraction: float
    longest_run_samples: int
    longest_run_duration_s: float
    tolerance_uV: float
    qualifying_run_count: int


@dataclass(frozen=True, slots=True)
class SpectralRatio:
    """A named numerator/denominator spectral-power ratio."""

    ratio: float
    numerator_power: float
    denominator_power: float
    numerator_band_hz: tuple[float, float]
    denominator_band_hz: tuple[float, float]


def _as_1d_float(samples: Iterable[float] | np.ndarray) -> np.ndarray:
    values = np.asarray(samples, dtype=np.float64)
    if values.ndim != 1:
        raise ValueError("samples must be a one-dimensional array")
    return values


def nonfinite_ratio(samples: Iterable[float] | np.ndarray) -> float:
    """Return non-finite samples divided by all samples."""

    values = _as_1d_float(samples)
    if values.size == 0:
        return 1.0
    return float(1.0 - np.isfinite(values).sum() / values.size)


def robust_amplitude_scale_uV(samples: Iterable[float] | np.ndarray) -> float:
    """Estimate a robust signal scale in microvolts.

    The median absolute deviation is multiplied by 1.4826 so that, for a normal
    distribution, it estimates the standard deviation.  A percentile fallback
    is used when MAD is zero.  This scale is used only to make a *relative*
    flatline tolerance; it is not an amplitude-validity threshold.
    """

    values = _as_1d_float(samples)
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return 0.0
    median = float(np.median(finite))
    mad = float(np.median(np.abs(finite - median)))
    scale = 1.4826 * mad
    if scale <= 0.0 or not math.isfinite(scale):
        q05, q95 = np.percentile(finite, [5.0, 95.0])
        scale = float((q95 - q05) / 3.2897072539)  # approx 90% normal span
    if scale <= 0.0 or not math.isfinite(scale):
        scale = float(np.max(np.abs(finite - median)))
    return max(0.0, scale)


def compute_flatline_stats(
    samples: Iterable[float] | np.ndarray,
    *,
    sampling_rate_hz: float,
    minimum_contiguous_duration_ms: float,
    relative_tolerance: float = 1e-6,
    absolute_floor_uV: float = 1e-9,
) -> FlatlineStats:
    """Detect near-constant runs using adjacent differences.

    A run qualifies only when its duration meets
    ``minimum_contiguous_duration_ms``. Non-finite values break a run. The
    returned total fraction counts samples that belong to qualifying runs.
    """

    values = _as_1d_float(samples)
    fs = float(sampling_rate_hz)
    if not math.isfinite(fs) or fs <= 0:
        raise ValueError("sampling_rate_hz must be positive and finite")
    if minimum_contiguous_duration_ms <= 0:
        raise ValueError("minimum_contiguous_duration_ms must be positive")
    if relative_tolerance < 0 or absolute_floor_uV < 0:
        raise ValueError("flatline tolerances must be non-negative")
    if values.size == 0:
        return FlatlineStats(1.0, 0, 0.0, absolute_floor_uV, 0)

    scale = robust_amplitude_scale_uV(values)
    tolerance = max(float(absolute_floor_uV), float(relative_tolerance) * scale)
    minimum_samples = max(2, int(math.ceil(minimum_contiguous_duration_ms * fs / 1000.0)))

    finite = np.isfinite(values)
    if values.size == 1:
        return FlatlineStats(0.0, 1, 1.0 / fs, tolerance, 0)

    equal_adjacent = (
        finite[:-1]
        & finite[1:]
        & (np.abs(np.diff(values)) <= tolerance)
    )

    total_qualifying_samples = 0
    longest_run_samples = 1
    qualifying_run_count = 0
    index = 0
    while index < equal_adjacent.size:
        if not equal_adjacent[index]:
            index += 1
            continue
        start = index
        while index < equal_adjacent.size and equal_adjacent[index]:
            index += 1
        # k equal adjacent differences represent k + 1 constant samples.
        run_samples = (index - start) + 1
        longest_run_samples = max(longest_run_samples, run_samples)
        if run_samples >= minimum_samples:
            total_qualifying_samples += run_samples
            qualifying_run_count += 1

    total_fraction = min(1.0, total_qualifying_samples / values.size)
    return FlatlineStats(
        total_fraction=float(total_fraction),
        longest_run_samples=int(longest_run_samples),
        longest_run_duration_s=float(longest_run_samples / fs),
        tolerance_uV=float(tolerance),
        qualifying_run_count=int(qualifying_run_count),
    )


def repeated_extrema_fraction(
    samples: Iterable[float] | np.ndarray,
    *,
    relative_tolerance: float = 1e-9,
    absolute_floor_uV: float = 1e-9,
) -> float:
    """Return the fraction of finite samples repeated at global extrema.

    This is a vendor-neutral clipping heuristic. It cannot prove that an ADC
    rail was reached because the hardware range is unknown.
    """

    values = _as_1d_float(samples)
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return 1.0
    minimum = float(np.min(finite))
    maximum = float(np.max(finite))
    scale = max(abs(minimum), abs(maximum), robust_amplitude_scale_uV(finite), 1.0)
    tolerance = max(float(absolute_floor_uV), float(relative_tolerance) * scale)
    at_min = np.isclose(finite, minimum, rtol=0.0, atol=tolerance)
    at_max = np.isclose(finite, maximum, rtol=0.0, atol=tolerance)
    return float(np.count_nonzero(at_min | at_max) / finite.size)


def fill_nonfinite_linear(samples: Iterable[float] | np.ndarray) -> np.ndarray:
    """Return a finite copy using linear interpolation for internal QC spectra."""

    values = _as_1d_float(samples).copy()
    if values.size == 0:
        return values
    finite = np.isfinite(values)
    if not np.any(finite):
        raise ValueError("cannot interpolate a signal with no finite samples")
    if np.all(finite):
        return values
    indexes = np.arange(values.size, dtype=np.float64)
    values[~finite] = np.interp(indexes[~finite], indexes[finite], values[finite])
    return values


def one_sided_periodogram(
    samples: Iterable[float] | np.ndarray,
    *,
    sampling_rate_hz: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute a deterministic Hann-windowed one-sided periodogram.

    The scaling is chosen so that power ratios are meaningful within this
    module. This is a QC-only spectrum, not the future feature-extraction PSD
    contract.
    """

    values = fill_nonfinite_linear(samples)
    fs = float(sampling_rate_hz)
    if not math.isfinite(fs) or fs <= 0:
        raise ValueError("sampling_rate_hz must be positive and finite")
    if values.size < 4:
        raise ValueError("at least four samples are required for a spectrum")

    centered = values - float(np.mean(values))
    window = np.hanning(values.size)
    window_energy = float(np.sum(window * window))
    if window_energy <= 0:
        raise ValueError("invalid spectral window energy")
    spectrum = np.fft.rfft(centered * window)
    power = (np.abs(spectrum) ** 2) / (fs * window_energy)
    if power.size > 2:
        power[1:-1] *= 2.0
    frequencies = np.fft.rfftfreq(values.size, d=1.0 / fs)
    return frequencies.astype(np.float64), power.astype(np.float64)


def band_power(
    frequencies_hz: Iterable[float] | np.ndarray,
    power: Iterable[float] | np.ndarray,
    *,
    low_hz: float,
    high_hz: float,
) -> float:
    """Integrate power in the half-open frequency band [low_hz, high_hz]."""

    frequencies = _as_1d_float(frequencies_hz)
    values = _as_1d_float(power)
    if frequencies.size != values.size:
        raise ValueError("frequency and power arrays must have equal length")
    low = float(low_hz)
    high = float(high_hz)
    if not (math.isfinite(low) and math.isfinite(high) and 0 <= low < high):
        raise ValueError("frequency band must satisfy 0 <= low_hz < high_hz")
    mask = (frequencies >= low) & (frequencies < high)
    if not np.any(mask):
        return 0.0
    selected_f = frequencies[mask]
    selected_p = values[mask]
    if selected_f.size == 1:
        return float(selected_p[0])
    return float(np.trapezoid(selected_p, selected_f))


def powerline_contamination_ratio(
    samples: Iterable[float] | np.ndarray,
    *,
    sampling_rate_hz: float,
    line_frequency_hz: float,
    integration_half_width_hz: float,
    analysis_band_hz: tuple[float, float],
) -> SpectralRatio:
    """Power near the line frequency divided by analysis-band power."""

    fs = float(sampling_rate_hz)
    nyquist = fs / 2.0
    analysis_low, analysis_high = map(float, analysis_band_hz)
    analysis_high = min(analysis_high, np.nextafter(nyquist, 0.0))
    line_low = max(0.0, float(line_frequency_hz) - float(integration_half_width_hz))
    line_high = min(nyquist, float(line_frequency_hz) + float(integration_half_width_hz))

    frequencies, power = one_sided_periodogram(samples, sampling_rate_hz=fs)
    numerator = band_power(frequencies, power, low_hz=line_low, high_hz=line_high)
    denominator = band_power(
        frequencies,
        power,
        low_hz=analysis_low,
        high_hz=analysis_high,
    )
    ratio = float(numerator / denominator) if denominator > 0 else float("inf")
    return SpectralRatio(
        ratio=ratio,
        numerator_power=numerator,
        denominator_power=denominator,
        numerator_band_hz=(line_low, line_high),
        denominator_band_hz=(analysis_low, analysis_high),
    )


def low_frequency_motion_ratio(
    samples: Iterable[float] | np.ndarray,
    *,
    sampling_rate_hz: float,
    low_band_hz: tuple[float, float],
    analysis_band_hz: tuple[float, float],
) -> SpectralRatio:
    """Low-frequency power divided by conventional sEMG-band power."""

    fs = float(sampling_rate_hz)
    nyquist = fs / 2.0
    low_low, low_high = map(float, low_band_hz)
    analysis_low, analysis_high = map(float, analysis_band_hz)
    low_high = min(low_high, np.nextafter(nyquist, 0.0))
    analysis_high = min(analysis_high, np.nextafter(nyquist, 0.0))

    frequencies, power = one_sided_periodogram(samples, sampling_rate_hz=fs)
    numerator = band_power(frequencies, power, low_hz=low_low, high_hz=low_high)
    denominator = band_power(
        frequencies,
        power,
        low_hz=analysis_low,
        high_hz=analysis_high,
    )
    ratio = float(numerator / denominator) if denominator > 0 else float("inf")
    return SpectralRatio(
        ratio=ratio,
        numerator_power=numerator,
        denominator_power=denominator,
        numerator_band_hz=(low_low, low_high),
        denominator_band_hz=(analysis_low, analysis_high),
    )


def pearson_correlation(left: np.ndarray, right: np.ndarray) -> float:
    """Compute finite-pair Pearson correlation for future MFCV eligibility."""

    x = _as_1d_float(left)
    y = _as_1d_float(right)
    if x.size != y.size:
        raise ValueError("signals must have equal length")
    mask = np.isfinite(x) & np.isfinite(y)
    if np.count_nonzero(mask) < 3:
        return float("nan")
    x_f = x[mask]
    y_f = y[mask]
    if float(np.std(x_f)) == 0.0 or float(np.std(y_f)) == 0.0:
        return float("nan")
    return float(np.corrcoef(x_f, y_f)[0, 1])
