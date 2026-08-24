#!/usr/bin/env bash
set -euo pipefail
echo "MyoLab-AI One-Command Demo Bootstrap"
if [ -x ".venv/bin/python" ]; then
  PY=".venv/bin/python"
else
  PY="python3"
fi
$PY scripts/dev/finish_phase7r_critical_path.py .
