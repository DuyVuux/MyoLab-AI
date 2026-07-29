from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day29.feature_eligibility import assess_feature_eligibility
from day29.readiness import decide_readiness


def test_frequency_requires_full_provenance():
    result = assess_feature_eligibility({
        "signal_loadable": True,
        "unit_verified": True,
        "channel_mapping_verified": True,
        "sampling_rate_verified": True,
        "raw_or_near_raw_verified": False,
        "prior_filtering_known": True,
        "window_policy_locked": True,
        "channel_order_verified": True,
    })
    assert result["F1_sparse_classical_core"]["eligible"] is True
    assert result["F2_frequency_extension"]["eligible"] is False
    assert result["MFCV"]["eligible"] is False


def test_readiness_fails_closed():
    result = decide_readiness({})
    assert result["status"] == "BLOCKED_WITH_EVIDENCE"


def test_readiness_go_when_all_checks_pass():
    checks = {
        "source_and_license_verified": True,
        "archive_and_file_hashes_verified": True,
        "metadata_index_verified": True,
        "label_mapping_frozen": True,
        "partition_guard_passed": True,
        "test_seal_present_and_unopened": True,
        "unit_sampling_channel_provenance_sufficient": True,
        "eda_completed_on_train_validation": True,
        "cross_day_audit_completed": True,
        "feature_eligibility_frozen": True,
        "critical_duplicate_or_group_overlap": False,
        "hierarchy_verified_or_documented_partial": True,
    }
    assert decide_readiness(checks)["status"] == "GO_FOR_DAY30_HARMONIZATION"
