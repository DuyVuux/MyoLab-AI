#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-$(pwd)}"
cd "$PROJECT_ROOT"

export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$PROJECT_ROOT${PYTHONPATH:+:$PYTHONPATH}"

printf '[DAY08] root=%s\n' "$PROJECT_ROOT"

if [[ "${DAY08_STRICT_UPSTREAM:-0}" == "1" ]]; then
  if [[ -x scripts/dev/run_day07_checks.sh ]]; then
    echo '[DAY08] running DAY07 regression in strict mode'
    bash scripts/dev/run_day07_checks.sh
  else
    echo '[DAY08][FAIL] DAY07 runner missing in strict mode' >&2
    exit 2
  fi
else
  if [[ -x scripts/dev/run_day07_checks.sh ]]; then
    echo '[DAY08] DAY07 runner detected; running regression'
    bash scripts/dev/run_day07_checks.sh
  else
    echo '[DAY08] isolated-pack mode: DAY07 runner not present; Gate evidence must remain NOT_VERIFIED'
  fi
fi

python3 scripts/dev/validate_day08_requirements_gate.py --root .
python3 -m pytest -q -p no:cacheprovider qa-validation/automated-tests/governance/test_day08_requirements_gate.py
python3 scripts/dev/evaluate_day08_gate_a.py --root . --write-report qa-validation/evidence/day08-gate-a-evaluation.json
python3 scripts/dev/check_day08_artifacts.py --root .

echo '[DAY08] engineering checks complete; inspect Gate A evidence/manual review before promotion.'
