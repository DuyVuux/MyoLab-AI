#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

mkdir -p qa-validation/evidence
LOG="qa-validation/evidence/day28-check-run.log"
: > "$LOG"

{
  echo "[day28] Python syntax"
  python - <<'PYCODE'
from pathlib import Path
import ast
paths = list(Path("ai-core/data/day28").glob("*.py")) + list(Path("scripts/data").glob("day28_*.py"))
for path in paths:
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
print(f"Parsed {len(paths)} Python files")
PYCODE

  echo "[day28] Automated tests"
  PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider qa-validation/automated-tests/test_day28_preflight.py qa-validation/automated-tests/test_day28_statistics.py

  echo "[day28] Safety string scan"
  if grep -R --line-number -E 'trainingAllowed:[[:space:]]*true|training_execution_allowed:[[:space:]]*true|clinical_use_allowed:[[:space:]]*true|motion_lab_transfer_verified:[[:space:]]*true' \
      ai-core/configs docs/05-data/day28 docs/plans packages/common-schemas qa-validation/requirements; then
    echo "Unsafe flag found"
    exit 1
  fi

  echo "[day28] No raw/model artifacts"
  if find . -type f \( -name '*.pkl' -o -name '*.joblib' -o -name '*.onnx' -o -name '*.mat' -o -name '*.c3d' -o -name '*.parquet' \) | grep -q .; then
    echo "Unexpected model/raw artifact in pack"
    exit 1
  fi

  echo "[day28] PASS"
} 2>&1 | tee "$LOG"
