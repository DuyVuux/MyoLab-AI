"""Day 32 — Core gate decision logic.

The core gate determines whether optional models may proceed.
It checks structural completeness, not model quality:
  • All six core models must have a status.
  • Both dummy baselines must be present.
  • Safety invariants must hold (no leakage, no sealed test reads).

Reference: Execution Plan §8 (Bước 8 — Core Gate).
"""
from __future__ import annotations

from .model_factory import CORE_MODEL_IDS


def decide_core_gate(
    results: list[dict],
    *,
    test_signal_rows_read: int = 0,
    pooled_rows: int = 0,
) -> dict:
    """Evaluate core gate pass/fail from model run results.

    Parameters
    ----------
    results : list[dict]
        Each dict must have ``model_id`` and ``status`` keys.
    test_signal_rows_read : int
        Number of sealed test rows read (must be 0).
    pooled_rows : int
        Number of pooled cross-dataset rows (must be 0).

    Returns
    -------
    dict
        Gate status with schema_version, status, and diagnostic fields.
    """
    by_id = {r["model_id"]: r for r in results}
    missing = [
        model_id for model_id in CORE_MODEL_IDS
        if model_id not in by_id
    ]
    failures = [
        model_id for model_id in CORE_MODEL_IDS
        if model_id in by_id and by_id[model_id].get("status") != "COMPLETED"
    ]

    # Safety invariant checks  (Execution Plan §8)
    safety_violations: list[str] = []
    if test_signal_rows_read != 0:
        safety_violations.append(
            f"SEALED_TEST_READ:{test_signal_rows_read}"
        )
    if pooled_rows != 0:
        safety_violations.append(f"POOLED_ROWS:{pooled_rows}")

    if missing or safety_violations:
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
        "safety_violations": safety_violations,
        "dummy_majority_present": "dummy_majority" in by_id,
        "dummy_stratified_present": "dummy_stratified" in by_id,
        "optional_models_may_run": status != "CORE_GATE_BLOCKED",
    }
