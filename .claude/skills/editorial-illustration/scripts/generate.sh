#!/bin/sh
# Generate an editorial illustration in one of the three styles, with that style's three
# example pictures attached as references. A thin wrapper over the wikiHow skill's
# generate.mjs (same keys, providers and retries).
#
#   GEMINI_API_KEY=... sh generate.sh <tempo|flat|collage> <prompt.txt> <out.png> [options]
#   OPENROUTER_API_KEY=... sh generate.sh <tempo|flat|collage> <prompt.txt> <out.png> [options]
#
# Options pass straight to generate.mjs: --aspect 4:3 (default) or 16:9, --model <id>
# (default here: Nano Banana 2.1), --provider google|openrouter, --ref <image>. A --ref you
# give goes BEFORE the style examples, so a post's first picture can set its character.
set -e
here=$(cd "$(dirname "$0")" && pwd)
style=$1; prompt=$2; out=$3
if [ -z "$out" ]; then
  echo "usage: sh generate.sh <tempo|flat|collage> <prompt.txt> <out.png> [--aspect 4:3] [--model <id>] [--ref <image>]..." >&2
  exit 1
fi
shift 3
ex=$here/../examples
case $style in
  tempo) refs="$ex/tempo-above.webp $ex/tempo-closeup.webp $ex/tempo-two.webp" ;;
  flat) refs="$ex/flat-hat.webp $ex/flat-drink.webp $ex/flat-split.webp" ;;
  collage) refs="$ex/collage-train.webp $ex/collage-portrait.webp $ex/collage-bomber.webp" ;;
  *) echo "style must be tempo, flat or collage" >&2; exit 1 ;;
esac
case " $* " in
  *" --model "*) ;;
  *) set -- "$@" --model google/gemini-nano-banana-2.1 ;;
esac
for r in $refs; do set -- "$@" --ref "$r"; done
exec node "$here/../../wikihow-illustration/scripts/generate.mjs" "$prompt" "$out" "$@"
