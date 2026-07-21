"""Mô hình dữ liệu cho kết quả ước lượng PSD theo từng cửa sổ."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any


_ROW_STATUSES = {"computed", "not_computed"}
_RESULT_STATUSES = {"completed", "completed_with_exclusions", "blocked"}


@dataclass(frozen=True, slots=True)
class SpectralWindowValues:
    """PSD trong dải phân tích, dùng chung frequency axis ở cấp result."""

    psd_uV2_per_hz: tuple[float, ...]
    band_power_uV2: float
    full_power_uV2: float
    time_domain_variance_uV2: float
    window_weighted_power_uV2: float
    parseval_ratio: float | None
    peak_frequency_hz: float | None
    qa_flags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        values = tuple(float(item) for item in self.psd_uV2_per_hz)
        if len(values) < 2:
            raise ValueError("PSD cần ít nhất 2 bins")
        if any(not math.isfinite(item) or item < 0 for item in values):
            raise ValueError("PSD values phải hữu hạn và không âm")
        for name, value in (
            ("band_power_uV2", self.band_power_uV2),
            ("full_power_uV2", self.full_power_uV2),
            ("time_domain_variance_uV2", self.time_domain_variance_uV2),
            ("window_weighted_power_uV2", self.window_weighted_power_uV2),
        ):
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} phải hữu hạn và không âm")
        if self.band_power_uV2 > self.full_power_uV2 + max(1e-12, self.full_power_uV2 * 1e-9):
            raise ValueError("band power không được lớn hơn full power")
        if self.parseval_ratio is not None:
            if not math.isfinite(self.parseval_ratio) or self.parseval_ratio < 0:
                raise ValueError("parseval_ratio phải hữu hạn và không âm")
        if self.peak_frequency_hz is not None:
            if not math.isfinite(self.peak_frequency_hz) or self.peak_frequency_hz < 0:
                raise ValueError("peak_frequency_hz phải hữu hạn và không âm")
        object.__setattr__(self, "psd_uV2_per_hz", values)
        object.__setattr__(self, "qa_flags", tuple(dict.fromkeys(self.qa_flags)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "psd": {
                "values": list(self.psd_uV2_per_hz),
                "unit": "uV^2/Hz",
            },
            "band_power": {
                "value": float(self.band_power_uV2),
                "unit": "uV^2",
            },
            "full_power": {
                "value": float(self.full_power_uV2),
                "unit": "uV^2",
            },
            "time_domain_variance": {
                "value": float(self.time_domain_variance_uV2),
                "unit": "uV^2",
            },
            "window_weighted_power": {
                "value": float(self.window_weighted_power_uV2),
                "unit": "uV^2",
            },
            "parseval_ratio": (
                float(self.parseval_ratio) if self.parseval_ratio is not None else None
            ),
            "qa_flags": list(self.qa_flags),
            "peak_frequency": {
                "value": (
                    float(self.peak_frequency_hz)
                    if self.peak_frequency_hz is not None
                    else None
                ),
                "unit": "Hz",
                "purpose": "qa_only_not_fatigue_feature",
            },
        }


@dataclass(frozen=True, slots=True)
class SpectralWindowRow:
    spectral_row_id: str
    session_id: str
    channel_id: str
    muscle: str
    side: str
    role: str
    phase_id: str
    profile_id: str
    window_id: str
    window_index: int
    start_sample: int
    end_sample_exclusive: int
    start_time_s: float
    end_time_exclusive_s: float
    center_time_s: float
    sample_count: int
    status: str
    values: SpectralWindowValues | None
    reason_codes: tuple[str, ...]
    spectral_estimator_id: str
    windowing_config_id: str
    preprocess_config_id: str
    source_signal_hash_sha256: str
    window_plan_hash_sha256: str
    schema_version: str = "spectral-window-row.v0.1"

    def __post_init__(self) -> None:
        if self.status not in _ROW_STATUSES:
            raise ValueError(f"Spectral row status không hỗ trợ: {self.status}")
        if self.window_index < 0:
            raise ValueError("window_index không được âm")
        if self.end_sample_exclusive <= self.start_sample:
            raise ValueError("Window boundary không hợp lệ")
        if self.sample_count != self.end_sample_exclusive - self.start_sample:
            raise ValueError("sample_count không khớp boundary")
        if self.status == "computed" and self.values is None:
            raise ValueError("computed row phải có values")
        if self.status == "not_computed" and self.values is not None:
            raise ValueError("not_computed row không được có values")
        if self.status == "computed" and self.reason_codes:
            raise ValueError("computed row không được có reason_codes")
        if self.status == "not_computed" and not self.reason_codes:
            raise ValueError("not_computed row phải có reason_codes")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "spectral_row_id": self.spectral_row_id,
            "session_id": self.session_id,
            "channel": {
                "channel_id": self.channel_id,
                "muscle": self.muscle,
                "side": self.side,
                "role": self.role,
            },
            "phase_id": self.phase_id,
            "profile_id": self.profile_id,
            "window": {
                "window_id": self.window_id,
                "window_index": int(self.window_index),
                "start_sample": int(self.start_sample),
                "end_sample_exclusive": int(self.end_sample_exclusive),
                "start_time_s": float(self.start_time_s),
                "end_time_exclusive_s": float(self.end_time_exclusive_s),
                "center_time_s": float(self.center_time_s),
                "sample_count": int(self.sample_count),
            },
            "status": self.status,
            "spectral": self.values.to_dict() if self.values else None,
            "reason_codes": list(dict.fromkeys(self.reason_codes)),
            "provenance": {
                "spectral_estimator_id": self.spectral_estimator_id,
                "windowing_config_id": self.windowing_config_id,
                "preprocess_config_id": self.preprocess_config_id,
                "source_signal_hash_sha256": self.source_signal_hash_sha256,
                "window_plan_hash_sha256": self.window_plan_hash_sha256,
            },
        }


@dataclass(frozen=True, slots=True)
class SpectralEstimationResult:
    session_id: str
    status: str
    downstream_allowed: bool
    config_id: str
    inherited_windowing_status: str
    inherited_windowing_config_id: str | None
    inherited_window_plan_hash_sha256: str | None
    frequency_axis_hz: tuple[float, ...] | None
    estimator_metadata: dict[str, Any] | None
    reason_codes: tuple[str, ...]
    rows: tuple[SpectralWindowRow, ...]
    result_hash_sha256: str | None
    limitations: tuple[str, ...]
    schema_version: str = "spectral-estimation-result.v0.1"

    def __post_init__(self) -> None:
        if self.status not in _RESULT_STATUSES:
            raise ValueError(f"Result status không hỗ trợ: {self.status}")
        if self.downstream_allowed and self.status == "blocked":
            raise ValueError("blocked result không được downstream_allowed=true")
        if not self.downstream_allowed and self.status != "blocked":
            raise ValueError("downstream_allowed=false phải có status=blocked")
        if self.downstream_allowed and self.computed_row_count < 1:
            raise ValueError("downstream_allowed=true cần ít nhất một computed row")
        if self.status == "blocked" and self.rows:
            raise ValueError("blocked result không được có rows")
        if self.downstream_allowed and not self.result_hash_sha256:
            raise ValueError("Kết quả thành công phải có result_hash_sha256")
        if self.downstream_allowed:
            if self.frequency_axis_hz is None or self.estimator_metadata is None:
                raise ValueError("Kết quả thành công cần frequency axis và metadata")
            axis = tuple(float(item) for item in self.frequency_axis_hz)
            if len(axis) < 2:
                raise ValueError("frequency axis cần ít nhất 2 bins")
            if any(not math.isfinite(item) or item < 0 for item in axis):
                raise ValueError("frequency axis phải hữu hạn và không âm")
            if any(b <= a for a, b in zip(axis, axis[1:])):
                raise ValueError("frequency axis phải tăng nghiêm ngặt")
            for row in self.rows:
                if row.values is not None and len(row.values.psd_uV2_per_hz) != len(axis):
                    raise ValueError("PSD row không khớp shared frequency axis")
            object.__setattr__(self, "frequency_axis_hz", axis)

    @property
    def total_row_count(self) -> int:
        return len(self.rows)

    @property
    def computed_row_count(self) -> int:
        return sum(row.status == "computed" for row in self.rows)

    @property
    def not_computed_row_count(self) -> int:
        return self.total_row_count - self.computed_row_count

    @property
    def usable_window_ratio(self) -> float:
        if self.total_row_count == 0:
            return 0.0
        return self.computed_row_count / self.total_row_count

    @property
    def channel_count(self) -> int:
        return len({row.channel_id for row in self.rows})

    @property
    def reason_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for row in self.rows:
            for code in row.reason_codes:
                counts[code] = counts.get(code, 0) + 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        axis = self.frequency_axis_hz
        metadata = dict(self.estimator_metadata or {})
        return {
            "schema_version": self.schema_version,
            "session_id": self.session_id,
            "status": self.status,
            "downstream_allowed": bool(self.downstream_allowed),
            "config": {
                "config_id": self.config_id,
                "profile_id": "frequency_domain",
                "canonical_amplitude_unit": "uV",
                "psd_unit": "uV^2/Hz",
                "mdf_mnf_computed": False,
            },
            "inherited_windowing": {
                "status": self.inherited_windowing_status,
                "config_id": self.inherited_windowing_config_id,
                "plan_hash_sha256": self.inherited_window_plan_hash_sha256,
            },
            "frequency_axis": (
                {
                    "values": list(axis),
                    "unit": "Hz",
                    "bin_count": len(axis),
                    "lower_hz": float(axis[0]),
                    "upper_hz": float(axis[-1]),
                    "bin_spacing_hz": float(metadata.get("frequency_bin_spacing_hz")),
                    "rayleigh_resolution_hz": float(metadata.get("rayleigh_resolution_hz")),
                }
                if axis is not None
                else None
            ),
            "estimator": metadata or None,
            "summary": {
                "channel_count": int(self.channel_count),
                "total_row_count": int(self.total_row_count),
                "computed_row_count": int(self.computed_row_count),
                "not_computed_row_count": int(self.not_computed_row_count),
                "usable_window_ratio": float(self.usable_window_ratio),
                "not_computed_reason_counts": self.reason_counts,
            },
            "reason_codes": list(dict.fromkeys(self.reason_codes)),
            "result_hash_sha256": self.result_hash_sha256,
            "rows": [row.to_dict() for row in self.rows],
            "limitations": list(self.limitations),
        }
