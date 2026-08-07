from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = ROOT / "scripts/dev"
sys.path.insert(0, str(SCRIPT_DIR))

from day03_time_motion_utils import (  # noqa: E402
    BASELINE_COLUMNS,
    baseline_eligible_rows,
    calculate_observation_summary,
    determine_gate_status,
    load_yaml,
    read_baseline_rows,
)


BASELINE = ROOT / "clinical/studies/time-motion-baseline-round1.csv"
EVIDENCE_LOG = ROOT / "clinical/workflows/current-workflow-evidence-log.md"
BURNDOWN = ROOT / "docs/02-clinical/discovery/open-questions-burndown.md"
TRACE = ROOT / "docs/03-architecture/traceability/day03-workflow-observation-traceability.v0.1.csv"
SCHEMA = ROOT / "packages/common-schemas/json/day03-time-motion-baseline-row.schema.json"
SYNTHETIC = ROOT / "qa-validation/test-data/day03/synthetic-time-motion-observation.v0.1.yaml"
MANIFEST = ROOT / "qa-validation/evidence/day03-artifact-manifest.json"


def test_01_mandatory_roadmap_outputs_exist() -> None:
    assert BASELINE.is_file()
    assert EVIDENCE_LOG.is_file()
    assert BURNDOWN.is_file()


def test_02_baseline_header_matches_frozen_contract() -> None:
    with BASELINE.open("r", encoding="utf-8", newline="") as file_obj:
        reader = csv.reader(file_obj)
        header = next(reader)
    assert header == BASELINE_COLUMNS


def test_03_no_direct_phi_columns_in_baseline_contract() -> None:
    forbidden = {
        "patient_name",
        "mrn",
        "date_of_birth",
        "email",
        "phone",
        "address",
    }
    assert forbidden.isdisjoint(BASELINE_COLUMNS)


def test_04_schema_is_draft_2020_12() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert schema["$schema"].endswith("2020-12/schema")


def test_05_empty_round1_dataset_is_safely_blocked() -> None:
    rows = read_baseline_rows(BASELINE)
    assert determine_gate_status(rows) == "BLOCKED_WITH_EVIDENCE"


def test_06_synthetic_fixture_is_not_baseline_evidence() -> None:
    fixture = load_yaml(SYNTHETIC)
    assert fixture["observation"]["observation_mode"] == "SYNTHETIC_QA"
    assert fixture["baseline_eligible"] is False


def test_07_interval_union_prevents_naive_overlap_counting() -> None:
    fixture = load_yaml(SYNTHETIC)
    summary = calculate_observation_summary(fixture)
    assert summary["elapsed_time_sec"] == pytest.approx(420.0)
    assert summary["parallel_time_union_sec"] > 0


def test_08_doctor_time_is_separate_from_interpretation() -> None:
    fixture = load_yaml(SYNTHETIC)
    summary = calculate_observation_summary(fixture)
    assert "doctor_data_hands_on_union_sec" in summary
    assert "clinical_interpretation_union_sec" in summary


def test_09_remeasurement_episode_is_detected() -> None:
    fixture = load_yaml(SYNTHETIC)
    summary = calculate_observation_summary(fixture)
    assert summary["remeasurement_occurred"] is True
    assert summary["remeasurement_episode_count"] == 1


def test_10_evidence_log_keeps_measurement_and_inference_separate() -> None:
    text = EVIDENCE_LOG.read_text(encoding="utf-8").lower()
    assert "measurement fact" in text
    assert "operator-reported" in text
    assert "observer inference" in text
    assert "clinical interpretation" in text


def test_11_no_site_workflow_node_is_silently_verified() -> None:
    text = EVIDENCE_LOG.read_text(encoding="utf-8")
    assert "SITE_VERIFIED" not in "\n".join(
        line
        for line in text.splitlines()
        if line.startswith("| CW-")
    )


def test_12_burndown_does_not_silently_close_key_questions() -> None:
    text = BURNDOWN.read_text(encoding="utf-8")
    for question_id in ["OQ-001", "OQ-002", "OQ-003", "OQ-005"]:
        assert question_id in text
    assert "0` questions are closed" in text


def test_13_sixty_minute_estimate_is_not_baseline() -> None:
    combined = (
        EVIDENCE_LOG.read_text(encoding="utf-8")
        + BURNDOWN.read_text(encoding="utf-8")
    ).lower()
    assert "no manual-processing baseline is claimed" in combined


def test_14_fifty_percent_is_not_a_commitment() -> None:
    acceptance = (
        ROOT / "qa-validation/requirements/day03-acceptance-criteria.md"
    ).read_text(encoding="utf-8")
    assert "research target, not commitment" in acceptance


def test_15_traceability_includes_prd_10_prd_14_and_ac10() -> None:
    text = TRACE.read_text(encoding="utf-8")
    assert "PRD §10" in text
    assert "PRD §14" in text
    assert "SRS AC-10" in text


def test_16_baseline_eligible_helper_rejects_interview_rows() -> None:
    row = {column: "x" for column in BASELINE_COLUMNS}
    row["baseline_eligible"] = "true"
    row["observation_mode"] = "INTERVIEW_ONLY"
    row["reviewer_status"] = "ACCEPTED_FOR_ROUND1_BASELINE"
    assert baseline_eligible_rows([row]) == []


def test_17_baseline_eligible_helper_requires_review() -> None:
    row = {column: "x" for column in BASELINE_COLUMNS}
    row["baseline_eligible"] = "true"
    row["observation_mode"] = "DIRECT_OBSERVATION"
    row["reviewer_status"] = "PENDING_REVIEW"
    assert baseline_eligible_rows([row]) == []


def test_18_managed_manifest_is_day03_scoped() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["scope"] == "DAY03_MANAGED_ARTIFACTS_ONLY"
    assert all(item["path"] for item in manifest["files"])


def test_19_no_binary_or_model_suffix_is_introduced_by_day03() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    forbidden = {
        ".npz",
        ".npy",
        ".mat",
        ".c3d",
        ".joblib",
        ".pkl",
        ".pickle",
        ".pt",
        ".pth",
        ".onnx",
    }
    introduced = [
        item["path"]
        for item in manifest["files"]
        if Path(item["path"]).suffix.lower() in forbidden
    ]
    assert introduced == []


def test_20_no_real_patient_or_training_claim_in_packaged_gate() -> None:
    snapshot = json.loads(
        (ROOT / "qa-validation/evidence/day03-day02-handoff-snapshot.json").read_text(
            encoding="utf-8"
        )
    )
    assert snapshot["training_executed"] is False
    assert snapshot["raw_patient_data_read"] is False


def test_21_no_unauthorized_binary_data_in_repo() -> None:
    import os
    skip_dirs = {"__pycache__", ".pytest_cache", ".venv", "env", ".git", "node_modules", "raw", "datasets", "experiments", "fixtures"}
    legacy_whitelist = {"day5-preprocess-golden.npz"}
    
    forbidden_suffixes = {
        ".npz",
        ".npy",
        ".mat",
        ".c3d",
        ".joblib",
        ".pkl",
        ".pickle",
        ".pt",
        ".pth",
        ".onnx",
    }
    
    unauthorized_files = []
    
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # Prune skipped directories so os.walk doesn't traverse them
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        
        for filename in filenames:
            if filename in legacy_whitelist:
                continue
            
            path = Path(dirpath) / filename
            if path.suffix.lower() in forbidden_suffixes:
                unauthorized_files.append(str(path.relative_to(ROOT)))
                
    assert not unauthorized_files, f"Found unauthorized binary/model data in repo outside allowed directories: {unauthorized_files}"
