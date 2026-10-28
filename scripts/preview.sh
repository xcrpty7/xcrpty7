#!/bin/bash
# Render the final frame of every SVG to PNG via QuickLook (macOS) for a visual check.
# Usage: scripts/preview.sh <out_dir> [build_script ...]
set -euo pipefail

OUT="${1:?usage: preview.sh <out_dir> [build_script ...]}"
shift
DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPTS=("$@")
[ ${#SCRIPTS[@]} -eq 0 ] && SCRIPTS=(build_hero.py build_terminal.py build_cards.py build_stack.py)

rm -rf "$OUT" && mkdir -p "$OUT/svg"
for s in "${SCRIPTS[@]}"; do
  STATIC=1 ASSETS_DIR="$OUT/svg" python3 "$DIR/$s"
done
find "$OUT/svg" -name '*.svg' | while read -r f; do
  qlmanage -t -s 1400 -o "$(dirname "$f")" "$f" >/dev/null 2>&1 || echo "qlmanage failed: $f" >&2
done
find "$OUT/svg" -name '*.png' | sort
