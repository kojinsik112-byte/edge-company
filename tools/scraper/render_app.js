const { chromium } = require('playwright');
const path=require('path');
const APP='file://'+path.resolve('C:/Users/win11/Downloads/_edgeapp/app/index.html');
(async()=>{
  const b=await chromium.launch();
  const ctx=await b.newContext({viewport:{width:402,height:874},deviceScaleFactor:2,isMobile:true});
  const page=await ctx.newPage();
  const logs=[];page.on('console',m=>logs.push(m.text()));
  await page.goto(APP,{waitUntil:'networkidle',timeout:30000});
  await page.waitForTimeout(1200);
  const out='C:/Users/win11/Downloads/_edgeapp/shots';
  require('fs').mkdirSync(out,{recursive:true});
  await page.screenshot({path:out+'/01_landing.png'});
  // 페이지 내 버튼/텍스트 수집
  const info=await page.evaluate(()=>{
    const txt=document.body.innerText.slice(0,800);
    const btns=[...document.querySelectorAll('button')].map(b=>b.innerText.trim()).filter(Boolean).slice(0,30);
    return {txt,btns};
  });
  console.log('=== 첫화면 텍스트 ===');console.log(info.txt);
  console.log('=== 버튼들 ===');console.log(info.btns.join(' | '));
  console.log('=== console errors ===');console.log(logs.slice(0,10).join('\n'));
  await b.close();
})().catch(e=>{console.error('ERR',e.message.split('\n')[0]);process.exit(1);});
