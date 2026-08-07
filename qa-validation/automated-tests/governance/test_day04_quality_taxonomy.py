from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema
import pytest
import yaml


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = ROOT / "scripts/dev"
sys.path.insert(0, str(SCRIPT_DIR))

from day04_quality_taxonomy_utils import (  # noqa: E402
    aggregate_signal_quality,
    load_json,
    load_yaml,
    taxonomy_by_code,
    validate_reason_record,
)


TAXONOMY_PATH = ROOT / "clinical/quality/qc-taxonomy.v0.1.yaml"
GUIDANCE_PATH = ROOT / "clinical/quality/artifact-vs-physiology-guidance.v0.1.md"
REASON_SCHEMA_PATH = ROOT / "packages/common-schemas/json/quality-reason-codes.schema.json"
TAXONOMY_SCHEMA_PATH = ROOT / "packages/common-schemas/json/qc-taxonomy.schema.json"
FIXTURE_PATH = ROOT / "qa-validation/test-data/day04/synthetic-quality-reason-cases.v0.1.yaml"
TRACE_PATH = ROOT / "docs/03-architecture/traceability/day04-quality-taxonomy-traceability.v0.1.csv"
MANIFEST_PATH = ROOT / "qa-validation/evidence/day04-artifact-manifest.json"
UPSTREAM_PATH = ROOT / "qa-validation/evidence/day04-day03-handoff-snapshot.json"
OPENQ_PATH = ROOT / "docs/02-clinical/discovery/day04-open-question-impact.v0.1.md"


def test_01_mandatory_roadmap_outputs_exist() -> None:
    assert TAXONOMY_PATH.is_file()
    assert GUIDANCE_PATH.is_file()
    assert REASON_SCHEMA_PATH.is_file()


def test_02_taxonomy_yaml_and_schema_validate() -> None:
    taxonomy = load_yaml(TAXONOMY_PATH)
    schema = load_json(TAXONOMY_SCHEMA_PATH)
    jsonschema.Draft202012Validator(schema).validate(taxonomy)


def test_03_reason_schema_is_draft_2020_12() -> None:
    schema = load_json(REASON_SCHEMA_PATH)
    assert schema["$schema"].endswith("2020-12/schema")


def test_04_reason_codes_are_unique() -> None:
    taxonomy = load_yaml(TAXONOMY_PATH)
    by_code = taxonomy_by_code(taxonomy)
    assert len(by_code) == len(taxonomy["reason_codes"])


def test_05_required_fr030_040_codes_are_represented() -> None:
    taxonomy = load_yaml(TAXONOMY_PATH)
    requirements = " ".join(item["requirement"] for item in taxonomy["reason_codes"])
    for requirement in [
        "FR-031", "FR-032", "FR-033", "FR-034", "FR-035", "FR-036",
        "FR-037", "FR-038", "FR-039",
    ]:
        assert requirement in requirements


def test_06_three_qc_scopes_are_defined() -> None:
    taxonomy = load_yaml(TAXONOMY_PATH)
    assert set(taxonomy["scope_enum"]) == {"SESSION", "CHANNEL", "WINDOW"}


def test_07_quality_states_are_exactly_pass_warning_fail() -> None:
    taxonomy = load_yaml(TAXONOMY_PATH)
    assert taxonomy["signal_quality_enum"] == ["PASS", "WARNING", "FAIL"]


def test_08_no_numeric_threshold_is_frozen() -> None:
    taxonomy = load_yaml(TAXONOMY_PATH)
    assert taxonomy["threshold_policy"]["numeric_thresholds_frozen"] is False
    assert taxonomy["threshold_policy"]["status"] == "TBD_SITE_VALIDATION_REQUIRED"


def test_09_context_tags_cannot_be_qc_failure_reasons() -> None:
    taxonomy = load_yaml(TAXONOMY_PATH)
    tags = {item["tag"] for item in taxonomy["context_tags_never_sufficient_for_qc_failure"]}
    assert "STROKE_CONTEXT" in tags
    assert "MUSCLE_ATROPHY_CONTEXT" in tags
    assert "BODY_HABITUS_HIGH_ADIPOSITY_CONTEXT" in tags
    reason_codes = {item["code"] for item in taxonomy["reason_codes"]}
    assert tags.isdisjoint(reason_codes)


def test_10_physiology_possible_does_not_downgrade_quality() -> None:
    taxonomy = load_yaml(TAXONOMY_PATH)
    fixture = load_yaml(FIXTURE_PATH)
    case = next(item for item in fixture["cases"] if item["case_id"] == "D04-QA-002")
    assert aggregate_signal_quality(case["reasons"], taxonomy) == "PASS"


def test_11_ambiguity_routes_to_warning() -> None:
    taxonomy = load_yaml(TAXONOMY_PATH)
    fixture = load_yaml(FIXTURE_PATH)
    case = next(item for item in fixture["cases"] if item["case_id"] == "D04-QA-003")
    assert aggregate_signal_quality(case["reasons"], taxonomy) == "WARNING"


def test_12_quality_blocked_routes_to_fail() -> None:
    taxonomy = load_yaml(TAXONOMY_PATH)
    fixture = load_yaml(FIXTURE_PATH)
    case = next(item for item in fixture["cases"] if item["case_id"] == "D04-QA-004")
    assert aggregate_signal_quality(case["reasons"], taxonomy) == "FAIL"


def test_13_all_synthetic_reason_records_validate() -> None:
    schema = load_json(REASON_SCHEMA_PATH)
    fixture = load_yaml(FIXTURE_PATH)
    for case in fixture["cases"]:
        for reason in case["reasons"]:
            validate_reason_record(reason, schema)


def test_14_guidance_explicitly_separates_artifact_and_pathology() -> None:
    text = GUIDANCE_PATH.read_text(encoding="utf-8").lower()
    assert "not automatically an acquisition artifact" in text
    assert "not a diagnosis" in text
    assert "stroke" in text
    assert "atrophy" in text


def test_15_guidance_preserves_raw_and_uses_review_for_ambiguity() -> None:
    text = GUIDANCE_PATH.read_text(encoding="utf-8").lower()
    assert "preserve raw" in text
    assert "review/abstain" in text


def test_16_traceability_covers_all_day04_requirements() -> None:
    text = TRACE_PATH.read_text(encoding="utf-8")
    for requirement in [
        "FR-030", "FR-031", "FR-032", "FR-033", "FR-034", "FR-035",
        "FR-036", "FR-037", "FR-038", "FR-039", "FR-040", "NFR-009",
        "PRD-JTBD-03",
    ]:
        assert requirement in text


def test_17_open_questions_remain_explicit() -> None:
    text = OPENQ_PATH.read_text(encoding="utf-8")
    assert "OQ-004" in text
    assert "TBD" in text
    assert "No clinical/site QC threshold is closed in DAY04" in text


def test_18_upstream_day03_status_is_not_silently_upgraded() -> None:
    snapshot = load_json(UPSTREAM_PATH)
    assert snapshot["day03_status"] == "BLOCKED_WITH_EVIDENCE"
    assert snapshot["day04_can_claim_upstream_acceptance"] is False


def test_19_manifest_is_day04_scoped_and_introduces_no_binary_model_data() -> None:
    manifest = load_json(MANIFEST_PATH)
    assert manifest["scope"] == "DAY04_MANAGED_ARTIFACTS_ONLY"
    forbidden = {
        ".npz", ".npy", ".mat", ".c3d", ".joblib", ".pkl", ".pickle",
        ".pt", ".pth", ".onnx",
    }
    introduced = [
        item["path"]
        for item in manifest["files"]
        if Path(item["path"]).suffix.lower() in forbidden
    ]
    assert introduced == []


def test_20_no_training_patient_data_or_clinical_threshold_claim() -> None:
    snapshot = load_json(UPSTREAM_PATH)
    taxonomy = load_yaml(TAXONOMY_PATH)
    fixture = load_yaml(FIXTURE_PATH)
    assert snapshot["training_executed"] is False
    assert snapshot["raw_patient_data_read"] is False
    assert fixture["clinical_evidence"] is False
    assert taxonomy["threshold_policy"]["numeric_thresholds_frozen"] is False


def test_21_global_no_rogue_binary_data() -> None:
    skip_dirs = {
        "__pycache__", ".pytest_cache", ".venv", "env", ".git", 
        "node_modules", "raw", "datasets", "experiments", "fixtures"
    }
    forbidden_exts = {".npz", ".npy", ".mat", ".c3d", ".joblib", ".pkl", ".pickle", ".pt", ".pth", ".onnx"}
    legacy_whitelist = {"day5-preprocess-golden.npz"}

    for path in ROOT.rglob("*"):
        if path.is_file():
            if any(part in skip_dirs for part in path.parts):
                continue
            if path.suffix.lower() in forbidden_exts:
                if path.name not in legacy_whitelist:
                    pytest.fail(f"Unauthorized binary file found outside skip_dirs: {path}")
