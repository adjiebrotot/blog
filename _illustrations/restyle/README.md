# Restyled briefs

The blog's wikiHow illustration briefs (the files one folder up) rewritten for three other
styles of the `editorial-illustration` skill: `<name>--tempo.txt`, `<name>--flat.txt` and
`<name>--collage.txt`, made on 26 November 2026 to try the styles on real posts. They are
candidates, not live pictures: the posts still use the originals until Adjie picks a
version. The generated pictures (WebP, 1456 px wide) are kept outside the repo, in the
review page Adjie picks from (https://claude.ai/artifact/FiKFRNunvxktpoThREwoED, files
`full/<name>--<style>.webp`), so use those rather than regenerating. A picked one becomes the post's picture (WebP in `assets/img/`), and its prompt
moves up a folder as that picture's prompt file.

Regenerate one with:

```sh
sh .claude/skills/editorial-illustration/scripts/generate.sh tempo \
  _illustrations/restyle/<name>--tempo.txt <scratchpad>/<name>--tempo.png
```

(add `--aspect 16:9` for `cbf-ill-two-engineers` and `fx-ill-money-changer`). The
`gsl-ill-podium-id--*` prompts remake the English picture with only the words changed, so
they also need `--ref <the gsl-ill-podium-en picture of that style>`; the
`debt-ill-three-people-id--*` prompts have their own Indonesian cast, as the original did.
