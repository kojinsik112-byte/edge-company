// 제안서 HTML 쪽별 겹침 검사 — page_audit.js가 못 잡는 '글자 ↔ 글자', '글자 ↔ 다른 상자(카드 · KEY POINT 띠)' 겹침.
// 사용: PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node jugansa/tools/overlap_audit.js <제안서.html> <결과.json> [쪽 번호,…]
// 글자 사각형 = 텍스트 노드의 실제 줄 사각형(Range) · 상자 = 배경색 · 테두리 · 그림자가 있는 요소(조상 아닌 것)
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'); const path = require('path');
(async () => {
  const [, , file, out, only] = process.argv;
  const want = only ? new Set(only.split(',').map(Number)) : null;
  const browser = await chromium.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
  await page.goto('file://' + path.resolve(file), { waitUntil: 'load', timeout: 120000 });
  await page.evaluate(() => document.fonts && document.fonts.ready);
  await page.waitForTimeout(1500);
  const res = await page.evaluate((want) => {
    const out = [];
    const inter = (a, b, pad = 1) => Math.max(0, Math.min(a.right, b.right) - Math.max(a.left, b.left) - pad) * Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) - pad);
    const vis = el => { for (let n = el; n && n.nodeType === 1; n = n.parentElement) { const s = getComputedStyle(n); if (s.display === 'none' || s.visibility === 'hidden' || parseFloat(s.opacity) === 0) return false; } return true; };
    [...document.querySelectorAll('section.page')].forEach((sec, pi) => {
      if (want && !want.includes(pi + 1)) return;
      const sr = sec.getBoundingClientRect();
      // 글자 줄 사각형
      const lines = [];
      const tw = document.createTreeWalker(sec, NodeFilter.SHOW_TEXT);
      for (let t; (t = tw.nextNode());) {
        if (!t.textContent.trim()) continue;
        const el = t.parentElement; if (!vis(el)) continue;
        // 사진 위 캡션 · 배경 이미지 위 글자는 의도된 겹침
        const rg = document.createRange(); rg.selectNodeContents(t);
        [...rg.getClientRects()].forEach(r => { if (r.width > 2 && r.height > 2) lines.push({ el, r, t: t.textContent.trim().slice(0, 24) }); });
      }
      // 상자(배경 · 테두리 · 그림자) — 쪽 자신 · 아주 큰 바탕은 제외
      const boxes = [];
      sec.querySelectorAll('*').forEach(el => {
        if (!vis(el)) return;
        const s = getComputedStyle(el); const r = el.getBoundingClientRect();
        if (r.width < 20 || r.height < 14) return;
        if (r.width * r.height > sr.width * sr.height * 0.7) return;
        const bg = s.backgroundColor && !/rgba\(0, 0, 0, 0\)|transparent/.test(s.backgroundColor);
        // 사진(IMG · url 배경)은 캡션을 얹는 자리라 제외 — 사진 위 글자는 의도된 배치
        if (el.tagName === 'IMG' || /url\(/.test(s.backgroundImage)) return;
        const grad = s.backgroundImage !== 'none' && /gradient/.test(s.backgroundImage);
        const bd = parseFloat(s.borderTopWidth) > 0 || parseFloat(s.borderLeftWidth) > 0;
        if (bg || grad || bd || s.boxShadow !== 'none') boxes.push({ el, r, cls: (el.className && el.className.baseVal === undefined ? el.className : el.tagName).toString().slice(0, 30) });
      });
      const issues = [];
      // ① 글자 ↔ 글자(서로 다른 요소)
      for (let i = 0; i < lines.length; i++) for (let j = i + 1; j < lines.length; j++) {
        const a = lines[i], b = lines[j];
        if (a.el === b.el || a.el.contains(b.el) || b.el.contains(a.el)) continue;
        const ar = inter(a.r, b.r, 2);
        if (ar > Math.min(a.r.width * a.r.height, b.r.width * b.r.height) * 0.12) issues.push(`글자겹침: "${a.t}" × "${b.t}"`);
      }
      // ② 글자 ↔ 다른 상자: 글자가 상자 경계를 걸치거나(일부만 안) 조상 아닌 상자 안에 들어감
      lines.forEach(l => {
        boxes.forEach(b => {
          if (b.el.contains(l.el) || l.el.contains(b.el)) return;
          const a = inter(l.r, b.r, 1); if (a <= 0) return;
          const la = l.r.width * l.r.height;
          const ih = Math.min(l.r.bottom, b.r.bottom) - Math.max(l.r.top, b.r.top);
          if (ih > 4 && a > la * 0.08) { issues.push(`상자겹침: "${l.t}" ↔ [${b.cls}] ${Math.round(a / la * 100)}%`); return; }
          // 그림자 · 테두리 상자의 옆 자식 등 의도된 겹침 제외: 글자가 상자 안 '절대 위치' 요소의 자식인지
        });
      });
      // ③ 상자 ↔ 상자(형제 카드끼리 · 카드와 KEY POINT): 같은 부모가 아니어도 서로 조상 아님 + 둘 다 배경 있음
      for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
        const a = boxes[i], b = boxes[j];
        if (a.el.contains(b.el) || b.el.contains(a.el)) continue;
        const ar = inter(a.r, b.r, 3);
        if (ar > 60) issues.push(`상자↔상자: [${a.cls}] × [${b.cls}] ${Math.round(ar)}px²`);
      }
      const uniq = [...new Set(issues)];
      if (uniq.length) out.push({ no: pi + 1, n: uniq.length, issues: uniq.slice(0, 25) });
    });
    return out;
  }, want ? [...want] : null);
  fs.writeFileSync(out, JSON.stringify(res, null, 1));
  await browser.close();
  console.log('pages with overlap', res.length, res.map(p => p.no + '(' + p.n + ')').join(' '));
})();
