from __future__ import annotations
import json
import sys
from pathlib import Path
import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/dev"))
from day05_privacy_utils import classify_structured_fields, load_json, load_yaml  # noqa: E402

CLASS = ROOT / "security-compliance/privacy/motionlab-data-classification.v0.1.md"
SOP = ROOT / "security-compliance/privacy/deidentification-sop.v0.1.md"
MATRIX = ROOT / "security-compliance/privacy/patient-data-access-matrix.v0.1.yaml"
SCHEMA = ROOT / "packages/common-schemas/json/patient-data-access-matrix.schema.json"
FIX = ROOT / "qa-validation/test-data/day05/synthetic-privacy-boundary-cases.v0.1.yaml"
TRACE = ROOT / "docs/03-architecture/traceability/day05-privacy-traceability.v0.1.csv"
UP = ROOT / "qa-validation/evidence/day05-day04-handoff-snapshot.json"
MAN = ROOT / "qa-validation/evidence/day05-artifact-manifest.json"
OQ = ROOT / "docs/02-clinical/discovery/day05-open-question-impact.v0.1.md"

def test_01_outputs_exist():
    assert CLASS.is_file() and SOP.is_file() and MATRIX.is_file()
def test_02_access_matrix_schema_validates():
    jsonschema.Draft202012Validator(load_json(SCHEMA)).validate(load_yaml(MATRIX))
def test_03_required_roles_present():
    roles = {r["role"] for r in load_yaml(MATRIX)["roles"]}
    assert {"operator", "doctor", "admin", "research", "technical_reviewer"} <= roles
def test_04_unknown_classification_fails_closed():
    assert load_yaml(MATRIX)["hard_rules"]["unknown_classification_access"] == "DENY"
def test_05_git_raw_patient_data_denied():
    assert load_yaml(MATRIX)["hard_rules"]["git_raw_patient_data"] == "DENY"
def test_06_analysis_id_direct_identifier_denied():
    assert load_yaml(MATRIX)["hard_rules"]["direct_identifier_in_analysis_id"] == "DENY"
def test_07_direct_identifier_fixture_detected():
    case = load_yaml(FIX)["cases"][0]
    assert classify_structured_fields(case["fields"]) == case["expected"]
def test_08_safe_analysis_id_fixture_passes():
    case = load_yaml(FIX)["cases"][1]
    assert classify_structured_fields(case["fields"]) == case["expected"]
def test_09_free_text_requires_review():
    case = load_yaml(FIX)["cases"][2]
    assert classify_structured_fields(case["fields"]) == case["expected"]
def test_10_unknown_governance_detected():
    case = load_yaml(FIX)["cases"][3]
    assert classify_structured_fields(case["fields"]) == case["expected"]
def test_11_raw_is_immutable_not_rewritten():
    text = SOP.read_text(encoding="utf-8").lower()
    assert "never overwrite raw" in text
def test_12_retention_is_not_invented():
    text = CLASS.read_text(encoding="utf-8")
    assert "TBD / GOVERNANCE_CONFIRMATION_REQUIRED" in text
def test_13_no_hipaa_compliance_claim():
    text = SOP.read_text(encoding="utf-8").lower()
    assert "does not certify hipaa compliance" in text
def test_14_traceability_complete():
    text = TRACE.read_text(encoding="utf-8")
    for req in ["FR-020", "FR-025", "NFR-004", "NFR-005", "NFR-006", "TBD-05"]:
        assert req in text
def test_15_tbd05_remains_open():
    assert "NEED_GOVERNANCE_CONFIRMATION" in OQ.read_text(encoding="utf-8")
def test_16_upstream_not_silently_upgraded():
    up = load_json(UP)
    assert up["day05_can_claim_upstream_acceptance"] is False
def test_17_site_privacy_not_falsely_confirmed():
    assert load_json(UP)["site_privacy_governance_confirmed"] is False
def test_18_fixture_not_clinical_evidence():
    f = load_yaml(FIX)
    assert f["clinical_evidence"] is False and f["data_class"] == "SYNTHETIC_QA_FIXTURE"
def test_19_no_unauthorized_binary_data_in_project():
    from qa_utils import scan_project_files
    files = scan_project_files(ROOT)
    forbidden_exts = {".npz", ".npy", ".mat", ".c3d", ".joblib", ".pkl", ".pickle", ".pt", ".pth", ".onnx"}
    whitelist_files = {"day5-preprocess-golden.npz"}
    
    violations = []
    for f in files:
        if f.suffix.lower() in forbidden_exts:
            if f.name not in whitelist_files:
                violations.append(str(f.relative_to(ROOT)))
                
    assert not violations, f"Found unauthorized binary files: {violations}"
def test_20_no_training_or_patient_data_used():
    up = load_json(UP)
    assert up["training_executed"] is False and up["raw_patient_data_read"] is False
