from __future__ import annotations
from .model_factory import CORE_MODEL_IDS

def decide_core_gate(results: list[dict]) -> dict:
    by_id = {r["model_id"]: r for r in results}
    missing = [model_id for model_id in CORE_MODEL_IDS if model_id not in by_id]
    failures = [
        model_id for model_id in CORE_MODEL_IDS
        if model_id in by_id and by_id[model_id].get("status") != "COMPLETED"
    ]
    if missing:
        status = "CORE_GATE_BLOCKED"
    elif failures:
        status = "CORE_GATE_PASS_WITH_MODEL_FAILURES"
    else:
        status = "CORE_GATE_PASS"
    return {
        "schema_version": "day32-core-gate.v1",
        "status": status,
        "missing_models": missing,
        "failed_models": failures,
        "dummy_majority_present": "dummy_majority" in by_id,
        "dummy_stratified_present": "dummy_stratified" in by_id,
        "optional_models_may_run": status != "CORE_GATE_BLOCKED",
    }
