/* Minimal first-party aggregate analytics. No cookies, IDs, fingerprints or external scripts. */
(() => {
  'use strict';
  const KEY = 'mattsidnell_analytics_opt_out';
  const projectHosts = Object.freeze({
    'grinders.golf': 'grinders',
    'lynehamflyingclub.com': 'lyneham-flying-club',
    'sidnell.uk': 'sidnell',
    'pixlwrk.com': 'pixlwrk',
    'pstructures.com': 'professional-structures',
    'webdesignerdirect.com': 'web-designer-direct',
    'digipixel.uk': 'digipixel',
    'sunnysideaccountancy.co.uk': 'sunnyside',
    'lpsgardenbuildings.co.uk': 'lps-garden-buildings'
  });
  let optedOutForPage = false;
  const optedOut = () => {
    if (optedOutForPage || navigator.globalPrivacyControl === true || navigator.doNotTrack === '1') return true;
    try { return localStorage.getItem(KEY) === '1'; } catch (_) { return false; }
  };
  const source = (() => {
    if (!document.referrer) return 'direct';
    try {
      const host = new URL(document.referrer).hostname.toLowerCase();
      if (host === location.hostname) return 'internal';
      if (/(^|\.)(google\.|bing\.|duckduckgo\.|yahoo\.|ecosia\.)/.test(host)) return 'search';
      if (/(^|\.)(linkedin\.|facebook\.|instagram\.|reddit\.|twitter\.|x\.com|t\.co|threads\.)/.test(host)) return 'social';
      return 'referral';
    } catch (_) { return 'direct'; }
  })();
  const track = (kind, target) => {
    window.portfolioGA4?.track(kind, target);
    // No requests to the private aggregate endpoint until the PHP release is live.
    if (window.PORTFOLIO_FIRST_PARTY_ANALYTICS_ENABLED !== true || optedOut()) return;
    try {
      fetch('/api/analytics', {
        method: 'POST', mode: 'same-origin', credentials: 'omit', keepalive: true,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ kind, target, source })
      }).catch(() => {});
    } catch (_) { /* Analytics must never affect the website. */ }
  };
  window.portfolioAnalytics = Object.freeze({ track });

  if (location.pathname === '/' || location.pathname === '/privacy.html') {
    track('pageview', location.pathname === '/' ? 'home' : 'privacy');
  }
  document.addEventListener('click', event => {
    const trigger = event.target.closest?.('a[href]');
    if (trigger) {
      try {
        const url = new URL(trigger.href);
        const host = url.hostname.replace(/^www\./, '').toLowerCase();
        if (projectHosts[host]) track('project_click', projectHosts[host]);
      } catch (_) { /* Ignore malformed links. */ }
    }
    if (event.target.closest?.('[data-contact-open]')) track('contact_open', 'form');
  }, { passive: true });

  const control = document.getElementById('analytics-preference');
  if (control) {
    const render = () => { control.textContent = optedOut() ? 'Enable anonymous site statistics' : 'Disable anonymous site statistics'; };
    control.addEventListener('click', () => {
      const stop = !optedOut();
      optedOutForPage = stop;
      try { localStorage.setItem(KEY, stop ? '1' : '0'); } catch (_) { /* Applies for this page. */ }
      if (!stop) optedOutForPage = false;
      render();
    });
    render();
  }
})();
