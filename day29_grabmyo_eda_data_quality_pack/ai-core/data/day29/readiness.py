from __future__ import annotations

from typing import Any

REQUIRED_TRUE = {
    "source_and_license_verified",
    "archive_and_file_hashes_verified",
    "metadata_index_verified",
    "label_mapping_frozen",
    "partition_guard_passed",
    "test_seal_present_and_unopened",
    "unit_sampling_channel_provenance_sufficient",
    "eda_completed_on_train_validation",
    "cross_day_audit_completed",
    "feature_eligibility_frozen",
}


def decide_readiness(checks: dict[str, Any]) -> dict[str, Any]:
    missing = sorted(key for key in REQUIRED_TRUE if checks.get(key) is not True)
    overlap = checks.get("critical_duplicate_or_group_overlap") is True
    hierarchy_ok = checks.get("hierarchy_verified_or_documented_partial") is True
    if overlap:
        missing.append("critical_duplicate_or_group_overlap_must_be_false")
    if not hierarchy_ok:
        missing.append("hierarchy_verified_or_documented_partial")

    status = "GO_FOR_DAY30_HARMONIZATION" if not missing else "BLOCKED_WITH_EVIDENCE"
    return {
        "schema_version": "day29-readiness-decision.v1",
        "status": status,
        "training_allowed": False,
        "test_set_opened": False,
        "motionlab_transfer_verified": False,
        "clinical_use_allowed": False,
        "missing_or_failed_checks": missing,
    }
