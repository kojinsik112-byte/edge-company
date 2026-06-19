const { chromium } = require('playwright');
const path=require('path');
const APP='file://'+path.resolve('C:/Users/win11/Downloads/_edgeapp/app/index.html');
const out='C:/Users/win11/Downloads/_edgeapp/shots';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function shot(p,n){await sleep(700);await p.screenshot({path:`${out}/${n}.png`});console.log('shot',n);}
async function clickText(p,t){const el=p.getByText(t,{exact:false}).first();if(await el.count()){await el.click({timeout:4000}).catch(()=>{});return true;}return false;}
(async()=>{
  const b=await chromium.launch();
  const ctx=await b.newContext({viewport:{width:402,height:874},deviceScaleFactor:2,isMobile:true});
  const p=await ctx.newPage();
  p.on('dialog',d=>d.accept().catch(()=>{}));
  await p.goto(APP,{waitUntil:'networkidle',timeout:30000});await sleep(900);
  await clickText(p,'입주민');await clickText(p,'시작하기');await sleep(700);
  const sel=await p.$('select'); if(sel){const v=await p.$$eval('select option',o=>o.map(x=>x.value));await sel.selectOption(v.find(x=>x)||v[1]).catch(()=>{});}
  const ins=await p.$$('input');const vals=['101','1502','김입주','010','1234','5678'];
  for(let i=0;i<ins.length&&i<vals.length;i++)await ins[i].fill(vals[i]).catch(()=>{});
  await clickText(p,'인증번호 받기');await sleep(800);
  const code=p.getByPlaceholder('6자리 인증번호 입력').first();
  if(await code.count())await code.fill('123456').catch(()=>{});
  await sleep(300);
  await clickText(p,'입장하기');await sleep(1200);     // ← 핵심 수정
  await shot(p,'20_home');
  await p.evaluate(()=>window.scrollTo(0,520));await shot(p,'21_home2');
  await p.evaluate(()=>window.scrollTo(0,1100));await shot(p,'22_home3');
  await p.evaluate(()=>window.scrollTo(0,0));await sleep(300);
  await clickText(p,'조명');await sleep(900);await shot(p,'23_category');
  for(const nm of ['엣지컴퍼니','휴젠트','한샘','메가창']){if(await clickText(p,nm))break;}
  await sleep(900);await shot(p,'24_vendor');
  await p.evaluate(()=>window.scrollBy(0,650));await shot(p,'25_vendor2');
  // 하단 탭 탐색: 견적/후기/마이/AS 등
  console.log('=== home text ===');console.log(await p.evaluate(()=>document.body.innerText.slice(0,600)));
  await b.close();
})().catch(e=>{console.error('ERR',e.message.split('\n')[0]);process.exit(1);});
