from __future__ import annotations

from collections.abc import Mapping, Sequence
from math import isfinite
from statistics import median

import numpy as np

MENDELEY_PRIMARY_CHANNELS = (
    "EMG_Raw_CH1",
    "EMG_RAW_CH2",
    "EMG_RAW_CH3",
)
MENDELEY_CH4 = "EMG_RAW_CH4"


def expand_grabmyo_primary_channels() -> tuple[str, ...]:
    return tuple(f"F{i}" for i in range(1, 17)) + tuple(
        f"W{i}" for i in range(1, 13)
    )


def grabmyo_excluded_channels() -> tuple[str, ...]:
    return tuple(f"U{i}" for i in range(1, 5))


def decide_mendeley_ch4(
    std_by_channel: Mapping[str, float],
    ratio_threshold: float = 0.10,
) -> dict[str, float | str | bool]:
    if not isfinite(ratio_threshold) or not 0 < ratio_threshold <= 1:
        raise ValueError("ratio_threshold must be finite and in (0, 1]")
    expected = MENDELEY_PRIMARY_CHANNELS + (MENDELEY_CH4,)
    missing = [name for name in expected if name not in std_by_channel]
    if missing:
        raise ValueError(f"Missing channel statistics: {missing}")
    values = {name: float(std_by_channel[name]) for name in expected}
    if any(not isfinite(value) for value in values.values()):
        raise ValueError("Channel statistics must be finite")
    primary_median = median(values[name] for name in MENDELEY_PRIMARY_CHANNELS)
    if primary_median <= 0:
        raise ValueError("Primary channel standard deviations must be positive")
    if values[MENDELEY_CH4] < 0:
        raise ValueError("CH4 standard deviation must be non-negative")
    ratio = values[MENDELEY_CH4] / primary_median
    quarantine = ratio < ratio_threshold
    return {
        "channel": MENDELEY_CH4,
        "primary_median_std": primary_median,
        "ch4_std": values[MENDELEY_CH4],
        "std_ratio": ratio,
        "status": (
            "QUARANTINED_EXCLUDED_PRIMARY" if quarantine else "REVIEW_REQUIRED"
        ),
        "broken_channel_claim_allowed": False,
        "reference_channel_claim_allowed": False,
        "sensitivity_view_allowed": True,
    }


def channel_summary(
    values: Sequence[float],
    active_threshold: float = 0.0,
) -> dict[str, float]:
    source = np.asarray(values, dtype=float)
    if source.ndim != 1 or source.size == 0:
        raise ValueError("values must be a non-empty 1D vector")
    if not np.isfinite(source).all():
        raise ValueError("values must contain only finite values")
    if not isfinite(active_threshold) or active_threshold < 0:
        raise ValueError("active_threshold must be finite and non-negative")
    q25, q75, q90 = np.quantile(source, [0.25, 0.75, 0.90])
    return {
        "median": float(np.median(source)),
        "iqr": float(q75 - q25),
        "q90": float(q90),
        "max": float(np.max(source)),
        "active_channel_fraction": float(
            np.mean(np.abs(source) > active_threshold)
        ),
    }

