#!/bin/sh
# Generate an illustration in one of the six styles, with that style's example pictures
# attached as references. A thin wrapper over generate.mjs (keys, providers, retries).
#
#   GEMINI_API_KEY=... sh generate.sh <style> <prompt.txt> <out.png> [options]
#   OPENROUTER_API_KEY=... sh generate.sh <style> <prompt.txt> <out.png> [options]
#
# <style>: wikihow, tempo, flat, collage, hybrid (live-action hybrid), or the propaganda
# poster in one of its four treatments: propaganda-print, propaganda-painted, propaganda-jet
# or propaganda-montage (each attaches only its own two examples).
# Options pass straight to generate.mjs: --aspect 4:3 (default), 16:9 or 3:4, --model <id>
# (default: Nano Banana 2.1), --provider google|openrouter, --ref <image>. A --ref you give
# goes BEFORE the style examples, so a post's first picture can set its character, or a
# photograph can be the one the hybrid style draws on.
set -e
here=$(cd "$(dirname "$0")" && pwd)
style=$1; prompt=$2; out=$3
styles="wikihow, tempo, flat, collage, hybrid or propaganda-print|painted|jet|montage"
if [ -z "$out" ]; then
  echo "usage: sh generate.sh <$styles> <prompt.txt> <out.png> [--aspect 4:3] [--model <id>] [--ref <image>]..." >&2
  exit 1
fi
shift 3
ex=$here/../examples
case $style in
  wikihow) refs="$ex/wikihow-midshot.webp $ex/wikihow-indonesia.webp $ex/wikihow-split.webp $ex/wikihow-back.webp" ;;
  tempo) refs="$ex/tempo-above.webp $ex/tempo-closeup.webp $ex/tempo-two.webp" ;;
  flat) refs="$ex/flat-hat.webp $ex/flat-drink.webp $ex/flat-split.webp" ;;
  collage) refs="$ex/collage-train.webp $ex/collage-portrait.webp $ex/collage-bomber.webp" ;;
  hybrid) refs="$ex/hybrid-street.webp $ex/hybrid-warung.webp $ex/hybrid-riverside.webp" ;;
  propaganda-print) refs="$ex/propaganda-print-saver.webp $ex/propaganda-print-beam.webp" ;;
  propaganda-painted) refs="$ex/propaganda-painted-refuse.webp $ex/propaganda-painted-flypast.webp" ;;
  propaganda-jet) refs="$ex/propaganda-jet-train.webp $ex/propaganda-jet-airport.webp" ;;
  propaganda-montage) refs="$ex/propaganda-montage-trucks.webp $ex/propaganda-montage-future.webp" ;;
  propaganda) echo "pick a treatment: propaganda-print, propaganda-painted, propaganda-jet or propaganda-montage (references/propaganda.md)" >&2; exit 1 ;;
  *) echo "style must be $styles" >&2; exit 1 ;;
esac
for r in $refs; do
  [ -f "$r" ] || { echo "missing example $r: make this style's examples first (its guide in references/)" >&2; exit 1; }
  set -- "$@" --ref "$r"
done
exec node "$here/generate.mjs" "$prompt" "$out" "$@"
