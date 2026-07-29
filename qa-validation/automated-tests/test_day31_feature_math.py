from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.stats import kurtosis, skew

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "semg-core"))

from semg_core.day31_features import (
    FEATURE_ORDER,
    FEATURE_VERSION,
    FeatureExtractionError,
    extract_feature_set_14,
)
from semg_core.day31_features.spectral_v1 import (
    periodogram_power_proxy,
    spectral_features,
)

EXPECTED_FEATURE_ORDER = (
    "rms",
    "mav",
    "skewness_unbiased",
    "kurtosis_fisher_unbiased",
    "max_signed",
    "min_signed",
    "std_sample_ddof1",
    "mean",
    "spectral_min_power",
    "spectral_max_power",
    "spectral_std_power_ddof1",
    "mdf_hz",
    "mnf_hz",
    "spectral_entropy_bits",
)


def test_feature_contract_and_reference_vector() -> None:
    signal = np.array([-3.0, -1.0, 0.5, 2.0, 4.0])
    result = extract_feature_set_14(signal, sampling_rate_hz=2_000.0)

    assert FEATURE_ORDER == EXPECTED_FEATURE_ORDER
    assert FEATURE_VERSION == "feature-set-14.v1.0.0"
    assert tuple(result.features) == EXPECTED_FEATURE_ORDER
    assert result.contract_version == FEATURE_VERSION
    assert result.features["rms"] == pytest.approx(
        math.sqrt(float(np.mean(np.square(signal))))
    )
    assert result.features["mav"] == pytest.approx(float(np.mean(np.abs(signal))))
    assert result.features["std_sample_ddof1"] == pytest.approx(
        float(np.std(signal, ddof=1))
    )
    assert result.features["skewness_unbiased"] == pytest.approx(
        float(skew(signal, bias=False))
    )
    assert result.features["kurtosis_fisher_unbiased"] == pytest.approx(
        float(kurtosis(signal, fisher=True, bias=False))
    )


def test_exact_bin_sine_and_positive_scale_invariants() -> None:
    sampling_rate_hz = 2_000.0
    time = np.arange(400) / sampling_rate_hz
    signal = np.sin(2 * np.pi * 50 * time)
    base = extract_feature_set_14(signal, sampling_rate_hz).features
    scaled = extract_feature_set_14(7.5 * signal, sampling_rate_hz).features

    assert base["mdf_hz"] == pytest.approx(50.0)
    assert base["mnf_hz"] == pytest.approx(50.0, abs=1e-10)
    assert base["spectral_entropy_bits"] < 1e-8
    for name in (
        "rms",
        "mav",
        "max_signed",
        "min_signed",
        "std_sample_ddof1",
        "mean",
    ):
        assert scaled[name] == pytest.approx(7.5 * base[name])
    for name in (
        "spectral_min_power",
        "spectral_max_power",
        "spectral_std_power_ddof1",
    ):
        assert scaled[name] == pytest.approx(7.5**2 * base[name])
    for name in (
        "skewness_unbiased",
        "kurtosis_fisher_unbiased",
        "mdf_hz",
        "mnf_hz",
        "spectral_entropy_bits",
    ):
        assert scaled[name] == pytest.approx(base[name], nan_ok=True)


def test_sign_inversion_contract() -> None:
    signal = np.array([-4.0, -2.0, -1.0, 0.5, 3.0, 8.0])
    base = extract_feature_set_14(signal, 2_000.0).features
    inverted = extract_feature_set_14(-signal, 2_000.0).features

    for name in (
        "rms",
        "mav",
        "std_sample_ddof1",
        "kurtosis_fisher_unbiased",
        "spectral_min_power",
        "spectral_max_power",
        "spectral_std_power_ddof1",
        "mdf_hz",
        "mnf_hz",
        "spectral_entropy_bits",
    ):
        assert inverted[name] == pytest.approx(base[name])
    assert inverted["mean"] == pytest.approx(-base["mean"])
    assert inverted["skewness_unbiased"] == pytest.approx(
        -base["skewness_unbiased"]
    )
    assert inverted["max_signed"] == pytest.approx(-base["min_signed"])
    assert inverted["min_signed"] == pytest.approx(-base["max_signed"])


@pytest.mark.parametrize(
    ("signal", "expected_flags"),
    [
        (
            np.zeros(400),
            {"constant_window", "zero_power_window", "feature_nonfinite"},
        ),
        (
            np.ones(400),
            {"constant_window", "feature_nonfinite"},
        ),
        (
            np.array([1.0]),
            {
                "insufficient_samples_moments",
                "insufficient_spectral_bins",
                "feature_nonfinite",
            },
        ),
    ],
)
def test_edge_cases_emit_nan_with_reason_codes(
    signal: np.ndarray, expected_flags: set[str]
) -> None:
    result = extract_feature_set_14(signal, 2_000.0)

    assert expected_flags.issubset(result.qc_flags)
    assert not any(math.isinf(value) for value in result.features.values())


@pytest.mark.parametrize("sampling_rate_hz", [0.0, -1.0, math.nan, math.inf])
def test_sampling_rate_must_be_positive_and_finite(
    sampling_rate_hz: float,
) -> None:
    with pytest.raises(FeatureExtractionError):
        extract_feature_set_14(np.arange(8.0), sampling_rate_hz)


def test_nonfinite_input_is_fail_closed_or_explicitly_flagged() -> None:
    signal = np.array([1.0, math.nan, 2.0, math.inf])

    with pytest.raises(FeatureExtractionError, match="nonfinite_input"):
        extract_feature_set_14(signal, 2_000.0)

    result = extract_feature_set_14(signal, 2_000.0, strict_nonfinite=False)
    assert set(result.qc_flags) == {"feature_nonfinite", "nonfinite_input"}
    assert all(math.isnan(value) for value in result.features.values())


def test_finite_extreme_input_never_leaks_infinity() -> None:
    signal = np.array([1e308, -1e308, 1e308, -1e308])
    result = extract_feature_set_14(signal, 2_000.0)

    assert "feature_nonfinite" in result.qc_flags
    assert not any(math.isinf(value) for value in result.features.values())
    assert math.isfinite(result.features["rms"])
    assert math.isfinite(result.features["mav"])


def test_spectral_helpers_reject_invalid_vectors() -> None:
    with pytest.raises(ValueError):
        periodogram_power_proxy(np.array([1.0, math.nan]), 2_000.0)
    with pytest.raises(ValueError):
        spectral_features(
            np.array([1.0, -1.0]),
            np.array([0.0, 1.0]),
        )
    with pytest.raises(ValueError):
        spectral_features(
            np.array([1.0, 2.0]),
            np.array([1.0, 0.0]),
        )


def test_entropy_is_bounded_by_number_of_positive_bins() -> None:
    power = np.ones(17)
    frequencies = np.arange(17, dtype=float)
    values, flags = spectral_features(power, frequencies)

    assert flags == ()
    assert values["spectral_entropy_bits"] == pytest.approx(math.log2(17))

