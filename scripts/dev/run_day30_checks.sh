#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

if [[ -n "${PYTHON_BIN:-}" ]]; then
  :
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python)"
else
  echo "No Python interpreter found" >&2
  exit 127
fi

EVIDENCE_DIR="qa-validation/evidence/day30"
mkdir -p "$EVIDENCE_DIR"
LOG="$EVIDENCE_DIR/day30-check-run.log"
: > "$LOG"

run() {
  echo "+ $*" | tee -a "$LOG"
  "$@" 2>&1 | tee -a "$LOG"
}

run bash scripts/dev/run_day28_checks.sh
run bash scripts/dev/run_day29_checks.sh
run env PYTHONDONTWRITEBYTECODE=1 "$PYTHON_BIN" -m compileall -q -f \
  ai-core/data/day30 scripts/data scripts/dev
run "$PYTHON_BIN" scripts/data/day30_build_input_report.py \
  --output "$EVIDENCE_DIR/day30-pre-day30-input-baseline.json"
run "$PYTHON_BIN" scripts/data/day30_preflight.py \
  --config ai-core/configs/day30_harmonization.research.yaml \
  --report "$EVIDENCE_DIR/day30-pre-day30-input-baseline.json" \
  --output "$EVIDENCE_DIR/day30-preflight.json"
run "$PYTHON_BIN" scripts/data/day30_validate_sampling_policy.py
run "$PYTHON_BIN" scripts/data/day30_validate_channel_policy.py
run "$PYTHON_BIN" scripts/data/day30_build_common_ontology.py \
  --mendeley-labels data-platform/manifests/public-datasets/mendeley-4channel-hand-gesture-v2/label-dictionary.yaml \
  --grabmyo-labels data-platform/manifests/public-datasets/grabmyo-canonical/label-dictionary.yaml \
  --output data-platform/configs/day30/common-ontology.yaml
run "$PYTHON_BIN" scripts/data/day30_build_view_registry.py \
  --ontology data-platform/configs/day30/common-ontology.yaml \
  --output data-platform/configs/day30/dataset-view-registry.yaml
run "$PYTHON_BIN" scripts/data/day30_build_window_index.py \
  --metadata-index qa-validation/fixtures/day30/metadata-index.fixture.csv \
  --output "$EVIDENCE_DIR/day30-window-index.fixture.json" \
  --channel-policy-id mendeley-ch123-primary-v1 \
  --preprocessing-policy-id per-record-channel-mean-v1
run "$PYTHON_BIN" scripts/data/day30_run_harmonization.py \
  --config ai-core/configs/day30_harmonization.research.yaml \
  --report "$EVIDENCE_DIR/day30-pre-day30-input-baseline.json" \
  --evidence-dir "$EVIDENCE_DIR"
run "$PYTHON_BIN" scripts/data/day30_render_harmonization_report.py \
  --run-json "$EVIDENCE_DIR/day30-harmonization-run.json" \
  --output "$EVIDENCE_DIR/day30-harmonization-report.md"
run "$PYTHON_BIN" scripts/dev/day30_tooling_smoke.py
run "$PYTHON_BIN" scripts/dev/stress_test_day30.py \
  --records 2000 \
  --output "$EVIDENCE_DIR/day30-stress-test.json"
run env PYTHONDONTWRITEBYTECODE=1 "$PYTHON_BIN" -m pytest -q \
  -p no:cacheprovider qa-validation/automated-tests/test_day30_*.py
run "$PYTHON_BIN" scripts/dev/check_day30_artifacts.py
run "$PYTHON_BIN" scripts/dev/build_day30_manifest.py

echo "DAY30_CHECKS_PASS" | tee -a "$LOG"
