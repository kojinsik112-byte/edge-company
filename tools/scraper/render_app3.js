const { chromium } = require('playwright');
const path=require('path');
const APP='file://'+path.resolve('C:/Users/win11/Downloads/_edgeapp/app/index.html');
const out='C:/Users/win11/Downloads/_edgeapp/shots';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function shot(p,n){await sleep(600);await p.screenshot({path:`${out}/${n}.png`});console.log('shot',n);}
async function clickText(p,t){const el=p.getByText(t,{exact:false}).first();if(await el.count()){await el.click({timeout:4000}).catch(()=>{});return true;}return false;}
(async()=>{
  const b=await chromium.launch();
  const ctx=await b.newContext({viewport:{width:402,height:874},deviceScaleFactor:2,isMobile:true});
  const p=await ctx.newPage();
  p.on('dialog',d=>d.accept().catch(()=>{}));   // alert 자동 확인
  await p.goto(APP,{waitUntil:'networkidle',timeout:30000});await sleep(900);
  await clickText(p,'입주민');await clickText(p,'시작하기');await sleep(700);
  // select dropdown
  const sel=await p.$('select'); if(sel){const v=await p.$$eval('select option',o=>o.map(x=>x.value));await sel.selectOption(v.find(x=>x)||v[1]).catch(()=>{});}
  const ins=await p.$$('input');
  console.log('inputs',ins.length);
  // [0]동 [1]호수 [2]이름 [3]010 [4]mid [5]last  (010 프리필 가정)
  const vals=['101','1502','김입주','010','1234','5678'];
  for(let i=0;i<ins.length&&i<vals.length;i++){await ins[i].fill(vals[i]).catch(()=>{});}
  await shot(p,'10_auth');
  await clickText(p,'인증번호 받기');await sleep(700);await shot(p,'11_code');
  // 6자리 코드: 새로 나타난 input(들)
  const ins2=await p.$$('input');
  if(ins2.length>=6){for(let i=ins2.length-6;i<ins2.length;i++)await ins2[i].fill('1').catch(()=>{});}
  else if(ins2.length)await ins2[ins2.length-1].fill('123456').catch(()=>{});
  await clickText(p,'인증 확인');await sleep(700);
  await clickText(p,'동의하고 계속하기');await sleep(500);
  await clickText(p,'다음 단계');await sleep(700);await shot(p,'12_danji');
  await clickText(p,'창원 센트럴 아이파크');await sleep(1000);await shot(p,'13_main');
  await p.evaluate(()=>window.scrollBy(0,650));await shot(p,'14_main2');
  await p.evaluate(()=>window.scrollTo(0,0));await sleep(300);
  await clickText(p,'조명');await sleep(800);await shot(p,'15_category');
  for(const nm of ['휴젠트','한샘','메가창','감각줄눈']){if(await clickText(p,nm))break;}
  await sleep(800);await shot(p,'16_vendor');
  await p.evaluate(()=>window.scrollBy(0,600));await shot(p,'17_vendor2');
  console.log('=== now ===');console.log(await p.evaluate(()=>document.body.innerText.slice(0,400)));
  await b.close();
})().catch(e=>{console.error('ERR',e.message.split('\n')[0]);process.exit(1);});
