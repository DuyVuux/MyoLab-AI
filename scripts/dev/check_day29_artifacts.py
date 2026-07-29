#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED = [
    "docs/plans/DAY29_EXECUTION_PLAN.md",
    "ai-core/configs/day29_grabmyo_eda.research.yaml",
    "ai-core/configs/day29_grabmyo_quality_rules.provisional.yaml",
    "ai-core/configs/day29_cross_day_drift.research.yaml",
    "scripts/data/day29_preflight.py",
    "scripts/data/day29_run_eda.py",
    "scripts/dev/run_day29_checks.sh",
    "qa-validation/requirements/day29-acceptance-criteria.md",
]


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).exists()]
    prohibited_suffixes = {".pkl", ".pickle", ".joblib", ".onnx", ".pt", ".pth"}
    excluded_dirs = {".venv", "venv", "node_modules", ".git", "__pycache__",
                     "day29_grabmyo_eda_data_quality_pack", ".agents"}

    def _project_files() -> list[Path]:
        files: list[Path] = []
        for path in ROOT.rglob("*"):
            if any(part in excluded_dirs for part in path.relative_to(ROOT).parts):
                continue
            if path.is_file():
                files.append(path)
        return files

    all_files = _project_files()
    prohibited = [
        str(path.relative_to(ROOT))
        for path in all_files
        if path.suffix.lower() in prohibited_suffixes
    ]

    unsafe_text: list[str] = []
    for path in all_files:
        if path.suffix.lower() not in {".yaml", ".yml", ".json"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        if "training_allowed: true" in text or '"training_allowed": true' in text:
            unsafe_text.append(str(path.relative_to(ROOT)))

    result = {
        "schema_version": "day29-artifact-check.v1",
        "missing": missing,
        "prohibited_model_artifacts": prohibited,
        "training_enable_violations": unsafe_text,
        "pass": not missing and not prohibited and not unsafe_text,
    }
    output = ROOT / "qa-validation/evidence/day29-artifact-check.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
