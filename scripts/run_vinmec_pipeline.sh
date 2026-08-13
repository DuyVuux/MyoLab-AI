#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
RAW_ROOT="${VINMEC_MOTION_LAB_RAW_ROOT:-$ROOT/data-platform/raw/Vinmec/Motion Lab Example Output csv files}"
BRONZE_OUT_DIR="$ROOT/data-platform/bronze/Vinmec/EMG"
GOLD_PARQUET_PATH="$ROOT/ai-core/metrics/public-feature-summary-v1.1.parquet"
GOLD_SUMMARY_PATH="$ROOT/qa-validation/evidence/site-metric-execution-summary-v1.1.json"

export PYTHONPATH="$ROOT"

# Ensure dependencies
python3 -c "import pandas, scipy, pyarrow" || {
    echo "MISSING_DEPENDENCIES: Install pandas, scipy, and pyarrow" >&2
    exit 3
}

if [[ ! -d "$RAW_ROOT" ]]; then
  echo "RAW_ROOT_NOT_FOUND: $RAW_ROOT" >&2
  exit 4
fi

echo "Running Bronze Ingestion (Raw -> Bronze Parquet)..."
python3 -c "
import sys; from pathlib import Path
sys.path.insert(0, '$ROOT/data-platform')
from adapters.vinmec.noraxon_parser import convert_to_bronze
convert_to_bronze(Path('$RAW_ROOT'), Path('$BRONZE_OUT_DIR'))
"

echo "Running Feature Extraction (Bronze -> Gold Parquet)..."
python3 -c "
import sys; from pathlib import Path
sys.path.insert(0, '$ROOT/ai-core')
from pipelines.emg_feature_extraction import process_bronze_to_gold
process_bronze_to_gold(Path('$BRONZE_OUT_DIR'), Path('$GOLD_PARQUET_PATH'), Path('$GOLD_SUMMARY_PATH'))
"

echo "Pipeline complete. Output written to:"
echo "- Bronze: $BRONZE_OUT_DIR"
echo "- Gold: $GOLD_PARQUET_PATH"
echo "- Report: $GOLD_SUMMARY_PATH"
