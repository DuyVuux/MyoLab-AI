from pathlib import Path

REQUIRED = [
    "apps/web-portal/src/contracts/automation/index.ts",
    "apps/web-portal/src/data/automation/automation-repository.ts",
    "apps/web-portal/src/data/automation/real-automation-repository.ts",
    "apps/web-portal/src/data/automation/mock-automation-repository.ts",
    "apps/web-portal/src/lib/api/automation/endpoints.ts",
    "apps/web-portal/src/hooks/usePipelineJob.ts",
    "docs/frontend/frontend-backend-contract-map.yaml",
    "docs/frontend/uc-use-case-preservation-contract.yaml",
]

def test_ui_i1_required_files_exist():
    root = Path(__file__).resolve().parents[2]
    missing = [rel for rel in REQUIRED if not (root / rel).exists()]
    assert not missing, f"Missing UI-I1 files: {missing}"

def test_ui_i1_does_not_add_uc_route_files():
    root = Path(__file__).resolve().parents[2]
    # Foundation package must be additive and must not introduce new files under UC route trees.
    # Historical UC files can exist; preservation is enforced by PATCH_MANIFEST at package level.
    manifest = root / "docs/frontend/uc-use-case-preservation-contract.yaml"
    assert manifest.exists()
    text = manifest.read_text(encoding="utf-8")
    assert "PRESERVE_NO_BEHAVIOR_CHANGE" in text
    assert "/uc1/**" in text and "/uc4/**" in text
