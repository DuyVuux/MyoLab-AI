#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED = [
    "DAY29_KE_HOACH_GRABMYO_EDA_DATA_QUALITY_FINAL.md",
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
    prohibited = [
        str(path.relative_to(ROOT))
        for path in ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in prohibited_suffixes
    ]

    unsafe_text: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".yaml", ".yml", ".json"}:
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
