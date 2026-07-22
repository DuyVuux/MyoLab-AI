"""Các hàm thuần để mô tả xu hướng feature theo thời gian.

Phạm vi Day 11:
- OLS slope theo thời gian thực (giây), không dùng window index;
- intercept, R^2 và RMSE mô tả độ phù hợp;
- median khối đầu/cuối, absolute change và percent change;
- không p-value, không confidence interval và không suy luận mỏi cơ.

Các cửa sổ overlap không độc lập. Vì vậy R^2 ở đây là chỉ số mô tả fit,
không phải bằng chứng thống kê suy diễn.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

import numpy as np


class TrendFeatureError(ValueError):
    """Lỗi contract hoặc dữ liệu khi fit trend."""


@dataclass(frozen=True, slots=True)
class LinearTrendMetrics:
    point_count: int
    start_time_s: float
    end_time_s: float
    duration_s: float
    slope_per_s: float
    slope_per_min: float
    intercept: float
    r_squared: float
    rmse: float
    early_median: float
    late_median: float
    absolute_change: float
    percent_change: float | None
    normalized_slope_percent_per_min: float | None
    early_block_count: int
    late_block_count: int

    def __post_init__(self) -> None:
        if self.point_count < 2:
            raise TrendFeatureError("point_count phải >= 2")
        if self.duration_s <= 0:
            raise TrendFeatureError("duration_s phải > 0")
        if not (0.0 <= self.r_squared <= 1.0 + 1e-12):
            raise TrendFeatureError("R^2 phải nằm trong [0,1]")
        if self.rmse < 0 or not math.isfinite(self.rmse):
            raise TrendFeatureError("RMSE phải hữu hạn và không âm")
        for name, value in (
            ("start_time_s", self.start_time_s),
            ("end_time_s", self.end_time_s),
            ("slope_per_s", self.slope_per_s),
            ("slope_per_min", self.slope_per_min),
            ("intercept", self.intercept),
            ("early_median", self.early_median),
            ("late_median", self.late_median),
            ("absolute_change", self.absolute_change),
        ):
            if not math.isfinite(value):
                raise TrendFeatureError(f"{name} phải hữu hạn")
        for name, value in (
            ("percent_change", self.percent_change),
            ("normalized_slope_percent_per_min", self.normalized_slope_percent_per_min),
        ):
            if value is not None and not math.isfinite(value):
                raise TrendFeatureError(f"{name} phải hữu hạn hoặc null")
        if self.early_block_count < 1 or self.late_block_count < 1:
            raise TrendFeatureError("Block count phải >= 1")

    def to_dict(self, *, value_unit: str) -> dict[str, Any]:
        return {
            "point_count": int(self.point_count),
            "time_span": {
                "start_s": float(self.start_time_s),
                "end_s": float(self.end_time_s),
                "duration_s": float(self.duration_s),
            },
            "linear_fit": {
                "slope_per_s": {"value": float(self.slope_per_s), "unit": f"{value_unit}/s"},
                "slope_per_min": {"value": float(self.slope_per_min), "unit": f"{value_unit}/min"},
                "intercept": {"value": float(self.intercept), "unit": value_unit},
                "r_squared": float(min(max(self.r_squared, 0.0), 1.0)),
                "rmse": {"value": float(self.rmse), "unit": value_unit},
            },
            "early_late_summary": {
                "early_median": {"value": float(self.early_median), "unit": value_unit},
                "late_median": {"value": float(self.late_median), "unit": value_unit},
                "absolute_change": {"value": float(self.absolute_change), "unit": value_unit},
                "percent_change": (
                    {"value": float(self.percent_change), "unit": "%"}
                    if self.percent_change is not None
                    else None
                ),
                "early_block_count": int(self.early_block_count),
                "late_block_count": int(self.late_block_count),
            },
            "normalized_slope_percent_per_min": (
                {"value": float(self.normalized_slope_percent_per_min), "unit": "%/min"}
                if self.normalized_slope_percent_per_min is not None
                else None
            ),
        }


def _validated_series(
    times_s: np.ndarray | list[float] | tuple[float, ...],
    values: np.ndarray | list[float] | tuple[float, ...],
) -> tuple[np.ndarray, np.ndarray]:
    times = np.asarray(times_s, dtype=np.float64)
    y = np.asarray(values, dtype=np.float64)
    if times.ndim != 1 or y.ndim != 1:
        raise TrendFeatureError("times và values phải là vector một chiều")
    if times.size != y.size or times.size < 2:
        raise TrendFeatureError("times và values phải cùng kích thước >= 2")
    if not np.isfinite(times).all() or not np.isfinite(y).all():
        raise TrendFeatureError("times và values phải hoàn toàn hữu hạn")
    if np.any(np.diff(times) <= 0):
        raise TrendFeatureError("times phải tăng nghiêm ngặt")
    return times, y


def fit_linear_trend(
    times_s: np.ndarray | list[float] | tuple[float, ...],
    values: np.ndarray | list[float] | tuple[float, ...],
    *,
    minimum_point_count: int = 10,
    minimum_duration_s: float = 10.0,
    early_fraction: float = 0.2,
    late_fraction: float = 0.2,
    minimum_reference_abs: float = 1.0e-12,
) -> LinearTrendMetrics:
    """Fit OLS và tóm tắt early/late trên một feature series."""

    times, y = _validated_series(times_s, values)
    if minimum_point_count < 2:
        raise TrendFeatureError("minimum_point_count phải >= 2")
    if times.size < minimum_point_count:
        raise TrendFeatureError("Không đủ điểm để fit trend")
    duration = float(times[-1] - times[0])
    if not math.isfinite(duration) or duration < float(minimum_duration_s):
        raise TrendFeatureError("Khoảng thời gian không đủ để fit trend")
    for name, fraction in (("early_fraction", early_fraction), ("late_fraction", late_fraction)):
        if not math.isfinite(fraction) or not (0.0 < fraction <= 0.5):
            raise TrendFeatureError(f"{name} phải nằm trong (0, 0.5]")
    if early_fraction + late_fraction > 1.0:
        raise TrendFeatureError("Tổng early/late fraction không được > 1")

    x_centered = times - float(np.mean(times, dtype=np.float64))
    y_mean = float(np.mean(y, dtype=np.float64))
    denominator = float(np.dot(x_centered, x_centered))
    if denominator <= 0 or not math.isfinite(denominator):
        raise TrendFeatureError("Trục thời gian không đủ biến thiên")
    slope = float(np.dot(x_centered, y - y_mean) / denominator)
    intercept = float(y_mean - slope * float(np.mean(times, dtype=np.float64)))
    predicted = intercept + slope * times
    residual = y - predicted
    sse = float(np.dot(residual, residual))
    centered_y = y - y_mean
    sst = float(np.dot(centered_y, centered_y))
    if sst <= max(1e-30, abs(y_mean) * 1e-30):
        r_squared = 1.0 if sse <= 1e-24 else 0.0
    else:
        r_squared = float(1.0 - sse / sst)
        r_squared = float(np.clip(r_squared, 0.0, 1.0))
    rmse = float(np.sqrt(np.mean(residual * residual, dtype=np.float64)))

    early_count = max(1, int(math.ceil(times.size * float(early_fraction))))
    late_count = max(1, int(math.ceil(times.size * float(late_fraction))))
    early = float(np.median(y[:early_count]))
    late = float(np.median(y[-late_count:]))
    change = float(late - early)
    reference = abs(early)
    if reference <= float(minimum_reference_abs):
        percent_change = None
        normalized_slope = None
    else:
        percent_change = float(100.0 * change / reference)
        normalized_slope = float(100.0 * slope * 60.0 / reference)

    return LinearTrendMetrics(
        point_count=int(times.size),
        start_time_s=float(times[0]),
        end_time_s=float(times[-1]),
        duration_s=duration,
        slope_per_s=slope,
        slope_per_min=float(slope * 60.0),
        intercept=intercept,
        r_squared=r_squared,
        rmse=rmse,
        early_median=early,
        late_median=late,
        absolute_change=change,
        percent_change=percent_change,
        normalized_slope_percent_per_min=normalized_slope,
        early_block_count=early_count,
        late_block_count=late_count,
    )
