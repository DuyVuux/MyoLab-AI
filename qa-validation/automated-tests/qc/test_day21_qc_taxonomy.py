from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import jsonschema
import pytest
import yaml


ROOT = Path(__file__).resolve().parents[3]


def load_yaml(rel: str):
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def load_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def load_module(rel: str, name: str):
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def taxonomy():
    return load_yaml("clinical/quality/qc-taxonomy.v0.2.yaml")


@pytest.fixture(scope="module")
def reasons():
    return load_yaml("services/quality-gate-service/configs/reason-codes.v0.1.yaml")


@pytest.fixture(scope="module")
def reasons_by_code(reasons):
    return {row["code"]: row for row in reasons["reason_codes"]}


@pytest.fixture(scope="module")
def qc_schema():
    return load_json("packages/common-schemas/json/qc-result.v0.2.schema.json")


@pytest.fixture(scope="module")
def lf_schema():
    return load_json("packages/common-schemas/json/labeling-function-output.schema.json")


def test_01_taxonomy_version(taxonomy):
    assert taxonomy["version"] == "0.2"


def test_02_taxonomy_supersedes_day04(taxonomy):
    assert taxonomy["supersedes"].endswith("qc-taxonomy.v0.1.yaml")


def test_03_three_scopes(taxonomy):
    assert taxonomy["scope_enum"] == ["SESSION", "CHANNEL", "WINDOW"]


def test_04_signal_quality_exact(taxonomy):
    assert taxonomy["signal_quality_enum"] == ["PASS", "WARNING", "FAIL"]


def test_05_no_threshold_freeze(taxonomy):
    assert taxonomy["threshold_policy"]["numeric_thresholds_frozen"] is False


def test_06_weak_supervision_contract_only(taxonomy):
    weak = taxonomy["weak_supervision_boundary"]
    assert weak["enabled_as_contract"] is True
    assert weak["label_model_trained"] is False


def test_07_active_learning_not_running_day21(taxonomy):
    assert taxonomy["weak_supervision_boundary"]["active_learning_selection_running"] is False


def test_08_required_principle_preserve_physiology(taxonomy):
    assert "physiological variation != acquisition artifact" in taxonomy["principles"]


def test_09_reason_codes_unique(reasons):
    codes = [row["code"] for row in reasons["reason_codes"]]
    assert len(codes) == len(set(codes))


def test_10_reason_registry_no_numeric_threshold(reasons):
    for row in reasons["reason_codes"]:
        for key, value in row.items():
            if "threshold" in key.lower():
                assert not isinstance(value, (int, float))


def test_11_reason_registry_no_diagnosis_fields(reasons):
    forbidden = {"diagnosis", "disease", "pathology_code", "treatment"}
    for row in reasons["reason_codes"]:
        assert forbidden.isdisjoint(row)


def test_12_phys_variation_not_lf(reasons_by_code):
    assert (
        reasons_by_code["PHYSIOLOGICAL_VARIATION_POSSIBLE"][
            "labeling_function_candidate"
        ]
        is False
    )


def test_13_quality_blocked_not_lf(reasons_by_code):
    assert reasons_by_code["QUALITY_BLOCKED"]["labeling_function_candidate"] is False


def test_14_missing_dropout_is_lf_candidate(reasons_by_code):
    assert reasons_by_code["MISSING_DROPOUT"]["labeling_function_candidate"] is True


def test_15_clipping_is_lf_candidate(reasons_by_code):
    assert reasons_by_code["CLIPPING_SATURATION_SUSPECTED"]["labeling_function_candidate"] is True


def test_16_powerline_is_lf_candidate(reasons_by_code):
    assert (
        reasons_by_code["POWERLINE_INTERFERENCE_SUSPECTED"][
            "labeling_function_candidate"
        ]
        is True
    )


def test_17_poor_contact_forbidden_inference(reasons_by_code):
    text = reasons_by_code["POOR_CONTACT_SUSPECTED"]["forbidden_inference"].lower()
    assert "diagnosis" in text or "pathology" in text


def test_18_qc_not_evaluated_exists(reasons_by_code):
    assert "QC_NOT_EVALUATED" in reasons_by_code


def test_19_insufficient_evidence_exists(reasons_by_code):
    assert "INSUFFICIENT_QC_EVIDENCE" in reasons_by_code


def test_20_qc_schema_valid(qc_schema):
    jsonschema.Draft202012Validator.check_schema(qc_schema)


def test_21_lf_schema_valid(lf_schema):
    jsonschema.Draft202012Validator.check_schema(lf_schema)


@pytest.mark.parametrize(
    "name",
    [
        "qc-result-pass.json",
        "qc-result-warning.json",
        "qc-result-fail.json",
        "qc-result-not-evaluated.json",
    ],
)
def test_22_25_positive_qc_fixtures(name, qc_schema):
    obj = load_json("qa-validation/test-data/day21/" + name)
    jsonschema.Draft202012Validator(qc_schema).validate(obj)


def test_26_invalid_not_evaluated_pass_rejected(qc_schema):
    obj = load_json("qa-validation/test-data/day21/qc-result-invalid-not-evaluated-pass.json")
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(qc_schema).validate(obj)


def test_27_invalid_diagnosis_field_rejected(qc_schema):
    obj = load_json("qa-validation/test-data/day21/qc-result-invalid-diagnosis-field.json")
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(qc_schema).validate(obj)


def test_28_lf_positive_valid(lf_schema):
    obj = load_json("qa-validation/test-data/day21/labeling-function-output-positive.json")
    jsonschema.Draft202012Validator(lf_schema).validate(obj)


def test_29_lf_ground_truth_claim_rejected(lf_schema):
    obj = load_json(
        "qa-validation/test-data/day21/"
        "labeling-function-output-invalid-ground-truth.json"
    )
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(lf_schema).validate(obj)


def test_30_lf_registry_no_label_model():
    reg = load_yaml("clinical/labels/qc-labeling-function-registry.v0.1.yaml")
    assert reg["ground_truth_policy"]["label_model_training_authorized"] is False


def test_31_lf_registry_future_days_only():
    reg = load_yaml("clinical/labels/qc-labeling-function-registry.v0.1.yaml")
    days = {row["implementation_status"] for row in reg["labeling_functions"]}
    assert days == {
        "PLANNED_DAY23",
        "PLANNED_DAY24",
        "PLANNED_DAY25",
        "PLANNED_DAY26",
        "PLANNED_DAY27",
        "PLANNED_DAY28",
    }


def test_32_lf_registry_reason_candidates_consistent(reasons_by_code):
    reg = load_yaml("clinical/labels/qc-labeling-function-registry.v0.1.yaml")
    for row in reg["labeling_functions"]:
        assert reasons_by_code[row["reason_code"]]["labeling_function_candidate"] is True


def test_33_non_candidates_consistent(reasons_by_code):
    reg = load_yaml("clinical/labels/qc-labeling-function-registry.v0.1.yaml")
    for code in reg["non_candidates"]:
        assert reasons_by_code[code]["labeling_function_candidate"] is False


def test_34_semantic_pass_fixture(reasons_by_code):
    mod = load_module("scripts/dev/day21_qc_semantics.py", "day21_qc_semantics")
    obj = load_json("qa-validation/test-data/day21/qc-result-pass.json")
    assert mod.validate_qc_result_semantics(obj, reasons_by_code) == []


def test_35_semantic_warning_fixture(reasons_by_code):
    mod = load_module("scripts/dev/day21_qc_semantics.py", "day21_qc_semantics_b")
    obj = load_json("qa-validation/test-data/day21/qc-result-warning.json")
    assert mod.validate_qc_result_semantics(obj, reasons_by_code) == []


def test_36_semantic_fail_fixture(reasons_by_code):
    mod = load_module("scripts/dev/day21_qc_semantics.py", "day21_qc_semantics_c")
    obj = load_json("qa-validation/test-data/day21/qc-result-fail.json")
    assert mod.validate_qc_result_semantics(obj, reasons_by_code) == []


def test_37_pass_with_review_reason_detected(reasons_by_code):
    mod = load_module("scripts/dev/day21_qc_semantics.py", "day21_qc_semantics_d")
    obj = load_json("qa-validation/test-data/day21/qc-result-warning.json")
    obj["signal_quality"] = "PASS"
    errors = mod.validate_qc_result_semantics(obj, reasons_by_code)
    assert "pass_cannot_contain_review_required_reason" in errors


def test_38_fail_without_block_detected(reasons_by_code):
    mod = load_module("scripts/dev/day21_qc_semantics.py", "day21_qc_semantics_e")
    obj = load_json("qa-validation/test-data/day21/qc-result-warning.json")
    obj["signal_quality"] = "FAIL"
    errors = mod.validate_qc_result_semantics(obj, reasons_by_code)
    assert "fail_requires_blocking_reason" in errors


def test_39_unknown_reason_detected(reasons_by_code):
    mod = load_module("scripts/dev/day21_qc_semantics.py", "day21_qc_semantics_f")
    obj = load_json("qa-validation/test-data/day21/qc-result-warning.json")
    obj["reasons"][0]["code"] = "NOT_REGISTERED"
    errors = mod.validate_qc_result_semantics(obj, reasons_by_code)
    assert "unknown_reason_code:NOT_REGISTERED" in errors


def test_40_requirement_impact_configuration_driven():
    impact = load_yaml("qa-validation/traceability/day21-requirement-impact.yaml")
    assert impact["python_hardcoded_requirement_count"] is False
    assert impact["source_of_truth"].endswith("requirements-manifest.yaml")


def test_41_requirement_impact_exact_roadmap_ids():
    impact = load_yaml("qa-validation/traceability/day21-requirement-impact.yaml")
    ids = {row["requirement_id"] for row in impact["requirements"]}
    assert ids == {
        "FR-030",
        "FR-037",
        "FR-038",
        "FR-039",
        "FR-040",
        "FR-041",
        "NFR-009",
        "NFR-011",
    }


def test_42_phase_entry_report_does_not_fake_gate():
    entry = load_yaml("qa-validation/evidence/day21-phase-entry-evidence.yaml")
    assert entry["user_reported_state"]["reported_gate_b_decision"] == "NOT_STATED_IN_REPORT"
    assert entry["phase_entry_interpretation"]["site_real_data_qc_claim_allowed"] is False


def test_43_day22_window_implementation():
    assert (ROOT / "packages/common-schemas/json/qc-window-identity.schema.json").exists()


def test_44_no_detector_implementation_day23_28():
    forbidden = [
        "dropout_detector.py",
        "clipping_detector.py",
        "powerline_detector.py",
        "motion_artifact_detector.py",
    ]
    for name in forbidden:
        assert not any(ROOT.rglob(name))


def test_45_no_model_artifacts():
    forbidden_ext = {".pt", ".pth", ".onnx", ".joblib", ".pkl"}
    day21_paths = [
        ROOT / "clinical/quality",
        ROOT / "clinical/labels",
        ROOT / "services/quality-gate-service",
        ROOT / "packages/common-schemas",
        ROOT / "qa-validation/automated-tests/qc",
    ]
    for p in day21_paths:
        if p.exists():
            assert not any(path.suffix.lower() in forbidden_ext for path in p.rglob("*"))


def test_46_config_validator_passes():
    mod = load_module("scripts/dev/day21_qc_contract_validator.py", "day21_qc_contract_validator")
    report = mod.validate(ROOT)
    assert report["status"] == "PASS", report


def test_47_validator_maturity_is_contract_only():
    mod = load_module(
        "scripts/dev/day21_qc_contract_validator.py",
        "day21_qc_contract_validator_b",
    )
    report = mod.validate(ROOT)
    assert report["weak_supervision_maturity"] == "CONTRACT_AND_REGISTRY_ONLY"
    assert report["label_model_trained"] is False


def test_48_no_site_thresholds_frozen():
    mod = load_module(
        "scripts/dev/day21_qc_contract_validator.py",
        "day21_qc_contract_validator_c",
    )
    assert mod.validate(ROOT)["site_thresholds_frozen"] is False
