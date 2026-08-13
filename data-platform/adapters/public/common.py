from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any

@dataclass(frozen=True)
class TransformProvenance:
    operation: str
    source_unit: str
    target_unit: str
    factor: float
    evidence_basis: str

@dataclass(frozen=True)
class CanonicalPublicRecord:
    dataset_id: str
    dataset_version: str
    source_file: str
    source_sha256: str
    subject_id: str
    session_id: str
    fs_hz: float
    channel_names: tuple[str, ...]
    units: tuple[str, ...]
    values: tuple[tuple[float, ...], ...]
    evidence_tier: str
    license_id: str
    source_task_code: str | None
    canonical_task: str | None
    task_reason: str | None
    unknown_metadata: tuple[str, ...]
    transforms: tuple[TransformProvenance, ...]

    def metadata_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop('values')
        return data
