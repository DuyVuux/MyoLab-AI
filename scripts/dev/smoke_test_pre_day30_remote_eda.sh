#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
TMP="qa-validation/evidence/pre-day30/smoke"
rm -rf "$TMP" && mkdir -p "$TMP"

echo "===== Smoke Test: Pre-Day30 Remote EDA Pipeline ====="

echo "[1/4] Building remote catalog from local fixture..."
python3 scripts/data/build_remote_catalog.py \
  --input qa-validation/fixtures/pre_day30/remote-objects.local.csv \
  --output "$TMP/catalog.json"

echo "[2/4] Selecting bounded sample..."
python3 scripts/data/select_remote_sample.py \
  --catalog "$TMP/catalog.json" \
  --config data-platform/configs/pre_day30_remote_eda.research.yaml \
  --output "$TMP/sample-plan.json"

echo "[3/4] Running streaming signal EDA..."
python3 scripts/data/streaming_signal_eda.py \
  --plan "$TMP/sample-plan.json" \
  --output-dir "$TMP/eda" \
  --mode bounded-sample

echo "[4/4] Running pytest suite..."
python3 -m pytest -q qa-validation/tests/pre_day30

echo ""
echo "===== Smoke test PASS ====="
echo "NOTE: This fixture is synthetic/local and does not prove real dataset EDA."
