from typing import List, Tuple
from .schema import ContextInputEvent, ContextOutputEvent

FORBIDDEN = ("diagnosed fatigue", "fatigue diagnosis", "treatment recommendation", "treatment")

def evaluate_context(evidence: ContextInputEvent) -> Tuple[str, List[str]]:
    """
    Evaluates context state based on the deterministic rules in DAY36_EXECUTION_PLAN.md.
    """
    if evidence.quality_status == "fail":
        return "QUALITY_BLOCKED", ["QUALITY_FAIL"]
        
    if not evidence.protocol_supported:
        return "UNSUPPORTED_PROTOCOL", ["UNSUPPORTED_PROTOCOL"]
        
    lanes = evidence.lanes
    spectral = lanes.get("spectral", None)
    amplitude = lanes.get("amplitude", None)
    performance = lanes.get("performance", None)
    
    s_status = spectral.status if spectral else "missing"
    a_status = amplitude.status if amplitude else "missing"
    p_status = performance.status if performance else "missing"
    
    if s_status == "missing" and a_status == "missing" and p_status == "missing":
        return "INSUFFICIENT_EVIDENCE", ["ALL_CORE_LANES_MISSING"]
        
    if s_status == "supportive" and a_status == "supportive" and p_status == "supportive":
        return "FATIGUE_CONTEXT_SUPPORTED", ["MULTI_LANE_SUPPORT_FULL"]
        
    if s_status == "supportive" and a_status == "neutral" and p_status == "supportive":
        return "POSSIBLE_FATIGUE_CONTEXT", ["MULTI_LANE_SUPPORT_PARTIAL"]
        
    if s_status == "supportive" and a_status == "contradictory":
        return "CONFLICTING_EVIDENCE", ["SPECTRAL_AMPLITUDE_CONFLICT"]
        
    # Robust deterministic handling for combinations not explicitly spelled out
    supportive_count = sum(1 for status in [s_status, a_status, p_status] if status == "supportive")
    contradictory_count = sum(1 for status in [s_status, a_status, p_status] if status == "contradictory")
    
    if contradictory_count > 0:
        return "CONFLICTING_EVIDENCE", ["GENERAL_CONFLICT"]
        
    if supportive_count > 0:
        return "POSSIBLE_FATIGUE_CONTEXT", ["GENERAL_POSSIBLE_CONTEXT"]
        
    return "NO_CONTEXT_EVIDENCE", ["NO_SUPPORTIVE_PATTERN"]

def adjust_confidence(original: float, state: str, quality_status: str, metadata_complete: bool) -> float:
    # Handle hard gate for unsupported protocol
    if state == "UNSUPPORTED_PROTOCOL":
        return 0.0
        
    penalties = {
        "QUALITY_BLOCKED": 1.0, 
        "POSSIBLE_FATIGUE_CONTEXT": 0.05,
        "CONFLICTING_EVIDENCE": 0.15, 
        "INSUFFICIENT_EVIDENCE": 0.10,
        "FATIGUE_CONTEXT_SUPPORTED": 0.0,
        "NO_CONTEXT_EVIDENCE": 0.0
    }
    
    penalty = penalties.get(state, 0.0)
    
    if quality_status == "warning":
        penalty += 0.10
    if not metadata_complete:
        penalty += 0.10
        
    adjusted = max(0.0, float(original) - penalty)
    
    # Confidence may never increase
    if adjusted > original:
        raise RuntimeError("CONFIDENCE_INCREASE_BLOCKED")
        
    return adjusted

def final_route(state: str, abstention_decision: str) -> str:
    if state == "UNSUPPORTED_PROTOCOL":
        return "ABSTAIN_UNSUPPORTED_PROTOCOL"
        
    if state == "QUALITY_BLOCKED":
        return "ABSTAIN_QUALITY_FAIL"
        
    if str(abstention_decision).startswith("abstain"):
        return "ABSTAIN_LOW_CONFIDENCE"
        
    if state == "CONFLICTING_EVIDENCE":
        return "ABSTAIN_CONFLICTING_EVIDENCE"
        
    if state in {"POSSIBLE_FATIGUE_CONTEXT", "FATIGUE_CONTEXT_SUPPORTED", "INSUFFICIENT_EVIDENCE"}:
        return "CONTINUE_WITH_WARNING"
        
    return "CONTINUE_WITH_CONTEXT"

def language_guard(text: str) -> bool:
    lower = text.lower()
    return not any(term in lower for term in FORBIDDEN)

def process_context(event: ContextInputEvent) -> ContextOutputEvent:
    state, reason_codes = evaluate_context(event)
    
    eff_conf = adjust_confidence(
        original=event.calibrated_confidence,
        state=state,
        quality_status=event.quality_status,
        metadata_complete=event.metadata_complete
    )
    
    route = final_route(state, event.abstention_decision)
    
    summary = f"Evaluated context for {event.session_id}. State: {state}. Route: {route}."
    if not language_guard(summary):
        raise ValueError("Language guard failed on generated summary.")
        
    return ContextOutputEvent(
        context_state=state,
        supportability="supported" if event.protocol_supported else "unsupported",
        evidence_lanes=event.lanes,
        original_confidence=event.calibrated_confidence,
        effective_confidence=eff_conf,
        final_route=route,
        reason_codes=reason_codes,
        human_readable_summary=summary,
        provenance=event.provenance_hashes
    )
