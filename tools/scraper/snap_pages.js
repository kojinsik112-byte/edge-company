// 제안서 페이지 미리보기 캡처 (검토용)
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch({ channel: 'chrome', headless: true });
  const p = await b.newPage({ viewport: { width: 900, height: 1200 }, deviceScaleFactor: 1 });
  const src = path.resolve(__dirname, '..', '..', 'acro', 'ACRO_원삼센트레빌_옵션제안서_v3.html');
  await p.goto('file:///' + src.replace(/\\/g, '/'), { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(800);
  const pages = await p.$$('.page');
  const outDir = process.env.SNAP_OUT || path.join(__dirname, 'snap');
  require('fs').mkdirSync(outDir, { recursive: true });
  for (const i of [3]) {
    if (pages[i]) { await pages[i].scrollIntoViewIfNeeded(); await pages[i].screenshot({ path: path.join(outDir, `p${i + 1}.png`) }); }
  }
  console.log('snapped');
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
