"""Deterministic Day 31 feature-engineering reference implementation.

This namespace is intentionally separate from :mod:`semg_core.features`,
which remains the stable Day 8 RMS/MAV API.
"""

from .feature_set_14_v1 import (
    FEATURE_ORDER,
    FEATURE_VERSION,
    SPECTRAL_FEATURE_IDS,
    TIME_FEATURE_IDS,
    FeatureExtractionError,
    FeatureResult,
    extract_feature_set_14,
)

__all__ = [
    "FEATURE_ORDER",
    "FEATURE_VERSION",
    "SPECTRAL_FEATURE_IDS",
    "TIME_FEATURE_IDS",
    "FeatureExtractionError",
    "FeatureResult",
    "extract_feature_set_14",
]
