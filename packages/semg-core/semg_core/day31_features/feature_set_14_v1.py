"""Locked 14-feature reference extractor for Day 31."""

from __future__ import annotations

import math
import warnings
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType

import numpy as np
from scipy.stats import kurtosis, skew

from .spectral_v1 import extract_spectral_features

FEATURE_VERSION = "feature-set-14.v1.0.0"
TIME_FEATURE_IDS = (
    "rms",
    "mav",
    "skewness_unbiased",
    "kurtosis_fisher_unbiased",
    "max_signed",
    "min_signed",
    "std_sample_ddof1",
    "mean",
)
SPECTRAL_FEATURE_IDS = (
    "spectral_min_power",
    "spectral_max_power",
    "spectral_std_power_ddof1",
    "mdf_hz",
    "mnf_hz",
    "spectral_entropy_bits",
)
FEATURE_ORDER = TIME_FEATURE_IDS + SPECTRAL_FEATURE_IDS


class FeatureExtractionError(ValueError):
    """Raised when an input violates the locked extraction contract."""


@dataclass(frozen=True, slots=True)
class FeatureResult:
    """Immutable output of one window-channel extraction."""

    features: Mapping[str, float]
    qc_flags: tuple[str, ...]
    contract_version: str = FEATURE_VERSION

    def __post_init__(self) -> None:
        if tuple(self.features) != FEATURE_ORDER:
            raise ValueError("feature order contract violated")
        object.__setattr__(
            self,
            "features",
            MappingProxyType(dict(self.features)),
        )
        object.__setattr__(self, "qc_flags", tuple(sorted(set(self.qc_flags))))


def _validated_signal(
    signal: Sequence[float] | np.ndarray,
) -> np.ndarray:
    try:
        values = np.asarray(signal, dtype=np.float64)
    except (TypeError, ValueError, OverflowError) as error:
        raise FeatureExtractionError("signal must be numeric") from error
    if values.ndim != 1 or values.size == 0:
        raise FeatureExtractionError("signal must be a non-empty 1D window")
    return values


def _stable_amplitude_statistics(
    values: np.ndarray,
) -> tuple[float, float, float, float]:
    """Return RMS, MAV, sample STD, and mean with scale-safe arithmetic."""

    scale = float(np.max(np.abs(values)))
    if scale == 0.0:
        return 0.0, 0.0, 0.0 if values.size >= 2 else math.nan, 0.0
    normalized = values / scale
    with np.errstate(over="ignore", invalid="ignore"):
        rms = float(scale * np.sqrt(np.mean(normalized * normalized)))
        mav = float(scale * np.mean(np.abs(normalized)))
        std = (
            float(scale * np.std(normalized, ddof=1))
            if values.size >= 2
            else math.nan
        )
        mean = float(scale * np.mean(normalized))
    return rms, mav, std, mean


def _sanitize_nonfinite(
    values: dict[str, float],
    flags: set[str],
) -> dict[str, float]:
    sanitized: dict[str, float] = {}
    for name in FEATURE_ORDER:
        value = float(values[name])
        if math.isinf(value):
            value = math.nan
            flags.add("numeric_overflow")
        if not math.isfinite(value):
            flags.add("feature_nonfinite")
        sanitized[name] = value
    return sanitized


def extract_feature_set_14(
    signal: Sequence[float] | np.ndarray,
    sampling_rate_hz: float,
    strict_nonfinite: bool = True,
) -> FeatureResult:
    """Extract the locked Day 31 feature set from one one-dimensional window.

    Input is assumed to have already passed the versioned upstream DC-removal
    policy. This function performs no filtering, smoothing, imputation, or
    learned transformation.
    """

    values = _validated_signal(signal)
    try:
        sampling_rate = float(sampling_rate_hz)
    except (TypeError, ValueError, OverflowError) as error:
        raise FeatureExtractionError(
            "sampling_rate_hz must be positive and finite"
        ) from error
    if not math.isfinite(sampling_rate) or sampling_rate <= 0.0:
        raise FeatureExtractionError(
            "sampling_rate_hz must be positive and finite"
        )
    if not bool(np.isfinite(values).all()):
        if strict_nonfinite:
            raise FeatureExtractionError("nonfinite_input")
        missing = {name: math.nan for name in FEATURE_ORDER}
        return FeatureResult(
            missing,
            ("feature_nonfinite", "nonfinite_input"),
        )

    flags: set[str] = set()
    is_constant = bool(np.max(values) == np.min(values))
    if is_constant:
        flags.add("constant_window")
    if values.size < 4:
        flags.add("insufficient_samples_moments")

    rms, mav, sample_std, mean = _stable_amplitude_statistics(values)
    if values.size < 4 or is_constant:
        skewness = math.nan
        excess_kurtosis = math.nan
    else:
        amplitude_scale = float(np.max(np.abs(values)))
        moment_input = values / amplitude_scale
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            skewness = float(skew(moment_input, bias=False))
            excess_kurtosis = float(
                kurtosis(moment_input, fisher=True, bias=False)
            )

    time_features = {
        "rms": rms,
        "mav": mav,
        "skewness_unbiased": skewness,
        "kurtosis_fisher_unbiased": excess_kurtosis,
        "max_signed": float(np.max(values)),
        "min_signed": float(np.min(values)),
        "std_sample_ddof1": sample_std,
        "mean": mean,
    }
    spectral_features, spectral_flags = extract_spectral_features(
        values,
        sampling_rate,
    )
    flags.update(spectral_flags)
    combined = {**time_features, **spectral_features}
    if tuple(combined) != FEATURE_ORDER:
        raise RuntimeError("feature order contract violated")
    return FeatureResult(_sanitize_nonfinite(combined, flags), tuple(flags))
