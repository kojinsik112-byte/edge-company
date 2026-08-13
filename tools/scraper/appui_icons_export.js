// 아이콘팩: 각 마크를 투명 배경 PNG로 개별 추출
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const repo = path.join(__dirname, '..', '..');
const SRC = path.join(repo, 'acro', 'ACRO_앱UI_아이콘팩_한중.html');
const outDir = path.join(repo, 'acro', '앱UI_아이콘');
fs.mkdirSync(outDir, { recursive: true });

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const page = await browser.newPage({ viewport: { width: 1300, height: 1000 }, deviceScaleFactor: 4 });
  await page.goto('file:///' + SRC.replace(/\\/g, '/'), { waitUntil: 'networkidle', timeout: 60000 });
  await page.evaluate(() => document.fonts.ready);
  // 투명 PNG: 페이지·타일 배경 제거 (화면 표시용 배경이 캡처에 찍히지 않게)
  await page.addStyleTag({ content: 'body,.tile{background:transparent!important} .tile{border-color:transparent!important}' });
  await page.waitForTimeout(1200);

  const boxes = await page.$$('.ico');
  console.log('icons:', boxes.length);
  for (const box of boxes) {
    const name = await box.getAttribute('data-name');
    await box.scrollIntoViewIfNeeded();
    await box.screenshot({ path: path.join(outDir, `ACRO_아이콘_${name}.png`), omitBackground: true });
  }
  console.log('done');
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
