import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../services/evidence-service/src")))

from application.evidence_reader import EvidenceReadService, ApprovedLocalResearchStore

@pytest.fixture
def temp_research_dir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)

@pytest.fixture
def mock_session_bundle():
    return {
        "session_id": "case_123",
        "claim_scope": "RESEARCH_ONLY",
        "source_refs": ["ref_1", "ref_2"],
        "qc": {"signal_quality": "PASS", "supportability": "SUPPORTED"},
        "processing": {"outcome": "COMPLETED", "manifest_id": "m1"},
        "metrics": [
            {
                "metric_name": "mvc_amplitude",
                "status": "AVAILABLE",
                "value": 42.0,
                "reason_codes": []
            },
            {
                "metric_name": "fatigue_index",
                "status": "NOT_AVAILABLE",
                "value": None,
                "reason_codes": ["NOISY_SIGNAL"]
            }
        ],
        "distribution_support": {"status": "SUPPORTED"},
        "uncertainty": {"uncertainty_type": "NOT_APPLICABLE"},
        "limitations": [],
        "unsupported_capabilities": []
    }

def test_get_case_summary(mock_session_bundle):
    service = EvidenceReadService(mock_session_bundle)
    env = service.get_case_summary("case_123")
    
    assert env.status == "AVAILABLE"
    assert env.value is not None
    assert env.value["case_id"] == "case_123"
    assert env.value["claim_scope"] == "RESEARCH_ONLY"

def test_get_case_summary_wrong_id(mock_session_bundle):
    service = EvidenceReadService(mock_session_bundle)
    env = service.get_case_summary("wrong_case")
    
    assert env.status == "NOT_AVAILABLE"
    assert env.value is None
    assert "CASE_NOT_FOUND" in env.reason_codes

def test_get_metric_preserves_semantics(mock_session_bundle):
    service = EvidenceReadService(mock_session_bundle)
    
    # Available metric
    env = service.get_metric("case_123", "mvc_amplitude")
    assert env.status == "AVAILABLE"
    assert env.value["value"] == 42.0
    
    # Unavailable metric (must preserve None and reason codes)
    env2 = service.get_metric("case_123", "fatigue_index")
    assert env2.status == "AVAILABLE"  # The metric record is available to read
    assert env2.value["status"] == "NOT_AVAILABLE" # But its internal status is NOT_AVAILABLE
    assert env2.value["value"] is None
    assert "NOISY_SIGNAL" in env2.value["reason_codes"]
    
    # Non-existent metric
    env3 = service.get_metric("case_123", "unknown")
    assert env3.status == "NOT_AVAILABLE"
    assert "METRIC_NOT_FOUND" in env3.reason_codes

def test_pagination(mock_session_bundle):
    # Add many metrics
    bundle = dict(mock_session_bundle)
    bundle["metrics"] = [{"metric_name": f"m{i}", "status": "AVAILABLE"} for i in range(1, 26)]
    
    service = EvidenceReadService(bundle)
    
    # First page
    env = service.list_metrics("case_123", page=1, page_size=10)
    assert env.status == "AVAILABLE"
    page = env.value
    assert page.page == 1
    assert page.page_size == 10
    assert page.total == 25
    assert len(page.items) == 10
    assert page.has_next is True
    
    # Third page (last)
    env3 = service.list_metrics("case_123", page=3, page_size=10)
    page3 = env3.value
    assert page3.page == 3
    assert len(page3.items) == 5
    assert page3.has_next is False

def test_raw_window_path_traversal_protection(temp_research_dir):
    store = ApprovedLocalResearchStore(temp_research_dir)
    
    # Try traversal
    with pytest.raises(PermissionError, match="RAW_PATH_TRAVERSAL_FORBIDDEN"):
        store._resolve("../outside.json")
        
    with pytest.raises(PermissionError, match="RAW_PATH_TRAVERSAL_FORBIDDEN"):
        store._resolve("/absolute/path.json")

def test_raw_window_read(temp_research_dir, mock_session_bundle):
    # Setup dummy raw data
    raw_file = temp_research_dir / "valid.json"
    raw_file.write_text(json.dumps([1.0, 2.0, 3.0, 4.0, 5.0]))
    
    store = ApprovedLocalResearchStore(temp_research_dir)
    service = EvidenceReadService(mock_session_bundle, raw_store=store)
    
    # Successful read
    env = service.get_raw_window(
        "case_123", 
        requester_role="RESEARCHER", 
        source_ref="ref_1", 
        relative_path="valid.json", 
        start=1, 
        end=4
    )
    
    assert env.status == "AVAILABLE"
    assert env.value["values"] == (2.0, 3.0, 4.0)
    # Ensure local path is not leaked
    assert env.value["local_path"] is None

def test_raw_window_forbidden_role(temp_research_dir, mock_session_bundle):
    store = ApprovedLocalResearchStore(temp_research_dir)
    service = EvidenceReadService(mock_session_bundle, raw_store=store)
    
    env = service.get_raw_window(
        "case_123", 
        requester_role="VIEWER", # Not in RAW_ROLES
        source_ref="ref_1", 
        relative_path="valid.json", 
        start=0, 
        end=2
    )
    
    assert env.status == "FORBIDDEN"
    assert "RAW_RESEARCH_ACCESS_FORBIDDEN" in env.reason_codes

def test_reconstruct_case(mock_session_bundle):
    mock_event_store = MagicMock()
    mock_event_store.timeline.return_value = [{"event_id": "e1"}, {"event_id": "e2"}]
    
    service = EvidenceReadService(mock_session_bundle, event_store=mock_event_store)
    
    env = service.reconstruct_case("case_123")
    assert env.status == "AVAILABLE"
    
    data = env.value
    assert data["summary"]["case_id"] == "case_123"
    assert len(data["metrics"]) == 2
    assert len(data["timeline"]) == 2
