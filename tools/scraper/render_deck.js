const { chromium } = require('playwright');
const path=require('path'),fs=require('fs');
const f='file://'+path.resolve('C:/Users/win11/Downloads/에어전트 팀/edge-company-claude-friendly-thompson-NDkKH/design-division/output/주관사PT/deck.html');
const out='C:/Users/win11/Downloads/에어전트 팀/edge-company-claude-friendly-thompson-NDkKH/design-division/output/주관사PT/slides';
fs.mkdirSync(out,{recursive:true});
(async()=>{
  const b=await chromium.launch();
  const p=await b.newPage({viewport:{width:1280,height:720},deviceScaleFactor:2});
  await p.goto(f,{waitUntil:'networkidle',timeout:40000});
  await p.waitForTimeout(1500);
  let n=0;
  for(let i=1;i<=40;i++){
    const el=await p.$('#s'+i);
    if(!el){continue;}
    await el.screenshot({path:`${out}/s${String(i).padStart(2,'0')}.png`});
    n++;
  }
  console.log('rendered',n,'slides');
  await b.close();
})().catch(e=>{console.error('ERR',e.message.split('\n')[0]);process.exit(1);});
