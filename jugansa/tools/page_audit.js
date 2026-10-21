// 제안서 HTML 쪽별 자동 검사 — ① 글자 대비(WCAG 4.5 / 큰 글자 3) ② 쪽 밖 넘침 ③ overflow:hidden 잘림. 사진 위 글자는 제외.
// 사용: PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node jugansa/tools/page_audit.js <제안서.html> <결과.json>
// 사용: node audit.js <html> <out.json> — 쪽마다 ① 글자 대비(WCAG) ② 쪽 밖으로 넘친 요소 ③ overflow:hidden 안에서 잘린 글자
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'); const path = require('path');
(async () => {
  const [, , file, out] = process.argv;
  const browser = await chromium.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
  await page.goto('file://' + path.resolve(file), { waitUntil: 'load', timeout: 120000 });
  await page.evaluate(() => document.fonts && document.fonts.ready);
  await page.waitForTimeout(1500);
  const res = await page.evaluate(() => {
    const P = c => { const m = c && c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const v = m[1].split(',').map(s => parseFloat(s)); return { r: v[0], g: v[1], b: v[2], a: v.length > 3 ? v[3] : 1 }; };
    const blend = (top, bot) => ({ r: top.r * top.a + bot.r * (1 - top.a), g: top.g * top.a + bot.g * (1 - top.a), b: top.b * top.a + bot.b * (1 - top.a), a: 1 });
    const L = c => { const f = x => { x /= 255; return x <= .03928 ? x / 12.92 : Math.pow((x + .055) / 1.055, 2.4); }; return .2126 * f(c.r) + .7152 * f(c.g) + .0722 * f(c.b); };
    const CR = (a, b) => { const x = L(a), y = L(b); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05); };
    const gradAvg = s => { const cs = (s.match(/rgba?\([^)]+\)|#[0-9a-fA-F]{6}/g) || []).map(x => x[0] === '#' ? { r: parseInt(x.substr(1, 2), 16), g: parseInt(x.substr(3, 2), 16), b: parseInt(x.substr(5, 2), 16), a: 1 } : P(x)); if (!cs.length) return null; const n = cs.length; return cs.reduce((o, c) => ({ r: o.r + c.r / n, g: o.g + c.g / n, b: o.b + c.b / n, a: o.a + c.a / n }), { r: 0, g: 0, b: 0, a: 0 }); };
    const pages = [...document.querySelectorAll('section.page')];
    const out = [];
    pages.forEach((sec, pi) => {
      const sr = sec.getBoundingClientRect();
      const lowC = [], overflow = [], clipped = [];
      sec.querySelectorAll('*').forEach(el => {
        const cs = getComputedStyle(el);
        if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) === 0) return;
        const r = el.getBoundingClientRect();
        if (r.width < 1 || r.height < 1) return;
        const own = [...el.childNodes].filter(n => n.nodeType === 3 && n.textContent.trim()).map(n => n.textContent.trim()).join(' ');
        // ② 쪽 밖으로 넘침
        if (own && (r.bottom > sr.bottom + 1 || r.right > sr.right + 1 || r.top < sr.top - 1)) overflow.push(own.slice(0, 40));
        // ③ 잘림(overflow hidden 상자 안 글자가 넘침)
        if ((cs.overflow === 'hidden' || cs.overflowY === 'hidden') && el.scrollHeight > el.clientHeight + 4 && el.innerText && el.innerText.trim().length > 3 && !el.querySelector('img'))
          clipped.push((el.className || el.tagName) + ': ' + el.innerText.trim().replace(/\s+/g, ' ').slice(0, 40) + ` (${el.scrollHeight}>${el.clientHeight})`);
        // ① 대비
        if (!own) return;
        const fg = P(cs.color); if (!fg || fg.a < .05) return;
        // 사진 위 글자는 건너뜀
        const cx = Math.min(Math.max(r.left + r.width / 2, sr.left + 1), sr.right - 1), cy = Math.min(Math.max(r.top + r.height / 2, sr.top + 1), sr.bottom - 1);
        // 사진 위 글자(이미지 사각형 안 · 배경 이미지 조상)는 건너뜀 — elementsFromPoint는 화면 밖 쪽에서 비어 쓰지 않는다
        const onImg = [...sec.querySelectorAll('img')].some(im => { const q = im.getBoundingClientRect(); return q.width > 40 && cx >= q.left && cx <= q.right && cy >= q.top && cy <= q.bottom && !im.contains(el); });
        let urlAnc = false; for (let n = el; n && n !== sec.parentElement; n = n.parentElement) if (/url\(/.test(getComputedStyle(n).backgroundImage)) { urlAnc = true; break; }
        if (onImg || urlAnc) return;
        const layers = [];
        let n = el;
        while (n && n.nodeType === 1) {
          const s = getComputedStyle(n);
          const bc = P(s.backgroundColor); const gi = s.backgroundImage !== 'none' ? gradAvg(s.backgroundImage) : null;
          if (gi) layers.push(gi);
          if (bc && bc.a > 0) layers.push(bc);
          if (bc && bc.a >= 1) break;
          n = n.parentElement;
        }
        let bg = { r: 255, g: 255, b: 255, a: 1 };
        for (let k = layers.length - 1; k >= 0; k--) bg = blend(layers[k], bg);
        const fgc = fg.a < 1 ? blend(fg, bg) : fg;
        const ratio = CR(fgc, bg);
        const fs = parseFloat(cs.fontSize), bold = parseInt(cs.fontWeight) >= 700;
        const need = (fs >= 24 || (fs >= 18.5 && bold)) ? 3 : 4.5;
        if (ratio < need) lowC.push({ t: own.slice(0, 30), ratio: +ratio.toFixed(2), fs, need, fg: cs.color, bg: `rgb(${bg.r | 0},${bg.g | 0},${bg.b | 0})` });
      });
      const h = sec.querySelector('h1,h2');
      out.push({ no: pi + 1, cls: sec.className, title: h ? h.innerText.replace(/\s+/g, ' ').slice(0, 30) : '', lowC, overflow, clipped });
    });
    return out;
  });
  fs.writeFileSync(out, JSON.stringify(res, null, 1));
  await browser.close();
  console.log('pages', res.length);
})();
