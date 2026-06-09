// 아크로/실링팬 네이버 직접 검색·캡처 — 회장 로그인된 디버그 Chrome(9222) 연결.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const out = path.join(__dirname, '..', '..', 'scout_reports', 'acro_gather');
fs.mkdirSync(out, { recursive: true });

const TARGETS = [
  ['1_쇼핑검색_아크로실링팬', 'https://search.shopping.naver.com/search/all?query=' + encodeURIComponent('아크로 실링팬')],
  ['2_쇼핑검색_실링팬', 'https://search.shopping.naver.com/search/all?query=' + encodeURIComponent('실링팬')],
  ['3_아크로_제품페이지', 'https://smartstore.naver.com/edge2050/products/11887564363'],
];

function autoScroll(page){return page.evaluate(async()=>{await new Promise(r=>{let t=0;const s=700;const i=setInterval(()=>{window.scrollBy(0,s);t+=s;if(t>=document.body.scrollHeight+1500){clearInterval(i);r();}},150);});});}

(async () => {
  const b = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = b.contexts()[0] || (await b.newContext());
  const page = ctx.pages()[0] || (await ctx.newPage());
  // 로그인 확인
  await page.goto('https://www.naver.com', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(2000);
  const loggedIn = await page.evaluate(() => !!document.querySelector('a[href*="logout"], .MyView-module__btn_logout, .link_login') ? true : !/로그인/.test((document.querySelector('.link_login')||{}).innerText||''));
  for (const [name, url] of TARGETS) {
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
      await page.waitForTimeout(3500);
      const body = await page.evaluate(() => document.body.innerText.slice(0, 200));
      if (/서비스 접속이 불가|접속이 일시적|nid\.naver\.com/.test(body) || /nid\.naver\.com/.test(page.url())) {
        console.log(`[BLOCKED] ${name} — 네이버 로그인 필요(디버그 창에서 로그인 후 재실행)`);
        continue;
      }
      await autoScroll(page); await page.waitForTimeout(1000);
      // ★★★ 회장 규칙(절대): 상품 상세 페이지는 반드시 '상세정보 펼쳐보기' 클릭 후 캡처 ★★★
      if (!/검색/.test(name)) {
        let clicked=false;
        for (const label of ['상세정보 펼쳐보기','상품정보 펼쳐보기','펼쳐보기']) {
          try { const btn=page.getByText(label,{exact:false}).first(); if(await btn.count()){ await btn.click({timeout:5000}); clicked=true; await page.waitForTimeout(2500); break; } } catch(e){}
        }
        console.log('   펼쳐보기 클릭:', clicked);
        for (let k=0;k<4;k++){ await autoScroll(page); await page.waitForTimeout(1200); }
      }
      await page.evaluate(() => window.scrollTo(0, 0)); await page.waitForTimeout(500);
      if (/검색/.test(name)) {
        // 검색결과는 상단(1~10위)만 잘라 캡처(긴 페이지 타임아웃 회피)
        await page.screenshot({ path: path.join(out, name + '.png'), clip: { x: 0, y: 0, width: 1900, height: 2600 }, timeout: 60000 });
      } else {
        await page.screenshot({ path: path.join(out, name + '.png'), fullPage: true, timeout: 90000 });
      }
      const text = await page.evaluate(() => document.body.innerText);
      fs.writeFileSync(path.join(out, name + '.txt'), text, 'utf8');
      console.log(`[OK] ${name}`);
    } catch (e) { console.log(`[FAIL] ${name}: ${e.message.split('\n')[0]}`); }
  }
  await b.close();
})().catch(e => { console.error('ERR', e.message.split('\n')[0]); process.exit(1); });
