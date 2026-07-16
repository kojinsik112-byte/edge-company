# -*- coding: utf-8 -*-
def won(n): return f"{n:,}"
def pays(a):
    return won(round(a*0.2)), won(round(a*0.1)), won(round(a*0.7))
ALL="전타입<br>동일"

# (순번, 품목명, 비고, groups)  groups: [(제품명, [(Type, amt or '선택')])]
DATA = [
 (1,"친환경<br>바이오도료","그래핀 규조토 · 라돈 방출 저감 · 시멘트 독성 중화 · 유해물질 흡착분해 · 흡습·방습 · 불연성능 · <b>무상A/S 3년</b>",
   [("규조토 세스 바이오 (바닥 제외 실내벽체 / 발코니·타일·아트월 제외)",[("59",2400000),("76",2700000),("84",2900000)])]),
 (2,"현관중문","<b>단가</b> 스윙도어 1,500,000 / 원슬라이딩 1,300,000 · 5T 강화유리 · 시트 랩핑 · <b>무상AS 1년</b> · ※ 원슬라이딩 선택 : 59확장/84B",
   [("스윙도어(양방향)",[("59기본형",1500000)]),
    ("스윙도어(양방향) / 원슬라이딩",[("59확장형","선택")]),
    ("스윙도어(양방향)",[("76",1500000)]),
    ("스윙도어(양방향)",[("84A",1500000)]),
    ("스윙도어(양방향) / 원슬라이딩",[("84B","선택")])]),
 (3,"열차단<br>단열필름","<b>대피실(실외기실) 제외</b> · 무상A/S 12년",
   [("레이노 프리미엄 LX",[("59",2100000),("76",2300000),("84",2500000)])]),
 (4,"간접조명<br>&amp; 실링팬","<span class='hlapp'>★ 실링팬·조명·BT스위치·전동커튼 아크로 앱 통합제어</span> · 실링팬 = <b>아크로 블루투스 실링팬 최신형</b><br><span class='hlapp'>◎ 조명&amp;실링팬 + 전동커튼 세트(아크로 앱 연동) 5% 할인</span>",
   [("[선택1] SPOT조명(거실·복도) + 매립스위치(IOT) + 욕실장·신발장하부 센서",[(ALL,1300000)]),
    ("[선택2] 선택1 + 우물천장 간접조명 + 거실 커튼라인조명",[(ALL,2400000)]),
    ("[추가] 아크로 실링팬 + 우물천장 간접조명 또는 다운라이트 8개",[(ALL,1400000)])]),
 (5,"전동커튼","<span class='hlapp'>아크로 앱 연동 통합제어</span> · 무상A/S 2년 · IOT 허브 별도 · 거실=속지+겉지 2겹 / 안방 1겹 · <b>자사 잠정단가</b><br><span class='hlapp'>◎ 조명&amp;실링팬 + 전동커튼 세트 계약 시 5% 할인</span>",
   [("[패키지1] 거실 — 속지(쉬어) + 겉지(암막) 2겹",[(ALL,800000)]),
    ("[패키지2] 거실 2겹 + 안방 1겹 (안방 +300,000)",[(ALL,1100000)])]),
 (6,"휴젠뜨<br>(욕실환기)","자동 제습으로 샤워 후 습기 세균 방지 · 제조사 1년 보증 · ※ 2개소 설치 시 5만원 할인",
   [("휴젠뜨3 풀옵션 1개소 (공용욕실)",[(ALL,740000)]),
    ("휴젠뜨3 풀옵션 2개소 (공용+부부)",[(ALL,1430000)])]),
 (7,"안전<br>방범<br>방충망","1톤 하중 내구성 · 외부 침입/추락/빈집털이 방지 · 찢어지지 않는 방충망 · <b>무상A/S 망 10년·부품 2년</b> · 대피공간(실외기실) 제외",
   [("59 · 안전용 0.4mm",[("59",2330000)]),("59 · 방범용 0.7mm",[("59",2490000)]),
    ("76 · 안전용 0.4mm",[("76",2400000)]),("76 · 방범용 0.7mm",[("76",2570000)]),
    ("84 · 안전용 0.4mm",[("84",2450000)]),("84 · 방범용 0.7mm",[("84",2630000)])]),
 (8,"음식물<br>처리기","12만원 상당 리필용 미생물 3년분 + A/S용 1회분 무상증정 · <b>무상A/S 1년</b>",
   [("롯데 필링스 DCS-HM4A",[(ALL,1390000)])]),
 (9,"수돗물 정화<br>아토버스터","계량기·샤워·씽크 정수 필터 · 설치 시공 포함",
   [("계량기용 + 샤워기용 2ea",[(ALL,1270000)]),
    ("계량기용 + 씽크대용 + 샤워기용 2ea",[(ALL,1460000)])]),
 (10,"전동루버","실외기실 자동 환기 개폐 · 과열 방지",
   [("실외기실 자동개폐기 1대",[(ALL,600000)])]),
 (11,"홈케어<br>(줄눈·나노<br>·탄성)","<span class='hlapp'>◎ 3종 합계 2,980,000 → 2,850,000 할인 적용</span><br>줄눈 790,000 + 나노 1,200,000 + 탄성(3개소) 990,000<br><b>[줄눈]</b> 바닥3칸+샤워부스 안쪽3면+실리콘 오염방지 · <b>[나노]</b> 수전·걸이·코너선반 무상A/S 3년 · <b>[탄성]</b> 규조토 광촉매 3개소 통일",
   [("줄눈 + 나노코팅 + 탄성코트(3개소) &nbsp;<b>[홈케어 3종 세트]</b>",[(ALL,2850000)])]),
]

def item_rows(item):
    no,name,remark,groups = item
    total = sum(len(g[1]) for g in groups)
    html=[]; first_item=True
    for prod,rows in groups:
        first_g=True
        for (typ,amt) in rows:
            tds=[]
            if first_item:
                tds.append(f'<td class="no" rowspan="{total}">{no}</td>')
                tds.append(f'<td class="item" rowspan="{total}">{name}</td>')
            tds.append(f'<td class="type">{typ}</td>')
            if first_g:
                tds.append(f'<td class="prod" rowspan="{len(rows)}">{prod}</td>')
            if amt=="선택":
                tds.append('<td class="amt">선택</td><td class="pay">-</td><td class="pay2">-</td><td class="pay2">-</td>')
            else:
                g1,g2,g3=pays(amt)
                tds.append(f'<td class="amt">{won(amt)}</td><td class="pay">{g1}</td><td class="pay2">{g2}</td><td class="pay2">{g3}</td>')
            tds.append('<td class="stamp">(인)</td>')
            if first_item:
                tds.append(f'<td class="remark" rowspan="{total}">{remark}</td>')
            html.append("      <tr>"+"".join(tds)+"</tr>")
            first_item=False; first_g=False
    return "\n".join(html)

# 2페이지: 1~4 / 5~11
p1 = [i for i in DATA if i[0]<=4]
p2 = [i for i in DATA if i[0]>=5]
def build_tbody(items): return "\n".join(item_rows(it) for it in items)

THEAD = '''    <thead>
      <tr>
        <th class="no" rowspan="2">순번</th><th class="item" rowspan="2">품목</th><th class="type" rowspan="2">Type</th><th class="prod" rowspan="2">제품명 / 사양</th>
        <th class="amt" rowspan="2">총금액</th><th colspan="3">대금 지급 (계약금 20% · 중도금 10% · 잔금 70%)</th><th class="stamp" rowspan="2">계약자<br>날인</th><th class="remark" rowspan="2" style="text-align:center;">비고</th>
      </tr>
      <tr><th class="pay">계약금 20%<br><span style="font-weight:400">계약시</span></th><th class="pay2">중도금 10%</th><th class="pay2">잔금 70%<br><span style="font-weight:400">공사완료시</span></th></tr>
    </thead>'''

STYLE = '''<style>
@page { size: A4; margin: 0; }
* { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family:'Malgun Gothic','맑은 고딕',sans-serif; color:#1a1a1a; margin:0; background:#eceef1; }
.page { width:210mm; height:297mm; padding:10mm 9mm 12mm; position:relative; background:#fff; margin:0 auto 8px; overflow:hidden; display:flex; flex-direction:column; }
.brandbar { height:6px; background:linear-gradient(90deg,#15233d 0%,#15233d 55%,#c9a227 100%); border-radius:4px; }
.head { display:flex; justify-content:space-between; align-items:flex-end; margin-top:7px; }
.brand { font-size:12.5px; font-weight:800; letter-spacing:1px; color:#15233d; }
.brand small { display:block; font-size:8.5px; font-weight:600; letter-spacing:2px; color:#6b7a8d; margin-top:1px; }
h1 { text-align:center; font-size:20px; font-weight:800; letter-spacing:4px; color:#15233d; margin:6px 0 3px; }
.re { border:1.5px solid #c9c9cd; border-radius:8px; padding:6px 12px; font-size:11px; margin:4px 0 5px; }
.re b { color:#15233d; } .re .fld u { text-decoration:none; border-bottom:1px solid #9aa4b2; display:inline-block; min-width:60px; }
.pre { font-size:9.5px; line-height:1.5; color:#333; margin:0 2px 4px; } .pre b { color:#15233d; }
.art { font-size:10px; line-height:1.6; margin:5px 2px; } .art b { color:#15233d; }
.sec2 { font-size:12.5px; font-weight:800; color:#15233d; margin:5px 2px 3px; }
.unit { font-size:10px; color:#8a6d12; font-weight:700; }
table { width:100%; border-collapse:collapse; font-size:10.5px; table-layout:fixed; flex:0 0 auto; }
.foot { flex:0 0 auto; }
.page { justify-content:flex-start; }
th, td { border:1px solid #b3b8c2; padding:8px 4px; text-align:center; word-break:keep-all; vertical-align:middle; line-height:1.3; }
thead th { background:#15233d; color:#fff; font-weight:700; font-size:10.5px; padding:6px 4px; }
.no { width:22px; font-weight:800; color:#15233d; background:#eef0f4; font-size:11px; }
.item { width:56px; font-weight:800; color:#15233d; background:#fff7df; font-size:11px; }
.type { width:56px; font-weight:700; font-size:10px; }
.prod { width:170px; text-align:left; padding-left:8px; }
.amt { width:72px; text-align:right; padding-right:8px; font-variant-numeric:tabular-nums; font-weight:800; font-size:13px; color:#15233d; }
.pay { width:62px; text-align:right; padding-right:7px; font-variant-numeric:tabular-nums; font-size:10.5px; font-weight:700; color:#15233d; }
.pay2 { width:60px; text-align:right; padding-right:7px; font-variant-numeric:tabular-nums; font-size:10px; color:#555; }
.stamp { width:38px; font-size:10px; color:#aeb4bf; }
.remark { width:150px; text-align:left; padding-left:7px; font-size:9.2px; line-height:1.4; color:#c0392b; }
.remark b { color:#15233d; }
.hlapp { background:#fff3cf; color:#15233d; font-weight:700; }
thead th.no, thead th.item, thead th.type, thead th.prod, thead th.amt, thead th.pay, thead th.pay2, thead th.stamp, thead th.remark { color:#fff; background:#15233d; }
.foot { margin-top:6px; font-size:9px; color:#666; line-height:1.5; } .foot b { color:#15233d; }
.botbar { position:absolute; left:9mm; right:9mm; bottom:6mm; border-top:1px solid #e0e0e3; padding-top:4px; display:flex; justify-content:space-between; font-size:8px; color:#90a0b2; }
/* ── 약관 페이지 ── */
.ypage { padding:10mm 12mm 12mm; }
.ytitle { text-align:center; font-size:18px; font-weight:800; letter-spacing:8px; color:#15233d; margin:10px 0 8px; }
.ybox { columns:2; column-gap:9mm; column-rule:1px solid #e2e4e9; }
.yart { break-inside:avoid; margin:0 0 6px; }
.yart h3 { font-size:10px; font-weight:800; color:#15233d; margin:0 0 2px; }
.yart ol { margin:0; padding-left:15px; }
.yart li { font-size:8.4px; line-height:1.4; color:#333; margin:1.5px 0; text-align:justify; }
.signnote { font-size:10px; font-weight:800; color:#15233d; margin:10px 0 5px; }
.signtbl { width:100%; border-collapse:collapse; table-layout:fixed; flex:0 0 auto; }
.signtbl td { border:1px solid #b3b8c2; padding:7px 9px; font-size:10px; vertical-align:middle; }
.slbl { width:52px; text-align:center; font-weight:800; color:#15233d; background:#eef0f4; }
.sgap { width:33%; line-height:1.7; }
.sgap u, .sfld u { text-decoration:none; border-bottom:1px solid #9aa4b2; display:inline-block; min-width:60px; }
.ins { color:#aeb4bf; font-size:9px; }
.sfld { padding:5px 9px; }
.frow { display:flex; align-items:center; padding:2px 0; }
.frow + .frow { border-top:1px dashed #d7dae0; }
.fk { width:110px; color:#6b7a8d; font-size:9px; }
.fv { flex:1; }
.fv u { min-width:120px; }
.cday { text-align:center; font-size:11px; letter-spacing:1px; }
.cday u { min-width:56px; }
.signwarn { margin-top:8px; font-size:9px; color:#c0392b; font-weight:700; text-align:center; }
</style>'''

HEADER_BLOCK = '''  <div class="re"><span class="fld"><b>■ 부동산의 표시</b> : 힐스테이트 물금센트럴 &nbsp; <u>&nbsp;</u> 동 &nbsp; <u>&nbsp;</u> 호 &nbsp;&nbsp; [ 타입 <u>&nbsp;</u> ]</span></div>
  <div class="pre">상기 부동산에 대하여 각 옵션 품목의 <b>공급 대표 업체</b>(별첨 「입금계좌 안내」)를 "갑", 매수인을 "을"이라 하고 <b>제2조 옵션품목</b>의 공급계약(이하 "본 계약")을 체결하며, 계약서 2부를 각 1부씩 보관한다. ㈜엣지컴퍼니는 옵션주관사로서 각 업체의 이행·품질·A/S를 보증한다. <b>제1조(목적)</b> "갑"은 목적물을 상기 부동산에 시공·설치하고, "을"은 제2조 지급조건에 따라 "갑" 지정 <b>아래(별첨) 계좌</b>에 직접 납부한다.</div>
  <div class="sec2">제2조 (옵션품목 및 공급대금) <span class="unit" style="float:right;">단위 : 원 / VAT 포함</span></div>'''

# ── 3페이지 : 약관 + 서명·날인 ──────────────────────────────
YAKGWAN = [
 ("제3조 (하자보수)", [
   '"갑"은 본 목적물 공사의 시공상 하자에 대하여 「주택법 시행령」의 규정에 의하여 하자보수 책임을 진다.',
   '하자보수책임 기간 중 본 목적물에 대한 "을" 또는 사용자(전용부분)를 임대하는 경우, 임차인을 포함한 고의·관리부실 및 부주의로 인한 훼손 부분은 "을"이 유지·보수한다.',
   '"갑"의 하자담보책임의 범위는 목적물의 계약 내역에 준한다.',
 ]),
 ("제4조 (해약 등)", [
   '본 목적물의 공급계약 체결 후에는 상기 부동산의 구조물에 대하여 변형 및 원자재 구입 등 공사비용이 선 투입되는 관계로, 어떠한 경우에도 본 계약을 임의로 해약할 수 없다.',
   '공급계약 체결 후 "을"의 대금 납입 여부와 관계없이 "갑"은 계약사항을 공급·시공하여야 하며, "을"은 이러한 사항을 명확히 인지하고 추후 계약의 해지(포기) 및 대금 납부를 기피하거나 이의를 제기할 수 없다.',
   '"을"의 귀책사유로 인한 계약 해약 시 위약금이 발생한다. (계약 30일 이내 : 총금액의 10% / 31~60일 이내 : 총금액의 30% / 60일 초과 : 총금액의 50%) 단, 제품(자재) 발주 및 공사 진행 시에는 계약 해지가 불가하다.',
 ]),
 ("제5조 (연체 및 지체상금)", [
   '"갑"은 "을"의 공급대금(중도금·잔금)을 납부기일 이전에 납부하더라도 선납할인을 적용하지 아니한다.',
   '"을"이 공급대금을 납부일정보다 지연할 경우, 그 지연일수에 해당하는 연체료를 가산하여 납부하여야 하며, 납부액이 부족할 경우 연체료·공사비 순으로 처리된다.',
   '"갑"이 목적물 인도일까지 공사·설치를 완료하지 못할 경우, 기납부 대금에 대하여 제2항의 연체율에 의거 "을"에게 지체상금을 지불하거나 잔금에서 공제한다.',
   '"갑"의 귀책사유가 아닌 불가항력(천재지변, 관공서 검사·신고·허가 등 행정절차의 지연)으로 공사가 지연될 경우, "갑"은 이를 "을"에게 통보하며 제3항의 지체상금을 지급하지 아니한다.',
 ]),
 ("제6조 (권리의무 승계 등)", [
   '"을"은 본 공급계약에 따른 권리·의무를 "갑"의 승인 없이 타인에게 양도하는 등의 행위를 할 수 없다.',
   '본 공급계약은 아파트 공급계약을 전제로 이루어진 계약임을 인지하고, "을"은 아파트 공급계약의 권리·의무 승계 시 본 공급계약의 권리·의무를 양수인에게 승계하도록 하며, 이를 이행하지 않을 경우 "갑"은 승계를 거부할 수 있다.',
 ]),
 ("제7조 (특기사항)", [
   '"을"은 다음 사항을 충분히 숙지하고 계약을 체결하는 것이며, 추후 이에 대하여 "갑"에게 이의를 제기하지 아니한다.',
   '본 옵션 품목은 「공동주택 분양가격의 산정 등에 관한 규칙·시행규칙」에 의한 분양가격에 포함되지 아니하는 품목이다.',
   '카탈로그·견본품 및 각 시공 명칭은 카탈로그 기준이며, 실제 계약·시공 시 위치가 변경될 수 있다.',
   '옵션물의 제조사·모델은 제품의 품질 개선·품귀 등의 사유로 동급 이상의 협의 사양으로 변경될 수 있다.',
   '옵션물의 설치 위치는 지정되어 있으며, 계약자가 임의로 위치를 지정할 수 없다.',
   '옵션 품목은 공동주택 컨셉에 맞추어 디자인·품질관리하는 품목으로, 타사·시중 품목과 충분히 비교 검토한 후 계약하기 바란다.',
   '계약이 해제된 때에는 총 유상옵션 금액의 10%가 위약금으로 귀속되며, 착수일(공사업체·자재 선정 등의 업무 포함) 후에는 위약금을 초과하여 발생된 손실에 대하여 손해배상을 청구할 수 있다.',
 ]),
 ("제8조 (기타)", [
   '본 공급계약상 부기하지 아니한 규정 등은 아파트 공급계약서의 규정을 연동하여 적용한다.',
   '본 공급계약에 명시되지 아니한 사항은 "갑"과 "을"이 합의하여 결정하되, 합의되지 아니한 사항은 관계 법령 및 일반 상관례에 따른다.',
   '본 공급계약에 관한 소송은 표시 부동산의 소재지를 관할하는 법원으로 한다.',
 ]),
]

def yakgwan_page():
    arts=[]
    for title,items in YAKGWAN:
        lis="".join(f"<li>{t}</li>" for t in items)
        arts.append(f'<div class="yart"><h3>{title}</h3><ol>{lis}</ol></div>')
    body="\n".join(arts)
    sign='''  <div class="signnote">■ 본 목적물의 공급계약은 당사자가 충분히 그 내용을 숙지한 후 서명·날인한 것임을 확인합니다.</div>
  <table class="signtbl">
    <tr>
      <td class="slbl">공급자<br>"갑"</td>
      <td class="sgap">주식회사 엣지컴퍼니 (옵션주관사)<br>사업자등록번호 <u>&nbsp;</u><br>대표번호 <u>&nbsp;</u><br>대표이사 &nbsp;이 유 호 &nbsp;<span class="ins">(인)</span></td>
      <td class="slbl">매수인<br>"을"</td>
      <td class="sfld">
        <div class="frow"><span class="fk">성 명</span><span class="fv"><u>&nbsp;</u> <span class="ins">(인)</span></span></div>
        <div class="frow"><span class="fk">주민번호</span><span class="fv"><u>&nbsp;</u> &ndash; <u>&nbsp;</u></span></div>
        <div class="frow"><span class="fk">주 소</span><span class="fv"><u>&nbsp;</u></span></div>
        <div class="frow"><span class="fk">연락처1 (휴대폰)</span><span class="fv"><u>&nbsp;</u></span></div>
        <div class="frow"><span class="fk">연락처2 (현금영수증)</span><span class="fv"><u>&nbsp;</u></span></div>
      </td>
    </tr>
    <tr><td class="slbl">계 약 일</td><td class="cday" colspan="3"><u>&nbsp;</u> 년 &nbsp; <u>&nbsp;</u> 월 &nbsp; <u>&nbsp;</u> 일</td></tr>
  </table>
  <div class="signwarn">※ "갑" 및 "을"의 인장 날인 및 서명이 없는 계약은 무효로 한다. (단, 전화계약 시 계약금 입금 시 계약 성립)</div>'''
    return f'''<div class="page ypage">
  <div class="brandbar"></div>
  <div class="head"><div class="brand">EDGE COMPANY<small>㈜엣지컴퍼니 · 입주옵션 주관</small></div><div class="unit">힐스테이트 물금센트럴 추가 옵션 계약서</div></div>
  <div class="ytitle">【 약 관 】</div>
  <div class="ybox">
{body}
  </div>
{sign}
  <div class="botbar"><span>㈜엣지컴퍼니 · 입주품목 옵션 및 박람회 전문기획</span><span>힐스테이트 물금센트럴 추가 옵션 계약서 (3/3)</span></div>
</div>'''

def page(inner, pageno):
    hd='''  <div class="brandbar"></div>
  <div class="head"><div class="brand">EDGE COMPANY<small>㈜엣지컴퍼니 · 입주옵션 주관</small></div><div class="unit">힐스테이트 물금센트럴 추가 옵션 계약서</div></div>'''
    title='<h1>힐스테이트 물금센트럴 추가 옵션 계약서</h1>' if pageno==1 else '<div style="text-align:center;font-size:11px;color:#6b7a8d;margin:6px 0 4px;letter-spacing:1px;">힐스테이트 물금센트럴 추가 옵션 계약서 · 제2조 (계속)</div>'
    hb=HEADER_BLOCK if pageno==1 else ''
    if pageno==2:
        foot='  <div class="foot">※ <b>대금 지급</b> : 계약금 20%(계약시) · 중도금 10% · 잔금 70%(공사완료시) &nbsp;|&nbsp; <b>각 대표 업체 계좌로 직접 납부</b>(별첨 입금계좌 안내) &nbsp;|&nbsp; <span class="hlapp">◎ 조명&amp;실링팬+전동커튼 세트(앱 연동) 5% 할인</span> &nbsp;|&nbsp; "선택" 품목은 옵션 선택 시 금액 확정</div>'
    else:
        foot='<div class="foot">※ 계약금 20%(계약시) · 중도금 10% · 잔금 70%(공사완료시) · 각 대표 업체 계좌 직접 납부 · 엣지컴퍼니 이행·품질·A/S 보증</div>'
    return f'''<div class="page">
{hd}
{title}
{hb}
  <table>
{THEAD}
    <tbody>
{inner}
    </tbody>
  </table>
{foot}
  <div class="botbar"><span>㈜엣지컴퍼니 · 입주품목 옵션 및 박람회 전문기획</span><span>힐스테이트 물금센트럴 추가 옵션 계약서 ({pageno}/3)</span></div>
</div>'''

html=f'''<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8"><title>힐스테이트 물금센트럴 추가 옵션 계약서</title>
{STYLE}</head>
<body>
{page(build_tbody(p1),1)}
{page(build_tbody(p2),2)}
{yakgwan_page()}
</body></html>'''
open("/home/user/edge-company/business-ops/movein/양산현장_서류/양산현장_추가옵션_계약서.html","w",encoding="utf-8").write(html)
print("written")
