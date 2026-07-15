"""Canonical in-memory representation for normalized sEMG sessions.

Day 3 scope:
- preserve source provenance;
- normalize supported amplitude units to microvolts;
- expose deterministic phase slicing;
- keep raw numeric arrays out of JSON summaries.

This module does not filter signals, extract features, or infer fatigue.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

import numpy as np

from .version import NORMALIZED_SIGNAL_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class ProtocolRef:
    """Immutable reference to the protocol used for the session."""

    protocol_id: str
    version: str

    def to_dict(self) -> dict[str, str]:
        return {"id": self.protocol_id, "version": self.version}


@dataclass(frozen=True, slots=True)
class PhaseMarker:
    """Half-open phase interval [start_s, end_s)."""

    phase_id: str
    start_s: float
    end_s: float

    @property
    def duration_s(self) -> float:
        return self.end_s - self.start_s

    def to_dict(self) -> dict[str, float | str]:
        return {
            "phase_id": self.phase_id,
            "start_s": float(self.start_s),
            "end_s": float(self.end_s),
            "duration_s": float(self.duration_s),
        }


@dataclass(frozen=True, slots=True)
class NormalizedChannel:
    """One channel after unit normalization to microvolts."""

    channel_id: str
    samples_uV: np.ndarray
    muscle: str
    side: str
    role: str
    source_column: str
    source_unit: str
    canonical_unit: str = "uV"

    def __post_init__(self) -> None:
        samples = np.ascontiguousarray(self.samples_uV, dtype=np.float64)
        if samples.ndim != 1:
            raise ValueError("Channel samples must be a one-dimensional array")
        samples.setflags(write=False)
        object.__setattr__(self, "samples_uV", samples)

    @property
    def sample_count(self) -> int:
        return int(self.samples_uV.size)

    @property
    def finite_ratio(self) -> float:
        if self.sample_count == 0:
            return 0.0
        return float(np.isfinite(self.samples_uV).sum() / self.sample_count)

    def to_summary(self) -> dict[str, Any]:
        """Return metadata only; raw samples are intentionally omitted."""

        return {
            "channel_id": self.channel_id,
            "muscle": self.muscle,
            "side": self.side,
            "role": self.role,
            "source_column": self.source_column,
            "source_unit": self.source_unit,
            "canonical_unit": self.canonical_unit,
            "sample_count": self.sample_count,
            "finite_ratio": self.finite_ratio,
        }


@dataclass(frozen=True, slots=True)
class NormalizedSignal:
    """Canonical session object passed to downstream QC/preprocessing.

    The object is immutable at the dataclass level and stores read-only NumPy
    arrays. It is an in-memory contract, not a clinical result.
    """

    session_id: str
    sampling_rate_hz: float
    time_s: np.ndarray
    channels: Mapping[str, NormalizedChannel]
    protocol_ref: ProtocolRef
    phase_markers: tuple[PhaseMarker, ...]
    data_source: str
    source_file_name: str
    source_hash_sha256: str
    processing_history: Mapping[str, Any]
    source_manifest: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = NORMALIZED_SIGNAL_SCHEMA_VERSION

    def __post_init__(self) -> None:
        time_axis = np.ascontiguousarray(self.time_s, dtype=np.float64)
        if time_axis.ndim != 1:
            raise ValueError("time_s must be a one-dimensional array")
        time_axis.setflags(write=False)
        object.__setattr__(self, "time_s", time_axis)

        channel_copy = dict(self.channels)
        object.__setattr__(self, "channels", MappingProxyType(channel_copy))
        object.__setattr__(
            self,
            "processing_history",
            MappingProxyType(dict(self.processing_history)),
        )
        object.__setattr__(
            self,
            "source_manifest",
            MappingProxyType(dict(self.source_manifest)),
        )
        object.__setattr__(self, "phase_markers", tuple(self.phase_markers))

    @property
    def sample_count(self) -> int:
        return int(self.time_s.size)

    @property
    def channel_count(self) -> int:
        return len(self.channels)

    @property
    def duration_s(self) -> float:
        """Elapsed time between first and last stored sample.

        For N uniformly sampled values at Fs, this equals (N - 1) / Fs.
        Protocol phase duration is represented separately by phase markers.
        """

        if self.sample_count < 2:
            return 0.0
        return float(self.time_s[-1] - self.time_s[0])

    @property
    def record_span_s(self) -> float:
        """Half-open recording span, approximately N / Fs."""

        if self.sample_count == 0:
            return 0.0
        return float(self.sample_count / self.sampling_rate_hz)

    def get_phase(self, phase_id: str) -> PhaseMarker:
        matches = [marker for marker in self.phase_markers if marker.phase_id == phase_id]
        if not matches:
            raise KeyError(f"Unknown phase_id: {phase_id}")
        if len(matches) > 1:
            raise ValueError(f"Duplicate phase_id: {phase_id}")
        return matches[0]

    def phase_slice(self, phase_id: str) -> slice:
        """Convert a half-open phase marker to a deterministic NumPy slice."""

        marker = self.get_phase(phase_id)
        start = int(np.searchsorted(self.time_s, marker.start_s, side="left"))
        end = int(np.searchsorted(self.time_s, marker.end_s, side="left"))
        return slice(start, end)

    def to_summary(self) -> dict[str, Any]:
        """Create a JSON-safe provenance/shape summary without raw arrays."""

        return {
            "schema_version": self.schema_version,
            "session_id": self.session_id,
            "data_source": self.data_source,
            "sampling_rate_hz": float(self.sampling_rate_hz),
            "sample_count": self.sample_count,
            "channel_count": self.channel_count,
            "elapsed_duration_s": self.duration_s,
            "record_span_s": self.record_span_s,
            "protocol_ref": self.protocol_ref.to_dict(),
            "phase_markers": [marker.to_dict() for marker in self.phase_markers],
            "channels": [
                self.channels[channel_id].to_summary()
                for channel_id in sorted(self.channels)
            ],
            "source_file_name": self.source_file_name,
            "source_hash_sha256": self.source_hash_sha256,
            "processing_history": dict(self.processing_history),
        }
