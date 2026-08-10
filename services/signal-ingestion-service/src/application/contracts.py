"""Domain contracts and interfaces for ingestion orchestration."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Callable, Protocol

class InputKind(StrEnum):
    MR4_SINGLE = "MR4_SINGLE"
    MR4_SEPARATED = "MR4_SEPARATED"
    VICON_STACKED = "VICON_STACKED"

class IngestionStatus(StrEnum):
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"

class EventType(StrEnum):
    IMPORT_STARTED = "IMPORT_STARTED"
    IMPORT_SUCCEEDED = "IMPORT_SUCCEEDED"
    IMPORT_FAILED = "IMPORT_FAILED"
    VALIDATION_FAILED = "VALIDATION_FAILED"

@dataclass(frozen=True)
class ParserBindings:
    single_csv: Callable[[Path], Any]
    separated_csv: Callable[[Path], Any]
    vicon_stacked: Callable[[Path], Any]

    def for_kind(self, kind: InputKind) -> Callable[[Path], Any]:
        return {
            InputKind.MR4_SINGLE: self.single_csv,
            InputKind.MR4_SEPARATED: self.separated_csv,
            InputKind.VICON_STACKED: self.vicon_stacked,
        }[kind]

@dataclass(frozen=True)
class IngestionRequest:
    session_id: str
    case_id: str
    correlation_id: str
    input_kind: InputKind
    source_path: str
    config_version: str = "day19.v0.1"

@dataclass(frozen=True)
class IngestionEvent:
    event_id: str
    event_type: str
    operation_id: str
    case_id: str
    correlation_id: str
    session_id: str
    input_kind: str
    source_refs: tuple[str, ...]
    config_version: str
    emitted_at_utc: str
    outcome_status: str | None
    reason_code: str | None

@dataclass(frozen=True)
class IngestionResult:
    operation_id: str
    status: str
    stage: str
    session_id: str
    case_id: str
    correlation_id: str
    input_kind: str
    source_refs: tuple[str, ...]
    config_version: str
    reason_code: str | None
    payload: Any | None
    ready_for_downstream: bool
    processed: bool
    final_looking: bool
    replayed: bool = False

class EventSink(Protocol):
    def emit(self, event: IngestionEvent) -> None: ...

class IdempotencyStore(Protocol):
    def get(self, operation_id: str) -> IngestionResult | None: ...
    def put(self, operation_id: str, result: IngestionResult) -> None: ...
