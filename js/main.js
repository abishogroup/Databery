/* =========================================================
   DATABERY — Interactions
   ========================================================= */
(function () {
  'use strict';

  /* ---- Nav: scroll state + mobile toggle ---- */
  const nav = document.querySelector('.nav');
  const toggle = document.querySelector('.nav-toggle');
  const links = document.querySelector('.nav-links');

  const onScroll = () => {
    if (nav) nav.classList.toggle('scrolled', window.scrollY > 24);
    // scroll progress bar
    const bar = document.querySelector('.scroll-bar');
    if (bar) {
      const h = document.documentElement;
      const p = h.scrollTop / (h.scrollHeight - h.clientHeight);
      bar.style.width = (p * 100) + '%';
    }
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  if (toggle && links) {
    toggle.addEventListener('click', () => {
      const isOpen = links.classList.toggle('open');
      toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });
    // close mobile menu when a real link is tapped (but not a dropdown parent on mobile)
    links.querySelectorAll('a').forEach(a =>
      a.addEventListener('click', (e) => {
        if ((a.classList.contains('mega-trigger') || a.classList.contains('dropdown-trigger')) &&
            window.matchMedia('(max-width: 860px)').matches) return;
        links.classList.remove('open');
      })
    );
  }

  /* ---- Nav dropdowns/mega: expand on tap (mobile only) ---- */
  document.querySelectorAll('.nav-item .mega-trigger, .nav-item .dropdown-trigger').forEach(trigger => {
    trigger.addEventListener('click', (e) => {
      if (window.matchMedia('(max-width: 860px)').matches) {
        e.preventDefault();
        const item = trigger.closest('.nav-item');
        const wasOpen = item.classList.contains('open');
        document.querySelectorAll('.nav-item.open').forEach(i => i.classList.remove('open'));
        if (!wasOpen) item.classList.add('open');
      }
    });
  });

  /* ---- Blog: search + category filter + pagination ---- */
  const blog = document.querySelector('#blog-list');
  if (blog) {
    const cards = Array.from(blog.querySelectorAll('.post-card'));
    const search = document.querySelector('#blog-search');
    const chips = Array.from(document.querySelectorAll('.cat-chips .chip'));
    const countEl = document.querySelector('#blog-count');
    const empty = document.querySelector('#blog-empty');
    const pager = document.querySelector('#blog-pagination');
    const PER = 10;
    let cat = 'all', page = 1;

    const filtered = () => {
      const q = (search ? search.value : '').trim().toLowerCase();
      return cards.filter(c => {
        const text = (c.dataset.title + ' ' + c.dataset.cat + ' ' + (c.dataset.tags || '')).toLowerCase();
        return (cat === 'all' || c.dataset.cat === cat) && (!q || text.includes(q));
      });
    };

    const renderPager = (pages) => {
      if (!pager) return;
      pager.innerHTML = '';
      if (pages <= 1) return;
      const mk = (label, p, opt) => {
        const b = document.createElement('button');
        b.type = 'button'; b.textContent = label;
        if (opt && opt.active) b.classList.add('active');
        if (opt && opt.disabled) b.disabled = true;
        b.addEventListener('click', () => { page = p; render(); blog.scrollIntoView({ behavior: 'smooth', block: 'start' }); });
        return b;
      };
      pager.appendChild(mk('‹', page - 1, { disabled: page <= 1 }));
      for (let p = 1; p <= pages; p++) pager.appendChild(mk(String(p), p, { active: p === page }));
      pager.appendChild(mk('›', page + 1, { disabled: page >= pages }));
    };

    const render = () => {
      const list = filtered();
      const pages = Math.ceil(list.length / PER) || 1;
      if (page > pages) page = pages;
      cards.forEach(c => { c.hidden = true; });
      list.forEach((c, idx) => { if (Math.floor(idx / PER) + 1 === page) c.hidden = false; });
      if (countEl) countEl.textContent = list.length + (list.length === 1 ? ' article' : ' articles');
      if (empty) empty.classList.toggle('show', list.length === 0);
      renderPager(pages);
    };

    if (search) search.addEventListener('input', () => { page = 1; render(); });
    chips.forEach(ch => ch.addEventListener('click', () => {
      chips.forEach(x => x.classList.remove('active'));
      ch.classList.add('active');
      cat = ch.dataset.cat; page = 1; render();
    }));
    render();
  }

  /* ---- Custom cursor ---- */
  const dot = document.querySelector('.cursor-dot');
  const ring = document.querySelector('.cursor-ring');
  if (dot && ring && window.matchMedia('(pointer:fine)').matches) {
    let rx = 0, ry = 0, x = 0, y = 0;
    document.addEventListener('mousemove', (e) => {
      x = e.clientX; y = e.clientY;
      dot.style.transform = `translate(${x}px, ${y}px) translate(-50%,-50%)`;
    });
    const loop = () => {
      rx += (x - rx) * 0.18;
      ry += (y - ry) * 0.18;
      ring.style.transform = `translate(${rx}px, ${ry}px) translate(-50%,-50%)`;
      requestAnimationFrame(loop);
    };
    loop();
    const hoverables = 'a, button, .service-card, .info-item, input, textarea, select, .faq-q';
    document.querySelectorAll(hoverables).forEach(el => {
      el.addEventListener('mouseenter', () => ring.classList.add('is-hover'));
      el.addEventListener('mouseleave', () => ring.classList.remove('is-hover'));
    });
  }

  /* ---- Reveal on scroll ---- */
  const io = new IntersectionObserver((entries) => {
    entries.forEach(en => {
      if (en.isIntersecting) {
        en.target.classList.add('in');
        io.unobserve(en.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
  document.querySelectorAll('.reveal').forEach(el => io.observe(el));

  /* ---- Count-up stats ---- */
  const counters = document.querySelectorAll('[data-count]');
  const cio = new IntersectionObserver((entries) => {
    entries.forEach(en => {
      if (!en.isIntersecting) return;
      const el = en.target;
      const target = parseFloat(el.dataset.count);
      const suffix = el.dataset.suffix || '';
      const dec = (target % 1 !== 0) ? 1 : 0;
      let start = 0;
      const dur = 1600;
      const t0 = performance.now();
      const tick = (now) => {
        const p = Math.min((now - t0) / dur, 1);
        const eased = 1 - Math.pow(1 - p, 3);
        el.textContent = (eased * target).toFixed(dec) + suffix;
        if (p < 1) requestAnimationFrame(tick);
        else el.textContent = target.toFixed(dec) + suffix;
      };
      requestAnimationFrame(tick);
      cio.unobserve(el);
    });
  }, { threshold: 0.5 });
  counters.forEach(c => cio.observe(c));

  /* ---- Service card cursor glow ---- */
  document.querySelectorAll('.service-card').forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const r = card.getBoundingClientRect();
      card.style.setProperty('--mx', ((e.clientX - r.left) / r.width * 100) + '%');
      card.style.setProperty('--my', ((e.clientY - r.top) / r.height * 100) + '%');
    });
  });

  /* ---- Magnetic buttons ---- */
  if (window.matchMedia('(pointer:fine)').matches) {
    document.querySelectorAll('[data-magnetic]').forEach(btn => {
      btn.addEventListener('mousemove', (e) => {
        const r = btn.getBoundingClientRect();
        const mx = e.clientX - r.left - r.width / 2;
        const my = e.clientY - r.top - r.height / 2;
        btn.style.transform = `translate(${mx * 0.25}px, ${my * 0.35}px)`;
      });
      btn.addEventListener('mouseleave', () => { btn.style.transform = ''; });
    });
  }

  /* ---- FAQ accordion (contact page) ---- */
  document.querySelectorAll('.faq-item').forEach(item => {
    const q = item.querySelector('.faq-q');
    const a = item.querySelector('.faq-a');
    q.addEventListener('click', () => {
      const open = item.classList.contains('open');
      document.querySelectorAll('.faq-item').forEach(i => {
        i.classList.remove('open');
        i.querySelector('.faq-a').style.maxHeight = null;
      });
      if (!open) {
        item.classList.add('open');
        a.style.maxHeight = a.scrollHeight + 'px';
      }
    });
  });

  /* ---- Web3Forms submission (shared) ---- */
  const WEB3FORMS_URL = 'https://api.web3forms.com/submit';

  function setMsg(el, kind, text) {
    if (!el) return;
    el.classList.remove('is-error', 'is-ok');
    if (text) { el.classList.add(kind === 'ok' ? 'is-ok' : 'is-error'); el.textContent = text; }
    else { el.textContent = ''; }
  }

  function submitWeb3Form(formEl, opts) {
    // client-side validation of required fields (native UI)
    if (typeof formEl.reportValidity === 'function' && !formEl.checkValidity()) {
      formEl.reportValidity();
      return;
    }
    const btn = formEl.querySelector('button[type="submit"]');
    const label = btn ? btn.innerHTML : '';
    if (btn) { btn.disabled = true; btn.dataset.busy = '1'; btn.innerHTML = 'Sending…'; }
    setMsg(opts.statusEl, 'ok', '');

    fetch(WEB3FORMS_URL, {
      method: 'POST',
      headers: { 'Accept': 'application/json' },
      body: new FormData(formEl)
    })
      .then((res) => res.json().then((data) => ({ ok: res.ok, data })))
      .then(({ ok, data }) => {
        if (ok && data && data.success) {
          opts.onSuccess(data);
        } else {
          throw new Error((data && data.message) || 'Submission failed.');
        }
      })
      .catch((err) => {
        setMsg(opts.statusEl, 'error',
          (err && err.message ? err.message : 'Something went wrong.') +
          ' Please try again, or email hello@databery.com.');
        if (btn) { btn.disabled = false; delete btn.dataset.busy; btn.innerHTML = label; }
      });
  }

  /* ---- Contact form ---- */
  const form = document.querySelector('#contact-form');
  if (form) {
    const success = document.querySelector('.form-success');
    const errEl = document.querySelector('#contact-error');
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      submitWeb3Form(form, {
        statusEl: errEl,
        onSuccess: () => {
          setMsg(errEl, 'ok', '');
          form.style.display = 'none';
          if (success) success.classList.add('show');
        }
      });
    });
  }

  /* ---- Newsletter form ---- */
  const news = document.querySelector('#news-form');
  if (news) {
    const newsMsg = document.querySelector('#news-msg');
    news.addEventListener('submit', (e) => {
      e.preventDefault();
      submitWeb3Form(news, {
        statusEl: newsMsg,
        onSuccess: () => {
          news.style.display = 'none';
          setMsg(newsMsg, 'ok', 'Thanks — you’re subscribed. Watch your inbox.');
        }
      });
    });
  }

  /* ---- Footer year ---- */
  const yr = document.querySelector('#year');
  if (yr) yr.textContent = new Date().getFullYear();

  /* ---- Cookie consent banner ---- */
  (function () {
    let stored = null;
    try { stored = localStorage.getItem('db-cookie'); } catch (e) { return; }
    if (stored) return;
    const bar = document.createElement('div');
    bar.className = 'cookie-bar';
    bar.setAttribute('role', 'dialog');
    bar.setAttribute('aria-label', 'Cookie notice');
    bar.innerHTML =
      '<p>We use a few essential and analytics cookies to understand how the site is used. ' +
      'See our <a href="cookies.html">Cookie Policy</a>.</p>' +
      '<div class="cb-actions">' +
        '<button class="cb-decline" type="button">Decline</button>' +
        '<button class="btn btn-primary" type="button">Accept</button>' +
      '</div>';
    document.body.appendChild(bar);
    const done = (v) => { try { localStorage.setItem('db-cookie', v); } catch (e) {} bar.remove(); };
    bar.querySelector('.btn-primary').addEventListener('click', () => done('accepted'));
    bar.querySelector('.cb-decline').addEventListener('click', () => done('declined'));
  })();
})();
