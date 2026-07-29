from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = [
    "DAY27_KE_HOACH_PUBLIC_DATASET_ENGINEERING_FINAL.md",
    "docs/plans/DAY27_EXECUTION_PLAN.md",
    "docs/05-data/public-datasets/mendeley-4channel-hand-gesture-v2/01-dataset-selection-decision.md",
    "ai-core/configs/day27_dataset_selection.research.yaml",
    "ai-core/data/day27/engineering_gate.py",
    "scripts/data/day27_acquire_public_dataset.py",
    "packages/common-schemas/json/engineering-data-gate.v1.schema.json",
    "qa-validation/requirements/day27-acceptance-criteria.md",
]
SKIP_DIRS = {".venv", "node_modules", ".next", ".git", ".agents", "day27_public_dataset_engineering_pack", ".pytest_cache", "__pycache__"}
errors = []
for rel in REQUIRED:
    if not (ROOT / rel).is_file():
        errors.append(f"MISSING:{rel}")
for path in ROOT.rglob("*"):
    if not path.is_file():
        continue
    rel = str(path.relative_to(ROOT))
    if any(rel.startswith(skip + "/") or ("/" + skip + "/") in rel or (skip + "/") in rel for skip in SKIP_DIRS):
        continue
    if "__pycache__" in rel or ".pytest_cache" in rel or path.suffix == ".pyc":
        errors.append(f"CACHE_ARTIFACT:{rel}")
    if path.suffix.lower() in {".zip", ".tar", ".gz", ".pkl", ".pickle", ".joblib", ".onnx", ".pt", ".pth", ".mat", ".dat", ".hea"}:
        errors.append(f"FORBIDDEN_ARTIFACT:{rel}")
report = {
    "schemaVersion":"day27-tooling-validation.v1",
    "packValid":not errors,
    "errors":errors,
    "realDatasetPresent":False,
    "realEngineeringDataGateStatus":"PENDING_EXTERNAL_DATA",
    "trainingExecutionAllowed":False,
    "testSetOpened":False,
}
out = ROOT / "qa-validation/evidence/day27-tooling-validation.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(0 if not errors else 2)
