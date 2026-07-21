"""Mô hình kết quả Windowing v0.1 với hai profile theo protocol."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

import numpy as np

from preprocess_result_models import PreprocessedSignal
from semg_core.windowing import WindowGeometry, WindowValidity, window_view


_ALLOWED_STATUSES = {"completed", "blocked"}


@dataclass(frozen=True, slots=True)
class ChannelWindowPlan:
    channel_id: str
    muscle: str
    side: str
    role: str
    windows: tuple[WindowValidity, ...]

    @property
    def valid_window_count(self) -> int:
        return sum(item.status == "valid" for item in self.windows)

    @property
    def invalid_window_count(self) -> int:
        return len(self.windows) - self.valid_window_count

    @property
    def reason_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for window in self.windows:
            for code in window.reason_codes:
                counts[code] = counts.get(code, 0) + 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        return {
            "channel_id": self.channel_id,
            "muscle": self.muscle,
            "side": self.side,
            "role": self.role,
            "window_count": len(self.windows),
            "valid_window_count": self.valid_window_count,
            "invalid_window_count": self.invalid_window_count,
            "feature_extraction_eligible": self.valid_window_count > 0,
            "invalid_reason_counts": self.reason_counts,
            "windows": [item.to_dict() for item in self.windows],
        }


@dataclass(frozen=True, slots=True)
class WindowProfilePlan:
    profile_id: str
    purpose: str
    window_size_samples: int
    hop_size_samples: int
    overlap_fraction: float
    remainder_samples: int
    geometries: tuple[WindowGeometry, ...]
    channels: Mapping[str, ChannelWindowPlan]

    def __post_init__(self) -> None:
        object.__setattr__(self, "geometries", tuple(self.geometries))
        object.__setattr__(self, "channels", MappingProxyType(dict(self.channels)))
        if not self.geometries:
            raise ValueError(f"Profile {self.profile_id} cần ít nhất một geometry")
        indices = [item.window_index for item in self.geometries]
        if indices != list(range(len(self.geometries))):
            raise ValueError("Window indices phải liên tục từ 0 trong mỗi profile")
        for channel in self.channels.values():
            if len(channel.windows) != len(self.geometries):
                raise ValueError("Mỗi channel phải có validity cho mọi geometry")

    @property
    def window_count(self) -> int:
        return len(self.geometries)

    def to_dict(self, *, spectral_taper_default: str) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "purpose": self.purpose,
            "windowing": {
                "window_size_samples": int(self.window_size_samples),
                "hop_size_samples": int(self.hop_size_samples),
                "overlap_fraction": float(self.overlap_fraction),
                "window_count": int(self.window_count),
                "remainder_samples": int(self.remainder_samples),
                "boundary_convention": "half_open",
                "partial_windows_included": False,
                "spectral_taper_default": spectral_taper_default,
                "taper_applied_during_windowing": False,
            },
            "geometries": [item.to_dict() for item in self.geometries],
            "channels": [
                self.channels[key].to_dict() for key in sorted(self.channels)
            ],
        }


@dataclass(frozen=True, slots=True)
class WindowedSignalPlan:
    """Hai profile geometry tham chiếu cùng một PreprocessedSignal."""

    source_signal: PreprocessedSignal
    phase_id: str
    phase_start_sample: int
    phase_end_sample_exclusive: int
    profiles: Mapping[str, WindowProfilePlan]
    windowing_config_id: str
    plan_hash_sha256: str
    spectral_taper_default: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "profiles", MappingProxyType(dict(self.profiles)))
        if set(self.profiles) != {"time_domain", "frequency_domain"}:
            raise ValueError("Plan cần đúng hai profile time_domain/frequency_domain")

    @property
    def phase_sample_count(self) -> int:
        return self.phase_end_sample_exclusive - self.phase_start_sample

    def get_window_samples(
        self,
        profile_id: str,
        channel_id: str,
        window_index: int,
    ) -> np.ndarray:
        if profile_id not in self.profiles:
            raise KeyError(f"Không có profile_id={profile_id}")
        if channel_id not in self.source_signal.channels:
            raise KeyError(f"Không có channel_id={channel_id}")
        profile = self.profiles[profile_id]
        if not (0 <= window_index < profile.window_count):
            raise IndexError("window_index ngoài phạm vi")
        geometry = profile.geometries[window_index]
        samples = self.source_signal.channels[channel_id].samples_uV
        return window_view(samples, geometry)

    def get_window_validity(
        self,
        profile_id: str,
        channel_id: str,
        window_index: int,
    ) -> WindowValidity:
        if profile_id not in self.profiles:
            raise KeyError(f"Không có profile_id={profile_id}")
        profile = self.profiles[profile_id]
        if channel_id not in profile.channels:
            raise KeyError(f"Không có channel_id={channel_id}")
        return profile.channels[channel_id].windows[window_index]

    def to_summary(self) -> dict[str, Any]:
        return {
            "session_id": self.source_signal.session_id,
            "phase": {
                "phase_id": self.phase_id,
                "start_sample": int(self.phase_start_sample),
                "end_sample_exclusive": int(self.phase_end_sample_exclusive),
                "sample_count": int(self.phase_sample_count),
            },
            "config": {
                "windowing_config_id": self.windowing_config_id,
                "boundary_convention": "half_open",
                "spectral_taper_default": self.spectral_taper_default,
                "taper_applied_during_windowing": False,
            },
            "upstream": {
                "preprocess_config_id": self.source_signal.preprocess_config_id,
                "preprocessed_signal_hash_sha256": (
                    self.source_signal.combined_output_hash_sha256
                ),
            },
            "plan_hash_sha256": self.plan_hash_sha256,
            "profiles": [
                self.profiles[key].to_dict(
                    spectral_taper_default=self.spectral_taper_default
                )
                for key in ("time_domain", "frequency_domain")
            ],
        }


@dataclass(frozen=True, slots=True)
class WindowingRunResult:
    session_id: str
    status: str
    downstream_allowed: bool
    config_id: str
    inherited_preprocessing_status: str
    reason_codes: tuple[str, ...]
    plan: WindowedSignalPlan | None
    limitations: tuple[str, ...]
    schema_version: str = "windowing-result.v0.1"

    def __post_init__(self) -> None:
        if self.status not in _ALLOWED_STATUSES:
            raise ValueError(f"Status không hỗ trợ: {self.status}")
        if self.downstream_allowed and self.plan is None:
            raise ValueError("downstream_allowed=true cần plan")
        if not self.downstream_allowed and self.status != "blocked":
            raise ValueError("downstream_allowed=false phải có status=blocked")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "session_id": self.session_id,
            "status": self.status,
            "downstream_allowed": bool(self.downstream_allowed),
            "config": {"config_id": self.config_id},
            "inherited_preprocessing": {
                "status": self.inherited_preprocessing_status,
            },
            "reason_codes": list(dict.fromkeys(self.reason_codes)),
            "plan": self.plan.to_summary() if self.plan else None,
            "limitations": list(self.limitations),
        }
