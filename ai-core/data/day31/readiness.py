"""Deterministic Feature Engineering Gate for the Day 32 handoff."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

_REQUIRED_SMOKE_GATES = (
    "preflight",
    "contract_validation",
    "golden_tests",
    "mendeley_smoke",
    "grabmyo_smoke",
    "quality",
    "stress",
    "manifest",
)
_FORBIDDEN_EXECUTION_FIELDS = (
    "training_executed",
    "model_fitting_executed",
    "pooled_training_executed",
)


def decide_feature_gate(evidence: Mapping[str, Any]) -> dict[str, Any]:
    """Produce a smoke/full/blocked decision solely from explicit evidence."""

    failed: list[str] = []
    for gate in _REQUIRED_SMOKE_GATES:
        value = evidence.get(gate)
        if not isinstance(value, Mapping) or value.get("pass") is not True:
            failed.append(gate)
    contract = evidence.get("contract_validation")
    if not isinstance(contract, Mapping) or contract.get("feature_count") != 14:
        failed.append("feature_count")
    for field in _FORBIDDEN_EXECUTION_FIELDS:
        if evidence.get(field) is not False:
            failed.append(field)
    if evidence.get("test_signal_rows_read") != 0:
        failed.append("test_signal_rows_read")

    unique_failed = sorted(set(failed))
    if unique_failed:
        status = "BLOCKED_WITH_EVIDENCE"
    else:
        full_requirements = (
            evidence.get("full_materialization_complete") is True
            and evidence.get("dependency_lock_resolved") is True
            and evidence.get("day32_training_authorization_present") is True
        )
        status = (
            "GO_FOR_DAY32_SEPARATE_BASELINE_FULL"
            if full_requirements
            else "GO_FOR_DAY32_SEPARATE_BASELINE_SMOKE"
        )

    return {
        "schema_version": "day31-readiness-decision.v1",
        "status": status,
        "pass": not unique_failed,
        "failed_gates": unique_failed,
        "training_allowed": False,
        "model_fitting_allowed": False,
        "scaler_fitting_allowed": False,
        "pooled_training_allowed": False,
        "test_signal_access_allowed": False,
        "test_set_opened": False,
        "fatigue_inference_allowed": False,
        "clinical_use_allowed": False,
    }
