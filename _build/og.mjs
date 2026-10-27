// Draws the social preview cards (1200x630 JPEG) in assets/img/og/: one per post, from its
// title, its first category and its first illustration (an *-ill-*.webp in the body), and
// blog.jpg, the card for the home and category pages (site.default_image).
//   node _build/og.mjs            # from the repository root
// Then point the post at its card in the front matter:
//   image: /assets/img/og/<slug>.jpg
//   image_alt: "..."
// This folder starts with _, so Jekyll does not publish it.
import { createRequire } from 'module';
import fs from 'fs';
import path from 'path';
const require = createRequire(import.meta.url);
let pw;
try { pw = require('playwright'); } catch { pw = createRequire('/opt/node22/lib/node_modules/')('playwright'); }

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const OUT = path.join(ROOT, 'assets/img/og');
const url = f => 'file://' + path.join(ROOT, f);

// The category labels, per language, from _data/categories.yml (one line per language).
const labels = {};
for (const m of fs.readFileSync(path.join(ROOT, '_data/categories.yml'), 'utf8').matchAll(/- key: (\w+)\n\s+en: \{ label: ([^,]+),[^\n]*\n\s+id: \{ label: ([^,]+),/g)) labels[m[1]] = { en: m[2], id: m[3] };

const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const unq = s => s.trim().replace(/^"(.*)"$/, '$1').replace(/^'(.*)'$/, '$1').replace(/\\"/g, '"');

function posts() {
  const list = [];
  for (const lang of ['en', 'id']) {
    const dir = path.join(ROOT, lang, '_posts');
    for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.md'))) {
      const src = fs.readFileSync(path.join(dir, f), 'utf8');
      const fm = src.split(/^---$/m)[1];
      const get = k => (fm.match(new RegExp(`^${k}:(.*)$`, 'm')) || [, ''])[1];
      const tag = (get('tags').match(/\w+/) || ['others'])[0];
      const ill = (src.match(/\/assets\/img\/([\w-]+-ill-[\w-]+\.webp)/) || [])[1];
      list.push({ slug: f.replace(/^\d{4}-\d{2}-\d{2}-/, '').replace(/\.md$/, ''), lang, title: unq(get('title')), eyebrow: (labels[tag] || labels.others)[lang], ill });
    }
  }
  return list;
}

function card({ title, eyebrow, ill, lang }) {
  return `<!DOCTYPE html><html lang="${lang}"><head>
<link rel="stylesheet" href="${url('assets/css/fonts.css')}">
<style>
  html, body { margin: 0; width: 1200px; height: 630px; overflow: hidden; }
  body { background: #F0F4FF; color: #14203A; font-family: 'DM Sans', system-ui, sans-serif; position: relative; }
  .txt { position: absolute; left: 64px; top: 60px; width: ${ill ? 560 : 1000}px; height: 510px; display: flex; flex-direction: column; }
  .eyebrow { font-family: 'Caveat', cursive; font-size: 40px; font-weight: 600; color: #B45309; transform: rotate(-2deg); transform-origin: left center; margin: 0 0 14px; }
  h1 { font-size: ${title.length > 70 ? 46 : title.length > 50 ? 52 : 60}px; line-height: 1.06; letter-spacing: -.03em; margin: 0; font-weight: 800; }
  .brand { margin-top: auto; display: flex; align-items: center; gap: 14px; font-size: 23px; font-weight: 700; }
  .brand img { width: 44px; height: 44px; }
  .brand span { color: #4C5B76; font-weight: 500; }
  .ill { position: absolute; right: 48px; top: 60px; width: 500px; height: 510px; border: 2px solid #14203A; border-radius: 18px; box-shadow: 6px 6px 0 #14203A; overflow: hidden; background: #fff; }
  .ill img { width: 100%; height: 100%; object-fit: cover; display: block; }
</style></head><body>
  <div class="txt">
    <p class="eyebrow">${esc(eyebrow)}</p>
    <h1>${esc(title)}</h1>
    <div class="brand"><img src="${url('assets/img/logo.svg')}" alt="">Adjie Brotot Blog <span>blog.adjiebrotots.com</span></div>
  </div>
  ${ill ? `<div class="ill"><img src="${url('assets/img/' + ill)}"></div>` : ''}
</body></html>`;
}

const browser = await pw.chromium.launch();
const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
fs.mkdirSync(OUT, { recursive: true });
const jobs = posts().map(p => [p.slug, p]);
jobs.push(['blog', { title: 'Money, power systems and life between Perth and Jakarta', eyebrow: 'Adjie Brotot Blog', ill: 'rvo-ill-count-wealth.webp', lang: 'en' }]);
for (const [name, p] of jobs) {
  // Written next to the page as a file, so the fonts and images load from the repository.
  const tmp = path.join(ROOT, '_build', '.card.html');
  fs.writeFileSync(tmp, card(p));
  await page.goto(url('_build/.card.html'), { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: path.join(OUT, name + '.jpg'), type: 'jpeg', quality: 86 });
  fs.unlinkSync(tmp);
  console.log(`assets/img/og/${name}.jpg · ${p.title}`);
}
await browser.close();
