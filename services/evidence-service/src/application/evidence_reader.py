"""DAY55 typed research evidence read service; storage details stay behind DTO boundaries."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Generic, Mapping, TypeVar

T = TypeVar("T")
RAW_ROLES = {"REVIEWER", "RESEARCHER", "ADMIN"}


@dataclass(frozen=True)
class ReadEnvelope(Generic[T]):
    status: str
    value: T | None
    reason_codes: tuple[str, ...] = ()


@dataclass(frozen=True)
class Page(Generic[T]):
    items: tuple[T, ...]
    page: int
    page_size: int
    total: int
    has_next: bool


def _page(items: list[T], page: int, page_size: int) -> Page[T]:
    if page < 1:
        raise ValueError("PAGE_MUST_BE_POSITIVE")
    if page_size < 1 or page_size > 100:
        raise ValueError("PAGE_SIZE_OUT_OF_RANGE")
    start = (page - 1) * page_size
    subset = tuple(items[start:start + page_size])
    return Page(subset, page, page_size, len(items), start + page_size < len(items))


class ApprovedLocalResearchStore:
    """Explicit local research waveform store with traversal protection."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve(self, relative_path: str) -> Path:
        candidate = Path(relative_path)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise PermissionError("RAW_PATH_TRAVERSAL_FORBIDDEN")
        resolved = (self.root / candidate).resolve()
        try:
            resolved.relative_to(self.root)
        except ValueError as exc:
            raise PermissionError("RAW_PATH_TRAVERSAL_FORBIDDEN") from exc
        return resolved

    def read_window(self, relative_path: str, start: int, end: int) -> tuple[float | None, ...]:
        if start < 0 or end <= start:
            raise ValueError("RAW_WINDOW_RANGE_INVALID")
        path = self._resolve(relative_path)
        if path.suffix.lower() != ".json":
            raise ValueError("RAW_RESEARCH_FORMAT_UNSUPPORTED")
        if not path.is_file():
            raise FileNotFoundError("RAW_RESEARCH_OBJECT_NOT_FOUND")
        values = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(values, list):
            raise ValueError("RAW_RESEARCH_OBJECT_INVALID")
        if end > len(values):
            raise ValueError("RAW_WINDOW_RANGE_OUT_OF_BOUNDS")
        return tuple(float(v) if v is not None else None for v in values[start:end])


class EvidenceReadService:
    def __init__(self, session_bundle: Mapping[str, Any], *, event_store: Any | None = None,
                 raw_store: ApprovedLocalResearchStore | None = None) -> None:
        self.bundle = dict(session_bundle)
        self.event_store = event_store
        self.raw_store = raw_store

    def _case_ok(self, case_id: str) -> bool:
        return case_id == self.bundle.get("session_id")

    def get_case_summary(self, case_id: str) -> ReadEnvelope[dict[str, Any]]:
        if not self._case_ok(case_id):
            return ReadEnvelope("NOT_AVAILABLE", None, ("CASE_NOT_FOUND",))
        summary = {
            "case_id": case_id,
            "claim_scope": self.bundle.get("claim_scope"),
            "source_refs": tuple(self.bundle.get("source_refs", [])),
            "qc": self.bundle.get("qc"),
            "processing": self.bundle.get("processing"),
            "distribution_support": self.bundle.get("distribution_support"),
            "uncertainty": self.bundle.get("uncertainty"),
            "limitations": tuple(self.bundle.get("limitations", [])),
            "unsupported_capabilities": tuple(self.bundle.get("unsupported_capabilities", [])),
        }
        return ReadEnvelope("AVAILABLE", summary)

    def get_qc(self, case_id: str) -> ReadEnvelope[dict[str, Any]]:
        if not self._case_ok(case_id):
            return ReadEnvelope("NOT_AVAILABLE", None, ("CASE_NOT_FOUND",))
        qc = self.bundle.get("qc")
        return ReadEnvelope("AVAILABLE" if qc else "NOT_AVAILABLE", qc, () if qc else ("QC_NOT_AVAILABLE",))

    def get_processing(self, case_id: str) -> ReadEnvelope[dict[str, Any]]:
        if not self._case_ok(case_id):
            return ReadEnvelope("NOT_AVAILABLE", None, ("CASE_NOT_FOUND",))
        value = self.bundle.get("processing")
        return ReadEnvelope("AVAILABLE" if value else "NOT_AVAILABLE", value, () if value else ("PROCESSING_NOT_AVAILABLE",))

    def list_metrics(self, case_id: str, *, page: int = 1, page_size: int = 20) -> ReadEnvelope[Page[dict[str, Any]]]:
        if not self._case_ok(case_id):
            return ReadEnvelope("NOT_AVAILABLE", None, ("CASE_NOT_FOUND",))
        metrics = [dict(item) for item in self.bundle.get("metrics", [])]
        return ReadEnvelope("AVAILABLE", _page(metrics, page, page_size))

    def get_metric(self, case_id: str, metric_name: str) -> ReadEnvelope[dict[str, Any]]:
        if not self._case_ok(case_id):
            return ReadEnvelope("NOT_AVAILABLE", None, ("CASE_NOT_FOUND",))
        for item in self.bundle.get("metrics", []):
            if item.get("metric_name") == metric_name:
                return ReadEnvelope("AVAILABLE", dict(item))
        return ReadEnvelope("NOT_AVAILABLE", None, ("METRIC_NOT_FOUND",))

    def get_timeline(self, case_id: str, *, page: int = 1, page_size: int = 50) -> ReadEnvelope[Page[dict[str, Any]]]:
        if not self._case_ok(case_id):
            return ReadEnvelope("NOT_AVAILABLE", None, ("CASE_NOT_FOUND",))
        if self.event_store is None:
            return ReadEnvelope("NOT_AVAILABLE", None, ("EVENT_STORE_NOT_CONFIGURED",))
        events = [dict(item) for item in self.event_store.timeline(case_id)]
        return ReadEnvelope("AVAILABLE", _page(events, page, page_size))

    def get_raw_window(self, case_id: str, *, requester_role: str, source_ref: str,
                       relative_path: str, start: int, end: int) -> ReadEnvelope[dict[str, Any]]:
        if not self._case_ok(case_id):
            return ReadEnvelope("NOT_AVAILABLE", None, ("CASE_NOT_FOUND",))
        if requester_role not in RAW_ROLES:
            return ReadEnvelope("FORBIDDEN", None, ("RAW_RESEARCH_ACCESS_FORBIDDEN",))
        if source_ref not in self.bundle.get("source_refs", []):
            return ReadEnvelope("NOT_AVAILABLE", None, ("SOURCE_REF_NOT_IN_CASE",))
        if self.raw_store is None:
            return ReadEnvelope("NOT_AVAILABLE", None, ("RAW_RESEARCH_STORE_NOT_CONFIGURED",))
        try:
            values = self.raw_store.read_window(relative_path, start, end)
        except FileNotFoundError:
            return ReadEnvelope("NOT_AVAILABLE", None, ("RAW_RESEARCH_OBJECT_NOT_FOUND",))
        # Security/range errors intentionally propagate as explicit request failures.
        return ReadEnvelope("AVAILABLE", {
            "source_ref": source_ref,
            "start": start,
            "end": end,
            "values": values,
            "local_path": None,
        })

    def reconstruct_case(self, case_id: str) -> ReadEnvelope[dict[str, Any]]:
        summary = self.get_case_summary(case_id)
        if summary.value is None:
            return ReadEnvelope(summary.status, None, summary.reason_codes)
        metrics = self.list_metrics(case_id).value
        timeline_env = self.get_timeline(case_id)
        return ReadEnvelope("AVAILABLE", {
            "summary": summary.value,
            "metrics": metrics.items if metrics else (),
            "timeline": timeline_env.value.items if timeline_env.value else (),
            "timeline_status": timeline_env.status,
            "timeline_reason_codes": timeline_env.reason_codes,
        })
