"""Adapter mỏng giữa preprocessing service và semg_core."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from semg_core.preprocessing import CorePreprocessResult, preprocess_channel


def run_channel_filters(
    samples_uV: np.ndarray,
    *,
    sampling_rate_hz: float,
    config: Mapping[str, Any],
    apply_notch: bool,
) -> CorePreprocessResult:
    steps = config["steps"]
    mean_cfg = steps["mean_center"]
    band_cfg = steps["bandpass"]
    notch_cfg = steps["notch"]
    return preprocess_channel(
        samples_uV,
        sampling_rate_hz=sampling_rate_hz,
        mean_center_enabled=bool(mean_cfg["enabled"]),
        bandpass_low_hz=float(band_cfg["low_cut_hz"]),
        bandpass_high_hz=float(band_cfg["high_cut_hz"]),
        bandpass_order=int(band_cfg["order"]),
        nyquist_margin_ratio=float(band_cfg["nyquist_margin_ratio"]),
        notch_enabled=bool(apply_notch),
        notch_frequency_hz=float(notch_cfg["line_frequency_hz"]),
        notch_q_factor=float(notch_cfg["q_factor"]),
    )
