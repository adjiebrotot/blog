/* Adjie Brotot Blog: the only script on the page.
   1. The theme button: flips light / dark and remembers the pick.
   2. Charts embedded from tool.adjiebrotots.com follow the blog's theme. Their
      link names a theme (#embed=…&theme=light); the tool reads it once when
      the frame loads, so a frame in the wrong theme is swapped for a fresh one.
   3. kramdown's {:toc} list gets its heading in the page's language. */
(function () {
  var root = document.documentElement;

  function theme() { return root.classList.contains('light') ? 'light' : 'dark'; }

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

  var btn = document.getElementById('themeToggle');
  if (btn) btn.addEventListener('click', function () {
    var next = theme() === 'light' ? 'dark' : 'light';
    root.classList.remove('light', 'dark');
    root.classList.add(next);
    try { localStorage.setItem('blog-theme', next); } catch (e) {}
    syncEmbeds();
  });

  syncEmbeds();

  var toc = document.getElementById('markdown-toc');
  if (toc) toc.setAttribute('data-title', root.lang === 'id' ? 'Daftar isi' : 'Contents');
})();
