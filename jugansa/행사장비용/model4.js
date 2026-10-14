/* 홀별 원가 모델 (공급가, 원).
   임대료·기본관리비 = 대관일수 비례
   전력(elm) — 'area'(기본, BEXCO 정산서 실측 보정): 대관 면적 × 0.24kWh/㎡·일 × 대관일수 (설치일도 조명을 켬)
              'band'(엑셀 '행사장 비용비교' 원래 가정): (행사 kW × 8h × 박람회일수 + 설치 kW × (설치일 × 8h + 철거 2h))
              × kWh 단가 × 배수(elx, 기본 1)
   냉난방 = ㎡ × (하루 가동시간 h의 ㎡ 단가) × 냉난방 일수(박람회일 + 설치일 선택)
   하루 h시간 ㎡ 단가는 홀별 요금 규정대로: 7+1(7시간 기본 + 추가 1시간 단가) · 7비례 · 8h비례 · 2h비례 · hour(㎡·시간)
   폐기물 = 대관 면적 × 195원/㎡ (행사 1회, BEXCO 정산서 실측: 산업폐기물 약 4㎥/1,000㎡ × 45,000원 + 생활쓰레기)
   sea: 'jan' 난방(1월 요율) · 'aug' 냉방(8월 요율) · 'spr' 봄·가을(정상가 + 시설이 밝힌 할증, 전기·냉난방은 1월·8월 중 낮은 쪽)
        x.spr가 있으면 그 값(실측)으로 덮어씀 — 예: BEXCO 5월 정산서 월별 등차율 1.10 · 전기 169원/kWh
   단가가 없는 홀(I·K 없음)은 opt.fb가 참이면 전국 중앙값(FB)으로 추정하고 est 표시 */
const KW_BANDS=[[800,50,20],[1500,80,30],[2500,120,40],[Infinity,180,60]];
const EL_AREA=0.24;   /* kWh/㎡·대관일 — BEXCO 2025.12 4B 0.226 · 2026.05 4E+4F 0.257 평균 */
const WASTE=195;      /* 원/㎡·행사 — BEXCO 2025.12 212 · 2026.05 181 평균 */
const FB={jan:{I:182,Kh:23},aug:{I:209.5,Kh:30.9}};  /* 단가 확인된 홀 항목들의 중앙값(전기 원/kWh · 냉난방 원/㎡·시간, v7 데이터) */
function bandKW(hh){for(const [lim,kw,skw] of KW_BANDS)if(hh<lim)return {kw,skw};}
function kwhOf(p,A){
  if(p.elm==='area')return EL_AREA*A*p.rent;
  return p.kw*p.show*8+p.skw*(8*Math.max(0,p.rent-p.show)+2);
}
function hvPerSqm(rule,K,M,h){
  if(K==null)return null;
  return rule==='7+1'?K+M*Math.max(0,h-7):rule==='7비례'?K*h/7:rule==='8h'?K*h/8:rule==='2h'?K*h/2:rule==='hour'?K*h:null;
}
function unitOf(x,sea){
  if(sea!=='spr')return x[sea];
  const j=x.jan,a=x.aug,mn=(p,q)=>p==null||q==null?null:Math.min(p,q);
  const hv=j.J==null||a.J==null?{J:null,K:null,M:0}:(j.J<=a.J?j:a);
  return Object.assign({E:j.E,G:x.goff,H:j.H,I:mn(j.I,a.I),J:hv.J,K:hv.K,M:hv.M},x.spr||{});
}
function hvDays(p){return p.show+(p.setupHv?Math.max(0,p.rent-p.show):0);}
function fbOf(sea){return sea==='spr'?{I:Math.min(FB.jan.I,FB.aug.I),Kh:Math.min(FB.jan.Kh,FB.aug.Kh)}:FB[sea];}
function costOf(x,sea,p,opt={}){
  const u=unitOf(x,sea),A=x.a,h=p.hrs??8,kwh=kwhOf(p,A);
  const rentDay=u.E==null||u.G==null?null:x.rt==='hall'?u.E*u.G:x.rt==='sqm'?A*u.E*u.G:u.E*u.G/4;
  let I=u.I,per=hvPerSqm(x.hr,u.K,u.M,h),estEl=false,estHv=false;
  if(opt.fb){
    const f=fbOf(sea);
    if(I==null){I=f.I;estEl=true}
    if(per==null){per=f.Kh*h;estHv=true}
  }
  return {
    rent:rentDay==null?null:rentDay*p.rent,
    mng:u.H==null?null:A*u.H*p.rent,
    el:I==null?null:I*kwh*(p.elx??1),  /* elx: 배수(기본 1 = 정산서 실측·엑셀과 동일) */
    hv:per==null?null:A*per*hvDays(p),
    waste:A*WASTE,
    kwh,I,hvPer:per,hvDays:hvDays(p),estEl,estHv
  };
}
if(typeof module!=='undefined')module.exports={bandKW,kwhOf,hvPerSqm,unitOf,hvDays,costOf,EL_AREA,WASTE,FB};
