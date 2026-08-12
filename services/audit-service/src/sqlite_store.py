"""RDBMS implementation of dual-log research event store using sqlite3."""
from __future__ import annotations

import sqlite3
import json
import hashlib
from typing import Any, Mapping
from pathlib import Path
from dataclasses import dataclass

from append_only_store import validate_research_event, _sha, _canonical, AppendResult, DualLogAccessPolicy
from interfaces import IAuditStore

class SQLiteEventStore:
    def __init__(self, db_path: str | Path, stream_name: str) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.stream_name = stream_name
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_events (
                    stream_name TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    event_id TEXT NOT NULL UNIQUE,
                    previous_record_hash TEXT NOT NULL,
                    record_hash TEXT NOT NULL,
                    event_payload TEXT NOT NULL,
                    PRIMARY KEY (stream_name, sequence)
                )
            ''')
            conn.commit()

    def _get_last_sequence_and_hash(self, conn: sqlite3.Connection) -> tuple[int, str]:
        cursor = conn.execute(
            'SELECT sequence, record_hash FROM audit_events WHERE stream_name = ? ORDER BY sequence DESC LIMIT 1',
            (self.stream_name,)
        )
        row = cursor.fetchone()
        if row:
            return row[0], row[1].removeprefix("evtrow_sha256_")
        return 0, "0" * 64

    def append(self, event: Mapping[str, Any]) -> AppendResult:
        validate_research_event(event)
        event_id = event["event_id"]
        canonical_event_payload = _canonical(dict(event)).decode("utf-8")
        
        with sqlite3.connect(self.db_path) as conn:
            # Check for existing event
            cursor = conn.execute('SELECT event_payload, sequence, record_hash FROM audit_events WHERE event_id = ?', (event_id,))
            row = cursor.fetchone()
            if row:
                existing_payload, existing_seq, existing_hash = row
                if _canonical(json.loads(existing_payload)) != _canonical(dict(event)):
                    raise ValueError("EVENT_ID_CONFLICT")
                return AppendResult(existing_seq, event_id, existing_hash, True)
            
            # Start transaction to append
            conn.execute("BEGIN IMMEDIATE")
            try:
                last_seq, previous = self._get_last_sequence_and_hash(conn)
                sequence = last_seq + 1
                
                body = {
                    "stream": self.stream_name,
                    "sequence": sequence,
                    "previous_record_hash": previous,
                    "event": dict(event),
                }
                record_hash = "evtrow_sha256_" + _sha(body)
                
                conn.execute(
                    'INSERT INTO audit_events (stream_name, sequence, event_id, previous_record_hash, record_hash, event_payload) VALUES (?, ?, ?, ?, ?, ?)',
                    (self.stream_name, sequence, event_id, previous, record_hash, canonical_event_payload)
                )
                conn.commit()
                return AppendResult(sequence, event_id, record_hash, False)
            except Exception:
                conn.rollback()
                raise

    def events(self, *, case_id: str | None = None, correlation_id: str | None = None) -> list[dict[str, Any]]:
        self.verify_integrity()
        values = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT event_payload FROM audit_events WHERE stream_name = ? ORDER BY sequence ASC', (self.stream_name,))
            for (payload_json,) in cursor:
                values.append(json.loads(payload_json))
        
        if case_id is not None:
            values = [item for item in values if item.get("case_id") == case_id]
        if correlation_id is not None:
            values = [item for item in values if item.get("correlation_id") == correlation_id]
        return values

    def verify_integrity(self) -> int:
        previous = "0" * 64
        seen: set[str] = set()
        count = 0
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'SELECT sequence, event_id, previous_record_hash, record_hash, event_payload FROM audit_events WHERE stream_name = ? ORDER BY sequence ASC',
                (self.stream_name,)
            )
            for expected_sequence, (seq, event_id, prev_hash, rec_hash, payload_json) in enumerate(cursor, 1):
                if seq != expected_sequence:
                    raise ValueError("EVENT_STORE_SEQUENCE_TAMPERED")
                if prev_hash != previous:
                    raise ValueError("EVENT_STORE_CHAIN_TAMPERED")
                if event_id in seen:
                    raise ValueError("EVENT_STORE_DUPLICATE_EVENT_ID")
                seen.add(event_id)
                
                event = json.loads(payload_json)
                body = {
                    "stream": self.stream_name,
                    "sequence": expected_sequence,
                    "previous_record_hash": previous,
                    "event": event,
                }
                actual = "evtrow_sha256_" + _sha(body)
                if rec_hash != actual:
                    raise ValueError("EVENT_STORE_RECORD_TAMPERED")
                previous = actual.removeprefix("evtrow_sha256_")
                count += 1
        return count

    def find(self, key: str, value: Any) -> dict[str, Any] | None:
        for event in self.events():
            if event.get(key) == value:
                return event
        return None

class SQLiteDualEventStore(IAuditStore):
    def __init__(self, db_path: str | Path, policy: DualLogAccessPolicy | None = None) -> None:
        self.audit = SQLiteEventStore(db_path, "COMPLIANCE_AUDIT")
        self.research = SQLiteEventStore(db_path, "RESEARCH_PROCESS")
        self.policy = policy or DualLogAccessPolicy()

    def append_research(self, event: Mapping[str, Any]) -> AppendResult:
        return self.research.append(event)

    def append_compliance(self, event: Mapping[str, Any]) -> AppendResult:
        return self.audit.append(event)

    def verify_all(self) -> dict[str, int]:
        return {"compliance": self.audit.verify_integrity(), "research": self.research.verify_integrity()}

    def timeline(self, case_id: str) -> list[dict[str, Any]]:
        return self.research.events(case_id=case_id)
