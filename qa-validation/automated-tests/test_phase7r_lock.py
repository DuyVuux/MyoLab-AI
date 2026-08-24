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
        spec = importlib.util.spec_from_file_location("phase7r_release_test_lock", path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        return mod


def test_freeze_and_verify(tmp_path):
    mod = load()
    p = tmp_path / "qa-validation/evidence/split.yaml"
    p.parent.mkdir(parents=True)
    p.write_text("split: frozen\n")
    q = tmp_path / "ai-core/configs/qc.yaml"
    q.parent.mkdir(parents=True)
    q.write_text("threshold: frozen\n")
    payload = mod.freeze_manifest(tmp_path, [p, q])
    assert payload["lock_sha256"]
    assert all(c.status == "PASS" for c in mod.verify_manifest(tmp_path, payload))


def test_mutation_breaks_lock(tmp_path):
    mod = load()
    p = tmp_path / "manifest.yaml"
    p.write_text("a: 1\n")
    payload = mod.freeze_manifest(tmp_path, [p])
    p.write_text("a: 2\n")
    assert any(c.status == "FAIL" for c in mod.verify_manifest(tmp_path, payload))


def test_outside_repo_rejected(tmp_path):
    mod = load()
    outside = tmp_path.parent / "outside-freeze.txt"
    outside.write_text("x")
    try:
        mod.freeze_manifest(tmp_path, [outside])
        assert False
    except ValueError:
        assert True
