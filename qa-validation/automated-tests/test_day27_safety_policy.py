from __future__ import annotations
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core"))


def test_training_flags_remain_false():
    yaml_text = (ROOT/"ai-core/configs/day27_training_authorization.research.yaml").read_text(encoding="utf-8")
    assert "training_allowed: false" in yaml_text
    selection = (ROOT/"ai-core/configs/day27_dataset_selection.research.yaml").read_text(encoding="utf-8")
    assert "training_execution_allowed: false" in selection


def test_no_raw_or_model_artifacts_in_pack():
    forbidden_suffixes = {".pkl", ".pickle", ".joblib", ".onnx", ".pt", ".pth", ".h5", ".mat", ".dat", ".hea"}
    skip_dirs = {".venv", "node_modules", ".next", ".git", ".agents", "day27_public_dataset_engineering_pack"}
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = str(path.relative_to(ROOT))
        if any(rel.startswith(skip + "/") or ("/" + skip + "/") in rel for skip in skip_dirs):
            continue
        assert path.suffix.lower() not in forbidden_suffixes, f"Forbidden artifact: {rel}"
