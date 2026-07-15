"""Convert validated manifest dictionaries into typed metadata objects."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from semg_core.io import PhaseMarker, ProtocolRef


@dataclass(frozen=True, slots=True)
class ChannelSpec:
    column: str
    channel_id: str
    muscle: str
    side: str
    unit: str
    role: str


@dataclass(frozen=True, slots=True)
class SessionMetadata:
    session_id: str
    data_source: str
    signal_file: str
    time_column: str
    sampling_rate_hz: float
    protocol_ref: ProtocolRef
    channels: tuple[ChannelSpec, ...]
    phase_markers: tuple[PhaseMarker, ...]
    processing_history: Mapping[str, Any]
    declared_source_hash_sha256: str | None
    raw_manifest: Mapping[str, Any]

    def resolve_signal_path(self, manifest_path: Path) -> Path:
        return manifest_path.parent / self.signal_file


def extract_session_metadata(manifest: Mapping[str, Any]) -> SessionMetadata:
    protocol = manifest["protocol"]
    channels = tuple(
        ChannelSpec(
            column=str(item["column"]),
            channel_id=str(item["channel_id"]),
            muscle=str(item["muscle"]),
            side=str(item["side"]),
            unit=str(item["unit"]),
            role=str(item["role"]),
        )
        for item in manifest["channels"]
    )
    markers = tuple(
        PhaseMarker(
            phase_id=str(item["phase_id"]),
            start_s=float(item["start_s"]),
            end_s=float(item["end_s"]),
        )
        for item in manifest.get("phase_markers", [])
    )
    return SessionMetadata(
        session_id=str(manifest["session_id"]),
        data_source=str(manifest["data_source"]),
        signal_file=str(manifest["signal_file"]),
        time_column=str(manifest["time_column"]),
        sampling_rate_hz=float(manifest["sampling_rate_hz"]),
        protocol_ref=ProtocolRef(
            protocol_id=str(protocol["id"]),
            version=str(protocol["version"]),
        ),
        channels=channels,
        phase_markers=markers,
        processing_history=dict(manifest["processing_history"]),
        declared_source_hash_sha256=(
            str(manifest["source_hash_sha256"])
            if manifest.get("source_hash_sha256")
            else None
        ),
        raw_manifest=dict(manifest),
    )
