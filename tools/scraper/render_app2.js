const { chromium } = require('playwright');
const path=require('path'),fs=require('fs');
const APP='file://'+path.resolve('C:/Users/win11/Downloads/_edgeapp/app/index.html');
const out='C:/Users/win11/Downloads/_edgeapp/shots';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function shot(p,n){await sleep(700);await p.screenshot({path:`${out}/${n}.png`});console.log('shot',n);}
async function clickText(p,t){
  const el=p.getByText(t,{exact:false}).first();
  if(await el.count()){await el.click({timeout:4000}).catch(()=>{});return true;}
  return false;
}
(async()=>{
  const b=await chromium.launch();
  const ctx=await b.newContext({viewport:{width:402,height:874},deviceScaleFactor:2,isMobile:true});
  const p=await ctx.newPage();
  await p.goto(APP,{waitUntil:'networkidle',timeout:30000});
  await sleep(900);
  // 입주민 선택 + 시작하기
  await clickText(p,'입주민');
  await clickText(p,'시작하기');await sleep(600);
  // 입력칸 채우기
  const inputs=await p.$$('input');
  console.log('inputs found',inputs.length);
  if(inputs[0]) await inputs[0].fill('김입주').catch(()=>{});
  if(inputs[1]) await inputs[1].fill('01012345678').catch(()=>{});
  await shot(p,'10_auth');
  await clickText(p,'인증번호 받기');await sleep(600);
  // 6자리 입력 (단일 또는 6칸)
  const ins2=await p.$$('input');
  if(ins2.length>=6){for(let i=ins2.length-6;i<ins2.length;i++){await ins2[i].fill(String((i)%10)).catch(()=>{});}}
  else if(ins2.length){await ins2[ins2.length-1].fill('123456').catch(()=>{});}
  await shot(p,'11_code');
  await clickText(p,'인증 확인');await sleep(500);
  await clickText(p,'동의하고 계속하기');await sleep(500);
  await clickText(p,'다음 단계');await sleep(700);
  await shot(p,'12_danji');
  // 단지 선택: 창원 센트럴 아이파크 (LIVE)
  await clickText(p,'창원 센트럴 아이파크');await sleep(900);
  await shot(p,'13_main');
  // 스크롤 더
  await p.evaluate(()=>window.scrollBy(0,700));await shot(p,'14_main2');
  await p.evaluate(()=>window.scrollTo(0,0));
  // 카테고리 조명 클릭
  await clickText(p,'조명');await sleep(800);await shot(p,'15_category');
  // 첫 업체 카드 클릭 시도
  const cards=await p.$$('[class*=card],[class*=Card]');
  // 업체명 텍스트로 클릭
  for(const nm of ['휴젠트','한샘','감각줄눈','메가창']){if(await clickText(p,nm)){break;}}
  await sleep(800);await shot(p,'16_vendor');
  await p.evaluate(()=>window.scrollBy(0,600));await shot(p,'17_vendor2');
  const finalTxt=await p.evaluate(()=>document.body.innerText.slice(0,500));
  console.log('=== 현재화면 ===');console.log(finalTxt);
  await b.close();
})().catch(e=>{console.error('ERR',e.message.split('\n')[0]);process.exit(1);});
