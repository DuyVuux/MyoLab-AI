#!/usr/bin/env bash
set -euo pipefail

MODE="${1:---dry-run}"
REPO_ROOT="${REPO_ROOT:-/home/duyvd9/massive/projects/semg-fatigue/MyoLab-AI}"
DATA_ROOT="${DATA_ROOT:-/home/duyvd9/massive/projects/semg-fatigue/myolab-ai-data}"
DEST="$REPO_ROOT/qa-validation/evidence/pre-day30"

if [[ "$MODE" != "--dry-run" && "$MODE" != "--apply" ]]; then
  echo "Usage: $0 [--dry-run|--apply]" >&2
  exit 2
fi

mkdir -p "$DEST"

copy_small() {
  local src="$1" dataset="$2"
  [[ -d "$src" ]] || return 0
  while IFS= read -r -d '' file; do
    rel="${file#$src/}"
    case "$file" in
      *.json|*.yaml|*.yml|*.csv|*.md|*.sha256)
        size=$(stat -c %s "$file")
        if (( size <= 5242880 )); then
          target="$DEST/$dataset/$rel"
          if [[ "$MODE" == "--apply" ]]; then
            mkdir -p "$(dirname "$target")"
            cp -p "$file" "$target"
            echo "COPIED $file -> $target"
          else
            echo "WOULD_COPY $file -> $target"
          fi
        fi
        ;;
    esac
  done < <(find "$src" -type f -print0)
}

copy_small "$DATA_ROOT/external/mendeley-4channel-hand-gesture-v2/evidence/day28" mendeley
copy_small "$DATA_ROOT/external/grabmyo-v1.1.0/evidence/day29" grabmyo
