#!/usr/bin/env bash
set -euo pipefail

HOST="${MLFLOW_HOST:-127.0.0.1}"
PORT="${MLFLOW_PORT:-5000}"
BACKEND="${MLFLOW_BACKEND_STORE_URI:-sqlite:////data/experiments/mlflow/mlflow.db}"
ARTIFACTS="${MLFLOW_ARTIFACT_ROOT:-file:///data/experiments/mlflow/artifacts}"

if [[ "$HOST" != "127.0.0.1" && "$HOST" != "localhost" ]]; then
  echo "Refusing non-loopback bind without an approved authentication/TLS deployment." >&2
  exit 2
fi

mkdir -p /data/experiments/mlflow/artifacts /data/experiments/mlflow

exec mlflow server \
  --host "$HOST" \
  --port "$PORT" \
  --backend-store-uri "$BACKEND" \
  --default-artifact-root "$ARTIFACTS"
