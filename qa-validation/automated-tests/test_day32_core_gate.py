"""Day 32 — Core gate tests.

Verifies:
  • CORE_GATE_PASS when all models complete
  • CORE_GATE_PASS_WITH_MODEL_FAILURES when some fail
  • CORE_GATE_BLOCKED when models are missing
  • CORE_GATE_BLOCKED when safety violations exist
  • Dummy baselines are always checked
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "modeling"))

from day32.core_gate import decide_core_gate
from day32.model_factory import CORE_MODEL_IDS


def test_core_gate_pass():
    results = [{"model_id": m, "status": "COMPLETED"} for m in CORE_MODEL_IDS]
    gate = decide_core_gate(results)
    assert gate["status"] == "CORE_GATE_PASS"
    assert gate["optional_models_may_run"]
    assert gate["dummy_majority_present"]
    assert gate["dummy_stratified_present"]
    assert gate["missing_models"] == []
    assert gate["failed_models"] == []
    assert gate["safety_violations"] == []


def test_core_gate_pass_with_failures():
    """One model failing should be PASS_WITH_MODEL_FAILURES, not BLOCKED."""
    results = [{"model_id": m, "status": "COMPLETED"} for m in CORE_MODEL_IDS]
    # Make one fail
    results[2]["status"] = "FAILED"
    gate = decide_core_gate(results)
    assert gate["status"] == "CORE_GATE_PASS_WITH_MODEL_FAILURES"
    assert gate["optional_models_may_run"]
    assert len(gate["failed_models"]) == 1


def test_core_gate_blocked_missing_model():
    """Missing a core model should block the gate."""
    results = [
        {"model_id": m, "status": "COMPLETED"}
        for m in CORE_MODEL_IDS
        if m != "lda_shrinkage"  # Omit one
    ]
    gate = decide_core_gate(results)
    assert gate["status"] == "CORE_GATE_BLOCKED"
    assert not gate["optional_models_may_run"]
    assert "lda_shrinkage" in gate["missing_models"]


def test_core_gate_blocked_on_sealed_test_read():
    """Reading sealed test rows must block the gate."""
    results = [{"model_id": m, "status": "COMPLETED"} for m in CORE_MODEL_IDS]
    gate = decide_core_gate(results, test_signal_rows_read=100)
    assert gate["status"] == "CORE_GATE_BLOCKED"
    assert any("SEALED_TEST_READ" in v for v in gate["safety_violations"])


def test_core_gate_blocked_on_pooled_rows():
    """Pooled rows must block the gate."""
    results = [{"model_id": m, "status": "COMPLETED"} for m in CORE_MODEL_IDS]
    gate = decide_core_gate(results, pooled_rows=50)
    assert gate["status"] == "CORE_GATE_BLOCKED"
    assert any("POOLED_ROWS" in v for v in gate["safety_violations"])


def test_core_gate_schema_version():
    results = [{"model_id": m, "status": "COMPLETED"} for m in CORE_MODEL_IDS]
    gate = decide_core_gate(results)
    assert gate["schema_version"] == "day32-core-gate.v1"
