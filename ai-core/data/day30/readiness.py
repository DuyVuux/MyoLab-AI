from __future__ import annotations

from typing import Any

CONTRACT_CHECKS = frozenset(
    {
        "input_gate_passed",
        "common_ontology_built",
        "channel_policy_validated",
        "sampling_policy_validated",
        "window_policy_validated",
        "view_registry_built",
        "storage_contract_validated",
        "test_seals_unopened",
        "pooled_training_disabled",
    }
)
FULL_CHECKS = frozenset(
    {
        "full_subject_index_verified",
        "split_hashes_verified",
        "resolved_dependency_lock_verified",
        "day31_training_authorization_present",
    }
)


def decide_readiness(checks: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(checks, dict):
        raise TypeError("checks must be a mapping")
    missing_contract = sorted(
        name for name in CONTRACT_CHECKS if checks.get(name) is not True
    )
    missing_full = sorted(
        name for name in FULL_CHECKS if checks.get(name) is not True
    )
    if missing_contract:
        status = "BLOCKED_WITH_EVIDENCE"
    elif missing_full:
        status = "GO_FOR_DAY31_SEPARATE_BASELINE_SMOKE"
    else:
        status = "GO_FOR_DAY31_SEPARATE_BASELINE_FULL"
    return {
        "schema_version": "day30-readiness-decision.v1",
        "status": status,
        "training_allowed": False,
        "pooled_training_allowed": False,
        "test_set_opened": False,
        "fatigue_inference_allowed": False,
        "mfcv_eligible": False,
        "motionlab_transfer_verified": False,
        "clinical_use_allowed": False,
        "missing_contract_checks": missing_contract,
        "missing_full_baseline_checks": missing_full,
    }

