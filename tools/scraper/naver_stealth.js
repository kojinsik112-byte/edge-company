// playwright-extra + stealth 로 네이버 봇탐지 우회
const { chromium } = require('playwright-extra');
const stealth = require('puppeteer-extra-plugin-stealth')();
chromium.use(stealth);
const fs = require('fs');
const path = require('path');

const url = process.argv[2];
const outDir = process.argv[3] || './out';
fs.mkdirSync(outDir, { recursive: true });

(async () => {
  const browser = await chromium.launch({ headless: false, channel: 'chrome' });
  const ctx = await browser.newContext({
    viewport: { width: 1366, height: 900 },
    locale: 'ko-KR',
    timezoneId: 'Asia/Seoul',
    extraHTTPHeaders: { 'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8' },
  });
  const page = await ctx.newPage();
  console.log('navigating:', url);
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(4000);

  await autoScroll(page);
  await page.waitForTimeout(2000);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(800);
  await autoScroll(page);
  await page.waitForTimeout(1500);

  await page.screenshot({ path: path.join(outDir, 'fullpage.png'), fullPage: true });
  const data = await page.evaluate(() => ({
    title: document.querySelector('meta[property="og:title"]')?.content ?? document.title,
    ogDesc: document.querySelector('meta[property="og:description"]')?.content ?? null,
    bodySnippet: document.body.innerText.slice(0, 8000),
    imageCount: document.images.length,
    detailImgs: Array.from(document.images).map(i => i.currentSrc || i.src).filter(s => /phinf|pstatic/.test(s)).slice(0, 80),
  }));
  fs.writeFileSync(path.join(outDir, 'bodytext.txt'), data.bodySnippet || '', 'utf8');
  fs.writeFileSync(path.join(outDir, 'data.json'), JSON.stringify(data, null, 2), 'utf8');
  console.log('done. title=', data.title, '| images=', data.imageCount);
  await browser.close();
})().catch((e) => { console.error('ERROR:', e.message.split('\n')[0]); process.exit(1); });

function autoScroll(page) {
  return page.evaluate(async () => {
    await new Promise((resolve) => {
      let total = 0; const step = 600;
      const timer = setInterval(() => {
        window.scrollBy(0, step); total += step;
        if (total >= document.body.scrollHeight + 2000) { clearInterval(timer); resolve(); }
      }, 250);
    });
  });
}
