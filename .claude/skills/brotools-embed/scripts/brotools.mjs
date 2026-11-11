#!/usr/bin/env node
// Adjie Brotools from the blog: open a tool on the LIVE site (tool.adjiebrotots.com) on a
// scenario, read what it computed, and write the chart's "Embed as HTML" code, its figures
// and pictures of the embed as the blog will show it. The tool repo is never needed: the
// code comes from the tool's own Share menu (SharedShare.embedCode in shared.js), so it is
// byte for byte what a reader would copy from Share -> Embed as HTML.
//
//   node brotools.mjs charts <tool url>                      what the page offers
//   node brotools.mjs embed  <tool url> [options]            code, figures, screenshots
//   node brotools.mjs shot   <url> [--width 390] [--theme dark] [--out file.png]
//
// <tool url> is a tool page, usually with an AI link's scenario on it:
//   https://tool.adjiebrotots.com/financingvscash/#load&v=1&qs=...&price=12000
//
// embed options:
//   --chart KEY        the chart's key (from `charts`); default the first chart shown
//   --view TEXT        set a view in the chart's card first (a select option or a button
//                      whose words contain TEXT); repeat for several controls
//   --include VALUE    tick an "Include:" option of the embed dialog; repeat
//   --name NAME        folder name under the output root (default <tool>-<chart>)
//   --out DIR          output root (default _build/brotools in the blog)
//   --wait SECONDS     longest wait for the tool to finish computing (default 45)
//   --light            take the embed while the tool is in light theme (default dark)
//
// Output, in <out>/<name>/:
//   embed.html   the code to paste into the post (iframe, credit line, sizing script)
//   link.txt     the link back: the whole tool, opened on this scenario and view
//   inputs.md    what the #load link set, skipped, clamped, and its errors
//   data.md      every view of the chart as a table (the figures the embed draws)
//   data.json    the same, full length, for exact numbers
//   tool.txt     the tool page's visible text: its results, verdicts and summary cards
//   tool.png     the chart card on the tool page
//   embed-{light,dark}-{760,390}.png   the embed in a page, at a desktop and a phone width
import { createRequire } from 'node:module';
import { mkdirSync, writeFileSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require('/usr/local/lib/node_modules_global/playwright')); }

const HERE = dirname(fileURLToPath(import.meta.url));
const BLOG = resolve(HERE, '../../../..');
const [cmd, target, ...rest] = process.argv.slice(2);
const opt = { view: [], include: [] };
for (let i = 0; i < rest.length; i++) {
  const a = rest[i];
  if (a === '--light') { opt.light = true; continue; }
  if (!a.startsWith('--')) continue;
  const k = a.slice(2), v = rest[++i];
  if (Array.isArray(opt[k])) opt[k].push(v); else opt[k] = v;
}
if (!cmd || !target || !['charts', 'embed', 'shot'].includes(cmd)) {
  console.error('usage: brotools.mjs charts|embed|shot <url> [options]  (see the header of this file)');
  process.exit(2);
}

// The chart's card and its Share cluster, the way the tool's own checks find them.
const CARD = '.chart-modal, .detail-subsection, .chart-card, .chart-panel, .card';
const IN_PAGE = `
window.__bt = {
  clusters() {
    return [...document.querySelectorAll('.btn-cluster')].filter(c => c.__share);
  },
  cardOf(c) { return c.closest(${JSON.stringify(CARD)}) || c.parentElement; },
  chartOf(card) { return card && card.querySelector('canvas[id], .js-plotly-plot[id], [data-share-chart]'); },
  keyOf(el) { return el ? (el.id || (el.classList[0] ? '.' + el.classList[0] : '')) : ''; },
  titleOf(card) {
    const h = card && card.querySelector('h1,h2,h3,h4,.chart-title,.card-title,legend');
    return h ? h.textContent.replace(/\\s+/g, ' ').trim() : '';
  },
  list() {
    return this.clusters().map((c, i) => {
      const card = this.cardOf(c), el = this.chartOf(card);
      const views = [];
      card && card.querySelectorAll('select').forEach(s => {
        if (s.closest('.share-menu') || !this.shown(s)) return;
        views.push({ control: (s.getAttribute('aria-label') || s.id || 'select'),
          options: [...s.options].map(o => o.textContent.trim()), at: s.options[s.selectedIndex] && s.options[s.selectedIndex].textContent.trim() });
      });
      const btns = card ? [...card.querySelectorAll('[data-embed-mode] button, [data-embed-mode] [role=tab], .seg button, .toggle-group button')]
        .filter(b => b.offsetParent).map(b => b.textContent.replace(/\\s+/g, ' ').trim()).filter(Boolean) : [];
      if (btns.length) views.push({ control: 'buttons', options: [...new Set(btns)] });
      return { n: i, key: this.keyOf(el) || (c.__share.tool ? '(whole tool)' : ''), title: this.titleOf(card),
               shown: !!c.offsetParent, wholeTool: !!c.__share.tool, views };
    });
  },
  find(key) {
    const all = this.clusters();
    if (!key) return all.find(c => c.offsetParent) || all[0];
    if (/^#?\\d+$/.test(key)) return all[+key.replace('#', '')];
    return all.find(c => this.keyOf(this.chartOf(this.cardOf(c))) === key);
  },
  drawn(c) {
    const el = this.chartOf(this.cardOf(c));
    if (!el) return 'tool';
    const ch = window.Chart && window.Chart.getChart && window.Chart.getChart(el);
    if (ch) return JSON.stringify([ch.data.labels, ch.data.datasets.map(d => [d.label, d.data])]);
    if (el.data) return JSON.stringify(el.data.map(t => [t.name, t.x, t.y]));
    return el.getAttribute('data-share-sig') || el.innerHTML.length;
  },
  // A select the tool shows (some are drawn as a row of buttons over a hidden select).
  shown(s) { return !!(s.offsetParent || (s.parentElement && s.parentElement.offsetParent)); },
  // How close a control sits to the chart: the depth of their nearest common ancestor.
  near(a, b) {
    if (!b) return 0;
    let n = a; while (n && !n.contains(b)) n = n.parentElement;
    let d = 0; while (n) { d++; n = n.parentElement; } return d;
  },
  setView(c, text) {
    const card = this.cardOf(c), el = this.chartOf(card), want = text.toLowerCase().trim();
    const words = x => x.replace(/\\s+/g, ' ').trim().toLowerCase();
    const cands = [];
    card.querySelectorAll('select').forEach(s => [...s.options].forEach(o => {
      const t = words(o.textContent), exact = t === want || o.value.toLowerCase() === want;
      if (exact || t.includes(want)) cands.push({ exact, shown: this.shown(s), d: this.near(s, el), go: () => {
        s.value = o.value; s.dispatchEvent(new Event('input', { bubbles: true })); s.dispatchEvent(new Event('change', { bubbles: true }));
        return 'select ' + (s.getAttribute('aria-label') || s.id) + ': ' + o.textContent.trim(); } });
    }));
    [...card.querySelectorAll('button, [role=tab], label')].filter(b => b.offsetParent && !b.closest('.btn-cluster')).forEach(b => {
      const t = words(b.textContent), exact = t === want;
      if (exact || t.includes(want)) cands.push({ exact, shown: true, d: this.near(b, el), go: () => { b.click(); return 'button: ' + b.textContent.replace(/\\s+/g, ' ').trim(); } });
    });
    // A control the reader can see first, then an exact match, then the one nearest the chart.
    cands.sort((a, b) => (b.shown - a.shown) || (b.exact - a.exact) || (b.d - a.d));
    if (cands.length) return cands[0].go();
    return null;
  }
};`;

async function openTool(browser, url, light) {
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 1 });
  // A returning visitor: no first-visit tour over the page, and the theme we ask for.
  await ctx.addInitScript(([light]) => {
    const get = Storage.prototype.getItem;
    Storage.prototype.getItem = function (k) {
      if (/-seen$/.test(k)) return '1';
      if (/theme/i.test(k) && get.call(this, k) == null) return light ? 'light' : 'dark';
      return get.call(this, k);
    };
  }, [!!light]);
  await ctx.addInitScript(IN_PAGE);
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(String(e.message || e)));
  page.on('dialog', d => { errors.push('dialog: ' + d.message()); d.dismiss(); });
  await page.goto(url, { waitUntil: 'load', timeout: 60000 });
  // An AI link is applied once SharedAgent.done resolves.
  await page.evaluate(() => window.SharedAgent && window.SharedAgent.done ? Promise.race([window.SharedAgent.done, new Promise(r => setTimeout(r, 20000))]) : null).catch(() => {});
  if (light !== undefined) await page.evaluate(light => {
    if (document.body.classList.contains('light') !== light) { const b = document.getElementById('themeToggle'); if (b) b.click(); }
  }, !!light);
  return { ctx, page, errors };
}

// Wait until the chart stops changing (the tool has finished computing and drawing).
async function settle(page, key, seconds) {
  const end = Date.now() + seconds * 1000;
  let last = null, same = 0;
  while (Date.now() < end) {
    const d = await page.evaluate(k => { const c = __bt.find(k); return c ? String(__bt.drawn(c)) : null; }, key).catch(() => null);
    if (d && d === last) { if (++same >= 3) return true; } else same = 0;
    last = d;
    await page.waitForTimeout(500);
  }
  return false;
}

async function agentReport(page) {
  return page.evaluate(() => window.SharedAgent ? { link: !!SharedAgent.link, report: SharedAgent.report || null } : null);
}

function inputsMd(url, a) {
  const out = [`# Inputs`, '', `Tool page: ${url.split('#')[0]}`, ''];
  if (!a || !a.link) { out.push('No #load link was applied: the tool shows its defaults (or the page has no AI link support).'); return out.join('\n'); }
  const r = a.report || {};
  if (r.qs) out.push(`Quick Start: ${r.qs.key} (${r.qs.ok ? 'applied' : 'NOT applied'})`, '');
  out.push('| Key | Field | Value | Why |', '| --- | --- | --- | --- |');
  (r.applied || []).forEach(x => out.push(`| ${x.key} | ${cell(x.label)} | ${cell(x.value)} | ${cell(x.why || '')} |`));
  if ((r.unknown || []).length) out.push('', `**Unknown keys (ignored):** ${r.unknown.join(', ')}`);
  if ((r.clamped || []).length) out.push('', '**Clamped:**', ...r.clamped.map(c => `- ${c.key}: asked ${c.given}, used ${c.used}`));
  if ((r.errors || []).length) out.push('', '**Errors:**', ...r.errors.map(e => `- ${e}`));
  return out.join('\n');
}
const cell = v => String(v == null ? '' : v).replace(/\|/g, '\\|').replace(/\n/g, ' ');
const num = v => typeof v === 'number' ? (Number.isInteger(v) ? v : +v.toPrecision(6)) : v;

// The snapshot written as tables: one per view the embed offers.
function framesOf(snap) {
  const pool = snap.pool || [];
  const de = v => v && typeof v === 'object' && '$p' in v ? pool[v.$p] : v;
  const modes = snap.modes || [];
  const names = {};
  Object.entries(snap.map || {}).forEach(([combo, fi]) => {
    names[fi] = String(combo).split(',').map((o, i) => modes[i] && modes[i].o && modes[i].o[+o] ? (modes[i].o[+o].l || `${modes[i].l} ${o}`) : o).join(' / ');
  });
  const at = modes.map(m => m.at).join(',');
  return (snap.frames || []).map((f, i) => {
    const labels = de(f.labels) || [];
    const sets = (f.datasets || []).map(d => ({ label: d.label, type: d.type || f.type, data: (de(d.data) || []).map(p => p && typeof p === 'object' ? { x: num(de(p.x)), y: num(de(p.y)) } : num(p)) }));
    const sc = (f.options && f.options.scales) || {};
    const axes = Object.fromEntries(Object.entries(sc).map(([k, s]) => [k, s && s.title && s.title.text]).filter(([, t]) => t));
    const title = f.options && f.options.plugins && f.options.plugins.title && f.options.plugins.title.text;
    return { view: names[i] || (i === 0 ? 'default' : `frame ${i}`), shownFirst: snap.map ? snap.map[at] === i : i === 0,
             kind: snap.kind, type: f.type, title, axes, labels: Array.isArray(labels) ? labels.map(num) : labels, datasets: sets,
             traces: snap.kind === 'plotly' ? f.traces : undefined };
  });
}

function dataMd(meta, frames) {
  const out = [`# ${meta.title || meta.key}`, '', `Tool: ${meta.tool} · chart key: ${meta.key}`, '',
    'Figures as the embed draws them, unrounded beyond 6 significant digits. Long series are',
    'sampled here (first, last and evenly between); data.json has every point.', ''];
  if (meta.kind !== 'chartjs') out.push(`This is a ${meta.kind} chart: read data.json, tool.txt and the screenshots for its figures.`, '');
  frames.forEach(f => {
    out.push(`## View: ${f.view}${f.shownFirst ? ' (the view the embed opens on)' : ''}`, '');
    if (f.title) out.push(`Chart title: ${f.title}`, '');
    const ax = Object.entries(f.axes || {}).map(([k, t]) => `${k}: ${t}`).join(' · ');
    if (ax) out.push(`Axes: ${ax}`, '');
    if (!f.datasets.length) { out.push('(no datasets)', ''); return; }
    const xy = f.datasets.some(d => d.data.some(p => p && typeof p === 'object'));
    let rows;
    if (xy) {
      const xs = [...new Set(f.datasets.flatMap(d => d.data.map(p => p && p.x)))].filter(x => x != null).sort((a, b) => a - b);
      rows = xs.map(x => [x, ...f.datasets.map(d => { const p = d.data.find(p => p && p.x === x); return p ? p.y : ''; })]);
    } else {
      const n = Math.max(f.labels.length || 0, ...f.datasets.map(d => d.data.length));
      rows = Array.from({ length: n }, (_, i) => [f.labels[i] ?? i, ...f.datasets.map(d => d.data[i] ?? '')]);
    }
    const MAX = 25;
    if (rows.length > MAX) {
      const pick = new Set([0, rows.length - 1]);
      for (let k = 1; k < MAX - 1; k++) pick.add(Math.round(k * (rows.length - 1) / (MAX - 1)));
      rows = [...pick].sort((a, b) => a - b).map(i => rows[i]);
      out.push(`(${n_(f)} points, ${MAX} shown)`, '');
    }
    out.push(`| ${cell(f.axes.x || 'Label')} | ${f.datasets.map(d => cell(d.label)).join(' | ')} |`,
             `| --- | ${f.datasets.map(() => '---:').join(' | ')} |`,
             ...rows.map(r => `| ${r.map(cell).join(' | ')} |`), '');
  });
  return out.join('\n');
}
const n_ = f => Math.max(f.labels.length || 0, ...f.datasets.map(d => d.data.length));

// The embed code in a page shaped like a blog post's column.
function hostPage(code, theme) {
  const dark = theme === 'dark';
  const c = code.replace(/(src="[^"]*\/embed\/#[^"]*?)(")/, `$1&amp;theme=${theme}$2`)
                .replace(/(src="[^"]*#embed=[^"]*?theme=)(light|dark)/, `$1${theme}`);
  return `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{margin:0;padding:24px 16px;background:${dark ? '#0f1726' : '#ffffff'};color:${dark ? '#e6ecf5' : '#14203a'};font:17px/1.6 system-ui,sans-serif}
main{max-width:720px;margin:0 auto}a{color:${dark ? '#7fb0ff' : '#0052cc'}}</style></head>
<body><main><p>A paragraph of the post, before the chart.</p>
${c}
<p>A paragraph of the post, after the chart.</p></main></body></html>`;
}

async function shootEmbed(browser, code, theme, width, file) {
  const ctx = await browser.newContext({ viewport: { width, height: 900 }, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  // A real origin for the host page, so the frame's sizing message is handled as on the blog.
  await page.route('https://blog.preview/**', r => r.fulfill({ contentType: 'text/html', body: hostPage(code, theme) }));
  await page.goto('https://blog.preview/post/', { waitUntil: 'load', timeout: 60000 });
  const frame = page.frames().find(f => f !== page.mainFrame());
  if (frame) await frame.waitForFunction(() => !document.documentElement.classList.contains('abt-embed-wait') && !/Loading data/.test(document.body.innerText), null, { timeout: 30000 }).catch(() => {});
  await page.waitForTimeout(2500);
  await page.screenshot({ path: file, fullPage: true });
  const h = await page.evaluate(() => { const f = document.querySelector('iframe'); return f ? f.getBoundingClientRect().height : 0; });
  const over = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
  await ctx.close();
  return { height: Math.round(h), sideways: over };
}

async function main() {
  const browser = await chromium.launch();
  try {
    if (cmd === 'shot') {
      const width = +(opt.width || 390), theme = opt.theme;
      const ctx = await browser.newContext({ viewport: { width, height: 900 }, deviceScaleFactor: 1, colorScheme: theme === 'light' ? 'light' : 'dark' });
      // The blog's own pick (head.html reads blog-theme, the tool reads abt-theme).
      if (theme) await ctx.addInitScript(t => { try { localStorage.setItem('blog-theme', t); localStorage.setItem('abt-theme', t); } catch (e) {} }, theme);
      const page = await ctx.newPage();
      await page.goto(target, { waitUntil: 'load', timeout: 60000 });
      await page.waitForTimeout(4000);
      const file = opt.out || join(BLOG, '_build/brotools', `shot-${width}.png`);
      mkdirSync(dirname(file), { recursive: true });
      await page.screenshot({ path: file, fullPage: true });
      const over = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
      console.log(`${file}\nscrolls sideways: ${over > 0 ? 'YES, by ' + over + 'px' : 'no'}`);
      // Each tool embed on its own, with the text around it: the frames are lazy, so each is
      // scrolled to and given time to draw first.
      const frames = await page.$$('iframe[src*="tool.adjiebrotots.com"]');
      // The sticky top bar and floating buttons would sit over a crop: hide them for these.
      if (frames.length) await page.evaluate(() => document.querySelectorAll('body *').forEach(el => {
        const p = getComputedStyle(el).position;
        if (p === 'fixed' || p === 'sticky') el.style.visibility = 'hidden';
      }));
      for (let i = 0; i < frames.length; i++) {
        await frames[i].scrollIntoViewIfNeeded();
        await page.waitForTimeout(3500);
        const box = await frames[i].evaluate(f => {
          const r = f.getBoundingClientRect(), y = r.top + scrollY;
          return { y: Math.max(0, y - 160), h: r.height + 320 };
        });
        const f = file.replace(/\.png$/, '') + `-embed-${i + 1}.png`;
        await page.screenshot({ path: f, fullPage: true, clip: { x: 0, y: box.y, width, height: box.h } });
        console.log(f);
      }
      return;
    }

    const { ctx, page, errors } = await openTool(browser, target, opt.light ? true : false);
    if (cmd === 'charts') {
      await page.waitForTimeout(1500);
      const a = await agentReport(page);
      console.log(inputsMd(target, a), '\n');
      const list = await page.evaluate(() => __bt.list());
      console.log('# Charts (embed --chart KEY; --view picks a view first)\n');
      if (!list.length) console.log('(none: this page has no chart with a Share menu yet. Some tools show one only after you run or generate something; then embed the whole page with the tool-embed include, or ask Adjie for the code.)');
      list.forEach(c => {
        console.log(`- ${c.key || '#' + c.n}  "${c.title}"${c.shown ? '' : '  (hidden until opened)'}${c.wholeTool ? '  (embeds the whole tool)' : ''}`);
        c.views.forEach(v => console.log(`    views (${v.control}): ${v.options.join(' | ')}${v.at ? '   [now: ' + v.at + ']' : ''}`));
      });
      if (errors.length) console.log('\nPage errors:', errors.slice(0, 5).join(' | '));
      return;
    }

    // embed
    const key = opt.chart || '';
    const found = await page.evaluate(k => !!__bt.find(k), key);
    if (!found) throw new Error(`no chart "${key}" on this page: run the charts command to list them`);
    await settle(page, key, +(opt.wait || 45));
    for (const v of opt.view) {
      const r = await page.evaluate(([k, v]) => __bt.setView(__bt.find(k), v), [key, v]);
      if (!r) throw new Error(`no view "${v}" in the chart's card`);
      console.log('view set:', r);
      await settle(page, key, +(opt.wait || 45));
    }
    const meta = await page.evaluate(k => {
      const c = __bt.find(k), card = __bt.cardOf(c), el = __bt.chartOf(card);
      return { key: __bt.keyOf(el), title: __bt.titleOf(card), tool: location.pathname };
    }, key);
    const res = await page.evaluate(([k, inc]) => SharedShare.embedCode(__bt.find(k), inc.length ? inc : undefined)
      .then(r => ({ code: r.code, open: r.open, snap: r.snap ? JSON.stringify(r.snap) : null })), [key, opt.include]);
    const name = opt.name || `${meta.tool.replace(/^\/|\/$/g, '').replace(/\//g, '-')}-${(meta.key || 'tool').replace(/^\./, '')}`;
    const dir = resolve(opt.out || join(BLOG, '_build/brotools'), name);
    mkdirSync(dir, { recursive: true });
    writeFileSync(join(dir, 'embed.html'), res.code + '\n');
    writeFileSync(join(dir, 'link.txt'), (res.open || '') + '\n');
    writeFileSync(join(dir, 'inputs.md'), inputsMd(target, await agentReport(page)) + '\n');
    const text = await page.evaluate(() => (document.querySelector('main') || document.body).innerText);
    writeFileSync(join(dir, 'tool.txt'), text.replace(/\n{3,}/g, '\n\n') + '\n');
    const card = await page.evaluateHandle(k => __bt.cardOf(__bt.find(k)), key);
    await card.asElement().scrollIntoViewIfNeeded().catch(() => {});
    await card.asElement().screenshot({ path: join(dir, 'tool.png') }).catch(e => console.log('tool.png:', e.message));
    let frames = [];
    if (res.snap) {
      const snap = JSON.parse(res.snap);
      frames = framesOf(snap);
      meta.kind = snap.kind;
      writeFileSync(join(dir, 'data.json'), JSON.stringify({ ...meta, link: res.open, frames }, null, 1) + '\n');
      writeFileSync(join(dir, 'data.md'), dataMd(meta, frames) + '\n');
    } else {
      const t = meta.title || ((/title="([^"]*)"/.exec(res.code) || [])[1] || '').replace(/&amp;/g, '&');
      writeFileSync(join(dir, 'data.md'), `# ${t}\n\nThis embed is the whole tool (an iframe of the tool page), so it carries no chart data. Read tool.txt and the screenshots.\n`);
    }
    await ctx.close();
    const shots = [];
    for (const [theme, width] of [['light', 760], ['dark', 760], ['light', 390], ['dark', 390]]) {
      const f = join(dir, `embed-${theme}-${width}.png`);
      const r = await shootEmbed(browser, res.code, theme, width, f);
      shots.push(`${f}  (frame ${r.height}px tall${r.sideways ? ', PAGE SCROLLS SIDEWAYS' : ''})`);
    }
    const kb = Math.round(res.code.length / 1024);
    console.log([`Embed written to ${dir}`, `  embed.html  ${kb} KB${kb > 8 ? ' (long: the chart carries its data in the link; fine to paste)' : ''}`,
      `  data.md     ${frames.length} view(s): ${frames.map(f => f.view).join(' | ')}`,
      '  inputs.md, tool.txt, link.txt, tool.png', ...shots.map(s => '  ' + s),
      errors.length ? `Page errors: ${errors.slice(0, 5).join(' | ')}` : ''].filter(Boolean).join('\n'));
  } finally { await browser.close(); }
}
main().catch(e => { console.error('ERROR', e.message); process.exit(1); });
