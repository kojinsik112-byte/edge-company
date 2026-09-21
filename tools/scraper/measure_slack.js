// 페이지별 높이 + 하단 빈공간(slack) 측정
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch({ channel: 'chrome', headless: true });
  const p = await b.newPage();
  const src = path.resolve(__dirname, '..', '..', 'acro', 'ACRO_원삼센트레빌_옵션제안서_v5.html');
  await p.goto('file:///' + src.replace(/\\/g, '/'), { waitUntil: 'networkidle' });
  await p.waitForTimeout(600);
  const rows = await p.evaluate(() => [...document.querySelectorAll('.page')].map(pg => {
    const r = pg.getBoundingClientRect();
    let maxB = 0;
    [...pg.children].forEach(c => {
      if (!c.className || !String(c.className).includes('foot')) {
        const cr = c.getBoundingClientRect();
        maxB = Math.max(maxB, cr.bottom - r.top);
      }
    });
    return { h: Math.round(r.height), slack: Math.round(r.height - 45 - maxB) };
  }));
  rows.forEach((x, i) => console.log('page', i + 1, 'h', x.h, x.h > 1123 ? 'OVERFLOW' : '', 'slack', x.slack));
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
