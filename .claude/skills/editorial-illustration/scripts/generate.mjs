// Generate an illustration with an image model and save it as a PNG. Usually called through
// generate.sh, which attaches the chosen style's example pictures. Two providers:
//
//   Google Gemini API, directly:
//   GEMINI_API_KEY=... node generate.mjs <prompt.txt> <out.png>
//     [--model gemini-nano-banana-2.1] [--aspect 4:3] [--ref <image>]...
//
//   OpenRouter:
//   OPENROUTER_API_KEY=sk-or-... node generate.mjs <prompt.txt> <out.png> --provider openrouter
//     [--model google/gemini-nano-banana-2.1] [--aspect 4:3] [--ref <image>]...
//
// --provider auto (the default) uses OpenRouter when OPENROUTER_API_KEY is set, else Google
// when GEMINI_API_KEY is set. The default model is Nano Banana 2.1 on both; a "google/"
// prefix on a Google model id is dropped, and added for OpenRouter when missing.
//
// <prompt.txt> holds the full prompt (opening line, scene, the style block from the style's
// guide in references/, the text rule). --ref attaches a picture (repeatable): the style's
// examples, a post's earlier picture to keep a character, or a photograph to draw on.
// Then convert the PNG with render.mjs.
import { readFile, writeFile } from 'node:fs/promises';

const args = process.argv.slice(2);
const opt = (name, fallback) => {
  const i = args.indexOf(`--${name}`);
  return i === -1 ? fallback : args.splice(i, 2)[1];
};
const refs = [];
for (let i = args.indexOf('--ref'); i !== -1; i = args.indexOf('--ref')) refs.push(args.splice(i, 2)[1]);
let provider = opt('provider', 'auto');
if (provider === 'auto') {
  provider = !process.env.OPENROUTER_API_KEY && process.env.GEMINI_API_KEY ? 'google' : 'openrouter';
}
const google = provider === 'google';
let model = opt('model', 'gemini-nano-banana-2.1');
model = google ? model.replace(/^google\//, '') : model.includes('/') ? model : `google/${model}`;
const aspect = opt('aspect', '4:3');
const [promptFile, output] = args;
const keyName = google ? 'GEMINI_API_KEY' : 'OPENROUTER_API_KEY';
const key = process.env[keyName];
if (!promptFile || !output || !['google', 'openrouter'].includes(provider)) {
  console.error('usage: node generate.mjs <prompt.txt> <out.png> [--provider auto|openrouter|google] [--model <id>] [--aspect 4:3] [--ref <image>]...');
  process.exit(1);
}
if (!key) {
  console.error(`set ${keyName} (ask Adjie for a key; never write it into a file in the repo)`);
  process.exit(1);
}

const mimes = { png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', webp: 'image/webp' };
const text = await readFile(promptFile, 'utf8');
const images = [];
for (const ref of refs) {
  images.push({ mime: mimes[ref.split('.').pop().toLowerCase()], data: (await readFile(ref)).toString('base64') });
}

const viaOpenRouter = () => fetch('https://openrouter.ai/api/v1/chat/completions', {
  method: 'POST',
  headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
  body: JSON.stringify({
    model,
    messages: [{
      role: 'user',
      content: [
        { type: 'text', text },
        ...images.map(({ mime, data }) => ({ type: 'image_url', image_url: { url: `data:${mime};base64,${data}` } })),
      ],
    }],
    modalities: ['image', 'text'],
    image_config: { aspect_ratio: aspect },
  }),
});
const viaGoogle = () => fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`, {
  method: 'POST',
  headers: { 'x-goog-api-key': key, 'Content-Type': 'application/json' },
  body: JSON.stringify({
    contents: [{
      role: 'user',
      parts: [{ text }, ...images.map(({ mime, data }) => ({ inline_data: { mime_type: mime, data } }))],
    }],
    generationConfig: { responseModalities: ['IMAGE', 'TEXT'], imageConfig: { aspectRatio: aspect } },
  }),
});
const request = google ? viaGoogle : viaOpenRouter;

// A 429 (too many requests at once) or a 502/503 (the model's provider is busy) clears after
// a few seconds: wait and try again.
const busy = (status) => [429, 502, 503].includes(status);
let res = await request();
for (let tries = 1; busy(res.status) && tries <= 3; tries++) {
  const wait = Number(res.headers.get('retry-after')) || 10;
  console.error(`${res.status}, retrying in ${wait}s`);
  await new Promise((r) => setTimeout(r, wait * 1000));
  res = await request();
}
const body = await res.json();
if (!res.ok) {
  console.error(`${res.status}: ${JSON.stringify(body.error ?? body)}`);
  if (/spend(ing)? cap/i.test(JSON.stringify(body))) {
    console.error('The Google project is at its monthly spend cap (set in AI Studio, separate from its credit). '
      + '"Rate-limited to prevent exceeding" lifts in a minute or two; "has exceeded" does not: ask Adjie to raise the cap.');
  }
  process.exit(1);
}

let b64;
let said;
if (google) {
  const parts = body.candidates?.[0]?.content?.parts ?? [];
  const img = parts.map((p) => p.inlineData ?? p.inline_data).find((d) => d?.data);
  b64 = img?.data;
  said = parts.map((p) => p.text).filter(Boolean).join(' ') || body.candidates?.[0]?.finishReason;
} else {
  const message = body.choices?.[0]?.message;
  b64 = message?.images?.[0]?.image_url?.url?.split(',')[1];
  said = message?.content;
}
if (!b64) {
  console.error(`no image in the reply: ${said ?? JSON.stringify(body).slice(0, 500)}`);
  process.exit(1);
}
await writeFile(output, Buffer.from(b64, 'base64'));
const cost = body.usage?.cost;
console.log(`${output}: ${provider} ${model}${cost != null ? `, $${cost.toFixed(4)}` : ''}`);
