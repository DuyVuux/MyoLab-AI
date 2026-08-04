#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
required = [
    "DAY37_KE_HOACH_TASK_C_QUANTITATIVE_METRICS_FINAL.md",
    "notebooks/Day37_TaskC_Quantitative_Metrics_Scenarios.ipynb",
    "ai-core/quantitative/day37/repeatability.py",
    "ai-core/quantitative/day37/similarity.py",
    "ai-core/quantitative/day37/cocontraction.py",
    "data-platform/contracts/day37/taskc-event.schema.json",
    "scripts/dev/run_day37_checks.sh",
]
missing = [x for x in required if not (ROOT / x).exists()]
prohibited = [
    str(p.relative_to(ROOT))
    for p in ROOT.rglob("*")
    if p.is_file() and p.suffix.lower() in {".mat", ".dat", ".pkl", ".joblib", ".onnx", ".pt", ".pth"}
]
result = {
    "schema_version": "day37-artifact-check.v1",
    "missing": missing,
    "prohibited_raw_or_model_artifacts": prohibited,
    "pass": not missing and not prohibited,
}
out = ROOT / "qa-validation" / "evidence" / "day37-artifact-check.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
raise SystemExit(0 if result["pass"] else 2)
