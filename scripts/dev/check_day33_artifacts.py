#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = [
    "DAY33_KE_HOACH_EVALUATION_ERROR_ANALYSIS_FINAL.md",
    "ai-core/evaluation/day33/aggregation.py",
    "ai-core/evaluation/day33/day32_adapters.py",
    "ai-core/evaluation/day33/metrics.py",
    "ai-core/pipelines/day33_build_prediction_contract.py",
    "ai-core/pipelines/day33_run_evaluation.py",
    "data-platform/contracts/day33/window-prediction-columns.csv",
    "data-platform/contracts/day33/repetition-prediction-columns.csv",
    "data-platform/contracts/day33/failure-case-columns.csv",
    "qa-validation/evidence/day33/synthetic-evaluation/run-summary.json",
    "qa-validation/evidence/day33/real-development/mendeley/run-summary.json",
    "qa-validation/evidence/day33/real-development/grabmyo/run-summary.json",
    "scripts/dev/run_day33_checks.sh",
]
DAY33_SCOPES = [
    ROOT / "ai-core/evaluation/day33",
    ROOT / "ai-core/pipelines",
    ROOT / "qa-validation/evidence/day33",
    ROOT / "data-platform/contracts/day33",
    ROOT / "packages/common-schemas/json",
]
PROHIBITED_SUFFIXES = {".pkl", ".joblib", ".onnx", ".pt", ".pth", ".mat", ".dat"}

missing = [item for item in REQUIRED if not (ROOT / item).exists()]
prohibited = []
for scope in DAY33_SCOPES:
    if not scope.exists():
        continue
    for path in scope.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() in PROHIBITED_SUFFIXES:
            prohibited.append(str(path.relative_to(ROOT)))

result = {
    "schema_version": "day33-artifact-check.v1",
    "missing": missing,
    "prohibited_artifacts": prohibited,
    "pass": not missing and not prohibited,
}
output = ROOT / "qa-validation/evidence/day33-artifact-check.json"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
raise SystemExit(0 if result["pass"] else 2)
