import pytest
from offline_pipeline_v0_1 import (
    OfflinePipeline, 
    PipelineStateMachine, 
    verify_model_bundle,
    GovernanceError,
    TransitionError
)

@pytest.fixture
def valid_bundle():
    return {
        "model_id": "model-123",
        "registry_state": "RESEARCH_BASELINE",
        "rerun_status": "EXACT_MATCH",
        "model_card_present": True,
        "bundle_sha256": "abc123hash"
    }

@pytest.fixture
def valid_config():
    return {"mode": "offline"}

# --- Governance Guards Tests ---

def test_verify_model_bundle_success(valid_bundle):
    assert verify_model_bundle(valid_bundle) is True

def test_verify_model_bundle_missing_fields():
    with pytest.raises(GovernanceError, match="MODEL_BUNDLE_MISSING"):
        verify_model_bundle({"model_id": "model-123"})

def test_verify_model_bundle_invalid_registry(valid_bundle):
    valid_bundle["registry_state"] = "PROD_APPROVED" # Not allowed in offline v0.1
    with pytest.raises(GovernanceError, match="MODEL_STATE_NOT_ELIGIBLE"):
        verify_model_bundle(valid_bundle)

def test_verify_model_bundle_invalid_rerun(valid_bundle):
    valid_bundle["rerun_status"] = "FAILED" 
    with pytest.raises(GovernanceError, match="RERUN_NOT_VERIFIED"):
        verify_model_bundle(valid_bundle)

def test_verify_model_bundle_no_model_card(valid_bundle):
    valid_bundle["model_card_present"] = False 
    with pytest.raises(GovernanceError, match="MODEL_CARD_MISSING"):
        verify_model_bundle(valid_bundle)


# --- State Machine Tests ---

def test_state_machine_valid_transitions():
    sm = PipelineStateMachine()
    assert sm.current_state == "RECEIVED"
    sm.transition("PREFLIGHT_PASSED")
    sm.transition("IMPORTED")
    sm.transition("QC_PASSED")
    assert sm.current_state == "QC_PASSED"

def test_state_machine_invalid_transition():
    sm = PipelineStateMachine()
    with pytest.raises(TransitionError):
        sm.transition("REPORTED") # Cannot jump to REPORTED from RECEIVED

def test_state_machine_terminal_state():
    sm = PipelineStateMachine()
    sm.force_fail()
    assert sm.current_state == "FAILED"
    with pytest.raises(TransitionError, match="Cannot transition from terminal state"):
        sm.transition("QC_PASSED")

def test_state_machine_history_tracking():
    sm = PipelineStateMachine()
    sm.transition("PREFLIGHT_PASSED")
    sm.transition("IMPORTED")
    sm.transition("QC_FAILED")
    sm.transition("ABSTAINED")
    assert sm.history == ["RECEIVED", "PREFLIGHT_PASSED", "IMPORTED", "QC_FAILED", "ABSTAINED"]


# --- Orchestrator & Pipeline Tests ---

def test_pipeline_initialization_failure(valid_config, valid_bundle):
    valid_bundle["registry_state"] = "INVALID"
    with pytest.raises(GovernanceError):
        OfflinePipeline(valid_config, valid_bundle)

def test_pipeline_run_synthetic_pass(valid_config, valid_bundle):
    pipeline = OfflinePipeline(valid_config, valid_bundle)
    session = {"session_id": "ses-001", "quality_status": "pass", "confidence": 0.9}
    report = pipeline.run_synthetic(session)
    
    assert report["status"] == "REPORTED"
    assert report["inference"]["decision"] == "accept"
    assert report["taskc"]["supportability"] == "SUPPORTED"
    assert "REPORTED" in report["history"]

def test_pipeline_run_synthetic_quality_warning(valid_config, valid_bundle):
    pipeline = OfflinePipeline(valid_config, valid_bundle)
    session = {"session_id": "ses-001-warn", "quality_status": "warning", "confidence": 0.9}
    report = pipeline.run_synthetic(session)
    
    assert report["status"] == "REPORTED"
    assert report["inference"]["decision"] == "accept"
    assert "QC_WARNING" in report["history"]

def test_pipeline_run_synthetic_quality_fail(valid_config, valid_bundle):
    pipeline = OfflinePipeline(valid_config, valid_bundle)
    session = {"session_id": "ses-002", "quality_status": "fail", "confidence": 0.9}
    report = pipeline.run_synthetic(session)
    
    assert report["status"] == "ABSTAINED"
    assert report["inference"]["decision"] == "abstain_quality_fail"
    assert "QC_FAILED" in report["history"]

def test_pipeline_run_synthetic_low_confidence(valid_config, valid_bundle):
    pipeline = OfflinePipeline(valid_config, valid_bundle)
    session = {"session_id": "ses-003", "quality_status": "pass", "confidence": 0.2, "threshold": 0.5}
    report = pipeline.run_synthetic(session)
    
    assert report["status"] == "ABSTAINED"
    assert report["inference"]["decision"] == "abstain_low_confidence"

def test_pipeline_fail_closed_mechanism(valid_config, valid_bundle, monkeypatch):
    """Stress test: Inject an unexpected error to ensure it fails closed to FAILED state."""
    pipeline = OfflinePipeline(valid_config, valid_bundle)
    
    # Mock transition to artificially crash
    def mocked_transition(*args, **kwargs):
        raise RuntimeError("Simulated Crash")
        
    import offline_pipeline_v0_1.state
    monkeypatch.setattr(offline_pipeline_v0_1.state.PipelineStateMachine, "transition", mocked_transition)
    
    session = {"session_id": "ses-crash"}
    report = pipeline.run_synthetic(session)
    
    assert report["status"] == "FAILED"
    assert report["inference"]["decision"] == "error_unexpected"
    assert "FAILED" in report["history"]

def test_pipeline_unsupported_modes(valid_config, valid_bundle):
    pipeline = OfflinePipeline(valid_config, valid_bundle)
    with pytest.raises(NotImplementedError):
        pipeline.run_normalized({"session_id": "1"})
    with pytest.raises(NotImplementedError):
        pipeline.run_raw_index({"session_id": "1"})
