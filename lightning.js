(() => {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const surfaces = [document.getElementById('home'), ...document.querySelectorAll('section.sec')].filter(Boolean);
  if (!surfaces.length) return;

  const style = document.createElement('style');
  style.textContent = `
    .lightning-bolt{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}
    #home>.lightning-bolt{z-index:-1}
    section.sec>.lightning-bolt{z-index:0}
    .lightning-flash{position:absolute;inset:0;pointer-events:none;opacity:0;mix-blend-mode:screen;
      background:radial-gradient(ellipse at var(--fx,70%) 15%,rgba(255,238,130,.55),rgba(255,212,0,.16) 42%,transparent 72%)}
    #home>.lightning-flash{z-index:-1}
    section.sec>.lightning-flash{z-index:0}
    .lightning-flash.on{animation:heroFlash .55s ease-out}
    @keyframes heroFlash{0%{opacity:0}10%{opacity:1}26%{opacity:.2}38%{opacity:.75}100%{opacity:0}}`;
  document.head.appendChild(style);

  surfaces.forEach(hero => {
  const cv = document.createElement('canvas');
  cv.className = 'lightning-bolt'; cv.setAttribute('aria-hidden', 'true');
  const flash = document.createElement('div');
  flash.className = 'lightning-flash'; flash.setAttribute('aria-hidden', 'true');
  hero.append(cv, flash);

  const cx = cv.getContext('2d');
  let W = 0, H = 0, strikes = [], streak = null, running = false;

  const fit = () => {
    const d = Math.min(devicePixelRatio || 1, 2);
    W = hero.clientWidth; H = hero.clientHeight;
    cv.width = W * d; cv.height = H * d;
    cx.setTransform(d, 0, 0, d, 0, 0);
  };
  fit();
  new ResizeObserver(fit).observe(hero);

  // jalur bergerigi (midpoint displacement)
  const jag = (x1, y1, x2, y2, off, out) => {
    if (off < 3) { out.push([x2, y2]); return; }
    const mx = (x1 + x2) / 2 + (Math.random() - .5) * off;
    const my = (y1 + y2) / 2 + (Math.random() - .5) * off;
    jag(x1, y1, mx, my, off / 2, out);
    jag(mx, my, x2, y2, off / 2, out);
  };

  function makeBolt(x) {
    const m = [[x, 0]];
    jag(x, 0, x + (Math.random() - .5) * 220, H * (.5 + Math.random() * .35), 150, m);
    const br = [], step = Math.max(3, Math.ceil(m.length / 6));
    for (let i = 3; i < m.length - 2; i += step) {
      if (Math.random() < .75) {
        const b = [m[i]];
        jag(m[i][0], m[i][1], m[i][0] + (Math.random() - .5) * 320, m[i][1] + 90 + Math.random() * 170, 60, b);
        br.push(b);
      }
    }
    return { m, br, t: performance.now(), life: 520 };
  }

  function line(p, w, col, blur) {
    cx.beginPath();
    p.forEach((q, i) => i ? cx.lineTo(q[0], q[1]) : cx.moveTo(q[0], q[1]));
    cx.lineWidth = w; cx.strokeStyle = col; cx.shadowColor = '#ffd400'; cx.shadowBlur = blur; cx.stroke();
  }

  function pulse(xPct) {
    hero.style.setProperty('--fx', xPct + '%');
    flash.classList.remove('on'); void flash.offsetWidth; flash.classList.add('on');
  }

  function fire() {
    if (Math.random() < .2) { // Thunderclap and Flash: sambaran zig-zag horizontal
      const y = H * (.25 + Math.random() * .5), dir = Math.random() < .5 ? 1 : -1;
      const xs = dir > 0 ? [-40, W * .25, W * .5, W * .75, W + 40] : [W + 40, W * .75, W * .5, W * .25, -40];
      streak = { t: performance.now(), dur: 240,
        pts: xs.map((x, i) => [x, y + (i % 2 ? -1 : 1) * (40 + Math.random() * 70)]) };
      pulse(50);
    } else {
      const n = Math.random() < .35 ? 2 : 1;
      for (let i = 0; i < n; i++) {
        const x = W * (.1 + Math.random() * .8);
        setTimeout(() => { strikes.push(makeBolt(x)); pulse(x / W * 100); start(); }, i * 130);
      }
    }
    start();
  }

  function draw(now) {
    cx.clearRect(0, 0, W, H); cx.lineJoin = 'round'; cx.lineCap = 'round';
    strikes = strikes.filter(s => now - s.t < s.life);
    strikes.forEach(s => {
      const a = 1 - (now - s.t) / s.life, f = a > .55 && Math.floor(now / 45) % 2 ? .5 : 1;
      line(s.m, 8, `rgba(255,212,0,${.32 * a * f})`, 34);
      line(s.m, 2.6, `rgba(255,250,205,${a * f})`, 18);
      s.br.forEach(b => line(b, 1.4, `rgba(255,235,120,${.85 * a * f})`, 12));
    });
    if (streak) {
      const el = now - streak.t, p = Math.min(1, el / streak.dur), fade = 1 - Math.max(0, el - streak.dur) / 300;
      if (fade <= 0) streak = null;
      else {
        const total = streak.pts.length - 1, seg = p * total, pts = [streak.pts[0]];
        for (let i = 1; i <= total; i++) {
          if (seg >= i) pts.push(streak.pts[i]);
          else { const f = seg - (i - 1); if (f > 0) { const a = streak.pts[i - 1], b = streak.pts[i]; pts.push([a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f]); } break; }
        }
        line(pts, 14, `rgba(255,212,0,${.4 * fade})`, 40);
        line(pts, 4, `rgba(255,255,232,${fade})`, 24);
      }
    }
    if (strikes.length || streak) requestAnimationFrame(draw);
    else { running = false; cx.clearRect(0, 0, W, H); }
  }
  function start() { if (!running) { running = true; requestAnimationFrame(draw); } }

  // jadwal sambaran: hanya saat hero terlihat, tab aktif, dan intro sudah selesai
  let visible = false, timer = 0;
  function schedule(delay = 500) {
    clearTimeout(timer);
    if (!visible || document.hidden) return;
    timer = setTimeout(() => {
      if (!document.getElementById('intro')) fire();
      schedule(1800 + Math.random() * 1800);
    }, delay);
  }
  new IntersectionObserver(entries => {
    visible = entries[0].isIntersecting;
    if (visible) schedule();
    else clearTimeout(timer);
  }).observe(hero);
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) clearTimeout(timer);
    else schedule(300);
  });
  });
})();