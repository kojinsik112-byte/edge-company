# -*- coding: utf-8 -*-
"""롯데캐슬 나리벡시티 — 요약제안서 12쪽(제출서류 14 '기타 제안 내용 확인 자료' · 정회원 투표 · PT 기본 자료 · 카페 게시 대상).

build_nr.py build() 가 제안서(02)를 만든 뒤 emit_summary(globals()) 로 부른다(--no-summary 면 생략).
순서(착수 strategy 4-4): ① 표지 ② 한 장 요약(같은 기준 · 먼저 공개 · 한 창구) ③ 약속 10가지 ④ 먼저 묻는 다섯 가지 ⑤ 세대 혜택 · 선택 항목
⑥ 가격 검증 · 10배 보상 ⑦ A/S · 하자 창구 ⑧ 사전점검 · 전문 지원 범위 ⑨ 입예협 활동 · 커뮤니티 · 경관 ⑩ 실적 · 사람 ⑪ 담당 체계 · 일정
⑫ 책임자 · 대표 확약 + 대표번호 · 이메일(휴대번호 없음).
원칙: 숫자 · 문구는 제안서와 같은 값(D · ST · PROM10 · VOICE · CHECK5 · MENU_ROWS · EXPERT6 · REQ6 · MON)만 쓴다. 쪽 번호는 방금 만든 제안서 PGNO로.
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "분당퍼스트빌리지"))
from summary_bd import CSS as _CSS_BD  # noqa: E402  (분당 요약제안서와 같은 카드 · 표 스타일)

CSS = re.sub(r"/\*.*?\*/", "", _CSS_BD)

NAME_SUM = "엣지컴퍼니_롯데캐슬나리벡시티_요약제안서"
PT_LINE = ("계약 후 실제 업무를 맡을 책임자(주관사업 총괄 본부장)와 결정권자(대표이사)가 함께 나옵니다. "
           "발표는 둘 중 한 명이 맡고 질의에는 둘이 함께 답하며, 제안 조건은 대표이사가 그 자리에서 확약합니다.")  # 본부장 10-23 — 제안서 문장 그대로

CSS_NR = r"""
.sx .ms3{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;min-height:0}
.sx .ms3>div{border:1px solid rgba(200,168,106,.55);border-top:3px solid var(--gold2);border-radius:14px;padding:16px 20px;display:flex;flex-direction:column;gap:8px;background:linear-gradient(180deg,rgba(235,203,143,.10),rgba(255,255,255,.01) 50%)}
.sx .ms3 em{font-style:normal;font-size:12px;letter-spacing:.2em;color:var(--gold2);font-weight:700}
.sx .ms3 h4{font-size:24px;font-weight:800}
.sx .ms3 .bn{font-size:44px;font-weight:800;color:var(--gold);line-height:1}.sx .ms3 .bn small{font-size:16px;margin-left:3px}
.sx .ms3 p{font-size:14px;color:var(--sub);line-height:1.5}
.sx .ptq{border-left:3px solid var(--gold2);padding:8px 16px;font-size:14px;line-height:1.55;color:var(--ink)}
.sx .ptq b{color:var(--gold);margin-right:6px}
.sx table.mt td{font-size:13px;padding:6px 10px;line-height:1.38;vertical-align:middle}
.sx table.mt td.n{width:40px;white-space:nowrap}.sx table.mt td.pg{white-space:nowrap;color:var(--gold);font-weight:800}
.sx .m3{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.sx .m3>div{border:1px solid var(--line);border-radius:10px;padding:10px 14px}
.sx .m3 b{display:block;font-size:15px;color:var(--gold)}
.sx .m3 span{display:block;font-size:12.5px;color:var(--sub);line-height:1.42;margin-top:3px}
.sx .rq6{display:grid;grid-template-columns:1fr 1fr;grid-auto-rows:1fr;gap:10px;flex:1;min-height:0}
.sx .rq6>div{border:1px solid var(--line);border-radius:10px;padding:12px 15px;display:flex;flex-direction:column;justify-content:center;gap:5px}
.sx .rq6 b{font-size:16.5px;color:var(--gold)}.sx .rq6 span{font-size:13.5px;color:var(--sub);line-height:1.45}
.sx .bx.fl .phx{flex:1;position:relative;min-height:240px}
.sx .bx.fl .mx{padding:7px 12px;gap:4px}.sx .bx.fl .mx p{font-size:11.8px}.sx .bx.fl .mbar{height:24px}
.sx table.mt.mn td{font-size:12px;padding:4px 8px;line-height:1.3}
"""


def emit_summary(G):
    B, D, ST, t = G["B"], G["D"], G["ST"], G["t"]
    PGNO = dict(G["PGNO"])
    sec = "요약제안서"
    hh, ft = D.FUND_HH, G["FT"]

    def pg(*keys):
        return "p." + " · ".join(f"{n:02d}" for n in sorted({PGNO[k] for k in keys}))

    def std(label, title, lead, body, kp):
        return ("std", dict(sec=f"{sec} · {label}", title=title, lead=lead, body=body, kp=kp))

    def mtable(head, rows):
        th = "".join(f"<th>{h}</th>" for h in head)
        return f'<table class="mt{" mn" if len(head) == 3 else ""}"><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table>'

    # ---------------------------------------------------------------- 2 · 한 장 요약
    _t84 = sum(n for a, n in ST["types"] if a.startswith("84"))
    p2 = f"""<div class="sx" style="grid-template-rows:auto 1fr auto">
<div class="fact">
<div><b>{hh:,}<small>세대</small></b><span>{ST['buildings']}개 동 · {ST['floors']}</span></div>
<div><b>84<small>㎡</small> {_t84 * 100 // hh}<small>%</small></b><span>84㎡ {_t84}세대 · 102 ~ 155㎡ {hh - _t84}세대</span></div>
<div><b>2027.11</b><span>입주 예정 · 박람회 {ST['expo']} 예정</span></div>
<div><b>{ST['builder']}</b><span>시공 · 시행 {ST['developer']}</span></div>
</div>
<div class="ms3">
<div><em>SAME STANDARD</em><h4>같은 기준</h4><div class="bn">15<small>만원 상당</small></div>
<p>{hh}세대 모두, 계약 시기와 상관없이 세대당 15만원 상당(총 {ft} 상당)을 주관사가 직접 사서 드립니다. 참여업체 사은품 · 경품은 이와 별도입니다.</p></div>
<div><em>OPEN FIRST</em><h4>먼저 공개</h4><div class="bn">×10</div>
<p>가격 비교자료를 박람회 14일 전에 카페에 먼저 올립니다. 더 싼 곳이 영수증으로 확인되면 차액의 10배(1건당 최대 50만원)를 보상하고, 계약금은 5%까지만 받습니다(맞춤 제작 품목 예외).</p></div>
<div><em>ONE DESK</em><h4>한 창구</h4><div class="bn">48<small>시간</small></div>
<p>하자 · A/S는 한 곳에서 받아 24시간 안에 1차 회신, 48시간 안에 방문 일정을 확정하고, 입주 후 12개월 동안 하자 처리 현황을 공개합니다.</p></div>
</div>
<div class="ptq"><b>PT</b>{PT_LINE}</div>
</div>"""

    # ---------------------------------------------------------------- 3 · 약속 10가지
    p3 = '<div class="sx">' + mtable(["NO", "약속", "조건 · 기준", "제안서"], "".join(
        f'<tr><td class="n">{i:02d}</td><td class="k">{t(a)}</td><td>{t(b)}</td><td class="pg">{pg(*ks)}</td></tr>'
        for i, (a, b, ks) in enumerate(G["PROM10"], 1))) + "</div>"

    # ---------------------------------------------------------------- 4 · 먼저 묻는 다섯 가지
    p4 = '<div class="sx">' + mtable(["NO", "먼저 묻는 것", "엣지컴퍼니 답", "제안서"], "".join(
        f'<tr><td class="n">{n}</td><td class="k">{t(q)}</td><td>{t(a)}</td><td class="pg">{pg(*ks)}</td></tr>'
        for n, q, a, ks in G["VOICE"])) + "</div>"

    # ---------------------------------------------------------------- 5 · 세대 혜택 · 선택 항목
    mix = G["_mix"]
    p5 = f"""<div class="sx" style="grid-template-columns:1.55fr 1fr">
<div class="bx hl"><h3><i>BENEFIT</i>선택 항목 가격표 · {ft} 상당 안에서<small>제안서 {pg('fund', 'menu')}</small></h3>
{G['_menu_tbl']()}
<div class="nt" style="margin-top:8px">A · B · C는 세트가 아니라 선택 목록입니다 · ‘협의 단가’ 항목은 협약 때 단가 · 수량을 정합니다 · 사용 내역 공개 · 주관사 부담이라 공구가에 얹지 않습니다</div></div>
<div class="col"><div class="bx fl"><h3><i>MIX</i>담는 예시 3가지</h3>
{mix("①", "상품권형", G["_g10"], "상품권 세대당 10만원 · 남은 금액으로 방문 선물 · B 항목")}
{mix("②", "균형형", G["_g5"], "상품권 세대당 5만원 · 남은 금액으로 실측 · VR · 3D · 방문 선물 · B 항목")}
{mix("③", "서비스형", 0, "상품권 없이 B 항목 · 실측 · VR · 3D · 방문 선물로 구성")}
</div></div></div>"""

    # ---------------------------------------------------------------- 6 · 가격 검증 · 10배
    flw = "".join((('<span class="ar">›</span>' if i else "") + f'<div class="st{" hl" if i == 4 else ""}"><i>{a}</i><b>{b}</b><span>{t(c)}</span></div>')
                  for i, (a, b, c) in enumerate(G["CHECK5"]))
    p6 = f"""<div class="sx" style="grid-template-rows:auto 1fr">
<div class="flw">{flw}</div>
<div class="sx" style="grid-template-columns:1fr 1fr;min-height:0">
<div class="bx"><h3><i>GUARD</i>공동구매 단가를 지키는 장치<small>제안서 {pg('check', 'guard4')}</small></h3>
<div class="g4">
<div><b>D-30</b><strong>단가표 검수</strong><span>모델명 · 출시연도 · 설치 · 배송 · A/S 포함 여부를 입예협과 확인 · 현장 가격 변경 없음</span></div>
<div><b>D-14</b><strong>비교자료 공개</strong><span>같은 모델 · 같은 조건 총액으로 시중 매장 · 온라인과 비교해 카페에 먼저 공개(승인 후)</span></div>
<div><b>{D.DEPOSIT_MAX}<small>%</small></b><strong>계약금 상한</strong><span>맞춤 제작 품목 예외 · 잔금은 시공 · 설치 확인 후</span></div>
<div><b>동일</b><strong>현금 · 카드 같은 단가</strong><span>결제 방식에 따른 단가 차이 없음 · 업체 참가비는 정액 · 공구가 연동 없음</span></div>
</div></div>
<div class="bx"><h3><i>× 10</i>최저가 차액 10배 보상 (예시)<small>제안서 {pg('x10', 'rule1')}</small></h3>
<div class="x10">
<div><div class="lb2">박람회 공동구매가 (예시)</div><div class="br" style="width:100%">35만원</div></div>
<div><div class="lb2">인근({ST['local']}) 매장 동일 제품</div><div class="br g" style="width:91.4%">32만원</div></div>
<div class="rw2"><b>30<small>만원</small></b><span>차액 3만원 × 10배 보상<br>+ 판매가 32만원으로 조정</span></div>
<div class="nt">구매 영수증 + 주관사 매장 확인 · 계약 후 7일 이내 · 1건당 최대 50만원(계약금액이 더 적으면 그 금액) · 세대 · 품목당 1회 · <b style="color:var(--ink)">보상금은 주관사 부담</b>. 온라인 · 홈쇼핑, 시공 품목, 카드할인 · 사은품, 전시 · 리퍼, 한정 수량 행사가는 제외(규정 제8조).</div>
</div></div>
</div></div>"""

    # ---------------------------------------------------------------- 7 · A/S · 하자 창구
    as5 = "".join((('<span class="ar">›</span>' if i else "") + f'<div class="st{" k" if k else ""}"><b>{a}</b><strong>{b}</strong><span>{c}</span></div>')
                  for i, (a, b, c, k) in enumerate([
                      ("1<small>창구</small>", "주관 콜센터 접수", f"{D.TEL} 평일 · 카페 신문고 · 카카오채널 365일", False),
                      ("24<small>시간</small>", "안에 1차 회신", "주말 · 공휴일은 다음 영업일 12시 · 업체 무응답이면 주관사 개입", False),
                      ("48<small>시간</small>", "안에 방문 일정 확정", "방문은 입주민과 정한 날 · 누수 · 전기 등 긴급 하자 우선 배정", False),
                      ("선보상", "업체가 미루면", "입주민께 먼저 보상하고 업체와는 나중에 정산", True),
                      ("해피콜", "완료 확인 후 종결", "접수 · 처리 · 지연 사유 기록 · 정기 보고", False),
                  ]))
    p7 = f"""<div class="sx" style="grid-template-rows:auto 1fr auto">
<div class="as5">{as5}</div>
<div class="sn3">
<div class="bx hl"><b class="n">12<small>개월</small></b><strong>하자 창구 하나</strong>
<ul class="xl"><li>입주 지정기간 시작일부터 12개월</li><li>접수 · 취합 · 시공사 전달 · 처리 진행 관리</li><li>현황 보고 지정기간 주 1회 → 이후 월 1회</li></ul></div>
<div class="bx"><b class="n">24<small>개월</small></b><strong>계약이행 · 하자보증보험</strong>
<ul class="xl"><li>피보험자 = 입예협 · 협약 후 발급</li><li>금액 · 기산일 · 보증 대상은 협약 때 확정</li><li>하자 예치금 최대 1억 · 엣지컴퍼니 자산 · 선보상 재원</li></ul></div>
<div class="bx"><b class="n">2<small>년</small></b><strong>무상 A/S · 업체 이관</strong>
<ul class="xl"><li>시공 품목 최소 2년 · 브랜드는 제조사 보증</li><li>업체 도산 · 연락 두절 시 대체 업체 이관(계약자 동의)</li><li>무상 A/S 기간 안 이관 비용은 주관사 부담</li></ul></div>
</div>
<div class="rs2">
<div><b>업체 부담은 늘리지 않습니다</b><span>콜센터 운영비 · 하자 예치금 · 10배 보상금은 주관사 부담 - 업체 예치금 · 추가 보증금 없음(공고 우대 17)</span></div>
<div><b>두 기간은 따로입니다</b><span>시공사({ST['builder']}) 하자 창구 = 12개월 · 공동구매 품목 A/S = 품목별 무상 기간(시공 품목 최소 2년) · 제안서 {pg('desk', 'as')}</span></div>
</div></div>"""

    # ---------------------------------------------------------------- 8 · 사전점검 · 전문 지원 범위
    ex = mtable(["구분", "누가", "무엇을 · 몇 번", "비용"], "".join(
        f'<tr><td class="k">{t(a)}</td><td>{t(b)}</td><td>{t(c)}</td><td>{t(d)}</td></tr>' for a, b, c, d in G["EXPERT6"]))
    p8 = f"""<div class="sx" style="grid-template-rows:auto 1fr">
<div class="m3">
<div><b>사전점검 2일 · 하루 6명</b><span>현장 안내 · 체크리스트 배포 · 점검 장비 대여 창구 · 모집공고 옵션표 대조 점검표</span></div>
<div><b>세대 전문 점검</b><span>원하시는 세대는 ‘사전점검 대행 할인’(최대 50%)으로 - 할인형이라 15만원에서 차감하지 않습니다</span></div>
<div><b>법정 감리 아님</b><span>자문 의견은 법정 감리 · 하자 판정 · 법률 의견이 아닙니다 · 법률은 지정 법무법인</span></div>
</div>
<div class="bx">{ex}</div></div>"""

    # ---------------------------------------------------------------- 9 · 입예협 활동 · 커뮤니티 · 경관
    rq = "".join(f'<div><b>{x["nm"]}</b><span>{t(x["ds"])}</span></div>' for x in G["REQ6"])
    im, _own = G["slot"]("lx_front2")
    ph = (f'<div class="phx"><img src="assets_ins/{im}.jpg" alt="" style="object-position:50% 50%"><div class="cp"><b>경관조명 진단 · 개선안</b>'
          f'<span>{D.LX_CAP}</span></div></div>') if im else ""
    p9 = f"""<div class="sx" style="grid-template-columns:1.1fr 1fr">
<div class="bx"><h3><i>COUNCIL</i>입예협 활동, 주관사가 함께 합니다<small>제안서 {pg('council')}</small></h3>
<div class="rq6">{rq}</div>
<div class="nt" style="margin-top:8px">협상의 주체는 입예협 - 주관사는 자료와 일손으로 돕습니다 · 회의 장소는 입예협이 정합니다</div></div>
<div class="col">
<div class="bx"><h3><i>COMMUNITY</i>커뮤니티 시설 업그레이드 안<small>제안서 {pg('comm', 'lx')}</small></h3>
<ul class="xl"><li><b>공간별 진단 1회</b> - 피트니스 · 북카페 · 스터디룸 · 키즈룸 · 시니어 · 로비의 조명 · 공기 순환 · 차광</li>
<li><b>개선안 1부</b> - 물량 · 공사비 · 유지관리비를 함께 비교</li><li><b>설치는 승인 시</b> - 입예협 · 관리주체 결정 · 별도 견적</li></ul></div>
<div class="bx fl" style="padding:0;overflow:hidden;display:flex;min-height:240px">{ph}</div>
</div></div>"""

    # ---------------------------------------------------------------- 10 · 실적 · 사람
    recs = list(D.RECORDS)
    mx = max(r[3] for r in recs)
    SHORT = {"부산사상 중흥S-클래스 그랜드센트럴": "사상 중흥S클래스", "e편한세상 송도 더퍼스트비치": "송도 더퍼스트비치",
             "두산위브더제니스 센트럴사하": "센트럴사하", "양정자이더샵SK VIEW 1·2단지": "양정자이 1·2단지",
             "춘천 학곡지구 중해마루힐 포레스트": "춘천 중해마루힐", "에코델타 대성베르힐": "대성베르힐",
             "두산위브더제니스 오션시티": "오션시티", "창원 센트럴 아이파크": "창원 센트럴 아이파크"}
    hb = "".join(f'<div><span>{SHORT.get(nm, nm)}<small>{d}</small></span><i style="width:{100 * n / mx:.1f}%"></i><b>{n:,}</b></div>' for d, nm, _, n in recs)
    rec_n, rec_hh = G["_rec_n"], G["_rec_hh"]
    r5 = D.RECENT3_500
    r5_n, r5_j = len(r5), sum(1 for r in r5 if r[3])
    stf = " · ".join(f"{n.replace('팀', '')} {c}" for n, c, _ in D.STAFF)
    pro = "".join(f"<u>{f} {c}</u>" for f, c in G["PRO5"])
    p10 = f"""<div class="sx" style="grid-template-rows:1fr auto">
<div class="sx" style="grid-template-columns:1.15fr 1fr;min-height:0">
<div class="bx"><h3><i>RECORD</i>1,000세대 이상 주관 {rec_n}개 단지 · {rec_hh:,}세대<small>제안서 {pg('r500')}</small></h3>
<div class="hb">{hb}</div><div class="nt" style="margin-top:6px">날짜 = 입주 연월 · 실적 증빙 = 제출서류 03(NICE 연혁 · 실적 확약서 · 주관사 협약서 · 공식 행사일정)</div></div>
<div class="bx"><h3><i>PEOPLE</i>{ST['short']}을 맡을 사람<small>제안서 {pg('people', 'pm')}</small></h3>
<div class="ppl">
<div><i>대표이사 · 결정권자</i><b>고진식</b><span><em>제안 조건을 PT 자리에서 확약</em><br>울산과학대 전기과 · 대한유화 → 엣지조명 대표 → <nobr>㈜엣지컴퍼니 창업(2022.02)</nobr> · 전기공사업 등록 대표자</span></div>
<div><i>주관사업 총괄 본부장 · 책임자</i><b>총괄 본부장</b><span><em>입주예정자협의회 회장 3년 역임</em> - 계약 후 실제 업무를 맡을 책임자</span></div>
<div><i>핵심 운영인력</i><b>임직원 {G['_lead_n']}명</b><span>대표 · 본부장 + {stf} · 단지 전담 PM 1명(명단은 협약 시)</span>
<div class="pro">{pro}</div></div>
</div></div>
</div>
<div class="rec">
<div><b>67<small>개 단지</small></b><span>누적 수임 56,361세대<br>(전신 실적 · 입주 예정 포함)</span></div>
<div><b>{r5_n}<small>개 단지</small></b><span>최근 3년 500세대 이상<br>그중 주관 {r5_j}</span></div>
<div><b>4,470<small>세대</small></b><span>단일 단지 최대<br>레이카운티</span></div>
<div><b>2<small>억원</small></b><span>자본금 · NICE BB-<br>현금흐름 A</span></div>
<div><b>ISO 3종</b><span>9001 · 14001 · 45001<br>{D.ELEC_LICENSE}</span></div>
</div></div>"""

    # ---------------------------------------------------------------- 11 · 담당 체계 · 일정
    mon = mtable(["시기", "주관사 업무", "보고 · 산출물"], "".join(
        f'<tr><td class="n" style="width:110px">{a}</td><td>{t(b)}</td><td class="k">{t(c)}</td></tr>' for a, b, c in G["MON"]))
    p11 = f"""<div class="sx" style="grid-template-columns:1.5fr 1fr">
<div class="bx"><h3><i>SCHEDULE</i>협약부터 입주 후 12개월까지<small>제안서 {pg('mon')}</small></h3>{mon}</div>
<div class="col">
<div class="bx hl"><h3><i>FIELD</i>경인 지사 관리 · 찾아가는 책임자<small>제안서 {pg('pm', 'sameq')}</small></h3>
<ul class="xl"><li><b>관리 거점</b> - 경인 지사(평택) 상설 쇼룸 · 시공 · A/S 관리</li>
<li><b>정기 방문</b> - 협약부터 입주까지 월 1회 + 자문 · 사전점검 · 박람회</li>
<li><b>출동</b> - 의정부 · 양주권 참여업체 먼저 · 직영 품목 · 업체 미응답 건은 본사</li>
<li><b>같은 시기 입주</b> - 우리 단지 업체 모집 · 시공 일정을 먼저 확정</li></ul></div>
<div class="bx fl"><h3><i>BOND</i>계약과 책임은 본사</h3>
<ul class="xl"><li>협약 · 업체 계약 · 보상은 모두 ㈜엣지컴퍼니 명의</li><li>주관사 업무는 하도급 · 재위탁하지 않음(공고 9항 6)</li><li>전문업체는 입예협 사전 서면 승인 시에만</li></ul></div>
</div></div>"""

    pages = [
        ("cover", {}),
        std("한 장 요약", "같은 기준 · 먼저 공개 · [[한 창구]]",
            f"{ST['name']} {hh:,}세대에 드리는 약속을 세 가지로 줄였습니다.", p2,
            ("숫자에는 근거 쪽을 함께 적었고, 제안서는 [[계약서와 같은 효력]]을 갖습니다.", "공고 8항 · 업체 제공 혜택은 참여업체 확정 후 입예협 승인")),
        std("약속 10가지", f"{ST['short']}에 드리는 [[약속 10가지]]",
            "정회원이 먼저 보시는 한 장입니다 - 오른쪽 쪽 번호는 제안서(제출서류 02) 우측 상단 번호입니다.", p3,
            ("지킬 수 있는 [[숫자 하나와 조건]]으로만 약속합니다.", "이 범위를 넘는 요청은 범위 · 비용을 협의해 서면으로 정합니다")),
        std("먼저 묻는 다섯 가지", "입주예정자가 먼저 묻는 [[다섯 가지]]",
            "공고 업무범위 · 우대사항과 공개 자료에서 먼저 나올 질문 다섯 가지에 답했습니다.", p4,
            ("비싸고, 늦고, 연락이 끊기는 입주 준비가 되지 않게 - [[다섯 가지]]에 먼저 답합니다.", "질문은 공고 · 공개 자료 기준(2026.10) · 카페 글 집계 아님")),
        std("세대 혜택", f"세대당 15만원 상당, [[{hh}세대 모두]] 같은 기준입니다",
            f"{hh}세대 × 15만원 상당 = {ft} 상당 안에서 입예협이 골라 담습니다. 주관사가 직접 사서 드리고, 사용 내역을 공개합니다.", p5,
            (f"고른 항목의 합계가 [[{ft} 상당]] 안에 들어오도록 맞춥니다.", "할인으로 드리는 항목 · 공고 업무범위 기본 약속은 차감하지 않음 · 업체 사은품 · 경품 · 정회원 혜택 · 박람회 상품권은 별도")),
        std("가격 검증", "가격은 [[박람회 전에 먼저]] 공개하고, [[계약 후에도]] 지킵니다",
            "공고 1차 종합평가 ‘공동구매 단가’ · 우대 17 ‘최저가 보상’ - 30일 전 검수 · 14일 전 공개 · 계약 후 10배 보상.", p6,
            ("검수는 [[박람회 전]], 보상은 [[계약 후]] - 두 번 확인합니다.", "보상금은 주관사 부담 - 업체 부담을 늘리지 않습니다")),
        std("A/S · 하자", "입주민은 [[한 창구]]로, 처리는 [[기한으로]] 약속합니다",
            "공고 업무범위 5) · 6) · 우대 17 ‘A/S 정책’ - 입주민은 업체를 쫓아다니지 않고, 주관사 한 곳에 연락하시면 됩니다.", p7,
            ("접수 → 24시간 회신 → 48시간 방문 일정 확정 → [[선보상]] → 해피콜까지 주관사가 따라갑니다.", f"제안서 {pg('as', 'desk', 'cpl')}")),
        std("입주지원 범위", "사전점검 · 전문분야 지원, [[횟수로]] 정했습니다",
            "공고 업무범위 2) · 4) · 5) - 할 일과 횟수를 먼저 정했습니다. 외부 전문업체는 입예협 사전 서면 승인 시에만 함께합니다.", p8,
            ("할 수 있는 일을 [[횟수와 함께]] 적었습니다 - 넘는 요청은 서면으로 정합니다.", f"제안서 {pg('work1', 'work2', 'expert', 'desk')}")),
        std("활동 지원 · 커뮤니티", "입예협 활동과 커뮤니티, [[함께 챙깁니다]]",
            "공고 업무범위 3) · 7) · 8) · 참가자격 14 · 우대 17 - 행사 · 공문 · 법무 협력과 커뮤니티 · 경관 진단까지.", p9,
            ("공용부에 쓰는 돈이 [[관리비 · 공구가로 돌아오지 않게]] - 진단과 개선안까지만 약속합니다.", "설치 여부 · 범위 · 비용은 입예협 · 관리주체 결정")),
        std("실적 · 사람", "실적은 [[숫자로]], 운영은 [[사람으로]] 보여 드립니다",
            "제3자 공식 기록이 있는 실적과, 계약 후 이 단지를 맡을 사람입니다.", p10,
            (f"대단지에서 다진 [[운영 시스템]]을 {hh:,}세대 규모에 맞춰 씁니다.", "실적 증빙은 제출서류 03 · 명단은 협약 시 제출")),
        std("담당 체계 · 일정", "협약부터 [[입주 후 12개월]]까지 맡습니다",
            "입주 2027년 11월 예정 기준 - 박람회는 입주 3 ~ 2개월 전, 날짜는 사전점검 일정 확정 뒤 입예협과 정합니다.", p11,
            ("책임자가 [[찾아가고]], 가까운 업체가 [[먼저 출동]]합니다.", "일정은 공정 · 사전점검 일정에 따라 입예협과 조정")),
        ("contact", {}),
    ]
    assert len(pages) == 12, len(pages)

    cover0, contact0 = B.p_cover, B.p_contact

    def cover_sum():
        s = cover0()
        s = G["sub"](s, "<em>입주박람회 주관사 제안서</em>", "<em>입주박람회 주관사 요약제안서</em>")
        s = G["sub"](s, f'<span class="pill">{G["COVER"]["pill"]}</span>', '<span class="pill">요약제안서 · 제출서류 14</span>')
        s = G["sub"](s, f'<div class="tag2">{G["COVER"]["tag"]}</div>',
                     '<div class="tag2">같은 기준 · 먼저 공개 · 한 창구 -<br>정회원이 한눈에 보시도록 10쪽에 담았습니다.</div>')
        return G["sub"](s, '<div class="bt"><span>입주박람회 주관사 제안서</span>', '<div class="bt"><span>입주박람회 주관사 요약제안서</span>')

    def contact_sum():
        # 착수 strategy ⑫: 확약 문장 + 대표번호 · 이메일(휴대번호 없음 — 카페 게시 대상)
        s = contact0()
        s = re.sub(r'<div><b>010-[\d-]+</b><span>[^<]*</span></div>\n?', "", s)
        assert "010-" not in s, "요약 연락처에 휴대번호 남음"
        return G["sub"](s, '<div class="gbar"></div>', f'<div class="gbar"></div><div class="ptq" style="font-size:15px;line-height:1.6;max-width:560px;margin-bottom:14px">{PT_LINE}</div>')

    out = os.path.join(G["HERE"], NAME_SUM + ".html")
    keep_pages, keep_css = list(B.PAGES), B.CSS
    B.p_cover, B.p_contact = cover_sum, contact_sum
    B.CSS += CSS + CSS_NR + ".cv4 h1.cvx{font-size:44px}.ppl{gap:2px}.ppl>div{padding-bottom:2px}.ppl span{font-size:11.8px;line-height:1.34}.ppl .pro{padding:0;border:0;background:none;margin-top:4px}section.page .ppl span{font-size:11.8px!important;line-height:1.3!important}"
    try:
        B.PAGES[:] = pages
        B.OUT_HTML, B.OUT_PDF = out, out[:-5] + ".pdf"
        B.build_html()
        B.PAGES[:] = keep_pages
        G["finish"](out, f"엣지컴퍼니 {D.SITE['name']} 요약제안서")
        doc = open(out, encoding="utf-8").read()
        assert 'class="todo"' not in doc, "요약제안서에는 노란 칸이 없어야 합니다"
        assert not re.search(r"현장 직접 주관|더퍼스트비치\(|8,000|8천", doc), "요약제안서 금지 문구"
        if "--no-pdf" not in sys.argv:
            B.build_pdf()
    finally:
        B.p_cover, B.p_contact = cover0, contact0
        B.CSS = keep_css
        B.PAGES[:] = keep_pages
    print(f"요약제안서 {len(pages)}쪽 → {out}")
    return out
