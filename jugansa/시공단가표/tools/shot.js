const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  for (const [w, name] of [[900, 'desk'], [390, 'phone']]) {
    const p = await b.newPage({ viewport: { width: w, height: 1200 } });
    await p.goto('file://' + process.argv[2]);
    await p.waitForTimeout(800);
    await p.screenshot({ path: process.argv[3] + '_' + name + '.png', fullPage: true });
    const ov = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    console.log(name, 'overflow', ov);
  }
  const p = await b.newPage();
  await p.goto('file://' + process.argv[2]);
  await p.pdf({ path: process.argv[3] + '.pdf', format: 'A4', printBackground: true });
  await b.close();
})();
