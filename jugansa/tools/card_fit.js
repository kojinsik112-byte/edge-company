// 카드 안 글자 · 칩이 카드 아래 테두리(안쪽 여백 포함)를 넘는지 잰다 — 요약제안서 9쪽 칩 잘림(10-23) 같은 '상자 안 잘림' 검사.
// 사용: PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node jugansa/tools/card_fit.js <요약제안서.html> [선택자=.bx]
// 출력: 넘친 카드마다 '쪽 · 카드 제목 · 넘친 px'. 0줄이면 통과(종료 코드 0), 있으면 종료 코드 1.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path');
(async () => {
  const [, , file, sel = '.bx'] = process.argv;
  const browser = await chromium.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
  await page.goto('file://' + path.resolve(file), { waitUntil: 'load', timeout: 120000 });
  await page.evaluate(() => document.fonts && document.fonts.ready);
  await page.waitForTimeout(1200);
  const bad = await page.evaluate((sel) => {
    const out = [];
    [...document.querySelectorAll('section.page')].forEach((sec, pi) => {
      sec.querySelectorAll(sel).forEach(bx => {
        const r = bx.getBoundingClientRect(), s = getComputedStyle(bx);
        const inner = r.bottom - parseFloat(s.paddingBottom) - parseFloat(s.borderBottomWidth);
        let low = -Infinity;
        bx.querySelectorAll('*').forEach(el => {
          const e = el.getBoundingClientRect();
          if (e.width > 0 && e.height > 0 && getComputedStyle(el).position !== 'absolute') low = Math.max(low, e.bottom);
        });
        if (low - inner > 0.5) out.push({ page: pi + 1, title: (bx.querySelector('h3,h2') || bx).textContent.trim().slice(0, 30), over: +(low - inner).toFixed(1) });
      });
    });
    return out;
  }, sel);
  await browser.close();
  bad.forEach(b => console.log(`p.${b.page}  ${b.title}  +${b.over}px`));
  console.log(bad.length ? `넘침 ${bad.length}곳` : '넘침 0');
  process.exit(bad.length ? 1 : 0);
})();
