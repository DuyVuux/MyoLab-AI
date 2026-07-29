#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-/home/duyvd9/massive/projects/semg-fatigue/MyoLab-AI}"
DATA_ROOT="${DATA_ROOT:-/home/duyvd9/massive/projects/semg-fatigue/myolab-ai-data}"
MODE="${1:---dry-run}"

if [[ "$MODE" != "--dry-run" && "$MODE" != "--apply" ]]; then
  echo "Usage: $0 [--dry-run|--apply]" >&2
  exit 2
fi

paths=(
  "$DATA_ROOT/shared/cache"
  "$DATA_ROOT/shared/temporary"
  "$DATA_ROOT/shared/logs"
)
for dataset in mendeley-4channel-hand-gesture-v2 grabmyo-v1.1.0; do
  base="$DATA_ROOT/external/$dataset"
  paths+=(
    "$base/source-metadata"
    "$base/remote-catalog"
    "$base/cache/blocks"
    "$base/cache/downloads"
    "$base/acquired"
    "$base/extracted"
    "$base/normalized"
    "$base/metadata"
    "$base/splits"
    "$base/derived"
  )
done
paths+=(
  "$DATA_ROOT/external/mendeley-4channel-hand-gesture-v2/evidence/day28"
  "$DATA_ROOT/external/grabmyo-v1.1.0/evidence/day29"
  "$REPO_ROOT/qa-validation/evidence/pre-day30"
)

printf 'REPO_ROOT=%s\nDATA_ROOT=%s\nMODE=%s\n' "$REPO_ROOT" "$DATA_ROOT" "$MODE"

for p in "${paths[@]}"; do
  if [[ "$MODE" == "--apply" ]]; then
    mkdir -p "$p"
    printf 'CREATED/EXISTS %s\n' "$p"
  else
    printf 'WOULD_CREATE %s\n' "$p"
  fi
done

if [[ "$MODE" == "--apply" ]]; then
  cat > "$DATA_ROOT/README_LOCAL_DATA.md" <<EOF
# MyoLab-AI local data plane

This directory is outside Git worktree.
Repository: $REPO_ROOT
Raw/archive/cache must not be copied into repository.
EOF
fi
