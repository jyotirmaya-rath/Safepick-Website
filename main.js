/*
 * SafePick website: links to fill in.
 * Paste each web address between the quotes and save. Empty ones stay as they are now
 * (store buttons scroll to the download section; Terms and Contact are hidden).
 */
const SITE_LINKS = {
  appStore: '',      // e.g. 'https://apps.apple.com/ca/app/safepick/id0000000000'
  googlePlay: '',    // e.g. 'https://play.google.com/store/apps/details?id=com.safepick.app'
  privacy: '',       // the hosted privacy policy page
  terms: '',         // the hosted terms page
  contactEmail: '',  // e.g. 'hello@safepick.app'
};

(function () {
  'use strict';

  // Store buttons
  document.querySelectorAll('[data-store]').forEach(function (a) {
    var url = SITE_LINKS[a.getAttribute('data-store')];
    if (url) {
      a.href = url;
      a.target = '_blank';
      a.rel = 'noopener';
    }
  });

  // Footer links
  var footer = {
    privacy: SITE_LINKS.privacy,
    terms: SITE_LINKS.terms,
    contact: SITE_LINKS.contactEmail ? 'mailto:' + SITE_LINKS.contactEmail : '',
  };
  document.querySelectorAll('[data-link]').forEach(function (a) {
    var key = a.getAttribute('data-link');
    if (footer[key]) {
      a.href = footer[key];
      if (key !== 'contact') { a.target = '_blank'; a.rel = 'noopener'; }
    } else if (key !== 'privacy') {
      a.hidden = true;
    }
  });

  // Year
  var year = document.getElementById('year');
  if (year) year.textContent = String(new Date().getFullYear());

  // Header border once the page scrolls
  var header = document.querySelector('.site-header');
  function onScroll() { if (header) header.classList.toggle('scrolled', window.scrollY > 8); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Phone-width menu
  var btn = document.getElementById('menu-btn');
  var nav = document.getElementById('site-nav');
  if (btn && nav) {
    function setOpen(open) {
      nav.classList.toggle('open', open);
      btn.setAttribute('aria-expanded', String(open));
      btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    }
    btn.addEventListener('click', function () { setOpen(!nav.classList.contains('open')); });
    nav.addEventListener('click', function (e) { if (e.target.closest('a')) setOpen(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setOpen(false); });
  }
})();
