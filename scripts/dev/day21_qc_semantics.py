from __future__ import annotations

from typing import Any


def validate_qc_result_semantics(
    result: dict[str, Any],
    reasons_by_code: dict[str, dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    evaluation_status = result["evaluation_status"]
    quality = result["signal_quality"]
    reasons = result["reasons"]

    if evaluation_status == "EVALUATED" and quality is None:
        errors.append("evaluated_requires_signal_quality")
    if evaluation_status != "EVALUATED" and quality is not None:
        errors.append("not_evaluated_must_not_look_pass_warning_fail")

    blocking = False
    warning = False
    for reason in reasons:
        code = reason["code"]
        registry = reasons_by_code.get(code)
        if registry is None:
            errors.append(f"unknown_reason_code:{code}")
            continue
        if reason["semantic_class"] != registry["semantic_class"]:
            errors.append(f"semantic_class_mismatch:{code}")
        if reason["technical_action"] == "BLOCK_UNSUPPORTED_DOWNSTREAM":
            blocking = True
        if reason["qc_supportability"] == "BLOCKED":
            blocking = True
        if reason["qc_supportability"] == "REVIEW_REQUIRED":
            warning = True

    if quality == "PASS" and blocking:
        errors.append("pass_cannot_contain_blocking_reason")
    if quality == "PASS" and warning:
        errors.append("pass_cannot_contain_review_required_reason")
    if quality == "FAIL" and not blocking:
        errors.append("fail_requires_blocking_reason")
    if quality == "WARNING" and not warning:
        errors.append("warning_requires_review_reason")
    return errors
