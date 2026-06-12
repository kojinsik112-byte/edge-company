// Naver SmartStore 상세페이지 스크래퍼 (Playwright)
// 사용: node naver_scrape.js <url> <outDir>
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const url = process.argv[2];
const outDir = process.argv[3] || './out';
fs.mkdirSync(outDir, { recursive: true });

(async () => {
  const browser = await chromium.launch({
    headless: false,
    channel: 'chrome',
    args: ['--disable-blink-features=AutomationControlled'],
  });
  const ctx = await browser.newContext({
    userAgent:
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    viewport: { width: 1366, height: 900 },
    locale: 'ko-KR',
    timezoneId: 'Asia/Seoul',
    extraHTTPHeaders: {
      'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
      Referer: 'https://search.shopping.naver.com/',
    },
  });
  // 자동화 탐지 회피
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'languages', { get: () => ['ko-KR', 'ko', 'en'] });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
    window.chrome = { runtime: {} };
  });
  const page = await ctx.newPage();
  // 네이버 메인을 먼저 거쳐 쿠키 확보
  try {
    await page.goto('https://www.naver.com', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(1500);
  } catch (e) {}
  console.log('navigating:', url);
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });

  // 상품명/가격 등 상단 정보 대기
  await page.waitForTimeout(4000);

  // 페이지 끝까지 점진 스크롤 → 지연 로딩 이미지 트리거
  await autoScroll(page);
  await page.waitForTimeout(2000);
  // 다시 위로 올렸다 내려 안정화
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(1000);
  await autoScroll(page);
  await page.waitForTimeout(1500);

  // 1) 풀페이지 스크린샷
  const shotPath = path.join(outDir, 'fullpage.png');
  await page.screenshot({ path: shotPath, fullPage: true });
  console.log('screenshot saved:', shotPath);

  // 2) 텍스트 추출 (상단 정보 + 상세설명 영역)
  const data = await page.evaluate(() => {
    const t = (sel) => {
      const el = document.querySelector(sel);
      return el ? el.innerText.trim() : null;
    };
    // 상품명 후보
    const title =
      t('h3._22kNQuEXmb') ||
      t('h3') ||
      (document.querySelector('meta[property="og:title"]')?.content ?? null);
    // 가격 후보
    const priceText = document.body.innerText.match(/[\d,]+\s*원/g)?.slice(0, 5) || [];
    // 상세설명 컨테이너 후보 텍스트
    const detail =
      document.querySelector('#INTRODUCE') ||
      document.querySelector('._2-I30XS1lA') ||
      document.querySelector('div[class*="detail"]');
    const ogTitle = document.querySelector('meta[property="og:title"]')?.content ?? null;
    const ogDesc = document.querySelector('meta[property="og:description"]')?.content ?? null;
    // 이미지 alt / src 목록 (상세 이미지 순서 파악용)
    const imgs = Array.from(document.images)
      .map((im) => ({ src: im.currentSrc || im.src, alt: im.alt }))
      .filter((o) => o.src && /phinf|pstatic|naver/.test(o.src));
    return {
      title,
      ogTitle,
      ogDesc,
      priceCandidates: priceText,
      detailText: detail ? detail.innerText.trim().slice(0, 8000) : null,
      bodySnippet: document.body.innerText.slice(0, 4000),
      imageCount: imgs.length,
      images: imgs.slice(0, 60),
    };
  });

  fs.writeFileSync(path.join(outDir, 'data.json'), JSON.stringify(data, null, 2), 'utf8');
  fs.writeFileSync(path.join(outDir, 'bodytext.txt'), data.bodySnippet || '', 'utf8');
  console.log('data saved. title=', data.title, '| images=', data.imageCount);

  await browser.close();
})().catch((e) => {
  console.error('ERROR:', e.message);
  process.exit(1);
});

function autoScroll(page) {
  return page.evaluate(async () => {
    await new Promise((resolve) => {
      let total = 0;
      const step = 600;
      const timer = setInterval(() => {
        window.scrollBy(0, step);
        total += step;
        if (total >= document.body.scrollHeight + 2000) {
          clearInterval(timer);
          resolve();
        }
      }, 250);
    });
  });
}
