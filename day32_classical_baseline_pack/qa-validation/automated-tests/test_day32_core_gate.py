from day32.core_gate import decide_core_gate
from day32.model_factory import CORE_MODEL_IDS

def test_core_gate_pass():
    results = [{"model_id": m, "status":"COMPLETED"} for m in CORE_MODEL_IDS]
    result = decide_core_gate(results)
    assert result["status"] == "CORE_GATE_PASS"
    assert result["optional_models_may_run"]
