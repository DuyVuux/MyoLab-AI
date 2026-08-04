FORBIDDEN=("diagnosed fatigue","fatigue diagnosis","treatment recommendation")

def evaluate_context(evidence):
    quality=evidence.get("quality_status","unknown")
    if quality=="fail": return "QUALITY_BLOCKED",["QUALITY_FAIL"]
    if not evidence.get("protocol_supported",False): return "UNSUPPORTED_PROTOCOL",["UNSUPPORTED_PROTOCOL"]
    statuses=[v.get("status","missing") for v in evidence.get("lanes",{}).values()]
    supportive=sum(s=="supportive" for s in statuses)
    contradictory=sum(s=="contradictory" for s in statuses)
    available=sum(s not in {"missing","unknown"} for s in statuses)
    if available==0:return "INSUFFICIENT_EVIDENCE",["NO_AVAILABLE_LANES"]
    if contradictory and supportive:return "CONFLICTING_EVIDENCE",["LANE_CONFLICT"]
    if supportive>=3:return "FATIGUE_CONTEXT_SUPPORTED",["MULTI_LANE_SUPPORT"]
    if supportive>=1:return "POSSIBLE_FATIGUE_CONTEXT",["LIMITED_LANE_SUPPORT"]
    return "NO_CONTEXT_EVIDENCE",["NO_SUPPORTIVE_PATTERN"]

def adjust_confidence(original,state,quality_status,metadata_complete=True):
    penalties={"QUALITY_BLOCKED":1.0,"POSSIBLE_FATIGUE_CONTEXT":0.05,
               "CONFLICTING_EVIDENCE":0.15,"INSUFFICIENT_EVIDENCE":0.10,
               "UNSUPPORTED_PROTOCOL":1.0}
    penalty=penalties.get(state,0.0)
    if quality_status=="warning":penalty+=0.10
    if not metadata_complete:penalty+=0.10
    adjusted=max(0.0,min(float(original),float(original)-penalty))
    if adjusted>original:raise RuntimeError("CONFIDENCE_INCREASE_BLOCKED")
    return adjusted

def final_route(state,abstention_decision):
    if state=="QUALITY_BLOCKED":return "ABSTAIN_QUALITY_FAIL"
    if state=="UNSUPPORTED_PROTOCOL":return "ABSTAIN_UNSUPPORTED_PROTOCOL"
    if str(abstention_decision).startswith("abstain"):return "ABSTAIN_LOW_CONFIDENCE"
    if state=="CONFLICTING_EVIDENCE":return "ABSTAIN_CONFLICTING_EVIDENCE"
    if state in {"POSSIBLE_FATIGUE_CONTEXT","FATIGUE_CONTEXT_SUPPORTED","INSUFFICIENT_EVIDENCE"}:
        return "CONTINUE_WITH_WARNING"
    return "CONTINUE_WITH_CONTEXT"

def language_guard(text):
    lower=text.lower()
    return not any(term in lower for term in FORBIDDEN)
