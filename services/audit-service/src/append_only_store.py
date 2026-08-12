"""DAY53 append-only dual-log research event store with hash-chain integrity."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

PROHIBITED_KEYS = {
    "waveform", "raw_samples", "samples", "diagnosis", "patient_name", "mrn",
    "source_path", "absolute_path", "free_text_clinical_note",
}


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _scan_prohibited(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key).lower() in PROHIBITED_KEYS and child not in (None, "", [], {}):
                raise ValueError(f"PROHIBITED_EVENT_FIELD:{path}.{key}")
            _scan_prohibited(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _scan_prohibited(child, f"{path}[{index}]")


def validate_research_event(event: Mapping[str, Any]) -> None:
    required = {
        "event_id", "event_type", "case_id", "activity", "actor_role",
        "event_time_utc", "correlation_id", "reason_codes", "source_refs", "versions",
    }
    missing = sorted(required.difference(event))
    if missing:
        raise ValueError("MISSING_EVENT_FIELDS:" + ",".join(missing))
    if not str(event["event_id"]).strip():
        raise ValueError("EVENT_ID_REQUIRED")
    if event["event_type"] not in {
        "REVIEW_TRANSITION", "REVIEW_ACTION", "PROCESSING_LIFECYCLE", "SYSTEM_WORKFLOW"
    }:
        raise ValueError("EVENT_TYPE_UNSUPPORTED")
    if not isinstance(event["reason_codes"], list):
        raise ValueError("REASON_CODES_MUST_BE_LIST")
    if not isinstance(event["source_refs"], list):
        raise ValueError("SOURCE_REFS_MUST_BE_LIST")
    _scan_prohibited(event)


def normalize_review_transition(
    transition_event: Mapping[str, Any], *, case_id: str, actor_role: str,
    correlation_id: str, event_time_utc: str | None = None,
) -> dict[str, Any]:
    event = {
        "event_id": transition_event["event_id"],
        "event_type": "REVIEW_TRANSITION",
        "case_id": case_id,
        "activity": transition_event["action"],
        "actor_role": actor_role,
        "event_time_utc": event_time_utc or datetime.now(timezone.utc).isoformat(),
        "correlation_id": correlation_id,
        "state_before": transition_event["state_before"],
        "state_after": transition_event["state_after"],
        "reason_codes": [transition_event["reason_code"]] if transition_event.get("reason_code") else [],
        "source_refs": [transition_event["evidence_bundle_id"]],
        "versions": {"review_state_machine": transition_event.get("schema_version", "0.2-research")},
        "parent_event_id": None,
        "duration_ms": None,
        "outcome": transition_event["state_after"],
    }
    validate_research_event(event)
    return event


@dataclass(frozen=True)
class AppendResult:
    sequence: int
    event_id: str
    record_hash: str
    idempotent_replay: bool


class AppendOnlyJsonlStore:
    """Persistent append-only JSONL stream with tamper-evident hash chaining."""

    def __init__(self, path: str | Path, stream_name: str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.stream_name = stream_name
        if not self.path.exists():
            self.path.touch()

    def _records(self) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, 1):
                text = line.strip()
                if not text:
                    continue
                try:
                    records.append(json.loads(text))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"EVENT_STORE_CORRUPT_JSON_LINE:{line_no}") from exc
        return records

    def verify_integrity(self) -> int:
        previous = "0" * 64
        seen: set[str] = set()
        records = self._records()
        for expected_sequence, record in enumerate(records, 1):
            if record.get("sequence") != expected_sequence:
                raise ValueError("EVENT_STORE_SEQUENCE_TAMPERED")
            if record.get("previous_record_hash") != previous:
                raise ValueError("EVENT_STORE_CHAIN_TAMPERED")
            event = record.get("event")
            if not isinstance(event, dict):
                raise ValueError("EVENT_STORE_EVENT_INVALID")
            if event.get("event_id") in seen:
                raise ValueError("EVENT_STORE_DUPLICATE_EVENT_ID")
            seen.add(event["event_id"])
            body = {
                "stream": self.stream_name,
                "sequence": expected_sequence,
                "previous_record_hash": previous,
                "event": event,
            }
            actual = "evtrow_sha256_" + _sha(body)
            if record.get("record_hash") != actual:
                raise ValueError("EVENT_STORE_RECORD_TAMPERED")
            previous = actual.removeprefix("evtrow_sha256_")
        return len(records)

    def append(self, event: Mapping[str, Any]) -> AppendResult:
        validate_research_event(event)
        records = self._records()
        for record in records:
            existing = record["event"]
            if existing["event_id"] == event["event_id"]:
                if _canonical(existing) != _canonical(dict(event)):
                    raise ValueError("EVENT_ID_CONFLICT")
                return AppendResult(record["sequence"], event["event_id"], record["record_hash"], True)
        self.verify_integrity()
        previous = records[-1]["record_hash"].removeprefix("evtrow_sha256_") if records else "0" * 64
        sequence = len(records) + 1
        body = {
            "stream": self.stream_name,
            "sequence": sequence,
            "previous_record_hash": previous,
            "event": dict(event),
        }
        record_hash = "evtrow_sha256_" + _sha(body)
        envelope = {**body, "record_hash": record_hash}
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(_canonical(envelope).decode("utf-8") + "\n")
            handle.flush()
        return AppendResult(sequence, event["event_id"], record_hash, False)

    def events(self, *, case_id: str | None = None, correlation_id: str | None = None) -> list[dict[str, Any]]:
        self.verify_integrity()
        values = [record["event"] for record in self._records()]
        if case_id is not None:
            values = [item for item in values if item.get("case_id") == case_id]
        if correlation_id is not None:
            values = [item for item in values if item.get("correlation_id") == correlation_id]
        return values

    def find(self, key: str, value: Any) -> dict[str, Any] | None:
        for event in self.events():
            if event.get(key) == value:
                return event
        return None

    def replay_states(self, case_id: str) -> list[tuple[str | None, str | None, str]]:
        output: list[tuple[str | None, str | None, str]] = []
        for event in self.events(case_id=case_id):
            if event["event_type"] in {"REVIEW_TRANSITION", "REVIEW_ACTION"}:
                output.append((event.get("state_before"), event.get("state_after"), event["activity"]))
        return output


@dataclass(frozen=True)
class DualLogAccessPolicy:
    compliance_roles: tuple[str, ...] = ("ADMIN", "AUDITOR")
    research_roles: tuple[str, ...] = ("ADMIN", "AUDITOR", "RESEARCHER", "REVIEWER")
    compliance_retention: str = "LOCAL_RESEARCH_POLICY_DEFINED"
    research_retention: str = "LOCAL_RESEARCH_POLICY_DEFINED"


class DualEventStore:
    """Separate compliance and process streams; no update/delete methods by design."""

    def __init__(self, root: str | Path, policy: DualLogAccessPolicy | None = None) -> None:
        root_path = Path(root)
        self.audit = AppendOnlyJsonlStore(root_path / "compliance-audit.jsonl", "COMPLIANCE_AUDIT")
        self.research = AppendOnlyJsonlStore(root_path / "research-events.jsonl", "RESEARCH_PROCESS")
        self.policy = policy or DualLogAccessPolicy()

    def append_research(self, event: Mapping[str, Any]) -> AppendResult:
        return self.research.append(event)

    def append_compliance(self, event: Mapping[str, Any]) -> AppendResult:
        return self.audit.append(event)

    def verify_all(self) -> dict[str, int]:
        return {"compliance": self.audit.verify_integrity(), "research": self.research.verify_integrity()}

    def timeline(self, case_id: str) -> list[dict[str, Any]]:
        return self.research.events(case_id=case_id)
