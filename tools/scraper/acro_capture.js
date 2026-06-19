// 아크로 실링팬(우리) 스마트스토어 페이지 캡처 — 디버그 Chrome(9222) 연결.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const URL = 'https://smartstore.naver.com/edge2050/products/11887564363';
const out = path.join(__dirname, '..', '..', 'scout_reports', 'acro');
fs.mkdirSync(out, { recursive: true });

(async () => {
  const b = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = b.contexts()[0] || (await b.newContext());
  let page = ctx.pages().find(p => /smartstore\.naver/.test(p.url()));
  if (!page) { page = await ctx.newPage(); await page.goto(URL, { waitUntil: 'domcontentloaded', timeout: 60000 }); }
  await page.waitForTimeout(4500);
  const url = page.url();
  if (/nid\.naver\.com/.test(url)) { console.log('LOGIN_NEEDED'); await b.close(); return; }
  // 상단(제품 갤러리+가격) 뷰포트 캡처
  await page.evaluate(() => window.scrollTo(0, 0)); await page.waitForTimeout(600);
  await page.screenshot({ path: path.join(out, 'acro_top.png') });
  // 한 화면 더 내려서 옵션/요약
  await page.evaluate(() => window.scrollBy(0, 700)); await page.waitForTimeout(800);
  await page.screenshot({ path: path.join(out, 'acro_mid.png') });
  const info = await page.evaluate(() => ({
    title: document.querySelector('meta[property="og:title"]')?.content || document.title,
    img: document.querySelector('meta[property="og:image"]')?.content || '',
    price: (document.body.innerText.match(/[\d,]+\s*원/) || [''])[0],
  }));
  fs.writeFileSync(path.join(out, 'info.json'), JSON.stringify(info, null, 2), 'utf8');
  console.log('OK', JSON.stringify(info));
  await b.close();
})().catch(e => { console.error('ERR', e.message.split('\n')[0]); process.exit(1); });
