"""Các hàm thuần cho segmentation và fixed-window planning của sEMG.

Phạm vi Day 7:
- chuyển thời lượng giây sang số mẫu một cách có kiểm soát;
- tính hop từ tỷ lệ overlap;
- tạo cửa sổ full-length theo khoảng half-open [start, end);
- đánh giá tính hợp lệ của từng cửa sổ dựa trên finite values và valid mask;
- không trích xuất RMS/MAV/MDF/MNF;
- không áp dụng Hann taper tại tầng windowing.

Tầng này tạo *kế hoạch chỉ số* (index plan), không sao chép toàn bộ dữ liệu
cửa sổ và không tạo kết luận mỏi cơ.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Any, Iterable

import numpy as np


class WindowingError(ValueError):
    """Lỗi cấu hình hoặc hình học cửa sổ."""


@dataclass(frozen=True, slots=True)
class WindowGeometry:
    """Hình học một cửa sổ full-length theo quy ước half-open."""

    window_index: int
    phase_id: str
    start_sample: int
    end_sample_exclusive: int
    start_time_s: float
    end_time_exclusive_s: float
    center_time_s: float
    sample_count: int

    @property
    def window_id(self) -> str:
        return f"W{self.window_index:04d}"

    def to_dict(self) -> dict[str, int | float | str]:
        return {
            "window_id": self.window_id,
            "window_index": int(self.window_index),
            "phase_id": self.phase_id,
            "start_sample": int(self.start_sample),
            "end_sample_exclusive": int(self.end_sample_exclusive),
            "start_time_s": float(self.start_time_s),
            "end_time_exclusive_s": float(self.end_time_exclusive_s),
            "center_time_s": float(self.center_time_s),
            "sample_count": int(self.sample_count),
        }


@dataclass(frozen=True, slots=True)
class WindowValidity:
    """Kết quả đánh giá một channel-window, không chứa raw samples."""

    window_index: int
    status: str
    valid_sample_count: int
    valid_sample_ratio: float
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.status not in {"valid", "invalid"}:
            raise WindowingError(f"Window status không hỗ trợ: {self.status}")
        if self.valid_sample_count < 0:
            raise WindowingError("valid_sample_count không được âm")
        if not (0.0 <= self.valid_sample_ratio <= 1.0):
            raise WindowingError("valid_sample_ratio phải nằm trong [0, 1]")

    @property
    def window_id(self) -> str:
        return f"W{self.window_index:04d}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "window_id": self.window_id,
            "window_index": int(self.window_index),
            "status": self.status,
            "valid_sample_count": int(self.valid_sample_count),
            "valid_sample_ratio": float(self.valid_sample_ratio),
            "reason_codes": list(dict.fromkeys(self.reason_codes)),
        }


def seconds_to_exact_samples(
    duration_s: float,
    sampling_rate_hz: float,
    *,
    absolute_tolerance_samples: float = 1e-9,
) -> int:
    """Đổi giây sang số mẫu và từ chối cấu hình không khớp lưới mẫu.

    Ví dụ 1.0 s tại 1000 Hz -> 1000 mẫu.
    0.333 s tại 1000 Hz -> 333 mẫu nếu tích gần số nguyên trong tolerance.
    """

    if not math.isfinite(duration_s) or duration_s <= 0:
        raise WindowingError("duration_s phải dương và hữu hạn")
    if not math.isfinite(sampling_rate_hz) or sampling_rate_hz <= 0:
        raise WindowingError("sampling_rate_hz phải dương và hữu hạn")

    exact = duration_s * sampling_rate_hz
    rounded = int(round(exact))
    if rounded < 1:
        raise WindowingError("Cửa sổ phải có ít nhất một mẫu")
    if abs(exact - rounded) > absolute_tolerance_samples:
        raise WindowingError(
            "duration_s × sampling_rate_hz không phải số nguyên mẫu: "
            f"duration_s={duration_s}, Fs={sampling_rate_hz}, exact={exact}"
        )
    return rounded


def overlap_to_hop_samples(
    window_size_samples: int,
    overlap_fraction: float,
    *,
    absolute_tolerance_samples: float = 1e-9,
) -> int:
    """Tính hop size từ overlap fraction.

    H = L × (1 - overlap).
    """

    if not isinstance(window_size_samples, int) or window_size_samples < 1:
        raise WindowingError("window_size_samples phải là số nguyên >= 1")
    if not math.isfinite(overlap_fraction) or not (0.0 <= overlap_fraction < 1.0):
        raise WindowingError("overlap_fraction phải nằm trong [0, 1)")

    exact = window_size_samples * (1.0 - overlap_fraction)
    rounded = int(round(exact))
    if rounded < 1:
        raise WindowingError("Hop size phải có ít nhất một mẫu")
    if abs(exact - rounded) > absolute_tolerance_samples:
        raise WindowingError(
            "Overlap tạo hop không nguyên mẫu: "
            f"L={window_size_samples}, overlap={overlap_fraction}, exact_hop={exact}"
        )
    return rounded


def full_window_count(
    phase_sample_count: int,
    window_size_samples: int,
    hop_size_samples: int,
) -> int:
    """Số cửa sổ full-length khi không cho partial final window."""

    for name, value in (
        ("phase_sample_count", phase_sample_count),
        ("window_size_samples", window_size_samples),
        ("hop_size_samples", hop_size_samples),
    ):
        if not isinstance(value, int) or value < 0:
            raise WindowingError(f"{name} phải là số nguyên không âm")
    if window_size_samples < 1 or hop_size_samples < 1:
        raise WindowingError("window_size_samples và hop_size_samples phải >= 1")
    if phase_sample_count < window_size_samples:
        return 0
    return ((phase_sample_count - window_size_samples) // hop_size_samples) + 1


def _exclusive_time(
    time_s: np.ndarray,
    end_sample_exclusive: int,
    sampling_rate_hz: float,
) -> float:
    if end_sample_exclusive <= 0:
        raise WindowingError("end_sample_exclusive phải > 0")
    if end_sample_exclusive > time_s.size:
        raise WindowingError("Cửa sổ vượt quá time axis")
    return float(time_s[end_sample_exclusive - 1] + (1.0 / sampling_rate_hz))


def build_fixed_window_geometries(
    *,
    time_s: np.ndarray,
    sampling_rate_hz: float,
    phase_id: str,
    phase_start_sample: int,
    phase_end_sample_exclusive: int,
    window_size_samples: int,
    hop_size_samples: int,
) -> tuple[WindowGeometry, ...]:
    """Tạo các cửa sổ full-length, không vượt phase boundary."""

    time_axis = np.asarray(time_s, dtype=np.float64)
    if time_axis.ndim != 1 or time_axis.size < 1:
        raise WindowingError("time_s phải là mảng một chiều không rỗng")
    if not np.isfinite(time_axis).all():
        raise WindowingError("time_s phải hoàn toàn hữu hạn")
    if phase_start_sample < 0:
        raise WindowingError("phase_start_sample không được âm")
    if phase_end_sample_exclusive > time_axis.size:
        raise WindowingError("phase_end_sample_exclusive vượt time axis")
    if phase_end_sample_exclusive <= phase_start_sample:
        raise WindowingError("Phase phải có ít nhất một mẫu")

    phase_count = phase_end_sample_exclusive - phase_start_sample
    count = full_window_count(phase_count, window_size_samples, hop_size_samples)
    geometries: list[WindowGeometry] = []

    for index in range(count):
        start = phase_start_sample + index * hop_size_samples
        end = start + window_size_samples
        if end > phase_end_sample_exclusive:
            raise AssertionError("Internal error: full window vượt phase boundary")
        start_time = float(time_axis[start])
        end_time = _exclusive_time(time_axis, end, sampling_rate_hz)
        geometries.append(
            WindowGeometry(
                window_index=index,
                phase_id=phase_id,
                start_sample=start,
                end_sample_exclusive=end,
                start_time_s=start_time,
                end_time_exclusive_s=end_time,
                center_time_s=(start_time + end_time) / 2.0,
                sample_count=window_size_samples,
            )
        )
    return tuple(geometries)


def assess_window_validity(
    *,
    samples: np.ndarray,
    valid_sample_mask: np.ndarray,
    geometries: Iterable[WindowGeometry],
    minimum_valid_sample_ratio: float,
) -> tuple[WindowValidity, ...]:
    """Đánh giá từng cửa sổ theo finite samples và mask từ preprocessing."""

    values = np.asarray(samples, dtype=np.float64)
    mask = np.asarray(valid_sample_mask, dtype=np.bool_)
    if values.ndim != 1 or mask.ndim != 1:
        raise WindowingError("samples và valid_sample_mask phải là mảng một chiều")
    if values.size != mask.size:
        raise WindowingError("samples và valid_sample_mask phải có cùng chiều dài")
    if not math.isfinite(minimum_valid_sample_ratio) or not (
        0.0 <= minimum_valid_sample_ratio <= 1.0
    ):
        raise WindowingError("minimum_valid_sample_ratio phải nằm trong [0, 1]")

    output: list[WindowValidity] = []
    for geometry in geometries:
        start = geometry.start_sample
        end = geometry.end_sample_exclusive
        if start < 0 or end > values.size or end <= start:
            raise WindowingError("Window geometry không hợp lệ với channel array")

        window_values = values[start:end]
        window_mask = mask[start:end]
        finite_mask = np.isfinite(window_values)
        combined = window_mask & finite_mask
        valid_count = int(np.count_nonzero(combined))
        ratio = valid_count / geometry.sample_count

        reasons: list[str] = []
        if not finite_mask.all():
            reasons.append("WINDOW_CONTAINS_NONFINITE")
        if not window_mask.all():
            reasons.append("WINDOW_INTERSECTS_INVALID_SAMPLE_MASK")
        if ratio < minimum_valid_sample_ratio:
            reasons.append("WINDOW_VALID_SAMPLE_RATIO_BELOW_THRESHOLD")

        output.append(
            WindowValidity(
                window_index=geometry.window_index,
                status="invalid" if reasons else "valid",
                valid_sample_count=valid_count,
                valid_sample_ratio=float(ratio),
                reason_codes=tuple(reasons),
            )
        )
    return tuple(output)


def window_view(samples: np.ndarray, geometry: WindowGeometry) -> np.ndarray:
    """Trả về read-only view của một cửa sổ; không copy nếu NumPy cho phép."""

    values = np.asarray(samples, dtype=np.float64)
    if values.ndim != 1:
        raise WindowingError("samples phải là mảng một chiều")
    if geometry.start_sample < 0 or geometry.end_sample_exclusive > values.size:
        raise WindowingError("Window geometry vượt array")
    view = values[geometry.start_sample : geometry.end_sample_exclusive]
    view.setflags(write=False)
    return view


def window_plan_sha256(payload: dict[str, Any]) -> str:
    """Hash canonical JSON cho geometry/validity plan, không hash raw samples."""

    canonical = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()
