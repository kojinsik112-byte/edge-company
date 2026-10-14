# 사용: python verify_excel.py <이 폴더> <엑셀.xlsx>
# 엑셀 수식을 pycel로 일수별 재계산 → model.js와 행·항목 단위 대조
import json,sys,subprocess
from pycel import ExcelCompiler
SP=sys.argv[1]; X=sys.argv[2]  # 회장 제공 '행사장 비용비교' 엑셀 경로(깃 제외)
xl=ExcelCompiler(filename=X)
S="'행사장 비용비교'"
rows=[]
for r in range(13,70):
    v=xl.evaluate(f"{S}!A{r}"); h=xl.evaluate(f"{S}!B{r}"); s=xl.evaluate(f"{S}!D{r}")
    if not v or s not in ('1월','8월'): continue
    if v=='DCC 제2전시장': h=h.replace('제2전시장 ','')
    rows.append((r,v,h,'jan' if s=='1월' else 'aug'))
B="'규모별 예산'"
num=lambda q: q if isinstance(q,(int,float)) and not isinstance(q,bool) else None
for c in ('B5','D5','H5'): xl.evaluate(f"{S}!{c}")
for r,_,_,_ in rows:
    for c in 'EFGH': xl.evaluate(f"{S}!{c}{r}")
for r in range(5,40):
    for c in 'BDFHIJ': xl.evaluate(f"{B}!{c}{r}")
checked=fails=0
for rent,show in [(4,3),(5,3),(3,2),(6,4),(2,2),(7,5),(3,3)]:
    xl.set_value(f"{S}!B5",rent); xl.set_value(f"{S}!D5",show); xl.set_value(f"{S}!H5",8*max(0,rent-show))
    exp=[[num(xl.evaluate(f"{S}!{c}{r}")) for c in 'EFGH'] for r,_,_,_ in rows]
    q=json.dumps([[v,h,s] for _,v,h,s in rows],ensure_ascii=False)
    out=subprocess.run(['node','-e',f'const M=require("{SP}/model4.js"),U=require("{SP}/units.json");const p={{rent:{rent},show:{show},kw:80,skw:30}};console.log(JSON.stringify({q}.map(([v,h,s])=>{{const c=M.costOf(U.find(u=>u.v===v&&u.h===h),s,p);return [c.rent,c.mng,c.el,c.hv]}})))'],capture_output=True,text=True,check=True).stdout
    mine=json.loads(out)
    for (r,v,h,s),e,m in zip(rows,exp,mine):
        for k in range(4):
            if v.startswith('춘천') and k==0 and rent!=4: continue
            checked+=1
            a,b=e[k],m[k]
            if (a is None)!=(b is None) or (a is not None and abs(a-b)>0.01):
                fails+=1; print('MISMATCH',rent,show,v,h,s,'EFGH'[k],a,b)
    print(f'대관 {rent}일·박람회 {show}일: {len(rows)}행 OK' if not fails else '')
print('checked',checked,'fails',fails)
# 규모별 예산 시트(복수 홀·세대 구간별 kW) 대조: 대관+관리, 전기, 냉난방
B="'규모별 예산'"; xl.set_value(f"{S}!B5",4); xl.set_value(f"{S}!D5",3); xl.set_value(f"{S}!H5",8)
bad=0;n=0
for r in range(5,40):
    hall=xl.evaluate(f"{B}!D{r}"); sea=xl.evaluate(f"{B}!F{r}"); hh=xl.evaluate(f"{B}!B{r}")
    if not isinstance(hall,str) or '/' not in hall or sea not in ('1월','8월'): continue
    v,h=[t.strip() for t in hall.split(' / ',1)]
    vals=[num(xl.evaluate(f"{B}!{c}{r}")) for c in 'HIJ']
    out=subprocess.run(['node','-e',f'const M=require("{SP}/model4.js"),U=require("{SP}/units.json");const x=U.find(u=>u.v==={json.dumps(v)}&&u.h==={json.dumps(h)});if(!x){{console.log("null");process.exit()}};const b=M.bandKW({hh});const c=M.costOf(x,"{"jan" if sea=="1월" else "aug"}",{{rent:4,show:3,kw:b.kw,skw:b.skw}});console.log(JSON.stringify([c.rent+c.mng,c.el,c.hv]))'],capture_output=True,text=True,check=True).stdout.strip()
    m=json.loads(out); n+=1
    if m is None or any(abs(a-b)>0.01 for a,b in zip(vals,m)): bad+=1; print('SCALE MISMATCH',hh,v,h,sea,vals,m)
print('scale rows',n,'bad',bad)
