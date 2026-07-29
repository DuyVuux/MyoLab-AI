from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day30.contracts import PROJECT_CLASS_ORDER
from day30.ontology import build_ontology_report, load_supported_canonical_labels
from day30.policy_validation import (
    validate_channel_policy,
    validate_sampling_policy,
    validate_storage_contract,
    validate_windowing_policy,
)
from day30.preflight import validate_pre_day30_report
from day30.readiness import CONTRACT_CHECKS, FULL_CHECKS, decide_readiness


def valid_pre_day30_report() -> dict:
    return {
        "overall_status": "GO_FOR_DAY30_HARMONIZATION",
        "governance": {
            "test_set_opened": False,
            "training_allowed": False,
            "fatigue_inference_allowed": False,
        },
        "key_findings": [
            "amplitude_scale_difference_about_40x",
            "sampling_rate_2048_vs_2000",
            "mendeley_dc_offset",
            "mendeley_ch4_low_amplitude_anomaly",
            "grabmyo_u1_u4_noise_floor",
            "channel_count_mismatch",
            "gesture_ontology_mismatch",
            "cross_day_vs_single_session",
        ],
        "datasets": {
            "mendeley": {
                "readiness_status": "GO_FOR_DAY30_HARMONIZATION",
                "test_set_opened": False,
                "test_signal_rows_read": 0,
            },
            "grabmyo": {
                "readiness_status": "GO_FOR_DAY30_HARMONIZATION",
                "test_set_opened": False,
                "test_signal_rows_read": 0,
            },
        },
    }


def test_preflight_accepts_only_two_sealed_ready_sources() -> None:
    result = validate_pre_day30_report(valid_pre_day30_report())
    assert result["pass"] is True
    assert result["test_set_opened"] is False
    assert result["training_allowed"] is False
    assert result["pooled_training_allowed"] is False


@pytest.mark.parametrize(
    ("mutation", "expected_error"),
    [
        (lambda report: report.pop("governance"), "missing_governance"),
        (
            lambda report: report["datasets"]["mendeley"].update(
                {"test_signal_rows_read": 1}
            ),
            "mendeley_test_signal_rows_must_be_zero",
        ),
        (
            lambda report: report["datasets"]["grabmyo"].update(
                {"readiness_status": "BLOCKED_WITH_EVIDENCE"}
            ),
            "grabmyo_readiness_not_go",
        ),
    ],
)
def test_preflight_fails_closed(mutation, expected_error: str) -> None:
    report = valid_pre_day30_report()
    mutation(report)
    result = validate_pre_day30_report(report)
    assert result["pass"] is False
    assert expected_error in result["errors"]


def test_real_label_dictionaries_build_verified_intersection() -> None:
    mendeley = load_supported_canonical_labels(
        ROOT
        / "data-platform/manifests/public-datasets/"
        "mendeley-4channel-hand-gesture-v2/label-dictionary.yaml"
    )
    grabmyo = load_supported_canonical_labels(
        ROOT
        / "data-platform/manifests/public-datasets/"
        "grabmyo-canonical/label-dictionary.yaml"
    )
    report = build_ontology_report(mendeley, grabmyo, PROJECT_CLASS_ORDER)
    assert report["intersection"] == [
        "rest",
        "hand_close",
        "wrist_flexion",
        "wrist_extension",
    ]
    assert report["support"]["hand_open"]["mendeley"] is False
    assert report["unknown_supervised_core_allowed"] is False


def test_conflicting_source_mapping_is_rejected(tmp_path: Path) -> None:
    dictionary = tmp_path / "labels.yaml"
    dictionary.write_text(
        """
schema_version: label-mapping.v1
mappings:
  - source_label: Same
    canonical_label: rest
    mapping_status: CONFIRMED
  - source_label: Same
    canonical_label: hand_close
    mapping_status: CONFIRMED
""".strip(),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Conflicting canonical mappings"):
        load_supported_canonical_labels(dictionary)


def test_policy_validators_accept_locked_pack_contracts() -> None:
    config_root = ROOT / "ai-core/configs"
    contract_root = ROOT / "data-platform/contracts/day30"
    assert validate_sampling_policy(
        config_root / "day30_sampling_policy.research.yaml"
    )["pass"]
    assert validate_channel_policy(
        config_root / "day30_channel_policy.research.yaml"
    )["pass"]
    assert validate_windowing_policy(
        config_root / "day30_windowing_policy.research.yaml"
    )["pass"]
    assert validate_storage_contract(
        contract_root / "storage-contract.yaml"
    )["pass"]


def test_readiness_is_fail_closed_and_never_authorizes_training() -> None:
    blocked = decide_readiness({})
    assert blocked["status"] == "BLOCKED_WITH_EVIDENCE"

    smoke_checks = {name: True for name in CONTRACT_CHECKS}
    smoke = decide_readiness(smoke_checks)
    assert smoke["status"] == "GO_FOR_DAY31_SEPARATE_BASELINE_SMOKE"
    assert smoke["training_allowed"] is False
    assert smoke["pooled_training_allowed"] is False

    full_checks = smoke_checks | {name: True for name in FULL_CHECKS}
    full = decide_readiness(full_checks)
    assert full["status"] == "GO_FOR_DAY31_SEPARATE_BASELINE_FULL"
    assert full["clinical_use_allowed"] is False
