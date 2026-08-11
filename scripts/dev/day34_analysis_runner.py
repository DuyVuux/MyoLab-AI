from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    module = load_module(
        "day34_analysis_cli",
        root / "qa-validation/lib/day34_weak_label_analysis.py",
    )
    family_rows, integrity_rows = module.run_evaluation(
        root / "qa-validation/evidence/research-benchmark-corpus-v0.1.manifest.yaml",
        root / "qa-validation/test-data/research/day33/corpus",
        repo_root=root,
    )
    summary = module.write_outputs(
        root / "qa-validation/evidence",
        family_rows,
        integrity_rows,
    )
    print(json.dumps({"status": "PASS", **summary}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
