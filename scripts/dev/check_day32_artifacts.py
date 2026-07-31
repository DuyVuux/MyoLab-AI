#!/usr/bin/env python3
"""Day 32 — Artifact integrity checker.

Verifies that all required Day 32 files exist in the project root
and that no prohibited model artifacts (joblib, pkl, onnx, pt) are present.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]

required = [
    "docs/plans/DAY32_EXECUTION_PLAN.md",
    "ai-core/configs/day32_core_models.research.yaml",
    "ai-core/configs/day32_optional_models.research.yaml",
    "ai-core/configs/day32_baseline_protocol.research.yaml",
    "ai-core/modeling/day32/model_factory.py",
    "ai-core/modeling/day32/authorization.py",
    "ai-core/modeling/day32/matrix_gate.py",
    "ai-core/modeling/day32/grouped_cv.py",
    "ai-core/modeling/day32/aggregation.py",
    "ai-core/modeling/day32/metrics.py",
    "ai-core/modeling/day32/smoke_runner.py",
    "ai-core/modeling/day32/core_gate.py",
    "ai-core/pipelines/day32_run_core_baselines.py",
    "ai-core/pipelines/day32_materialize_matrix.py",
    "ai-core/pipelines/day32_run_optional_baselines.py",
    "scripts/dev/run_day32_checks.sh",
    "scripts/data/day32_generate_synthetic_matrix.py",
    "scripts/data/day32_preflight.py",
]

missing = [p for p in required if not (ROOT / p).exists()]

prohibited_suffixes = {".joblib", ".pkl", ".pickle", ".onnx", ".pt", ".pth"}
# Only scan day32-related directories for prohibited artifacts
scan_dirs = [
    ROOT / "ai-core" / "modeling" / "day32",
    ROOT / "qa-validation" / "evidence" / "day32",
]
artifacts = []
for scan_dir in scan_dirs:
    if scan_dir.exists():
        for p in scan_dir.rglob("*"):
            if p.is_file() and p.suffix.lower() in prohibited_suffixes:
                artifacts.append(str(p.relative_to(ROOT)))

result = {
    "schema_version": "day32-artifact-check.v1",
    "missing": missing,
    "model_artifacts_in_repo": artifacts,
    "pass": not missing and not artifacts,
}

out = ROOT / "qa-validation" / "evidence" / "day32" / "day32-artifact-check.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
raise SystemExit(0 if result["pass"] else 2)
