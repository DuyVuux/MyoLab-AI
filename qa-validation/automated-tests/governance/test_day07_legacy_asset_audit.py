from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/dev"))

import day07_asset_audit
import validate_day07_legacy_assets
import check_day07_artifacts
from qa_utils import scan_project_files

INVENTORY = ROOT / "data-platform/catalog/legacy-asset-inventory.v1.0.yaml"
REGRESSION = ROOT / "qa-validation/regression/legacy-regression-scope.v1.0.yaml"
DISPOSITION = ROOT / "docs/00-executive/rebaseline/legacy-asset-disposition.v1.0.md"
DEBT = ROOT / "docs/00-executive/rebaseline/technical-debt-register.v1.0.md"
TRACE = ROOT / "docs/03-architecture/traceability/day07-legacy-asset-traceability.v1.0.csv"
EXEC = ROOT / "docs/00-executive/day07/DAY07_EXECUTION_PLAN.md"
FEYNMAN = ROOT / "docs/00-executive/day07/DAY07_FEYNMAN_LEARNING_GUIDE.md"
AUDIT_SCRIPT = ROOT / "scripts/dev/day07_asset_audit.py"
VALIDATOR_SCRIPT = ROOT / "scripts/dev/validate_day07_legacy_assets.py"
CHECK_SCRIPT = ROOT / "scripts/dev/check_day07_artifacts.py"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_01_mandatory_roadmap_outputs_exist() -> None:
    for path in (DISPOSITION, REGRESSION, DEBT):
        assert path.is_file(), path


def test_02_inventory_schema_validates() -> None:
    instance = load_yaml(INVENTORY)
    schema = json.loads((ROOT / "packages/common-schemas/json/legacy-asset-inventory.schema.json").read_text())
    jsonschema.Draft202012Validator(schema).validate(instance)


def test_03_regression_schema_validates() -> None:
    instance = load_yaml(REGRESSION)
    schema = json.loads((ROOT / "packages/common-schemas/json/legacy-regression-scope.schema.json").read_text())
    jsonschema.Draft202012Validator(schema).validate(instance)


def test_04_allowed_disposition_set_is_exact() -> None:
    data = load_yaml(INVENTORY)
    assert data["allowed_dispositions"] == ["REUSE_AS_IS", "ADAPT", "REVALIDATE", "PARK", "DEPRECATE"]


def test_05_legacy_asset_ids_are_unique() -> None:
    items = load_yaml(INVENTORY)["asset_families"]
    ids = [item["id"] for item in items]
    assert len(ids) == len(set(ids))


def test_06_inventory_covers_required_asset_families() -> None:
    items = load_yaml(INVENTORY)["asset_families"]
    assert len(items) >= 20


def test_07_binary_fatigue_product_center_is_deprecated() -> None:
    items = {item["id"]: item for item in load_yaml(INVENTORY)["asset_families"]}
    assert items["LA-09"]["disposition"] == "DEPRECATE"


def test_08_mfcv_is_revalidation_gated() -> None:
    items = {item["id"]: item for item in load_yaml(INVENTORY)["asset_families"]}
    assert items["LA-10"]["disposition"] == "REVALIDATE"


def test_09_public_healthy_datasets_are_parked() -> None:
    items = {item["id"]: item for item in load_yaml(INVENTORY)["asset_families"]}
    assert items["LA-18"]["disposition"] == "PARK"


def test_10_old_post_preday41_schedule_is_deprecated() -> None:
    items = {item["id"]: item for item in load_yaml(INVENTORY)["asset_families"]}
    assert items["LA-19"]["disposition"] == "DEPRECATE"


def test_11_all_prd_product_principles_are_present() -> None:
    text = DISPOSITION.read_text(encoding="utf-8")
    principles = (
        "Quality before intelligence",
        "Preserve physiology",
        "Human final authority",
        "Abstain over hallucinate",
        "Traceable by design",
        "Automation of toil first",
        "Modality-neutral foundation",
    )
    for principle in principles:
        assert principle in text


def test_12_traceability_has_exact_day07_authorities() -> None:
    text = TRACE.read_text(encoding="utf-8")
    for token in ("PRD_PRODUCT_PRINCIPLES", "NFR-001", "NFR-011"):
        assert token in text


def test_13_regression_suites_never_authorize_clinical_claim() -> None:
    suites = load_yaml(REGRESSION)["suites"]
    assert suites
    assert all(suite["clinical_claim_allowed"] is False for suite in suites)


def test_14_regression_gate_distinguishes_site_validation() -> None:
    gate = load_yaml(REGRESSION)["regression_gate"]
    assert "does not establish site validity" in gate["success_meaning"]


def test_15_technical_debt_contains_critical_evidence_debt() -> None:
    text = DEBT.read_text(encoding="utf-8")
    assert "TD-002" in text
    assert "Severity: CRITICAL" in text
    assert "site-validated" in text


def test_16_repo_confirmation_debt_is_explicit() -> None:
    text = DEBT.read_text(encoding="utf-8")
    assert "TD-015" in text
    assert "post-DAY06 monorepo" in text
    assert "day07_asset_audit.py" in text


def test_17_inventory_requires_repo_confirmation() -> None:
    data = load_yaml(INVENTORY)
    assert data["repo_confirmation"]["required"] is True
    assert "day07_asset_audit.py" in data["repo_confirmation"]["command"]


def test_18_synthetic_path_cases_classify_as_expected() -> None:
    cases = load_yaml(ROOT / "qa-validation/test-data/day07/synthetic-repo-asset-cases.yaml")["cases"]
    for case in cases:
        assert day07_asset_audit.classify(Path(case["path"])) == case["expected_family"], case


def test_19_git_tracked_scan_preferred_in_synthetic_repo(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    path = tmp_path / "ai-core/configs/day37_taskc_metric_registry.yaml"
    path.parent.mkdir(parents=True)
    path.write_text("version: 1\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], check=True)
    files = day07_asset_audit.tracked_files(tmp_path)
    assert files is not None
    assert Path("ai-core/configs/day37_taskc_metric_registry.yaml") in files


def test_20_os_walk_fallback_prunes_infrastructure_and_data_payloads(tmp_path: Path) -> None:
    good = tmp_path / "ai-core/day34-personalization-v2/file.txt"
    good.parent.mkdir(parents=True)
    good.write_text("x", encoding="utf-8")
    noisy = tmp_path / ".venv/lib/noise.txt"
    noisy.parent.mkdir(parents=True)
    noisy.write_text("x", encoding="utf-8")
    data = tmp_path / "datasets/external/huge.bin"
    data.parent.mkdir(parents=True)
    data.write_text("x", encoding="utf-8")
    files = {path.as_posix() for path in day07_asset_audit.walk_files(tmp_path)}
    assert "ai-core/day34-personalization-v2/file.txt" in files
    assert not any(".venv" in path for path in files)
    assert not any(path.startswith("datasets/") for path in files)


def test_21_audit_reports_unknown_legacy_candidates() -> None:
    report = day07_asset_audit.audit([Path("docs/day33_weird_legacy_unknown.xyz")])
    assert report["unclassified_count"] == 1
    assert report["repo_confirmation_complete"] is False


def test_22_no_forbidden_new_model_or_patient_binary_artifacts() -> None:
    files = scan_project_files(ROOT, extra_skip_dirs={".mypy_cache", ".ruff_cache", "dist", "build"})
    forbidden_exts = {".joblib", ".pkl", ".pickle", ".pt", ".pth", ".onnx", ".mat", ".npz", ".npy", ".c3d"}
    whitelist_files = {"day5-preprocess-golden.npz"}
    
    violations = []
    for f in files:
        if f.suffix.lower() in forbidden_exts:
            if f.name not in whitelist_files:
                violations.append(str(f.relative_to(ROOT)))
                
    assert not violations, f"Found unauthorized binary files: {violations}"


def test_23_managed_paths_do_not_include_cache_artifacts() -> None:
    offenders = [
        rel
        for rel in check_day07_artifacts.MANAGED
        if "__pycache__" in Path(rel).parts or ".pytest_cache" in Path(rel).parts or Path(rel).suffix == ".pyc"
    ]
    assert offenders == []


def test_24_python_scripts_compile() -> None:
    for path in (AUDIT_SCRIPT, VALIDATOR_SCRIPT, CHECK_SCRIPT):
        py_compile.compile(str(path), doraise=True)


def test_25_default_status_cannot_be_go_without_repo_and_human_review() -> None:
    assert validate_day07_legacy_assets.determine_status(False, False) == "READY_WITH_LIMITATIONS"
    assert validate_day07_legacy_assets.determine_status(True, False) == "READY_WITH_LIMITATIONS"
    assert validate_day07_legacy_assets.determine_status(True, True) == "GO_FOR_DAY_08"


def test_26_execution_plan_has_all_required_sections() -> None:
    text = EXEC.read_text(encoding="utf-8")
    required = [
        "## 0. Document Control", "## 1. Executive Intent", "## 2. Why This Day Exists",
        "## 3. Position in the 90-Day Critical Path", "## 4. Relationship With Previous Day",
        "## 5. What Must Be True Before Starting", "## 6. Objectives",
        "## 7. Non-Goals / Explicitly Out of Scope", "## 8. Source-of-Truth for This Day",
        "## 9. Requirements Addressed Today", "## 10. Inputs", "## 11. Mandatory Outputs",
        "## 12. Supporting Outputs", "## 13. Target Repo Tree After This Day",
        "## 14. Data / Evidence Boundaries", "## 15. Safety & Governance Invariants",
        "## 16. Environment / Tooling Requirements", "## 17. Preflight Checklist",
        "# 18. Detailed Execution Procedure", "## 19. Automated Validation Strategy",
        "## 20. Manual / Expert Review", "## 21. Failure Injection / Negative Tests",
        "## 22. Requirement Traceability", "## 23. Acceptance Criteria", "## 24. Definition of Done",
        "## 25. Stop / Block Conditions", "## 26. Known Limitations", "## 27. Open Questions Carried Forward",
        "## 28. Integration Into Main Repository", "## 29. Git Workflow", "## 30. Rollback Procedure",
        "## 31. Evidence & Provenance Capture", "## 32. Closeout Checklist", "## 33. DAY 08 Handoff",
        "## 34. Final Day Status Rules",
    ]
    for heading in required:
        assert heading in text, heading


def test_27_execution_steps_have_required_step_fields() -> None:
    text = EXEC.read_text(encoding="utf-8")
    steps = text.split("## STEP ")[1:]
    assert len(steps) >= 10
    required_fields = (
        "### Goal", "### Input", "### Why", "### Concepts used", "### Action",
        "### Files to create / modify", "### Code / Command", "### Expected Output",
        "### Verification", "### Negative Check", "### Evidence Produced",
        "### Stop Condition", "### Pass Condition",
    )
    for step in steps:
        for field in required_fields:
            assert field in step, (step[:80], field)


def test_28_feynman_has_learning_depth_components() -> None:
    text = FEYNMAN.read_text(encoding="utf-8")
    required = (
        "## 0. Learning Objectives", "## 3. Mental Model tổng thể", "## 4. Vocabulary Map",
        "## 17. Worked Example 1", "## 18. Worked Example 2", "## 19. Worked Example 3",
        "## 20. Counterexamples", "## 21. Những lỗi junior thường mắc",
        "## 23. Những gì chưa cần học hôm nay", "## 24. Flashcards", "## 25. Exercises",
        "## 26. Quiz", "## 27. Answers with Explanation", "## 28. Teach-back Test",
        "## 29. Final Mental Model", "## 30. Readiness Checklist for Next Day",
    )
    for heading in required:
        assert heading in text, heading


def test_29_docs_meet_depth_floor_without_using_length_as_only_quality_gate() -> None:
    exec_words = len(EXEC.read_text(encoding="utf-8").split())
    feynman_words = len(FEYNMAN.read_text(encoding="utf-8").split())
    assert exec_words >= 4000, exec_words
    assert feynman_words >= 4000, feynman_words


def test_30_closeout_keeps_pre_integration_status_ready_with_limitations() -> None:
    closeout = (ROOT / "docs/00-executive/day07/day07-closeout-summary.v1.0.md").read_text(encoding="utf-8")
    assert "Final status before current-repo audit: `READY_WITH_LIMITATIONS`" in closeout
    assert "Actual current-repo path binding: required" in closeout


def test_31_document_quality_self_review_has_no_score_below_four() -> None:
    review = json.loads((ROOT / "qa-validation/evidence/day07-document-quality-review.json").read_text(encoding="utf-8"))
    assert review["result"] == "PASS"
    assert all(item["score"] >= review["minimum_allowed_score"] for item in review["dimensions"].values())
    assert all(value == "PASS" for value in review["adversarial_review"].values())
