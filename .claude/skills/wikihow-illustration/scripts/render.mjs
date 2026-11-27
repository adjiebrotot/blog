// Render an illustration to a WebP for the blog, plus a PNG preview to look at.
//
//   node render.mjs <in.svg|png|jpg|webp> <out.webp> [--width 1456] [--quality 0.88] [--preview <out.png>]
//
// An SVG needs a viewBox; the height follows its aspect ratio. A raster image (one made by
// an image model) is scaled to --width at its own aspect ratio, so this also converts those.
// Uses the Playwright + Chromium that come with the container: Chromium draws the image
// on a canvas and encodes the WebP itself, so nothing else needs installing.
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { createRequire } from 'node:module';

// require() finds the globally installed Playwright; an ESM import would not.
const { chromium } = createRequire(import.meta.url)('playwright');

const args = process.argv.slice(2);
const opt = (name, fallback) => {
  const i = args.indexOf(`--${name}`);
  return i === -1 ? fallback : args.splice(i, 2)[1];
};
const width = Number(opt('width', 1456));
const quality = Number(opt('quality', 0.88));
const preview = opt('preview', null);
const [input, output] = args;
if (!input || !output) {
  console.error('usage: node render.mjs <in.svg|png|jpg|webp> <out.webp> [--width 1456] [--quality 0.88] [--preview <out.png>]');
  process.exit(1);
}

const ext = input.split('.').pop().toLowerCase();
const mime = { svg: 'image/svg+xml', png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', webp: 'image/webp' }[ext];
if (!mime) { console.error(`unsupported input: .${ext}`); process.exit(1); }
const bytes = await readFile(input);
if (ext === 'svg' && !/viewBox="[\d.\s-]+"/.test(bytes.toString('utf8'))) {
  console.error('the SVG needs a viewBox');
  process.exit(1);
}
const src = `data:${mime};base64,${bytes.toString('base64')}`;

const browser = await chromium.launch();
const page = await browser.newPage();
const result = await page.evaluate(async ({ src, width, quality }) => {
  const img = new Image();
  img.src = src;
  await img.decode();
  const height = Math.round(width * img.naturalHeight / img.naturalWidth);
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  canvas.getContext('2d').drawImage(img, 0, 0, width, height);
  return {
    webp: canvas.toDataURL('image/webp', quality),
    png: canvas.toDataURL('image/png'),
    height,
  };
}, { src, width, quality });
await browser.close();

const save = async (path, dataUrl) => {
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, Buffer.from(dataUrl.split(',')[1], 'base64'));
};
await save(output, result.webp);
if (preview) await save(preview, result.png);
console.log(`${output}: ${width}×${result.height}${preview ? `, preview ${preview}` : ''}`);
// Every illustration saved to the blog gets a focus box before it is used (focus-box.md).
if (/assets\/img\/[^/]+-ill-[^/]+\.webp$/.test(output)) {
  const name = output.split('/').pop();
  console.log(`\nMandatory next: its focus box in _data/focus.yml, the subject every crop keeps whole`);
  console.log(`(.claude/skills/wikihow-illustration/references/focus-box.md):`);
  console.log(`  ${(name + ':').padEnd(34)}{ box: [x0, y0, x1, y1], size: [${width}, ${result.height}] }   # the subject`);
  console.log(`then: python3 _build/focus.py --preview <scratchpad>/focus  and  python3 _build/focus.py`);
}
