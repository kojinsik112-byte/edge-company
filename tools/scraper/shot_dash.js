const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ headless: true });
  const p = await b.newPage({ viewport: { width: 1500, height: 900 }, deviceScaleFactor: 1.5 });
  await p.goto('http://localhost:8077/team_dashboard.html', { waitUntil: 'networkidle' });
  await p.waitForTimeout(2500);
  await p.screenshot({ path: '../../business-ops/dashboard/dashboard_shot.png' });
  console.log('OK'); await b.close();
})().catch(e=>{console.error(e.message);process.exit(1)});
