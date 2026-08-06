from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "clinical-governance"))

from pre_day41_01.portfolio import (  # noqa: E402
    UNSAFE_CLAIMS,
    iter_branches,
    load_json,
    load_yaml,
    validate_portfolio,
)


PORTFOLIO_PATH = ROOT / "clinical/governance/task-portfolio.v0.1.yaml"
SCHEMA_PATH = ROOT / "packages/common-schemas/json/pre-day41-task-portfolio.schema.json"
KEYWORDS_PATH = ROOT / "clinical/learning/lower-limb-acl/pre-day41-01-medical-keywords.v0.1.yaml"


def portfolio():
    return load_yaml(PORTFOLIO_PATH)


def branches():
    return {b["branch_id"]: b for b in iter_branches(portfolio())}


def test_schema_and_invariants_pass():
    result = validate_portfolio(PORTFOLIO_PATH, SCHEMA_PATH)
    assert result.ok, result.errors


def test_all_parallel_branches_present():
    assert set(branches()) == {"A1", "A2", "B1", "B2", "C1", "C2"}
    assert all(b["status"] == "ACTIVE_PARALLEL" for b in branches().values())


def test_hand_track_is_not_demoted():
    a1 = branches()["A1"]
    assert a1["clinical_priority"] == "ACTIVE_PROGRAM"
    assert a1["status"] == "ACTIVE_PARALLEL"


def test_lower_limb_track_is_parallel_not_replacement():
    a2 = branches()["A2"]
    assert a2["status"] == "ACTIVE_PARALLEL"
    assert "A1" in branches()


def test_governance_flags():
    g = portfolio()["governance"]
    for key in (
        "training_allowed",
        "model_fitting_allowed",
        "scaler_fitting_allowed",
        "sealed_test_opened",
        "real_patient_data_allowed",
        "automated_clinical_recommendation_allowed",
    ):
        assert g[key] is False
    assert g["human_review_required"] is True


def test_mfcv_site_not_verified():
    assert portfolio()["governance"]["mfcv_site_eligibility"] == "NOT_VERIFIED"


def test_medical_keyword_domains():
    data = load_yaml(KEYWORDS_PATH)
    assert set(data["domains"]) == {
        "anatomy_and_joint",
        "muscles",
        "protocol_and_contraction",
        "rehabilitation_and_outcomes",
    }
    total = sum(len(items) for items in data["domains"].values())
    assert total >= 30
    for items in data["domains"].values():
        for item in items:
            assert item["term"]
            assert item["vi"]
            assert item["relevance"]
            assert item["boundary"]


def test_no_unsafe_output_claims():
    for branch in branches().values():
        assert not (set(branch["output_families"]) & UNSAFE_CLAIMS)


def test_task_b_confidence_is_not_increased():
    for branch_id in ("B1", "B2"):
        outputs = set(branches()[branch_id]["output_families"])
        assert "CONFIDENCE_SAME_OR_LOWER" in outputs
        assert "CONFIDENCE_INCREASE" not in outputs


def test_c2_blocks_rts_and_diagnosis():
    claims = set(branches()["C2"]["prohibited_claims"])
    assert "AUTOMATIC_RETURN_TO_SPORT_CLEARANCE" in claims
    assert "DIAGNOSE_ACL_TEAR" in claims
    assert "AUTOMATIC_LOAD_PRESCRIPTION" in claims


def test_handoff_gate():
    h = portfolio()["handoff"]
    assert h["required_gate"] == "PORTFOLIO_GATE_PASS"
    assert h["target_status"] == "GO_FOR_PRE_DAY41_02_FUNCTIONAL_ANATOMY"


def test_no_raw_data_extensions():
    prohibited = {".edf", ".c3d", ".mat", ".dat", ".parquet", ".h5", ".hdf5"}
    excluded_dirs = {".venv", "node_modules", "ai-core", ".git"}
    hits = [
        p for p in ROOT.rglob("*") 
        if p.is_file() and p.suffix.lower() in prohibited
        and not any(part in excluded_dirs for part in p.parts)
    ]
    assert not hits
