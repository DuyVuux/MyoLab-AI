from __future__ import annotations

import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/dev"))

from day06_evidence_utils import load_json, load_yaml, promotable_tier  # noqa: E402

INV = ROOT / "data-platform/catalog/motionlab-evidence-inventory.v0.1.yaml"
POLICY = ROOT / "data-platform/governance/evidence-tier-policy.v0.1.md"
REQ = ROOT / "clinical/discovery/vinmec-data-request-pack.v0.1.md"
SCHEMA = ROOT / "packages/common-schemas/json/motionlab-evidence-inventory.schema.json"
FIX = ROOT / "qa-validation/test-data/day06/synthetic-evidence-promotion-cases.v0.1.yaml"
TRACE = ROOT / "docs/03-architecture/traceability/day06-evidence-inventory-traceability.v0.1.csv"
UP = ROOT / "qa-validation/evidence/day06-day05-handoff-snapshot.json"
MAN = ROOT / "qa-validation/evidence/day06-artifact-manifest.json"
OQ = ROOT / "docs/02-clinical/discovery/day06-open-question-impact.v0.1.md"


def test_01_outputs_exist() -> None:
    assert INV.is_file()
    assert POLICY.is_file()
    assert REQ.is_file()


def test_02_inventory_schema_validates() -> None:
    validator = jsonschema.Draft202012Validator(load_json(SCHEMA))
    validator.validate(load_yaml(INV))


def test_03_source_classes_complete() -> None:
    assert set(load_yaml(INV)["source_classes"]) == {
        "SYNTHETIC",
        "VENDOR_SAMPLE",
        "DEIDENTIFIED_HISTORICAL",
        "PROSPECTIVE",
        "PILOT",
    }


def test_04_evidence_ids_unique() -> None:
    ids = [item["evidence_id"] for item in load_yaml(INV)["items"]]
    assert len(ids) == len(set(ids))


def test_05_unknown_human_governance_blocks_promotion() -> None:
    case = load_yaml(FIX)["cases"][1]
    assert promotable_tier(case) == "BLOCKED"


def test_06_synthetic_is_e0_only() -> None:
    case = load_yaml(FIX)["cases"][0]
    assert promotable_tier(case) == "E0"


def test_07_vendor_sample_is_e1_only() -> None:
    case = load_yaml(FIX)["cases"][2]
    assert promotable_tier(case) == "E1"


def test_08_no_site_compatibility_claim_for_vendor_sample() -> None:
    item = next(
        entry for entry in load_yaml(INV)["items"]
        if entry["evidence_id"] == "EV-D06-002"
    )
    assert item["site_compatibility_support"] is False


def test_09_public_vendor_not_clinical_effectiveness() -> None:
    for item in load_yaml(INV)["items"]:
        if item["source_class"] in {"SYNTHETIC", "VENDOR_SAMPLE"}:
            assert item["clinical_effectiveness_support"] is False


def test_10_knee_real_failure_request_present() -> None:
    text = REQ.read_text(encoding="utf-8")
    assert "DR-K01" in text
    assert "real governed failure case" in text


def test_11_pressure_abnormal_gait_request_present() -> None:
    text = REQ.read_text(encoding="utf-8")
    assert "abnormal/pathological gait" in text


def test_12_mfcv_not_assumed() -> None:
    text = POLICY.read_text(encoding="utf-8")
    assert "MFCV remains NOT_VERIFIED" in text


def test_13_traceability_complete() -> None:
    text = TRACE.read_text(encoding="utf-8")
    for requirement in ["PRD-11", "PRD-14", "FR-025", "DR-K01"]:
        assert requirement in text


def test_14_open_evidence_gaps_explicit() -> None:
    assert "NOT_RECEIVED" in OQ.read_text(encoding="utf-8")


def test_15_upstream_not_silently_upgraded() -> None:
    assert load_json(UP)["day06_can_claim_upstream_acceptance"] is False


def test_16_no_real_export_fabricated() -> None:
    assert load_json(UP)["real_deidentified_motionlab_export_received"] is False


def test_17_no_knee_case_fabricated() -> None:
    assert load_json(UP)["real_knee_failure_case_received"] is False


def test_18_fixture_not_clinical_evidence() -> None:
    assert load_yaml(FIX)["clinical_evidence"] is False


def test_19_manifest_day06_scoped_no_binary_artifacts() -> None:
    from day06_evidence_utils import scan_project_files
    files = scan_project_files(ROOT)
    forbidden_exts = {".npz", ".npy", ".mat", ".c3d", ".joblib", ".pkl", ".pickle", ".pt", ".pth", ".onnx"}
    whitelist_files = {"day5-preprocess-golden.npz"}
    
    violations = []
    for f in files:
        if f.suffix.lower() in forbidden_exts:
            if f.name not in whitelist_files:
                violations.append(str(f.relative_to(ROOT)))
                
    assert not violations, f"Found unauthorized binary files: {violations}"


def test_20_no_training_or_patient_data_used() -> None:
    upstream = load_json(UP)
    assert upstream["training_executed"] is False
    assert upstream["raw_patient_data_read"] is False
