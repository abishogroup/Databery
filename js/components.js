/* =========================================================
   DATABERY — Shared header & footer (single source of truth)
   Injects the branded nav (with Services mega-menu) and footer
   into #site-header / #site-footer on every page.
   ========================================================= */
(function () {
  'use strict';

  /* ---- Logo mark (echoes the Databery berry-node logo) ---- */
  var LOGO =
    '<svg class="brand-mark" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' +
    '<defs><linearGradient id="dbg" x1="8" y1="42" x2="40" y2="8" gradientUnits="userSpaceOnUse">' +
    '<stop stop-color="#1c1b4e"/><stop offset=".5" stop-color="#6324c4"/><stop offset="1" stop-color="#3f5efb"/></linearGradient></defs>' +
    '<path d="M23 13c-1-3 0-6 2-8" stroke="#1c1b4e" stroke-width="2" stroke-linecap="round"/>' +
    '<path d="M26 12c1.5-4.5 6-6.5 10-5.5.4 4-2 8.5-6.5 9.6-1.8.4-3-.5-3.5-1.6z" fill="url(#dbg)"/>' +
    '<g stroke="url(#dbg)" stroke-width="1.4" opacity=".5"><path d="M16 18 24 16M16 18 12 26M24 16 28 24M12 26 20 30M28 24 20 30M20 30 16 38M16 38 26 36M28 24 26 36"/></g>' +
    '<g fill="url(#dbg)"><circle cx="16" cy="18" r="3"/><circle cx="24" cy="16" r="3.4"/><circle cx="12" cy="26" r="3.6"/>' +
    '<circle cx="28" cy="24" r="3"/><circle cx="20" cy="30" r="4"/><circle cx="16" cy="38" r="3.4"/><circle cx="26" cy="36" r="3"/></g>' +
    '<g fill="#3f5efb"><circle cx="34" cy="20" r="1.7"/><circle cx="37.5" cy="26" r="2"/><circle cx="34.5" cy="32" r="1.6"/>' +
    '<circle cx="31" cy="38" r="1.3"/><circle cx="38.5" cy="33" r="1.1"/></g></svg>';

  var BRAND =
    '<a href="index.html" class="brand">' + LOGO +
    '<span class="brand-text"><span class="t-ink">Data</span><span class="t-grad">bery</span></span></a>';

  var ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M13 6l6 6-6 6"/></svg>';
  var CARET = '<svg class="caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg>';

  /* ---- Service registry (drives mega-menu + footer) ---- */
  var SERVICES = [
    { slug: 'account-intelligence',            name: 'Account Intelligence',            blurb: 'Intent-scored target accounts, signal-rich and ready for outreach.', icon: '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3.4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/>' },
    { slug: 'pipeline-signal-monitoring',      name: 'Pipeline Signal Monitoring',      blurb: 'Ongoing buying-trigger monitoring across your account list.',         icon: '<path d="M3 12h4l2-6 4 12 2-6h6"/>' },
    { slug: 'competitive-intelligence',        name: 'Competitive Intelligence',        blurb: 'A living view of your top 3–5 competitors and their gaps.',           icon: '<path d="M12 2 4 6v6c0 5 3.5 8 8 10 4.5-2 8-5 8-10V6Z"/><path d="m9 12 2 2 4-4"/>' },
    { slug: 'stakeholder-executive-intelligence', name: 'Stakeholder & Executive Intel', blurb: 'Profiles of the people you must influence to win the deal.',         icon: '<path d="M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z"/><path d="M4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1"/>' },
    { slug: 'gtm-research',                    name: 'Go-To-Market Research',           blurb: 'A research-backed foundation for a new market or vertical.',          icon: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>' },
    { slug: 'win-loss-intelligence',           name: 'Win-Loss Intelligence',           blurb: 'Why you really won or lost — and what to change next time.',          icon: '<path d="M7 4h10v4a5 5 0 0 1-10 0V4Z"/><path d="M7 6H4v1a3 3 0 0 0 3 3M17 6h3v1a3 3 0 0 1-3 3M9 18h6M10 14v4M14 14v4"/>' },
    { slug: 'battlecard-research',             name: 'Battlecard Research',             blurb: 'Live intelligence that powers your sales battlecards.',              icon: '<path d="M12 3 3 8l9 5 9-5-9-5Z"/><path d="m3 12 9 5 9-5M3 16l9 5 9-5"/>' }
  ];

  function svc(s) {
    return '<a class="mega-link" href="service-' + s.slug + '.html">' +
      '<span class="mega-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7">' + s.icon + '</svg></span>' +
      '<span><strong>' + s.name + '</strong><em>' + s.blurb + '</em></span></a>';
  }

  var page = (document.body.getAttribute('data-page') || '').toLowerCase();
  function on(p) { return page === p ? ' active' : ''; }

  /* ---- Header ---- */
  var header =
    '<header class="nav">' +
      '<div class="container nav-inner">' +
        BRAND +
        '<nav class="nav-links">' +
          '<div class="nav-item has-mega' + on('services') + '">' +
            '<a href="services.html" class="mega-trigger">Services ' + CARET + '</a>' +
            '<div class="mega">' +
              SERVICES.map(svc).join('') +
              '<a class="mega-cta" href="services.html"><div><strong>The full intelligence suite</strong>' +
                '<span>See how the seven services work together</span></div>' +
                '<span class="go">Explore all ' + ARROW + '</span></a>' +
            '</div>' +
          '</div>' +
          '<a href="why.html" class="' + (on('why') ? 'active' : '') + '">Why us</a>' +
          '<a href="process.html" class="' + (on('process') ? 'active' : '') + '">Process</a>' +
          '<a href="contact.html" class="' + (on('contact') ? 'active' : '') + '">Contact</a>' +
        '</nav>' +
        '<div class="nav-cta"><a href="contact.html" class="btn btn-primary" data-magnetic>Book a call ' + ARROW + '</a></div>' +
        '<button class="nav-toggle" aria-label="Menu"><span></span><span></span></button>' +
      '</div>' +
    '</header>';

  /* ---- Footer ---- */
  var footYear = new Date().getFullYear();
  var footServices = SERVICES.slice(0, 5).map(function (s) {
    return '<li><a href="service-' + s.slug + '.html">' + s.name + '</a></li>';
  }).join('');

  var footer =
    '<footer class="footer"><div class="container">' +
      '<div class="footer-top">' +
        '<div>' + BRAND +
          '<p class="about">Account &amp; sales intelligence that turns target lists into closed revenue — researched account by account.</p>' +
          '<div class="tagline-chip" style="margin-top:22px"><b>Insights</b> · <b>Intelligence</b> · <b>Impact</b></div>' +
        '</div>' +
        '<div><h5>Services</h5><ul>' + footServices +
          '<li><a href="services.html">All services</a></li></ul></div>' +
        '<div><h5>Company</h5><ul>' +
          '<li><a href="why.html">Why Databery</a></li>' +
          '<li><a href="process.html">Our process</a></li>' +
          '<li><a href="contact.html">Contact</a></li></ul></div>' +
        '<div><h5>Get in touch</h5><ul>' +
          '<li><a href="mailto:hello@databery.com">hello@databery.com</a></li>' +
          '<li><a href="tel:+10000000000">+1 (000) 000-0000</a></li>' +
          '<li><a href="contact.html">Book a call</a></li></ul></div>' +
      '</div>' +
      '<div class="footer-bottom">' +
        '<span>© ' + footYear + ' Databery. All rights reserved.</span>' +
        '<div class="socials">' +
          '<a href="#" aria-label="LinkedIn"><svg viewBox="0 0 24 24" width="16" fill="currentColor"><path d="M4.98 3.5A2.5 2.5 0 1 1 0 3.5a2.5 2.5 0 0 1 4.98 0ZM.5 8h4V24h-4V8Zm7 0h3.8v2.2h.05c.53-1 1.83-2.2 3.77-2.2 4 0 4.8 2.65 4.8 6.1V24h-4v-6.9c0-1.65-.03-3.77-2.3-3.77-2.3 0-2.65 1.8-2.65 3.65V24h-4V8Z"/></svg></a>' +
          '<a href="#" aria-label="X"><svg viewBox="0 0 24 24" width="15" fill="currentColor"><path d="M18.9 2H22l-7.1 8.1L23.2 22h-6.6l-5.2-6.8L5.5 22H2.4l7.6-8.7L1.2 2h6.7l4.7 6.2L18.9 2Zm-1.1 18h1.8L7.3 3.9H5.4L17.8 20Z"/></svg></a>' +
          '<a href="#" aria-label="Email"><svg viewBox="0 0 24 24" width="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 6 10 7 10-7"/></svg></a>' +
        '</div>' +
      '</div>' +
    '</div></footer>';

  var h = document.getElementById('site-header');
  var f = document.getElementById('site-footer');
  if (h) h.innerHTML = header;
  if (f) f.innerHTML = footer;
})();
