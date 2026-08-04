import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core"))

from context.schema import ContextInputEvent, EvidenceLane
from context.engine import evaluate_context, adjust_confidence, final_route, language_guard, process_context

def test_language_guard():
    assert language_guard("Có bằng chứng bối cảnh, cần human review.")
    assert not language_guard("Fatigue diagnosis confirmed.")
    assert not language_guard("We have a diagnosed fatigue.")
    assert not language_guard("Recommend treatment.")

def test_adjust_confidence():
    # UNSUPPORTED_PROTOCOL should zero out confidence
    assert adjust_confidence(0.8, "UNSUPPORTED_PROTOCOL", "pass", True) == 0.0
    
    # QUALITY_BLOCKED penalty is 1.0 -> should result in 0.0
    assert adjust_confidence(0.8, "QUALITY_BLOCKED", "pass", True) == 0.0
    
    # Missing metadata adds 0.1 penalty to whatever base
    assert abs(adjust_confidence(0.8, "POSSIBLE_FATIGUE_CONTEXT", "pass", False) - (0.8 - 0.05 - 0.10)) < 1e-6
    
    # Quality warning adds 0.1 penalty
    assert abs(adjust_confidence(0.8, "POSSIBLE_FATIGUE_CONTEXT", "warning", True) - (0.8 - 0.05 - 0.10)) < 1e-6
    
    # Boundary tests
    # Ensure it doesn't go below 0
    assert adjust_confidence(0.1, "CONFLICTING_EVIDENCE", "warning", False) == 0.0

def test_final_route():
    assert final_route("UNSUPPORTED_PROTOCOL", "accept") == "ABSTAIN_UNSUPPORTED_PROTOCOL"
    assert final_route("QUALITY_BLOCKED", "accept") == "ABSTAIN_QUALITY_FAIL"
    assert final_route("FATIGUE_CONTEXT_SUPPORTED", "abstain") == "ABSTAIN_LOW_CONFIDENCE"
    assert final_route("CONFLICTING_EVIDENCE", "accept") == "ABSTAIN_CONFLICTING_EVIDENCE"
    assert final_route("FATIGUE_CONTEXT_SUPPORTED", "accept") == "CONTINUE_WITH_WARNING"
    assert final_route("NO_CONTEXT_EVIDENCE", "accept") == "CONTINUE_WITH_CONTEXT"

def build_evidence(spectral, amplitude, performance, quality="pass", protocol=True):
    lanes = {}
    if spectral:
        lanes["spectral"] = EvidenceLane(status=spectral)
    if amplitude:
        lanes["amplitude"] = EvidenceLane(status=amplitude)
    if performance:
        lanes["performance"] = EvidenceLane(status=performance)
        
    return ContextInputEvent(
        session_id="test", subject_id="sub1", protocol_id="p1", protocol_version="v1",
        quality_status=quality, protocol_supported=protocol,
        calibrated_confidence=0.9, abstention_decision="accept",
        lanes=lanes
    )

def test_evaluate_context_matrix():
    # Fully supported
    ev = build_evidence("supportive", "supportive", "supportive")
    state, codes = evaluate_context(ev)
    assert state == "FATIGUE_CONTEXT_SUPPORTED"
    
    # Partial support
    ev = build_evidence("supportive", "neutral", "supportive")
    state, codes = evaluate_context(ev)
    assert state == "POSSIBLE_FATIGUE_CONTEXT"
    
    # Conflict
    ev = build_evidence("supportive", "contradictory", "neutral")
    state, codes = evaluate_context(ev)
    assert state == "CONFLICTING_EVIDENCE"
    
    # All missing
    ev = build_evidence(None, None, None)
    state, codes = evaluate_context(ev)
    assert state == "INSUFFICIENT_EVIDENCE"

def test_process_context():
    ev = build_evidence("supportive", "supportive", "supportive")
    res = process_context(ev)
    assert res.context_state == "FATIGUE_CONTEXT_SUPPORTED"
    assert res.effective_confidence == 0.9  # No penalty for SUPPORTED
    assert res.final_route == "CONTINUE_WITH_WARNING"
    assert res.supportability == "supported"
    
    # Test unsupported protocol hard gate
    ev_unsup = build_evidence("supportive", "supportive", "supportive", protocol=False)
    res_unsup = process_context(ev_unsup)
    assert res_unsup.context_state == "UNSUPPORTED_PROTOCOL"
    assert res_unsup.effective_confidence == 0.0
    assert res_unsup.final_route == "ABSTAIN_UNSUPPORTED_PROTOCOL"
    assert res_unsup.supportability == "unsupported"
