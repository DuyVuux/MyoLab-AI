"""Fail-closed Day 30 to Day 31 authorization boundary."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

_SAFETY_FLAGS = (
    "training_allowed",
    "model_fitting_allowed",
    "scaler_fitting_allowed",
    "pooled_training_allowed",
    "test_signal_access_allowed",
    "test_set_opened",
    "fatigue_inference_allowed",
    "clinical_use_allowed",
)
_UPSTREAM_FALSE_FLAGS = (
    "training_allowed",
    "pooled_training_allowed",
    "test_set_opened",
    "fatigue_inference_allowed",
    "clinical_use_allowed",
)


def validate_preflight(
    config: Mapping[str, Any],
    day30_readiness: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate that feature engineering is authorized but training is not."""

    errors: list[str] = []
    input_day30 = config.get("input_day30")
    accepted_statuses = (
        input_day30.get("accepted_statuses")
        if isinstance(input_day30, Mapping)
        else None
    )
    if (
        not isinstance(accepted_statuses, list)
        or day30_readiness.get("status") not in accepted_statuses
    ):
        errors.append("day30_status_not_accepted")

    for flag in _SAFETY_FLAGS:
        if config.get(flag) is not False:
            errors.append(f"{flag}_must_be_false")
    for flag in _UPSTREAM_FALSE_FLAGS:
        if day30_readiness.get(flag) is not False:
            errors.append(f"day30_{flag}_must_be_false")

    visible = config.get("visible_partitions")
    forbidden = config.get("forbidden_partitions")
    if visible != ["train", "validation"]:
        errors.append("visible_partitions_must_be_train_validation")
    if not isinstance(forbidden, list) or not {
        "test",
        "sealed_test",
        "outer_test",
    }.issubset(forbidden):
        errors.append("forbidden_partitions_incomplete")
    unique_errors = sorted(set(errors))
    return {
        "schema_version": "day31-preflight.v1",
        "pass": not unique_errors,
        "errors": unique_errors,
        "day30_status": day30_readiness.get("status"),
        "feature_engineering_allowed": not unique_errors,
        "training_allowed": False,
        "model_fitting_allowed": False,
        "scaler_fitting_allowed": False,
        "pooled_training_allowed": False,
        "test_signal_access_allowed": False,
        "test_set_opened": False,
    }
