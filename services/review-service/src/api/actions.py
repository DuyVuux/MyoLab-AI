"""DAY54 typed review action API service with idempotent dual-log emission."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Any
import sys
import os

# Add parent path to import domain and security
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domain.state_machine import ReviewContext, transition
from security.research_rbac import ALLOWED_ROLES

ACTION_TO_TRANSITION = {
    "ACCEPT_TECHNICAL": "ACCEPT_TECHNICAL",
    "OVERRIDE_WITH_REASON": "ACCEPT_TECHNICAL",
    "REQUEST_REPROCESS": "REQUEST_REPROCESS",
    "SUGGEST_REMEASURE": "SUGGEST_REMEASURE",
    "MARK_INCONCLUSIVE": "MARK_INCONCLUSIVE",
}
REASON_REQUIRED = {"OVERRIDE_WITH_REASON", "REQUEST_REPROCESS", "SUGGEST_REMEASURE", "MARK_INCONCLUSIVE"}

def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

def _hash(prefix: str, value: Any) -> str:
    return prefix + hashlib.sha256(_canonical(value)).hexdigest()

@dataclass(frozen=True)
class ReviewActionRequest:
    case_id: str
    current_state: str
    action: str
    reviewer_id: str
    reviewer_role: str
    evidence_bundle_id: str
    idempotency_key: str
    requested_at_utc: str
    correlation_id: str
    qc_signal_quality: str | None
    metric_states: tuple[str, ...]
    reason_code: str | None = None
    new_evidence_bundle_ref: str | None = None
    reviewer_approval: bool = False

@dataclass(frozen=True)
class ReviewActionResponse:
    logical_action_id: str
    state_before: str
    state_after: str
    action: str
    transition_action: str
    research_event_id: str
    compliance_event_id: str
    idempotent_replay: bool
    reversible: bool
    compensating_action: str | None

def _validate_request(req: ReviewActionRequest) -> None:
    if req.reviewer_role not in ALLOWED_ROLES:
        raise PermissionError("REVIEW_ACTION_ROLE_FORBIDDEN")
    if req.action not in ACTION_TO_TRANSITION:
        raise ValueError("REVIEW_ACTION_UNSUPPORTED")
    if req.current_state != "REVIEWING":
        raise ValueError("REVIEW_ACTION_REQUIRES_REVIEWING_STATE")
    if len(req.idempotency_key) < 8:
        raise ValueError("IDEMPOTENCY_KEY_TOO_SHORT")
    if req.action in REASON_REQUIRED and not req.reason_code:
        raise ValueError("REVIEW_ACTION_REASON_REQUIRED")

def logical_action_id(req: ReviewActionRequest) -> str:
    facts = asdict(req)
    facts["metric_states"] = list(req.metric_states)
    return _hash("ract_sha256_", facts)

def _response_from_event(event: dict[str, Any], replay: bool) -> ReviewActionResponse:
    return ReviewActionResponse(
        logical_action_id=event["logical_action_id"],
        state_before=event["state_before"],
        state_after=event["state_after"],
        action=event["activity"],
        transition_action=event["transition_action"],
        research_event_id=event["event_id"],
        compliance_event_id=event["compliance_event_id"],
        idempotent_replay=replay,
        reversible=event["reversible"],
        compensating_action=event.get("compensating_action"),
    )

class ReviewActionService:
    def __init__(self, event_store) -> None:
        self.event_store = event_store

    def execute(self, req: ReviewActionRequest) -> ReviewActionResponse:
        _validate_request(req)
        action_id = logical_action_id(req)
        
        # In a real API route, you would use event_store.research.find("logical_action_id", action_id)
        # But depending on the implementation of event_store, we need to adapt here.
        existing = self.event_store.research.find("logical_action_id", action_id) if hasattr(self.event_store, 'research') else None
        if existing is not None:
            return _response_from_event(existing, True)

        transition_action = ACTION_TO_TRANSITION[req.action]
        ctx = ReviewContext(
            evidence_bundle_id=req.evidence_bundle_id,
            qc_signal_quality=req.qc_signal_quality,
            metric_states=req.metric_states,
            reviewer_id=req.reviewer_id,
            reviewer_approval=req.reviewer_approval,
            reason_code=req.reason_code,
            new_evidence_bundle_ref=req.new_evidence_bundle_ref,
        )
        result = transition(req.current_state, transition_action, ctx)
        idempotency_hash = _hash("idem_sha256_", req.idempotency_key)
        compliance_event_id = _hash("caevt_sha256_", {"logical_action_id": action_id, "stream": "COMPLIANCE"})
        research_event_id = _hash("raevt_sha256_", {"logical_action_id": action_id, "stream": "RESEARCH"})
        reversible = req.action in {"REQUEST_REPROCESS", "SUGGEST_REMEASURE"}
        compensating = "REPROCESS_COMPLETED" if req.action == "REQUEST_REPROCESS" else None
        if req.action == "SUGGEST_REMEASURE":
            compensating = "CLOSE_PENDING_REMEASUREMENT"
        
        research_event = {
            "event_id": research_event_id,
            "event_type": "REVIEW_ACTION",
            "case_id": req.case_id,
            "activity": req.action,
            "actor_role": req.reviewer_role,
            "event_time_utc": req.requested_at_utc,
            "correlation_id": req.correlation_id,
            "state_before": result.state_before,
            "state_after": result.state_after,
            "reason_codes": [req.reason_code] if req.reason_code else [],
            "source_refs": [req.evidence_bundle_id, result.event["event_id"]],
            "versions": {"review_state_machine": "0.2-research", "review_action_api": "0.1.0"},
            "logical_action_id": action_id,
            "idempotency_key_hash": idempotency_hash,
            "transition_action": transition_action,
            "override_applied": req.action == "OVERRIDE_WITH_REASON",
            "reversible": reversible,
            "compensating_action": compensating,
            "compliance_event_id": compliance_event_id,
        }
        
        compliance_event = {
            **research_event,
            "event_id": compliance_event_id,
            "event_type": "REVIEW_ACTION",
            "actor_role": req.reviewer_role,
            "research_event_id": research_event_id,
            "actor_ref": _hash("actor_sha256_", req.reviewer_id),
        }
        
        if hasattr(self.event_store, 'append_research'):
            self.event_store.append_research(research_event)
            try:
                self.event_store.append_compliance(compliance_event)
            except Exception:
                raise RuntimeError("COMPLIANCE_AUDIT_APPEND_FAILED_AFTER_RESEARCH_APPEND")
        
        return _response_from_event(research_event, False)
