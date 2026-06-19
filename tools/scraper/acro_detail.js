// 아크로 제품 상세 '펼쳐보기' 클릭 후 풀캡처 (회장 규칙: 반드시 상세정보 펼쳐보기 클릭!)
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const URL = 'https://smartstore.naver.com/edge2050/products/11887564363';
const out = path.join(__dirname, '..', '..', 'scout_reports', 'acro_gather');
fs.mkdirSync(out, { recursive: true });
function autoScroll(page){return page.evaluate(async()=>{await new Promise(r=>{let t=0;const s=800;const i=setInterval(()=>{window.scrollBy(0,s);t+=s;if(t>=document.body.scrollHeight+2000){clearInterval(i);r();}},180);});});}
(async () => {
  const b = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = b.contexts()[0] || (await b.newContext());
  const page = ctx.pages().find(p=>/edge2050\/products/.test(p.url())) || (await ctx.newPage());
  await page.goto(URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(3500);
  if (/nid\.naver\.com|서비스 접속이 불가/.test(page.url()+await page.evaluate(()=>document.body.innerText.slice(0,150)))) { console.log('LOGIN_NEEDED'); await b.close(); return; }
  await autoScroll(page); await page.waitForTimeout(1200);
  // ★ 상세정보 펼쳐보기 클릭 (회장 규칙)
  let clicked=false;
  for (const label of ['상세정보 펼쳐보기','상품정보 펼쳐보기','펼쳐보기']) {
    try { const btn=page.getByText(label,{exact:false}).first(); if(await btn.count()){ await btn.click({timeout:5000}); clicked=true; await page.waitForTimeout(2500); break; } } catch(e){}
  }
  console.log('펼쳐보기 클릭:', clicked);
  for (let k=0;k<5;k++){ await autoScroll(page); await page.waitForTimeout(1300); }
  // 텍스트 먼저 저장(스크린샷 실패해도 보존)
  fs.writeFileSync(path.join(out,'아크로_상세_펼침.txt'), await page.evaluate(()=>document.body.innerText), 'utf8');
  // ★ 화면 단위 분할 캡처(캔버스 한계 회피)
  const seg = path.join(out,'아크로_상세_세그먼트'); fs.mkdirSync(seg,{recursive:true});
  const vh = await page.evaluate(()=>window.innerHeight);
  const total = await page.evaluate(()=>document.body.scrollHeight);
  let y=0, i=0;
  while (y < total && i < 45) {
    await page.evaluate((yy)=>window.scrollTo(0,yy), y); await page.waitForTimeout(450);
    try { await page.screenshot({ path: path.join(seg, String(i).padStart(2,'0')+'.png'), timeout:30000 }); } catch(e){ console.log('seg',i,'skip'); }
    y += vh - 40; i++;
  }
  console.log('OK 분할캡처:', i, '장 ->', seg);
  await b.close();
})().catch(e=>{console.error('ERR',e.message.split('\n')[0]);process.exit(1);});
