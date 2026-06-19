// 네이버 스마트스토어 경쟁사 다중 캡처 (로그인 1회 → 10개 자동)
// 로그인 세션은 naver_profile에 저장돼 재사용됨.
const { chromium } = require('playwright-extra');
const stealth = require('puppeteer-extra-plugin-stealth')();
chromium.use(stealth);
const fs = require('fs');
const path = require('path');

const profileDir = path.join(__dirname, 'naver_profile');
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
];

(async () => {
  const ctx = await chromium.launchPersistentContext(profileDir, {
    headless: false, channel: 'chrome',
    viewport: { width: 1366, height: 900 }, locale: 'ko-KR', timezoneId: 'Asia/Seoul',
    args: ['--disable-blink-features=AutomationControlled', '--no-first-run', '--no-default-browser-check', '--no-sandbox'],
  });
  const page = ctx.pages()[0] || (await ctx.newPage());

  // 1) 로그인 보장: 첫 타깃 열고, 로그인 페이지로 튕기면 대기
  await page.goto(TARGETS[0][1], { waitUntil: 'domcontentloaded', timeout: 60000 });
  let waited = 0;
  while (await needLogin(page)) {
    if (waited === 0) console.log('>>> [로그인 필요] 지금 열린 이 Chrome 창에서 네이버 로그인 해주세요. (로그인 상태 유지 체크) — 감지되면 10개 자동 캡처');
    await page.waitForTimeout(3000); waited += 3;
    if (waited >= 600) { console.log('타임아웃(10분). 다시 실행 필요.'); await ctx.close(); return; }
    if (!/smartstore\.naver\.com/.test(page.url())) {
      try { await page.goto(TARGETS[0][1], { waitUntil: 'domcontentloaded', timeout: 30000 }); } catch (e) {}
    }
  }
  console.log('>>> 로그인 확인됨. 캡처 시작.');

  // 2) 전 타깃 캡처
  for (const [name, url] of TARGETS) {
    const dir = path.join(outRoot, name);
    fs.mkdirSync(dir, { recursive: true });
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
      await page.waitForTimeout(3500);
      await autoScroll(page); await page.waitForTimeout(1500);
      await page.evaluate(() => window.scrollTo(0, 0)); await page.waitForTimeout(600);
      await autoScroll(page); await page.waitForTimeout(1200);
      await page.screenshot({ path: path.join(dir, 'fullpage.png'), fullPage: true });
      const data = await page.evaluate(() => ({
        title: document.querySelector('meta[property="og:title"]')?.content ?? document.title,
        body: document.body.innerText,
      }));
      fs.writeFileSync(path.join(dir, 'text.txt'), data.body || '', 'utf8');
      console.log(`  [OK] ${name}  (${data.title?.slice(0,30)})`);
    } catch (e) {
      console.log(`  [FAIL] ${name}: ${e.message.split('\n')[0]}`);
    }
  }
  console.log('>>> 전체 캡처 완료 ->', outRoot);
  await ctx.close();
})().catch((e) => { console.error('ERROR:', e.message.split('\n')[0]); process.exit(1); });

async function needLogin(page) {
  if (/nid\.naver\.com/.test(page.url())) return true;
  let b = ''; try { b = (await page.evaluate(() => document.body.innerText.slice(0, 400))) || ''; } catch (e) {}
  if (/서비스 접속이 불가/.test(b)) return true;
  return false;
}
function autoScroll(page) {
  return page.evaluate(async () => { await new Promise((r) => { let t = 0; const s = 700; const i = setInterval(() => { window.scrollBy(0, s); t += s; if (t >= document.body.scrollHeight + 2000) { clearInterval(i); r(); } }, 220); }); });
}
