# -*- coding: utf-8 -*-
"""철산역 자이(조합) 입주박람회 주관사 입찰 — 공고 04항 필수 제출서류 중 직접 작성하는 문서(A4 세로).

01 입찰참가 신청서 · 04 사용인감계 · 08 최근 3년 주관사 실적 증빙(+별첨 1 NICE 연혁 발췌)
10 사후관리 대책 방안서 · 12 서약서
숫자·문구는 data.py와 제안서(09)에 이미 쓴 약속만 옮긴다(새 약속 없음). 직인은 ../동탄파라곤3차/stamp.py.

사용: python docs_cs.py [NICE_기업신용평가.pdf]
  NICE 원본·직인이 들어간 결과물은 깃에 올리지 않는다(.gitignore: *.pdf, 엣지컴퍼니_*.html).
"""
import html
import os
import pathlib
import subprocess
import sys

import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "요약제안서")]
import data as D  # noqa: E402
from build import find_chrome  # noqa: E402

e = html.escape
PFX = "엣지컴퍼니_철산역자이_"

CSS = r"""
@page{size:A4;margin:13mm 17mm 13mm}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Pretendard','Malgun Gothic','맑은 고딕',sans-serif;color:#1B2433;font-size:10pt;line-height:1.6;
  word-break:keep-all;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.top{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:2.5pt solid #0D1E33;padding-bottom:6pt}
.top .lb{font-size:9pt;font-weight:700;letter-spacing:.18em;color:#9A7B3F}
.top .co{font-size:9pt;color:#5B6676;text-align:right}
h1{font-size:20pt;font-weight:800;color:#0D1E33;margin-top:12pt;letter-spacing:-.01em}
h1.c{text-align:center;font-size:24pt;letter-spacing:.3em;margin-top:22pt}
.case{font-size:10pt;color:#5B6676;margin-top:3pt}
.info{width:100%;border-collapse:collapse;margin-top:12pt;font-size:9.8pt}
.info th{width:17%;background:#F1EDE4;color:#0D1E33;font-weight:700;text-align:left;padding:5pt 9pt;border:.6pt solid #D5CCB9}
.info td{padding:5pt 9pt;border:.6pt solid #D5CCB9}
h2{font-size:12pt;font-weight:800;color:#0D1E33;margin:12pt 0 5pt;padding-left:8pt;border-left:3.5pt solid #C8A86A;line-height:1.3}
.t{width:100%;border-collapse:collapse;font-size:9.6pt}
.t th{background:#0D1E33;color:#fff;font-weight:700;padding:4pt 6pt;border:.6pt solid #0D1E33;text-align:center}
.t td{padding:3.6pt 6pt;border:.6pt solid #C9CED6;text-align:center;vertical-align:middle}
.t td.l{text-align:left}
.t td.r{text-align:right;font-variant-numeric:tabular-nums}
.t tr.sum td{background:#F1EDE4;font-weight:800}
.t td.k{font-weight:700;background:#F6F7F9;text-align:left;width:22%}
.box{border:1pt solid #C8A86A;background:#FBF8F1;border-radius:4pt;padding:8pt 11pt;margin-top:10pt;font-size:10pt}
.box b{color:#0D1E33}
.ok{color:#1F7A4D;font-weight:800}
p.body{margin-top:12pt;font-size:10.5pt;line-height:1.8}
ol.pl{margin:10pt 0 0 0;padding-left:0;list-style:none;font-size:10.5pt;line-height:1.75}
ol.pl li{padding-left:18pt;text-indent:-18pt;margin-top:5pt}
.note{font-size:9pt;color:#5B6676;margin-top:5pt}
.art{margin-top:8pt;break-inside:avoid}
.art h3{font-size:10.8pt;font-weight:800;color:#0D1E33}
.art ol{list-style:none;margin-top:2pt}
.art ol li{padding-left:16pt;text-indent:-16pt;margin-top:2pt}
.sign{margin-top:14pt;text-align:center;break-inside:avoid}
.sign .d{font-size:11pt;letter-spacing:.06em}
.sign .who{margin-top:5pt;font-size:12pt;font-weight:700;display:inline-flex;gap:14pt;align-items:center}
.sign .seal{color:#5B6676;font-size:10pt;font-weight:400;margin-left:6pt}
.to{margin-top:24pt;text-align:center;font-size:12.5pt;font-weight:800;color:#0D1E33}
.seals{display:grid;grid-template-columns:1fr 1fr;gap:18pt;margin-top:14pt}
.seals div{border:.8pt solid #9AA3B0;height:122pt;display:flex;flex-direction:column;align-items:center;justify-content:space-between;padding:8pt}
.seals b{font-size:10.5pt;color:#0D1E33}
.seals span{color:#8A93A0;font-size:9.5pt}
.seals small{font-size:8.5pt;color:#5B6676}
"""


def page(label, title, body, sign=True, center=False):
    yy, mm, dd = D.SIGN_DATE
    sig = f"""<div class="sign"><div class="d">{yy}년 {mm}월 {dd}일</div>
<div class="who"><span>{D.COMPANY} &nbsp; 대표이사 &nbsp; {D.CEO}</span><span class="seal">(인)</span></div></div>
<div class="to">{e(D.CLIENT)} 귀중</div>""" if sign else ""
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{e(title)}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<style>{CSS}</style></head><body>
<div class="top"><div class="lb">{e(label)}</div><div class="co">{D.COMPANY} · 입주박람회 주관사</div></div>
<h1 class="{'c' if center else ''}">{e(title)}</h1>
<div class="case" style="{'text-align:center' if center else ''}">건명 : {e(D.NOTICE)} ({D.NOTICE_DATE} 공고)</div>
{body}
{sig}
</body></html>"""


def company_table(extra=""):
    m = D.MANAGER
    return f"""<table class="info">
<tr><th>상호</th><td>{D.COMPANY}</td><th>대표자</th><td>{D.CEO}</td></tr>
<tr><th>사업자등록번호</th><td>{D.BIZ_NO}</td><th>법인등록번호</th><td>{D.CORP_NO}</td></tr>
<tr><th>본사 소재지</th><td colspan="3">{D.ADDRESS}</td></tr>
<tr><th>설립일</th><td>{D.FOUNDED}</td><th>대표 전화</th><td>{D.TEL}</td></tr>
<tr><th>담당자</th><td colspan="3">{m[1]} {m[0]} · {m[2]} · {D.EMAIL}</td></tr>{extra}
</table>"""


# 공고 04항 필수 제출서류(번호 = 공고 번호)
SUBMIT = [
    ("01", "입찰참가 신청서", "본 서류"),
    ("02", "사업자등록증 사본", "2026.08.04 발급"),
    ("03", "법인 등기부등본(최근 1개월 이내)", "2026.10.02 발행"),
    ("04", "인감증명서 및 사용인감계(최근 1개월 이내)", "인감증명서 · 사용인감계"),
    ("05", "국세 및 지방세 완납증명서", "2026.10.02 발급"),
    ("06", "4대 보험 사업장 가입자 명부(최근 1개월 이내)", "2026.10.02 출력"),
    ("07", "회사소개서(연혁 · 조직도 포함)", ""),
    ("08", "최근 3년 주관사 실적 증빙서류", "별첨 NICE 연혁 발췌"),
    ("09", "입주박람회 주관사 제안서", "109쪽"),
    ("10", "사후관리 대책 방안서", ""),
    ("11", "기업신용평가서", "NICE CLIP · 2026.06.19"),
    ("12", "서류 반환 불가 · 이의제기 금지 서약서", ""),
    ("13", "기타 추가 제안사항", "요약 제안서"),
]


# ============================================================ 01 입찰참가 신청서
def doc01():
    rows = "".join(f'<tr><td>{n}</td><td class="l">{e(t)}</td><td class="l">{e(r)}</td><td>1부</td></tr>' for n, t, r in SUBMIT)
    body = f"""<style>.t td{{padding:2.6pt 6pt}} h1.c{{margin-top:14pt}} .sign{{margin-top:10pt}} .to{{margin-top:14pt}} h2{{margin:9pt 0 4pt}} p.body{{margin-top:9pt;line-height:1.7}}</style>
{company_table()}
<p class="body">당사는 {e(D.CLIENT)}의 「{e(D.NOTICE)}」({D.NOTICE_DATE})에 따라 위 입찰에 참가하고자
공고 04항의 필수 제출서류를 갖추어 신청합니다. 공고의 입찰 참가 자격(03항) · 입찰 참가 제한(05항) · 주의사항(06항)을
모두 확인하였으며, 제출한 서류의 내용이 사실과 다름없음을 확인합니다.</p>
<h2>제출서류 목록 (공고 04항 순서)</h2>
<table class="t"><thead><tr><th style="width:7%">No</th><th>서류</th><th style="width:30%">비고</th><th style="width:8%">부수</th></tr></thead>
<tbody>{rows}</tbody></table>"""
    return page("제출서류 01", "입찰참가 신청서", body, center=True)


# ============================================================ 04 사용인감계
def doc04():
    body = f"""{company_table()}
<p class="body">위 법인은 아래 사용인감을 「{e(D.NOTICE)}」 입찰 참가 및 이에 따른 협약 체결에 관한 일체의 서류에 사용하고자
신고합니다. 이 인감의 사용으로 생기는 모든 책임은 당사가 집니다.</p>
<div class="seals">
<div><b>사용인감</b><span>(인감날인)</span><small>입찰 · 협약 서류에 사용</small></div>
<div><b>법인인감</b><span>(인감날인)</span><small>인감증명서상 등록 인감</small></div>
</div>
<p class="note" style="margin-top:8pt">※ 첨부: 법인 인감증명서 1부(최근 1개월 이내 발급)</p>"""
    return page("제출서류 04", "사용인감계", body, center=True)


# ============================================================ 08 최근 3년 주관사 실적
def doc08():
    recs = D.RECENT3
    rows = "".join(
        f'<tr><td>{i}</td><td>{d}</td><td class="l">{e(nm)}</td><td>{e(reg)}</td><td class="r">{n:,}</td>'
        f'<td style="white-space:nowrap">입주박람회 주관</td><td>별첨 1</td></tr>'
        for i, (d, nm, reg, n) in enumerate(recs, 1))
    total = sum(r[3] for r in recs)
    body = f"""{company_table()}
<h2>1. 최근 3년 1,000세대 이상 아파트 입주박람회 주관 실적</h2>
<p class="note" style="margin:0 0 5pt">기준: 공고일({D.NOTICE_DATE}) 기준 최근 3년(2023.10.06 ~ 2026.10.06) · 1,000세대 이상 아파트 입주박람회 주관 (공고 03항 6호).
주관 시기·세대수는 NICE디앤비 CLIP 기업신용평가보고서(평가완료일 2026.06.19) ‘연혁’(별첨 1)에 기재된 내용과 같습니다.</p>
<table class="t"><thead><tr><th style="width:5%">No</th><th style="width:10%">주관 시기</th><th>단지명</th><th style="width:11%">지역</th>
<th style="width:10%">세대수</th><th style="width:16%">수행 내용</th><th style="width:9%">증빙</th></tr></thead>
<tbody>{rows}
<tr class="sum"><td colspan="4">합계</td><td class="r">{total:,}</td><td colspan="2">{len(recs)}건</td></tr></tbody></table>
<div class="box"><b>참가 자격 대비</b> &nbsp; 요건: 최근 3년간 1,000세대 이상 입주박람회 진행 경험 5회 이상
&nbsp;→&nbsp; 보유: <b>{len(recs)}회 · 합계 {total:,}세대</b> &nbsp; <span class="ok">충족</span></div>
<h2>2. 별첨 증빙</h2>
<ol class="pl" style="font-size:10pt;margin-top:2pt"><li>1. NICE디앤비 CLIP 기업신용평가보고서 ‘연혁’ 발췌 (표지 · 9쪽) — 1매 (보고서 전문은 제출서류 11)</li></ol>
<p class="body" style="font-size:10pt">위 실적은 사실과 다름이 없음을 확인하며, 허위로 확인될 경우 공고 05항에 따른 어떠한 조치도 이의 없이 따르겠습니다.</p>"""
    return page("제출서류 08", "최근 3년 주관사 실적 증빙", body)


# ============================================================ 10 사후관리 대책 방안서
def doc10():
    arts = [
        ("1. 기본 방침", [
            "사후관리는 박람회가 끝난 뒤부터 시작합니다. 주관사는 <b>입주 후 1년</b> 동안 운영 관리를 맡고 결과 보고서를 제출합니다.",
            "공동구매 품목의 무상 A/S는 <b>최소 2년</b>(업체·품목에 따라 기간이 다를 수 있음)이며, 장기 사후관리는 <b>최대 10년</b>까지 이어갑니다.",
            "입주민은 업체를 따로 찾지 않고 <b>주관사 한 곳</b>에 접수합니다. 처리 책임도 주관사가 집니다.",
        ]),
        ("2. 접수 창구와 처리 기준", [
            f"접수 채널 4종: 상담 콜센터({D.TEL}) · 공식카페 신문고 · 카카오채널 · 홈페이지. <b>365일</b> 접수합니다.",
            "VOC 접수 후 <b>24시간 안에 1차 회신</b>하고, 주관사 관리·감독 아래 <b>48시간 안에 하자보수</b>를 원칙으로 합니다. 업체가 응답하지 않으면 주관사가 직접 개입합니다.",
            "보수가 끝나면 주관사가 입주민에게 직접 전화해 확인(해피콜 검수)하고, 모든 접수·처리 내역은 CRM에 기록합니다.",
        ]),
        ("3. 보증과 보상 재원", [
            "<b>이행보증보험 2년 · 최대 10억원</b>: 제안 내용 미이행·업체 도산·검증 미비에 대비하며, 협약 시 증권 실물을 제출합니다. 보험기간 개시일은 박람회·입주 일정에 맞춰 협약으로 정합니다.",
            "<b>하자 예치금 최대 1억원</b>: 참여 업체에게 걷은 돈이 아닌 엣지컴퍼니 자산으로 예치하며, 업체 책임이 확인되면 입주민에게 <b>먼저 보상(선보상)</b>하고 업체와는 나중에 정산합니다. 예치 규모는 단지 규모와 조합 입예협 협의로 정하고, 사용 내역을 공개합니다.",
            "모든 참여업체로부터 <b>하자보수 이행각서</b>와 <b>입주박람회 특약이행각서</b>를 받습니다.",
        ]),
        ("4. 참여업체 관리", [
            "업체가 도산하면 동종업체로 사후관리를 이관하고, 그 A/S 비용은 <b>주관사가 전액 부담</b>합니다.",
            "위반 업체에는 패널티 3단계를 적용합니다: ① 홍보정지 → ② 총액 10% 배상 → ③ 자격박탈 및 전 계약을 대체업체로 이관. 하자보수 지연 시에는 하자지연 패널티를 부과합니다.",
            "업체는 4단계 공개 심사로 고르며, 시공 품목은 인근 지역업체를 우선 선정해 48시간 처리가 가능한 거리를 확보합니다.",
        ]),
        ("5. 계약 보호 · 취소 · 환불", [
            f"계약금은 총액의 <b>{D.DEPOSIT_MAX}% 이하</b>, 잔금은 시공·설치 확인 후 납부합니다. 카드 결제도 현금가와 같습니다.",
            "품목별 취소 기한 안에는 100% 해약할 수 있습니다: 청소·줄눈·탄성코트·유리막코팅·선반잡물·음식물처리기·인덕션·벽걸이TV·LED조명은 <b>시공일 7일 전</b>, 미세방충망·인테리어·단열필름·시스템에어컨·포장이사는 <b>시공일 15일 전</b>, 맞춤 제작 품목은 출고 지시 전 업체 협의.",
            "환불은 <b>3영업일 이내</b>에 처리하고, 업체가 미루면 주관사가 먼저 보상합니다.",
        ]),
        ("6. 철산역 자이 맞춤 운영", [
            "1단지(101~110동) · 2단지(201~207동) · 3단지(301~302동)로 나뉜 단지 특성에 맞춰 단지별 설치 예약 · 하역 위치 · 엘리베이터 사용 시간을 나눠 운영합니다.",
            "조합원 유상옵션 · 기본 제공 품목 목록을 받아 공동구매 품목과 대조하고, 이미 들어간 품목은 권하지 않습니다.",
            "가구·가전 포장재와 대형폐기물은 납품업체가 직접 회수하도록 협약에 넣습니다.",
        ]),
        ("7. 보고와 기록", [
            "입주까지 분기마다 진행 상황을 조합 입예협에 보고하고, 입주 후 1년 운영 관리가 끝나면 결과 보고서를 제출합니다.",
            "클레임 접수·처리 현황은 CRM으로 관리해 분기 보고에 담고, 하자 예치금 사용 내역은 공개합니다.",
        ]),
    ]
    out = []
    for h, items in arts:
        lis = "".join(f"<li>{'①②③④⑤'[i]} {x}</li>" for i, x in enumerate(items))
        out.append(f'<div class="art"><h3>{h}</h3><ol>{lis}</ol></div>')
    flow = """<table class="t" style="margin-top:6pt"><thead><tr><th>접수</th><th>1차 회신</th><th>처리</th><th>검수</th><th>정산·기록</th></tr></thead>
<tbody><tr><td>콜센터 · 신문고 · 카카오 · 홈페이지<br>365일</td><td>24시간 이내</td><td>48시간 이내 보수<br>(업체 미응답 시 주관사 개입)</td>
<td>주관사 해피콜</td><td>선보상 후 업체 정산<br>CRM 기록</td></tr></tbody></table>"""
    summary = """<div class="box"><b>핵심 요약</b> &nbsp; 주관사 1창구 365일 접수 · 24시간 회신 · 48시간 처리 · 선보상 후 정산 ·
이행보증보험 2년 최대 10억 · 하자 예치금 최대 1억 · 무상 A/S 최소 2년(업체·품목별 상이) · 장기 관리 최대 10년</div>"""
    return page("제출서류 10", "사후관리 대책 방안서", summary + flow + "".join(out))


# ============================================================ 12 서약서
def doc12():
    body = f"""{company_table()}
<p class="body">당사는 {e(D.CLIENT)}의 「{e(D.NOTICE)}」({D.NOTICE_DATE}) 입찰에 참가하면서 다음 사항을 서약합니다.</p>
<ol class="pl">
<li>1. 본 입찰에 제출한 서류는 반환되지 않음에 동의합니다.</li>
<li>2. 제안서 평가 및 선정 결과를 포함한 입찰 결과에 대하여 일체의 이의를 제기하지 않겠습니다.</li>
<li>3. 제출한 서류에 허위의 사실이 있는 경우 공고 05항·06항에 따른 입주예정자협의회의 조치를 이의 없이 따르겠습니다.</li>
</ol>"""
    return page("제출서류 12", "서약서", body, center=True)


# ============================================================ 08 별첨 1 — NICE 연혁 발췌(동탄 annex.py와 같은 방식)
FONTS = os.path.join(HERE, "..", "통합제안서", "fonts")
NAVY, GOLD, GRAY, LINE = (0.051, 0.118, 0.2), (0.78, 0.66, 0.42), (0.36, 0.4, 0.46), (0.79, 0.81, 0.84)
CLIP_TITLE = fitz.Rect(0, 0, 595, 76)
CLIP_HIST = fitz.Rect(36, 321, 560, 511)
ROWS_RECENT = (398, 506)     # 연혁 표 중 최근 3년 주관 실적 6행(2023/11 ~ 2026/07) — 한 행 18pt
CLIP_FOOT = fitz.Rect(36, 800, 560, 828)


def annex08(nice_path, out_path):
    nice = fitz.open(nice_path)
    out = fitz.open()
    pg = out.new_page(width=595.28, height=841.89)
    F = {"r": fitz.Font(fontfile=os.path.join(FONTS, "Pretendard-Regular.ttf")),
         "b": fitz.Font(fontfile=os.path.join(FONTS, "Pretendard-Bold.ttf"))}

    def text(x, y, s, size=9.5, w="r", color=NAVY, align="l"):
        f = F[w]
        if align != "l":
            tl = f.text_length(s, fontsize=size)
            x = x - tl / 2 if align == "c" else x - tl
        tw = fitz.TextWriter(pg.rect)
        tw.append((x, y), s, font=f, fontsize=size)
        tw.write_text(pg, color=color)

    L, R = 48, 547
    pg.draw_rect(fitz.Rect(L, 40, L + 46, 56), color=GOLD, width=1)
    text(L + 23, 51.5, "별첨 1", 8.5, "b", GOLD, "c")
    text(R, 51.5, "제출서류 08 최근 3년 주관사 실적 증빙", 8.5, "r", GRAY, "r")
    pg.draw_line((L, 64), (R, 64), color=NAVY, width=2)
    text(L, 92, "NICE디앤비 기업신용평가보고서 ‘연혁’ 발췌", 17, "b")
    text(L, 110, f"건명 : {D.NOTICE} ({D.NOTICE_DATE} 공고)", 8.8, "r", GRAY)
    top = 126
    cover = fitz.Rect(L, top, L + 168, top + 168 * 842 / 595)
    pg.show_pdf_page(cover, nice, 0)
    pg.draw_rect(cover, color=LINE, width=0.6)
    info = [("보고서명", "CLIP 기업신용평가보고서"), ("발행 기관", "NICE디앤비 (dun & bradstreet)"),
            ("평가 대상", f"{D.COMPANY} ({D.BIZ_NO})"), ("관리번호", "11125949-202605-001"),
            ("평가완료일", "2026.06.19"), ("발췌 범위", "9쪽 ‘04 영업 현황(기업개요)’ 중 ‘연혁’"),
            ("원본 분량", f"전 {len(nice)}쪽 (전문은 제출서류 11)")]
    x0, x1, xk, rh = L + 186, R, L + 186 + 70, 24
    for i, (k, v) in enumerate(info):
        y = top + i * rh
        pg.draw_rect(fitz.Rect(x0, y, xk, y + rh), color=LINE, fill=(0.945, 0.929, 0.894), width=0.6)
        pg.draw_rect(fitz.Rect(xk, y, x1, y + rh), color=LINE, width=0.6)
        text(x0 + 8, y + 15.5, k, 8.8, "b")
        text(xk + 8, y + 15.5, v, 8.8, "r", (0.1, 0.14, 0.2))
    y = top + len(info) * rh + 18
    text(x0, y, "아래 연혁 중 금색 테두리 6행이 공고일 기준", 8.8, "r", GRAY)
    text(x0, y + 13, "최근 3년 1,000세대 이상 입주박람회 주관 실적입니다.", 8.8, "r", GRAY)
    s = (R - L) / 595
    y = cover.y1 + 22
    text(L, y, "■ 원본 9쪽 발췌", 9, "b")
    box_top = y + 8
    y = box_top + 4

    def put(clip, y):
        r = fitz.Rect(L + clip.x0 * s, y, L + clip.x1 * s, y + clip.height * s)
        pg.show_pdf_page(r, nice, 8, clip=clip)
        return r

    put(CLIP_TITLE, y)
    y += CLIP_TITLE.height * s + 2
    text((L + R) / 2, y + 9, "··· (중략: 기업개요) ···", 8, "r", GRAY, "c")
    y += 16
    hist = put(CLIP_HIST, y)
    hy0 = hist.y0 + (ROWS_RECENT[0] - CLIP_HIST.y0) * s
    hy1 = hist.y0 + (ROWS_RECENT[1] - CLIP_HIST.y0) * s
    pg.draw_rect(fitz.Rect(hist.x0 - 3, hy0 - 1, hist.x1 + 3, hy1 + 1), color=GOLD, width=1.6)
    y = hist.y1 + 4
    text((L + R) / 2, y + 9, "··· (이하 생략: 관계회사) ···", 8, "r", GRAY, "c")
    y += 16
    foot = put(CLIP_FOOT, y)
    pg.draw_rect(fitz.Rect(L, box_top, R, foot.y1 + 6), color=LINE, width=0.6)
    y = foot.y1 + 40
    text((L + R) / 2, y, "위 발췌 내용은 원본과 같음을 확인합니다.", 10, "r", (0.1, 0.14, 0.2), "c")
    yy, mm, dd = D.SIGN_DATE
    text((L + R) / 2, y + 26, f"{yy}년 {mm}월 {dd}일", 10, "r", (0.1, 0.14, 0.2), "c")
    who = f"{D.COMPANY}   대표이사   {D.CEO}"
    text((L + R) / 2 - 14, y + 52, who, 11, "b", NAVY, "c")
    sx = (L + R) / 2 - 14 + F["b"].text_length(who, fontsize=11) / 2 + 8
    text(sx, y + 52, "(인)", 10, "r", GRAY)
    out.set_metadata({"title": "별첨 1 NICE 기업신용평가보고서 연혁 발췌", "author": D.COMPANY})
    out.save(out_path, garbage=4, deflate=True)


def to_pdf(html_path, pdf_path):
    exe = find_chrome()
    subprocess.run([exe, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=8000", f"--print-to-pdf={pdf_path}", pathlib.Path(html_path).as_uri()],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


DOCS = [("01_입찰참가신청서", doc01), ("04_사용인감계", doc04), ("08_최근3년_주관사실적", doc08),
        ("10_사후관리_대책방안서", doc10), ("12_서약서", doc12)]


def main():
    for name, fn in DOCS:
        h = os.path.join(HERE, PFX + name + ".html")
        with open(h, "w", encoding="utf-8") as f:
            f.write(fn())
        to_pdf(h, h[:-5] + ".pdf")
        print("saved", h[:-5] + ".pdf", len(fitz.open(h[:-5] + ".pdf")), "p")
    if len(sys.argv) > 1:
        ann = os.path.join(HERE, PFX + "08_별첨1_NICE연혁발췌.pdf")
        annex08(sys.argv[1], ann)
        both = fitz.open(os.path.join(HERE, PFX + "08_최근3년_주관사실적.pdf"))
        both.insert_pdf(fitz.open(ann))
        both.set_metadata({"title": "08 최근 3년 주관사 실적 증빙 (별첨 1 포함)", "author": D.COMPANY})
        both.save(os.path.join(HERE, PFX + "08_최근3년_주관사실적_별첨포함.pdf"), garbage=4, deflate=True)
        print("saved 08 + 별첨", len(both), "p")


if __name__ == "__main__":
    main()
