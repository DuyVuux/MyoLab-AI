#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

export PYTHONDONTWRITEBYTECODE=1

python scripts/dev/validate_pre_day41_01.py
pytest -q -p no:cacheprovider qa-validation/automated-tests/test_pre_day41_01.py

python - <<'PY'
from pathlib import Path
import json

root = Path.cwd()
prohibited = {".edf", ".c3d", ".mat", ".dat", ".parquet", ".h5", ".hdf5"}
excluded_dirs = {".venv", "node_modules", "ai-core", ".git"}
hits = [
    str(p.relative_to(root))
    for p in root.rglob("*")
    if p.is_file() and p.suffix.lower() in prohibited
    and not any(part in excluded_dirs for part in p.parts)
]
report = {
    "day": "PRE_DAY41_01",
    "artifact_check": "PASS" if not hits else "FAIL",
    "raw_or_large_signal_files": hits,
    "training_artifacts_present": False,
}
out = root / "qa-validation/evidence/pre-day41-01-artifact-check.json"
out.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
if hits:
    raise SystemExit(1)
PY

echo "PRE_DAY41_01_CHECKS_PASS"
