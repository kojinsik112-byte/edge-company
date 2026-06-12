// 네이버쇼핑 '실링팬' 실제 랭킹순 추출 (로그인 디버그 Chrome 9222, __NEXT_DATA__ 파싱)
const { chromium } = require('playwright');
const KW = process.argv[2] || '실링팬';
(async () => {
  const b = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = b.contexts()[0] || (await b.newContext());
  const page = ctx.pages()[0] || (await ctx.newPage());
  await page.goto('https://search.shopping.naver.com/search/all?query=' + encodeURIComponent(KW),
    { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(4500);
  // 결과 로드 위해 스크롤
  for (let k = 0; k < 4; k++) { await page.evaluate(() => window.scrollBy(0, 1400)); await page.waitForTimeout(900); }
  await page.evaluate(() => window.scrollTo(0, 0)); await page.waitForTimeout(500);
  const head = await page.evaluate(() => document.body.innerText.slice(0, 120));
  if (/서비스 접속이 불가|일시적|nid\.naver/.test(head) || /nid\.naver/.test(page.url())) {
    console.log('BLOCKED 또는 로그인 필요'); await b.close(); return;
  }
  const items = await page.evaluate(() => {
    const seen = new Set(), out = [];
    document.querySelectorAll('a[href]').forEach(a => {
      const h = a.href || '';
      if (/(smartstore\.naver|shopping\.naver\.com\/(catalog|adcr|product)|cr\.shopping\.naver)/.test(h)) {
        const t = (a.innerText || '').replace(/\s+/g, ' ').trim();
        if (t.length >= 8 && t.length <= 80 && /[가-힣]/.test(t) && !seen.has(t)) { seen.add(t); out.push(t); }
      }
    });
    return out.slice(0, 15);
  });
  await b.close();
  console.log('=== 네이버쇼핑 "' + KW + '" 노출 순서(상단부터) ===');
  if (!items.length) { console.log('상품 추출 실패 — 셀렉터/구조 변경'); return; }
  items.forEach((t, i) => console.log(`${i + 1}. ${t}`));
})().catch(e => { console.error('ERR', e.message.split('\n')[0]); process.exit(1); });
