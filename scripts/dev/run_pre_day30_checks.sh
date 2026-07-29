#!/usr/bin/env bash
set -euo pipefail

CONFIG="${1:-data-platform/configs/pre_day30_storage.local.yaml}"
OUT="qa-validation/evidence/pre-day30"
mkdir -p "$OUT"

echo "===== Pre-Day30 Tooling Checks ====="
echo "[1/4] Two-zone contract check..."
python3 scripts/data/check_two_zone_contract.py --config "$CONFIG" --output "$OUT/two-zone-contract-check.json"

echo "[2/4] Repo raw data scan..."
python3 scripts/data/audit_repo_no_raw_data.py \
  --repo-root /home/duyvd9/massive/projects/semg-fatigue/MyoLab-AI \
  --output "$OUT/repo-raw-scan.json"

echo "[3/4] Day 28/29 regression hook check..."
for script in scripts/dev/run_day28_checks.sh scripts/dev/run_day29_checks.sh; do
  if [[ -f "$script" ]]; then
    echo "  FOUND: $script"
  else
    echo "  WARNING: $script not found (regression hook missing)"
  fi
done

echo "[4/4] Pre-Day30 pytest suite..."
python3 -m pytest -q qa-validation/tests/pre_day30

echo ""
echo "Pre-Day30 tooling checks completed."
echo "NOTE: This does NOT mean real EDA is complete — only tooling is verified."
