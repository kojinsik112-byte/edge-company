// 제안서 각 .page 높이 측정 (A4 넘침 진단)
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch({ channel: 'chrome', headless: true });
  const p = await b.newPage();
  const src = path.resolve(__dirname, '..', '..', 'acro', 'ACRO_원삼센트레빌_옵션제안서_v5.html');
  await p.goto('file:///' + src.replace(/\\/g, '/'), { waitUntil: 'networkidle' });
  const hs = await p.evaluate(() => [...document.querySelectorAll('.page')].map(pg => Math.round(pg.getBoundingClientRect().height)));
  hs.forEach((h, i) => console.log('page', i + 1, h, h > 1123 ? 'OVERFLOW +' + Math.round(h - 1122) : 'ok'));
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
