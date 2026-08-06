"""Validation utilities for PRE-DAY41_01 task portfolio."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import json
import yaml
from jsonschema import Draft202012Validator


EXPECTED_BRANCHES = {"A1", "A2", "B1", "B2", "C1", "C2"}
PROHIBITED_STATUS = {"REGRESSION_ONLY", "ARCHIVED", "REPLACED", "DEPRECATED"}
UNSAFE_CLAIMS = {
    "DIAGNOSE_ACL_TEAR",
    "DIAGNOSE_GRAFT_FAILURE",
    "AUTOMATIC_RETURN_TO_SPORT_CLEARANCE",
    "AUTOMATIC_LOAD_PRESCRIPTION",
    "HARD_FATIGUE_DIAGNOSIS",
}


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    branch_ids: tuple[str, ...]


def load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}")
    return data


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected object in {path}")
    return data


def iter_branches(portfolio: dict[str, Any]) -> Iterable[dict[str, Any]]:
    for task in portfolio.get("tasks", {}).values():
        for branch in task.get("branches", []):
            yield branch


def validate_schema(portfolio: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema)
    return [
        f"{'/'.join(str(p) for p in error.path)}: {error.message}"
        for error in sorted(validator.iter_errors(portfolio), key=lambda e: list(e.path))
    ]


def validate_invariants(portfolio: dict[str, Any]) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    branches = list(iter_branches(portfolio))
    ids = {str(branch.get("branch_id")) for branch in branches}

    missing = EXPECTED_BRANCHES - ids
    extra = ids - EXPECTED_BRANCHES
    if missing:
        errors.append(f"Missing parallel branches: {sorted(missing)}")
    if extra:
        warnings.append(f"Unexpected branches present: {sorted(extra)}")

    for branch in branches:
        branch_id = str(branch.get("branch_id"))
        status = str(branch.get("status"))
        if status != "ACTIVE_PARALLEL":
            errors.append(f"{branch_id}: status must be ACTIVE_PARALLEL, got {status}")
        if status in PROHIBITED_STATUS:
            errors.append(f"{branch_id}: prohibited demotion status {status}")
        if not branch.get("dataset_roles"):
            errors.append(f"{branch_id}: dataset_roles is empty")
        if not branch.get("site_data_required_for"):
            errors.append(f"{branch_id}: site_data_required_for is empty")
        if not branch.get("prohibited_claims"):
            errors.append(f"{branch_id}: prohibited_claims is empty")

    a1 = next((b for b in branches if b.get("branch_id") == "A1"), None)
    if a1 is None:
        errors.append("A1 hand-gesture branch missing")
    elif a1.get("clinical_priority") != "ACTIVE_PROGRAM":
        errors.append("A1 must remain ACTIVE_PROGRAM, not regression-only")

    governance = portfolio.get("governance", {})
    false_flags = [
        "training_allowed",
        "model_fitting_allowed",
        "scaler_fitting_allowed",
        "sealed_test_opened",
        "real_patient_data_allowed",
        "automated_clinical_recommendation_allowed",
    ]
    for flag in false_flags:
        if governance.get(flag) is not False:
            errors.append(f"governance.{flag} must be false")
    if governance.get("human_review_required") is not True:
        errors.append("human_review_required must be true")
    if governance.get("mfcv_site_eligibility") != "NOT_VERIFIED":
        errors.append("MFCV site eligibility must remain NOT_VERIFIED")
    if governance.get("clinical_threshold_status") != "PROVISIONAL_RESEARCH_ONLY":
        errors.append("Clinical thresholds must remain PROVISIONAL_RESEARCH_ONLY")

    # Unsafe claims must appear only as prohibited claims, never as supported outputs.
    for branch in branches:
        outputs = set(branch.get("output_families", []))
        overlap = outputs & UNSAFE_CLAIMS
        if overlap:
            errors.append(
                f"{branch.get('branch_id')}: unsafe claims in output_families: {sorted(overlap)}"
            )

    return ValidationResult(
        ok=not errors,
        errors=tuple(errors),
        warnings=tuple(warnings),
        branch_ids=tuple(sorted(ids)),
    )


def validate_portfolio(
    portfolio_path: str | Path,
    schema_path: str | Path,
) -> ValidationResult:
    portfolio = load_yaml(portfolio_path)
    schema = load_json(schema_path)
    schema_errors = validate_schema(portfolio, schema)
    invariant_result = validate_invariants(portfolio)
    errors = tuple(schema_errors) + invariant_result.errors
    return ValidationResult(
        ok=not errors,
        errors=errors,
        warnings=invariant_result.warnings,
        branch_ids=invariant_result.branch_ids,
    )
