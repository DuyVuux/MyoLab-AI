#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$ROOT"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONPATH="$ROOT/packages/semg-core:$ROOT/services/signal-ingestion-service/src:$ROOT/services/quality-gate-service/src:$ROOT/services/preprocessing-service/src:$ROOT/services/feature-extraction-service/src${PYTHONPATH:+:$PYTHONPATH}"
if [[ "${DAY11_FULL_REGRESSION:-0}" == "1" ]]; then echo '[1/8] Full regression Day 10'; bash scripts/dev/run_day10_checks.sh; else echo '[1/8] Bỏ qua full regression Day 10'; fi
echo '[2/8] Tests'; pytest -q packages/semg-core/tests/test_trend.py services/feature-extraction-service/tests/test_trend_feature_config.py
echo '[3/8] Known-answer trend'; python scripts/data/verify_trend_features.py
echo '[4/8] Golden E2E'; python scripts/data/run_trend_features.py --manifest data-platform/synthetic-data/golden_signal_01.manifest.json --json-out qa-validation/evidence/day11-trends.json --csv-out qa-validation/evidence/day11-trends.csv --expect-status completed --expect-computed-channel-count 1
echo '[5/8] Deterministic rerun'; python scripts/data/run_trend_features.py --manifest data-platform/synthetic-data/golden_signal_01.manifest.json --json-out qa-validation/evidence/day11-trends-rerun.json --expect-status completed --expect-computed-channel-count 1 --quiet
echo '[6/8] Upstream block'; python qa-validation/test-data/synthetic/generate_qc_fixtures.py --source-manifest data-platform/synthetic-data/golden_signal_01.manifest.json --output-dir qa-validation/test-data/synthetic --overwrite >/dev/null; python scripts/data/run_trend_features.py --manifest qa-validation/test-data/synthetic/qc_fail_flatline.manifest.json --json-out qa-validation/evidence/day11-trends-blocked.json --expect-status blocked --expect-computed-channel-count 0 --expect-reason TREND_BLOCKED_BY_UPSTREAM --quiet
echo '[7/8] Validate/register'; python scripts/dev/validate_day11_outputs.py; python scripts/dev/register_trend_features_v0_1.py
echo '[8/8] Artifact'; python scripts/dev/check_day11_artifacts.py
echo 'All Day 11 checks passed.'
