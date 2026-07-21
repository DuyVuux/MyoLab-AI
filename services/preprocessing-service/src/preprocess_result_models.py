"""Mô hình kết quả cho preprocessing v0.1."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

import numpy as np

from semg_core.io import PhaseMarker, ProtocolRef


_ALLOWED_RUN_STATUSES = {"completed", "blocked"}
_ALLOWED_STEP_STATUSES = {"applied", "skipped"}


@dataclass(frozen=True, slots=True)
class StepRecord:
    step_id: str
    status: str
    parameters: Mapping[str, Any]
    reason: str | None = None

    def __post_init__(self) -> None:
        if self.status not in _ALLOWED_STEP_STATUSES:
            raise ValueError(f"Step status không hỗ trợ: {self.status}")
        object.__setattr__(self, "parameters", MappingProxyType(dict(self.parameters)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "status": self.status,
            "parameters": dict(self.parameters),
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class PreprocessedChannel:
    channel_id: str
    muscle: str
    side: str
    role: str
    samples_uV: np.ndarray
    valid_sample_mask: np.ndarray
    output_hash_sha256: str
    qa_diagnostics: Mapping[str, Any]

    def __post_init__(self) -> None:
        samples = np.ascontiguousarray(self.samples_uV, dtype=np.float64)
        mask = np.ascontiguousarray(self.valid_sample_mask, dtype=np.bool_)
        if samples.ndim != 1 or mask.ndim != 1:
            raise ValueError("samples và mask phải là mảng một chiều")
        if samples.size != mask.size:
            raise ValueError("samples và mask phải có cùng số phần tử")
        samples.setflags(write=False)
        mask.setflags(write=False)
        object.__setattr__(self, "samples_uV", samples)
        object.__setattr__(self, "valid_sample_mask", mask)
        object.__setattr__(self, "qa_diagnostics", MappingProxyType(dict(self.qa_diagnostics)))

    def to_summary(self) -> dict[str, Any]:
        return {
            "channel_id": self.channel_id,
            "muscle": self.muscle,
            "side": self.side,
            "role": self.role,
            "canonical_unit": "uV",
            "sample_count": int(self.samples_uV.size),
            "finite_ratio": float(np.isfinite(self.samples_uV).mean()),
            "valid_sample_ratio": float(self.valid_sample_mask.mean()),
            "output_hash_sha256": self.output_hash_sha256,
            "qa_diagnostics": dict(self.qa_diagnostics),
        }


@dataclass(frozen=True, slots=True)
class PreprocessedSignal:
    session_id: str
    sampling_rate_hz: float
    time_s: np.ndarray
    channels: Mapping[str, PreprocessedChannel]
    protocol_ref: ProtocolRef
    phase_markers: tuple[PhaseMarker, ...]
    source_file_name: str
    source_hash_sha256: str
    preprocess_config_id: str
    combined_output_hash_sha256: str
    edge_guard_samples: int

    def __post_init__(self) -> None:
        time_axis = np.ascontiguousarray(self.time_s, dtype=np.float64)
        time_axis.setflags(write=False)
        object.__setattr__(self, "time_s", time_axis)
        object.__setattr__(self, "channels", MappingProxyType(dict(self.channels)))
        object.__setattr__(self, "phase_markers", tuple(self.phase_markers))

    def phase_slice(self, phase_id: str) -> slice:
        matches = [phase for phase in self.phase_markers if phase.phase_id == phase_id]
        if len(matches) != 1:
            raise KeyError(f"Không tìm thấy duy nhất phase_id={phase_id}")
        phase = matches[0]
        start = int(np.searchsorted(self.time_s, phase.start_s, side="left"))
        end = int(np.searchsorted(self.time_s, phase.end_s, side="left"))
        return slice(start, end)

    def to_summary(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "sampling_rate_hz": float(self.sampling_rate_hz),
            "sample_count": int(self.time_s.size),
            "channel_count": len(self.channels),
            "protocol_ref": self.protocol_ref.to_dict(),
            "phase_markers": [phase.to_dict() for phase in self.phase_markers],
            "source_file_name": self.source_file_name,
            "source_hash_sha256": self.source_hash_sha256,
            "preprocess_config_id": self.preprocess_config_id,
            "combined_output_hash_sha256": self.combined_output_hash_sha256,
            "edge_guard_samples": int(self.edge_guard_samples),
            "channels": [
                self.channels[key].to_summary() for key in sorted(self.channels)
            ],
        }


@dataclass(frozen=True, slots=True)
class PreprocessingRunResult:
    session_id: str
    status: str
    downstream_allowed: bool
    config_id: str
    execution_mode: str
    inherited_qc_status: str
    inherited_qc_reason_codes: tuple[str, ...]
    reason_codes: tuple[str, ...]
    steps: tuple[StepRecord, ...]
    signal: PreprocessedSignal | None
    limitations: tuple[str, ...]
    schema_version: str = "preprocessing-result.v0.1"

    def __post_init__(self) -> None:
        if self.status not in _ALLOWED_RUN_STATUSES:
            raise ValueError(f"Run status không hỗ trợ: {self.status}")
        
        if self.status == "completed":
            if not self.downstream_allowed or self.signal is None:
                raise ValueError("completed yêu cầu downstream_allowed=True và signal != None")
        elif self.status == "blocked":
            if self.downstream_allowed or self.signal is not None:
                raise ValueError("blocked yêu cầu downstream_allowed=False và signal=None")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "session_id": self.session_id,
            "status": self.status,
            "downstream_allowed": bool(self.downstream_allowed),
            "config": {
                "config_id": self.config_id,
                "execution_mode": self.execution_mode,
            },
            "inherited_qc": {
                "status": self.inherited_qc_status,
                "reason_codes": list(dict.fromkeys(self.inherited_qc_reason_codes)),
            },
            "reason_codes": list(dict.fromkeys(self.reason_codes)),
            "steps": [step.to_dict() for step in self.steps],
            "signal_summary": self.signal.to_summary() if self.signal else None,
            "limitations": list(self.limitations),
        }
