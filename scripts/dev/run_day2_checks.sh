#!/usr/bin/env bash
set -euo pipefail

python3 scripts/dev/validate_protocol.py

python3 scripts/data/validate_signal_file.py \
  --manifest integrations/devices/generic-csv/sample_file.manifest.json \
  --mode format

python3 scripts/data/validate_signal_file.py \
  --manifest integrations/devices/generic-csv/sample_file.manifest.json \
  --mode protocol \
  --expect-error ACTIVE_DURATION_TOO_SHORT

python3 scripts/dev/check_day2_artifacts.py

echo "All Day 2 checks passed."
