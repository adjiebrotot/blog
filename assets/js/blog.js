/* Adjie Brotot Blog: the only script on the page.
   1. The theme button: flips light / dark and remembers the pick.
   2. Charts embedded from tool.adjiebrotots.com follow the blog's theme. Their
      link names a theme (#embed=…&theme=light); the tool reads it once when
      the frame loads, so a frame in the wrong theme is swapped for a fresh one.
   3. kramdown's {:toc} list gets its heading in the page's language.
   4. Rich Markdown in a post, the same set as the tool's Markdown Reader
      (tool.adjiebrotots.com/mdtopdf/): LaTeX through KaTeX, ```mermaid
      diagrams and charts, a copy button on code, and GitHub's > [!NOTE]
      alerts. KaTeX and Mermaid load only on a post that uses them.
   5. Comments (giscus) load only when the reader nears them, and follow the
      theme button.
   6. On a post, a reading guide built from its h2s: a floating list of
      sections at the left on a wide screen, a bar split by section length on
      a narrow one. Both are added here, never in the HTML, so crawlers and
      feeds see the same page as before.
   7. Abbreviations: kramdown writes *[PTKP]: … definitions as <abbr title>.
      A bubble shows the meaning on hover, focus, click or tap, so a phone
      reader gets it too; the title stays in the HTML for crawlers.
   8. The Share menu on a post (_includes/share.html): Facebook, X and
      LinkedIn as links, a Story or Post poster drawn here on a canvas, and
      Share as link.
   9. Ads fill the gaps in a card grid: the last row of a post grid gets
      in-feed tiles in its empty cells, and on the landing page the shorter
      language column gets the multiplex unit (or one tile). Settings:
      `adsense` in _config.yml.
   UI words come from _data/i18n.yml through data-* on <body>. */
(function () {
  var root = document.documentElement;
  var words = document.body.dataset;
  var prose = document.querySelector('.prose');

  function theme() { return root.classList.contains('light') ? 'light' : 'dark'; }
  function cssVar(name) { return getComputedStyle(root).getPropertyValue(name).trim(); }

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      var s = document.createElement('script');
      s.src = src; s.crossOrigin = 'anonymous';
      s.onload = resolve; s.onerror = reject;
      document.head.appendChild(s);
    });
  }
  function loadCss(href) {
    var l = document.createElement('link');
    l.rel = 'stylesheet'; l.href = href; l.crossOrigin = 'anonymous';
    document.head.appendChild(l);
  }

  function syncEmbeds() {
    var want = theme();
    Array.prototype.forEach.call(document.querySelectorAll('iframe[src*="tool.adjiebrotots.com"]'), function (f) {
      var src = f.getAttribute('src') || '';
      if (!/[#&]embed=/.test(src)) return;
      var next = src.replace(/([#&]theme=)(light|dark)\b/, '$1' + want);
      if (next === src) return;
      var fresh = f.cloneNode(false);
      fresh.setAttribute('src', next);
      f.parentNode.replaceChild(fresh, f);
    });
  }

  /* ── Mermaid: flowcharts, sequence, gantt, pie, xychart-beta, … ── */
  var MERMAID = 'https://cdn.jsdelivr.net/npm/mermaid@10.9.0/dist/mermaid.min.js';
  var diagrams = prose ? Array.prototype.map.call(
    prose.querySelectorAll('pre > code.language-mermaid'), function (code) {
      var box = document.createElement('div');
      box.className = 'mermaid-box';
      box.dataset.src = code.textContent;
      code.parentNode.replaceWith(box);
      return box;
    }) : [];
  var mermaidReady = null;

  /* Diagram colours are the blog's own tokens, read in the current theme, and
     series take the tool's neutral sequence (SharedPalette: blue, gold, teal,
     rose, purple), so a chart here matches a chart in a tool. */
  function mermaidTheme() {
    var seen = {}, pal = [];
    ['--line-a', '--gold', '--line-c', '--line-d', '--line-e'].forEach(function (n) {
      var c = cssVar(n); if (c && !seen[c.toLowerCase()]) { seen[c.toLowerCase()] = 1; pal.push(c); }
    });
    var v = {
      darkMode: theme() === 'dark',
      fontFamily: "'DM Sans', system-ui, sans-serif", fontSize: '15px',
      background: cssVar('--panel'), textColor: cssVar('--text'), titleColor: cssVar('--text'),
      primaryColor: cssVar('--positive-bg'), primaryBorderColor: cssVar('--positive-border'), primaryTextColor: cssVar('--text'),
      secondaryColor: cssVar('--bg-subtle'), tertiaryColor: cssVar('--panel-raised'),
      mainBkg: cssVar('--positive-bg'), nodeBorder: cssVar('--positive-border'),
      clusterBkg: cssVar('--bg-subtle'), clusterBorder: cssVar('--border'),
      lineColor: cssVar('--chart-text'), edgeLabelBackground: cssVar('--panel'),
      noteBkgColor: cssVar('--warning-bg'), noteTextColor: cssVar('--warning-text'), noteBorderColor: cssVar('--gold'),
      actorBkg: cssVar('--positive-bg'), actorBorder: cssVar('--positive-border'), actorTextColor: cssVar('--text'),
      signalColor: cssVar('--text'), signalTextColor: cssVar('--text'),
      pieOpacity: '0.92', pieStrokeColor: cssVar('--panel'), pieOuterStrokeColor: cssVar('--border'),
      pieTitleTextColor: cssVar('--text'), pieLegendTextColor: cssVar('--text'), pieSectionTextColor: cssVar('--text-inv'),
      xyChart: {
        backgroundColor: cssVar('--panel'), titleColor: cssVar('--text'),
        xAxisLabelColor: cssVar('--chart-text'), xAxisTitleColor: cssVar('--chart-text'),
        xAxisTickColor: cssVar('--chart-grid'), xAxisLineColor: cssVar('--chart-grid'),
        yAxisLabelColor: cssVar('--chart-text'), yAxisTitleColor: cssVar('--chart-text'),
        yAxisTickColor: cssVar('--chart-grid'), yAxisLineColor: cssVar('--chart-grid'),
        plotColorPalette: pal.join(',')
      }
    };
    pal.forEach(function (c, i) { v['pie' + (i + 1)] = c; v['cScale' + i] = c; });
    return { startOnLoad: false, securityLevel: 'strict', theme: 'base', themeVariables: v };
  }

  function drawDiagrams() {
    if (!diagrams.length) return;
    if (!mermaidReady) mermaidReady = loadScript(MERMAID);
    mermaidReady.then(function () {
      window.mermaid.initialize(mermaidTheme());
      diagrams.forEach(function (box, i) {
        window.mermaid.render('mmd-' + i + '-' + Date.now().toString(36), box.dataset.src).then(function (r) {
          box.innerHTML = r.svg;
        }, function () {
          var pre = document.createElement('pre');
          pre.textContent = box.dataset.src;
          box.replaceChildren(pre);
        });
      });
    }, function () {});
  }

  /* ── LaTeX: kramdown turns $$…$$ into \(…\) inline and \[…\] on its own
     line, which KaTeX renders. A lone $ stays a dollar sign. ── */
  var KATEX = 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/';
  function renderMath() {
    if (!prose || !/\\\(|\\\[|\$\$/.test(prose.textContent)) return;
    loadCss(KATEX + 'katex.min.css');
    loadScript(KATEX + 'katex.min.js')
      .then(function () { return loadScript(KATEX + 'contrib/auto-render.min.js'); })
      .then(function () {
        window.renderMathInElement(prose, {
          delimiters: [
            { left: '$$', right: '$$', display: true },
            { left: '\\[', right: '\\]', display: true },
            { left: '\\(', right: '\\)', display: false }
          ],
          throwOnError: false,
          ignoredTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']
        });
      }, function () {});
  }

  /* ── Code: a copy button on every block ── */
  function addCopyButtons() {
    if (!prose || !navigator.clipboard) return;
    Array.prototype.forEach.call(prose.querySelectorAll('pre'), function (pre) {
      if (pre.closest('.mermaid-box') || !pre.querySelector('code')) return;
      var host = pre.closest('.highlighter-rouge') || pre;
      if (host === pre) { var wrap = document.createElement('div'); pre.replaceWith(wrap); wrap.appendChild(pre); host = wrap; }
      host.classList.add('code-block');
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'code-copy'; b.textContent = words.copy;
      b.addEventListener('click', function () {
        navigator.clipboard.writeText(pre.querySelector('code').textContent.replace(/\n$/, '')).then(function () {
          b.textContent = words.copied;
          setTimeout(function () { b.textContent = words.copy; }, 1600);
        }, function () {});
      });
      host.appendChild(b);
    });
  }

  /* ── GitHub alerts: > [!NOTE], [!TIP], [!IMPORTANT], [!WARNING], [!CAUTION] ── */
  function styleAlerts() {
    if (!prose) return;
    Array.prototype.forEach.call(prose.querySelectorAll('blockquote'), function (q) {
      var p = q.firstElementChild;
      var m = p && p.tagName === 'P' && /^\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*/i.exec(p.innerHTML);
      if (!m) return;
      p.innerHTML = p.innerHTML.slice(m[0].length);
      if (!p.textContent.trim()) p.remove();
      q.classList.add('alert', 'alert-' + m[1].toLowerCase());
    });
  }

  /* ── Comments: giscus.app is not contacted until the comments section is
     within a screen of view, so it costs the post nothing on load. ── */
  var giscusBox = document.querySelector('.comments .giscus');
  function giscusTheme() { return giscusBox.dataset['theme' + (theme() === 'light' ? 'Light' : 'Dark')]; }
  function loadComments() {
    var d = giscusBox.dataset, s = document.createElement('script');
    s.src = 'https://giscus.app/client.js'; s.async = true; s.crossOrigin = 'anonymous';
    [['repo', d.repo], ['repo-id', d.repoId], ['category', d.category], ['category-id', d.categoryId],
     ['mapping', 'specific'], ['term', d.term], ['strict', '1'], ['reactions-enabled', '1'],
     ['emit-metadata', '0'], ['input-position', 'bottom'], ['lang', d.lang], ['theme', giscusTheme()]
    ].forEach(function (kv) { s.setAttribute('data-' + kv[0], kv[1]); });
    giscusBox.appendChild(s);
  }
  function syncComments() {
    var f = giscusBox && giscusBox.querySelector('iframe.giscus-frame');
    if (f) f.contentWindow.postMessage({ giscus: { setConfig: { theme: giscusTheme() } } }, 'https://giscus.app');
  }
  if (giscusBox) {
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) { io.disconnect(); loadComments(); }
      }, { rootMargin: '0px 0px 100% 0px' });
      io.observe(giscusBox);
    } else loadComments();
  }

  var btn = document.getElementById('themeToggle');
  /* The toggle says what a press will do, as on www and the tools. */
  function labelTheme() {
    if (!btn) return;
    var text = theme() === 'light' ? btn.dataset.toDark : btn.dataset.toLight;
    if (text) { btn.setAttribute('aria-label', text); btn.title = text; }
  }
  labelTheme();
  if (btn) btn.addEventListener('click', function () {
    var next = theme() === 'light' ? 'dark' : 'light';
    root.classList.remove('light', 'dark');
    root.classList.add(next);
    try { localStorage.setItem('blog-theme', next); } catch (e) {}
    // The pick is shared with www and the tools through one cookie on the
    // parent domain (see tool.adjiebrotots.com theme.js).
    if (/(^|\.)adjiebrotots\.com$/.test(location.hostname)) {
      document.cookie = 'abt-theme=' + next + '; max-age=31536000; path=/; SameSite=Lax; domain=adjiebrotots.com' + (location.protocol === 'https:' ? '; Secure' : '');
    }
    syncEmbeds();
    syncComments();
    labelTheme();
    if (mermaidReady) drawDiagrams();
  });

  syncEmbeds();
  styleAlerts();
  addCopyButtons();
  renderMath();
  drawDiagrams();

  var toc = document.getElementById('markdown-toc');
  if (toc) toc.setAttribute('data-title', words.contents);

  /* ── Reading guide: CSS shows the rail or the bar, never both. The active
     section is the last h2 above a line a third down the screen. The rail
     waits until the post's own {:toc} (or, without one, its header) has
     scrolled under the site bar, so the two lists never show together. The
     bar hangs from the bottom of the site bar and travels with it. ── */
  var heads = prose && document.querySelector('.post') ? Array.prototype.filter.call(
    prose.querySelectorAll('h2'), function (h) { return h.id; }) : [];
  if (heads.length > 1) {
    var rail = document.createElement('nav');
    rail.className = 'toc-rail';
    rail.setAttribute('aria-label', words.contents);
    var list = document.createElement('ol');
    var bar = document.createElement('div');
    bar.className = 'read-bar';
    bar.setAttribute('aria-hidden', 'true');
    var links = [], fills = [];
    heads.forEach(function (h) {
      var li = document.createElement('li'), a = document.createElement('a');
      a.href = '#' + h.id; a.textContent = h.textContent;
      li.appendChild(a); list.appendChild(li); links.push(a);
      var seg = document.createElement('span'), fill = document.createElement('i');
      seg.appendChild(fill); bar.appendChild(seg); fills.push(fill);
    });
    rail.appendChild(list);
    document.body.appendChild(rail);
    var header = document.querySelector('.site-header');
    (header || document.body).appendChild(bar);
    var gate = toc || document.querySelector('.post-header');

    var queued = false, current = -1;
    var update = function () {
      queued = false;
      var vh = window.innerHeight, line = vh / 3, end = prose.getBoundingClientRect().bottom;
      var tops = heads.map(function (h) { return h.getBoundingClientRect().top; });
      var atEnd = window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2;
      var top = header ? header.getBoundingClientRect().bottom : 0;
      rail.classList.toggle('is-shown', !gate || gate.getBoundingClientRect().bottom <= top);
      var active = -1;
      tops.forEach(function (t, i) {
        var next = i + 1 < tops.length ? tops[i + 1] : end, len = next - t;
        if (t <= line) active = i;
        /* Each part fills as its section scrolls into view. */
        var seen = Math.min(Math.max((vh - t) / len, 0), 1);
        fills[i].style.transform = 'scaleX(' + seen + ')';
        if (!fills[i].parentNode.style.flexGrow) fills[i].parentNode.style.flexGrow = Math.max(len, 1);
      });
      if (atEnd) active = heads.length - 1;
      if (active !== current) {
        if (current > -1) links[current].removeAttribute('aria-current');
        if (active > -1) links[active].setAttribute('aria-current', 'true');
        current = active;
      }
    };
    var queue = function () { if (!queued) { queued = true; requestAnimationFrame(update); } };
    /* Section lengths change as images, diagrams and embeds load. */
    var resize = function () { fills.forEach(function (f) { f.parentNode.style.flexGrow = ''; }); queue(); };
    window.addEventListener('scroll', queue, { passive: true });
    window.addEventListener('resize', resize);
    window.addEventListener('load', resize);
    if ('ResizeObserver' in window) new ResizeObserver(resize).observe(prose);
    update();
  }

  /* 7. Abbreviations. The native title is moved to data-title so it does not
     pop up a second time over the bubble. */
  var abbrs = prose ? prose.querySelectorAll('abbr[title]') : [];
  if (abbrs.length) {
    var bubble = document.createElement('div');
    bubble.className = 'abbr-tip';
    bubble.setAttribute('role', 'tooltip');
    bubble.id = 'abbr-tip';
    document.body.appendChild(bubble);
    var shown = null, shownAt = 0;
    var place = function (el) {
      var r = el.getBoundingClientRect(), b = bubble.getBoundingClientRect();
      var left = Math.min(Math.max(8, r.left + r.width / 2 - b.width / 2), window.innerWidth - b.width - 8);
      var top = r.top - b.height - 8;
      if (top < 8) top = r.bottom + 8;
      bubble.style.left = left + 'px';
      bubble.style.top = top + 'px';
    };
    var show = function (el) {
      if (shown !== el) shownAt = Date.now();
      shown = el;
      bubble.textContent = el.dataset.title;
      bubble.classList.add('is-shown');
      el.setAttribute('aria-describedby', 'abbr-tip');
      place(el);
    };
    var hide = function () {
      if (shown) shown.removeAttribute('aria-describedby');
      shown = null;
      bubble.classList.remove('is-shown');
    };
    Array.prototype.forEach.call(abbrs, function (el) {
      el.dataset.title = el.title;
      el.removeAttribute('title');
      el.tabIndex = 0;
      /* Hover is for a mouse only: a tap sends its own enter and leave. */
      el.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') show(el); });
      el.addEventListener('pointerleave', function (e) { if (e.pointerType === 'mouse') hide(); });
      el.addEventListener('focus', function () { show(el); });
      // Only when focus moves on to something else (Tab); a click away is handled below.
      el.addEventListener('blur', function (e) { if (e.relatedTarget) hide(); });
      /* A tap focuses the term just before click, so a click
         straight after the bubble opened keeps it open; a second tap closes it. */
      el.addEventListener('click', function (e) {
        e.stopPropagation();
        if (shown === el && Date.now() - shownAt > 400) hide(); else show(el);
      });
    });
    document.addEventListener('click', hide);
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') hide(); });
    window.addEventListener('scroll', function () { if (shown) place(shown); }, { passive: true });
  }

  /* 8. Share. The menu works as the tool site's Share menu does (shared.js
     SharedShare): opened under its button, arrow keys between rows, Escape
     or Tab back to the button. Its list moves to the body when it opens, so
     no box can clip it. */
  var shareMenus = document.querySelectorAll('.share-menu');
  var openShare = null;
  function shareRows(m) { return Array.prototype.slice.call(m.list.querySelectorAll('.share-opt')); }
  /* Below the button, right edges lined up; above it when there is no room. */
  function placeList(btn, list) {
    var r = btn.getBoundingClientRect(), vw = root.clientWidth, vh = window.innerHeight;
    var w = Math.min(292, vw - 16);
    list.style.width = w + 'px';
    list.style.left = Math.max(8, Math.min(r.right - w, vw - w - 8)) + 'px';
    var below = vh - r.bottom - 12, above = r.top - 12, cap = 420;
    if (below < Math.min(cap, 260) && above > below) {
      list.style.top = ''; list.style.bottom = (vh - r.top + 4) + 'px'; list.style.maxHeight = Math.min(cap, above) + 'px';
    } else {
      list.style.bottom = ''; list.style.top = (r.bottom + 4) + 'px'; list.style.maxHeight = Math.min(cap, Math.max(below, 160)) + 'px';
    }
  }
  function closeShare(m, refocus) {
    m.list.classList.remove('is-open');
    m.btn.setAttribute('aria-expanded', 'false');
    if (openShare === m) openShare = null;
    if (refocus) m.btn.focus({ preventScroll: true });
  }
  function showShare(m) {
    if (openShare && openShare !== m) closeShare(openShare);
    if (m.list.parentNode !== document.body) document.body.appendChild(m.list);
    m.list.classList.add('is-open');
    m.btn.setAttribute('aria-expanded', 'true');
    placeList(m.btn, m.list);
    openShare = m;
  }
  /* The button's own words say "Link copied" for a moment. */
  function flashShare(m) {
    var el = m.btn.querySelector('.share-label');
    if (el.__t) clearTimeout(el.__t); else el.__text = el.textContent;
    el.textContent = m.box.dataset.copied;
    el.__t = setTimeout(function () { el.textContent = el.__text; el.__t = null; }, 1600);
  }
  function copyText(text) {
    function fallback() {
      var ta = document.createElement('textarea');
      ta.value = text; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      var ok = false;
      try { ok = document.execCommand('copy'); } catch (e) {}
      ta.remove();
      return ok ? Promise.resolve() : Promise.reject(new Error('copy'));
    }
    if (navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(text).catch(fallback);
    return fallback();
  }

  function pickShare(m, kind) {
    var d = m.box.dataset;
    if (kind === 'link') { copyText(d.url).then(function () { flashShare(m); }, function () {}); return; }
    if (kind === 'story' || kind === 'post') {
      copyText(d.url).catch(function () {});
      openPoster(m, kind);
    }
  }

  Array.prototype.forEach.call(shareMenus, function (box) {
    var m = { box: box, btn: box.querySelector('.share-toggle'), list: box.querySelector('.share-list') };
    box.hidden = false;
    m.btn.addEventListener('click', function (e) {
      e.stopPropagation();
      if (openShare === m) { closeShare(m); return; }
      showShare(m);
      shareRows(m)[0].focus({ preventScroll: true });
    });
    m.btn.addEventListener('keydown', function (e) {
      if (e.key !== 'ArrowDown' && e.key !== 'ArrowUp') return;
      e.preventDefault();
      showShare(m);
      var r = shareRows(m);
      r[e.key === 'ArrowDown' ? 0 : r.length - 1].focus({ preventScroll: true });
    });
    m.list.addEventListener('click', function (e) {
      e.stopPropagation();
      var b = e.target.closest('.share-opt');
      if (!b) return;
      closeShare(m, true);
      // The three networks are plain links and open on their own.
      if (b.tagName === 'BUTTON') pickShare(m, b.dataset.kind);
    });
    m.list.addEventListener('mousemove', function (e) {
      var b = e.target.closest('.share-opt');
      if (b && b !== document.activeElement && m.list.contains(document.activeElement)) b.focus({ preventScroll: true });
    });
    m.list.addEventListener('keydown', function (e) {
      var r = shareRows(m), i = r.indexOf(document.activeElement), to = null;
      if (e.key === 'ArrowDown') to = r[(i + 1) % r.length];
      else if (e.key === 'ArrowUp') to = r[(i - 1 + r.length) % r.length];
      else if (e.key === 'Home') to = r[0];
      else if (e.key === 'End') to = r[r.length - 1];
      else if (e.key === 'Escape' || e.key === 'Tab') { e.preventDefault(); e.stopPropagation(); closeShare(m, true); return; }
      else return;
      e.preventDefault();
      to.focus();
    });
  });
  if (shareMenus.length) {
    document.addEventListener('click', function () { if (openShare) closeShare(openShare); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && openShare) closeShare(openShare, true); });
    window.addEventListener('scroll', function (e) { if (openShare && !openShare.list.contains(e.target)) closeShare(openShare); }, true);
    window.addEventListener('resize', function () { if (openShare) closeShare(openShare); });
  }

  /* The floating Share shows while neither the header's nor the footer's
     Share is on screen, so the reader can share from anywhere in the post. */
  var shareFloat = document.querySelector('.share-float');
  if (shareFloat && 'IntersectionObserver' in window) {
    var seen = new Set();
    var fio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) seen.add(en.target); else seen.delete(en.target); });
      var on = seen.size === 0;
      shareFloat.classList.toggle('is-shown', on);
      if (!on && openShare && shareFloat.contains(openShare.btn)) closeShare(openShare);
    });
    Array.prototype.forEach.call(document.querySelectorAll('.post-actions'), function (el) { fio.observe(el); });
  }

  /* ── The poster: the post's category, title and picture in the og card's
     look (_build/og.mjs), always in the day colours, with blank space left
     for Instagram's link sticker. A Story is 1080x1920, its picture and title
     high up, its name at the very bottom and a wide blank middle; a Post is
     1080x1080. ── */
  var INK = '#14203A', BG = '#F0F4FF', MUTED = '#4C5B76', GOLD = '#B45309';
  var SANS = "'DM Sans', system-ui, sans-serif";
  function loadImage(src) {
    return new Promise(function (resolve, reject) {
      var img = new Image();
      img.onload = function () { resolve(img); };
      img.onerror = reject;
      img.src = src;
    });
  }
  /* The picture: share_image from the front matter, else the post's first
     illustration, else its first image. */
  function posterPicture(d) {
    if (d.image) return d.image;
    var img = prose && (prose.querySelector('img[src*="-ill-"]') || prose.querySelector('img[src]'));
    return img ? img.currentSrc || img.src : null;
  }
  function wrapLines(ctx, text, width) {
    var words = text.split(/\s+/), lines = [], line = '';
    words.forEach(function (w) {
      var next = line ? line + ' ' + w : w;
      if (line && ctx.measureText(next).width > width) { lines.push(line); line = w; } else line = next;
    });
    if (line) lines.push(line);
    return lines;
  }
  /* The largest size from the list whose lines fit both maxLines and a
     height budget; the smallest size if none does. */
  function fitTitle(ctx, text, width, sizes, maxLines, budget) {
    for (var i = 0; i < sizes.length; i++) {
      ctx.font = '800 ' + sizes[i] + 'px ' + SANS;
      var lines = wrapLines(ctx, text, width);
      if ((lines.length <= maxLines && lines.length * sizes[i] * 1.08 <= budget) || i === sizes.length - 1) return { size: sizes[i], lines: lines };
    }
  }
  function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }
  /* The picture in the family sticker: an ink outline and a hard offset. */
  function drawSticker(ctx, img, x, y, w, h) {
    var r = 30;
    ctx.fillStyle = INK; roundRect(ctx, x + 12, y + 12, w, h, r); ctx.fill();
    ctx.fillStyle = '#fff'; roundRect(ctx, x, y, w, h, r); ctx.fill();
    if (img) {
      ctx.save(); roundRect(ctx, x, y, w, h, r); ctx.clip();
      var s = Math.max(w / img.naturalWidth, h / img.naturalHeight), iw = img.naturalWidth * s, ih = img.naturalHeight * s;
      ctx.drawImage(img, x + (w - iw) / 2, y + (h - ih) / 2, iw, ih);
      ctx.restore();
    }
    ctx.lineWidth = 4; ctx.strokeStyle = INK; roundRect(ctx, x, y, w, h, r); ctx.stroke();
  }
  function drawBrand(ctx, logo, x, y) {
    if (logo) ctx.drawImage(logo, x, y, 72, 72);
    ctx.fillStyle = INK; ctx.font = '700 38px ' + SANS;
    ctx.fillText('Adjie Brotot Blog', x + 92, y + 32);
    ctx.fillStyle = MUTED; ctx.font = '500 29px ' + SANS;
    ctx.fillText('blog.adjiebrotots.com', x + 92, y + 70);
  }
  function drawPoster(d, kind) {
    var story = kind === 'story', W = 1080, H = story ? 1920 : 1080, pad = story ? 90 : 72;
    var pic = posterPicture(d);
    return Promise.all([
      document.fonts ? Promise.all([document.fonts.load('800 80px "DM Sans"'), document.fonts.load('500 30px "DM Sans"'), document.fonts.load('600 60px Caveat')]).catch(function () {}) : null,
      pic ? loadImage(pic).catch(function () { return null; }) : null,
      loadImage(document.querySelector('.brand img').src).catch(function () { return null; })
    ]).then(function (got) {
      var img = got[1], logo = got[2];
      var c = document.createElement('canvas');
      c.width = W; c.height = H;
      var ctx = c.getContext('2d'), cw = W - pad * 2;
      ctx.fillStyle = BG; ctx.fillRect(0, 0, W, H);

      // The category, handwritten, then the title, from baseline-to-be `top`.
      function heading(top, catPx, sizes, max, budget) {
        ctx.save();
        ctx.translate(pad, top + Math.round(catPx * 0.8)); ctx.rotate(-2 * Math.PI / 180);
        ctx.fillStyle = GOLD; ctx.font = '600 ' + catPx + 'px Caveat, cursive';
        ctx.fillText(d.cat, 0, 0);
        ctx.restore();
        var t = fitTitle(ctx, d.title, cw, sizes, max, budget);
        var lh = Math.round(t.size * 1.08), y = top + Math.round(catPx * 1.35) + t.size;
        ctx.fillStyle = INK; ctx.font = '800 ' + t.size + 'px ' + SANS;
        // A title too long for the poster ends in an ellipsis on its last line.
        t.lines.slice(0, max).forEach(function (line, i) {
          if (i === max - 1 && t.lines.length > max) {
            while (line && ctx.measureText(line + '…').width > cw) line = line.replace(/\s*\S+$/, '');
            line += '…';
          }
          ctx.fillText(line, pad, y + i * lh);
        });
        return y + (Math.min(t.lines.length, max) - 1) * lh + Math.round(t.size * 0.3);
      }

      if (story) {
        // The picture and the title high up, the blog's name at the very
        // bottom, and the wide space between left blank for the reader's
        // link sticker or their own words.
        drawSticker(ctx, img, pad, 120, cw - 12, 480);
        heading(120 + 480 + 12 + 40, 56, [72, 66, 60, 54, 48], 4, 280);
        drawBrand(ctx, logo, pad, H - 64 - 72);
      } else {
        // The category and title, the picture, then an empty band for the
        // link above the blog's name.
        var textEnd = heading(pad, 54, [68, 62, 56, 50, 44], 3, 200);
        var brandY = H - pad - 72, imgTop = textEnd + 40;
        var imgH = Math.max(300, Math.min(brandY - 140 - imgTop, Math.round(cw * 0.6)));
        drawSticker(ctx, img, pad, imgTop, cw - 12, imgH);
        drawBrand(ctx, logo, pad, brandY);
      }
      return new Promise(function (resolve, reject) {
        c.toBlob(function (b) { if (b) resolve(b); else reject(new Error('poster')); }, 'image/png');
      });
    });
  }

  var overlay = document.querySelector('.poster-overlay');
  var poster = null, posterBack = null;
  function closePoster() {
    if (!overlay || overlay.hidden) return;
    overlay.hidden = true;
    if (poster && poster.href) URL.revokeObjectURL(poster.href);
    poster = null;
    if (posterBack) posterBack.focus({ preventScroll: true });
  }
  function openPoster(m, kind) {
    if (!overlay) return;
    var d = m.box.dataset, q = function (s) { return overlay.querySelector(s); };
    var frame = q('.poster-frame'), img = q('.poster-img'), share = q('.poster-share'), save = q('.poster-download');
    var job = poster = { kind: kind, url: d.url, title: d.title };
    posterBack = m.btn;
    q('#poster-title').textContent = q('#poster-title').dataset[kind];
    q('.poster-note').textContent = q('.poster-note').dataset[kind];
    img.hidden = true; img.removeAttribute('src');
    frame.classList.remove('is-failed'); frame.classList.add('is-making');
    share.hidden = true; save.classList.add('is-off'); save.removeAttribute('href');
    overlay.hidden = false;
    q('.poster-close').focus({ preventScroll: true });
    var slug = d.url.replace(/\/+$/, '').split('/').pop() || 'post';
    drawPoster(d, kind).then(function (blob) {
      if (poster !== job) return;
      job.file = new File([blob], slug + '-' + kind + '.png', { type: 'image/png' });
      job.href = URL.createObjectURL(blob);
      img.src = job.href; img.hidden = false;
      frame.classList.remove('is-making');
      save.href = job.href; save.download = job.file.name; save.classList.remove('is-off');
      share.hidden = !(navigator.canShare && navigator.canShare({ files: [job.file] }));
    }, function () {
      if (poster !== job) return;
      frame.classList.remove('is-making'); frame.classList.add('is-failed');
    });
  }
  if (overlay) {
    overlay.querySelector('.poster-close').addEventListener('click', closePoster);
    overlay.addEventListener('click', function (e) { if (e.target === overlay) closePoster(); });
    overlay.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { e.stopPropagation(); closePoster(); return; }
      if (e.key !== 'Tab') return;
      // Focus stays inside the dialog while it is open.
      var f = Array.prototype.filter.call(overlay.querySelectorAll('button, a[href]'), function (el) { return !el.hidden && el.offsetParent; });
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });
    overlay.querySelector('.poster-copy').addEventListener('click', function () {
      var b = this;
      if (!poster) return;
      copyText(poster.url).then(function () {
        if (b.__t) clearTimeout(b.__t); else b.__text = b.textContent;
        var label = document.querySelector('.share-menu');
        b.textContent = label ? label.dataset.copied : b.textContent;
        b.__t = setTimeout(function () { b.textContent = b.__text; b.__t = null; }, 1600);
      }, function () {});
    });
    overlay.querySelector('.poster-share').addEventListener('click', function () {
      if (!poster || !poster.file) return;
      // The link goes on the clipboard again, in case something replaced it.
      copyText(poster.url).catch(function () {});
      navigator.share({ files: [poster.file], title: poster.title }).catch(function () {});
    });
  }
})();

/* 9. Ads in the gaps of a card grid. A grid's last row is filled with in-feed
   tiles the size of a card, so the page ends square instead of on a lone card.
   The count follows the number of columns, so it is worked out again on a
   resize; a tile is pushed to AdSense the first time it is shown, and one that
   comes back unfilled is replaced by the next unit in `fill_units` (a tile
   waits invisible until it is filled, so nothing shows a bare box). A list
   never holds more ad tiles than posts. */
(function () {
  var d = document.body.dataset;
  if (!d.adUnits) return;
  var units;
  try { units = JSON.parse(d.adUnits); } catch (e) { return; }
  if (!units.length) return;

  function push() { try { (window.adsbygoogle = window.adsbygoogle || []).push({}); } catch (e) {} }
  function shown(el) { return getComputedStyle(el).display !== 'none'; }
  function isAd(el) { return el.classList.contains('ad-slot'); }
  function columns(grid) {
    return getComputedStyle(grid).gridTemplateColumns.split(' ').filter(function (c) { return c && c !== 'none'; }).length || 1;
  }
  function unfilled(aside) { var i = aside.querySelector('ins'); return i && i.getAttribute('data-ad-status') === 'unfilled'; }

  function makeTile(unit) {
    var aside = document.createElement('aside');
    aside.className = 'ad-slot ad-feed ad-fill';
    aside.setAttribute('aria-label', d.adLabel);
    aside.hidden = true;
    var label = document.createElement('p');
    label.className = 'ad-label';
    label.textContent = d.adLabel;
    var ins = document.createElement('ins');
    ins.className = 'adsbygoogle';
    ins.style.display = 'block';
    ins.dataset.adFormat = 'fluid';
    ins.dataset.adLayoutKey = unit.key;
    ins.dataset.adClient = d.adClient;
    ins.dataset.adSlot = unit.slot;
    aside.appendChild(label);
    aside.appendChild(ins);
    return aside;
  }

  // One list (a .post-grid, or a landing column) and its fillers.
  function Filler(list) {
    this.list = list;
    this.tiles = [];
    this.failed = 0;
    var self = this;
    new MutationObserver(function () { self.update(); })
      .observe(list, { subtree: true, attributes: true, attributeFilter: ['data-ad-status'] });
  }
  Filler.prototype.items = function () {
    return Array.prototype.filter.call(this.list.children, function (el) {
      return !el.classList.contains('ad-fill') && shown(el) && !(isAd(el) && unfilled(el));
    });
  };
  // Show `want` tiles at the end of the list, making new ones as needed.
  Filler.prototype.show = function (want) {
    var self = this;
    this.tiles = this.tiles.filter(function (t) {
      if (!unfilled(t)) return true;
      t.remove(); self.failed++;
      return false;
    });
    var posts = this.items().filter(function (el) { return !isAd(el); }).length;
    var ads = this.items().length - posts;
    want = Math.max(0, Math.min(want, posts - ads));
    // A tile left unfilled is replaced by the next unit; once each unit has
    // failed here, the gap stays.
    while (this.tiles.length < want && this.failed < units.length) {
      var t = makeTile(units[this.failed]);
      this.list.appendChild(t);
      this.tiles.push(t);
    }
    this.tiles.forEach(function (t, i) {
      var on = i < want;
      t.hidden = !on;
      if (on && !t.dataset.pushed) { t.dataset.pushed = '1'; push(); }
    });
  };
  // A post grid: the cells left empty in its last row.
  Filler.prototype.update = function () {
    if (this.busy) return;
    this.busy = true;
    var cols = columns(this.list), pos = 0;
    this.items().forEach(function (el) {
      pos = el.classList.contains('is-featured') ? 0 : (pos + 1) % cols;
    });
    this.show(cols > 1 && pos ? cols - pos : 0);
    this.busy = false;
  };

  var grids = Array.prototype.map.call(document.querySelectorAll('.post-grid'), function (g) { return new Filler(g); });

  // The landing page: two language columns side by side. The shorter gets the
  // multiplex unit when it is two or more cards short, one tile when it is one.
  var cols = document.querySelector('.landing-cols');
  var multiplex = document.querySelector('.ad-end[data-ad-defer]');
  var lists = cols ? Array.prototype.slice.call(cols.querySelectorAll('.post-list')) : [];
  if (lists.length === 2) {
    var fills = lists.map(function (l) { return new Filler(l); });
    var side = columns(cols) > 1;
    var count = function (f) { return f.items().length; };
    var short = count(fills[0]) < count(fills[1]) ? 0 : 1, gap = Math.abs(count(fills[0]) - count(fills[1]));
    if (side && gap >= 2 && multiplex) {
      fills[short].list.appendChild(multiplex);
      gap = 0;
    }
    fills.forEach(function (f, i) {
      f.update = function () {
        if (this.busy) return;
        this.busy = true;
        var other = count(fills[1 - i]);
        var two = columns(cols) > 1;
        this.show(two && this.list.contains(multiplex) ? 0 : two ? Math.min(1, Math.max(0, other - count(this))) : 0);
        this.busy = false;
      };
    });
    grids = grids.concat(fills);
  }
  if (multiplex) push();

  function all() { grids.forEach(function (g) { g.update(); }); }
  all();
  var t;
  window.addEventListener('resize', function () { clearTimeout(t); t = setTimeout(all, 150); });
})();
