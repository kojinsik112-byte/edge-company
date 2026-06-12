// 네이버 상세페이지 캡처기 (로그인 1회 → 영구 재사용)
// 고정 프로필(naver_profile)에 로그인 세션을 저장해, 다음부터는 로그인 없이 캡처.
//
// 사용:
//   node naver_capture.js "<상품 URL>" "<출력폴더>"
// 최초 1회: 창이 뜨면 회장님이 직접 네이버 로그인 ("로그인 상태 유지" 체크).
//   로그인되어 상품페이지가 보이면 스크립트가 자동으로 캡처 후 종료.
// 이후: 같은 명령만 실행하면 로그인 단계 없이 바로 캡처.

const { chromium } = require('playwright-extra');
const stealth = require('puppeteer-extra-plugin-stealth')();
chromium.use(stealth);
const fs = require('fs');
const path = require('path');

const url = process.argv[2];
const outDir = process.argv[3] || './out';
const profileDir = path.join(__dirname, 'naver_profile');
fs.mkdirSync(outDir, { recursive: true });
fs.mkdirSync(profileDir, { recursive: true });

(async () => {
  const ctx = await chromium.launchPersistentContext(profileDir, {
    headless: false,
    channel: 'chrome',
    viewport: { width: 1366, height: 900 },
    locale: 'ko-KR',
    timezoneId: 'Asia/Seoul',
    args: ['--disable-blink-features=AutomationControlled', '--no-first-run', '--no-default-browser-check'],
  });
  const page = ctx.pages()[0] || (await ctx.newPage());
  console.log('navigating:', url);
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });

  // 차단/로그인 상태면 회장님 수동 로그인 대기 (최대 5분)
  let waited = 0;
  while (await needsLogin(page, url)) {
    if (waited === 0) console.log('>>> 로그인 필요: 열린 Chrome 창에서 직접 네이버 로그인 해주세요 ("로그인 상태 유지" 체크). 자동 감지 후 캡처합니다...');
    await page.waitForTimeout(3000);
    waited += 3;
    if (waited >= 600) { console.log('타임아웃: 10분 내 로그인 안 됨. 다시 실행해 주세요.'); break; }
    if (!/smartstore\.naver\.com/.test(page.url())) {
      try { await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 }); } catch (e) {}
    }
  }

  await page.waitForTimeout(3000);
  await autoScroll(page);
  await page.waitForTimeout(2000);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(800);
  await autoScroll(page);
  await page.waitForTimeout(1500);

  await page.screenshot({ path: path.join(outDir, 'fullpage.png'), fullPage: true });
  const data = await page.evaluate(() => {
    const big = (s) => s.replace(/\?type=.*$/, '').replace(/_\d+\.(jpg|png)/i, '.$1');
    const urls = Array.from(document.images)
      .map((i) => i.currentSrc || i.src)
      .filter((s) => /phinf|pstatic/.test(s) && !/static\.|icon|logo|blank/.test(s));
    return {
      title: document.querySelector('meta[property="og:title"]')?.content ?? document.title,
      ogDesc: document.querySelector('meta[property="og:description"]')?.content ?? null,
      bodyText: document.body.innerText,
      imageCount: document.images.length,
      detailImgs: Array.from(new Set(urls)),
      detailImgsBig: Array.from(new Set(urls.map(big))),
    };
  });
  fs.writeFileSync(path.join(outDir, 'bodytext.txt'), data.bodyText || '', 'utf8');
  fs.writeFileSync(path.join(outDir, 'data.json'), JSON.stringify({ ...data, bodyText: undefined }, null, 2), 'utf8');

  // 실제 제품 이미지 다운로드 (브라우저 쿠키로 fetch)
  const imgDir = path.join(outDir, 'product_images');
  fs.mkdirSync(imgDir, { recursive: true });
  const api = ctx.request;
  let saved = 0;
  const list = data.detailImgs;
  for (let i = 0; i < list.length; i++) {
    try {
      const resp = await api.get(list[i]);
      if (!resp.ok()) continue;
      const buf = await resp.body();
      if (buf.length < 8000) continue; // 아이콘류 제외
      const ext = (list[i].match(/\.(jpg|jpeg|png|gif|webp)/i) || [, 'jpg'])[1];
      fs.writeFileSync(path.join(imgDir, `img_${String(i).padStart(3, '0')}.${ext}`), buf);
      saved++;
    } catch (e) {}
  }
  console.log('DONE. title=', data.title, '| images=', data.imageCount, '| 저장된 제품이미지=', saved);
  await ctx.close();
})().catch((e) => { console.error('ERROR:', e.message.split('\n')[0]); process.exit(1); });

async function needsLogin(page, url) {
  const u = page.url();
  if (/nid\.naver\.com/.test(u)) return true; // 로그인 페이지
  let body = '';
  try { body = (await page.evaluate(() => document.body.innerText.slice(0, 400))) || ''; } catch (e) {}
  if (/서비스 접속이 불가/.test(body)) return true; // 봇 차단 페이지
  // 상품 페이지 도달(상품명/가격 영역) → 통과
  if (/smartstore\.naver\.com\/.+\/products\//.test(u)) return false;
  return false;
}
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
