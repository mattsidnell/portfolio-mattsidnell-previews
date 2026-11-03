/* Basic consent mode: no Google script or network traffic until the visitor opts in. */
(() => {
  'use strict';
  const id = String(window.PORTFOLIO_GA4_ID || '').trim();
  if (!/^G-[A-Z0-9]{6,20}$/.test(id)) return;
  const KEY = 'mattsidnell_ga4_consent_v1';
  const get = () => { try { return localStorage.getItem(KEY); } catch (_) { return null; } };
  const put = value => { try { localStorage.setItem(KEY, value); } catch (_) {} };
  const defaults = {
    ad_storage: 'denied', ad_user_data: 'denied',
    ad_personalization: 'denied', analytics_storage: 'denied'
  };
  let enabled = false;
  let started = false;
  function gtag() { window.dataLayer.push(arguments); }
  function start() {
    if (started) {
      window.gtag('consent', 'update', Object.assign({}, defaults, {analytics_storage: 'granted'}));
      enabled = true;
      return;
    }
    started = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = gtag;
    gtag('consent', 'default', defaults);
    gtag('consent', 'update', Object.assign({}, defaults, {analytics_storage: 'granted'}));
    gtag('js', new Date());
    gtag('config', id, {send_page_view:true, allow_google_signals:false});
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id);
    document.head.appendChild(script);
    enabled = true;
  }
  function clearCookies() {
    const host = location.hostname.replace(/^www\./, '');
    for (const part of document.cookie.split(';')) {
      const name = part.trim().split('=')[0];
      if (!/^_ga(?:_|$)/.test(name)) continue;
      for (const domain of ['', '; domain=' + host, '; domain=.' + host]) {
        document.cookie = name + '=; Max-Age=0; path=/' + domain + '; SameSite=Lax';
      }
    }
  }
  function render() {
    const banner = document.getElementById('ga4-consent');
    if (banner) banner.hidden = get() !== null;
    const btn = document.getElementById('ga4-preference');
    if (btn) btn.textContent = get() === 'granted' ? 'Turn off Google Analytics' : 'Allow Google Analytics';
  }
  function allow() {
    put('granted');
    start();
    render();
  }
  function reject() {
    put('denied');
    enabled = false;
    if (typeof window.gtag === 'function') window.gtag('consent', 'update', defaults);
    clearCookies();
    render();
  }
  if (get() === 'granted' && navigator.globalPrivacyControl !== true && navigator.doNotTrack !== '1') start();
  function setup() {
    if (get() === null) {
      const banner = document.createElement('aside');
      banner.id = 'ga4-consent';
      banner.setAttribute('role', 'region');
      banner.setAttribute('aria-label', 'Optional Google Analytics');
      banner.innerHTML = '<p>May I use Google Analytics to understand portfolio visits? ' +
        'This is optional and stays off unless you allow it. ' +
        '<a href="/privacy.html">Privacy details</a>.</p>' +
        '<div><button type="button" data-ga4-reject>Decline</button>' +
        '<button type="button" data-ga4-accept>Allow analytics</button></div>';
      document.body.appendChild(banner);
      banner.querySelector('[data-ga4-reject]').addEventListener('click', reject);
      banner.querySelector('[data-ga4-accept]').addEventListener('click', allow);
    }
    document.getElementById('ga4-preference')?.addEventListener('click', () => get() === 'granted' ? reject() : allow());
    render();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', setup, {once:true});
  else setup();
  window.portfolioGA4 = Object.freeze({
    track(kind, target) {
      if (!enabled || get() !== 'granted' || typeof window.gtag !== 'function') return;
      if (kind === 'project_click') window.gtag('event','select_content',{content_type:'portfolio_project',item_id:target});
      if (kind === 'contact_open') window.gtag('event','contact_form_open');
      if (kind === 'enquiry_saved') window.gtag('event','generate_lead',{method:'contact_form'});
    }
  });
})();
