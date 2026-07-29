from __future__ import annotations

from dataclasses import dataclass, asdict
import math
from typing import Iterable

import numpy as np


@dataclass
class ChannelStatistics:
    sample_count: int
    finite_count: int
    nonfinite_ratio: float
    mean_uV: float | None
    median_uV: float | None
    std_uV: float | None
    mad_uV: float | None
    rms_uV: float | None
    mav_uV: float | None
    p01_uV: float | None
    p99_uV: float | None
    robust_range_uV: float | None
    flatline_ratio: float | None
    clipping_candidate_ratio: float | None
    dc_to_std_ratio: float | None
    low_frequency_0_20_ratio: float | None
    powerline_50hz_ratio: float | None
    powerline_60hz_ratio: float | None


def _safe_float(value: float) -> float | None:
    return None if not math.isfinite(float(value)) else float(value)


def _band_ratio(x: np.ndarray, fs: float, low: float, high: float) -> float | None:
    if x.size < 8 or fs <= 0:
        return None
    centered = x - np.mean(x)
    spectrum = np.fft.rfft(centered)
    power = np.abs(spectrum) ** 2
    freqs = np.fft.rfftfreq(centered.size, d=1.0 / fs)
    non_dc = freqs > 0
    total = float(np.sum(power[non_dc]))
    if total <= 0:
        return None
    mask = (freqs >= low) & (freqs <= high)
    return float(np.sum(power[mask]) / total)


def compute_channel_statistics(values: Iterable[float], sampling_rate_hz: float | None) -> ChannelStatistics:
    raw = np.asarray(list(values), dtype=float)
    n = int(raw.size)
    finite_mask = np.isfinite(raw)
    finite = raw[finite_mask]
    finite_n = int(finite.size)
    nonfinite_ratio = 1.0 if n == 0 else float(1.0 - finite_n / n)
    if finite_n == 0:
        return ChannelStatistics(n, 0, nonfinite_ratio, *([None] * 15))

    mean = float(np.mean(finite))
    median = float(np.median(finite))
    std = float(np.std(finite, ddof=1)) if finite_n > 1 else 0.0
    mad = float(np.median(np.abs(finite - median)))
    rms = float(np.sqrt(np.mean(np.square(finite))))
    mav = float(np.mean(np.abs(finite)))
    p01, p99 = np.percentile(finite, [1, 99])
    robust_range = float(p99 - p01)
    flatline = float(np.mean(np.diff(finite) == 0)) if finite_n > 1 else None
    min_value = float(np.min(finite))
    max_value = float(np.max(finite))
    clipping = float(np.mean((finite == min_value) | (finite == max_value)))
    dc_ratio = None if std == 0 else float(abs(mean) / std)

    low_ratio = p50 = p60 = None
    if sampling_rate_hz is not None and sampling_rate_hz > 0:
        low_ratio = _band_ratio(finite, sampling_rate_hz, 0.0, 20.0)
        p50 = _band_ratio(finite, sampling_rate_hz, 49.0, 51.0)
        p60 = _band_ratio(finite, sampling_rate_hz, 59.0, 61.0)

    return ChannelStatistics(
        sample_count=n,
        finite_count=finite_n,
        nonfinite_ratio=nonfinite_ratio,
        mean_uV=_safe_float(mean),
        median_uV=_safe_float(median),
        std_uV=_safe_float(std),
        mad_uV=_safe_float(mad),
        rms_uV=_safe_float(rms),
        mav_uV=_safe_float(mav),
        p01_uV=_safe_float(p01),
        p99_uV=_safe_float(p99),
        robust_range_uV=_safe_float(robust_range),
        flatline_ratio=_safe_float(flatline) if flatline is not None else None,
        clipping_candidate_ratio=_safe_float(clipping),
        dc_to_std_ratio=_safe_float(dc_ratio) if dc_ratio is not None else None,
        low_frequency_0_20_ratio=_safe_float(low_ratio) if low_ratio is not None else None,
        powerline_50hz_ratio=_safe_float(p50) if p50 is not None else None,
        powerline_60hz_ratio=_safe_float(p60) if p60 is not None else None,
    )


def stats_to_dict(stats: ChannelStatistics) -> dict[str, object]:
    return asdict(stats)
