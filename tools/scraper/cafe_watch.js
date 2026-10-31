// 주관사 공고 감시(로그인 카페) — 본부장 PC의 로그인 프로필로 카페 안 '주관사' 검색 결과 글 목록을 읽어 JSON으로 출력.
// 사용: node cafe_watch.js <watch_config.json>        → stdout = [{cafe, title, link}]
//       node cafe_watch.js --login                    → 네이버 로그인 창(본부장이 직접 로그인 · 에이전트는 비번 입력 금지)
//       node cafe_watch.js <watch_config.json> --show → 창을 화면에 띄워 실행(처음 점검용)
// 카페 설정 = {name, home(카페 주소), keyword} 또는 {name, search_url(검색 결과 주소)}.
// 프로필 = tools/scraper/naver_profile (깃 제외 · 세션 쿠키)
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const PROFILE = path.join(__dirname, 'naver_profile');
const ART = /ArticleRead|\/articles\/\d+|articleid=\d+/i;
const SHOW = process.argv.includes('--show');

async function open() {
  const ctx = await chromium.launchPersistentContext(PROFILE, {
    headless: false,
    channel: 'chrome',
    viewport: { width: 1280, height: 900 },
    locale: 'ko-KR',
    timezoneId: 'Asia/Seoul',
    args: ['--disable-blink-features=AutomationControlled', '--no-first-run', '--no-default-browser-check',
      ...(SHOW ? [] : ['--window-position=-2000,0'])],
  });
  await ctx.addInitScript(() => Object.defineProperty(navigator, 'webdriver', { get: () => undefined }));
  return ctx;
}

// 카페 주소(cafe.naver.com/xxx · m.cafe.naver.com/ca-fe/xxx) → 카페 번호(clubid)
async function cafeId(page, home) {
  await page.goto(home, { waitUntil: 'domcontentloaded', timeout: 45000 });
  await page.waitForTimeout(3000);
  for (const f of page.frames()) {
    const html = await f.content().catch(() => '');
    const m = html.match(/\/cafes\/(\d{4,})/) || html.match(/clubid=(\d{4,})/i) || html.match(/"cafeId"\s*:\s*"?(\d{4,})/i)
      || html.match(/g_sClubId\s*=\s*"(\d{4,})"/);
    if (m) return m[1];
  }
  const m = page.url().match(/\/cafes\/(\d{4,})/);
  return m ? m[1] : null;
}

async function rowsOnPage(page) {
  const rows = [];
  for (const f of page.frames()) {  // 옛 카페 화면은 iframe(cafe_main) 안에 목록이 있음
    const r = await f.evaluate((src) => {
      const re = new RegExp(src, 'i');
      return [...document.querySelectorAll('a[href]')]
        .filter((a) => re.test(a.href))
        .map((a) => {
          const t = a.querySelector('strong, .tit, [class*="title"], [class*="subject"]');
          const title = ((t && t.innerText) || a.innerText || '').trim().split('\n')[0].replace(/\s+/g, ' ');
          return { title, link: a.href };
        })
        .filter((x) => x.title.length >= 4);
    }, ART.source).catch(() => []);
    rows.push(...r);
  }
  return rows;
}

// 화면 대신 모바일 카페 검색 API(로그인 쿠키 공유) — 화면 구조가 바뀌어 0건일 때 보조
async function rowsByApi(page, id, kw) {
  const url = `https://apis.naver.com/cafe-web/cafe-mobile/CafeMobileWebArticleSearchListV4?cafeId=${id}`
    + `&query=${encodeURIComponent(kw)}&searchBy=1&sortBy=date&page=1&perPage=30&adUnit=MW_CAFE_BOARD`;
  try {
    const res = await page.request.get(url, { headers: { referer: 'https://m.cafe.naver.com/' } });
    const j = await res.json();
    const list = (j.message && j.message.result && j.message.result.articleList) || [];
    return list.map((it) => {
      const a = it.item || it;
      const aid = a.articleId || a.articleid;
      return { title: String(a.subject || '').replace(/<[^>]+>/g, '').trim(),
        link: `https://m.cafe.naver.com/ca-fe/web/cafes/${id}/articles/${aid}` };
    }).filter((x) => x.title && !x.link.endsWith('/undefined'));
  } catch (e) {
    return [];
  }
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
  if (process.argv[2] === '--read') {        // 새 공고 글을 열어 본문을 읽는다 (본부장 10-31 '글에 들어가서 확인하고 알려주면 더 좋고')
    const urls = process.argv.slice(3).filter((u) => /^https?:/.test(u));
    const ctx = await open(); const page = ctx.pages()[0] || (await ctx.newPage()); const res = [];
    for (const u of urls) {
      try {
        await page.goto(u, { waitUntil: 'domcontentloaded', timeout: 45000 });
        await page.waitForTimeout(4500);
        let text = '';
        for (const f of page.frames()) {
          const t = await f.evaluate(() => {
            const el = document.querySelector('.se-main-container, .ContentRenderer, #tbody, .article_viewer, .ArticleContentBox');
            return (el ? el.innerText : '') || '';
          }).catch(() => '');
          if (t.length > text.length) text = t;
        }
        res.push({ link: u, text: text.replace(/\s+\n/g, '\n').slice(0, 6000) });
      } catch (e) { res.push({ link: u, error: String(e).slice(0, 160) }); }
    }
    await ctx.close(); console.log(JSON.stringify(res)); return;
  }
  const cfg = JSON.parse(fs.readFileSync(process.argv[2].replace(/^\uFEFF/, ''), 'utf8').replace(/^\uFEFF/, ''));
  const cafes = (cfg.cafes || []).filter((c) => c.search_url || c.home);
  const sec = cfg.section_search || [];
  const out = [];
  if (!cafes.length && !sec.length) { console.log('[]'); return; }
  const ctx = await open();
  const page = ctx.pages()[0] || (await ctx.newPage());
  // ③ 네이버 카페 전체글 검색 (본부장 10-31: section.cafe.naver.com 상단 검색 '주관사 공고' → 전체글 → 1 ~ 4쪽)
  for (const q of sec) {
    for (let pg = 1; pg <= (q.pages || 4); pg++) {
      try {
        await page.goto(`https://section.cafe.naver.com/ca-fe/home/search/articles?q=${encodeURIComponent(q.query)}&p=${pg}${q.recent ? '&od=1' : ''}`,
          { waitUntil: 'domcontentloaded', timeout: 45000 });
        await page.waitForTimeout(3500);
        const r = await page.evaluate(() => [...document.querySelectorAll('.ArticleItem')].map((it) => {
          const a = it.querySelector('a[href]'); const t = it.querySelector('.title'); const d = it.querySelector('.text');
          const cafe = it.querySelector('.cafe_info, .cafe_name, [class*="cafe_name"]');
          const date = (it.innerText.match(/20\d\d\.\d{2}\.\d{2}\./) || [''])[0];
          return { title: (t ? t.innerText : '').trim(), desc: (d ? d.innerText : '').trim().slice(0, 200),
            cafeName: (cafe ? cafe.innerText : '').trim().split('\n').pop().replace(/\s*20\d\d\.\d{2}\.\d{2}\.?$/, ''), date, link: a ? a.href : '' };
        }).filter((x) => x.title && x.link));
        for (const x of r) out.push({ cafe: `전체검색 · ${x.cafeName || '카페'}`, title: x.title, desc: x.desc, date: x.date, link: x.link, page: pg });
        if (!r.length) break;
      } catch (e) { out.push({ cafe: `전체검색 '${q.query}' ${pg}쪽`, error: String(e).slice(0, 160) }); }
    }
  }
  for (const c of cafes) {
    try {
      const kw = c.keyword || '주관사';
      let rows = [];
      if (c.search_url) {
        await page.goto(c.search_url, { waitUntil: 'domcontentloaded', timeout: 45000 });
        await page.waitForTimeout(4000);
        rows = await rowsOnPage(page);
      } else {
        const id = await cafeId(page, c.home);
        if (!id) throw new Error('카페 번호를 못 찾음(로그인 · 가입 상태 확인)');
        // PC 카페 검색(본부장 10-31 방식: 왼쪽 검색칸에 '주관사' → 전체기간 · 글+댓글 목록) → 안 되면 모바일 검색 → API
        await page.goto(`https://cafe.naver.com/f-e/cafes/${id}/menus/0?viewType=L&ta=ARTICLE_COMMENT&page=1&q=${encodeURIComponent(kw)}`,
          { waitUntil: 'domcontentloaded', timeout: 45000 });
        await page.waitForTimeout(4500);
        rows = await rowsOnPage(page);
        if (!rows.length) {
          await page.goto(`https://m.cafe.naver.com/ca-fe/web/cafes/${id}/search/articles?q=${encodeURIComponent(kw)}`,
            { waitUntil: 'domcontentloaded', timeout: 45000 });
          await page.waitForTimeout(4000);
          rows = await rowsOnPage(page);
        }
        if (!rows.length) rows = await rowsByApi(page, id, kw);
        if (!rows.length) out.push({ cafe: c.name, note: `카페 번호 ${id}` });
      }
      if (!rows.length) out.push({ cafe: c.name, error: '검색 결과 0건(결과가 정말 없거나 화면 구조 변경 — --show로 확인)', empty: true });
      for (const r of rows) out.push({ cafe: c.name, ...r });
    } catch (e) {
      out.push({ cafe: c.name, error: String(e).slice(0, 200) });
    }
  }
  await ctx.close();
  const seen = new Set();
  console.log(JSON.stringify(out.filter((r) => r.error || (!seen.has(r.link) && seen.add(r.link)))));
})();
