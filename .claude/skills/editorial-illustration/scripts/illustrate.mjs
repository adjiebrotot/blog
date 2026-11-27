// What generate.sh runs: one illustration in one style, behind the great wall (SKILL.md).
//
//   node illustrate.mjs <style> <prompt.txt> <out.png> [options]
//
// 1. Prompt wall (no API call, no cost). The prompt holds the start of its own style block
//    (and, for a style with treatments, its treatment line); no other style's block or line;
//    and, outside its own block, none of the words another style owns (styles/*/style.json).
// 2. Reference wall. A --ref may not come from another style's folder, nor be a post picture
//    whose prompt in _illustrations/ was written for another style.
// 3. Generate with generate.mjs, attaching only this style's own examples, after any --ref.
// 4. Picture wall. judge.mjs checks the picture stays in this style.
//
// Exit 0: a clean picture. 1: usage or API failure. 2: a wall refused the prompt or a
// reference (nothing was generated). 3: the picture leaks another style (kept to look at,
// never to use).
//
// Options: --allow <word> (repeatable) lets one owned word through, only where Adjie wants
// a picture to borrow it on purpose; --lint-only stops after the walls of steps 1 and 2;
// --no-judge skips step 4. Everything else (--aspect, --model, --provider, --ref) goes to
// generate.mjs.
import { existsSync } from 'node:fs';
import { readFile } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import { basename, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { judge, report } from './judge.mjs';
import { findWords, foreignWords, loadStyles, norm, root, styleOfPrompt } from './styles.mjs';

const here = fileURLToPath(new URL('.', import.meta.url));
const args = process.argv.slice(2);
const take = (name) => {
  const out = [];
  for (let i = args.indexOf(name); i !== -1; i = args.indexOf(name)) out.push(args.splice(i, 2)[1]);
  return out;
};
const flag = (name) => {
  const i = args.indexOf(name);
  if (i !== -1) args.splice(i, 1);
  return i !== -1;
};
const allow = take('--allow').map((w) => w.toLowerCase());
const refs = take('--ref');
const lintOnly = flag('--lint-only');
const noJudge = flag('--no-judge');
const [style, promptFile, out, ...rest] = args;

const styles = await loadStyles();
const usage = `usage: sh generate.sh <${Object.keys(styles).join('|')}> <prompt.txt> <out.png> [--aspect 4:3] [--ref <image>]... [--allow <word>]... [--lint-only] [--no-judge]`;
if (!styles[style] || !promptFile || (!out && !lintOnly)) {
  console.error(styles[style] || !style ? usage : `unknown style "${style}". ${usage}`);
  process.exit(1);
}
const me = styles[style];
const prompt = norm(await readFile(promptFile, 'utf8'));
const problems = [];

// 1. Prompt wall.
if (!prompt.includes(norm(me.block))) {
  problems.push(`it lacks this style's block: paste the style block from ${me.guide} word for word ("${me.block.slice(0, 60)}...")`);
}
if (me.treatment && !prompt.includes(norm(me.treatment))) {
  problems.push(`it lacks the treatment line: paste "${me.treatment}..." from ${me.guide} word for word`);
}
for (const s of Object.values(styles)) {
  if (s.key === style) continue;
  if (s.block !== me.block && prompt.includes(norm(s.block))) problems.push(`it contains the style block of "${s.folder}"`);
  if (s.treatment && prompt.includes(norm(s.treatment))) problems.push(`it contains the treatment line of "${s.key}"`);
}
let scan = prompt;
for (const own of [me.fullBlock, me.fullTreatment]) if (own) scan = scan.split(own).join(' ');
for (const [owner, ws] of findWords(scan, foreignWords(styles, me, allow))) {
  problems.push(`${ws.map((w) => `"${w}"`).join(', ')} belong${ws.length === 1 ? 's' : ''} to ${owner}: say it in this style's own words (${me.guide}); --allow <word> only where Adjie wants the borrowing`);
}

// 2. Reference wall.
for (const r of refs) {
  const abs = resolve(r);
  const styleDir = resolve(root, 'styles');
  if (abs.startsWith(styleDir + '/') && !abs.startsWith(resolve(me.dir) + '/')) {
    problems.push(`--ref ${r} is another style's example: a picture may only lean on its own style`);
    continue;
  }
  const name = basename(abs).replace(/\.(webp|png|jpe?g)$/i, '');
  const promptOfRef = resolve(dirname(abs), '../../_illustrations', `${name}.txt`);
  if (existsSync(promptOfRef)) {
    const was = styleOfPrompt(styles, await readFile(promptOfRef, 'utf8'));
    if (was.length && !was.includes(style)) problems.push(`--ref ${r} was made in "${was.join(', ')}": a character reference must be a picture of the same style`);
  }
}

if (problems.length) {
  console.error(`great wall: ${promptFile} cannot be used for ${style}:`);
  for (const p of problems) console.error(`  - ${p}`);
  process.exit(2);
}
console.log(`great wall: ${promptFile} is clean for ${style}`);
if (lintOnly) process.exit(0);

// 3. Generate, with only this style's examples after the --ref pictures.
const refArgs = [...refs, ...me.examples].flatMap((r) => ['--ref', r]);
const gen = spawnSync(process.execPath, [`${here}generate.mjs`, promptFile, out, ...rest, ...refArgs], { stdio: 'inherit' });
if (gen.status !== 0) process.exit(gen.status ?? 1);

// 4. Picture wall.
if (noJudge) {
  console.log('style check skipped (--no-judge): run node scripts/judge.mjs before using the picture');
  process.exit(0);
}
try {
  const r = await judge(style, out, { styles });
  console.log(report(style, out, r));
  process.exit(r.pass ? 0 : 3);
} catch (e) {
  console.error(`picture saved, but the style check could not run (${e.message}): run node ${here}judge.mjs ${style} ${out} before using it`);
  process.exit(1);
}
