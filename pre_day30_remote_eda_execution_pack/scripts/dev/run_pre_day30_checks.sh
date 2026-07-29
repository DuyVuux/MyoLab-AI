#!/usr/bin/env bash
set -euo pipefail

CONFIG="${1:-data-platform/configs/pre_day30_storage.local.yaml}"
OUT="qa-validation/evidence/pre-day30"
mkdir -p "$OUT"

python scripts/data/check_two_zone_contract.py --config "$CONFIG" --output "$OUT/two-zone-contract-check.json"
python scripts/data/audit_repo_no_raw_data.py \
  --repo-root /home/duyvd9/massive/projects/semg-fatigue/MyoLab-AI \
  --output "$OUT/repo-raw-scan.json"
python -m pytest -q qa-validation/tests/pre_day30

echo "Pre-Day30 tooling checks completed. This does not mean real EDA is complete."
