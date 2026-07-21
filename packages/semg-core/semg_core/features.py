"""Các hàm thuần cho đặc trưng miền thời gian sEMG.

Phạm vi Day 8:
- RMS (Root Mean Square);
- MAV (Mean Absolute Value);
- kiểm tra input một chiều, không rỗng, hữu hạn;
- tính toán ổn định số đối với biên độ lớn;
- không chuẩn hóa MVC/baseline;
- không tính MDF/MNF, slope, fatigue score hoặc kết luận lâm sàng.

Đơn vị đầu ra giữ nguyên đơn vị biên độ đầu vào. Trong pipeline MVP-0,
đầu vào canonical là microvolt (uV), vì vậy RMS và MAV cũng có đơn vị uV.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

import numpy as np


class FeatureExtractionError(ValueError):
    """Lỗi contract hoặc dữ liệu khi tính đặc trưng."""


@dataclass(frozen=True, slots=True)
class TimeDomainFeatureValues:
    """Giá trị RMS/MAV của một cửa sổ hợp lệ."""

    rms: float
    mav: float
    sample_count: int
    amplitude_unit: str

    def __post_init__(self) -> None:
        if self.sample_count < 1:
            raise FeatureExtractionError("sample_count phải >= 1")
        if not math.isfinite(self.rms) or self.rms < 0:
            raise FeatureExtractionError("RMS phải hữu hạn và không âm")
        if not math.isfinite(self.mav) or self.mav < 0:
            raise FeatureExtractionError("MAV phải hữu hạn và không âm")
        if not self.amplitude_unit:
            raise FeatureExtractionError("amplitude_unit không được rỗng")
        tolerance = max(1e-12, 1e-12 * max(self.rms, self.mav, 1.0))
        if self.rms + tolerance < self.mav:
            raise FeatureExtractionError("Bất biến RMS >= MAV bị vi phạm")

    def to_dict(self) -> dict[str, Any]:
        return {
            "rms": {"value": float(self.rms), "unit": self.amplitude_unit},
            "mav": {"value": float(self.mav), "unit": self.amplitude_unit},
            "sample_count": int(self.sample_count),
        }


def _validated_vector(samples: np.ndarray | list[float] | tuple[float, ...]) -> np.ndarray:
    values = np.asarray(samples, dtype=np.float64)
    if values.ndim != 1:
        raise FeatureExtractionError("samples phải là mảng một chiều")
    if values.size < 1:
        raise FeatureExtractionError("samples không được rỗng")
    if not np.isfinite(values).all():
        raise FeatureExtractionError("samples phải hoàn toàn hữu hạn")
    return values


def root_mean_square(samples: np.ndarray | list[float] | tuple[float, ...]) -> float:
    """Tính RMS bằng công thức ổn định theo scale.

    Thay vì bình phương trực tiếp mọi giá trị, hàm chia cho biên độ lớn nhất,
    tính RMS trên vector đã scale rồi nhân ngược lại. Cách này giảm nguy cơ
    overflow số học đối với vector hữu hạn có biên độ rất lớn.
    """

    values = _validated_vector(samples)
    scale = float(np.max(np.abs(values)))
    if scale == 0.0:
        return 0.0
    normalized = values / scale
    result = float(scale * np.sqrt(np.mean(normalized * normalized)))
    if not math.isfinite(result):
        raise FeatureExtractionError("RMS không hữu hạn")
    return result


def mean_absolute_value(
    samples: np.ndarray | list[float] | tuple[float, ...],
) -> float:
    """Tính MAV bằng công thức ổn định theo scale."""

    values = _validated_vector(samples)
    scale = float(np.max(np.abs(values)))
    if scale == 0.0:
        return 0.0
    result = float(scale * np.mean(np.abs(values) / scale))
    if not math.isfinite(result):
        raise FeatureExtractionError("MAV không hữu hạn")
    return result


def extract_time_domain_features(
    samples: np.ndarray | list[float] | tuple[float, ...],
    *,
    amplitude_unit: str = "uV",
) -> TimeDomainFeatureValues:
    """Tính đồng thời RMS và MAV cho một cửa sổ đã được xác nhận hợp lệ."""

    values = _validated_vector(samples)
    return TimeDomainFeatureValues(
        rms=root_mean_square(values),
        mav=mean_absolute_value(values),
        sample_count=int(values.size),
        amplitude_unit=amplitude_unit,
    )
