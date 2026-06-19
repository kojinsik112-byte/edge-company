// 회장이 로그인한 '디버그 Chrome'(포트 9222)에 연결해서 경쟁사 페이지를 직접 캡처.
// Playwright가 띄우는 게 아니라 connectOverCDP로 '연결'만 → 창 안 닫힘, 봇차단 없음(실제 로그인 세션).
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const outRoot = path.join(__dirname, '..', '..', 'scout_reports', 'competitors');
fs.mkdirSync(outRoot, { recursive: true });

const TARGETS = [
  ['01_인디에어', 'https://smartstore.naver.com/main/products/6306668569'],
  ['02_모노인', 'https://smartstore.naver.com/main/products/11996262489'],
  ['03_소브코리아', 'https://smartstore.naver.com/main/products/11175145625'],
  ['04_모야무', 'https://smartstore.naver.com/main/products/8172880974'],
  ['05_신일a', 'https://smartstore.naver.com/main/products/12566003845'],
  ['06_신일b', 'https://smartstore.naver.com/main/products/13404172097'],
  ['07_신일c', 'https://smartstore.naver.com/main/products/12374927717'],
  ['08_스테이글로우', 'https://smartstore.naver.com/main/products/13467575131'],
  ['09_아크로시그니처', 'https://smartstore.naver.com/edge2050/products/11887564363'],
];

(async () => {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = browser.contexts()[0] || (await browser.newContext());
  const page = await ctx.newPage();

  // 로그인 확인
  await page.goto(TARGETS[0][1], { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(3000);
  let body = '';
  try { body = await page.evaluate(() => document.body.innerText.slice(0, 300)); } catch (e) {}
  if (/서비스 접속이 불가/.test(body) || /nid\.naver\.com/.test(page.url())) {
    console.log('아직 로그인 안 됨 / 차단. 디버그 Chrome 창에서 네이버 로그인 후 다시 실행.');
    await page.close(); await browser.close(); return;
  }
  console.log('로그인 OK. 캡처 시작.');

  for (const [name, url] of TARGETS) {
    const dir = path.join(outRoot, name);
    fs.mkdirSync(dir, { recursive: true });
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
      await page.waitForTimeout(3500);
      // 초기 스크롤로 '상세정보 펼쳐보기' 버튼 영역까지 내려가 로드
      await autoScroll(page); await page.waitForTimeout(1200);
      // ★ 상세정보 펼쳐보기 클릭 (여러 후보 텍스트)
      for (const label of ['상세정보 펼쳐보기', '상품정보 펼쳐보기', '펼쳐보기']) {
        try {
          const btn = page.getByText(label, { exact: false }).first();
          if (await btn.count()) { await btn.click({ timeout: 4000 }); await page.waitForTimeout(2000); break; }
        } catch (e) {}
      }
      // 펼친 뒤 지연로딩 이미지 끝까지 로드 (여러 패스)
      for (let k = 0; k < 4; k++) { await autoScroll(page); await page.waitForTimeout(1200); }
      await page.evaluate(() => window.scrollTo(0, 0)); await page.waitForTimeout(500);
      await autoScroll(page); await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(dir, 'fullpage.png'), fullPage: true });
      const data = await page.evaluate(() => ({
        title: document.querySelector('meta[property="og:title"]')?.content ?? document.title,
        body: document.body.innerText,
      }));
      fs.writeFileSync(path.join(dir, 'text.txt'), data.body || '', 'utf8');
      console.log(`  [OK] ${name}  (${(data.title||'').slice(0,28)})`);
    } catch (e) { console.log(`  [FAIL] ${name}: ${e.message.split('\n')[0]}`); }
  }
  console.log('완료 ->', outRoot);
  await page.close();
  await browser.close(); // 연결만 끊음 (Chrome 창은 안 닫힘)
})().catch((e) => { console.error('ERROR:', e.message.split('\n')[0]); process.exit(1); });

function autoScroll(page) {
  return page.evaluate(async () => { await new Promise((r) => { let t = 0; const s = 800; const i = setInterval(() => { window.scrollBy(0, s); t += s; if (t >= document.body.scrollHeight + 2000) { clearInterval(i); r(); } }, 200); }); });
}
