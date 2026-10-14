/* 홀별 원가 모델 — 엑셀 '행사장 비용비교' 수식과 같은 구조(공급가, 원).
   임대료·기본관리비 = 대관일수 비례
   전력 = (행사 kW × 8h × 박람회일수 + 설치 kW × (설치일 × 8h + 철거 2h)) × 업체 사용 배수(elx)   ← elx=1이면 엑셀과 동일
   냉난방 = ㎡ × (하루 가동시간 h의 ㎡ 단가) × 냉난방 일수(박람회일 + 설치일 선택)   ← h=8, 설치일 제외면 엑셀과 동일
   하루 h시간 ㎡ 단가는 홀별 요금 규정대로: 7+1(7시간 기본 + 추가 1시간 단가) · 7비례 · 8h비례 · 2h비례 · hour(㎡·시간)
   sea: 'jan' 난방(1월 요율) · 'aug' 냉방(8월 요율) · 'spr' 봄·가을(1·8월 할인 없는 정상가 + 시설이 밝힌 할증, 전기·냉난방은 1월·8월 중 낮은 쪽) */
const KW_BANDS=[[800,50,20],[1500,80,30],[2500,120,40],[Infinity,180,60]];
function bandKW(hh){for(const [lim,kw,skw] of KW_BANDS)if(hh<lim)return {kw,skw};}
function kwhOf(p){return p.kw*p.show*8+p.skw*(8*Math.max(0,p.rent-p.show)+2);}
function hvPerSqm(rule,K,M,h){
  if(K==null)return null;
  return rule==='7+1'?K+M*Math.max(0,h-7):rule==='7비례'?K*h/7:rule==='8h'?K*h/8:rule==='2h'?K*h/2:rule==='hour'?K*h:null;
}
function unitOf(x,sea){
  if(sea!=='spr')return x[sea];
  const j=x.jan,a=x.aug,mn=(p,q)=>p==null||q==null?null:Math.min(p,q);
  const hv=j.J==null||a.J==null?{J:null,K:null,M:0}:(j.J<=a.J?j:a);
  return {E:j.E,G:x.goff,H:j.H,I:mn(j.I,a.I),J:hv.J,K:hv.K,M:hv.M};
}
function hvDays(p){return p.show+(p.setupHv?Math.max(0,p.rent-p.show):0);}
function costOf(x,sea,p){
  const u=unitOf(x,sea),A=x.a,h=p.hrs??8;
  const rentDay=u.E==null||u.G==null?null:x.rt==='hall'?u.E*u.G:x.rt==='sqm'?A*u.E*u.G:u.E*u.G/4;
  const per=hvPerSqm(x.hr,u.K,u.M,h);
  return {
    rent:rentDay==null?null:rentDay*p.rent,
    mng:u.H==null?null:A*u.H*p.rent,
    el:u.I==null?null:u.I*kwhOf(p)*(p.elx??1),  /* elx: 참가업체 사용분 배수(기본 1 = 엑셀과 동일) */
    hv:per==null?null:A*per*hvDays(p),
    kwh:kwhOf(p),hvPer:per,hvDays:hvDays(p)
  };
}
if(typeof module!=='undefined')module.exports={bandKW,kwhOf,hvPerSqm,unitOf,hvDays,costOf};
