"""Các hàm thuần để tính MDF và MNF từ PSD đã được kiểm chứng.

Phạm vi Day 10:
- Mean Frequency (MNF) là trọng tâm phổ theo công suất;
- Median Frequency (MDF) là phân vị 50% của công suất phổ;
- đầu vào là trục tần số tăng đều và PSD không âm trong dải phân tích;
- không fit slope, không suy luận mỏi cơ, không tạo FRS hoặc khuyến nghị.

Với PSD density có đơn vị uV^2/Hz và khoảng bin ``df``, khối lượng công
suất của bin là ``PSD[k] * df``. MNF có đơn vị Hz. MDF dùng nội suy tuyến
tính bên trong bin theo quy ước bin-centered, sau đó được chặn trong dải
frequency axis đầu vào.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

import numpy as np


class FrequencyFeatureError(ValueError):
    """Lỗi contract hoặc dữ liệu khi tính MDF/MNF."""


@dataclass(frozen=True, slots=True)
class FrequencyFeatureValues:
    """MDF/MNF của một spectral window hợp lệ."""

    mdf_hz: float
    mnf_hz: float
    band_power_uV2: float
    frequency_bin_count: int
    frequency_bin_spacing_hz: float
    median_method: str = "cdf_bin_edge_linear_v0.1"
    mean_method: str = "power_weighted_centroid_v0.1"

    def __post_init__(self) -> None:
        for name, value in (
            ("mdf_hz", self.mdf_hz),
            ("mnf_hz", self.mnf_hz),
            ("band_power_uV2", self.band_power_uV2),
            ("frequency_bin_spacing_hz", self.frequency_bin_spacing_hz),
        ):
            if not math.isfinite(value):
                raise FrequencyFeatureError(f"{name} phải hữu hạn")
        if self.mdf_hz < 0 or self.mnf_hz < 0:
            raise FrequencyFeatureError("MDF/MNF không được âm")
        if self.band_power_uV2 <= 0:
            raise FrequencyFeatureError("band_power_uV2 phải > 0")
        if self.frequency_bin_count < 2:
            raise FrequencyFeatureError("frequency_bin_count phải >= 2")
        if self.frequency_bin_spacing_hz <= 0:
            raise FrequencyFeatureError("frequency_bin_spacing_hz phải > 0")
        if not self.median_method or not self.mean_method:
            raise FrequencyFeatureError("Tên phương pháp không được rỗng")

    def to_dict(self) -> dict[str, Any]:
        return {
            "mdf": {"value": float(self.mdf_hz), "unit": "Hz"},
            "mnf": {"value": float(self.mnf_hz), "unit": "Hz"},
            "band_power": {"value": float(self.band_power_uV2), "unit": "uV^2"},
            "frequency_bin_count": int(self.frequency_bin_count),
            "frequency_bin_spacing_hz": float(self.frequency_bin_spacing_hz),
            "methods": {
                "mdf": self.median_method,
                "mnf": self.mean_method,
            },
        }


def _validate_axis_and_psd(
    frequencies_hz: np.ndarray | list[float] | tuple[float, ...],
    psd_uV2_per_hz: np.ndarray | list[float] | tuple[float, ...],
) -> tuple[np.ndarray, np.ndarray, float]:
    frequencies = np.asarray(frequencies_hz, dtype=np.float64)
    psd = np.asarray(psd_uV2_per_hz, dtype=np.float64)
    if frequencies.ndim != 1 or psd.ndim != 1:
        raise FrequencyFeatureError("frequency và PSD phải là vector một chiều")
    if frequencies.size != psd.size or frequencies.size < 2:
        raise FrequencyFeatureError("frequency và PSD phải cùng kích thước >= 2")
    if not np.isfinite(frequencies).all() or not np.isfinite(psd).all():
        raise FrequencyFeatureError("frequency và PSD phải hoàn toàn hữu hạn")
    if np.any(np.diff(frequencies) <= 0):
        raise FrequencyFeatureError("frequency axis phải tăng nghiêm ngặt")
    tolerance = max(1e-15, float(np.max(np.abs(psd))) * 1e-12)
    if np.any(psd < -tolerance):
        raise FrequencyFeatureError("PSD không được âm")
    psd = np.maximum(psd, 0.0)
    diffs = np.diff(frequencies)
    df = float(np.median(diffs))
    if not math.isfinite(df) or df <= 0:
        raise FrequencyFeatureError("Khoảng cách bin phải hữu hạn và > 0")
    if float(np.max(np.abs(diffs - df))) > max(1e-12, abs(df) * 1e-9):
        raise FrequencyFeatureError("Day 10 yêu cầu frequency axis tăng đều")
    return frequencies, psd, df


def mean_frequency_hz(
    frequencies_hz: np.ndarray | list[float] | tuple[float, ...],
    psd_uV2_per_hz: np.ndarray | list[float] | tuple[float, ...],
    *,
    minimum_power_uV2: float = 0.0,
) -> float:
    """Tính MNF là trọng tâm công suất của PSD trong dải đầu vào."""

    frequencies, psd, df = _validate_axis_and_psd(
        frequencies_hz, psd_uV2_per_hz
    )
    masses = psd * df
    total = float(np.sum(masses, dtype=np.float64))
    if not math.isfinite(total) or total <= float(minimum_power_uV2):
        raise FrequencyFeatureError("Tổng công suất không đủ để tính MNF")
    result = float(np.sum(frequencies * masses, dtype=np.float64) / total)
    if not math.isfinite(result):
        raise FrequencyFeatureError("MNF không hữu hạn")
    return result


def median_frequency_hz(
    frequencies_hz: np.ndarray | list[float] | tuple[float, ...],
    psd_uV2_per_hz: np.ndarray | list[float] | tuple[float, ...],
    *,
    quantile: float = 0.5,
    minimum_power_uV2: float = 0.0,
) -> float:
    """Tính MDF bằng CDF công suất và nội suy tuyến tính trong bin.

    Mỗi PSD sample được xem là mật độ tại tâm một bin rộng ``df``. Sau khi
    tìm bin chứa quantile, vị trí được nội suy từ cạnh trái của bin. Kết quả
    cuối cùng được chặn trong [f_min, f_max] để tránh trả giá trị ngoài dải
    khi quantile nằm ở bin biên.
    """

    frequencies, psd, df = _validate_axis_and_psd(
        frequencies_hz, psd_uV2_per_hz
    )
    q = float(quantile)
    if not math.isfinite(q) or not (0.0 < q < 1.0):
        raise FrequencyFeatureError("quantile phải nằm trong (0, 1)")
    masses = psd * df
    total = float(np.sum(masses, dtype=np.float64))
    if not math.isfinite(total) or total <= float(minimum_power_uV2):
        raise FrequencyFeatureError("Tổng công suất không đủ để tính MDF")
    cumulative = np.cumsum(masses, dtype=np.float64)
    target = q * total
    index = int(np.searchsorted(cumulative, target, side="left"))
    index = min(max(index, 0), frequencies.size - 1)
    previous = float(cumulative[index - 1]) if index > 0 else 0.0
    bin_mass = float(masses[index])
    if bin_mass <= 0:
        # Trường hợp rất hiếm do plateau số học; tìm bin dương gần nhất bên phải.
        positive = np.flatnonzero(masses[index:] > 0)
        if positive.size == 0:
            raise FrequencyFeatureError("Không tìm được bin dương cho MDF")
        index += int(positive[0])
        previous = float(cumulative[index - 1]) if index > 0 else 0.0
        bin_mass = float(masses[index])
    fraction = (target - previous) / bin_mass
    fraction = float(np.clip(fraction, 0.0, 1.0))
    left_edge = float(frequencies[index] - 0.5 * df)
    result = left_edge + fraction * df
    result = float(np.clip(result, frequencies[0], frequencies[-1]))
    if not math.isfinite(result):
        raise FrequencyFeatureError("MDF không hữu hạn")
    return result


def extract_frequency_features(
    frequencies_hz: np.ndarray | list[float] | tuple[float, ...],
    psd_uV2_per_hz: np.ndarray | list[float] | tuple[float, ...],
    *,
    minimum_power_uV2: float = 0.0,
    median_quantile: float = 0.5,
) -> FrequencyFeatureValues:
    frequencies, psd, df = _validate_axis_and_psd(
        frequencies_hz, psd_uV2_per_hz
    )
    band_power = float(np.sum(psd * df, dtype=np.float64))
    if band_power <= float(minimum_power_uV2):
        raise FrequencyFeatureError("Tổng công suất không đủ để tính MDF/MNF")
    mdf = median_frequency_hz(
        frequencies,
        psd,
        quantile=median_quantile,
        minimum_power_uV2=minimum_power_uV2,
    )
    mnf = mean_frequency_hz(
        frequencies,
        psd,
        minimum_power_uV2=minimum_power_uV2,
    )
    lower = float(frequencies[0])
    upper = float(frequencies[-1])
    tolerance = max(1e-12, df * 1e-9)
    if not (lower - tolerance <= mdf <= upper + tolerance):
        raise FrequencyFeatureError("MDF nằm ngoài dải phân tích")
    if not (lower - tolerance <= mnf <= upper + tolerance):
        raise FrequencyFeatureError("MNF nằm ngoài dải phân tích")
    return FrequencyFeatureValues(
        mdf_hz=mdf,
        mnf_hz=mnf,
        band_power_uV2=band_power,
        frequency_bin_count=int(frequencies.size),
        frequency_bin_spacing_hz=df,
    )
