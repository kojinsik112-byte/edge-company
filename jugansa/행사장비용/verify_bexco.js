// BEXCO 전시장 사용료 정산서 2건(2025.12 · 2026.05)과 모델 대조 — node verify_bexco.js
// 정산서는 깃 제외(개인정보 포함). 아래 숫자는 정산서·사용일지에 적힌 값(공급가, 원).
const M=require('./model4.js'),U=require('./units.json');
const CASES=[
  {name:'2025.12 오션시티 4B', id:'BEXCO|제2전시장 4홀 1칸(4B)', sea:'jan', rent:3, show:2, hrs:6.25 /* 운전 9h + 3.5h */,
   E:1950 /* 2025 단가 */, actual:{rent:8536320, el:287216, kwh:1238, hv:592800, waste:387011}},
  {name:'2026.05 에코델타 디에트르 4E+4F', id:'BEXCO|제2전시장 4홀 2칸(4E+4F)', sea:'spr', rent:4, show:3, hrs:9, hvOff:true,
   actual:{rent:29008320, el:558545, kwh:3305, hv:0, waste:580516}},
];
const TOL={rent:0, hv:0, el:0.10, kwh:0.10, waste:0.10};
let fails=0;
for(const c of CASES){
  let x=U.find(u=>u.id===c.id); if(!x){console.log('NO UNIT',c.id);fails++;continue}
  if(c.E){x=JSON.parse(JSON.stringify(x));x[c.sea].E=c.E}
  const r=M.costOf(x,c.sea,{rent:c.rent,show:c.show,hrs:c.hrs,elm:'area',elx:1,setupHv:false});
  const got={rent:r.rent, el:r.el, kwh:r.kwh, hv:c.hvOff?0:r.hv, waste:r.waste};
  console.log('==',c.name);
  for(const k of Object.keys(c.actual)){
    const a=c.actual[k],g=got[k],e=a===0?Math.abs(g):Math.abs(g-a)/a,ok=e<=TOL[k]+1e-9;
    if(!ok)fails++;
    console.log(`${ok?'OK  ':'FAIL'} ${k.padEnd(5)} 실측 ${a.toLocaleString()} · 모델 ${Math.round(g).toLocaleString()} (${(e*100).toFixed(1)}%)`);
  }
}
console.log(fails?`FAILS ${fails}`:'ALL OK');
process.exit(fails?1:0);
