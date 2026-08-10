"""DAY19 unified ingestion facade.

The facade orchestrates parser adapters through dependency-injected bindings. It does
not parse vendor formats itself, resample signals, run QC/DSP/AI, or create processed-
looking success. Minimal ingestion events are emitted through an abstract sink.
"""
import hashlib
import json
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .contracts import (
    EventSink,
    EventType,
    IdempotencyStore,
    IngestionEvent,
    IngestionRequest,
    IngestionResult,
    IngestionStatus,
    ParserBindings,
    InputKind,
)
from .errors import VALIDATION_REASON_CODES
from src.provenance.fingerprint import SourceFingerprint, fingerprint_or_empty, digest_text

FACADE_ID = "motionlab-ingestion-facade"
FACADE_VERSION = "0.1.0"

class CollectingEventSink:
    """Engineering/test sink only; not the persistent Clinical Event Store."""
    def __init__(self) -> None:
        self.events: list[IngestionEvent] = []
        self._ids: set[str] = set()

    def emit(self, event: IngestionEvent) -> None:
        if event.event_id in self._ids:
            raise RuntimeError("duplicate ingestion event_id")
        self._ids.add(event.event_id)
        self.events.append(event)


class InMemoryIdempotencyStore:
    """Engineering/reference idempotency store; production storage is not DAY19 scope."""
    def __init__(self) -> None:
        self._results: dict[str, IngestionResult] = {}

    def get(self, operation_id: str) -> IngestionResult | None:
        return self._results.get(operation_id)

    def put(self, operation_id: str, result: IngestionResult) -> None:
        existing = self._results.get(operation_id)
        if existing is not None and existing != result:
            raise RuntimeError("idempotency conflict for operation_id")
        self._results[operation_id] = result


class IngestionFacade:
    def __init__(
        self,
        *,
        bindings: ParserBindings,
        event_sink: EventSink,
        idempotency_store: IdempotencyStore,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.bindings = bindings
        self.event_sink = event_sink
        self.idempotency_store = idempotency_store
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def ingest(self, request: IngestionRequest) -> IngestionResult:
        _validate_request(request)
        source_path = Path(request.source_path)
        before = fingerprint_or_empty(source_path)
        operation_id = _operation_id(request, before)
        cached = self.idempotency_store.get(operation_id)
        if cached is not None:
            return replace(cached, replayed=True)

        self._emit(
            request,
            before,
            operation_id,
            EventType.IMPORT_STARTED,
            outcome_status=None,
            reason_code=None,
            sequence=0,
        )

        payload: Any | None = None
        failure_code: str | None = None
        try:
            parser = self.bindings.for_kind(request.input_kind)
            payload = parser(source_path)
        except Exception as exc:
            failure_code = _exception_reason_code(exc)

        after = fingerprint_or_empty(source_path)
        if before != after:
            payload = None
            failure_code = "RAW_MUTATION_DETECTED"

        if failure_code is not None:
            event_type = (
                EventType.VALIDATION_FAILED
                if failure_code in VALIDATION_REASON_CODES
                else EventType.IMPORT_FAILED
            )
            self._emit(
                request,
                after,
                operation_id,
                event_type,
                outcome_status=IngestionStatus.FAILED.value,
                reason_code=failure_code,
                sequence=1,
            )
            result = IngestionResult(
                operation_id=operation_id,
                status=IngestionStatus.FAILED.value,
                stage="INGESTION_FAILED",
                session_id=request.session_id,
                case_id=request.case_id,
                correlation_id=request.correlation_id,
                input_kind=request.input_kind.value,
                source_refs=after.source_ids,
                config_version=request.config_version,
                reason_code=failure_code,
                payload=None,
                ready_for_downstream=False,
                processed=False,
                final_looking=False,
            )
        else:
            self._emit(
                request,
                after,
                operation_id,
                EventType.IMPORT_SUCCEEDED,
                outcome_status=IngestionStatus.SUCCEEDED.value,
                reason_code=None,
                sequence=1,
            )
            result = IngestionResult(
                operation_id=operation_id,
                status=IngestionStatus.SUCCEEDED.value,
                stage="INGESTED",
                session_id=request.session_id,
                case_id=request.case_id,
                correlation_id=request.correlation_id,
                input_kind=request.input_kind.value,
                source_refs=after.source_ids,
                config_version=request.config_version,
                reason_code=None,
                payload=payload,
                ready_for_downstream=True,
                processed=False,
                final_looking=False,
            )

        self.idempotency_store.put(operation_id, result)
        return result

    def _emit(
        self,
        request: IngestionRequest,
        fingerprint: SourceFingerprint,
        operation_id: str,
        event_type: EventType,
        *,
        outcome_status: str | None,
        reason_code: str | None,
        sequence: int,
    ) -> None:
        event = IngestionEvent(
            event_id=_event_id(operation_id, event_type, sequence),
            event_type=event_type.value,
            operation_id=operation_id,
            case_id=request.case_id,
            correlation_id=request.correlation_id,
            session_id=request.session_id,
            input_kind=request.input_kind.value,
            source_refs=fingerprint.source_ids,
            config_version=request.config_version,
            emitted_at_utc=self.clock().astimezone(timezone.utc).isoformat(),
            outcome_status=outcome_status,
            reason_code=reason_code,
        )
        self.event_sink.emit(event)


def _validate_request(request: IngestionRequest) -> None:
    for field_name in ("session_id", "case_id", "correlation_id", "config_version"):
        if not getattr(request, field_name).strip():
            raise ValueError(f"{field_name} must be non-empty")


def _operation_id(
    request: IngestionRequest,
    fingerprint: SourceFingerprint,
) -> str:
    payload = {
        "facade_version": FACADE_VERSION,
        "session_id": request.session_id,
        "case_id": request.case_id,
        "correlation_id": request.correlation_id,
        "input_kind": request.input_kind.value,
        "config_version": request.config_version,
        "source_digest": fingerprint.combined_digest,
    }
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return "ingest_sha256_" + hashlib.sha256(encoded).hexdigest()


def _event_id(operation_id: str, event_type: EventType, sequence: int) -> str:
    return "evt_sha256_" + digest_text(
        f"{operation_id}\x1f{event_type.value}\x1f{sequence}"
    )


def _exception_reason_code(exc: Exception) -> str:
    code = getattr(exc, "code", None)
    if isinstance(code, str) and code.strip():
        return code.strip()
    if isinstance(exc, FileNotFoundError):
        return "SOURCE_NOT_FOUND"
    return "UNEXPECTED_PARSER_FAILURE"
