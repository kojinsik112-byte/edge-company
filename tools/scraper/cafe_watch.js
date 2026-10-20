// 주관사 공고 감시(로그인 카페 4곳) — 본부장 PC의 로그인 프로필로 카페 안 검색 결과 글 목록을 읽어 JSON으로 출력.
// 사용: node cafe_watch.js <watch_config.json>        → stdout = [{cafe, title, link}]
//       node cafe_watch.js --login                    → 네이버 로그인 창(본부장이 직접 로그인 · 에이전트는 비번 입력 금지)
// 프로필 = tools/scraper/naver_profile (깃 제외 · 세션 쿠키)
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const PROFILE = path.join(__dirname, 'naver_profile');
const ART = /ArticleRead|\/articles\/\d+|articleid=\d+/i;

async function open() {
  const ctx = await chromium.launchPersistentContext(PROFILE, {
    headless: false,
    channel: 'chrome',
    viewport: { width: 1280, height: 900 },
    locale: 'ko-KR',
    timezoneId: 'Asia/Seoul',
    args: ['--disable-blink-features=AutomationControlled', '--no-first-run', '--no-default-browser-check', '--window-position=-2000,0'],
  });
  await ctx.addInitScript(() => Object.defineProperty(navigator, 'webdriver', { get: () => undefined }));
  return ctx;
}

(async () => {
  if (process.argv[2] === '--login') {
    const ctx = await open();
    const page = ctx.pages()[0] || (await ctx.newPage());
    await page.goto('https://nid.naver.com/nidlogin.login');
    console.error('네이버에 로그인한 뒤 창을 닫으세요(로그인 상태가 프로필에 저장됩니다).');
    await new Promise((r) => ctx.on('close', r));
    return;
  }
  const cfg = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const cafes = (cfg.cafes || []).filter((c) => c.search_url);
  const out = [];
  if (!cafes.length) { console.log('[]'); return; }
  const ctx = await open();
  const page = ctx.pages()[0] || (await ctx.newPage());
  for (const c of cafes) {
    try {
      await page.goto(c.search_url, { waitUntil: 'domcontentloaded', timeout: 45000 });
      await page.waitForTimeout(4000);
      for (const f of page.frames()) {  // 옛 카페 화면은 iframe(cafe_main) 안에 목록이 있음
        const rows = await f.evaluate((src) => {
          const re = new RegExp(src, 'i');
          return [...document.querySelectorAll('a[href]')]
            .filter((a) => re.test(a.href) && a.innerText.trim().length >= 4)
            .map((a) => ({ title: a.innerText.trim().replace(/\s+/g, ' '), link: a.href }));
        }, ART.source).catch(() => []);
        for (const r of rows) out.push({ cafe: c.name, ...r });
      }
    } catch (e) {
      out.push({ cafe: c.name, error: String(e).slice(0, 200) });
    }
  }
  await ctx.close();
  const seen = new Set();
  console.log(JSON.stringify(out.filter((r) => r.error || (!seen.has(r.link) && seen.add(r.link)))));
})();
