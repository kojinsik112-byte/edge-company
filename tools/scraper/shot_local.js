const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ headless: true });
  const p = await b.newPage({ viewport: { width: 860, height: 1200 } });
  const url = 'file:///' + 'C:/Users/win11/Downloads/에어전트 팀/edge-company-claude-friendly-thompson-NDkKH/design-division/output/슬림아크로/detail_page.html'.replace(/ /g,'%20');
  await p.goto(url, { waitUntil: 'networkidle' });
  await p.screenshot({ path: '../../scout_reports/screens/slim_arco_preview.png', fullPage: true });
  console.log('OK');
  await b.close();
})().catch(e=>{console.error(e.message);process.exit(1)});
