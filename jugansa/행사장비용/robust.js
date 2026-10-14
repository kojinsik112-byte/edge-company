const {chromium}=require('playwright');
const [,,file]=process.argv;
(async()=>{const b=await chromium.launch();
const ctx=await b.newContext({viewport:{width:1200,height:1400}});
const res=[];
async function run(label,ls,act){
  const p=await ctx.newPage();const errs=[];
  p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>m.type()==='error'&&!/CERT|ERR_/.test(m.text())&&errs.push(m.text()));
  await p.goto('file://'+file);
  if(ls!==undefined){await p.evaluate(v=>{if(v===null)localStorage.removeItem('venue-cost:v3');else localStorage.setItem('venue-cost:v3',v)},ls);await p.reload();}
  await p.waitForTimeout(150);
  if(act)await act(p);
  const txt=await p.evaluate(()=>document.body.innerText);
  const bad=/NaN|undefined|Infinity|null/.test(txt);
  res.push([label,errs.length?errs:'ok',bad?'BAD TEXT':'clean']);
  await p.close();
}
await run('깨진 JSON','{oops');
await run('배열','[1,2]');
await run('이상한 타입',JSON.stringify({reg:5,sea:'x',hvac:'no',hrs:'abc',rent:-3,show:99,hh:'1e9',cnt:3,util:'x',prog:-5,mul:9,sel:{},ovr:[1]}));
await run('ovr 이상',JSON.stringify({ovr:{'BEXCO|제1전시장 2A':-5,'없는홀':100,'SETEC|2관':'abc','COEX|B2':1e12}}));
await run('세대 0',null,async p=>{await p.fill('#hh','0')});
await run('세대 음수',null,async p=>{await p.fill('#hh','-500')});
await run('세대 거대',null,async p=>{await p.fill('#hh','99999999')});
await run('진행비 빈칸',null,async p=>{await p.fill('#prog','')});
await run('일수 경계',null,async p=>{const c=s=>p.evaluate(s=>document.querySelector(s).click(),s);for(let i=0;i<12;i++)await c('.stp button[data-k="show"][data-d="1"]');console.log('show7',await p.textContent('#showV'),await p.textContent('#rentV'));for(let i=0;i<12;i++)await c('.stp button[data-k="rent"][data-d="-1"]');console.log('rent min',await p.textContent('#rentV'),await p.textContent('#showV'));for(let i=0;i<10;i++)await c('.stp button[data-k="hrs"][data-d="1"]');console.log('hrs',await p.textContent('#hrsV'))});
await run('견적필요 지역 선택+견적',null,async p=>{await p.click('#regs button[data-v="충청"]');await p.click('#vl button[data-id="정부세종컨벤션센터|기획전시장"]');await p.fill('#ovr','1800.5');await p.press('#ovr','Enter');await p.click('#vl button[data-id="정부세종컨벤션센터|기획전시장"]')});
await run('XSS 저장값',JSON.stringify({sel:'<img src=x onerror=window.__x=1>',reg:'<b>x</b>',ovr:{'<img src=x onerror=window.__x=1>':5}}),async p=>{console.log('xss fired',await p.evaluate(()=>!!window.__x||!!document.querySelector('img[src=x]')))});
await run('2곳 mul 전환',null,async p=>{await p.fill('#hh','2000');for(const v of ['rent','ru','all'])await p.selectOption('#mul',v)});
await run('봄가을+사용+설치일',null,async p=>{await p.click('#sea button[data-v="spr"]');await p.click('#hvac button[data-v="1"]');await p.click('#setupHv button[data-v="1"]');for(const r of ['수도권','충청','강원','경상','전라','제주'])await p.click(`#regs button[data-v="${r}"]`)});
console.log(res.map(r=>r.join(' | ')).join('\n'));
await b.close();})();
