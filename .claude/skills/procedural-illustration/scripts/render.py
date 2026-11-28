#!/usr/bin/env python3
"""Render, check, preview and publish a procedural figure.

    python3 .claude/skills/procedural-illustration/scripts/render.py _illustrations/<name>.py --out <scratchpad>/pi
    python3 .claude/skills/procedural-illustration/scripts/render.py _illustrations/<name>.py --publish

--out     writes <name>-<lang>.html (the include), a preview page per language and
          <name>-<lang>-sheet.png: the figure as the blog shows it, dark and light, desktop
          column and 390px phone. Look at the sheet before publishing.
--publish also writes _includes/pi/<name>-<lang>.html and prints the include line to paste.
          Refused while the checklist has an ERROR.
--lang    only these languages (default: the figure's own).
--no-png  skip the screenshots (fast iteration on the checks).

A spec is a Python file that defines FIG (a pi.Figure) or FIGS (a list), or a YAML file
(references/yaml-specs.md). Specs live in _illustrations/ (Jekyll ignores it).
"""
import argparse, importlib.util, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BLOG = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

from pi import check as checks  # noqa: E402
from pi.figure import tr  # noqa: E402


def load(path):
    if path.endswith(('.yml', '.yaml')):
        from pi.yamlspec import load_yaml
        return load_yaml(path)
    spec = importlib.util.spec_from_file_location('spec', path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.dirname(os.path.abspath(path)))
    spec.loader.exec_module(mod)
    figs = getattr(mod, 'FIGS', None) or [getattr(mod, 'FIG')]
    return figs


def preview_page(fig, lang, frag):
    css = os.path.join(BLOG, 'assets', 'css')
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="stylesheet" href="/assets/css/fonts.css"><link rel="stylesheet" href="/assets/css/blog.css">
<style>body{{margin:0;padding:24px;background:var(--bg);color:var(--text)}} .wrap{{max-width:766px;margin:0 auto}}</style>
</head><body><main class="wrap prose">{frag}</main></body></html>'''


def liquid_free(html, lang):
    """Resolve the few Liquid tags an include uses, for the preview only."""
    import re, yaml
    i18n = yaml.safe_load(open(os.path.join(BLOG, '_data', 'i18n.yml'), encoding='utf-8'))
    html = re.sub(r'\{%-? comment -?%\}.*?\{%-? endcomment -?%\}', '', html, flags=re.S)
    return re.sub(r'\{\{\s*site\.data\.i18n\.(\w+)\.(\w+)\s*\}\}',
                  lambda m: str(i18n.get(m.group(1), {}).get(m.group(2), m.group(2))), html)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('spec')
    ap.add_argument('--out')
    ap.add_argument('--publish', action='store_true')
    ap.add_argument('--lang', nargs='*')
    ap.add_argument('--no-png', action='store_true')
    ap.add_argument('--quiet', action='store_true', help='print only ERROR and WARN lines')
    a = ap.parse_args()
    figs = load(a.spec)
    errors = 0
    for fig in figs:
        for lang in (a.lang or fig.langs):
            html = fig.html(lang)
            res = checks.run(fig, lang)
            print(f'\n== {fig.name} [{lang}] ==')
            for lv, item, msg in res:
                if a.quiet and lv in ('OK', 'REVIEW'):
                    continue
                print(f'{lv:6} item {item:2}: {msg}')
            n_err = sum(1 for r in res if r[0] == 'ERROR')
            errors += n_err
            print(f'-- {n_err} ERROR, {sum(1 for r in res if r[0] == "WARN")} WARN')
            if a.out:
                os.makedirs(a.out, exist_ok=True)
                open(os.path.join(a.out, f'{fig.name}-{lang}.html'), 'w', encoding='utf-8').write(html)
                pp = os.path.join(a.out, f'{fig.name}-{lang}-preview.html')
                open(pp, 'w', encoding='utf-8').write(preview_page(fig, lang, liquid_free(html, lang)))
                if not a.no_png:
                    sheet = os.path.join(a.out, f'{fig.name}-{lang}-sheet.png')
                    subprocess.run(['node', os.path.join(HERE, 'preview.mjs'), pp, sheet, BLOG], check=True)
                    print('sheet:', sheet)
            if a.publish:
                if n_err:
                    print(f'NOT published: {n_err} ERROR above')
                    continue
                d = os.path.join(BLOG, '_includes', 'pi')
                os.makedirs(d, exist_ok=True)
                open(os.path.join(d, f'{fig.name}-{lang}.html'), 'w', encoding='utf-8').write(html)
                print(f'published _includes/pi/{fig.name}-{lang}.html; in the {lang} post:')
                print(f'  {{% include pi/{fig.name}-{lang}.html %}}')
    sys.exit(1 if errors and a.publish else 0)


if __name__ == '__main__':
    main()
