#!/usr/bin/env bash
# Build the installable skill zip: SKILL.md + the toolkit (every git-tracked file of this repo, without the old
# reference toolkit). Models and fonts are downloaded by toolkit/setup.sh on first use.
#   bash skill/make_skill.sh [out.zip]      (default: output/style-b-roblox-shorts.skill.zip)
set -e
cd "$(dirname "$0")/.."
OUT="${1:-output/style-b-roblox-shorts.skill.zip}"
TMP="$(mktemp -d)"
D="$TMP/style-b-roblox-shorts"
mkdir -p "$D/toolkit"
cp skill/SKILL.md "$D/SKILL.md"
git ls-files | grep -v '^reference_examples/' | grep -v '^skill/' | while read -r f; do
  mkdir -p "$D/toolkit/$(dirname "$f")"; cp "$f" "$D/toolkit/$f"
done
mkdir -p "$(dirname "$OUT")"
rm -f "$OUT"
(cd "$TMP" && zip -qr - style-b-roblox-shorts) > "$OUT"
rm -rf "$TMP"
echo "wrote $OUT ($(du -h "$OUT" | cut -f1))"
