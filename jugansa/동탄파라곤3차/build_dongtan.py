# -*- coding: utf-8 -*-
"""동탄2 신동 A58BL 파라곤3차 — 임차예정자협의회 주관사 입찰 제안서 빌더.

기본틀(요약제안서 v5, ../요약제안서/build.py)은 건드리지 않고 불러와서 고친다.
- 표지 제목: 동탄2 신동 A58BL 파라곤3차 임차예정자협의회 주관사 선정
- 용어: 입예협/협의회 → 임예협(정식 명칭은 임차예정자협의회)
- 01장 신설 = 공고 8-2-2) 제안내용(박람회·공동구매 계획 / 품목별 예상 참가 업체 / 박람회 특화 제안)
- 기존 01~07장은 02~08장으로 밀고, 실적 장은 제출서류 8)과 같은 숫자(NICE 연혁)로 맞춤

사용: python build_dongtan.py          # HTML + PDF + 2-2 발췌 PDF
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, "..", "요약제안서"))
sys.path[:0] = [BASE, HERE]
import build as B  # noqa: E402  (기본틀 — import 시 PAGES가 채워짐)
import data as D  # noqa: E402

NAME = "엣지컴퍼니_동탄파라곤3차_주관사_입찰제안서"
B.OUT_HTML = os.path.join(HERE, NAME + ".html")
B.OUT_PDF = os.path.join(HERE, NAME + ".pdf")
OUT_22 = os.path.join(HERE, "엣지컴퍼니_동탄파라곤3차_2-2_제안내용.pdf")
t = B.t


def sub(s, old, new):
    """기본틀 문구가 바뀌었으면 조용히 넘어가지 않도록 확인 후 교체."""
    assert old in s, f"기본틀에서 문구를 찾지 못함: {old[:40]}"
    return s.replace(old, new)


def term(s):
    """입예협/협의회 → 임예협. 받침이 생기므로 조사도 같이 바꾼다."""
    s = s.replace("임차예정자협의회", "\0").replace("입주예정자협의회", "\0")
    s = s.replace("입예협", "임예협").replace("입주예정자", "임차예정자")
    s = s.replace("협의회와", "임예협과").replace("협의회가", "임예협이").replace("협의회", "임예협")
    return s.replace("\0", "임차예정자협의회")


# ============================================================ 표 스타일(신규 장)
B.CSS += r"""
.tbl{width:100%;border-collapse:collapse}
.tbl th{font-size:12.5px;font-weight:700;letter-spacing:.24em;color:var(--gold2);text-align:left;
  padding:0 14px 9px;border-bottom:1.5px solid rgba(200,168,106,.55)}
.tbl td{font-size:17px;padding:8.5px 14px;border-bottom:1px dashed rgba(255,255,255,.14);color:var(--sub);line-height:1.42;vertical-align:middle}
.tbl tr:last-child td{border-bottom:0}
.tbl td.k{color:var(--ink);font-weight:700;font-size:17.5px}
.tbl td.n{color:var(--gold);font-weight:800;font-size:15px;width:44px}
.tbl td.g{color:var(--gold);font-weight:700;font-size:14.5px;letter-spacing:.04em;border-right:1px solid rgba(255,255,255,.12)}
.tbl tr.own td{background:rgba(235,203,143,.07)}
.tbl em{font-weight:700}
.tbl.sm td{font-size:15px;padding:6px 14px}
.tbl.sm td.k{font-size:15.5px}
.lg .tile{padding:20px 24px}
.lg .tile .nm{font-size:23px}
.lg .tile .ds{font-size:17.5px;line-height:1.55;margin-top:8px}
.toc4{grid-template-columns:repeat(4,1fr)!important}
.toc4 .col{padding:0 22px}
"""


def table(head, rows_html, cls=""):
    th = "".join(f"<th>{h}</th>" for h in head)
    return f'<table class="tbl {cls}"><thead><tr>{th}</tr></thead><tbody>{rows_html}</tbody></table>'


# ============================================================ 01장 신설 — 2-2) 제안내용
S0 = "01. 동탄 맞춤 제안"
NEW = []


def new(kind, **kw):
    NEW.append((kind, kw))


new("divider", n="01", title="동탄 파라곤 3차를 위한 [[맞춤 제안]]",
    bl=["박람회·공동구매 계획", "품목별 예상 참가 업체", "임대 단지 특화 제안", "공고 업무범위 9개 항목 수행안"])

new("std", sec=S0, title="[[임대 단지]]의 박람회는 달라야 합니다",
    lead="동탄2 신동 A58BL 파라곤 3차 — 공고문 단지개요를 기준으로 설계했습니다.",
    body=B.cards([
        dict(lb="SCALE", big="1,247", unit="세대", nm="18개동 대단지",
             ds="시행 ㈜바우하우스 · 시공 ㈜라인건설. 1,000세대 이상 주관 경험을 그대로 적용합니다."),
        dict(lb="TYPE", big="2", unit="개 타입", nm="82㎡ · 108㎡",
             ds="835세대 · 411세대. 타입이 단순해 커튼·블라인드·조명을 [[규격화]]할 수 있어 단가 협상력이 커집니다."),
        dict(lb="MOVE-IN", big="2027", unit=".02.28", nm="입주 예정",
             ds="설 연휴 전 박람회를 열어 입주 전 시공 일정을 확보합니다."),
        dict(lb="LEASE", big="10", unit="년", nm="공공지원 민간임대", hl=True,
             ds="분양전환권 확정 세대와 거주형 세대는 [[필요한 품목이 다릅니다.]]"),
    ]),
    kp="타입 2개 · 임대 10년 — [[규격화된 공동구매]]와 [[원상복구 걱정 없는 시공]]이 핵심입니다.")

SCOPE = [
    ("박람회 개최·기획, 공동구매 총괄", "전담 PM 지정. 일정·품목·업체·계약 전 과정을 [[임예협과 공유]]하고 진행 현황을 정기 보고."),
    ("품목 구성·업체 섭외·계약·가격 검수", "수요조사로 품목 확정 → 공개 입찰(임예협·주관사 이메일 동시 접수) → 4단계 심사 → 단가표 사전 검수."),
    ("입주 후 A/S·하자 접수·이행관리", "콜센터·카페 신문고·카카오채널 단일 창구. [[24시간 회신 · 48시간 처리]], 업체 회피 시 선보상 후 정산."),
    ("사전점검·입주지원·입주설명회 지원", "현수막·도우미·라돈측정기 10대·커피차 지원, 사전점검 당일 공용부·조경 하자진단 보고서."),
    ("대관·동선·안전·인력·비품·홍보물", "주관사가 직접 대관·운영. [[행사 배상책임보험]] 가입, 안전요원·동선·비상구 계획 수립."),
    ("입주 전·후 전문분야 검토·행정지원", "착공·조경 도면 분석보고서, 열화상 드론·일조 분석, 민원 양식·접수 지원."),
    ("카페·공지채널 홍보 콘텐츠 제작", "카페 디자인, 품목 안내 카드뉴스·영상, 공지 콘텐츠를 주관사가 제작."),
    ("기타 임예협 요청 업무", "시행사·시공사 협의 자리 엔지니어 동석, 온라인 위임장 등 요청 시 지원."),
    ("이벤트 지원", "경품·키즈 프로그램·점등식 등 박람회 이벤트와 정회원 전용 혜택 운영."),
]
new("std", sec=S0, title="공고 업무범위 [[9개 항목]] 수행 방안",
    lead="공고문 4항의 업무를 빠짐없이, 항목별로 답합니다.",
    body=table(["NO", "공고 업무범위", "엣지컴퍼니 수행 방안"], "".join(
        f'<tr><td class="n">{i:02d}</td><td class="k">{t(a)}</td><td>{t(b)}</td></tr>'
        for i, (a, b) in enumerate(SCOPE, 1))),
    kp="제안서는 협약서와 같은 효력 — [[지킬 수 있는 것만]] 적었습니다.")

new("std", sec=S0, title="박람회·공동구매 [[추진 일정]] (안)",
    lead="입주 2027.02.28에서 거꾸로 짰습니다. 설 연휴 전 박람회, 입주 후 1년 사후관리까지.",
    body=B.rows([
        ("2026.10", "주관사 선정·협약 체결 · 임예협 카페/공지채널 지원 시작 · [[품목 수요조사]] 설문"),
        ("2026.11", "참여업체 [[공개 입찰공고]](임예협·주관사 이메일 동시 접수) · 행사장 대관 · 타입별 실측 데이터 준비"),
        ("2026.12", "1·2차 업체 심사 → [[임예협 최종 컨펌]] · 업체 협약식 · 특약이행각서·하자보수 이행각서 징구"),
        ("2027.01", "단가표 사전 공개 · 사전점검 행사 지원 · [[입주박람회 주말 양일]](설 연휴 전) · 온라인 박람회 오픈"),
        ("2027.02~03", "입주 지원 · 현장 베이스캠프·콜센터 운영 · 시공 일정 관리 · 2차 박람회(임예협 협의 시)"),
        ("~2028.02", "입주 후 1년 사후관리 — A/S·하자 이행관리, 협약 종료 시 [[결과 보고서]] 제출"),
    ], title_w=170),
    kp="세부 일정은 사전점검·입주지원센터 일정에 맞춰 [[임예협과 확정]]합니다.")

new("std", sec=S0, title="입주박람회 [[운영 계획]]",
    lead="계약을 재촉하는 자리가 아니라, 확인하고 비교하는 자리로 만듭니다.",
    body=B.tiles([
        dict(lb="WHEN", nm="주말 양일 · 설 연휴 전", ds="2027년 1월 중 토·일 개최(안). 2차 박람회는 임예협 협의 시."),
        dict(lb="WHERE", nm="동탄 생활권 대관 시설", ds="컨벤션·체육관 등 이동이 편한 장소를 주관사가 직접 대관합니다."),
        dict(lb="SAFETY", nm="행사 배상책임보험 가입", ds="안전요원·동선·비상구 계획 수립. 화재·상해 예방 수칙은 참여업체 서약."),
        dict(lb="MEMBERS", nm="정회원 사전예약 · 체크인", ds="정회원 우선 입장·혜택. 임예협 부스를 행사장 중앙에 배치합니다."),
        dict(lb="ONLINE", nm="온라인 박람회 · 라이브", ds="단지 입주민만 들어오는 폐쇄몰. 박람회와 같은 공동구매가."),
        dict(lb="PR", nm="카페·공지채널 콘텐츠", ds="품목 안내 카드뉴스·영상·현수막·알림톡을 주관사가 제작합니다."),
    ], cols=3, rows_n=2).replace('class="tiles"', 'class="tiles lg"'),
    kp="박람회장 가격 = 사전 공개 단가 — [[현장에서 가격이 바뀌지 않습니다.]]")


def vendor_rows():
    out, groups = [], {}
    for g, *_ in D.VENDORS:
        groups[g] = groups.get(g, 0) + 1
    seen = set()
    for g, item, who, note in D.VENDORS:
        cls = ' class="own"' if g == "주관사 직영" else ""
        gcell = "" if g in seen else f'<td class="g" rowspan="{groups[g]}">{g}</td>'
        seen.add(g)
        out.append(f"<tr{cls}>{gcell}<td class=\"k\">{t(item)}</td><td>{t(who)}</td><td>{t(note)}</td></tr>")
    return "".join(out)


new("std", sec=S0, title="품목별 [[예상 참가 업체]]",
    lead="확정은 임예협 공개 입찰·심사 후 — 시공 품목은 동탄·화성 지역업체가 우선입니다.",
    body=table(["구분", "품목", "예상 참가 업체", "비고"], vendor_rows(), "sm"),
    kp=("주관사 직영 품목도 [[같은 심사 · 같은 단가 공개 · 같은 최저가 보장]].", "하도급·타 주관사 연동 계약 없음"))

new("std", sec=S0, title="임대 단지라서 [[달라야 하는 것]]",
    lead="10년을 살 집, 언젠가 내 집이 될 수도 있는 집 — 두 경우를 모두 설계했습니다.",
    body=B.rows([
        ("시공 허용 품목 가이드", "임대사업자와 사전 협의해 품목을 [[허용·조건부·불가]] 3단계로 나눠 박람회 전에 공개합니다. 퇴거 시 원상복구 분쟁을 막습니다."),
        ("두 갈래 패키지", "분양전환 확정 세대는 ‘내 집’ 기준(중문·줄눈·시스템에어컨), 거주형 세대는 [[무타공·이동식·렌탈]] 중심으로 구성합니다."),
        ("세대별 시공 이력 카드", "시공 품목·자재·사진·보증기간을 세대별로 기록해 드립니다. A/S·분양전환·퇴거 때 [[증빙]]이 됩니다."),
        ("하자 창구 분리 접수", "공동구매 시공 하자는 주관사 콜센터가 처리하고, 건물 하자는 접수 후 [[임예협을 통해 임대사업자에 일괄 전달]]합니다."),
        ("타입 2개 규격화", "82·108㎡ 실측 데이터로 커튼·블라인드·조명을 미리 제작해 입주일에 바로 설치합니다."),
    ], title_w=230),
    kp="임차인의 시공은 ‘얼마나 싸게’보다 [[‘나갈 때 문제없나’]]가 먼저입니다.")

new("std", sec=S0, title="동탄 파라곤 3차 [[특화 제안]]",
    lead="엣지컴퍼니 본업(조명·커튼·실링팬)을 임대 단지에 맞게 다시 짰습니다.",
    body=B.tiles([
        dict(lb="01", nm="무타공 전동커튼·블라인드", ds="벽·천장 타공 없이 설치하는 방식을 우선 제안해 원상복구 부담을 줄입니다."),
        dict(lb="02", nm="교체형 조명 패키지", ds="기존 등기구 자리에 교체 설치. 기존 등은 세대에 보관해 퇴거 시 복원할 수 있습니다."),
        dict(lb="03", nm="경관·커뮤니티 조명 컨설팅", ds="임예협 요청 시 단지 경관조명·커뮤니티 조도 개선 제안서를 무상 제출합니다."),
        dict(lb="04", nm="온라인 박람회 · 라이브커머스", ds="박람회 날 오기 어려운 세대도 같은 공동구매가로 온라인 계약할 수 있습니다."),
        dict(lb="05", nm="임차인 입주설명회 지원", ds="입주 절차·사전점검 요령·시공 허용 가이드를 한 자리에서 안내합니다."),
        dict(lb="06", nm="정회원 혜택 · 임예협 부스", ds="정회원 전용 혜택을 구성하고, 임예협 홍보·가입 부스를 중앙에 둡니다."),
    ], cols=3, rows_n=2).replace('class="tiles"', 'class="tiles lg"'),
    kp="제안 품목·혜택은 수요조사 결과에 따라 [[임예협과 최종 확정]]합니다.")

new("std", sec=S0, title="공동구매 단가를 지키는 [[4가지 장치]]",
    lead="공고문이 우려한 ‘행사비 때문에 오르는 단가’를 구조로 막습니다.",
    body=B.cards([
        dict(lb="01", big="공개", nm="단가표 사전 공개", ds="박람회 전 품목별 단가·할인율을 임예협에 제출해 검수받습니다. 현장 가격 변경 없음."),
        dict(lb="02", big="10", unit="배", nm="최저가 차액 보상", ds="동일 브랜드·동일 제품이 더 싸면 차액의 10배 보상. (온라인 판매·시공 품목 제외)"),
        dict(lb="03", big="1~3", unit="%", nm="실적 비례 추가할인", ds="업체 기대매출 초과 시 잔금에서 추가할인. 예: 50·100·150세대 계약 시 1·2·3%."),
        dict(lb="04", big="5", unit="%", nm="계약금 상한", ds="계약금은 총액의 5% 이하, 잔금은 시공·설치 후. 현금·카드 동일가."),
    ]),
    kp="가격은 말이 아니라 [[사전 공개 단가 + 최저가 보장]]으로 검증받습니다.")


# ============================================================ 기존 장 고치기
def walk(v, f):
    if isinstance(v, str):
        return f(v)
    if isinstance(v, list):
        return [walk(x, f) for x in v]
    if isinstance(v, tuple):
        return tuple(walk(x, f) for x in v)
    if isinstance(v, dict):
        return {k: walk(x, f) for k, x in v.items()}
    return v


def bump(kind, kw):
    """기존 01~07장 → 02~08장."""
    kw = dict(kw)
    if kind == "divider":
        kw["n"] = f"{int(kw['n']) + 1:02d}"
    if "sec" in kw:
        kw["sec"] = re.sub(r"^0(\d)\.", lambda m: f"0{int(m.group(1)) + 1}.", kw["sec"])
    return kw


def find(title_part):
    hits = [i for i, (k, kw) in enumerate(B.PAGES) if title_part in kw.get("title", "")]
    assert len(hits) == 1, (title_part, hits)
    return hits[0]


# 실적 장 — 제출서류 8)과 같은 숫자(NICE 연혁)로
i = find("성공사례")
B.PAGES[i][1]["body"] = B.cards([
    dict(lb="2023", big="12", nm="진행 단지", ds="레이카운티 4,470 · 힐스테이트 포항 1,717 · 사상중흥 S-클래스 1,572 등."),
    dict(lb="2024", big="15", nm="진행 단지", ds="양정자이 SK뷰 2,272 · 사송 데시앙 1차 1,712 · 두산위브더제니스 센트럴사하 1,643 등."),
    dict(lb="2025", big="18", nm="진행 단지", ds="춘천 중해마루힐 1,114 · 에코델타 이편한세상 953 등."),
    dict(lb="2026", big="25", nm="확정 단지", ds="두산위브 오션시티 2,813 · 창원 센트럴아이파크 1,540 등 일정 확정 단지 순차 운영."),
])
total = sum(r[3] for r in D.RECORDS)
B.PAGES[i][1]["kp"] = f"최근 5년 1,000세대 이상 주관 [[{len(D.RECORDS)}건 · {total:,}세대]] (NICE 기업신용평가 연혁 기준)"

i = find("[[대단지]] 운영 경험")
big9 = sorted([(d[:4], n, nm) for d, nm, _, n in D.RECORDS]
              + [("2024", 1712, "사송 데시앙 1차"), ("2023", 1572, "사상중흥 S-클래스")], key=lambda r: -r[1])
B.PAGES[i][1]["body"] = B.tiles([dict(lb=y, big=f"{n:,}", unit="세대", nm=nm) for y, n, nm in big9], cols=3, rows_n=3)
B.PAGES[i][1]["kp"] = "최근 5년, 1,000세대 이상 단지만 모아도 [[이 정도]]입니다."

# 입증하기 어려운 표현 정리(공고 9-2 허위·과장 금지)
i = find("공인된 [[자격과 신뢰]]")
B.PAGES[i][1]["body"] = sub(B.PAGES[i][1]["body"], "대기업이 직접 검증한 주관사. LX하우시스·에몬스 추가 협의.", "LX하우시스·에몬스와 제휴 추가 협의 중.")
i = find("정회원 전용")
B.PAGES[i][1]["lead"] = "공동구매가에 더해지는 정회원 전용 혜택입니다."

# 임대 단지: 협상 상대는 시행사(임대사업자)·시공사
i = find("[[조경·착공]] 분석보고서")
kw = B.PAGES[i][1]
kw["lead"] = sub(kw["lead"], "시공사와 협상할 때", "시행사·시공사와 협의할 때")
kw["body"] = sub(kw["body"], "시공사 협상 자리에", "시행사·시공사 협의 자리에")

# 순서: 표지 · 목차 · [01 신설] · 기존(번호 +1)
old = [(k, bump(k, kw)) for k, kw in B.PAGES]
B.PAGES[:] = old[:2] + NEW + old[2:]


# ============================================================ 특수 페이지
def p_cover():
    return """<section class="page cv">
<div class="top"><div><div class="logo">EG</div><div class="en">EDGE COMPANY</div></div>
<div class="who">주식회사 엣지컴퍼니<br>입주박람회 전문 주관사</div></div>
<div class="mid"><span class="pill">공동구매 입찰 제안서</span>
<h1 style="font-size:50px">동탄2 신동 A58BL 파라곤 3차<br><em>임차예정자협의회 주관사 선정</em></h1>
<div class="tag2">박람회를 여는 회사가 아니라, 단지를 완성시키는 회사 — 1,247세대의 시작을 입주 후 1년까지 책임지겠습니다.</div>
<div class="stats">
<div><b>15만원<small>(VAT 포함)</small></b><span>세대당 발전지원금</span></div>
<div><b>현금 1억</b><span>하자 예치금 거치</span></div>
<div><b>10억 / 2년</b><span>이행보증보험</span></div>
<div><b>8가지</b><span>임예협 전용 무상 단지지원</span></div>
</div></div>
<div class="bt"><span>BID PROPOSAL · 주관사 입찰 제안서</span><span>2026.10</span></div>
</section>"""


TOC4 = [
    [("01", "동탄 맞춤 제안", ["단지 이해 · 업무범위", "추진 일정 · 운영 계획", "품목별 참가 업체", "임대 특화 제안", "단가 보호 장치"]),
     ("02", "회사 역량", ["실적·성장", "인증·재무", "지사망·직영", "대표와 채널"])],
    [("03", "조명 특화", ["경관조명 컨설팅", "직수입·생산·KC·시공", "커뮤니티 업그레이드"]),
     ("04", "안전망", ["예치금 1억·보증 10억", "업체 하자보증", "베이스캠프", "콜센터·선보상"])],
    [("05", "업체선정", ["4단계 심사", "지역업체 90%", "최저가 보장", "계약·환불 보호"]),
     ("06", "임예협 지원", ["발전지원금 15만원", "8가지 무상 지원", "조경 분석보고서", "시설 업그레이드"])],
    [("07", "입주민 혜택", ["상품권·백화점권", "정회원 혜택", "사전점검", "이벤트·편의"]),
     ("08", "주관 실적", ["수임실적", "신도시 연속 운영", "대단지 운영"])],
]


def p_toc(no):
    B.TOC = TOC4
    html = B_p_toc(no)
    return sub(html, 'class="toc"', 'class="toc toc4"').replace("요약제안서 <em>목차</em>", "제안서 <em>목차</em>")


B_p_toc = B.p_toc


def p_contact():
    s = B_p_contact()
    s = sub(s, "입주예정자협의회·시공사·협력업체 모두 환영합니다.", "임차예정자협의회·시행사·협력업체 모두 환영합니다.")
    s = sub(s, "울산광역시 울주군 청량읍 상남1길 28, 2동", D.ADDRESS)  # 사업자등록증(2026.08.04) 주소
    return sub(s, "SUMMARY PROPOSAL · 요약제안서", "BID PROPOSAL · 동탄 파라곤 3차")


B_p_contact = B.p_contact


def p_hi_fund(no, sec):
    n = D.SITE["households"] * 15  # 만원
    s = B_p_hi_fund(no, sec)
    return sub(s, "예: 1,000세대 단지 기준 <em>1억 5천만원</em>의 발전지원 규모.",
               f"{D.SITE['households']:,}세대 기준 <em>{n // 10000}억 {n % 10000:,}만원</em>의 발전지원 규모.")


B_p_hi_fund = B.p_hi_fund


def p_closing(no, sec):
    n = D.SITE["households"] * 15
    items = [("세대당 15만원 발전지원금", f"{D.SITE['households']:,}세대 기준 {n // 10000}억 {n % 10000:,}만원 · 임예협 협의 후 집행"),
             ("하자 예치금 1억 · 이행보증보험 10억", "주관사 순수 자산 공동통장 · 증권 실물 제출"),
             ("임예협 전용 8가지 무상 지원", "별도 비용 없음 · 자체 인력"),
             ("임대 단지 시공 허용 가이드", "원상복구 분쟁 예방 · 세대별 시공 이력 카드"),
             ("지역업체 90% 선정", "동탄·화성 지역업체 · 48시간 A/S"),
             ("최저가 보장 차액 10배", "단가표 사전 공개 · 현장 가격 변경 없음"),
             ("48시간 하자보수 · 10년 A/S", "베이스캠프·콜센터 상시 운영"),
             ("경관조명 컨설팅 · 설계 · 생산 · 직접시공", "조명 직수입·KC 인증·면허 시공까지 한 회사")]
    its = "".join(f'<div class="it"><div class="no">{i:02d}</div><div><b>{B.html.escape(a)}</b><p>{B.html.escape(b)}</p></div></div>'
                  for i, (a, b) in enumerate(items, 1))
    return B.render_std(no, sec, "엣지컴퍼니가 [[약속드리는 것]]", "제안서에 쓴 것은 전부 협약서와 증빙으로 남깁니다.",
                        f'<div class="cl">{its}</div>', "못 지키면 [[주관사 자격 철회 동의서]]를 쓰겠습니다.")


B_p_divider_lx = B.p_divider_lx
B.p_cover, B.p_toc, B.p_contact, B.p_hi_fund, B.p_closing = p_cover, p_toc, p_contact, p_hi_fund, p_closing
B.p_divider_lx = lambda: sub(B_p_divider_lx(), '<div class="n">02</div>', '<div class="n">03</div>')


# ============================================================ 빌드
def build():
    B.build_html()
    with open(B.OUT_HTML, encoding="utf-8") as f:
        doc = f.read()
    doc = term(doc)
    doc = doc.replace("url(assets/", "url(../요약제안서/assets/").replace("url('assets/", "url('../요약제안서/assets/")
    doc = doc.replace('src="assets/', 'src="../요약제안서/assets/')
    doc = sub(doc, "<title>엣지컴퍼니 요약제안서</title>", "<title>엣지컴퍼니 동탄 파라곤3차 주관사 입찰제안서</title>")
    left = re.findall(r".{0,12}(?:협의회|입예협).{0,6}", re.sub(r"임차예정자협의회", "", doc))
    assert not left, left
    with open(B.OUT_HTML, "w", encoding="utf-8") as f:
        f.write(doc)
    if "--no-pdf" in sys.argv:
        return
    B.build_pdf()
    # 2-2) 제안내용 발췌본: 표지 + 01장
    import pymupdf as fitz
    src = fitz.open(B.OUT_PDF)
    ex = fitz.open()
    ex.insert_pdf(src, from_page=0, to_page=0)
    ex.insert_pdf(src, from_page=2, to_page=1 + len(NEW))
    ex.set_metadata({"title": "동탄 파라곤3차 2-2 제안내용", "author": D.COMPANY})
    ex.save(OUT_22, garbage=4, deflate=True)
    print(f"2-2 : {OUT_22} ({len(ex)} pages)")


if __name__ == "__main__":
    build()
