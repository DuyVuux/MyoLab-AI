from pathlib import Path
import sys


def load():
    repo = Path(__file__).resolve().parents[2]
    ai_core_dir = repo / "ai-core"
    if str(ai_core_dir) not in sys.path:
        sys.path.insert(0, str(ai_core_dir))
    try:
        from governance import phase7r_release as mod
        return mod
    except ImportError:
        import importlib.util
        path = repo / "ai-core/governance/phase7r_release.py"
        spec = importlib.util.spec_from_file_location("phase7r_release_test_guard", path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        return mod


def test_final_status_decision():
    mod = load()
    assert mod.decide_final_status(False, []) == "BLOCKED_WITH_EVIDENCE"
    assert mod.decide_final_status(True, ["noncritical"]) == "READY_WITH_LIMITATIONS"
    assert mod.decide_final_status(True, []) == "PORTFOLIO_RESEARCH_READY"


def test_unsupported_positive_claim_blocked(tmp_path):
    mod = load()
    p = tmp_path / "report.md"
    p.write_text("This system is clinically validated and ready.\n")
    assert mod.claim_audit([p])


def test_negated_claim_not_blocked(tmp_path):
    mod = load()
    p = tmp_path / "limitations.md"
    p.write_text("Claim boundary: NOT clinically validated. Do not claim validated at Vinmec.\n")
    assert mod.claim_audit([p]) == []
