#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)";cd "$ROOT"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONPATH="$ROOT/packages/semg-core:$ROOT/services/signal-ingestion-service/src:$ROOT/services/quality-gate-service/src:$ROOT/services/preprocessing-service/src:$ROOT/services/feature-extraction-service/src:$ROOT/services/inference-service/src${PYTHONPATH:+:$PYTHONPATH}"
if [[ "${DAY12_FULL_REGRESSION:-0}" == "1" ]];then echo '[1/8] Full Day 11';bash scripts/dev/run_day11_checks.sh;else echo '[1/8] Bỏ qua full Day 11';fi
echo '[2/8] Tests';pytest -q packages/semg-core/tests/test_fatigue_evidence.py services/inference-service/tests/test_evidence_config.py
echo '[3/8] Scenario verification';python scripts/data/verify_fatigue_evidence.py
echo '[4/8] Golden E2E';python scripts/data/run_fatigue_evidence.py --manifest data-platform/synthetic-data/golden_signal_01.manifest.json --json-out qa-validation/evidence/day12-fatigue-evidence.json --expect-status completed --expect-pattern multi_domain_change_pattern_observed
echo '[5/8] Deterministic rerun';python scripts/data/run_fatigue_evidence.py --manifest data-platform/synthetic-data/golden_signal_01.manifest.json --json-out qa-validation/evidence/day12-fatigue-evidence-rerun.json --expect-status completed --expect-pattern multi_domain_change_pattern_observed --quiet
echo '[6/8] Abstention';python qa-validation/test-data/synthetic/generate_qc_fixtures.py --source-manifest data-platform/synthetic-data/golden_signal_01.manifest.json --output-dir qa-validation/test-data/synthetic --overwrite >/dev/null;python scripts/data/run_fatigue_evidence.py --manifest qa-validation/test-data/synthetic/qc_fail_flatline.manifest.json --json-out qa-validation/evidence/day12-fatigue-evidence-abstained.json --expect-status abstained --expect-reason EVIDENCE_ABSTAINED_BY_TREND --quiet
echo '[7/8] Validate/register';python scripts/dev/validate_day12_outputs.py;python scripts/dev/register_fatigue_evidence_v0_1.py
echo '[8/8] Artifact';python scripts/dev/check_day12_artifacts.py
echo 'All Day 12 checks passed.'
