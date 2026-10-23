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
})();
