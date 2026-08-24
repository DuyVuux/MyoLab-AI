from pathlib import Path
import json
import pytest
import sys

def test_core_feature_freeze_manifest():
    repo = Path(".").resolve()
    manifest_path = repo / "qa-validation/evidence/core-feature-freeze-manifest-v1.0.json"
    assert manifest_path.is_file(), f"Missing freeze manifest: {manifest_path}"

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert data["status"] == "CORE_FEATURE_FREEZE"
    assert data["m6_r"] == "RESEARCH_ML_NOT_JUSTIFIED"
    assert data["final_r"] == "READY_WITH_LIMITATIONS"
    assert data["phase7r_tests_passed"] == 13
    assert data["ml_default"] == "OFF"
    assert data["allowed_changes_only"] == "BUG_FIXES_REVEALED_BY_UI_INTEGRATION_ONLY"

    forbidden = data["forbidden_features"]
    assert "ssl" in forbidden
    assert "transformer" in forbidden
    assert "new_classifier" in forbidden
    assert "calibration" in forbidden
    assert "conformal" in forbidden
    assert "ood_model" in forbidden
    assert "rl" in forbidden
    assert "mfcv_without_eligibility" in forbidden
    assert "clinical_prediction" in forbidden

def test_core_feature_freeze_governance_evaluator():
    repo = Path(".").resolve()
    ai_core_dir = repo / "ai-core"
    if str(ai_core_dir) not in sys.path:
        sys.path.insert(0, str(ai_core_dir))
    from governance.core_feature_freeze import evaluate_core_freeze
    status = evaluate_core_freeze(repo)
    assert status.status == "CORE_FEATURE_FREEZE"
    assert status.m6_r == "RESEARCH_ML_NOT_JUSTIFIED"
    assert status.ml_default == "OFF"
