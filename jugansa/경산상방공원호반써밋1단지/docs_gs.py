# -*- coding: utf-8 -*-
"""경산 상방공원 호반써밋 1단지 — 제출서류 조립(공고 제4조 · 모두 자체 양식 · 본부장 10-28 '이 PC에서 다시 만들기').

순서: build_gs.py --no-pdf → python3 ../tools/light_build.py 경산상방공원호반써밋1단지 → python3 docs_gs.py [--final]
출력: 제출본/엣지컴퍼니_경산상방공원호반써밋1단지_주관사_제안서_제출서류.pdf(통합 1개 · 메일 대용량 첨부)
      + 제출본/번호별/NN_항목.pdf(확인용) · 작업/(자체 양식 HTML · 중간 PDF)
- 증빙은 이 PC의 원본 · 가림 끝난 최근 제출본에서 가져온다(EV). 가림을 새로 하지 않는다.
- 날인: 자체 양식 = 직인(사용인감 · 사용인감계로 신고) · 법인인감 = 사용인감계 실물 날인 스캔만(규칙 4).
- 메일용(저용량) PDF는 만들지 않는다(규칙 2).
"""
import html as _h
import os
import pathlib
import subprocess
import sys

import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.normpath(os.path.join(HERE, "..", "요약제안서"))]
import data as D  # noqa: E402
import build as BASE  # noqa: E402  (find_chrome)

FINAL = "--final" in sys.argv
NAME = "엣지컴퍼니_경산상방공원호반써밋1단지"
WORK, OUT = os.path.join(HERE, "작업"), os.path.join(HERE, "제출본")
SIGN = "2026년 10월 29일"   # 사용인감계 실물 날인일과 같게
B = "C:/본부장/"
BID = B + "05주관사 입찰공고/"
SJ = BID + "20261026_상주 자이르네/[주식회사 엣지컴퍼니]_상주자이르네_주관사입찰서류.pdf"   # 10-28 최종 · 가림 끝난 증빙 쪽
EV = {
    "proposal": os.path.join(HERE, f"{NAME}_주관사_사업제안서_밝은시안.pdf"),
    "company": os.path.join(HERE, f"{NAME}_회사소개서_밝은시안.pdf"),
    "biz": (SJ, [3]),                       # 사업자등록증 2026.10.14
    "reg": (SJ, [4, 5]),                    # 법인등기부 2026.10.14 · 대표 주소 가림
    "tax": (SJ, [6, 7]),                    # 국세 · 지방세 2026.10.14 · 휴대번호 가림
    "roster": (SJ, [13, 14]),               # 4대보험 사업장가입자명부 2026.10.23 · 성명 가운데 · 주민번호 뒷자리 가림
    "mou3": (SJ, [22, 23, 24]),             # 주관사 협약서 3건(센터포인트 · 드파인 센텀 · 디에트르) · 서명란 · 대표 가림
    "ingam": (BID + "20261029_엘리프 한신더휴 수원/클라우드_첨부_7개_20261028/법인인감증명서.pdf", None),   # 2026.10.26 · 주민번호 뒷자리 가림
    "seal": (BID + "20261030_경산 상방공원 호반써밋 1단지/날인서류_20261029/경산_사용인감계_법인인감날인_스캔_20261029.pdf", None),
    "fin25": (B + "02입찰공고필요양식(대외비)/9.최근 3년간 재무제표/표준재무제표증명.pdf", None),     # 2025 · 국세청 2026.06.18
    "fin24": (BID + "20261021_판교테크노밸리 중흥S-클래스/엣지컴퍼니_판교테크노밸리중흥S_제출서류/엣지컴퍼니_판교테크노밸리중흥S_12_최근2년_재무제표_손익계산서.pdf", [1, 2, 3, 4, 5, 6]),  # 제3기 2024(당) · 제2기 2023(전)
    "nice": (BID + "20261024_창릉신도시 S5/엣지컴퍼니_고양창릉S5_제출서류/15_신용평가서_상세내역/엣지컴퍼니_고양창릉S5_15_신용평가서_상세내역.pdf", list(range(2, 26))),  # 전문 24쪽 · 13쪽 생년월일 가림
    "elec": (B + "02입찰공고필요양식(대외비)/11.기타/전기공사업 등록증.pdf", None),
    "iso": (B + "02입찰공고필요양식(대외비)/11.기타/[글로벌시스템인증원]주식회사 엣지컴퍼니ISO인증.pdf", None),
    "kb": (BID + "20261024_창릉신도시 S5/엣지컴퍼니_고양창릉S5_제출서류/12_영업배상책임보험_증서/엣지컴퍼니_고양창릉S5_12_영업배상책임보험_증서.pdf", None),
    "dnb": (B + "협력사_협약서/20261028_디엔비파트너스건축사사무소/업무협약서_엣지컴퍼니_디엔비파트너스건축사사무소_20261028_양측날인_2쪽을정보모자이크_v2.pdf", None),
}
STAMP = os.path.join(HERE, "assets_ins", "jigin_t.png")   # 직인(사용인감) — 경산 사용인감계 출력본의 사용인감 칸 이미지
FONT = "C:/Windows/Fonts/malgun.ttf"

CSS = """@page{size:A4;margin:16mm 16mm 14mm}*{box-sizing:border-box}
body{margin:0;font-family:"Malgun Gothic","맑은 고딕",sans-serif;font-size:10pt;line-height:1.55;color:#111;word-break:keep-all}
.hd{display:flex;justify-content:space-between;font-size:8.5pt;color:#8a6d2b;border-bottom:1.2pt solid #8a6d2b;padding-bottom:2mm;margin-bottom:6mm}
h1{font-size:17pt;margin:0 0 2mm;letter-spacing:1pt}h1 small{font-size:10pt;color:#555;font-weight:400;margin-left:2mm}
.gun{font-size:9.5pt;color:#333;margin:0 0 4mm}
table{width:100%;border-collapse:collapse;margin:0 0 4mm}th,td{border:.6pt solid #666;padding:1.6mm 2.2mm;font-size:9pt;vertical-align:middle}
th{background:#f1ede3;font-weight:700;text-align:center}td.c{text-align:center}td.r{text-align:right}td.k{font-weight:700;background:#faf8f3}
.note{font-size:8.6pt;color:#444;margin:2mm 0}.box{border:.6pt solid #999;border-radius:2mm;padding:3mm 4mm;margin:3mm 0;font-size:9.5pt}
ol{margin:2mm 0 0;padding-left:6mm}ol li{margin:0 0 2.2mm}
.sig{margin-top:10mm;text-align:right;font-size:10.5pt;line-height:2}.sig .st{position:relative;display:inline-block}
.sig img{position:absolute;right:-6mm;top:-7mm;width:22mm;opacity:.92}
.to{margin-top:8mm;text-align:center;font-size:12pt;font-weight:700}
.rec th,.rec td{padding:.8mm 2mm;font-size:8.1pt}.sig.tight{margin-top:3mm;line-height:1.75}.sig,.to{page-break-inside:avoid}
.pb{page-break-before:always}.cap{display:grid;grid-template-columns:1fr;gap:5mm}
.cap figure{margin:0;border:.6pt solid #bbb;padding:3mm}.cap img{width:100%;max-height:100mm;object-fit:contain}
.cap figcaption{font-size:8.8pt;margin-top:2mm}.cap b{color:#8a6d2b}
"""


def hd(no, title):
    return f'<div class="hd"><span>제출서류 {no} · {_h.escape(title)}</span><span>주식회사 엣지컴퍼니 · 입주업무 주관사 선정 입찰</span></div>'


GUN = f'<p class="gun">건명 : {D.SITE["name"]} 입주예정자협의회 입주업무 주관사 선정 공고</p>'


def sig(to=True, tight=False):
    st = f'<img src="{pathlib.Path(STAMP).as_uri()}" alt="">' if os.path.exists(STAMP) else ""
    return (f'<div class="sig{" tight" if tight else ""}">{SIGN}<br>상 호 : {D.COMPANY}<br>대 표 자 : 대표이사 {D.CEO} <span class="st">(인){st}</span></div>'
            + (f'<div class="to">{D.SITE["name"]} 입주예정자협의회 귀중</div>' if to else ""))


def html2pdf(name, body):
    os.makedirs(WORK, exist_ok=True)
    src = os.path.join(WORK, name + ".html")
    pdf = os.path.join(WORK, name + ".pdf")
    with open(src, "w", encoding="utf-8") as f:
        f.write(f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}</body></html>')
    subprocess.run([BASE.find_chrome(), "--headless", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=4000",
                    f"--print-to-pdf={pdf}", pathlib.Path(src).as_uri()], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return pdf


def src_pages(key):
    p, pages = EV[key] if isinstance(EV[key], tuple) else (EV[key], None)
    assert os.path.exists(p), ("증빙 원본 없음", key, p)
    d = fitz.open(p)
    return d, [i - 1 for i in pages] if pages else list(range(d.page_count))


def band(page, text):
    """가져온 증빙 쪽 위 여백에 '제출서류 N · 항목' 머리글(원본 내용은 건드리지 않음)."""
    r = page.rect
    page.insert_textbox(fitz.Rect(18, 6, r.width - 18, 20), text, fontsize=7.5, fontname="mg", fontfile=FONT, color=(0.54, 0.43, 0.17))


# ------------------------------------------------------------ 자체 양식
def form_fin():
    rows = [("2025년(제4기)", "표준재무제표증명(국세청 발급 · 2026.06.18) - 재무상태표 · 손익계산서 · 부속명세서", "4쪽"),
            ("2024년(제3기)", "재무제표 - 재무상태표 · 손익계산서 · 공사원가명세서 · 이익잉여금처분계산서(당기 열)", "6쪽"),
            ("2023년(제2기)", "위 2024년 재무제표의 전기(비교) 열 - 같은 6쪽에 함께 표시", "-")]
    return html2pdf("06_재무제표_안내", hd("06", "최근 3년간 재무제표") + "<h1>최근 3년간 재무제표</h1>" + GUN
                    + "<table><tr><th>사업연도</th><th>서류</th><th>쪽</th></tr>"
                    + "".join(f'<tr><td class="k c">{a}</td><td>{b}</td><td class="c">{c}</td></tr>' for a, b, c in rows) + "</table>"
                    + '<p class="note">재무 요약(NICE 기업신용평가 2026.06.19): 신용등급 BB- · 현금흐름등급 A · 자본금 2억원. 원본 열람은 협의회 요청 시 가능합니다.</p>')


def form_rec():
    mou = {"e편한세상 에코델타 센터포인트": "A-1", "부산 드파인 센텀": "A-2", "디에트르 더 퍼스트": "A-3"}
    cap = {c[0]: f"B-{i}" for i, c in enumerate(D.EXPO_CAPS, 1)}
    rows = ""
    for i, (day, nm, n, venue) in enumerate(D.GS_REC, 1):
        ev = " · ".join(x for x in (mou.get(nm, ""), cap.get(nm, "")) if x) or "요청 시 제출"
        rows += f'<tr><td class="c">{i}</td><td class="c">{day}</td><td>{_h.escape(nm)}</td><td class="r">{n:,}</td><td>{_h.escape(venue)}</td><td class="c">주관</td><td class="c">{ev}</td></tr>'
    rows += f'<tr><td class="k c" colspan="3">합계 {len(D.GS_REC)}개 단지</td><td class="k r">{D.GS_REC_HH:,}</td><td colspan="3"></td></tr>'
    caps = "".join(f'<figure><img src="{pathlib.Path(os.path.join(HERE, "assets_ins", f)).as_uri()}"><figcaption><b>B-{i} {_h.escape(nm)}</b> · {_h.escape(src)} · {per} · {_h.escape(pl)}</figcaption></figure>'
                   for i, (nm, f, src, per, pl) in enumerate(D.EXPO_CAPS, 1))
    figs = [f for f in caps.split("</figure>") if f]
    cap_html = "".join(f'<div class="pb">{hd("07", "증빙 B · 공식 행사일정 · 카페 공지 캡처")}<div class="cap">' + "</figure>".join(figs[k:k + 2]) + "</figure></div></div>"
                       for k in range(0, len(figs), 2))
    body = (hd("07", "최근 3년간 입주행사 및 지원 실적") + "<h1>최근 3년간 입주행사 및 지원 실적<small>(2023.10.01 ~ 2026.09.30 · 박람회 개최일 기준)</small></h1>" + GUN
            + "<table class=\"rec\"><tr><th>No</th><th>개최일</th><th>단지</th><th>세대</th><th>행사 장소</th><th>구분</th><th>증빙</th></tr>" + rows + "</table>"
            + '<p class="note">증빙 A-1 ~ A-3 = 주관사 협약서 사본(서명란 · 상대방 대표 가림) · B-1 ~ B-7 = 박람회장 공식 행사일정 · 입주자 공식 카페 공지 캡처(다음 쪽) · '
              'NICE 기업신용평가보고서 연혁은 제출서류 10에 전문이 있습니다. 나머지 단지의 원자료(카페 공지 · 계약서)는 협의회 요청 시 제출합니다.</p>'
            + sig(tight=True) + cap_html)
    return html2pdf("07_실적", body)


def form_org():
    teams = "".join(f'<tr><td class="k">{t}</td><td class="c">{n}명</td><td>{_h.escape(w)}</td></tr>' for t, n, w in D.STAFF)
    ext = "".join(f'<tr><td colspan="2">{_h.escape(t)}</td><td>협의회 요청 시 · 협의회 사전 서면 승인 후 전문 업무만(하도급 · 재위탁 아님)</td></tr>' for t, _n in D.STAFF_EXT)
    body = (hd("08", "운영 조직 현황") + "<h1>운영 조직 현황</h1>" + GUN
            + f'<table><tr><th style="width:30%">구분</th><th style="width:12%">인원</th><th>담당 업무</th></tr>'
            + f'<tr><td class="k">대표이사</td><td class="c">1명</td><td>{D.CEO} · 협약 · 계약 · 보상 최종 책임 · 제안 조건 확약</td></tr>'
            + f'<tr><td class="k">주관사업 총괄 본부장</td><td class="c">1명</td><td>{D.MANAGER[0]} · 협의회 단일 창구 · 박람회 · A/S 전 과정 총괄(전담 책임자)</td></tr>'
            + teams + '<tr><td class="k">합계</td><td class="c"><b>14명</b></td><td>임직원 14명 = 정규직 13 + 인턴 1(2026.10 기준) · 4대보험 가입 13명(붙임 명부)</td></tr></table>'
            + "<table><tr><th colspan=\"2\">분야별 외부 전문 협력</th><th>운영 방식</th></tr>" + ext + "</table>"
            + f'<p class="note">본사 = {D.ADDRESS}(본사 · 쇼룸 · 시공팀 · 단지 직접 관리 · 출동) · 전기공사업 등록 제 울산-00821호 · 건축 분야 기술 자문 = 디엔비파트너스건축사사무소(업무협약 2026.10.28 · 사본 = 제출서류 10).<br>'
              '붙임: 4대 사회보험 사업장가입자명부(2026.10.23 발급 · 13명 · 성명 가운데 글자 · 주민등록번호 뒷자리 가림).</p>' + sig())
    return html2pdf("08_운영조직", body)


def form_pledge():
    items = ["협의회가 정한 선정 절차 · 심사 기준 · 결과를 존중하며, 선정 결과에 대하여 어떠한 이의도 제기하지 않겠습니다.",
             "공고 제6조에 따라 접수 메일 외 별도 연락 · 카페 쪽지 · 입주민을 통한 연락을 하지 않으며, 위반 시 자격 박탈을 받아들이겠습니다.",
             "제출 자료가 사실과 다르면 선정 취소(공고 제7조 2)를 받아들이겠습니다.",
             "제안서 작성 및 PT 참가 비용은 당사가 부담하며(공고 제7조 1), 선정되지 않더라도 비용을 청구하지 않겠습니다.",
             "협의회 사전 동의 없이 입주예정자 개인정보를 수집 · 이용 · 제3자 제공하지 않겠습니다(공고 제7조 6).",
             "본 사업이 시행사 · 시공사의 공식 행사와 별개임을 알고(공고 제7조 7), 홍보물에 '공식' 표현 · 브랜드 로고를 쓰지 않겠습니다.",
             "선정되지 않을 경우 이 단지 입주예정자를 대상으로 별도 박람회 · 공동구매를 하지 않겠습니다."]
    body = (hd("09", "이의제기 금지 서약서") + "<h1>이의제기 금지 서약서</h1>" + GUN
            + f'<p>당사는 {D.SITE["name"]} 입주예정자협의회의 입주업무 주관사 선정 공고에 참가함에 있어 다음 사항을 서약합니다.</p><ol>'
            + "".join(f"<li>{_h.escape(x)}</li>" for x in items) + "</ol>"
            + "<p>위 사항을 위반하는 경우 협의회의 어떠한 조치에도 이의를 제기하지 않겠습니다.</p>" + sig())
    return html2pdf("09_이의제기금지서약서", body)


def form_appeal():
    rows = [("① NICE 기업신용평가보고서 전문", "연 1회 정기 평가(재무제표 기준) · 유효기간 안 최근 평가본(2026.06.19 평가 · ~2027.06.18) · 신용 BB- · 현금흐름 A · 대표 외 임직원 생년월일 가림", "24쪽"),
            ("② 전기공사업 등록증", "제 울산-00821호 · 경관조명 진단 · 공용부 조명 개선의 근거", "1쪽"),
            ("③ ISO 9001 · 14001 · 45001 인증서", "글로벌시스템인증원 · 2025.08.12 인증", "6쪽"),
            ("④ 영업배상책임보험 증권(KB)", "시설소유관리자 · 본사 기준 · 행사배상책임보험은 박람회 기간 행사장 기준으로 별도 가입", "1쪽"),
            ("⑤ 서울보증보험 계약보증보험증권 발급 이력", "광고대행 용역 계약보증(입주박람회 이행보증 아님) · 금액 · 상대방 정보 가림 · 이 단지 계약이행 · 하자보증보험은 협약 후 협의회를 피보험자로 발급(금액 · 기산일은 협약 때)", "1쪽"),
            ("⑥ 건축 분야 기술 자문 업무협약서 사본", "디엔비파트너스건축사사무소 · 건축 분야 기술 자문 협력사(업무협약 2026.10.28) · 양측 날인 · 2쪽 을 정보 가림", "2쪽")]
    body = (hd("10", "그 외 어필 서류") + "<h1>그 외 어필 서류</h1>" + GUN
            + "<table><tr><th style='width:30%'>서류</th><th>내용</th><th style='width:9%'>쪽</th></tr>"
            + "".join(f'<tr><td class="k">{a}</td><td>{_h.escape(b)}</td><td class="c">{c}</td></tr>' for a, b, c in rows) + "</table>"
            + '<p class="note">가림 없는 원본은 협의회 요청 시 열람할 수 있습니다.</p>')
    sgi = pathlib.Path(os.path.join(HERE, "assets_ins", "os_sgi_bond_masked.png")).as_uri()
    body += (f'<div class="pb">{hd("10", "⑤ 서울보증보험 계약보증보험증권 발급 이력")}<h1>⑤ 계약보증보험증권 발급 이력<small>(광고대행 용역 · 입주박람회 이행보증 아님)</small></h1>'
             f'<div style="text-align:center"><img src="{sgi}" style="height:200mm;border:.6pt solid #bbb"></div>'
             '<p class="note">서울보증보험 계약보증보험증권(발급 2026.09.07) · 주계약 = 광고대행 용역 · 금액 · 상대방 정보 · 증권번호 일부 가림. '
             '보증 발급 이력의 근거이며, 이 단지 협약 이행 담보는 협약 후 협의회를 피보험자로 새로 발급합니다.</p></div>')
    return html2pdf("10_어필서류_안내", body)


def form_list(toc):
    rows = "".join(f'<tr><td class="c">{no}</td><td class="k">{_h.escape(t)}</td><td>{_h.escape(d)}</td><td class="c">{a} ~ {b}</td></tr>' for no, t, d, a, b in toc)
    body = (hd("00", "제출 서류 목록") + "<h1>제출 서류 목록<small>(공고 제4조 순서 · 모두 자체 양식)</small></h1>" + GUN
            + "<table><tr><th style='width:7%'>No</th><th style='width:26%'>서류</th><th>내용 · 발급일</th><th style='width:13%'>쪽</th></tr>" + rows + "</table>"
            + f'<p class="note">자체 양식(00 · 01 · 06 안내 · 07 · 08 · 09 · 10 안내)의 날인은 사용인감(직인)이며, 사용인감은 04의 사용인감계(법인인감 날인)로 신고했습니다. '
              f'접수 = {D.SUBMIT_TO if hasattr(D, "SUBMIT_TO") else "sonic7307@naver.com"} · 담당 = 주관사업 총괄 본부장 {D.MANAGER[0]} · {D.MANAGER[2]} · {D.EMAIL}</p>' + sig(to=True))
    return html2pdf("00_목록", body)


# ------------------------------------------------------------ 조립
def main():
    assert os.path.exists(STAMP), ("직인 이미지 없음 — assets_ins/jigin_t.png", STAMP)
    parts = [  # (번호, 서류, 내용, [(pdf 또는 키, 쪽 목록 또는 None, 머리글 여부)])
        ("01", "회사소개서", "자체 양식 · 연혁 · 법인 서류 · 재무 · 자격 · 조직 · 실적 · 협약", [("company", None, False)]),
        ("02", "사업자등록증", f"{D.ISSUE['biz']} 발급", [("biz", None, True)]),
        ("03", "법인등기부 등본", f"{D.ISSUE['reg']} 발급 · 대표 주소 가림", [("reg", None, True)]),
        ("04", "인감증명서 · 사용인감계", "법인인감증명서 2026.10.26 발급(주민번호 뒷자리 가림) · 사용인감계(법인인감 실물 날인)", [("ingam", None, True), ("seal", None, True)]),
        ("05", "국세 · 지방세 납부 증명서", f"{D.ISSUE['tax']} 발급(최근 1개월 · 유효 ~2026.11.13) · 휴대번호 가림", [("tax", None, True)]),
        ("06", "최근 3년간 재무제표", "2025 표준재무제표증명 · 2024 재무제표(2023 = 전기 비교 열)", [(form_fin(), None, False), ("fin25", None, True), ("fin24", None, True)]),
        ("07", "최근 3년간 입주행사 및 지원 실적", f"2023.10.01 ~ 2026.09.30 · {len(D.GS_REC)}개 단지 · {D.GS_REC_HH:,}세대 · 협약서 3 · 공식 일정 캡처 7", [(form_rec(), None, False), ("mou3", None, False)]),
        ("08", "운영 조직 현황", "임직원 14명 · 4개 팀 · 외부 전문 협력 · 4대보험 명부(2026.10.23 · 가림)", [(form_org(), None, False), ("roster", None, True)]),
        ("09", "이의제기 금지 서약서", "자유양식 · 직인", [(form_pledge(), None, False)]),
        ("10", "그 외 어필 서류", "NICE 전문 · 전기공사업 · ISO 3종 · 영업배상 · 보증 발급 이력 · 건축 자문 협약서", [(form_appeal(), [1], False), ("nice", None, True), ("elec", None, True), ("iso", None, True), ("kb", None, True), (os.path.join(WORK, "10_어필서류_안내.pdf"), [2], False), ("dnb", None, True)]),
        ("11", "사업 제안서", "제4조 2 8항목 · 평가표 순서", [("proposal", None, False)]),
    ]
    out = fitz.open()
    toc, per, start = [], [], 2  # 00 목록 1쪽 뒤
    for no, title, desc, srcs in parts:
        one = fitz.open()
        for s, pages, mark in srcs:
            if s in EV:
                d, idx = src_pages(s)
            else:
                d = fitz.open(s)
                idx = [i - 1 for i in pages] if pages else list(range(d.page_count))
            runs = []  # 연속 쪽은 한 번에 넣는다(쪽마다 넣으면 글꼴 · 이미지가 중복 복사돼 용량이 몇 배로 커짐)
            for i in idx:
                if runs and runs[-1][1] == i - 1:
                    runs[-1][1] = i
                else:
                    runs.append([i, i])
            for a, b in runs:
                n0 = one.page_count
                one.insert_pdf(d, from_page=a, to_page=b)
                if mark:
                    for k in range(n0, one.page_count):
                        band(one[k], f"제출서류 {no} · {title}")
        one.subset_fonts()  # 머리글 글꼴(맑은 고딕)은 쓴 글자만 남김
        per.append((no, title, one))
        toc.append((no, title, desc, start, start + one.page_count - 1))
        start += one.page_count
    lst = fitz.open(form_list(toc))
    assert lst.page_count == 1, ("목록이 1쪽을 넘음", lst.page_count)
    out.insert_pdf(lst)
    for _no, _t, one in per:  # 한 번에 이어 붙임(서류마다 1회)
        out.insert_pdf(one)
    os.makedirs(os.path.join(OUT, "번호별"), exist_ok=True)
    fn = os.path.join(OUT, f"{NAME}_주관사_제안서_제출서류.pdf")
    out.save(fn, garbage=2, deflate=True)
    lst.save(os.path.join(OUT, "번호별", "00_제출서류_목록.pdf"))
    for no, title, one in per:
        one.save(os.path.join(OUT, "번호별", f"{no}_{title.replace(' · ', '_').replace(' ', '')}.pdf"), garbage=2, deflate=True)
    print(f"제출서류 통합 {out.page_count}쪽 · {os.path.getsize(fn) / 1e6:.1f}MB → {fn}")
    for no, title, desc, a, b in toc:
        print(f"  {no} {title} p.{a} ~ {b}")
    if FINAL:
        todo = [t for t in ("본부장 자료",) if any(t in p.get_text() for p in fitz.open(EV["proposal"]))]
        assert not todo, "제출본에 '확인 필요' 칸이 남아 있습니다(GS_CASES · GS_REJOIN)"


if __name__ == "__main__":
    main()
