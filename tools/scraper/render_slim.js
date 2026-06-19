const { chromium } = require('playwright');
const path=require('path');
const f='file://'+path.resolve('C:/Users/win11/Downloads/에어전트 팀/edge-company-claude-friendly-thompson-NDkKH/design-division/output/슬림아크로/slim_v2.html');
(async()=>{
  const b=await chromium.launch();
  const p=await b.newPage({viewport:{width:1080,height:1200},deviceScaleFactor:1.5});
  await p.goto(f,{waitUntil:'networkidle',timeout:30000});
  await p.waitForTimeout(1200);
  const out='C:/Users/win11/Downloads/에어전트 팀/edge-company-claude-friendly-thompson-NDkKH/design-division/output/슬림아크로/slim_v2.png';
  await p.screenshot({path:out,fullPage:true});
  const h=await p.evaluate(()=>document.body.scrollHeight);
  console.log('OK rendered, page height',h);
  await b.close();
})().catch(e=>{console.error('ERR',e.message.split('\n')[0]);process.exit(1);});
