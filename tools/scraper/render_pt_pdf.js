const { chromium } = require('playwright');
const path=require('path');
const base='C:/Users/win11/Downloads/에어전트 팀/edge-company-claude-friendly-thompson-NDkKH/design-division/output/주관사PT/리허설대본.html';
const pdfOut='C:/Users/win11/Downloads/일광노르웨이숲_주관사PT_리허설대본.pdf';
(async()=>{
  const b=await chromium.launch();
  const p=await b.newPage();
  await p.goto('file://'+path.resolve(base),{waitUntil:'networkidle',timeout:40000});
  await p.waitForTimeout(1500);
  await p.pdf({path:pdfOut,format:'A4',printBackground:true,preferCSSPageSize:true});
  console.log('PDF OK ->',pdfOut);
  await b.close();
})().catch(e=>{console.error('ERR',e.message.split('\n')[0]);process.exit(1);});
