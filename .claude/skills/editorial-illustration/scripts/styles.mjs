// Loads the sealed style folders (styles/<folder>/style.json, guide.md, examples/) into one
// entry per style key. A folder is one style; the propaganda folder holds one style with four
// treatments, each its own key (propaganda-print, ...). Nothing here mixes two folders: every
// path an entry carries points inside its own folder.
import { readFile, readdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

export const root = fileURLToPath(new URL('..', import.meta.url));
export const norm = (s) => s.replace(/\s+/g, ' ').trim();
const fenced = (md) => [...md.matchAll(/```text\n([\s\S]*?)```/g)].map((m) => norm(m[1]));

export async function loadStyles() {
  const keys = {};
  for (const folder of (await readdir(`${root}styles`)).sort()) {
    const dir = `${root}styles/${folder}/`;
    const s = JSON.parse(await readFile(`${dir}style.json`, 'utf8'));
    const guide = await readFile(`${dir}guide.md`, 'utf8');
    const blocks = fenced(guide);
    const fullBlock = blocks.find((b) => b.startsWith(norm(s.block)));
    // Every word this folder owns, whichever treatment uses it: no other folder may use them.
    const folderWords = [...s.words, ...Object.values(s.treatments || {}).flatMap((t) => t.words)];
    const base = { folder, dir, name: s.name, guide: `styles/${folder}/guide.md`, block: s.block, fullBlock, folderWords };
    if (!s.treatments) {
      keys[folder] = { ...base, key: folder, words: s.words, siblingWords: [], describe: s.describe,
        examples: s.examples.map((e) => `${dir}examples/${e}`) };
      continue;
    }
    for (const [t, tr] of Object.entries(s.treatments)) {
      const siblings = Object.entries(s.treatments).filter(([u]) => u !== t);
      keys[`${folder}-${t}`] = {
        ...base, key: `${folder}-${t}`, treatment: tr.line,
        fullTreatment: blocks.find((b) => b.startsWith(norm(tr.line))),
        words: [...s.words, ...tr.words],
        // Words of the other treatments: the treatments are walled from each other too.
        siblingWords: siblings.flatMap(([, u]) => [...u.words, ...(u.siblingWords || [])]),
        describe: tr.describe,
        examples: tr.examples.map((e) => `${dir}examples/${e}`),
      };
    }
  }
  return keys;
}

// Every word another style owns, for the style `me`, as a map word -> owner key.
export function foreignWords(styles, me, allow = []) {
  const mine = new Set(me.words.map((w) => w.toLowerCase()));
  const out = new Map();
  for (const [k, s] of Object.entries(styles)) {
    if (k === me.key) continue;
    const words = s.folder === me.folder ? [] : s.folderWords;
    for (const w of words) {
      const lw = w.toLowerCase();
      if (!mine.has(lw) && !allow.includes(lw) && !out.has(lw)) out.set(lw, s.folder);
    }
  }
  for (const w of me.siblingWords) {
    const lw = w.toLowerCase();
    if (!mine.has(lw) && !allow.includes(lw) && !out.has(lw)) out.set(lw, `${me.folder} (another treatment)`);
  }
  return out;
}

export function findWords(text, words) {
  const t = text.toLowerCase();
  const found = new Map();
  for (const [w, owner] of words) {
    const re = new RegExp(`(?<![a-z])${w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(?![a-z])`);
    if (re.test(t)) found.set(owner, [...(found.get(owner) || []), w]);
  }
  return found;
}

// Which style a prompt was written for, from the style block (and treatment line) it holds.
export function styleOfPrompt(styles, text) {
  const p = norm(text);
  const hits = Object.values(styles).filter((s) => p.includes(norm(s.block)) && (!s.treatment || p.includes(norm(s.treatment))));
  return hits.map((s) => s.key);
}
