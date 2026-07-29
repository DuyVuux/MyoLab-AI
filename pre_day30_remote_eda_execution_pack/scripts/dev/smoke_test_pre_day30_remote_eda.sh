#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
TMP="qa-validation/evidence/pre-day30/smoke"
rm -rf "$TMP" && mkdir -p "$TMP"

python scripts/data/build_remote_catalog.py \
  --input qa-validation/fixtures/pre_day30/remote-objects.local.csv \
  --output "$TMP/catalog.json"

python scripts/data/select_remote_sample.py \
  --catalog "$TMP/catalog.json" \
  --config data-platform/configs/pre_day30_remote_eda.research.yaml \
  --output "$TMP/sample-plan.json"

python scripts/data/streaming_signal_eda.py \
  --plan "$TMP/sample-plan.json" \
  --output-dir "$TMP/eda" \
  --mode bounded-sample

python -m pytest -q qa-validation/tests/pre_day30

echo "Smoke test PASS. This fixture is synthetic/local and does not prove real dataset EDA."
