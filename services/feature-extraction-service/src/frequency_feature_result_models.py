"""Mô hình dữ liệu cho MDF/MNF theo từng spectral window."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from semg_core.spectral_features import FrequencyFeatureValues


_ROW_STATUSES = {"computed", "not_computed"}
_RESULT_STATUSES = {"completed", "completed_with_exclusions", "blocked"}


@dataclass(frozen=True, slots=True)
class FrequencyFeatureRow:
    frequency_feature_row_id: str
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
    values: FrequencyFeatureValues | None
    reason_codes: tuple[str, ...]
    frequency_feature_config_id: str
    spectral_estimator_id: str
    spectral_result_hash_sha256: str
    windowing_config_id: str
    preprocess_config_id: str
    source_signal_hash_sha256: str
    window_plan_hash_sha256: str
    schema_version: str = "frequency-feature-row.v0.1"

    def __post_init__(self) -> None:
        if self.status not in _ROW_STATUSES:
            raise ValueError(f"Row status không hỗ trợ: {self.status}")
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
            "frequency_feature_row_id": self.frequency_feature_row_id,
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
            "features": self.values.to_dict() if self.values else None,
            "reason_codes": list(dict.fromkeys(self.reason_codes)),
            "provenance": {
                "frequency_feature_config_id": self.frequency_feature_config_id,
                "spectral_estimator_id": self.spectral_estimator_id,
                "spectral_result_hash_sha256": self.spectral_result_hash_sha256,
                "windowing_config_id": self.windowing_config_id,
                "preprocess_config_id": self.preprocess_config_id,
                "source_signal_hash_sha256": self.source_signal_hash_sha256,
                "window_plan_hash_sha256": self.window_plan_hash_sha256,
            },
        }


@dataclass(frozen=True, slots=True)
class FrequencyFeatureExtractionResult:
    session_id: str
    status: str
    downstream_allowed: bool
    config_id: str
    inherited_spectral_status: str
    inherited_spectral_config_id: str | None
    inherited_spectral_result_hash_sha256: str | None
    analysis_band_low_hz: float | None
    analysis_band_high_hz: float | None
    reason_codes: tuple[str, ...]
    rows: tuple[FrequencyFeatureRow, ...]
    result_hash_sha256: str | None
    limitations: tuple[str, ...]
    schema_version: str = "frequency-feature-extraction-result.v0.1"

    def __post_init__(self) -> None:
        if self.status not in _RESULT_STATUSES:
            raise ValueError(f"Result status không hỗ trợ: {self.status}")
        if self.downstream_allowed and self.status == "blocked":
            raise ValueError("blocked result không được downstream_allowed=true")
        if not self.downstream_allowed and self.status != "blocked":
            raise ValueError("downstream_allowed=false phải có status=blocked")
        if self.downstream_allowed and self.computed_row_count < 1:
            raise ValueError("Kết quả downstream cần ít nhất một computed row")
        if self.status == "blocked" and self.rows:
            raise ValueError("blocked result không được có rows")
        if self.downstream_allowed and not self.result_hash_sha256:
            raise ValueError("Kết quả thành công cần result hash")

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
        return self.computed_row_count / self.total_row_count if self.total_row_count else 0.0

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
        return {
            "schema_version": self.schema_version,
            "session_id": self.session_id,
            "status": self.status,
            "downstream_allowed": bool(self.downstream_allowed),
            "config": {
                "config_id": self.config_id,
                "feature_names": ["mdf", "mnf"],
                "profile_id": "frequency_domain",
                "frequency_unit": "Hz",
                "psd_unit": "uV^2/Hz",
                "clinical_validation_status": "not_validated",
            },
            "inherited_spectral": {
                "status": self.inherited_spectral_status,
                "config_id": self.inherited_spectral_config_id,
                "result_hash_sha256": self.inherited_spectral_result_hash_sha256,
            },
            "analysis_band": (
                {
                    "low_hz": float(self.analysis_band_low_hz),
                    "high_hz": float(self.analysis_band_high_hz),
                    "unit": "Hz",
                }
                if self.analysis_band_low_hz is not None
                and self.analysis_band_high_hz is not None
                else None
            ),
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
