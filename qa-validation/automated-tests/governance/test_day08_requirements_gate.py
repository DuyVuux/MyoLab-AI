from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import jsonschema
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]

MANDATORY = [
    ROOT / "docs/01-product/PRD-motionlab-rebaseline-delta.v0.2.md",
    ROOT / "docs/03-architecture/SRS-traceability-baseline.v0.2.md",
    ROOT / "docs/00-executive/gates/GATE-A-requirements-readiness.md",
]
FREEZE = ROOT / "data-platform/contracts/requirements-freeze.v0.2.yaml"
MATRIX = ROOT / "qa-validation/traceability/day08-requirement-freeze-matrix.csv"
GATE = ROOT / "qa-validation/evidence/day08-gate-a-evidence.yaml"
SCHEMA = ROOT / "packages/common-schemas/json/gate-a-readiness.schema.json"
EXEC = ROOT.parents[0] / "DAY08_EXECUTION_PLAN.md" if (ROOT.parents[0] / "DAY08_EXECUTION_PLAN.md").exists() else None


def y(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_01_mandatory_outputs_exist():
    assert all(path.is_file() for path in MANDATORY)


def test_02_gate_schema_validates():
    jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text())).validate(y(GATE))


def test_03_requirement_count_is_79():
    assert len(y(FREEZE)["requirements"]) == 79


def test_04_requirement_type_counts_exact():
    counts = Counter(r["requirement_type"] for r in y(FREEZE)["requirements"])
    assert counts == Counter({"FUNCTIONAL": 57, "NON_FUNCTIONAL": 12, "ACCEPTANCE_CRITERION": 10})


def test_05_requirement_ids_unique():
    ids = [r["requirement_id"] for r in y(FREEZE)["requirements"]]
    assert len(ids) == len(set(ids))


def test_06_all_design_mapped():
    assert all(r["day08_design_mapping_state"] == "DESIGNED" for r in y(FREEZE)["requirements"])


def test_07_none_claim_validated():
    assert all(r["validation_state_at_gate_a"] == "NOT_VALIDATED" for r in y(FREEZE)["requirements"])


def test_08_requirement_text_frozen():
    assert all(r["requirement_text_freeze_state"] == "FROZEN" for r in y(FREEZE)["requirements"])


def test_09_matrix_has_79_rows():
    with MATRIX.open(encoding="utf-8", newline="") as f:
        assert len(list(csv.DictReader(f))) == 79


def test_10_ac10_present_and_safe():
    ac10 = next(r for r in y(FREEZE)["requirements"] if r["requirement_id"] == "AC-10")
    assert "commitment" in ac10["gate_a_note"].lower()
    assert ac10["validation_state_at_gate_a"] == "NOT_VALIDATED"


def test_11_prd_delta_preserves_north_star():
    text = MANDATORY[0].read_text(encoding="utf-8")
    assert "Giảm thời gian bác sĩ MotionLab" in text
    assert "AUTOMATION OF TOIL FIRST" in text


def test_12_prd_delta_blocks_mfcv_assumption():
    text = MANDATORY[0].read_text(encoding="utf-8")
    assert "MFCV remains optional" in text
    assert "16 sensors" in text


def test_13_prd_delta_blocks_knee_algorithm():
    text = MANDATORY[0].read_text(encoding="utf-8")
    assert "DR-K01..DR-K08" in text
    assert "does not authorize Knee ML/model development" in text


def test_14_traceability_explicit_design_not_implementation():
    text = MANDATORY[1].read_text(encoding="utf-8")
    assert "không có nghĩa implementation" in text or "does not mean implementation" in text
    assert "79/79" in text


def test_15_gate_is_not_pass_by_schedule():
    text = MANDATORY[2].read_text(encoding="utf-8")
    assert "calendar" in text.lower()
    assert "green pytest" in text.lower()


def test_16_gate_has_binary_decision():
    text = MANDATORY[2].read_text(encoding="utf-8")
    assert "REQUIREMENTS_READY" in text
    assert "BLOCKED_DISCOVERY" in text


def test_17_pack_gate_defaults_fail_closed():
    gate = y(GATE)
    assert gate["decision"]["gate_decision"] == "BLOCKED_DISCOVERY"
    assert gate["decision"]["day_status"] == "BLOCKED_WITH_EVIDENCE"


def test_18_manual_review_defaults_pending():
    assert y(GATE)["manual_review"]["status"] == "PENDING"


def test_19_all_gate_ids_unique():
    ids = [c["id"] for c in y(GATE)["criteria"]]
    assert len(ids) == len(set(ids))


def test_20_all_gate_critical():
    assert all(c["critical"] for c in y(GATE)["criteria"])


def test_21_no_autonomous_clinical_claim():
    corpus = "\n".join(p.read_text(encoding="utf-8") for p in MANDATORY).lower()
    assert "autonomous diagnosis" not in corpus or "does not claim" in corpus
    assert "auto-finalize" not in corpus or "no" in corpus


def test_22_no_numeric_target_commitment():
    prd = MANDATORY[0].read_text(encoding="utf-8").lower()
    assert "official pilot target is 50%" not in prd
    assert ">=50%" in prd
    assert "không phải commitment" in prd or "not commitment" in prd or "not a commitment" in prd


def test_23_no_forbidden_binary_artifact_in_project_files():
    from scripts.dev.qa_utils import scan_project_files
    forbidden = {".npz", ".npy", ".mat", ".joblib", ".pkl", ".pt", ".pth", ".onnx"}
    project_files = scan_project_files(ROOT, extra_skip_dirs={"DAY08_REQUIREMENTS_V02_FREEZE_GATE_A_HANDOFF"})
    found = [p for p in project_files if p.suffix.lower() in forbidden and p.name != "day5-preprocess-golden.npz"]
    assert not found, f"Forbidden binaries found: {found}"


def test_24_manifest_scope_is_day08_only():
    manifest = json.loads((ROOT / "qa-validation/evidence/day08-artifact-manifest.json").read_text())
    assert manifest["scope"] == "DAY08_MANAGED_ARTIFACTS_ONLY"


def test_25_gate_negative_fixture_blocks():
    from scripts.dev.evaluate_day08_gate_a import evaluate_gate
    data = y(ROOT / "qa-validation/test-data/day08/gate-a-negative-missing-privacy.yaml")
    decision, status, blockers = evaluate_gate(data)
    assert decision == "BLOCKED_DISCOVERY"
    assert status == "BLOCKED_WITH_EVIDENCE"
    assert blockers


def test_26_gate_positive_fixture_goes():
    from scripts.dev.evaluate_day08_gate_a import evaluate_gate
    data = y(ROOT / "qa-validation/test-data/day08/gate-a-positive-test-only.yaml")
    decision, status, blockers = evaluate_gate(data)
    assert decision == "REQUIREMENTS_READY"
    assert status == "GO_FOR_DAY_09"
    assert not blockers


def test_27_positive_fixture_is_marked_test_only():
    data = y(ROOT / "qa-validation/test-data/day08/gate-a-positive-test-only.yaml")
    assert data.get("test_fixture_only") is True


def test_28_open_evidence_doc_exists():
    assert (ROOT / "docs/00-executive/rebaseline/day08-open-evidence-carry-forward.md").is_file()


def test_29_acceptance_doc_distinguishes_engineering_and_gate():
    text = (ROOT / "qa-validation/requirements/day08-acceptance-criteria.md").read_text(encoding="utf-8")
    assert "Engineering acceptance" in text
    assert "Evidence/Gate acceptance" in text


def test_30_source_hash_ledger_exists():
    assert (ROOT / "qa-validation/evidence/day08-source-hash-ledger.json").is_file()


def test_31_quality_review_all_scores_at_least_4():
    review = json.loads((ROOT / "qa-validation/evidence/day08-document-quality-review.json").read_text())
    assert all(score >= 4 for score in review["scores"].values())


def test_32_no_pycache_or_pyc_in_manifest():
    manifest = json.loads((ROOT / "qa-validation/evidence/day08-artifact-manifest.json").read_text())
    assert not [item for item in manifest["files"] if "__pycache__" in item["path"] or item["path"].endswith(".pyc")]
