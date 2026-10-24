/* Общий движок визуализаторов: шапка, панель управления, проигрыватель шагов,
 * живая трассировка кода (Python / C++), журнал выполнения и рисование деревьев.
 *
 * Страница задачи вызывает Viz.page({...}) и передаёт:
 *   generate()      - строит массив шагов по текущим параметрам;
 *   render(step, el)- рисует шаг в области визуализации;
 *   code            - исходный код; строки с пометкой «#@ключ» / «//@ключ»
 *                     подсвечиваются, когда step.line === ключ.
 * Шаг: { line, msg, kind: 'ok'|'bad'|'hit'|undefined, vars: {}, stats: {}, code: 'имя', ...состояние }.
 */
(function () {
  'use strict';

  const TEXT = {
    ro: {
      viz: 'Vizualizare', theory: 'Teorie și formule', speed: 'Pauză între pași', reset: 'Reset',
      play: 'Play', pause: 'Pauză', prev: 'Pasul anterior', next: 'Pasul următor', tracer: 'Codul executat',
      log: 'Jurnalul execuției', step: 'Pas', back: '← Toate', timeline: 'Pas', vars: 'variabile',
      keys: 'Taste:', keyPlay: 'play / pauză', keyStep: 'pas',
    },
    ru: {
      viz: 'Визуализация', theory: 'Теория и формулы', speed: 'Пауза между шагами', reset: 'Сброс',
      play: 'Пуск', pause: 'Пауза', prev: 'Предыдущий шаг', next: 'Следующий шаг', tracer: 'Выполняемый код',
      log: 'Журнал выполнения', step: 'Шаг', back: '← Все задания', timeline: 'Шаг', vars: 'переменные',
      keys: 'Клавиши:', keyPlay: 'пуск / пауза', keyStep: 'шаг',
    },
  };

  const ICON = {
    play: '<svg viewBox="0 0 24 24"><path d="M7 4.5v15l12.5-7.5z"/></svg>',
    pause: '<svg viewBox="0 0 24 24"><path d="M6 4.5h4.2v15H6zM13.8 4.5H18v15h-4.2z"/></svg>',
    prev: '<svg viewBox="0 0 24 24"><path d="M5 4.5h2.4v15H5zM20 4.5v15L8.6 12z"/></svg>',
    next: '<svg viewBox="0 0 24 24"><path d="M16.6 4.5H19v15h-2.4zM4 4.5v15L15.4 12z"/></svg>',
    reset: '<svg viewBox="0 0 24 24"><path d="M12 4a8 8 0 1 1-7.4 5h2.3A6 6 0 1 0 12 6v3L7.5 5 12 1z"/></svg>',
  };

  const KW = {
    py: new Set('def return for in if elif else while not and or is None True False class self pass break continue lambda nonlocal import from try except raise with as yield'.split(' ')),
    cpp: new Set('int void bool double char auto const return for if else while do new delete nullptr true false struct class template typename static std vector string size_t unsigned long switch case break continue throw try catch using'.split(' ')),
  };

  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  function store(key, value) {
    try {
      if (value === undefined) return localStorage.getItem(key);
      localStorage.setItem(key, value);
    } catch (e) { /* хранилище недоступно - работаем без него */ }
    return null;
  }

  function highlight(text, lang) {
    const re = lang === 'py'
      ? /(#.*$)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|(\b\d+(?:\.\d+)?\b)|([A-Za-z_]\w*)/g
      : /(\/\/.*$)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|(\b\d+(?:\.\d+)?\b)|([A-Za-z_]\w*)/g;
    let out = '', last = 0, m, prevWord = '';
    while ((m = re.exec(text))) {
      out += esc(text.slice(last, m.index));
      if (m[1]) out += `<span class="com">${esc(m[1])}</span>`;
      else if (m[2]) out += `<span class="str">${esc(m[2])}</span>`;
      else if (m[3]) out += `<span class="num">${m[3]}</span>`;
      else if (KW[lang].has(m[4])) out += `<span class="kw">${m[4]}</span>`;
      else if (prevWord === 'def' || /^\s*\(/.test(text.slice(re.lastIndex)) && /^(void|bool|int|double|T\*|ENode\*|u64|long)$/.test(prevWord)) out += `<span class="fn">${m[4]}</span>`;
      else out += esc(m[4]);
      if (m[4]) prevWord = m[4];
      last = re.lastIndex;
    }
    return out + esc(text.slice(last));
  }

  function parseCode(src, lang) {
    const lines = src.replace(/^\n+/, '').replace(/\s+$/, '').split('\n');
    return lines.map(line => {
      const m = line.match(/\s*(?:#|\/\/)@([\w,-]+)\s*$/);
      const text = m ? line.slice(0, m.index) : line;
      return { html: highlight(text, lang), keys: m ? m[1].split(',') : [] };
    });
  }

  // ---------------------------------------------------------------------------

  function page(cfg) {
    const T = TEXT[cfg.lang || 'ro'];
    document.documentElement.lang = cfg.lang || 'ro';
    const tpl = id => { const t = document.getElementById(id); return t ? t.innerHTML : ''; };

    const codeSets = cfg.code.py ? { main: cfg.code } : cfg.code;
    const codes = {};
    for (const [name, c] of Object.entries(codeSets)) {
      codes[name] = { title: c.title || {}, py: parseCode(c.py, 'py'), cpp: parseCode(c.cpp, 'cpp') };
    }

    const legend = (cfg.legend || []).map(([color, text]) => `<span><i style="background:${color}"></i>${esc(text)}</span>`).join('');

    const root = document.getElementById('app');
    root.className = 'app';
    root.innerHTML = `
      <header class="top">
        <a class="back" href="${cfg.home || '../index.html'}">${T.back}</a>
        <div class="logo">${esc(cfg.logo || '◆')}</div>
        <div class="title">
          <h1>${esc(cfg.title)}<span class="badge">${esc(cfg.badge || '')}</span></h1>
          <p>${esc(cfg.subtitle || '')}</p>
        </div>
        <nav class="tabs">
          <button class="tab active" data-tab="viz">▶ ${T.viz}</button>
          <button class="tab" data-tab="theory">${T.theory}</button>
        </nav>
      </header>
      <section class="card controls" data-panel="viz">
        <div class="params">${tpl('params')}</div>
        <div class="speed">
          <span class="label">${T.speed} <output id="speedOut"></output></span>
          <input type="range" id="speed" min="20" max="1500" step="10">
        </div>
        <div class="buttons">
          <button class="btn" id="reset">${ICON.reset}${T.reset}</button>
          <button class="btn icon" id="prev" title="${T.prev}" aria-label="${T.prev}">${ICON.prev}</button>
          <button class="btn primary" id="play">${ICON.play}<span>${T.play}</span></button>
          <button class="btn icon" id="next" title="${T.next}" aria-label="${T.next}">${ICON.next}</button>
        </div>
      </section>
      <main class="grid" data-panel="viz">
        <section class="card stage">
          <div class="stage-head">
            <h2><span class="ic">▤</span>${esc(cfg.stageTitle || T.viz)}</h2>
            <div class="chips" id="chips"></div>
          </div>
          <div class="view" id="view"></div>
          <div class="legend">${legend}</div>
          <div class="banner" id="banner"></div>
          <div class="scrub">
            <span class="label">${T.timeline}</span>
            <input type="range" id="scrub" min="0" max="0" value="0">
          </div>
          <div class="kbd-hint">${T.keys} <kbd>Space</kbd> ${T.keyPlay} · <kbd>←</kbd> <kbd>→</kbd> ${T.keyStep}</div>
        </section>
        <section class="card tracer">
          <div class="tracer-head">
            <h2><span class="ic">&lt;/&gt;</span>${T.tracer}</h2>
            <div class="seg" id="langSeg"><button data-lang="py">Python</button><button data-lang="cpp">C++</button></div>
          </div>
          <div class="routine" id="routine"></div>
          <pre class="code" id="code"></pre>
          <div class="vars" id="vars"></div>
        </section>
        <section class="card log">
          <div class="log-head"><h2><span class="ic">≡</span>${T.log}</h2><span class="chip" id="lineChip"></span></div>
          <ol class="log-list" id="log"></ol>
        </section>
      </main>
      <main class="theory" data-panel="theory" hidden>${tpl('theory')}</main>`;

    const $ = id => document.getElementById(id);
    const view = $('view');
    const viz = {
      steps: [], i: 0, playing: false, timer: null, view,
      lang: store('viz-lang') === 'cpp' ? 'cpp' : 'py',
      delay: Number(store('viz-speed')) || cfg.speed || 300,
      shownCode: null,
    };

    // ---------- вкладки ----------
    root.querySelectorAll('.tab').forEach(btn => btn.addEventListener('click', () => {
      root.querySelectorAll('.tab').forEach(b => b.classList.toggle('active', b === btn));
      root.querySelectorAll('[data-panel]').forEach(p => { p.hidden = p.dataset.panel !== btn.dataset.tab; });
    }));

    // ---------- скорость ----------
    const speed = $('speed');
    speed.value = viz.delay;
    const showSpeed = () => { $('speedOut').textContent = viz.delay + ' ms'; };
    speed.addEventListener('input', () => { viz.delay = Number(speed.value); store('viz-speed', viz.delay); showSpeed(); });
    showSpeed();

    // ---------- язык кода ----------
    const langSeg = $('langSeg');
    const showLang = () => langSeg.querySelectorAll('button').forEach(b => b.classList.toggle('active', b.dataset.lang === viz.lang));
    langSeg.addEventListener('click', e => {
      const b = e.target.closest('button'); if (!b) return;
      viz.lang = b.dataset.lang; store('viz-lang', viz.lang); showLang(); viz.shownCode = null; draw();
    });
    showLang();

    // ---------- отрисовка шага ----------
    function drawCode(step) {
      const name = step.code || Object.keys(codes)[0];
      const set = codes[name];
      const key = name + '/' + viz.lang;
      const pre = $('code');
      if (viz.shownCode !== key) {
        pre.innerHTML = set[viz.lang].map((l, k) =>
          `<div class="ln" data-k="${l.keys.join(' ')}"><span class="no">${k + 1}</span><span>${l.html || ' '}</span></div>`).join('');
        $('routine').textContent = set.title[viz.lang] || '';
        viz.shownCode = key;
      }
      let first = null;
      pre.querySelectorAll('.ln').forEach(div => {
        const on = !!step.line && div.dataset.k.split(' ').includes(step.line);
        div.classList.toggle('active', on);
        if (on && !first) first = div;
      });
      if (first) {
        const top = first.offsetTop - pre.offsetTop;
        if (top < pre.scrollTop + 20 || top > pre.scrollTop + pre.clientHeight - 40) pre.scrollTop = top - pre.clientHeight / 3;
        $('lineChip').textContent = 'LINE: ' + (Array.prototype.indexOf.call(pre.children, first) + 1);
      } else {
        $('lineChip').textContent = 'LINE: —';
      }
    }

    function drawLog() {
      const from = Math.max(0, viz.i - 199);
      let html = '';
      for (let k = from; k <= viz.i && k < viz.steps.length; k++) {
        const s = viz.steps[k];
        html += `<li class="${k === viz.i ? 'cur ' : ''}${s.kind || ''}"><span class="n">${k + 1}</span><span class="m">${esc(s.msg || '')}</span></li>`;
      }
      const log = $('log');
      log.innerHTML = html;
      log.scrollTop = log.scrollHeight;
    }

    function draw() {
      const step = viz.steps[viz.i];
      if (!step) return;
      drawCode(step);
      cfg.render(step, view, viz);
      const banner = $('banner');
      banner.className = 'banner ' + (step.kind || '');
      banner.innerHTML = step.bannerHtml || esc(step.msg || '');
      $('vars').innerHTML = Object.entries(step.vars || {}).map(([k, v]) => `<span class="var">${esc(k)} = <b>${esc(v)}</b></span>`).join('');
      const stats = Object.entries(step.stats || {}).map(([k, v]) => `<span class="chip"><span>${esc(k)}:</span> <b>${esc(v)}</b></span>`).join('');
      $('chips').innerHTML = stats + `<span class="chip">${T.step}: <b>${viz.i + 1}</b> / <b>${viz.steps.length}</b></span>`;
      const scrub = $('scrub');
      scrub.max = Math.max(0, viz.steps.length - 1);
      scrub.value = viz.i;
      drawLog();
      $('prev').disabled = viz.i <= 0;
      $('next').disabled = viz.i >= viz.steps.length - 1;
    }

    // ---------- проигрыватель ----------
    function setPlaying(on) {
      viz.playing = on;
      clearTimeout(viz.timer);
      $('play').innerHTML = (on ? ICON.pause : ICON.play) + `<span>${on ? T.pause : T.play}</span>`;
      if (on) tick();
    }
    function tick() {
      viz.timer = setTimeout(() => {
        if (!viz.playing) return;
        if (viz.i < viz.steps.length - 1) {
          viz.go(viz.i + 1);
          if (viz.steps[viz.i].pause) { setPlaying(false); return; }
          tick();
        } else {
          setPlaying(false);
        }
      }, viz.delay);
    }

    viz.go = i => { viz.i = Math.max(0, Math.min(viz.steps.length - 1, i)); draw(); };
    viz.play = () => { if (viz.i >= viz.steps.length - 1) viz.go(0); setPlaying(true); };
    viz.pause = () => setPlaying(false);
    viz.redraw = draw;
    viz.load = (steps, opts = {}) => {
      viz.steps = steps.length ? steps : [{ msg: '' }];
      let last = {};
      for (const s of viz.steps) { if (s.code) last = s; else s.code = last.code; }
      viz.go(opts.start || 0);
      setPlaying(!!opts.autoplay && viz.steps.length > 1);
    };
    // Перейти к следующему шагу, удовлетворяющему условию (например, к следующему решению).
    viz.seek = pred => {
      for (let k = viz.i + 1; k < viz.steps.length; k++) if (pred(viz.steps[k])) { setPlaying(false); viz.go(k); return true; }
      return false;
    };
    viz.reset = () => {
      setPlaying(false);
      let steps;
      try { steps = cfg.generate(viz); } catch (e) { steps = [{ msg: e.message, kind: 'bad', error: true }]; }
      if (steps) viz.load(steps, { autoplay: !!cfg.autoplay });
    };

    $('play').addEventListener('click', () => (viz.playing ? viz.pause() : viz.play()));
    $('prev').addEventListener('click', () => { viz.pause(); viz.go(viz.i - 1); });
    $('next').addEventListener('click', () => { viz.pause(); viz.go(viz.i + 1); });
    $('reset').addEventListener('click', viz.reset);
    $('scrub').addEventListener('input', e => { viz.pause(); viz.go(Number(e.target.value)); });
    document.addEventListener('keydown', e => {
      if (e.target.closest('input, select, textarea') || e.metaKey || e.ctrlKey || e.altKey) return;
      if (e.code === 'Space') { e.preventDefault(); viz.playing ? viz.pause() : viz.play(); }
      else if (e.key === 'ArrowRight') { viz.pause(); viz.go(viz.i + 1); }
      else if (e.key === 'ArrowLeft') { viz.pause(); viz.go(viz.i - 1); }
    });
    // Enter в поле параметров = «Сброс» с новыми данными.
    root.querySelector('.params').addEventListener('keydown', e => {
      if (e.key === 'Enter' && e.target.matches('input')) { e.preventDefault(); (cfg.onEnter || viz.reset)(); }
    });

    if (cfg.init) cfg.init(viz);
    viz.reset();
    return viz;
  }

  // ---------------------------------------------------------------------------
  // Бинарное дерево в SVG. Узлы: { left, right, ... }; x - номер в симметричном
  // обходе (поэтому поисковое дерево рисуется «отсортированным» слева направо),
  // y - глубина. roots - массив корней (лес, например стек поддеревьев).
  function drawBinary(roots, o = {}) {
    const colW = o.colW || 54, rowH = o.rowH || 72, r = o.r || 19, pad = o.pad || 28;
    const rectW = o.rectW || 44, rectH = o.rectH || 32;
    const pos = new Map();
    let x = 0, maxD = 0;
    (function layout(list) {
      for (const root of list) {
        (function walk(n, d) {
          if (!n) return;
          walk(n.left, d + 1);
          pos.set(n, { x: pad + x * colW + colW / 2, y: pad + d * rowH + (o.top || 0) });
          x += 1; maxD = Math.max(maxD, d);
          walk(n.right, d + 1);
        })(root, 0);
        x += o.gap === undefined ? 0.6 : o.gap;
      }
    })(roots.filter(Boolean));
    const width = Math.max(o.minWidth || 0, pad * 2 + Math.max(1, x - (o.gap === undefined ? 0.6 : o.gap)) * colW);
    const height = pad * 2 + maxD * rowH + (o.top || 0) + (o.extraBottom || 14);
    let edges = '', nodes = '';
    for (const [n, p] of pos) {
      for (const side of ['left', 'right']) {
        const c = n[side];
        if (!c) continue;
        const q = pos.get(c);
        edges += `<line class="edge ${o.edgeCls ? o.edgeCls(n, c, side) || '' : ''}" x1="${p.x}" y1="${p.y}" x2="${q.x}" y2="${q.y}"/>`;
        if (o.edgeLabel) {
          const lx = (p.x + q.x) / 2 + (side === 'left' ? -9 : 9), ly = (p.y + q.y) / 2 - 2;
          edges += `<text class="edge-label" x="${lx}" y="${ly}" text-anchor="${side === 'left' ? 'end' : 'start'}">${esc(o.edgeLabel(n, side))}</text>`;
        }
      }
    }
    for (const [n, p] of pos) {
      const shape = o.shape ? o.shape(n) : 'circle';
      const body = shape === 'rect'
        ? `<rect x="${p.x - rectW / 2}" y="${p.y - rectH / 2}" width="${rectW}" height="${rectH}" rx="8"/>`
        : `<circle cx="${p.x}" cy="${p.y}" r="${r}"/>`;
      const sub = o.sub ? o.sub(n) : '';
      const badge = o.badge ? o.badge(n) : '';
      const bx = p.x + (shape === 'rect' ? rectW / 2 : r * 0.8), by = p.y - (shape === 'rect' ? rectH / 2 : r * 0.8);
      const bw = Math.max(16, String(badge).length * 6.4 + 8);
      nodes += `<g class="node ${o.cls ? o.cls(n) || '' : ''}">${o.title ? `<title>${esc(o.title(n))}</title>` : ''}${body}` +
        `<text x="${p.x}" y="${p.y}">${esc(o.label(n))}</text>` +
        (sub ? `<text class="sub" x="${p.x}" y="${p.y + (shape === 'rect' ? rectH / 2 : r) + 11}">${esc(sub)}</text>` : '') +
        (badge !== '' && badge !== undefined && badge !== null ? `<rect class="badge-bg" x="${bx - bw / 2}" y="${by - 8}" width="${bw}" height="16" rx="8"/><text class="badge-tx" x="${bx}" y="${by}">${esc(badge)}</text>` : '') +
        `</g>`;
    }
    return `<svg class="tree" viewBox="0 0 ${width} ${height}" width="${width}" height="${height}">${edges}${nodes}</svg>`;
  }

  window.Viz = { page, drawBinary, esc };
})();
