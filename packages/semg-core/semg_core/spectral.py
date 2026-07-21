"""Các hàm thuần cho nền tảng phân tích phổ sEMG.

Phạm vi Day 9:
- trục tần số một phía cho tín hiệu thực;
- periodogram và Welch PSD;
- Hann taper chỉ trong tầng spectral;
- giới hạn dải phân tích 20--400 Hz theo cấu hình;
- tích phân PSD và kiểm tra nhất quán năng lượng;
- chưa tính MDF, MNF, slope, fatigue score hoặc kết luận lâm sàng.

Đơn vị đầu vào canonical là microvolt (uV). Với ``scaling='density'``,
đơn vị PSD là uV^2/Hz và tích phân PSD theo tần số có đơn vị uV^2.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

import numpy as np
from scipy.signal import get_window, periodogram, welch


class SpectralEstimationError(ValueError):
    """Lỗi contract hoặc dữ liệu khi ước lượng phổ."""


@dataclass(frozen=True, slots=True)
class SpectralDensityEstimate:
    """Kết quả PSD một phía của một cửa sổ hữu hạn."""

    frequencies_hz: np.ndarray
    psd_uV2_per_hz: np.ndarray
    sampling_rate_hz: float
    method: str
    taper: str
    detrend: str
    scaling: str
    nperseg_samples: int
    noverlap_samples: int
    nfft_samples: int
    frequency_bin_spacing_hz: float
    rayleigh_resolution_hz: float
    full_power_uV2: float
    time_domain_variance_uV2: float
    window_weighted_power_uV2: float
    parseval_ratio: float | None

    def __post_init__(self) -> None:
        frequencies = np.ascontiguousarray(self.frequencies_hz, dtype=np.float64)
        psd = np.ascontiguousarray(self.psd_uV2_per_hz, dtype=np.float64)
        if frequencies.ndim != 1 or psd.ndim != 1:
            raise SpectralEstimationError("frequency và PSD phải là mảng một chiều")
        if frequencies.size != psd.size or frequencies.size < 2:
            raise SpectralEstimationError("frequency và PSD phải cùng kích thước >= 2")
        if not np.isfinite(frequencies).all() or not np.isfinite(psd).all():
            raise SpectralEstimationError("frequency và PSD phải hoàn toàn hữu hạn")
        if np.any(np.diff(frequencies) <= 0):
            raise SpectralEstimationError("frequency axis phải tăng nghiêm ngặt")
        if np.any(psd < -1e-15):
            raise SpectralEstimationError("PSD không được âm")
        if self.sampling_rate_hz <= 0 or not math.isfinite(self.sampling_rate_hz):
            raise SpectralEstimationError("sampling_rate_hz phải hữu hạn và > 0")
        if self.nperseg_samples < 2:
            raise SpectralEstimationError("nperseg_samples phải >= 2")
        if not (0 <= self.noverlap_samples < self.nperseg_samples):
            raise SpectralEstimationError("noverlap_samples không hợp lệ")
        if self.nfft_samples < self.nperseg_samples:
            raise SpectralEstimationError("nfft_samples phải >= nperseg_samples")
        for name, value in (
            ("frequency_bin_spacing_hz", self.frequency_bin_spacing_hz),
            ("rayleigh_resolution_hz", self.rayleigh_resolution_hz),
            ("full_power_uV2", self.full_power_uV2),
            ("time_domain_variance_uV2", self.time_domain_variance_uV2),
            ("window_weighted_power_uV2", self.window_weighted_power_uV2),
        ):
            if not math.isfinite(value) or value < 0:
                raise SpectralEstimationError(f"{name} phải hữu hạn và không âm")
        if self.parseval_ratio is not None:
            if not math.isfinite(self.parseval_ratio) or self.parseval_ratio < 0:
                raise SpectralEstimationError("parseval_ratio phải hữu hạn và không âm")
        frequencies.setflags(write=False)
        psd.setflags(write=False)
        object.__setattr__(self, "frequencies_hz", frequencies)
        object.__setattr__(self, "psd_uV2_per_hz", np.maximum(psd, 0.0))
        self.psd_uV2_per_hz.setflags(write=False)

    def to_summary(self) -> dict[str, Any]:
        return {
            "sampling_rate_hz": float(self.sampling_rate_hz),
            "method": self.method,
            "taper": self.taper,
            "detrend": self.detrend,
            "scaling": self.scaling,
            "nperseg_samples": int(self.nperseg_samples),
            "noverlap_samples": int(self.noverlap_samples),
            "nfft_samples": int(self.nfft_samples),
            "frequency_bin_spacing_hz": float(self.frequency_bin_spacing_hz),
            "rayleigh_resolution_hz": float(self.rayleigh_resolution_hz),
            "full_power_uV2": float(self.full_power_uV2),
            "time_domain_variance_uV2": float(self.time_domain_variance_uV2),
            "window_weighted_power_uV2": float(self.window_weighted_power_uV2),
            "parseval_ratio": (
                float(self.parseval_ratio) if self.parseval_ratio is not None else None
            ),
        }


def _validated_vector(
    samples: np.ndarray | list[float] | tuple[float, ...],
) -> np.ndarray:
    values = np.asarray(samples, dtype=np.float64)
    if values.ndim != 1:
        raise SpectralEstimationError("samples phải là mảng một chiều")
    if values.size < 4:
        raise SpectralEstimationError("samples cần ít nhất 4 phần tử")
    if not np.isfinite(values).all():
        raise SpectralEstimationError("samples phải hoàn toàn hữu hạn")
    return values


def _validated_sampling_rate(sampling_rate_hz: float) -> float:
    value = float(sampling_rate_hz)
    if not math.isfinite(value) or value <= 0:
        raise SpectralEstimationError("sampling_rate_hz phải hữu hạn và > 0")
    return value


def one_sided_frequency_axis(
    *, sampling_rate_hz: float, nfft_samples: int
) -> np.ndarray:
    """Trả trục tần số ``rfft`` từ 0 tới Nyquist."""

    sampling_rate = _validated_sampling_rate(sampling_rate_hz)
    if int(nfft_samples) != nfft_samples or nfft_samples < 2:
        raise SpectralEstimationError("nfft_samples phải là số nguyên >= 2")
    axis = np.fft.rfftfreq(int(nfft_samples), d=1.0 / sampling_rate)
    axis = np.ascontiguousarray(axis, dtype=np.float64)
    axis.setflags(write=False)
    return axis


def frequency_bin_spacing_hz(*, sampling_rate_hz: float, nfft_samples: int) -> float:
    sampling_rate = _validated_sampling_rate(sampling_rate_hz)
    if nfft_samples < 2:
        raise SpectralEstimationError("nfft_samples phải >= 2")
    return float(sampling_rate / int(nfft_samples))


def rayleigh_resolution_hz(
    *, sampling_rate_hz: float, nperseg_samples: int
) -> float:
    """Độ phân giải Rayleigh xấp xỉ ``Fs / N_segment``.

    Đây là độ phân giải vật lý do độ dài segment quyết định. Nếu ``nfft`` lớn hơn
    ``nperseg`` do zero-padding, khoảng cách bin có thể nhỏ hơn nhưng độ phân giải
    Rayleigh không được cải thiện tương ứng.
    """

    sampling_rate = _validated_sampling_rate(sampling_rate_hz)
    if nperseg_samples < 2:
        raise SpectralEstimationError("nperseg_samples phải >= 2")
    return float(sampling_rate / int(nperseg_samples))


def integrate_uniform_psd(
    frequencies_hz: np.ndarray,
    psd_density: np.ndarray,
) -> float:
    """Tích phân PSD trên trục đều bằng ``sum(PSD) * df``.

    Cách này phù hợp với convention của SciPy cho periodogram/Welch density,
    trong đó tổng mật độ nhân với khoảng cách bin xấp xỉ công suất miền thời gian đã được chuẩn hóa theo năng lượng taper.
    """

    frequencies = np.asarray(frequencies_hz, dtype=np.float64)
    psd = np.asarray(psd_density, dtype=np.float64)
    if frequencies.ndim != 1 or psd.ndim != 1:
        raise SpectralEstimationError("frequency và PSD phải là mảng một chiều")
    if frequencies.size != psd.size or frequencies.size < 2:
        raise SpectralEstimationError("frequency và PSD phải cùng kích thước >= 2")
    if not np.isfinite(frequencies).all() or not np.isfinite(psd).all():
        raise SpectralEstimationError("frequency và PSD phải hữu hạn")
    diffs = np.diff(frequencies)
    if np.any(diffs <= 0):
        raise SpectralEstimationError("frequency axis phải tăng nghiêm ngặt")
    df = float(np.median(diffs))
    tolerance = max(1e-12, abs(df) * 1e-9)
    if float(np.max(np.abs(diffs - df))) > tolerance:
        raise SpectralEstimationError("frequency axis phải có khoảng cách đều")
    return float(np.sum(np.maximum(psd, 0.0), dtype=np.float64) * df)


def select_frequency_band(
    frequencies_hz: np.ndarray,
    psd_density: np.ndarray,
    *,
    low_hz: float,
    high_hz: float,
    include_endpoints: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    frequencies = np.asarray(frequencies_hz, dtype=np.float64)
    psd = np.asarray(psd_density, dtype=np.float64)
    if frequencies.shape != psd.shape or frequencies.ndim != 1:
        raise SpectralEstimationError("frequency và PSD phải là vector cùng shape")
    if not (math.isfinite(low_hz) and math.isfinite(high_hz)):
        raise SpectralEstimationError("Giới hạn dải phải hữu hạn")
    if low_hz < 0 or high_hz <= low_hz:
        raise SpectralEstimationError("Dải tần không hợp lệ")
    if high_hz > float(frequencies[-1]) + 1e-12:
        raise SpectralEstimationError("high_hz vượt Nyquist/trục tần số")
    if include_endpoints:
        mask = (frequencies >= low_hz) & (frequencies <= high_hz)
    else:
        mask = (frequencies > low_hz) & (frequencies < high_hz)
    if int(np.count_nonzero(mask)) < 2:
        raise SpectralEstimationError("Dải phân tích cần ít nhất 2 frequency bins")
    selected_f = np.ascontiguousarray(frequencies[mask], dtype=np.float64)
    selected_p = np.ascontiguousarray(psd[mask], dtype=np.float64)
    selected_f.setflags(write=False)
    selected_p.setflags(write=False)
    return selected_f, selected_p


def _time_domain_variance(samples: np.ndarray, detrend: str) -> float:
    if detrend == "constant":
        centered = samples - float(np.mean(samples, dtype=np.float64))
        return float(np.mean(centered * centered, dtype=np.float64))
    if detrend in {"false", "none"}:
        return float(np.mean(samples * samples, dtype=np.float64))
    raise SpectralEstimationError(f"detrend không hỗ trợ: {detrend}")



def _window_weighted_power(samples: np.ndarray, detrend: str, taper: str) -> float:
    if detrend == "constant":
        prepared = samples - float(np.mean(samples, dtype=np.float64))
    elif detrend in {"false", "none"}:
        prepared = samples
    else:
        raise SpectralEstimationError(f"detrend không hỗ trợ: {detrend}")
    window = np.asarray(get_window(taper, samples.size, fftbins=True), dtype=np.float64)
    denominator = float(np.sum(window * window, dtype=np.float64))
    if denominator <= 0:
        raise SpectralEstimationError("Window energy phải > 0")
    weighted = prepared * window
    return float(np.sum(weighted * weighted, dtype=np.float64) / denominator)


def estimate_periodogram_psd(
    samples: np.ndarray | list[float] | tuple[float, ...],
    *,
    sampling_rate_hz: float,
    taper: str = "hann",
    detrend: str = "constant",
    scaling: str = "density",
    nfft_samples: int | None = None,
) -> SpectralDensityEstimate:
    """Ước lượng modified periodogram một phía cho tín hiệu thực."""

    values = _validated_vector(samples)
    sampling_rate = _validated_sampling_rate(sampling_rate_hz)
    nfft = int(nfft_samples or values.size)
    if nfft < values.size:
        raise SpectralEstimationError("nfft_samples phải >= sample count")
    if taper not in {"hann", "boxcar"}:
        raise SpectralEstimationError("Chỉ hỗ trợ taper hann hoặc boxcar")
    if detrend not in {"constant", "false", "none"}:
        raise SpectralEstimationError("Chỉ hỗ trợ detrend constant/none")
    if scaling != "density":
        raise SpectralEstimationError("Day 9 chỉ hỗ trợ scaling='density'")
    scipy_detrend: str | bool = False if detrend in {"false", "none"} else detrend
    frequencies, psd = periodogram(
        values,
        fs=sampling_rate,
        window=taper,
        detrend=scipy_detrend,
        return_onesided=True,
        scaling=scaling,
        nfft=nfft,
    )
    variance = _time_domain_variance(values, detrend)
    weighted_power = _window_weighted_power(values, detrend, taper)
    full_power = integrate_uniform_psd(frequencies, psd)
    ratio = None if weighted_power <= 0 else float(full_power / weighted_power)
    return SpectralDensityEstimate(
        frequencies_hz=frequencies,
        psd_uV2_per_hz=psd,
        sampling_rate_hz=sampling_rate,
        method="periodogram",
        taper=taper,
        detrend=detrend,
        scaling=scaling,
        nperseg_samples=int(values.size),
        noverlap_samples=0,
        nfft_samples=nfft,
        frequency_bin_spacing_hz=frequency_bin_spacing_hz(
            sampling_rate_hz=sampling_rate, nfft_samples=nfft
        ),
        rayleigh_resolution_hz=rayleigh_resolution_hz(
            sampling_rate_hz=sampling_rate, nperseg_samples=int(values.size)
        ),
        full_power_uV2=full_power,
        time_domain_variance_uV2=variance,
        window_weighted_power_uV2=weighted_power,
        parseval_ratio=ratio,
    )


def estimate_welch_psd(
    samples: np.ndarray | list[float] | tuple[float, ...],
    *,
    sampling_rate_hz: float,
    taper: str = "hann",
    detrend: str = "constant",
    scaling: str = "density",
    nperseg_samples: int | None = None,
    noverlap_samples: int = 0,
    nfft_samples: int | None = None,
    average: str = "mean",
) -> SpectralDensityEstimate:
    """Ước lượng Welch PSD một phía.

    Cấu hình MVP-0 dùng toàn bộ outer frequency window làm một segment,
    ``noverlap=0`` và ``nfft=window_length``. Khi đó Welch tương đương một
    modified periodogram về mặt estimator, nhưng dùng cùng API cho phép nâng
    cấp sang nhiều segment ở version sau mà không đổi contract downstream.
    """

    values = _validated_vector(samples)
    sampling_rate = _validated_sampling_rate(sampling_rate_hz)
    nperseg = int(nperseg_samples or values.size)
    nfft = int(nfft_samples or nperseg)
    if nperseg < 4 or nperseg > values.size:
        raise SpectralEstimationError("nperseg_samples phải nằm trong [4, N]")
    if not (0 <= int(noverlap_samples) < nperseg):
        raise SpectralEstimationError("noverlap_samples không hợp lệ")
    if nfft < nperseg:
        raise SpectralEstimationError("nfft_samples phải >= nperseg_samples")
    if taper not in {"hann", "boxcar"}:
        raise SpectralEstimationError("Chỉ hỗ trợ taper hann hoặc boxcar")
    if detrend not in {"constant", "false", "none"}:
        raise SpectralEstimationError("Chỉ hỗ trợ detrend constant/none")
    if scaling != "density":
        raise SpectralEstimationError("Day 9 chỉ hỗ trợ scaling='density'")
    if average not in {"mean", "median"}:
        raise SpectralEstimationError("average phải là mean hoặc median")
    scipy_detrend: str | bool = False if detrend in {"false", "none"} else detrend
    frequencies, psd = welch(
        values,
        fs=sampling_rate,
        window=taper,
        nperseg=nperseg,
        noverlap=int(noverlap_samples),
        nfft=nfft,
        detrend=scipy_detrend,
        return_onesided=True,
        scaling=scaling,
        average=average,
    )
    variance = _time_domain_variance(values, detrend)
    weighted_power = _window_weighted_power(values, detrend, taper)
    full_power = integrate_uniform_psd(frequencies, psd)
    ratio = None if weighted_power <= 0 else float(full_power / weighted_power)
    return SpectralDensityEstimate(
        frequencies_hz=frequencies,
        psd_uV2_per_hz=psd,
        sampling_rate_hz=sampling_rate,
        method="welch",
        taper=taper,
        detrend=detrend,
        scaling=scaling,
        nperseg_samples=nperseg,
        noverlap_samples=int(noverlap_samples),
        nfft_samples=nfft,
        frequency_bin_spacing_hz=frequency_bin_spacing_hz(
            sampling_rate_hz=sampling_rate, nfft_samples=nfft
        ),
        rayleigh_resolution_hz=rayleigh_resolution_hz(
            sampling_rate_hz=sampling_rate, nperseg_samples=nperseg
        ),
        full_power_uV2=full_power,
        time_domain_variance_uV2=variance,
        window_weighted_power_uV2=weighted_power,
        parseval_ratio=ratio,
    )
