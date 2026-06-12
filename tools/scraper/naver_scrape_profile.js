// 실제 Chrome 프로필 복사본으로 네이버 상세페이지 캡처
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const url = process.argv[2];
const outDir = process.argv[3] || './out';
const userDataDir = process.argv[4]; // 복사된 프로필 경로
fs.mkdirSync(outDir, { recursive: true });

(async () => {
  const ctx = await chromium.launchPersistentContext(userDataDir, {
    headless: false,
    channel: 'chrome',
    viewport: { width: 1366, height: 900 },
    locale: 'ko-KR',
    timezoneId: 'Asia/Seoul',
    args: ['--disable-blink-features=AutomationControlled', '--no-first-run', '--no-default-browser-check'],
  });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
  });
  const page = ctx.pages()[0] || (await ctx.newPage());
  try {
    await page.goto('https://www.naver.com', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(2000);
  } catch (e) {}
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
    bodySnippet: document.body.innerText.slice(0, 6000),
    imageCount: document.images.length,
  }));
  fs.writeFileSync(path.join(outDir, 'bodytext.txt'), data.bodySnippet || '', 'utf8');
  fs.writeFileSync(path.join(outDir, 'data.json'), JSON.stringify(data, null, 2), 'utf8');
  console.log('done. title=', data.title, '| images=', data.imageCount);
  await ctx.close();
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
