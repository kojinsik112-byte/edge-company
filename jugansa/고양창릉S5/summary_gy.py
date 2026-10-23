# -*- coding: utf-8 -*-
"""고양창릉 S-5BL — 요약제안서(공고 필수 제출서류 밖의 선택 자료 · 본부장 10-17 '서류에 없더라도 요약본도 만들어줘'). 오산 summary_os.py 사본을 고양 기준으로.

build_gy.py build() 가 제안서(08)를 만든 뒤 emit_summary(globals()) 로 부른다(--no-summary 면 생략).
대상: 2차 심사(공개 PT 또는 입주자 투표) 전에 입주민이 한눈에 보는 혜택 · 가격 · 환불 · A/S · 박람회 · 단지 맞춤 · 실적 · 공고 대응.
원칙(분당 summary_bd.py와 같은 틀)
- 숫자 · 문구는 제안서와 같은 값(D · ST · CHECK5 · MAP11 · _C7 등)을 그대로 쓴다 - 여기서 새 숫자를 만들지 않는다.
- 제안서 쪽 번호는 방금 만든 제안서의 PGNO · 제목으로 계산한다(쪽이 바뀌면 같이 바뀜).
- 발전지원금 세대당 15만원 상당(총 1억 1,385만원) = 세대 혜택 패키지(안) · 주관사 부담 · 공구가 전가 없음.
- 공고 근거는 고양 공고 표기(◆ 제안서 주요내용 1 ~ 11 · 입찰 참가자격 · 참가 제한 · 필수 제출서류) — 오산 공고 항 번호를 쓰지 않는다.
쪽수: 표지 + 본문 9 + 연락처 = 11쪽.
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "분당퍼스트빌리지"))
from summary_bd import CSS as _CSS_BD  # noqa: E402  (분당 요약제안서와 같은 카드 · 표 스타일)

CSS = re.sub(r"/\*.*?\*/", "", _CSS_BD)  # 주석은 빼고(분당 잔재 문구가 잔재 검사에 걸리지 않게)

NAME_SUM = "엣지컴퍼니_고양창릉S5_요약제안서"

CSS_OS = r"""
.sx .m3{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.sx .m3>div{border:1px solid var(--line);border-radius:10px;padding:9px 13px}
.sx .m3 b{display:block;font-size:14.5px;color:var(--gold)}
.sx .m3 span{display:block;font-size:12.5px;color:var(--sub);line-height:1.42;margin-top:3px}
.sx .lx2{display:grid;grid-template-columns:1fr 1fr;gap:10px;flex:1;min-height:0}
.sx .lx2 .phx{min-height:0}
.sx table.mt td.n{width:62px;white-space:nowrap}
.sx table.mt td{font-size:12.4px;padding:3px 9px;line-height:1.22}
.sx .q4 span{font-size:11.8px}
"""


def emit_summary(G):
    B, D, ST, t = G["B"], G["D"], G["ST"], G["t"]
    PGNO = dict(G["PGNO"])
    sec = "요약제안서"
    main_pages = list(B.PAGES)
    hh, tot = D.FUND_HH, f"{D.FUND_TOTAL:,}만원"
    per = f"{D.FUND}만원"  # 세대당 15만원 상당(본부장 10-17)
    tot = f"1억 {D.FUND_TOTAL - 10000:,}만원"  # 11,385만원 = 1억 1,385만원

    def _plain(s):
        return re.sub(r"\[\[|\]\]", "", s or "")

    def pno(x):
        if x in PGNO:
            return PGNO[x]
        hits = [i for i, (_, kw) in enumerate(main_pages) if x in _plain(kw.get("title"))]
        assert len(hits) == 1, ("요약제안서 - 제안서 쪽을 찾지 못함", x, hits)
        return hits[0] + 1

    def pg(*keys):
        return "p." + " · ".join(f"{n:02d}" for n in sorted({pno(k) for k in keys}))

    def std(label, title, lead, body, kp):
        return ("std", dict(sec=f"{sec} · {label}", title=title, lead=lead, body=body, kp=kp))

    # ---------------------------------------------------------------- 2 · 한눈에
    _tp = " · ".join(a for a, _ in ST["types"])
    _sm = sum(n for a, n in ST["types"] if a[:2] in ("51", "59"))  # 51 · 59㎡ 세대수(570)
    one = [(f"{D.FUND}", "만원 상당", "세대당 발전지원금 (안)", f"총 {tot} · 세대 혜택 패키지 · 주관사 부담 · 공구가와 분리"),
           ("10", "억원 한도", "계약이행보증보험 (협의)", "주관사 선정 후 협의회를 피보험자로 발급 · 입주 개시 1년 전 ~ 개시 후 1년(2년) · 금액은 단지 규모에 맞춰 협약 때 확정"),
           ("1", "억원 한도", "하자 예치금 (협의)", "이행보증으로 갈음 가능 · 둘 중 방식 · 금액은 협약 시 입예협과 협의 · 선보상 재원"),
           ("48", "시간", "하자보수 원칙", "24시간 안에 1차 회신 · 업체 미응답 시 주관사 선보상"),
           ("×10", "", "최저가 차액 10배 보상", "박람회 전 가격 검수 · 계약 후 인근 매장 동일 제품이 더 싸면 차액의 10배(온라인 판매 · 시공 품목 제외)"),
           ("2", "년 이상", "무상 A/S", "계약서에 기간 명시 · 업체 · 품목별 상이 · 주관 창구 입주 후 1년")]
    ob = "".join(f'<div><b>{a}<small>{u}</small></b><div><strong>{n}</strong><span>{c}</span></div></div>' for a, u, n, c in one)
    p2 = f"""<div class="sx" style="grid-template-rows:auto 1fr">
<div class="fact">
<div><b>{ST['households']:,}<small>세대</small></b><span>{ST['buildings']}개 동 · {ST['floors']}<br>경기 고양시 덕양구</span></div>
<div><b>51 ~ 84<small>㎡</small></b><span>{len(ST['types'])}개 타입 · 51 · 59㎡ {_sm * 100 / hh:.0f}%<br>74 · 84㎡ {hh - _sm}세대</span></div>
<div><b>2028.01</b><span>입주 예정 · 공고부터 약 {ST['months']}개월<br>{ST['supply']} · {ST['developer']}</span></div>
<div><b>{ST['builder']}</b><span>시공<br>{ST['project']}</span></div>
</div>
<div class="sx" style="grid-template-columns:.78fr 1.22fr;min-height:0">
<div class="phx"><img src="assets_ins/gy_lx_facade.jpg" alt="" style="object-position:50% 50%">
<div class="cp"><b>{ST['name']}</b><span>경관조명 제안 시뮬레이션 이미지 · 실제와 다를 수 있음</span></div></div>
<div class="bx hl"><h3><i>PROMISE</i>숫자로 드리는 핵심 제안 6가지<small>제안서 {pg('핵심 제안 6가지')}</small></h3><div class="ob">{ob}</div></div>
</div></div>"""

    # ---------------------------------------------------------------- 3 · 발전지원금 세대당 15만원 상당
    p3 = f"""<div class="sx" style="grid-template-columns:1.18fr 1fr">
<div class="bx hl"><h3><i>BENEFIT</i>발전지원금 {tot} 상당 · 세대 혜택 패키지 (안)<small>제안서 {pg('입예협이 골라서', 'sep')}</small></h3>
<div class="fx"><div class="bg">{D.FUND}<small>만원 상당 · 세대당</small></div>
<div class="fm">{hh:,}세대 전 세대 · 총 {tot} 상당<br>= <em>주관사 부담</em> · 공구가에 얹지 않음</div></div>
<div class="pk">
<div><b class="L">A</b><div><strong>입주민 특화서비스 - 세대가 직접 받는 혜택</strong><span>백화점 상품권 세대당 5만원 또는 10만원(세대 현물 직접 지급) · 사전점검 대행 최대 50% 할인 · 타입별 실측 · 샘플하우스 · 항공 VR · 3D 홈스타일링</span></div></div>
<div><b class="L">B</b><div><strong>협의회 업무지원 - 입예협 업무 · 하자 대응</strong><span>공용부 품질 점검 · 도면 분석보고서 · 열화상 드론 · 라돈 측정 · 사전점검 추가 지원 · 온라인 위임장 · 협상 미팅 동석 · 세스코 특수해충 점검</span></div></div>
<div><b class="L">C</b><div><strong>단지지원 컨설팅 - 진단 · 개선안 · 자료 제공</strong><span>동 파사드 · 문주 경관 진단 · 놀이터 · 산책로 조명 진단 · 커뮤니티 · 공용부 조명 · 전기차 충전 인프라 검토 · 입주 기념 점등식</span></div></div>
</div>
<div class="nt" style="margin-top:8px;border-top:1px dashed rgba(200,168,106,.35);padding-top:7px">입예협이 필요한 항목을 골라 같은 범위 안에서 구성 · 주관사가 직접 제공하고 사용 내역 공개 · 항목 · 금액은 협약서로 확정 · C는 진단 · 자료 제공까지(설치 여부 · 비용은 입예협 · 관리주체 결정)</div></div>
<div class="col">
<div class="bx"><h3><i>PRICE</i>세대 혜택과 공구가는 따로입니다</h3>
<div class="sflow">
<div><i>업체</i><div><b>참가비 정액제</b><span>업체 참가비는 정액으로 - 공구가와 연동하지 않음</span></div></div><em>↓</em>
<div><i>주관사</i><div><b>운영비 + 세대 혜택</b><span>박람회 운영비와 세대당 {per} 상당을 주관사 몫에서 부담</span></div></div><em>↓</em>
<div class="k"><i>입주민</i><div><b>세대 혜택 패키지</b><span>A · B · C 중 입예협이 골라 구성 · 사용 내역 공개 · 집행 예: 영주자이 시그니처 전 세대 도어록 763대</span></div></div>
</div>
<div class="nt" style="margin-top:8px">세대 혜택을 0원으로 해도 공구가는 같습니다 - 가격은 업체 공개 입찰 경쟁과 시중가 · 온라인 최저가 검수로 정해집니다.</div></div>
<div class="bx fl"><h3><i>NOTE</i>혜택 범위와 원칙 (안)</h3>
<ul class="xl">
<li><b>주관사 부담 · 공구단가와 무관</b> - 업체 참가비는 정액 · 발전지원금을 공구가에 얹지 않습니다</li>
<li><b>업체 사은품 · 경품 · 정회원 혜택</b> - 참여업체 제공(안) · 15만원 상당과 별도</li>
<li><b>박람회 상품권 · 현장 할인</b> - 참여업체 제공(안) · 15만원과 별도 · 승인 후 확정</li>
<li><b>기본 업무</b> - 행사 · 사전점검 기본 지원은 이 범위와 별도(주관사 부담)</li>
</ul></div>
</div></div>"""

    # ---------------------------------------------------------------- 4 · 가격 투명성
    ck = G["CHECK5"]
    flw = "".join((('<span class="ar">›</span>' if i else "") + f'<div class="st{" hl" if i == 3 else ""}"><i>{a}</i><b>{b}</b><span>{t(c)}</span></div>')
                  for i, (a, b, c) in enumerate(ck))
    p4 = f"""<div class="sx" style="grid-template-rows:auto 1fr">
<div class="flw">{flw}</div>
<div class="sx" style="grid-template-columns:1fr 1fr;min-height:0">
<div class="bx"><h3><i>GUARD</i>공동구매 단가를 지키는 4가지 장치<small>제안서 {pg('guard4')}</small></h3>
<div class="g4">
<div><b>공개</b><strong>단가표 사전 공개</strong><span>박람회 전 품목별 단가 · 할인율 · 모델코드를 입예협이 검수 · 현장 가격 변경 없음</span></div>
<div><b>10<small>배</small></b><strong>최저가 차액 보상</strong><span>인근 매장 동일 제품이 더 싸면 차액 10배 보상(구매 영수증 · 주관사 확인 · 1건당 최대 50만원 · 최대 금액은 입예협과 협의)</span></div>
<div><b>{D.DEPOSIT_MAX}<small>%</small></b><strong>계약금 상한</strong><span>계약금은 총액의 {D.DEPOSIT_MAX}% 이하, 잔금은 시공 · 설치 후</span></div>
<div><b>동일</b><strong>현금 · 카드 동일가</strong><span>결제 방식에 따른 단가 차이 없음 · 현금영수증 발행</span></div>
</div></div>
<div class="bx"><h3><i>× 10</i>최저가 차액 10배 보상 (예시)<small>제안서 {pg('x10')}</small></h3>
<div class="x10">
<div><div class="lb2">박람회 공동구매가 (예시)</div><div class="br" style="width:100%">35만원</div></div>
<div><div class="lb2">인근({ST['local']}) 매장 동일 제품</div><div class="br g" style="width:91.4%">32만원</div></div>
<div class="rw2"><b>30<small>만원</small></b><span>차액 3만원 × 10배 보상<br>+ 판매가 32만원으로 조정</span></div>
<div class="nt">동일 모델 새 제품 · 인근 오프라인 매장 정상가 · 구매 영수증 + 주관사 매장 확인 · 계약 후 7일 이내 · 1건당 최대 50만원 · 최대 금액은 입예협과 협의(세대 · 품목당 1회). 온라인 · 홈쇼핑, 시공 품목, 카드할인 · 사은품, 전시 · 리퍼, 특판 · 한정 수량 행사가는 비교 대상에서 제외(규정 제8조).</div>
</div></div>
</div></div>"""

    # ---------------------------------------------------------------- 5 · 취소 · 환불
    C7, C15, CU = G["_C7"], G["_C15"], G["_CU"]
    rt = "".join(f'<tr class="{c}"><td class="k"><b>{a}</b></td><td>{b}</td></tr>' for a, b, c in [
        ("시공일 7일 전", C7, ""),
        ("시공일 15일 전", C15, ""),
        ("출고 지시 전", f"맞춤 제작 품목({CU})은 업체와 협의 후 취소 · 브랜드 가전 · 가구(미제작 시)", ""),
        ("당일 취소", "사전 해피콜을 하지 않았으면 <strong>모든 품목</strong> 당일 취소 · 환불(공급사 귀책)", "x"),
        ("업체 귀책", "시공 지연 · 계약과 다른 제품 · 하자 미보수로 해지하면 <strong>기한과 관계없이 전액 환불</strong>", "x"),
        ("기한 지난 뒤", "실제 든 자재 · 제작비만 공제 - 업체가 내역을 서면으로 제시하고 주관사가 검토", "x"),
    ])
    p5 = f"""<div class="sx" style="grid-template-columns:1.45fr 1fr">
<div class="bx"><h3><i>DEADLINE</i>품목별 취소 가능 기한 (시공일 기준)<small>규정 전문 제안서 {pg('rule1', 'rule2')}</small></h3>
<table class="rt"><tbody>{rt}</tbody></table>
<div class="nt" style="margin-top:6px">기한 안에 취소하면 납부한 금액 <b style="color:var(--ink)">전액</b>을 환불합니다 · 추가 품목은 성격이 같은 품목의 기한을 따릅니다.</div></div>
<div class="bx hl"><h3><i>REFUND</i>환불은 이렇게 끝까지</h3>
<div class="vf">
<div><b>신청</b><div><strong>기록이 남는 방법으로</strong><span>업체 · 주관 콜센터 · 카페 신문고 · 카카오채널</span></div></div><em>↓</em>
<div class="k"><b>3<small>영업일</small></b><div><strong>안에 환불</strong><span>취소 확정일부터 · 카드는 같은 기한에 승인 취소</span></div></div><em>↓</em>
<div><b>해피콜</b><div><strong>환불 완료 확인</strong><span>주관사가 계약자에게 직접 확인</span></div></div><em>↓</em>
<div><b>선보상</b><div><strong>업체가 미루면</strong><span>콜센터 접수 → 사실 확인 후 주관사가 먼저 보상</span></div></div>
</div>
<div class="nt" style="margin-top:8px">계약금 {D.DEPOSIT_MAX}% 이하 · 잔금은 시공 · 설치 확인 후 · 규정은 모든 공동구매 계약서에 첨부</div></div>
</div>"""

    # ---------------------------------------------------------------- 6 · A/S · 하자
    as5 = "".join((('<span class="ar">›</span>' if i else "") + f'<div class="st{" k" if k else ""}"><b>{a}</b><strong>{b}</strong><span>{c}</span></div>')
                  for i, (a, b, c, k) in enumerate([
                      ("1<small>창구</small>", "주관 콜센터 접수", f"{D.TEL} 평일 · 카페 신문고 · 카카오채널 365일", False),
                      ("24<small>시간</small>", "안에 1차 회신", "담당 지정 · 업체 미응답 시 주관사가 직접 개입", False),
                      ("48<small>시간</small>", "하자보수 원칙", "주관사 관리 · 감독 · 미해결 시 하자지연 패널티", False),
                      ("선보상", "업체가 미루면", "입주민께 먼저 보상하고 업체와는 나중에 정산", True),
                      ("해피콜", "완료 확인 후 종결", "접수 · 처리 · 지연 사유 기록 · 정례 보고", False),
                  ]))
    p6 = f"""<div class="sx" style="grid-template-rows:auto 1fr auto">
<div class="as5">{as5}</div>
<div class="sn3">
<div class="bx hl"><b class="n"><i>최대</i>1<small>억원</small></b><strong>하자 예치금 · 선보상 재원</strong>
<ul class="xl"><li>엣지컴퍼니 자산으로 예치 - 참여업체에게 걷은 돈이 아닙니다</li><li>업체 사고 · 도산 시에도 입주민 먼저 보상</li><li>예치 여부 · 금액은 협약 시 협의(이행보증으로 갈음 가능)</li></ul></div>
<div class="bx"><b class="n"><i>최대</i>10<small>억원</small></b><strong>계약이행보증보험 2년</strong>
<ul class="xl"><li>계약이행 · 하자보수 이행 보증 - 금액은 협약으로 확정</li><li>주관사 선정 후 협의회를 피보험자로 증권 발급 · 입주 개시 1년 전 ~ 개시 후 1년(필수 제출서류 13)</li><li>업체 도산 시 동종업체로 이관 · 비용은 엣지컴퍼니 부담</li></ul></div>
<div class="bx"><b class="n">2<small>년 이상</small></b><strong>무상 A/S · 참여업체 하자보증</strong>
<ul class="xl"><li>무상 A/S 최소 2년(계약서 명시 · 업체 · 품목별 상이)</li><li>참여업체 전원 특약이행각서 9개 항 · 하자보수 이행각서</li><li>패널티 3단계: 홍보정지 → 총액 10% 배상 → 자격박탈 · 계약 이관</li></ul></div>
</div>
<div class="rs2">
<div><b>업체 부담은 늘리지 않습니다</b><span>콜센터 운영비 · 하자 예치금은 주관사 부담 - 업체 예치금 · 추가 보증금 없음 · 업체가 부담을 떠안으면 단가가 오르기 때문입니다</span></div>
<div><b>책임부터 나눕니다</b><span>시공사({ST['builder']}) 하자는 시공사 창구로 접수 대행 · 회신 추적, 공동구매 납품 · 시공 하자는 참여업체 + 주관사 책임 - 떠넘기지 않습니다</span></div>
</div></div>"""

    # ---------------------------------------------------------------- 7 · 입주박람회
    t6 = "".join(f'<div><i>{a}</i><b>{b}</b><span>{c}</span></div>' for a, b, c in [
        ("WHEN", f"{ST['expo']} 2 ~ 3일 (안)", "입주(2028.01) 2 ~ 3개월 전 - 일수 · 날짜는 사전점검 일정에 맞춰 협의회와 확정합니다."),
        ("WHERE", "행사장 후보 3곳", "① " + ST["venues"][0] + " ② " + ST["venues"][1] + " ③ " + ST["venues"][2] + " - 입예협과 답사한 뒤 확정합니다."),
        ("FAMILY", "놀이방 · 수유실 · 유모차", "어린이 놀이방 · 수유실 · 유모차 대여와 입구 안내데스크 · 카페테리아를 둡니다."),
        ("PRICE", "사전 공개 단가 그대로", "박람회장 가격 = 입예협이 검수한 사전 공개 단가 - 결제 방식과 관계없이 같습니다."),
        ("ONLINE", "온라인 박람회 · 카카오 상담", "단지 입주민만 들어오는 폐쇄몰 · 박람회와 같은 공동구매가 - 못 오셔도 같은 조건입니다."),
        ("SAFETY", "안전계획 · 구급 · 보험", "미아 방지 · 대피로 · 부스 전기 점검 · 보안 · 구급 · 119 연계 · 박람회 기간 행사장 기준 행사주최자배상책임보험 가입 · 개장 전 증권 사본 제출."),
    ])
    p7 = f"""<div class="sx" style="grid-template-rows:1fr auto auto">
<div class="t6">{t6}</div>
<div class="chips"><i>편의시설</i><span>에어바운스</span><span>영화 상영회</span><span>입예협 부스</span><span>카페테리아</span><span>수유실</span><span>휴게실</span><span>유모차 대여</span><span>안마의자 체험</span></div>
<div class="chips"><i>미리 보기</i><span>타입별 실측 사이즈</span><span>샘플하우스</span><span>항공 VR 촬영</span><span>3D 홈스타일링</span><span>카페 · 공지채널 콘텐츠(게시 전 입예협 승인)</span></div>
</div>"""

    # ---------------------------------------------------------------- 8 · 고양창릉 S-5BL 맞춤
    p8 = f"""<div class="sx" style="grid-template-columns:1.05fr 1fr">
<div class="col">
<div class="bx hl"><h3><i>51 ~ 84㎡ · {hh}세대</i>단지 규모에 맞춰 먼저 정할 것<small>제안서 {pg('먼저 챙길 것', 'special')}</small></h3>
<ul class="xl">
<li><b>{len(ST['types'])}개 타입 표준 견적</b> - {_tp} 타입별 실측으로 커튼 · 수납 · 조명 표준 견적표를 박람회 전에 공개</li>
<li><b>품목 · 업체 수 맞춤</b> - 수요조사 결과로 정합니다. 업체가 과하면 업체당 계약이 줄어 단가가 오히려 오를 수 있습니다</li>
<li><b>유상옵션 겹침 확인</b> - 모집공고 유상옵션 · 기본 제공 품목과 겹치면 권하지 않고 남은 수요만 모집</li>
<li><b>인근 시공 업체</b> - {ST['local']} 업체 우선 · 48시간 A/S가 되는 거리</li>
</ul></div>
<div class="bx fl"><h3><i>COUNCIL</i>시행 · 시공사 협의, 관리표로<small>제안서 {pg('req')}</small></h3>
<div class="vf" style="flex:0">
<div><b>접수</b><div><strong>입예협 건의 접수 · 담당 지정</strong><span>품질 · 시공 · 옵션 · 입주 일정 · 생활 인프라</span></div></div>
<div><b>협의</b><div><strong>기술 검토 · 협의 자료 · 동석</strong><span>공문 초안 · 질의서 · 현장 사진 · 도면 - 입예협 이름으로 발송</span></div></div>
<div class="k"><b>공유</b><div><strong>반영 · 보류 사유까지 기록</strong><span>‘협의 완료’와 ‘설치 완료’를 나눠 정례회의마다 보고</span></div></div>
</div></div>
</div>
<div class="col">
<div class="bx fl"><h3><i>LIGHTING</i>경관조명, 입주 전에 진단합니다<small>제안서 {pg('lx', 'lx2')}</small></h3>
<div class="lx2"><div class="phx"><img src="assets_ins/gy_lx_gate.jpg" alt=""><div class="cp"><b>정문 문주</b><span>시뮬레이션 이미지</span></div></div>
<div class="phx"><img src="assets_ins/gy_lx_play.jpg" alt=""><div class="cp"><b>어린이놀이터</b><span>{D.LX_PLAY_CAP}</span></div></div></div>
<div class="nt" style="margin-top:8px">동 파사드 → 정문 문주 → 놀이터 · 산책로 순서로 진단해 개선안을 냅니다(전기공사업 등록 업체) · 설치 여부 · 비용은 입예협 · 관리주체가 정합니다.</div></div>
<div class="m3">
<div><b>전담 4개 팀 12명</b><span>행사관리 4 · 영업 2 · 이벤트 3 · 대외지원 3 (안)</span></div>
<div><b>24시간 1차 회신</b><span>입예협 요청은 담당 지정 후 회신</span></div>
<div><b>월별 타임테이블</b><span>2026.10 ~ 2028.01 업무 · 보고 · 산출물</span></div>
</div>
</div></div>"""

    # ---------------------------------------------------------------- 9 · 실적 · 사람
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
    stf = " · ".join(f"{n} {c}" for n, c, _ in D.STAFF)
    pro = "".join(f"<u>{f} {c}</u>" for f, c in G["PRO5"])
    p9 = f"""<div class="sx" style="grid-template-rows:1fr auto">
<div class="sx" style="grid-template-columns:1.15fr 1fr;min-height:0">
<div class="bx"><h3><i>RECORD</i>1,000세대 이상 주관 {rec_n}개 단지 · {rec_hh:,}세대<small>제안서 {pg('1,000세대 이상 주관 단지', 'r500')}</small></h3>
<div class="hb">{hb}</div><div class="nt" style="margin-top:6px">날짜 = 입주 연월 · 실적 증빙 = 제출서류 9(별지 2 총괄표 · NICE 연혁 · 실적 확약서 · 주관사 협약서)</div></div>
<div class="bx"><h3><i>PEOPLE</i>{ST['short']}을 맡을 사람<small>제안서 {pg('people', 'pm')}</small></h3>
<div class="ppl">
<div><i>대표이사</i><b>고진식</b><span><em>주관 박람회 전 과정 현장 점검 · 진두지휘</em> - 협약 최종 책임 · PT 참석<br>울산과학대 전기과 · 대한유화 → 엣지조명 대표 → <nobr>㈜엣지컴퍼니 창업(2022.02)</nobr> · 전기공사업 등록 대표자</span></div>
<div><i>주관사업 총괄 본부장 · 전담 총괄</i><b>총괄 본부장</b><span><em>입주예정자협의회 회장 3년 역임</em> - 협의회 운영을 직접 겪어 봤습니다 · 정례회의 · 박람회 · 사전점검 현장 참석</span></div>
<div><i>핵심 운영인력</i><b>임직원 {G['_lead_n']}명</b><span>대표 · 본부장 + {stf}명 - 단지 전담 PM 지정(명단은 협약 시 제출)</span>
<div class="pro">{pro}</div></div>
</div></div>
</div>
<div class="rec">
<div><b>67<small>개 단지</small></b><span>누적 수임 56,361세대<br>(전신 실적 · 입주 예정 포함)</span></div>
<div><b>{r5_n}<small>개 단지</small></b><span>최근 3년 500세대 이상 진행<br>그중 주관 {r5_j}</span></div>
<div><b>4,470<small>세대</small></b><span>단일 단지 최대<br>레이카운티</span></div>
<div><b>2<small>억원</small></b><span>자본금 · NICE BB-<br>현금흐름 A</span></div>
<div><b>ISO 3종</b><span>9001 · 14001 · 45001<br>{D.ELEC_LICENSE}</span></div>
</div></div>"""

    # ---------------------------------------------------------------- 10 · 공고 대응
    mt = "".join(f'<tr><td class="n">{a}</td><td class="k">{t(b)}</td><td>{t(c)}</td><td class="pg">{pg(*ks)}</td></tr>'
                 for a, b, c, ks in G["MAP11"])
    p10 = f"""<div class="sx" style="grid-template-rows:1fr auto">
<div class="bx"><h3><i>공고 ◆ 주요내용</i>제안서 주요내용 11개 → 제안서 쪽<small>쪽 번호 = 제안서 우측 상단 번호</small></h3>
<table class="mt"><thead><tr><th>NO</th><th>공고 기준</th><th>엣지컴퍼니 제안 핵심</th><th>제안서 쪽</th></tr></thead><tbody>{mt}</tbody></table></div>
<div class="q4">
<div><i>참가자격</i><b>7개 항목 충족<em>{pg('qual')}</em></b><span>전시 · 박람회 업종 · 500세대 이상 주관 · 운영 {r5_n}개 단지(주관 {r5_j}) · 국세 · 지방세 완납 · 영업배상책임보험 · NICE BB-</span></div>
<div><i>참가 제한</i><b>10개 사유<em>{pg('ban')}</em></b><span>모두 해당 없음 - 담합 · 금품 · 허위 · 비방 없음 · 청렴계약 이행 준수 서약(별지 4)</span></div>
<div><i>절차 · 주의사항</i><b>서류 → PT → 30일 내 계약<em>{pg('note')}</em></b><span>PT는 책임자(총괄 본부장) 발표 · 대표이사 동석 · 일괄 도급 · 미선정 시 별도 행사 없음(별지 5)</span></div>
<div><i>이행 이력</i><b>보증보험 · 예치금<em>{pg('bond')}</em></b><span>보증보험증권 발급 · 법무법인 예치금 약정 이력 - 금액은 싣지 않았습니다</span></div>
</div></div>"""

    pages = [
        ("cover", {}),
        std("한눈에", "투표 전에, [[한눈에]] 보시도록",
            f"{ST['name']} {ST['households']:,}세대 - 우리 집이 받는 혜택과 약속을 한 장에 모았습니다.", p2,
            ("혜택은 [[조건까지]], 가격은 [[같은 조건 총액]]으로 보여 드립니다.", "‘(안)’ = 참여업체 · 항목 확정 후 입예협 승인으로 확정")),
        std("세대 혜택", f"세대당 {per} 상당, [[세대 혜택]]으로 드립니다",
            "공고 주요내용 4 - 입예협이 고른 항목을 주관사가 직접 구매 · 제공합니다. 주관사 부담이라 공구단가에 영향을 주지 않습니다.", p3,
            (f"{hh:,}세대 · 세대당 {per} 상당 = [[발전지원금 {tot} 상당]] (안)", "주관사 부담 · 사용 내역 공개 · 협약서로 확정 · 집행 예: 영주자이 시그니처 전 세대 도어록 지문형 763대")),
        std("가격 투명성", "가격은 [[박람회 전에]] 검수하고, [[계약 후에도]] 지킵니다",
            "공고 주요내용 4 - 시중가 · 온라인 최저가와 같은 조건 총액으로 비교하고, 입예협 검수를 거친 단가만 공개합니다.", p4,
            ("검수는 [[박람회 전]], 보상은 [[계약 후]] - 두 번 확인합니다.", f"유상옵션과 겹치는 품목은 권하지 않고 남은 수요만 모집 · 제안서 {pg('first', 'items')}")),
        std("취소 · 환불", "취소는 [[기한 안이면 전액]], 환불은 [[3영업일]] 안에",
            "공고 주요내용 8 · 9 · 별지 3 - 계약 취소 · 환불 규정(제1 ~ 10조 · 별표)을 모든 공동구매 계약서에 첨부합니다.", p5,
            ("기한 안 취소는 [[전액 환불]], 업체 귀책이면 [[기한과 관계없이]] 전액 환불합니다.", "규정 전문은 제안서 03장")),
        std("A/S · 하자", "입주민은 [[한 창구]]로, 처리는 [[기한으로]] 약속합니다",
            "공고 주요내용 8 · 9 - 입주민은 업체를 쫓아다니지 않고, 주관사 한 곳에 연락하시면 됩니다.", p6,
            ("접수 → 24시간 회신 → 48시간 처리 → [[선보상]] → 해피콜까지 주관사가 따라갑니다.", f"제안서 {pg('as', 'defect', 'call', 'trust')}")),
        std("입주박람회", "가족이 함께 [[확인하고 비교하는]] 2 ~ 3일",
            "계약을 재촉하는 자리가 아니라, 아이와 함께 와서 쉬고 비교하고 상담하는 박람회로 만듭니다.", p7,
            ("박람회장 가격 = 사전 공개 단가 - [[결제 방식과 관계없이]] 같습니다.", f"일정 · 장소 · 배치는 입예협과 확정 · 제안서 {pg('expo')}")),
        std("단지 맞춤", f"{ST['short']}, [[{len(ST['types'])}개 타입 · {hh}세대]]에 맞춥니다",
            "공고 주요내용 10 · 11 - 대단지 방식을 그대로 옮기지 않고, 단지 규모와 면적에 맞춰 다시 짰습니다.", p8,
            ("협상의 주체는 입예협 - 주관사는 [[자료와 기록]]으로 돕습니다.", f"월별 업무 타임테이블 제안서 {pg('mon1', 'mon2')}")),
        std("실적 · 사람", "실적은 [[숫자로]], 운영은 [[사람으로]] 보여 드립니다",
            "공고 입찰 참가자격 2 · 3 - 서류로 확인되는 주관 실적과, 이 단지를 맡을 사람입니다.", p9,
            ("대단지에서 다진 [[운영 시스템]]을 {:,}세대 규모에 맞춰 씁니다.".format(hh), "실적 증빙은 제출서류 9 · 15 · 조직은 제출서류 16 · 명단은 협약 시 제출")),
        std("공고 대응", "공고가 요구한 것, [[제안서 쪽 번호]]로 확인하세요",
            "공고 ◆ 제안서 주요내용 11개와 입찰 참가자격 · 참가 제한 · 심사 및 선정절차 대응을 한 장으로 정리했습니다.", p10,
            ("제안서에 쓴 것은 전부 [[협약서와 증빙]]으로 남깁니다.", "상세는 제안서(제출서류 8)와 제출서류 9 · 15 · 16에 있습니다")),
        ("contact", {}),
    ]
    assert len(pages) == 11, len(pages)

    cover0 = B.p_cover

    def cover_sum():
        s = cover0()
        im, _own = G["slot"]("cover")
        s = G["sub"](s, f'<div class="cvart cvx osc day"><img src="assets_ins/{im}.jpg" alt="">',
                     '<div class="cvart cvx osc"><img src="assets_ins/gy_lx_gate.jpg" alt="" style="object-position:50% 55%">')
        s = G["sub"](s, f"{D.SITE['name']} 조감도 · 홍보용 이미지 · 실제와 다를 수 있음", f"{D.SITE['name']} 정문 문주 경관조명 제안 · 시뮬레이션 이미지 · 실제와 다를 수 있음")
        s = G["sub"](s, "<em>입주박람회 주관사 제안서</em>", "<em>입주박람회 주관사 요약제안서</em>")
        s = G["sub"](s, f'<span class="pill">{G["COVER"]["pill"]}</span>', '<span class="pill">요약제안서 · 참고 자료</span>')
        s = G["sub"](s, f'<div class="tag2">{G["COVER"]["tag"]}</div>',
                     '<div class="tag2">투표 전에 한눈에 보시도록 -<br>혜택 · 가격 · 환불 · A/S · 실적을 9쪽에 담았습니다.</div>')
        return G["sub"](s, '<div class="bt"><span>입주박람회 주관사 제안서</span>', '<div class="bt"><span>입주박람회 주관사 요약제안서</span>')

    out = os.path.join(G["HERE"], NAME_SUM + ".html")
    keep_pages, keep_css = list(B.PAGES), B.CSS
    B.p_cover = cover_sum
    B.CSS += CSS + CSS_OS + ".cv4 h1.cvx{font-size:44px}.ppl{gap:3px}.ppl>div{padding-bottom:3px}.ppl span{font-size:11.8px;line-height:1.34}.ppl .pro{padding:0;border:0;background:none;margin-top:4px}"
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
        B.p_cover = cover0
        B.CSS = keep_css
        B.PAGES[:] = keep_pages
    print(f"요약제안서 {len(pages)}쪽 → {out}")
    return out
