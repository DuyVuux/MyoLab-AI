#!/usr/bin/env bash
set -euo pipefail
: "${MLFLOW_ROOT:=/data/experiments/mlflow}"
mkdir -p "$MLFLOW_ROOT/artifacts"
command -v mlflow >/dev/null 2>&1 || { echo "mlflow is not installed in the active environment" >&2; exit 2; }
exec mlflow server \
  --host 127.0.0.1 \
  --port 5000 \
  --backend-store-uri "sqlite:///$MLFLOW_ROOT/mlflow.db" \
  --default-artifact-root "file://$MLFLOW_ROOT/artifacts"
