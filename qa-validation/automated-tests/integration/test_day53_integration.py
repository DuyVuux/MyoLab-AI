from __future__ import annotations

import json
import sys
from pathlib import Path
import pytest
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[3]

if str(ROOT / 'services/audit-service/src') not in sys.path:
    sys.path.insert(0, str(ROOT / 'services/audit-service/src'))
if str(ROOT / 'services/review-service/src') not in sys.path:
    sys.path.insert(0, str(ROOT / 'services/review-service/src'))

from append_only_store import DualEventStore, AppendOnlyJsonlStore, validate_research_event, normalize_review_transition
from domain.state_machine import ReviewContext, transition, STATES
from application.review_workflow import ReviewWorkflowAppService


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield Path(d)
    shutil.rmtree(d)


@pytest.fixture
def event_store(temp_dir):
    return DualEventStore(temp_dir)


@pytest.fixture
def app_service(event_store):
    return ReviewWorkflowAppService(event_store)


def test_append_only_store_creates_files(temp_dir):
    store = DualEventStore(temp_dir)
    assert (temp_dir / "compliance-audit.jsonl").exists()
    assert (temp_dir / "research-events.jsonl").exists()


def test_prohibited_keys_rejected(event_store):
    payload = {
        "event_id": "evt_123",
        "event_type": "REVIEW_TRANSITION",
        "case_id": "C1",
        "activity": "START_REVIEW",
        "actor_role": "REVIEWER",
        "event_time_utc": "2026-01-01T00:00:00Z",
        "correlation_id": "corr_123",
        "reason_codes": [],
        "source_refs": [],
        "versions": {},
        # Prohibited field
        "waveform": [1.0, 2.0, 3.0] 
    }
    with pytest.raises(ValueError, match="PROHIBITED_EVENT_FIELD"):
        event_store.append_research(payload)


def test_idempotent_append(event_store):
    payload = {
        "event_id": "evt_123",
        "event_type": "REVIEW_TRANSITION",
        "case_id": "C1",
        "activity": "START_REVIEW",
        "actor_role": "REVIEWER",
        "event_time_utc": "2026-01-01T00:00:00Z",
        "correlation_id": "corr_123",
        "reason_codes": [],
        "source_refs": [],
        "versions": {}
    }
    res1 = event_store.append_research(payload)
    assert res1.idempotent_replay is False

    res2 = event_store.append_research(payload)
    assert res2.idempotent_replay is True
    assert res1.record_hash == res2.record_hash


def test_id_conflict_rejected(event_store):
    payload1 = {
        "event_id": "evt_123",
        "event_type": "REVIEW_TRANSITION",
        "case_id": "C1",
        "activity": "START_REVIEW",
        "actor_role": "REVIEWER",
        "event_time_utc": "2026-01-01T00:00:00Z",
        "correlation_id": "corr_123",
        "reason_codes": [],
        "source_refs": [],
        "versions": {}
    }
    payload2 = dict(payload1)
    payload2["activity"] = "QUEUE_FOR_REVIEW"
    
    event_store.append_research(payload1)
    with pytest.raises(ValueError, match="EVENT_ID_CONFLICT"):
        event_store.append_research(payload2)


def test_tamper_evident_chain(temp_dir):
    store = AppendOnlyJsonlStore(temp_dir / "test.jsonl", "TEST_STREAM")
    payload = {
        "event_id": "evt_123",
        "event_type": "REVIEW_TRANSITION",
        "case_id": "C1",
        "activity": "START_REVIEW",
        "actor_role": "REVIEWER",
        "event_time_utc": "2026-01-01T00:00:00Z",
        "correlation_id": "corr_123",
        "reason_codes": [],
        "source_refs": [],
        "versions": {}
    }
    store.append(payload)
    
    # Tamper the file manually
    lines = (temp_dir / "test.jsonl").read_text().splitlines()
    record = json.loads(lines[0])
    record["sequence"] = 2  # Tampered
    (temp_dir / "test.jsonl").write_text(json.dumps(record) + "\n")
    
    with pytest.raises(ValueError, match="EVENT_STORE_SEQUENCE_TAMPERED|EVENT_STORE_RECORD_TAMPERED"):
        store.verify_integrity()


def test_workflow_app_service_integration(app_service):
    ctx = ReviewContext(
        evidence_bundle_id="EB_123",
        qc_signal_quality="PASS",
        metric_states=("AVAILABLE",),
        reviewer_id="REV_1",
        reason_code="REASON_1",
        reviewer_approval=True
    )
    
    event = app_service.execute_action("NEW", "QUEUE_FOR_REVIEW", ctx)
    assert event["event_type"] == "REVIEW_TRANSITION"
    assert event["activity"] == "QUEUE_FOR_REVIEW"
    
    # Verify it was appended to the store
    timeline = app_service._audit_store.timeline("UNKNOWN_CASE")
    assert len(timeline) == 1
    assert timeline[0]["event_id"] == event["event_id"]

