const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ headless: true });
  const p = await b.newPage({ viewport: { width: 1080, height: 1400 }, deviceScaleFactor: 2 });
  const url = 'file:///' + 'C:/Users/win11/Downloads/에어전트 팀/edge-company-claude-friendly-thompson-NDkKH/design-division/output/슬림아크로/slim_full.html'.replace(/ /g,'%20');
  await p.goto(url, { waitUntil: 'networkidle' });
  await p.waitForTimeout(1200);
  await p.screenshot({ path: '../../design-division/output/슬림아크로/slim_full.png', fullPage: true });
  console.log('OK'); await b.close();
})().catch(e=>{console.error(e.message);process.exit(1)});
