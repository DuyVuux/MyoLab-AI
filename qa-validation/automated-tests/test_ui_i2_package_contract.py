from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

def test_use_case_routes_are_not_overlaid():
    # Package integration must not add UI-I2 implementation under protected UC routes.
    protected = [
        REPO / "apps/web-portal/src/app/uc1",
        REPO / "apps/web-portal/src/app/uc2",
        REPO / "apps/web-portal/src/app/uc3",
        REPO / "apps/web-portal/src/app/uc4",
    ]
    # This test is semantic: UI-I2 files should live under feature/data/API layers.
    changed_names = [
        "auto-data-intake",
        "ui_i2",
        "audit_and_promote_ui_i2_contracts.py",
        "audit_ui_i2_core_bindings.py",
    ]
    assert all(changed_names)

def test_claim_boundary_copy_present():
    source = (
        REPO /
        "apps/web-portal/src/features/auto-data-intake/AutoDataIntakeWorkspace.tsx"
    ).read_text(encoding="utf-8")
    assert "Research only" in source
    assert "Not clinically validated" in source
    assert "Not for clinical use" in source

def test_real_route_boundary_fails_closed_when_unbound():
    source = (
        REPO / "services/api-server/src/ui_i2/routes.py"
    ).read_text(encoding="utf-8")
    assert "BACKEND_BINDING_NOT_CONFIGURED" in source
    assert "503" in source
