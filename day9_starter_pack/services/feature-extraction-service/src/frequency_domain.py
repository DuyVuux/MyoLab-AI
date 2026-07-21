"""Tính PSD Welch cho một frequency-domain window hợp lệ."""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np

from semg_core.spectral import (
    SpectralEstimationError,
    estimate_welch_psd,
    integrate_uniform_psd,
    select_frequency_band,
)
from spectral_result_models import SpectralWindowValues


class SpectralPowerTooLow(SpectralEstimationError):
    """Dải phân tích không có đủ power để dùng downstream."""


def compute_spectral_window(
    samples: np.ndarray,
    *,
    sampling_rate_hz: float,
    config: Mapping[str, object],
) -> tuple[np.ndarray, SpectralWindowValues, dict[str, float | int | str | bool]]:
    estimator = dict(config["estimator"])  # type: ignore[arg-type]
    band = dict(config["analysis_band"])  # type: ignore[arg-type]
    guard = dict(config["power_guard"])  # type: ignore[arg-type]

    values = np.asarray(samples, dtype=np.float64)
    estimate = estimate_welch_psd(
        values,
        sampling_rate_hz=float(sampling_rate_hz),
        taper=str(estimator["taper"]),
        detrend=str(estimator["detrend"]),
        scaling=str(estimator["scaling"]),
        nperseg_samples=int(values.size),
        noverlap_samples=int(estimator["noverlap_samples"]),
        nfft_samples=int(values.size),
        average=str(estimator["average"]),
    )
    band_frequencies, band_psd = select_frequency_band(
        estimate.frequencies_hz,
        estimate.psd_uV2_per_hz,
        low_hz=float(band["low_hz"]),
        high_hz=float(band["high_hz"]),
        include_endpoints=bool(band["include_endpoints"]),
    )
    minimum_bins = int(band["minimum_frequency_bin_count"])
    if band_frequencies.size < minimum_bins:
        raise SpectralEstimationError(
            f"Dải phân tích chỉ có {band_frequencies.size} bins; cần >= {minimum_bins}"
        )
    band_power = integrate_uniform_psd(band_frequencies, band_psd)
    if band_power <= float(guard["minimum_band_power_uV2"]):
        raise SpectralPowerTooLow(
            f"Band power {band_power:.6g} uV^2 không vượt ngưỡng tối thiểu"
        )
    peak_frequency = float(band_frequencies[int(np.argmax(band_psd))])
    parseval_ratio = estimate.parseval_ratio
    qa_flags: list[str] = []
    if parseval_ratio is not None:
        lower = float(guard["parseval_ratio_warning_lower"])
        upper = float(guard["parseval_ratio_warning_upper"])
        if not (lower <= parseval_ratio <= upper):
            qa_flags.append("SPECTRAL_PARSEVAL_RATIO_OUTSIDE_EXPECTED_RANGE")
    window_values = SpectralWindowValues(
        psd_uV2_per_hz=tuple(float(item) for item in band_psd),
        band_power_uV2=float(band_power),
        full_power_uV2=float(estimate.full_power_uV2),
        time_domain_variance_uV2=float(estimate.time_domain_variance_uV2),
        window_weighted_power_uV2=float(estimate.window_weighted_power_uV2),
        parseval_ratio=(float(parseval_ratio) if parseval_ratio is not None else None),
        peak_frequency_hz=peak_frequency,
        qa_flags=tuple(qa_flags),
    )
    metadata: dict[str, float | int | str | bool] = {
        "method": estimate.method,
        "return_onesided": True,
        "taper": estimate.taper,
        "detrend": estimate.detrend,
        "scaling": estimate.scaling,
        "average": str(estimator["average"]),
        "nperseg_samples": int(estimate.nperseg_samples),
        "noverlap_samples": int(estimate.noverlap_samples),
        "nfft_samples": int(estimate.nfft_samples),
        "zero_padding_enabled": False,
        "frequency_bin_spacing_hz": float(estimate.frequency_bin_spacing_hz),
        "rayleigh_resolution_hz": float(estimate.rayleigh_resolution_hz),
        "analysis_band_low_hz": float(band_frequencies[0]),
        "analysis_band_high_hz": float(band_frequencies[-1]),
        "frequency_bin_count": int(band_frequencies.size),
    }
    return band_frequencies, window_values, metadata
