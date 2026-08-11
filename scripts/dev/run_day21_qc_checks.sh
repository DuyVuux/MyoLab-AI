#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
cd "$ROOT"
export PYTHONDONTWRITEBYTECODE=1

if [[ -f pyproject.toml ]] && command -v uv >/dev/null 2>&1; then
  PY=(uv run python)
  PYTEST=(uv run pytest -p no:cacheprovider)
else
  PY=(python3)
  PYTEST=(python3 -m pytest -p no:cacheprovider)
fi

echo "[1/3] Running Day 21 QC contract validator..."
"${PY[@]}" scripts/dev/day21_qc_contract_validator.py \
  --root "$ROOT" \
  --write-report qa-validation/evidence/day21-validation-report.json

echo "[2/3] Running Day 21 QC taxonomy pytest suite..."
"${PYTEST[@]}" -q qa-validation/automated-tests/qc/test_day21_qc_taxonomy.py

echo "[3/3] Checking Day 21 QC artifact manifest hashes..."
"${PY[@]}" scripts/dev/check_day21_qc_artifacts.py --root "$ROOT"

if [[ -f scripts/dev/day20_gate_evaluator.py ]]; then
  gate_json="$("${PY[@]}" scripts/dev/day20_gate_evaluator.py --project-root "$ROOT" || true)"
  printf '%s\n' "$gate_json" > qa-validation/evidence/day21-upstream-gate-b-live-check.json
  if [[ "${DAY21_STRICT_PHASE_ENTRY:-0}" == "1" ]]; then
    "${PY[@]}" - "$gate_json" <<'RUNPY'
import json
import sys
payload = json.loads(sys.argv[1])
if payload.get("gate_decision") != "REAL_DATA_READY":
    raise SystemExit("Strict phase entry requires Gate B REAL_DATA_READY")
RUNPY
  fi
fi

echo "DAY21 QC checks PASS. Strict Gate-B enforcement: ${DAY21_STRICT_PHASE_ENTRY:-0}"
