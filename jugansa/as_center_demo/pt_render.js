// PT 1장 HTML → PNG(3840×2160) · PDF(1장). 사용: node pt_render.js <html 경로>
const path = require('path');
const { chromium } = require(path.join('C:/본부장/Claude_Code/edge-company/tools/scraper/node_modules/playwright'));
const SRC = path.resolve(process.argv[2]); const base = SRC.replace(/\.html$/i, '');
(async () => {
  const b = await chromium.launch({ headless: true, channel: 'chrome' });
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2 });
  await p.goto('file:///' + SRC.replace(/\\/g, '/'), { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: base + '.png' });
  await p.pdf({ path: base + '.pdf', width: '1920px', height: '1080px', printBackground: true, pageRanges: '1' });
  await b.close(); console.log('만듦', base + '.png', base + '.pdf');
})().catch(e => { console.error(e); process.exit(1); });
