#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
required = [
    "DAY32_KE_HOACH_CLASSICAL_BASELINE_FINAL.md",
    "ai-core/configs/day32_core_models.research.yaml",
    "ai-core/configs/day32_optional_models.research.yaml",
    "ai-core/modeling/day32/model_factory.py",
    "ai-core/pipelines/day32_run_core_baselines.py",
    "scripts/dev/run_day32_checks.sh",
]
missing = [p for p in required if not (ROOT/p).exists()]
prohibited_suffixes = {".joblib",".pkl",".pickle",".onnx",".pt",".pth"}
artifacts = [
    str(p.relative_to(ROOT)) for p in ROOT.rglob("*")
    if p.is_file() and p.suffix.lower() in prohibited_suffixes
]
result = {
    "schema_version":"day32-artifact-check.v1",
    "missing":missing,
    "model_artifacts_in_portable_pack":artifacts,
    "pass":not missing and not artifacts,
}
out=ROOT/"qa-validation/evidence/day32-artifact-check.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,indent=2))
raise SystemExit(0 if result["pass"] else 2)
