from pathlib import Path
import json
import sys


def load(repo: Path):
    ai_core_dir = repo / "ai-core"
    if str(ai_core_dir) not in sys.path:
        sys.path.insert(0, str(ai_core_dir))
    try:
        from governance import phase7r_release as mod
        return mod
    except ImportError:
        import importlib.util
        path = repo / "ai-core/governance/phase7r_release.py"
        spec = importlib.util.spec_from_file_location("phase7r_release_test_entry", path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        return mod


def valid_repo(tmp_path: Path) -> Path:
    repo = tmp_path
    files = {
        "docs/00-executive/milestones/m6-r-research-ml.md": "M6-R: RESEARCH_ML_NOT_JUSTIFIED\n",
        "docs/00-executive/gates/gate-f-r-research-ml-decision.md": "Decision: RESEARCH_ML_NOT_JUSTIFIED\n",
        "qa-validation/evidence/phase6r-leakage-audit.json": json.dumps({"status": "PASS"}),
        "qa-validation/evidence/phase6r-claim-audit-contextual.json": json.dumps({"status": "PASS", "blocking_violations": 0}),
        "qa-validation/evidence/phase6r-branch-decision.json": json.dumps({"m6_r": "RESEARCH_ML_NOT_JUSTIFIED"}),
        "ai-core/research/phase6r/governance/phase6r-to-locked-validation-handoff.yaml": "m6_r: RESEARCH_ML_NOT_JUSTIFIED\nml_default: OFF\n",
    }
    for rel, text in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    return repo


def test_valid_entry_passes(tmp_path):
    repo = valid_repo(tmp_path)
    mod = load(Path(__file__).resolve().parents[2])
    result = mod.evaluate_phase7_entry(repo)
    assert result.allowed
    assert all(c.status == "PASS" for c in result.checks)


def test_missing_m6_blocks(tmp_path):
    repo = valid_repo(tmp_path)
    (repo / "docs/00-executive/milestones/m6-r-research-ml.md").unlink()
    mod = load(Path(__file__).resolve().parents[2])
    result = mod.evaluate_phase7_entry(repo)
    assert not result.allowed


def test_ml_must_be_off(tmp_path):
    repo = valid_repo(tmp_path)
    (repo / "ai-core/research/phase6r/governance/phase6r-to-locked-validation-handoff.yaml").write_text("m6_r: RESEARCH_ML_NOT_JUSTIFIED\nmodel_inclusion: none\n")
    mod = load(Path(__file__).resolve().parents[2])
    result = mod.evaluate_phase7_entry(repo)
    assert not result.allowed
