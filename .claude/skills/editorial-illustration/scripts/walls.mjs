// The wall check: run it after adding or changing any style. Every wall must hold.
//
//   node walls.mjs              # the free checks, then every example through the judge
//   node walls.mjs --no-judge   # the free checks only
//
// 1. Each folder's style.json lists exactly the pictures in its examples/, and each style
//    block and treatment line is in its guide.
// 2. No word is owned by two folders.
// 3. No style block or treatment line uses a word another folder owns (a block describes
//    its own style in its own words; it never names a neighbour's features, even to forbid
//    them, since naming a feature plants it).
// 4. Every example passes the judge as its own style: the walls still separate them.
// Exit 1 on any breach.
import { readdir } from 'node:fs/promises';
import { judge } from './judge.mjs';
import { findWords, foreignWords, loadStyles, root } from './styles.mjs';

const noJudge = process.argv.includes('--no-judge');
const styles = await loadStyles();
const breaches = [];

const byFolder = {};
for (const s of Object.values(styles)) (byFolder[s.folder] ||= []).push(s);
for (const [folder, keys] of Object.entries(byFolder)) {
  const listed = new Set(keys.flatMap((s) => s.examples.map((e) => e.split('/').pop())));
  const present = (await readdir(`${root}styles/${folder}/examples`)).filter((f) => !f.startsWith('.'));
  for (const f of present) if (!listed.has(f)) breaches.push(`${folder}: examples/${f} is not listed in style.json`);
  for (const f of listed) if (!present.includes(f)) breaches.push(`${folder}: style.json lists ${f}, which is missing`);
  for (const s of keys) {
    if (!s.fullBlock) breaches.push(`${s.key}: its style block is not in ${s.guide}`);
    if (s.treatment && !s.fullTreatment) breaches.push(`${s.key}: its treatment line is not in ${s.guide}`);
  }
}

const owner = new Map();
for (const [folder, keys] of Object.entries(byFolder)) {
  for (const w of new Set(keys[0].folderWords.map((x) => x.toLowerCase()))) {
    if (owner.has(w) && owner.get(w) !== folder) breaches.push(`"${w}" is owned by both ${owner.get(w)} and ${folder}`);
    owner.set(w, folder);
  }
}

for (const s of Object.values(styles)) {
  const text = [s.fullBlock, s.fullTreatment].filter(Boolean).join(' ');
  const outside = new Map([...foreignWords(styles, s)].filter(([, o]) => !o.startsWith(s.folder)));
  for (const [o, ws] of findWords(text, outside)) breaches.push(`${s.key}: its block names ${ws.map((w) => `"${w}"`).join(', ')}, owned by ${o}`);
}

console.log(`free checks: ${breaches.length ? `${breaches.length} breach(es)` : 'every wall holds'}`);
if (!noJudge) {
  for (const s of Object.values(styles)) {
    for (const e of s.examples) {
      const r = await judge(s.key, e, { styles });
      const name = e.split('/styles/')[1];
      console.log(`  ${r.pass ? 'pass' : 'LEAK'}  ${name}${r.pass ? '' : `: closest ${r.closest}; ${r.foreign.map((f) => `${f.feature} [${f.belongs_to}]`).join('; ')}`}`);
      if (!r.pass) breaches.push(`${name} does not pass as ${s.key}`);
    }
  }
}
for (const b of breaches) console.error(`breach: ${b}`);
console.log(breaches.length ? `${breaches.length} breach(es): fix them before using any style` : 'the great wall holds');
process.exit(breaches.length ? 1 : 0);
