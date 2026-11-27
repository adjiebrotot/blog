// The style judge: does a finished picture stay inside its style, or has another style
// leaked over the wall? A vision model reads every style's description (styles/*/style.json)
// and the picture, names the closest style and lists any feature that belongs to another
// style. generate.sh runs it after every picture; run it alone on any picture with:
//
//   GEMINI_API_KEY=... node judge.mjs <style> <picture>
//
// Exit 0: pass. Exit 3: a leak (the foreign features are printed). Exit 1: the check could
// not run. With only OPENROUTER_API_KEY set it asks OpenRouter instead.
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { loadStyles } from './styles.mjs';

export async function judge(style, picture, { model, styles } = {}) {
  styles = styles || (await loadStyles());
  if (!styles[style]) throw new Error(`unknown style ${style}`);
  const list = Object.values(styles).map((s) => `${s.key}: ${s.describe}.`).join('\n');
  const prompt = `You check whether an illustration stays inside its style, for a blog that keeps these styles strictly apart, each its own unique theme:

${list}

The picture is meant to be "${style}". Look closely at the technique: proportions and expressions, edges and borders, texture, palette, how paint, line or photograph is used. Answer only JSON: {"closest": "<style key>", "foreign": [{"feature": "<what you see>", "belongs_to": "<other style key>"}], "verdict": "pass" or "leak"}.
A feature is foreign only when it is distinctive of another style's technique and not part of "${style}". These are never foreign on their own: a plain background colour, a person or a crowd, the colour red, motion or speed lines on a moving thing, quoted words or a banner where "${style}" allows words, the subject matter itself. The verdict is "leak" when there is any foreign feature or when the closest style is not "${style}".`;
  const bytes = await readFile(picture);
  const mime = { png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', webp: 'image/webp' }[picture.split('.').pop().toLowerCase()];
  const data = bytes.toString('base64');
  const google = !!process.env.GEMINI_API_KEY;
  const key = process.env.GEMINI_API_KEY || process.env.OPENROUTER_API_KEY;
  if (!key) throw new Error('set GEMINI_API_KEY or OPENROUTER_API_KEY');
  let text;
  if (google) {
    const m = model || 'gemini-3.5-flash';
    const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${m}:generateContent`, {
      method: 'POST',
      headers: { 'x-goog-api-key': key, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ role: 'user', parts: [{ text: prompt }, { inline_data: { mime_type: mime, data } }] }],
        generationConfig: { responseMimeType: 'application/json', temperature: 0 },
      }),
    });
    const body = await res.json();
    if (!res.ok) throw new Error(`${res.status}: ${JSON.stringify(body.error ?? body)}`);
    text = body.candidates?.[0]?.content?.parts?.map((p) => p.text).join('') ?? '';
  } else {
    const m = model || 'google/gemini-2.5-flash';
    const res = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: m,
        temperature: 0,
        response_format: { type: 'json_object' },
        messages: [{ role: 'user', content: [{ type: 'text', text: prompt }, { type: 'image_url', image_url: { url: `data:${mime};base64,${data}` } }] }],
      }),
    });
    const body = await res.json();
    if (!res.ok) throw new Error(`${res.status}: ${JSON.stringify(body.error ?? body)}`);
    text = body.choices?.[0]?.message?.content ?? '';
  }
  const result = JSON.parse(text.replace(/^```(json)?|```$/g, '').trim());
  const foreign = (result.foreign || []).filter((f) => f.belongs_to && f.belongs_to !== style);
  return { pass: result.closest === style && foreign.length === 0, closest: result.closest, foreign };
}

export const report = (style, picture, r) => {
  if (r.pass) return `style check: ${picture} stays in ${style}`;
  const lines = [`style check: LEAK in ${picture} (meant to be ${style}, closest to ${r.closest})`];
  for (const f of r.foreign) lines.push(`  - ${f.feature}  [from ${f.belongs_to}]`);
  lines.push('  This picture fails: do not use it. Describe the wanted look in this style\'s own words and generate again.');
  return lines.join('\n');
};

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const [style, picture] = process.argv.slice(2);
  if (!style || !picture) {
    console.error('usage: node judge.mjs <style> <picture>');
    process.exit(1);
  }
  try {
    const r = await judge(style, picture);
    console.log(report(style, picture, r));
    process.exit(r.pass ? 0 : 3);
  } catch (e) {
    console.error(`style check could not run: ${e.message}`);
    process.exit(1);
  }
}
