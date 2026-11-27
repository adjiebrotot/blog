#!/bin/sh
# Generate an illustration in one style, kept apart from the others. A thin wrapper over
# illustrate.mjs, which checks the prompt, generates with only this style's examples
# (generate.mjs: keys, providers, retries) and judges the picture (judge.mjs).
#
#   GEMINI_API_KEY=... sh generate.sh <style> <prompt.txt> <out.png> [options]
#   OPENROUTER_API_KEY=... sh generate.sh <style> <prompt.txt> <out.png> [options]
#
# <style>: wikihow, tempo, flat, collage, hybrid (live-action hybrid), or the propaganda
# poster in one of its four treatments: propaganda-print, propaganda-painted, propaganda-jet
# or propaganda-montage. Each style is a sealed folder: styles/<style>/ (guide.md,
# style.json, examples/). The walls between them: SKILL.md, "The great wall".
#
# Options: --aspect 4:3 (default), 16:9 or 3:4; --model <id> (default: Nano Banana 2.1);
# --provider google|openrouter; --ref <image> (goes BEFORE the style's examples, so a post's
# first picture can set its character, or a photograph can be the one the hybrid style
# draws on); --allow <word>; --lint-only; --no-judge.
#
# Exit 0: clean picture. 1: usage or API failure. 2: the prompt failed its check (nothing
# was generated). 3: the picture leaks another style (kept, so you can look at it).
here=$(cd "$(dirname "$0")" && pwd)
exec node "$here/illustrate.mjs" "$@"
