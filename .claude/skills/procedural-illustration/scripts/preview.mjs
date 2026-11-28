// Screenshot a figure preview the way the blog shows it: dark and light, a desktop column
// and a 390px phone, stitched into one sheet. Files under /assets/ are served from the blog.
//   node preview.mjs <preview.html> <sheet.png> <blog root>
import { createRequire } from 'module';
import fs from 'fs';
import path from 'path';
const require = createRequire(import.meta.url);
let pw;
try { pw = require('playwright'); } catch { pw = createRequire('/opt/node22/lib/node_modules/')('playwright'); }
const [page, out, root] = process.argv.slice(2);
const html = fs.readFileSync(page, 'utf8');
const TYPES = { '.css': 'text/css', '.svg': 'image/svg+xml', '.woff2': 'font/woff2', '.png': 'image/png', '.webp': 'image/webp' };
const b = await pw.chromium.launch();
const shots = [];
for (const [w, label] of [[814, 'desktop'], [390, 'phone']]) {
  for (const theme of ['dark', 'light']) {
    const p = await b.newPage({ viewport: { width: w, height: 800 }, deviceScaleFactor: 2 });
    await p.route('**/*', r => {
      const u = new URL(r.request().url());
      if (u.pathname === '/preview.html') return r.fulfill({ body: html.replace('<html ', theme === 'light' ? '<html class="light" ' : '<html '), contentType: 'text/html' });
      const f = path.join(root, decodeURIComponent(u.pathname));
      if (fs.existsSync(f)) return r.fulfill({ body: fs.readFileSync(f), contentType: TYPES[path.extname(f)] || 'application/octet-stream' });
      return r.fulfill({ status: 404, body: '' });
    });
    await p.goto('http://pi.local/preview.html');
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(150);
    const fig = await p.$('figure');
    const file = out.replace(/\.png$/, `-${label}-${theme}.png`);
    await fig.screenshot({ path: file });
    shots.push(file);
    await p.close();
  }
}
// stitch: desktop dark | desktop light on top, phone dark | phone light below
const sp = await b.newPage({ viewport: { width: 1700, height: 1000 }, deviceScaleFactor: 1 });
const imgs = shots.map(f => 'data:image/png;base64,' + fs.readFileSync(f).toString('base64'));
await sp.setContent(`<body style="margin:0;background:#888;display:grid;grid-template-columns:auto auto;gap:12px;padding:12px;width:max-content;align-items:start">
${imgs.map(s => `<img src="${s}" style="width:${s === imgs[2] || s === imgs[3] ? 390 : 814}px">`).join('')}</body>`);
await sp.waitForTimeout(100);
const body = await sp.$('body');
await body.screenshot({ path: out });
await b.close();
