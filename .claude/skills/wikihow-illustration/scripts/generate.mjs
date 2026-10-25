// Generate an illustration with an image model on OpenRouter and save it as a PNG.
//
//   OPENROUTER_API_KEY=sk-or-... node generate.mjs <prompt.txt> <out.png>
//     [--model google/gemini-nano-banana-2.1] [--aspect 4:3] [--ref <image>]...
//
// <prompt.txt> holds the full prompt (scene + the style block from references/image-prompt.md).
// --ref attaches an earlier picture from this blog as a style reference (repeatable), so a
// post's pictures match each other. Then convert the PNG with render.mjs.
import { readFile, writeFile } from 'node:fs/promises';

const args = process.argv.slice(2);
const opt = (name, fallback) => {
  const i = args.indexOf(`--${name}`);
  return i === -1 ? fallback : args.splice(i, 2)[1];
};
const refs = [];
for (let i = args.indexOf('--ref'); i !== -1; i = args.indexOf('--ref')) refs.push(args.splice(i, 2)[1]);
const model = opt('model', 'google/gemini-nano-banana-2.1');
const aspect = opt('aspect', '4:3');
const [promptFile, output] = args;
const key = process.env.OPENROUTER_API_KEY;
if (!promptFile || !output) {
  console.error('usage: node generate.mjs <prompt.txt> <out.png> [--model <id>] [--aspect 4:3] [--ref <image>]...');
  process.exit(1);
}
if (!key) {
  console.error('set OPENROUTER_API_KEY (ask Adjie for a key; never write it into a file in the repo)');
  process.exit(1);
}

const mimes = { png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', webp: 'image/webp' };
const content = [{ type: 'text', text: await readFile(promptFile, 'utf8') }];
for (const ref of refs) {
  const mime = mimes[ref.split('.').pop().toLowerCase()];
  const data = (await readFile(ref)).toString('base64');
  content.push({ type: 'image_url', image_url: { url: `data:${mime};base64,${data}` } });
}

const request = () => fetch('https://openrouter.ai/api/v1/chat/completions', {
  method: 'POST',
  headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
  body: JSON.stringify({
    model,
    messages: [{ role: 'user', content }],
    modalities: ['image', 'text'],
    image_config: { aspect_ratio: aspect },
  }),
});
// A 429 (too many requests at once) clears after a few seconds: wait and try again.
let res = await request();
for (let tries = 1; res.status === 429 && tries <= 3; tries++) {
  const wait = Number(res.headers.get('retry-after')) || 10;
  console.error(`429, retrying in ${wait}s`);
  await new Promise((r) => setTimeout(r, wait * 1000));
  res = await request();
}
const body = await res.json();
if (!res.ok) {
  console.error(`${res.status}: ${JSON.stringify(body.error ?? body)}`);
  process.exit(1);
}
const message = body.choices?.[0]?.message;
const url = message?.images?.[0]?.image_url?.url;
if (!url) {
  console.error(`no image in the reply: ${message?.content ?? JSON.stringify(body).slice(0, 500)}`);
  process.exit(1);
}
await writeFile(output, Buffer.from(url.split(',')[1], 'base64'));
const cost = body.usage?.cost;
console.log(`${output}: ${model}${cost != null ? `, $${cost.toFixed(4)}` : ''}`);
