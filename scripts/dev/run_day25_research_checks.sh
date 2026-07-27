#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

export PYTHONPATH="$ROOT/ai-core:$ROOT:$ROOT/scripts/data:${PYTHONPATH:-}"

required=(
  docs/plans/DAY25_EXECUTION_PLAN.md
  docs/05-data/day25-research/dataset-inventory-v0.2.csv
  integrations/devices/noraxon/site-export-evidence-bundle.template.json
)
for file in "${required[@]}"; do
  [[ -f "$file" ]] || { echo "Thiếu prerequisite: $file" >&2; exit 1; }
done

echo "[1/8] Python syntax"
python -m compileall -q ai-core/data integrations/devices/noraxon scripts/data scripts/dev

echo "[2/8] Dataset inventory and license/access invariants"
python scripts/data/validate_day25_research_inventory.py

echo "[3/8] Subject-safe split"
python scripts/data/build_subject_group_split_v2.py \
  --metadata qa-validation/test-data/synthetic/day25-subject-session-metadata.json \
  --output qa-validation/evidence/day25-subject-group-split-v0.2.json \
  --seed 2501

echo "[4/8] Noraxon site evidence audit (expected NOT_VERIFIED)"
python scripts/data/audit_noraxon_site_evidence.py \
  --evidence integrations/devices/noraxon/site-export-evidence-bundle.template.json \
  --output qa-validation/evidence/day25-noraxon-site-audit.json

echo "[5/8] Data readiness gate"
python scripts/data/build_day25_readiness_gate.py \
  --output qa-validation/evidence/day25-data-readiness-gate-v0.2.json

echo "[6/8] Automated tests"
pytest -q \
  qa-validation/automated-tests/test_day25_research_catalog_v2.py \
  qa-validation/automated-tests/test_day25_group_split_v2.py \
  qa-validation/automated-tests/test_day25_site_audit_v2.py \
  qa-validation/automated-tests/test_day25_readiness_gate_v2.py \
  qa-validation/automated-tests/test_day25_contract_schemas_v2.py \
  qa-validation/automated-tests/test_day25_conflict_register_v2.py

echo "[7/8] JSON evidence summary"
python - <<'PY'
import json
from pathlib import Path
root = Path('.')
gate = json.loads((root/'qa-validation/evidence/day25-data-readiness-gate-v0.2.json').read_text())
site = json.loads((root/'qa-validation/evidence/day25-noraxon-site-audit.json').read_text())
assert gate['status'] == 'CONDITIONAL_READY'
assert gate['trainingAllowed'] is False
assert site['checks']['nativeJsonExportVerified'] is False
assert site['checks']['mfcvEligibilityVerified'] is False
print(json.dumps({
  'readiness': gate['status'],
  'implementationAllowed': gate['implementationAllowed'],
  'trainingAllowed': gate['trainingAllowed'],
  'siteStatus': site['status'],
  'nativeJsonVerified': site['checks']['nativeJsonExportVerified'],
  'mfcvVerified': site['checks']['mfcvEligibilityVerified'],
}, ensure_ascii=False, indent=2))
PY

echo "[8/8] Artifact/safety checker"
python scripts/dev/check_day25_research_artifacts.py

echo "All Day 25 research-grounded checks passed."
