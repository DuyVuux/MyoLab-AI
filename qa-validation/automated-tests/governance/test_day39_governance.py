import sys
import json
import pytest
from pathlib import Path

# Add governance path to sys.path
root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(root / "ai-core" / "governance"))

from day39.models import RegistryStateEnum, RerunStatusEnum
from day39.registry import validate_registry_state, load_and_validate_manifest
from day39.environment import audit_uv_lock
from day39.rerun import compare_predictions, compare_metric

def test_registry_state_validation():
    # Valid states
    assert validate_registry_state("COMPLETED") is True
    assert validate_registry_state("DRAFT") is True

    # Prohibited clinical states - MUST raise PermissionError
    with pytest.raises(PermissionError, match="PROHIBITED_CLINICAL_STATE|Prohibited clinical state"):
        validate_registry_state("CLINICALLY_VALIDATED")
    
    with pytest.raises(PermissionError, match="PROHIBITED_CLINICAL_STATE|Prohibited clinical state"):
        validate_registry_state("APPROVED_FOR_PATIENT_USE")
        
    # Unknown states - MUST raise ValueError
    with pytest.raises(ValueError, match="Unknown registry state"):
        validate_registry_state("UNKNOWN_STATE_123")

def test_uv_lock_missing(tmp_path):
    # Test missing lockfile
    result = audit_uv_lock(tmp_path / "uv.lock")
    assert result["pass"] is False
    assert result["reason"] == "UV_LOCK_MISSING"

def test_uv_lock_invalid(tmp_path):
    # Test non-resolver generated lockfile
    lock_file = tmp_path / "uv.lock"
    lock_file.write_text("fake lock file content that is short")
    result = audit_uv_lock(lock_file)
    assert result["pass"] is False
    assert result["reason"] == "UV_LOCK_NOT_RESOLVER_GENERATED"

def test_uv_lock_valid(tmp_path):
    # Test a valid looking lockfile
    lock_file = tmp_path / "uv.lock"
    valid_content = "version: 1\n" + ("x" * 150)
    lock_file.write_text(valid_content)
    result = audit_uv_lock(lock_file)
    assert result["pass"] is True
    assert "sha256" in result
    assert result["bytes"] == len(valid_content)

def test_rerun_compare_predictions():
    # Exact match
    res = compare_predictions([1, 2, 3], [1, 2, 3])
    assert res["status"] == RerunStatusEnum.EXACT_MATCH
    assert res["prediction_mismatch_count"] == 0
    
    # Mismatch
    res = compare_predictions([1, 2, 3], [1, 2, 4])
    assert res["status"] == RerunStatusEnum.MISMATCH
    assert res["prediction_mismatch_count"] == 1
    
    # Count mismatch
    res = compare_predictions([1, 2], [1, 2, 3])
    assert res["status"] == RerunStatusEnum.MISMATCH
    assert res["reason"] == "ROW_COUNT_MISMATCH"

def test_rerun_compare_metric():
    # Within tolerance
    res = compare_metric("accuracy", 0.85, 0.85 + 1e-12, tolerance=1e-10)
    assert res.within_tolerance is True
    
    # Outside tolerance
    res = compare_metric("accuracy", 0.85, 0.85 + 1e-9, tolerance=1e-10)
    assert res.within_tolerance is False

def test_manifest_validation(tmp_path):
    # Test strict Pydantic validation for manifest
    valid_manifest = {
        "run_id": "run-001",
        "created_at_utc": "2026-08-04T00:00:00Z",
        "git_commit": "abcdef1234567890",
        "environment_lock_sha256": "hash_env",
        "dataset_ids": ["dataset1"],
        "data_manifest_sha256": "hash_data",
        "split_manifest_sha256": "hash_split",
        "feature_contract_sha256": "hash_feature",
        "model_config_sha256": "hash_model",
        "random_seeds": {
            "split_seed": 42,
            "model_seed": 42
        },
        "command": ["python", "train.py"],
        "sealed_test_opened": False,
        "pooled_training": False,
        "registry_state": "COMPLETED"
    }
    
    manifest_file = tmp_path / "manifest.json"
    manifest_file.write_text(json.dumps(valid_manifest))
    
    manifest = load_and_validate_manifest(manifest_file)
    assert manifest.run_id == "run-001"
    assert manifest.registry_state == RegistryStateEnum.COMPLETED

    # Test prohibited clinical state
    invalid_manifest = dict(valid_manifest)
    invalid_manifest["registry_state"] = "CLINICALLY_VALIDATED"
    manifest_file.write_text(json.dumps(invalid_manifest))
    
    with pytest.raises(PermissionError):
        load_and_validate_manifest(manifest_file)
