REQUIRED_REAL={"day32_commit_closed","prediction_inventory_present","prediction_hashes_verified",
"fold_hashes_verified","prediction_gate_passed","repetition_metrics_generated",
"subject_metrics_generated","failure_registry_generated","sealed_test_unopened","pooled_evaluation_disabled"}

def decide_readiness(checks,known_failures=0):
    missing=sorted(k for k in REQUIRED_REAL if checks.get(k) is not True)
    if not checks.get("prediction_inventory_present"):
        status="TOOLING_READY_REAL_EVALUATION_BLOCKED"
    elif missing: status="BLOCKED_WITH_EVIDENCE"
    elif known_failures: status="GO_FOR_DAY34_WITH_KNOWN_FAILURES"
    else: status="GO_FOR_DAY34_ROBUSTNESS_CALIBRATION"
    return {"schema_version":"day33-readiness-decision.v1","status":status,
            "missing_checks":missing,"known_failure_count":int(known_failures),
            "sealed_test_opened":False,"pooled_evaluation_executed":False,
            "fatigue_inference_allowed":False,"clinical_use_allowed":False,
            "registry_state":"research"}
