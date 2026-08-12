import pytest
import datetime
from unittest.mock import MagicMock

# Make sure to import from the correct application path.
# Assuming tests run from project root, PYTHONPATH needs to include `services/review-service/src`.
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../services/review-service/src")))

from application.review_workflow import (
    ReviewWorkflowAppService, 
    ReviewActionRequest, 
    logical_action_id
)

@pytest.fixture
def mock_audit_store():
    store = MagicMock()
    # Setup mock research stream
    store.research = MagicMock()
    store.research.find.return_value = None
    return store

@pytest.fixture
def base_request():
    return ReviewActionRequest(
        case_id="case_123",
        current_state="REVIEWING",
        action="ACCEPT_TECHNICAL",
        reviewer_id="reviewer_456",
        reviewer_role="TECHNICAL_REVIEWER",
        evidence_bundle_id="bundle_789",
        idempotency_key="idempotency_key_001",
        requested_at_utc=datetime.datetime.utcnow().isoformat(),
        correlation_id="corr_abc",
        qc_signal_quality="PASS",
        metric_states=("AVAILABLE",),
        reviewer_approval=False
    )

def test_successful_action_with_dual_log(mock_audit_store, base_request):
    service = ReviewWorkflowAppService(mock_audit_store)
    response = service.execute_action(base_request)
    
    assert response.action == "ACCEPT_TECHNICAL"
    assert response.state_after == "ACCEPTED_TECHNICAL"
    assert response.idempotent_replay is False
    
    # Verify dual-log was written
    mock_audit_store.append_research.assert_called_once()
    mock_audit_store.append_compliance.assert_called_once()
    
    # Check that research event passed has the correct fields
    research_event = mock_audit_store.append_research.call_args[0][0]
    assert research_event["activity"] == "ACCEPT_TECHNICAL"
    assert research_event["state_after"] == "ACCEPTED_TECHNICAL"

def test_rbac_rejection(mock_audit_store, base_request):
    service = ReviewWorkflowAppService(mock_audit_store)
    # Use an invalid role
    invalid_req = ReviewActionRequest(**{**base_request.__dict__, "reviewer_role": "VIEWER"})
    
    with pytest.raises(PermissionError, match="REVIEW_ACTION_ROLE_FORBIDDEN"):
        service.execute_action(invalid_req)
        
    mock_audit_store.append_research.assert_not_called()

def test_missing_reason_code(mock_audit_store, base_request):
    service = ReviewWorkflowAppService(mock_audit_store)
    # Action requires reason but reason is missing
    invalid_req = ReviewActionRequest(**{**base_request.__dict__, "action": "OVERRIDE_WITH_REASON", "reason_code": None})
    
    with pytest.raises(ValueError, match="REVIEW_ACTION_REASON_REQUIRED"):
        service.execute_action(invalid_req)
        
def test_idempotency(mock_audit_store, base_request):
    service = ReviewWorkflowAppService(mock_audit_store)
    
    # First, test we execute logic if not found
    service.execute_action(base_request)
    mock_audit_store.append_research.assert_called_once()
    
    # Now simulate idempotency key match
    action_id = logical_action_id(base_request)
    mock_event = {
        "logical_action_id": action_id,
        "state_before": "REVIEWING",
        "state_after": "ACCEPTED_TECHNICAL",
        "activity": "ACCEPT_TECHNICAL",
        "transition_action": "ACCEPT_TECHNICAL",
        "event_id": "research_event_1",
        "compliance_event_id": "compliance_event_1",
        "reversible": False
    }
    mock_audit_store.research.find.return_value = mock_event
    
    # Execute again
    response = service.execute_action(base_request)
    
    assert response.idempotent_replay is True
    # Append should NOT be called again
    assert mock_audit_store.append_research.call_count == 1

def test_dual_log_eventual_consistency(mock_audit_store, base_request):
    service = ReviewWorkflowAppService(mock_audit_store)
    
    # Simulate compliance stream failure
    mock_audit_store.append_compliance.side_effect = Exception("DB Timeout")
    
    with pytest.raises(RuntimeError, match="COMPLIANCE_AUDIT_APPEND_FAILED_AFTER_RESEARCH_APPEND"):
        service.execute_action(base_request)
        
    # Verify research log was STILL written to
    mock_audit_store.append_research.assert_called_once()
