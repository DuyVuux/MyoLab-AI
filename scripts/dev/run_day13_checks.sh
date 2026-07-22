#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONPATH="$ROOT/packages/semg-core:$ROOT/services/signal-ingestion-service/src:$ROOT/services/quality-gate-service/src:$ROOT/services/preprocessing-service/src:$ROOT/services/feature-extraction-service/src:$ROOT/services/inference-service/src${PYTHONPATH:+:$PYTHONPATH}"
if [[ "${DAY13_FULL_REGRESSION:-0}" == "1" ]]; then
  echo '[1/8] Full Day 12 regression'
  bash scripts/dev/run_day12_checks.sh
else
  echo '[1/8] Bỏ qua full Day 12 regression; chạy targeted tests Day 13'
fi
echo '[2/8] Unit/config/engine tests'
pytest -q packages/semg-core/tests/test_fatigue_rules.py services/inference-service/tests/test_rule_config.py services/inference-service/tests/test_rule_engine.py
echo '[3/8] Scenario verification'
python scripts/data/verify_fatigue_rule.py
echo '[4/8] Golden E2E'
python scripts/data/run_fatigue_rule.py --manifest data-platform/synthetic-data/golden_signal_01.manifest.json --json-out qa-validation/evidence/day13-fatigue-rule.json --expect-status completed --expect-conclusion supported_pattern
echo '[5/8] Deterministic rerun'
python scripts/data/run_fatigue_rule.py --manifest data-platform/synthetic-data/golden_signal_01.manifest.json --json-out qa-validation/evidence/day13-fatigue-rule-rerun.json --expect-status completed --expect-conclusion supported_pattern --quiet
echo '[6/8] Upstream abstention'
python qa-validation/test-data/synthetic/generate_qc_fixtures.py --source-manifest data-platform/synthetic-data/golden_signal_01.manifest.json --output-dir qa-validation/test-data/synthetic --overwrite >/dev/null
python scripts/data/run_fatigue_rule.py --manifest qa-validation/test-data/synthetic/qc_fail_flatline.manifest.json --json-out qa-validation/evidence/day13-fatigue-rule-abstained.json --expect-status abstained --expect-conclusion abstained --expect-reason RULE_ABSTAINED_BY_EVIDENCE --quiet
echo '[7/8] Validate and register'
python scripts/dev/validate_day13_outputs.py
python scripts/dev/register_fatigue_rule_v0_1.py
echo '[8/8] Artifact check'
python scripts/dev/check_day13_artifacts.py
echo 'All Day 13 checks passed.'
