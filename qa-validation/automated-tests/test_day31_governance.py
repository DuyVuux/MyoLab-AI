from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day31.preflight import validate_preflight
from day31.readiness import decide_feature_gate


def _config() -> dict[str, object]:
    return {
        "training_allowed": False,
        "model_fitting_allowed": False,
        "scaler_fitting_allowed": False,
        "pooled_training_allowed": False,
        "test_signal_access_allowed": False,
        "test_set_opened": False,
        "fatigue_inference_allowed": False,
        "clinical_use_allowed": False,
        "input_day30": {
            "accepted_statuses": [
                "GO_FOR_DAY31_SEPARATE_BASELINE_SMOKE",
                "GO_FOR_DAY31_SEPARATE_BASELINE_FULL",
            ]
        },
        "visible_partitions": ["train", "validation"],
        "forbidden_partitions": ["test", "sealed_test", "outer_test"],
    }


def _day30_readiness() -> dict[str, object]:
    return {
        "status": "GO_FOR_DAY31_SEPARATE_BASELINE_SMOKE",
        "training_allowed": False,
        "pooled_training_allowed": False,
        "test_set_opened": False,
        "fatigue_inference_allowed": False,
        "clinical_use_allowed": False,
    }


def test_preflight_accepts_day30_smoke_without_granting_training() -> None:
    result = validate_preflight(_config(), _day30_readiness())

    assert result["pass"] is True
    assert result["feature_engineering_allowed"] is True
    assert result["training_allowed"] is False
    assert result["test_signal_access_allowed"] is False


@pytest.mark.parametrize(
    "unsafe_flag",
    [
        "training_allowed",
        "model_fitting_allowed",
        "scaler_fitting_allowed",
        "pooled_training_allowed",
        "test_signal_access_allowed",
        "test_set_opened",
        "fatigue_inference_allowed",
        "clinical_use_allowed",
    ],
)
def test_preflight_rejects_every_unsafe_config_flag(unsafe_flag: str) -> None:
    config = _config()
    config[unsafe_flag] = True

    result = validate_preflight(config, _day30_readiness())
    assert result["pass"] is False
    assert f"{unsafe_flag}_must_be_false" in result["errors"]


def test_preflight_rejects_unsafe_or_unknown_upstream_readiness() -> None:
    readiness = _day30_readiness()
    readiness["test_set_opened"] = True
    result = validate_preflight(_config(), readiness)
    assert result["pass"] is False
    assert "day30_test_set_opened_must_be_false" in result["errors"]

    readiness = _day30_readiness()
    readiness["status"] = "BLOCKED_WITH_EVIDENCE"
    result = validate_preflight(_config(), readiness)
    assert result["pass"] is False
    assert "day30_status_not_accepted" in result["errors"]


def _gate_evidence() -> dict[str, object]:
    return {
        "preflight": {"pass": True},
        "contract_validation": {"pass": True, "feature_count": 14},
        "golden_tests": {"pass": True},
        "mendeley_smoke": {"pass": True, "feature_dimensions": 42},
        "grabmyo_smoke": {"pass": True, "feature_dimensions": 392},
        "quality": {"pass": True},
        "stress": {"pass": True},
        "manifest": {"pass": True},
        "test_signal_rows_read": 0,
        "training_executed": False,
        "model_fitting_executed": False,
        "pooled_training_executed": False,
        "full_materialization_complete": False,
        "dependency_lock_resolved": False,
        "day32_training_authorization_present": False,
    }


def test_gate_requires_stress_and_never_overclaims_full() -> None:
    smoke = decide_feature_gate(_gate_evidence())
    assert smoke["status"] == "GO_FOR_DAY32_SEPARATE_BASELINE_SMOKE"
    assert smoke["training_allowed"] is False
    assert smoke["test_set_opened"] is False

    failed = _gate_evidence()
    failed["stress"] = {"pass": False}
    blocked = decide_feature_gate(failed)
    assert blocked["status"] == "BLOCKED_WITH_EVIDENCE"
    assert "stress" in blocked["failed_gates"]

    full = _gate_evidence()
    full.update(
        {
            "full_materialization_complete": True,
            "dependency_lock_resolved": True,
            "day32_training_authorization_present": True,
        }
    )
    decision = decide_feature_gate(full)
    assert decision["status"] == "GO_FOR_DAY32_SEPARATE_BASELINE_FULL"


def test_gate_rejects_any_execution_of_forbidden_actions() -> None:
    for field in (
        "training_executed",
        "model_fitting_executed",
        "pooled_training_executed",
    ):
        evidence = copy.deepcopy(_gate_evidence())
        evidence[field] = True
        decision = decide_feature_gate(evidence)
        assert decision["status"] == "BLOCKED_WITH_EVIDENCE"
        assert field in decision["failed_gates"]

    evidence = _gate_evidence()
    evidence["test_signal_rows_read"] = 1
    decision = decide_feature_gate(evidence)
    assert decision["status"] == "BLOCKED_WITH_EVIDENCE"
    assert "test_signal_rows_read" in decision["failed_gates"]

