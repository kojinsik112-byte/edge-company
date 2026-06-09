// 아크로 상세 HTML(스펙표·혜택배너) → 고해상 PNG 렌더 (로컬 파일, 봇차단 무관)
const { chromium } = require('playwright');
const path = require('path');
const dir = path.join(__dirname, '..', '..', 'design-division', 'output', '아크로상세');
(async () => {
  const b = await chromium.launch();
  const page = await b.newPage({ viewport: { width: 1080, height: 900 }, deviceScaleFactor: 2 });
  const jobs = [['스펙표', null], ['혜택배너', { x: 0, y: 0, width: 1080, height: 430 }]];
  for (const [name, clip] of jobs) {
    await page.goto('file://' + path.join(dir, name + '.html'), { waitUntil: 'networkidle' });
    await page.waitForTimeout(900);
    const opt = clip ? { path: path.join(dir, name + '.png'), clip } : { path: path.join(dir, name + '.png'), fullPage: true };
    await page.screenshot(opt);
    console.log('OK', name + '.png');
  }
  await b.close();
})().catch(e => { console.error('ERR', e.message.split('\n')[0]); process.exit(1); });
