from __future__ import annotations

from typing import Any


REQUIRED_FINDINGS = frozenset(
    {
        "amplitude_scale_difference_about_40x",
        "sampling_rate_2048_vs_2000",
        "mendeley_dc_offset",
        "mendeley_ch4_low_amplitude_anomaly",
        "grabmyo_u1_u4_noise_floor",
        "channel_count_mismatch",
        "gesture_ontology_mismatch",
        "cross_day_vs_single_session",
    }
)
READY_INPUT_STATES = frozenset({"GO_FOR_DAY30_HARMONIZATION"})


def _validate_governance(report: dict[str, Any], errors: list[str]) -> None:
    governance = report.get("governance")
    if not isinstance(governance, dict):
        errors.append("missing_governance")
        return
    for field, error in (
        ("test_set_opened", "test_set_must_be_unopened"),
        ("training_allowed", "training_must_be_disabled"),
        ("fatigue_inference_allowed", "fatigue_inference_must_be_disabled"),
    ):
        if governance.get(field) is not False:
            errors.append(error)


def _validate_dataset_inputs(report: dict[str, Any], errors: list[str]) -> None:
    datasets = report.get("datasets")
    if not isinstance(datasets, dict):
        errors.extend(("missing_dataset:mendeley", "missing_dataset:grabmyo"))
        return
    for dataset_id in ("mendeley", "grabmyo"):
        dataset = datasets.get(dataset_id)
        if not isinstance(dataset, dict):
            errors.append(f"missing_dataset:{dataset_id}")
            continue
        if dataset.get("readiness_status") not in READY_INPUT_STATES:
            errors.append(f"{dataset_id}_readiness_not_go")
        if dataset.get("test_set_opened") is not False:
            errors.append(f"{dataset_id}_test_set_must_be_unopened")
        if dataset.get("test_signal_rows_read") != 0:
            errors.append(f"{dataset_id}_test_signal_rows_must_be_zero")


def validate_pre_day30_report(report: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(report, dict):
        raise TypeError("report must be a mapping")
    errors: list[str] = []
    if report.get("overall_status") not in READY_INPUT_STATES:
        errors.append("overall_status_not_go")
    _validate_governance(report, errors)
    _validate_dataset_inputs(report, errors)

    findings = report.get("key_findings")
    finding_set = set(findings) if isinstance(findings, list) else set()
    errors.extend(
        f"missing_finding:{item}" for item in sorted(REQUIRED_FINDINGS - finding_set)
    )
    return {
        "schema_version": "day30-preflight.v1",
        "pass": not errors,
        "errors": errors,
        "training_allowed": False,
        "pooled_training_allowed": False,
        "test_set_opened": False,
    }

