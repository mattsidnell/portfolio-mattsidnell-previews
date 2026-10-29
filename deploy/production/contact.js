(() => {
  'use strict';
  const dialog = document.getElementById('contact-dialog');
  const form = document.getElementById('portfolio-contact-form');
  const status = document.getElementById('contact-status');
  const close = document.getElementById('contact-close');
  if (!dialog || !form || !status || !close) return;
  let previousFocus = null;
  const open = (event) => {
    if (event) event.preventDefault();
    previousFocus = event?.currentTarget || document.activeElement;
    const suggested = event?.currentTarget?.dataset?.contactTopic;
    const select = form.elements.namedItem('enquiry_type');
    if (select && suggested && [...select.options].some(option => option.value === suggested)) select.value = suggested;
    status.textContent = '';
    delete status.dataset.state;
    if (!dialog.open) dialog.showModal();
    document.body.classList.add('contact-open');
    form.elements.namedItem('name')?.focus();
  };
  const hide = () => {
    if (dialog.open) dialog.close();
    document.body.classList.remove('contact-open');
    if (previousFocus instanceof HTMLElement && previousFocus.isConnected) previousFocus.focus();
  };
  document.querySelectorAll('[data-contact-open]').forEach(link => link.addEventListener('click', open));
  close.addEventListener('click', hide);
  dialog.addEventListener('close', () => {
    document.body.classList.remove('contact-open');
    if (previousFocus instanceof HTMLElement && previousFocus.isConnected) previousFocus.focus();
  });
  dialog.addEventListener('click', event => {
    if (event.target === dialog) hide();
  });
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const button = form.querySelector('button[type=submit]');
    const data = Object.fromEntries(new FormData(form).entries());
    const payload = {
      name: String(data.name || '').trim(),
      email: String(data.email || '').trim(),
      company: String(data.company || '').trim(),
      enquiry_type: String(data.enquiry_type || ''),
      message: String(data.message || '').trim(),
      company_url: String(data.company_url || '')
    };
    if (payload.message.length < 10) {
      status.dataset.state = 'error';
      status.textContent = 'Please include a little more detail about the opportunity.';
      return;
    }
    button.disabled = true;
    button.querySelector('span').textContent = 'Sending…';
    status.textContent = '';
    delete status.dataset.state;
    try {
      const response = await fetch('/api/contact', {
        method: 'POST',
        mode: 'same-origin',
        credentials: 'omit',
        headers: {
          'Content-Type': 'application/json',
          'Idempotency-Key': crypto.randomUUID()
        },
        body: JSON.stringify(payload)
      });
      if (!response.ok) throw new Error('Request not accepted');
      const body = await response.json();
      if (!body || body.accepted !== true) throw new Error('Unexpected response');
      status.dataset.state = 'success';
      status.textContent = 'Thanks, your enquiry has been received. I’ll be in touch.';
      form.reset();
    } catch (_) {
      status.dataset.state = 'error';
      status.textContent = 'Your message could not be submitted. Please try again in a moment.';
    } finally {
      button.disabled = false;
      button.querySelector('span').textContent = 'Send enquiry';
    }
  });
})();
