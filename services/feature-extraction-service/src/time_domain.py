"""Wrapper service-level cho RMS/MAV trên một cửa sổ hợp lệ."""

from __future__ import annotations

import numpy as np

from semg_core.features import TimeDomainFeatureValues, extract_time_domain_features


def compute_time_domain_window_features(
    samples_uV: np.ndarray,
) -> TimeDomainFeatureValues:
    """Tính RMS/MAV từ band-passed, unrectified samples có đơn vị uV."""

    return extract_time_domain_features(samples_uV, amplitude_unit="uV")
