import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"ai-core/context"))
from day36.engine import evaluate_context,adjust_confidence,final_route,language_guard

def ev(statuses,quality="pass",protocol=True):
    return evaluate_context({"quality_status":quality,"protocol_supported":protocol,
                             "lanes":{str(i):{"status":s} for i,s in enumerate(statuses)}})[0]

def test_states():
    assert ev(["supportive","supportive","supportive"])=="FATIGUE_CONTEXT_SUPPORTED"
    assert ev(["supportive","neutral","neutral"])=="POSSIBLE_FATIGUE_CONTEXT"
    assert ev(["supportive","contradictory"])=="CONFLICTING_EVIDENCE"
    assert ev(["supportive"],quality="fail")=="QUALITY_BLOCKED"

def test_confidence():assert adjust_confidence(.8,"POSSIBLE_FATIGUE_CONTEXT","pass")<=.8
def test_route():assert final_route("QUALITY_BLOCKED","accept")=="ABSTAIN_QUALITY_FAIL"
def test_language():
    assert language_guard("Có bằng chứng bối cảnh, cần human review.")
    assert not language_guard("Fatigue diagnosis confirmed.")
