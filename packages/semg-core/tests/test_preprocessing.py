from __future__ import annotations

import numpy as np
import pytest
from scipy.signal import correlate

from semg_core.preprocessing import (
    PreprocessingError,
    array_sha256_float64,
    design_butterworth_bandpass_sos,
    apply_zero_phase_sos,
    mean_center,
    preprocess_channel,
)


def sine(frequency_hz: float, *, fs: float = 1000.0, duration_s: float = 4.0) -> np.ndarray:
    t = np.arange(int(fs * duration_s), dtype=np.float64) / fs
    return np.sin(2.0 * np.pi * frequency_hz * t)


def test_mean_center_removes_dc() -> None:
    x = 8.0 + sine(80.0)
    y = mean_center(x)
    assert abs(float(np.mean(y))) < 1e-12


def test_design_butterworth_bandpass_sos_returns_valid_shape() -> None:
    sos = design_butterworth_bandpass_sos(
        sampling_rate_hz=1000.0,
        low_cut_hz=20.0,
        high_cut_hz=400.0,
        order=4,
        nyquist_margin_ratio=0.90,
    )
    assert isinstance(sos, np.ndarray)
    assert sos.ndim == 2
    assert sos.shape[1] == 6


def test_invalid_high_cut_is_rejected() -> None:
    with pytest.raises(PreprocessingError):
        design_butterworth_bandpass_sos(
            sampling_rate_hz=1000.0,
            low_cut_hz=20.0,
            high_cut_hz=480.0,
            order=4,
            nyquist_margin_ratio=0.90,
        )


def test_bandpass_preserves_80_and_attenuates_5_and_450() -> None:
    fs = 1000.0
    x5 = sine(5.0, fs=fs)
    x80 = sine(80.0, fs=fs)
    x450 = sine(450.0, fs=fs)

    def filtered_std(x: np.ndarray) -> float:
        result = preprocess_channel(
            x,
            sampling_rate_hz=fs,
            mean_center_enabled=True,
            bandpass_low_hz=20.0,
            bandpass_high_hz=400.0,
            bandpass_order=4,
            nyquist_margin_ratio=0.90,
            notch_enabled=False,
            notch_frequency_hz=50.0,
            notch_q_factor=30.0,
        )
        # Loại 0,5 s ở hai đầu để tránh đánh giá transient.
        return float(np.std(result.samples_uV[500:-500]))

    original = float(np.std(x80[500:-500]))
    assert filtered_std(x80) / original > 0.90
    assert filtered_std(x5) / float(np.std(x5[500:-500])) < 0.05
    assert filtered_std(x450) / float(np.std(x450[500:-500])) < 0.10


def test_zero_phase_has_near_zero_lag_for_passband_sine() -> None:
    x = sine(80.0, duration_s=6.0)
    result = preprocess_channel(
        x,
        sampling_rate_hz=1000.0,
        mean_center_enabled=True,
        bandpass_low_hz=20.0,
        bandpass_high_hz=400.0,
        bandpass_order=4,
        nyquist_margin_ratio=0.90,
        notch_enabled=False,
        notch_frequency_hz=50.0,
        notch_q_factor=30.0,
    )
    x_mid = x[1000:-1000]
    y_mid = result.samples_uV[1000:-1000]
    corr = correlate(y_mid, x_mid, mode="full")
    lag = int(np.argmax(corr) - (x_mid.size - 1))
    assert abs(lag) <= 1


def test_notch_reduces_50_hz_and_preserves_80_hz() -> None:
    x_50 = sine(50.0, duration_s=6.0)
    x_80 = sine(80.0, duration_s=6.0)
    
    kwargs = dict(
        sampling_rate_hz=1000.0,
        mean_center_enabled=True,
        bandpass_low_hz=20.0,
        bandpass_high_hz=400.0,
        bandpass_order=4,
        nyquist_margin_ratio=0.90,
        notch_frequency_hz=50.0,
        notch_q_factor=30.0,
    )
    
    out_50_no_notch = preprocess_channel(x_50, notch_enabled=False, **kwargs).samples_uV
    out_50_with_notch = preprocess_channel(x_50, notch_enabled=True, **kwargs).samples_uV
    
    out_80_no_notch = preprocess_channel(x_80, notch_enabled=False, **kwargs).samples_uV
    out_80_with_notch = preprocess_channel(x_80, notch_enabled=True, **kwargs).samples_uV
    
    std_50_no = float(np.std(out_50_no_notch[1000:-1000]))
    std_50_with = float(np.std(out_50_with_notch[1000:-1000]))
    
    std_80_no = float(np.std(out_80_no_notch[1000:-1000]))
    std_80_with = float(np.std(out_80_with_notch[1000:-1000]))
    
    # 50 Hz component giảm rõ ràng (dưới 10%)
    assert std_50_with < std_50_no * 0.1
    
    # 80 Hz bị ảnh hưởng tối thiểu trong test (giữ > 95%)
    assert std_80_with > std_80_no * 0.95


def test_output_is_deterministic_and_read_only() -> None:
    rng = np.random.default_rng(42)
    x = rng.normal(size=8000)
    kwargs = dict(
        sampling_rate_hz=1000.0,
        mean_center_enabled=True,
        bandpass_low_hz=20.0,
        bandpass_high_hz=400.0,
        bandpass_order=4,
        nyquist_margin_ratio=0.90,
        notch_enabled=False,
        notch_frequency_hz=50.0,
        notch_q_factor=30.0,
    )
    a = preprocess_channel(x, **kwargs)
    b = preprocess_channel(x, **kwargs)
    assert array_sha256_float64(a.samples_uV) == array_sha256_float64(b.samples_uV)
    assert a.samples_uV.flags.writeable is False


def test_nonfinite_is_not_silently_imputed() -> None:
    x = sine(80.0)
    x[100] = np.nan
    with pytest.raises(PreprocessingError):
        preprocess_channel(
            x,
            sampling_rate_hz=1000.0,
            mean_center_enabled=True,
            bandpass_low_hz=20.0,
            bandpass_high_hz=400.0,
            bandpass_order=4,
            nyquist_margin_ratio=0.90,
            notch_enabled=False,
            notch_frequency_hz=50.0,
            notch_q_factor=30.0,
        )


def test_apply_zero_phase_sos_too_short_raises_error() -> None:
    sos = design_butterworth_bandpass_sos(
        sampling_rate_hz=1000.0,
        low_cut_hz=20.0,
        high_cut_hz=400.0,
        order=4,
        nyquist_margin_ratio=0.90,
    )
    # A very short array (less than padlen)
    x_short = np.ones(10, dtype=np.float64)
    with pytest.raises(PreprocessingError, match="Không thể sosfiltfilt"):
        apply_zero_phase_sos(x_short, sos)


def test_apply_zero_phase_sos_does_not_mutate_input_and_returns_same_length() -> None:
    sos = design_butterworth_bandpass_sos(
        sampling_rate_hz=1000.0,
        low_cut_hz=20.0,
        high_cut_hz=400.0,
        order=4,
        nyquist_margin_ratio=0.90,
    )
    x = sine(80.0, duration_s=1.0)
    x_copy = x.copy()
    y = apply_zero_phase_sos(x, sos)
    
    # Do not mutate input
    np.testing.assert_array_equal(x, x_copy)
    
    # Same length
    assert len(y) == len(x)
    
    # Finite output
    assert np.isfinite(y).all()
