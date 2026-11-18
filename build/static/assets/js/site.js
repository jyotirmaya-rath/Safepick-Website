/*
 * SafePick website: store links.
 * On launch day, paste each store address between the quotes and save.
 * While they are empty the buttons say "Coming soon"; once filled they become download buttons on every page.
 */
const SITE_LINKS = {
  appStore: '',    // e.g. 'https://apps.apple.com/ca/app/safepick/id0000000000'
  googlePlay: '',  // e.g. 'https://play.google.com/store/apps/details?id=com.safepick.app'
};

(function () {
  'use strict';

  // Store buttons: "Coming soon" until a link is filled in above
  var anyLive = false;
  document.querySelectorAll('[data-store]').forEach(function (a) {
    var url = SITE_LINKS[a.getAttribute('data-store')];
    if (!url) return;
    anyLive = true;
    a.href = url;
    a.target = '_blank';
    a.rel = 'noopener';
    a.classList.remove('is-soon');
    a.removeAttribute('aria-disabled');
    var small = a.querySelector('small[data-live]');
    if (small) small.textContent = small.getAttribute('data-live');
  });
  if (anyLive) {
    document.querySelectorAll('[data-when="soon"]').forEach(function (el) { el.hidden = true; });
    document.querySelectorAll('[data-when="live"]').forEach(function (el) { el.hidden = false; });
  }

  // Tabs: one section of the page at a time. Each tab is a link to its section, so the address can be shared.
  document.querySelectorAll('[data-tabs]').forEach(function (box) {
    var list = box.querySelector('.tablist');
    var tabs = Array.prototype.slice.call(box.querySelectorAll('.tab'));
    var panels = tabs.map(function (t) { return document.getElementById(t.getAttribute('data-panel')); });
    if (!list || !tabs.length || panels.indexOf(null) !== -1) return;

    list.setAttribute('role', 'tablist');
    tabs.forEach(function (t, i) {
      t.setAttribute('role', 'tab');
      t.id = 'tab-' + panels[i].id;
      t.setAttribute('aria-controls', panels[i].id);
      panels[i].setAttribute('role', 'tabpanel');
      panels[i].setAttribute('aria-labelledby', t.id);
      panels[i].removeAttribute('aria-label');
    });

    function select(i, opts) {
      opts = opts || {};
      tabs.forEach(function (t, k) {
        var on = k === i;
        t.classList.toggle('is-active', on);
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        panels[k].classList.toggle('is-active', on);
      });
      if (opts.focus) tabs[i].focus();
      if (opts.address && window.history && history.replaceState) history.replaceState(null, '', '#' + panels[i].id);
      var tab = tabs[i];
      if (list.scrollWidth > list.clientWidth) list.scrollLeft = tab.offsetLeft - (list.clientWidth - tab.offsetWidth) / 2;
    }

    function fromAddress(scroll) {
      var id = decodeURIComponent(location.hash.slice(1));
      if (!id) return false;
      var el = document.getElementById(id);
      var panel = el && el.closest ? el.closest('.tabpanel') : null;
      var i = panels.indexOf(panel);
      if (i === -1) return false;
      select(i);
      if (scroll) (el === panel ? box : el).scrollIntoView();
      return true;
    }

    tabs.forEach(function (t, i) {
      t.addEventListener('click', function (e) { e.preventDefault(); select(i, { address: true }); });
      t.addEventListener('keydown', function (e) {
        var to = e.key === 'ArrowRight' ? i + 1 : e.key === 'ArrowLeft' ? i - 1 : e.key === 'Home' ? 0 : e.key === 'End' ? tabs.length - 1 : null;
        if (to === null) return;
        e.preventDefault();
        select((to + tabs.length) % tabs.length, { focus: true, address: true });
      });
    });

    box.classList.add('is-on');
    if (!fromAddress(true)) select(0);
    window.addEventListener('hashchange', function () { fromAddress(true); });
    // a link elsewhere on the page that points into a tab (the address may not change, so listen for the click too)
    document.addEventListener('click', function (e) {
      var a = e.target.closest ? e.target.closest('a[href^="#"]') : null;
      if (!a || a.classList.contains('tab')) return;
      setTimeout(function () { fromAddress(true); }, 0);
    });
  });

  // Carousels: a row that slides sideways, with arrows, dots and swipe. Without JavaScript the row still scrolls.
  var reduceMotion = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  var ARROW = '<svg aria-hidden="true" viewBox="0 0 24 24"><path d="m9 5 7 7-7 7" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  document.querySelectorAll('[data-carousel]').forEach(function (box) {
    var track = box.querySelector('[data-track]');
    if (!track) return;
    box.setAttribute('role', 'region');
    box.setAttribute('aria-roledescription', 'carousel');
    box.setAttribute('aria-label', box.getAttribute('data-label') || 'Carousel');
    track.tabIndex = 0;

    function button(cls, text) {
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'c-btn ' + cls; b.setAttribute('aria-label', text); b.innerHTML = ARROW;
      return b;
    }
    var ui = document.createElement('div'); ui.className = 'carousel-ui'; ui.hidden = true;
    var prev = button('prev', 'Previous'), next = button('next', 'Next');
    var dots = document.createElement('div'); dots.className = 'c-dots';
    var count = document.createElement('span'); count.className = 'c-count';
    ui.appendChild(prev); ui.appendChild(dots); ui.appendChild(count); ui.appendChild(next);
    box.appendChild(ui);

    var total = 1, stopped = false, hold = false, seen = true, pause = null;
    function max() { return track.scrollWidth - track.clientWidth; }
    function gap() { return parseFloat(getComputedStyle(track).columnGap) || 0; }
    function page() { return track.clientWidth + gap(); }      // one screenful, including the space after it
    function current() {
      if (!track.clientWidth) return 0;
      if (track.scrollLeft >= max() - 2) return total - 1;
      return Math.min(total - 1, Math.round(track.scrollLeft / page()));
    }
    function go(i) {
      i = (i + total) % total;
      track.scrollTo({ left: Math.min(i * page(), max()), behavior: reduceMotion ? 'auto' : 'smooth' });
    }
    function paint() {
      var c = current();
      Array.prototype.forEach.call(dots.children, function (d, k) { d.setAttribute('aria-current', String(k === c)); });
      count.textContent = (c + 1) + ' / ' + total;
    }
    function stop() {
      stopped = true;
      if (pause) { pause.textContent = 'Play'; pause.setAttribute('aria-label', 'Play the slides'); }
    }
    function measure() {
      var w = track.clientWidth;
      var n = w ? Math.max(1, Math.ceil((track.scrollWidth + gap() - 4) / page())) : 1;
      if (n !== total || !dots.children.length) {
        total = n;
        dots.innerHTML = '';
        if (total <= 8) {
          for (var k = 0; k < total; k++) {
            (function (k) {
              var d = document.createElement('button');
              d.type = 'button'; d.className = 'c-dot'; d.setAttribute('aria-label', 'Go to ' + (k + 1) + ' of ' + total);
              d.addEventListener('click', function () { stop(); go(k); });
              dots.appendChild(d);
            })(k);
          }
        }
      }
      ui.hidden = total <= 1;
      count.hidden = total <= 8;      // a counter replaces the dots when there would be too many
      paint();
    }
    prev.addEventListener('click', function () { stop(); go(current() - 1); });
    next.addEventListener('click', function () { stop(); go(current() + 1); });
    var frame = 0;
    track.addEventListener('scroll', function () {
      if (frame) return;
      frame = requestAnimationFrame(function () { frame = 0; paint(); });
    }, { passive: true });
    if (window.ResizeObserver) new ResizeObserver(measure).observe(track);
    window.addEventListener('resize', measure);
    measure();

    // Moves on by itself only where asked (data-autoplay), never for people who prefer reduced motion.
    // It waits while the pointer or keyboard is on it, and stops for good once the person takes over.
    var every = parseInt(box.getAttribute('data-autoplay') || '0', 10);
    if (every && !reduceMotion) {
      pause = document.createElement('button');
      pause.type = 'button'; pause.className = 'c-pause'; pause.textContent = 'Pause'; pause.setAttribute('aria-label', 'Pause the slides');
      pause.addEventListener('click', function () {
        if (stopped) { stopped = false; pause.textContent = 'Pause'; pause.setAttribute('aria-label', 'Pause the slides'); } else stop();
      });
      ui.appendChild(pause);
      box.addEventListener('mouseenter', function () { hold = true; });
      box.addEventListener('mouseleave', function () { hold = false; });
      box.addEventListener('focusin', function () { hold = true; });
      box.addEventListener('focusout', function () { hold = false; });
      track.addEventListener('touchstart', stop, { passive: true });
      track.addEventListener('wheel', stop, { passive: true });
      if (window.IntersectionObserver) new IntersectionObserver(function (e) { seen = e[0].isIntersecting; }, { threshold: 0.4 }).observe(box);
      setInterval(function () { if (!stopped && !hold && seen && !document.hidden && total > 1) go(current() + 1); }, every);
    }
  });

  // Header border once the page scrolls
  var header = document.querySelector('.site-header');
  function onScroll() { if (header) header.classList.toggle('scrolled', window.scrollY > 8); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Phone-width menu
  var btn = document.getElementById('menu-btn');
  var nav = document.getElementById('site-nav');
  if (btn && nav) {
    var setOpen = function (open) {
      nav.classList.toggle('open', open);
      btn.setAttribute('aria-expanded', String(open));
      btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    };
    btn.addEventListener('click', function () { setOpen(!nav.classList.contains('open')); });
    nav.addEventListener('click', function (e) { if (e.target.closest('a')) setOpen(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setOpen(false); });
  }
})();
