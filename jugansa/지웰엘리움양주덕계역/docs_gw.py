# -*- coding: utf-8 -*-
"""지웰 엘리움 양주 덕계역 입주박람회 주관사 입찰 — 공고 5항 제출서류 중 직접 작성·조립하는 문서(A4 세로).

  1 입찰참가신청서 [별지 제1호] + 제출서류 목록       5 사용인감계(인감증명서와 함께)
  8 최근 3년간 주관사 실적 증빙 — 실적표 · [별지 제2호] 실적증명서 · 별첨 NICE 연혁 발췌 · 실적 확약서(카페 공지 붙임)
  11 서약서 및 별지 서식 — [별지 제3호] 청렴계약이행서약서 · [제4호] 비밀유지 서약서 · [제5호] 분쟁발생 시 책임배상 이행각서 · [제6호] 입찰결과 승복 서약서
  2 · 4 · 5 · 6 · 7 증빙 사본은 원본 스캔을 묶기만 한다(사업자등록증 · 등기부 · 인감증명서 · 납세증명서 · 4대보험 명부).
별지는 공고문 양식 문구를 그대로 옮기고 빈칸만 채운다. 사용인감계의 법인인감 칸은 실물 날인 후 스캔(디지털로 만들지 않음).

사용: python docs_gw.py <NICE.pdf> <직인.png> [--final]
  결과 PDF·HTML은 깃 제외(.gitignore).
"""
import html
import json
import os
import pathlib
import subprocess
import sys

import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "요약제안서"), os.path.join(HERE, "..", "동탄파라곤3차")]
import data as D  # noqa: E402
from build import find_chrome  # noqa: E402

e = html.escape
PFX = "엣지컴퍼니_지웰엘리움양주덕계역_"
SITE = "지웰 엘리움 양주 덕계역"
TODOS = []


def todo(x):
    TODOS.append(x)
    return f'<mark class="todo">{e(x)}</mark>'


_priv = os.path.join(HERE, "org_private.json")
PRIV = json.load(open(_priv, encoding="utf-8")) if os.path.exists(_priv) else {}
CEO_BIRTH = D.CEO_BIRTH or PRIV.get("ceo_birth")

CSS = r"""
@page{size:A4;margin:14mm 17mm 13mm}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Pretendard','Malgun Gothic','맑은 고딕',sans-serif;color:#1B2433;font-size:10pt;line-height:1.6;
  word-break:keep-all;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.pg{page-break-after:always}.pg:last-child{page-break-after:auto}
mark.todo{background:#FFE066;color:#0D1E33;font-weight:700;padding:0 4pt}
.top{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:2.5pt solid #0D1E33;padding-bottom:6pt}
.top .lb{font-size:9pt;font-weight:700;letter-spacing:.18em;color:#9A7B3F}
.top .co{font-size:9pt;color:#5B6676;text-align:right}
h1{font-size:20pt;font-weight:800;color:#0D1E33;margin-top:12pt}
h1.c{text-align:center;font-size:22pt;letter-spacing:.25em;margin-top:18pt}
.case{font-size:10pt;color:#5B6676;margin-top:3pt}
.info{width:100%;border-collapse:collapse;margin-top:12pt;font-size:9.8pt}
.info th{width:17%;background:#F1EDE4;color:#0D1E33;font-weight:700;text-align:left;padding:5pt 9pt;border:.6pt solid #D5CCB9}
.info td{padding:5pt 9pt;border:.6pt solid #D5CCB9}
h2{font-size:12pt;font-weight:800;color:#0D1E33;margin:12pt 0 5pt;padding-left:8pt;border-left:3.5pt solid #C8A86A;line-height:1.3}
.t{width:100%;border-collapse:collapse;font-size:9.5pt}
.t th{background:#0D1E33;color:#fff;font-weight:700;padding:4pt 6pt;border:.6pt solid #0D1E33;text-align:center}
.t td{padding:3.4pt 6pt;border:.6pt solid #C9CED6;text-align:center;vertical-align:middle}
.t td.l{text-align:left}.t td.r{text-align:right;font-variant-numeric:tabular-nums}
.t tr.sum td{background:#F1EDE4;font-weight:800}
.t td.k{font-weight:700;background:#F6F7F9;text-align:left;width:22%}
.box{border:1pt solid #C8A86A;background:#FBF8F1;border-radius:4pt;padding:8pt 11pt;margin-top:10pt;font-size:10pt}
.box b{color:#0D1E33}
.ok{color:#1F7A4D;font-weight:800}
p.body{margin-top:12pt;font-size:10.5pt;line-height:1.8}
.note{font-size:9pt;color:#5B6676;margin-top:5pt}
.art{margin-top:7pt;break-inside:avoid}
.art h3{font-size:10.6pt;font-weight:800;color:#0D1E33}
.art p{margin-top:2pt}
.art ol{list-style:none;margin-top:2pt}
.art ol li{padding-left:16pt;text-indent:-16pt;margin-top:2pt}
.sign{margin-top:14pt;text-align:center;break-inside:avoid}
.sign .d{font-size:11pt;letter-spacing:.06em}
.sign .who{margin-top:5pt;font-size:12pt;font-weight:700}
.sign .seal{color:#5B6676;font-size:10pt;font-weight:400;margin-left:30pt}
.to{margin-top:20pt;text-align:center;font-size:12.5pt;font-weight:800;color:#0D1E33}
.seals{display:grid;grid-template-columns:1fr 1fr;gap:18pt;margin-top:14pt}
.seals div{border:.8pt solid #9AA3B0;height:122pt;display:flex;flex-direction:column;align-items:center;justify-content:space-between;padding:8pt}
.seals b{font-size:10.5pt;color:#0D1E33}
.seals span.mk{color:#ECEEF1;font-size:5pt}
.seals small{font-size:8.5pt;color:#5B6676}
/* 공고 별지 양식 — 흑백 서식 */
.form{color:#111;font-size:11pt;line-height:1.85}
.form .no{font-size:10pt;color:#333}
.form h1{text-align:center;font-size:21pt;letter-spacing:.3em;color:#111;margin:14pt 0 16pt}
.form .ft{width:100%;border-collapse:collapse;font-size:10.5pt}
.form .ft th,.form .ft td{border:.8pt solid #333;padding:7pt 9pt;vertical-align:middle}
.form .ft th{background:#F2F2F2;font-weight:700;text-align:center;white-space:nowrap}
.form .ft td.v{min-width:120pt}
.form p.tx{margin-top:14pt;text-indent:10pt;text-align:justify}
.form ol{list-style:none;margin-top:8pt}
.form ol li{padding-left:16pt;text-indent:-16pt;margin-top:6pt;text-align:justify}
.form .dt{text-align:center;margin-top:26pt;font-size:12pt;letter-spacing:.15em}
.form .sg{margin:22pt 0 0 50%;font-size:11.5pt;line-height:3.0}
.form .sg b{font-weight:700}
.form .to2{margin-top:70pt;text-align:center;font-size:13pt;font-weight:800;line-height:1.6}
.form .agent{font-size:10.2pt;line-height:1.9}
.form .agent .ln{margin-left:150pt}
.form .chk{display:flex;gap:16pt;align-items:center;margin-top:16pt}
.form .chk table.stamp{border-collapse:collapse;border:1.2pt solid #333}
.form .chk table.stamp td{border:.8pt solid #333;text-align:center;font-size:10pt;padding:0 8pt;height:36pt}
.form .chk table.stamp td.sl{width:72pt;height:72pt;color:#777}
.form .chk table.stamp span.mk{color:#fff;font-size:4pt}
"""

HEAD = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{t}</title>'
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">'
        '<style>{css}</style></head><body>')


def doc(title, sections):
    return HEAD.format(t=e(title), css=CSS) + "".join(f'<section class="pg">{s}</section>' for s in sections) + "</body></html>"


def ymd():
    yy, mm, dd = D.SIGN_DATE
    return yy, mm, dd


def head(label, title, center=False):
    return (f'<div class="top"><div class="lb">{e(label)}</div><div class="co">{D.COMPANY} · 입주박람회 주관사</div></div>'
            f'<h1 class="{"c" if center else ""}">{e(title)}</h1>'
            f'<div class="case" style="{"text-align:center" if center else ""}">건명 : {e(D.NOTICE)} ({D.NOTICE_DATE} 공고)</div>')


def sign():
    yy, mm, dd = ymd()
    return (f'<div class="sign"><div class="d">{yy}년 {mm}월 {dd}일</div>'
            f'<div class="who">{D.COMPANY} &nbsp; 대표이사 &nbsp; {D.CEO}<span class="seal">(인)</span></div></div>'
            f'<div class="to">{e(D.CLIENT)} 귀중</div>')


def company_table(extra=""):
    m = D.MANAGER
    return f"""<table class="info">
<tr><th>상호</th><td>{D.COMPANY}</td><th>대표자</th><td>{D.CEO}</td></tr>
<tr><th>사업자등록번호</th><td>{D.BIZ_NO}</td><th>법인등록번호</th><td>{D.CORP_NO}</td></tr>
<tr><th>본사 소재지</th><td colspan="3">{D.ADDRESS}</td></tr>
<tr><th>설립일</th><td>{D.FOUNDED}</td><th>대표 전화</th><td>{D.TEL}</td></tr>
<tr><th>담당자</th><td colspan="3">{m[1]} {m[0]} · {m[2]} · {D.EMAIL}</td></tr>{extra}
</table>"""


def form_tail(addr=False):
    """별지 공통 꼬리: 날짜 → 주관사·대표자 (인) → 쪽 아래 '…입주예정자협의회 귀중'. 공고 원본 양식(p8~p10) 순서."""
    yy, mm, dd = ymd()
    a = f"주 &nbsp;소 : {D.ADDRESS}<br>" if addr else ""
    return (f'<div class="dt">{yy}년 &nbsp; {mm}월 &nbsp; {dd}일</div>'
            f'<div class="sg">{a}주관사 : <b>{D.COMPANY}</b><br>대표자 : <b>대표이사 {D.CEO}</b><span style="margin-left:48pt">(인)</span></div>'
            f'<div class="to2">{SITE}<br>입주예정자협의회 귀중</div>')


def birth():
    return e(CEO_BIRTH) if CEO_BIRTH else todo("대표자 생년월일 — 본부장 확인")


# ------------------------------------------------------------------ 발급일
def issued(key, label):
    v = D.ISSUE.get(key)
    return f"{v} 발급" if v else todo(f"{label} 재발급일(공고일 이후)")


EV = "/tmp/claude-0/-home-user-edge-company/a96d9eb6-5244-5d3f-9f1b-6f379ac2a82c/scratchpad/evidence"


def form_tail2(no=""):
    """지웰 별지 꼬리(공고 원본): 회사명 · 주소 · 대표자 (직인 또는 인감) → 날짜 → 귀하."""
    yy, mm, dd = ymd()
    return (f'<table class="ft" style="margin-top:22pt"><tr><th>회 사 명</th><td>{D.COMPANY}</td></tr>'
            f'<tr><th>주 &nbsp; &nbsp; 소</th><td>{D.ADDRESS}</td></tr>'
            f'<tr><th>대 표 자</th><td>대표이사 {D.CEO}<span style="margin-left:60pt;color:#555">(인)</span>'
            f'</td></tr></table>'
            f'<div class="dt">{yy}년 &nbsp; {mm}월 &nbsp; {dd}일</div>'
            f'<div class="to2" style="margin-top:34pt">{SITE} 입주예정자협의회 귀하</div>')


GW_RECS = [  # 공고일(2026.10.10) 기준 최근 3년 1,000세대 이상 주관 — (주관 시기, 단지, 지역, 세대수, 근거)
    ("2023.11", "레이카운티", "부산", 4470, "NICE 연혁"),
    ("2024.06", "두산위브더제니스 센트럴사하", "부산", 1643, "NICE 연혁"),
    ("2024.11 ~ 2025.12", "에코델타 대성베르힐", "부산 에코델타시티", 1120, "입예협 카페 공지"),
    ("2024.12", "양정자이더샵SK VIEW 1·2단지", "부산", 2272, "NICE 연혁"),
    ("2025.07", "춘천 학곡지구 중해마루힐 포레스트", "강원 춘천", 1114, "NICE 연혁"),
    ("2026.01", "두산위브더제니스 오션시티", "부산", 2813, "NICE 연혁"),
    ("2026.07", "창원 센트럴 아이파크", "경남 창원", 1540, "NICE 연혁"),
]
VENUE = {  # 단지명 → (행사일정, 행사장소) — 본부장 확인 10-13
    "레이카운티": ("1차 2023.08.12 ~ 13\n2차 2023.10.21 ~ 22", "벡스코(BEXCO)"),
    "두산위브더제니스 센트럴사하": ("1차 2024.06.08 ~ 09\n2차 2024.08.10 ~ 11", "벡스코(BEXCO)"),
    "에코델타 대성베르힐": ("2025.11.28 ~ 30", "벡스코(BEXCO)"),
    "양정자이더샵SK VIEW 1·2단지": ("2025.01.11 ~ 12", "벡스코(BEXCO)"),
    "춘천 학곡지구 중해마루힐 포레스트": ("2025.08.09 ~ 10", "춘천 베어스호텔"),
    "두산위브더제니스 오션시티": ("2025.12.06 ~ 07", "벡스코(BEXCO)"),
    "창원 센트럴 아이파크": ("2026.07.03 ~ 05", "창원컨벤션센터(CECO)"),
}


def submit_rows():
    n09 = len(fitz.open(os.path.join(HERE, PFX + "09_입주박람회_제안서.pdf")))
    return [
        ("1", "입찰참가신청서 (별지 서식)", "[별지 제1호]", "1부"),
        ("2", "사업자등록증 사본", issued("biz", "사업자등록증"), "1부"),
        ("3", "법인사업자 통장 사본", "법인 명의 · 우리은행 기업자유예금", "1부"),
        ("4", "법인등기부등본 (최근 1개월 이내 발급)", issued("reg", "등기부등본"), "1부"),
        ("5", "인감증명서 및 사용인감계 (최근 1개월 이내 발급)", f"인감증명서 {D.INGAM_DATE} 발급 · 사용인감계", "1부"),
        ("6", "국세 및 지방세 완납증명서 (유효기한 내)", f"국세 {issued('tax', '국세')} · 지방세 {issued('ltax', '지방세')}", "각 1부"),
        ("7", "4대 보험 가입자 명부 및 4대 보험 완납증명서 (유효기한 내)", f"가입자 명부 {D.ROSTER_DATE} 발급 · 4대 사회보험료 완납증명서 {D.WANNAP_DATE} 발급", "1부"),
        ("8", "최근 3년간 주관사 실적 증빙서류", f"[별지 제2호] 실적증명서 {len(GW_RECS)}건 · NICE 연혁 발췌 · 실적 확약서", "1부"),
        ("9", "입주박람회 제안서", f"{n09}쪽 · A/S 및 사후관리 · 품목별 취소·환불 규정 · 컴플레인 예시 및 해결 우수 사례 포함", "1부"),
        ("10", "제안 요약본 (5페이지 이내)", "5쪽", "1부"),
        ("11", "서약서 및 별지 서식", "[별지 제3 ~ 6호] 청렴계약이행 · 비밀유지 · 분쟁 책임배상 이행각서 · 입찰결과 승복 + 서류 반환 불가 · 결과 이의 제기 불가 서약서", "1부"),
    ]


# ================================================================== 1 입찰참가신청서 [별지 제1호]
def doc01():
    m = D.MANAGER
    yy, mm, dd = ymd()
    f1 = f"""<div class="form"><div class="no">[별지 제1호]</div><h1>입찰 참가 신청서</h1>
<p class="tx" style="margin-top:0">당사는 「{SITE} 입주예정자협의회」가 공고한 {SITE} 입주예정자협의회 입주박람회 주관사 선정 입찰에 참가하고자 입찰 공고사항을 모두 수락하며, 주관사로 선정될 경우 관련 조건 및 지시사항을 성실히 이행할 것을 확약하며 입찰참가신청서를 제출합니다.</p>
<h3 style="margin-top:18pt;font-size:11.5pt">■ 신청업체 정보</h3>
<table class="ft"><tr><th>회 사 명</th><td>{D.COMPANY}</td></tr><tr><th>대 표 자 명</th><td>대표이사 {D.CEO}</td></tr>
<tr><th>사업자등록번호</th><td>{D.BIZ_NO}</td></tr><tr><th>법인등록번호</th><td>{D.CORP_NO}</td></tr><tr><th>주 &nbsp; &nbsp; &nbsp; &nbsp; 소</th><td>{D.ADDRESS}</td></tr></table>
<h3 style="margin-top:14pt;font-size:11.5pt">■ 담당(책임)자 정보</h3>
<table class="ft"><tr><th>성 &nbsp; &nbsp; 명</th><td>{m[0]}</td></tr><tr><th>휴 대 전 화</th><td>{m[2]}</td></tr><tr><th>직 &nbsp; &nbsp; 위</th><td>{m[1]}</td></tr></table>
<div class="dt">{yy}년 &nbsp; {mm}월 &nbsp; {dd}일</div>
<div class="sg" style="margin-top:12pt">상 &nbsp;호 : <b>{D.COMPANY}</b><br>대표자 : <b>대표이사 {D.CEO}</b><span style="margin-left:48pt">(인)</span></div>
<div class="to2" style="margin-top:28pt">{SITE} 입주예정자협의회 귀하</div></div>"""
    rows = "".join(f'<tr><td>{n}</td><td class="l">{e(t)}</td><td class="l">{r}</td><td>{q}</td></tr>' for n, t, r, q in submit_rows())
    f2 = f"""{head("입찰참가신청서 붙임", "제출서류 목록")}
<h2>공고 5항 제출 서류 (공고 순서)</h2>
<table class="t"><thead><tr><th style="width:6%">No</th><th>서류</th><th style="width:40%">비고</th><th style="width:7%">부수</th></tr></thead><tbody>{rows}</tbody></table>
<p class="note">※ 최근 1개월 이내 발급(4 · 5) · 유효기한 내(6 · 7) 기준. 입찰 자격 관련 사항은 위 객관적 증빙서류로 확인하실 수 있습니다(공고 3항).</p>
<p class="note">※ 메일 제출: {D.SUBMIT_TO} · 압축파일 및 메일 제목 「엣지컴퍼니_{SITE}」 · 마감 {D.DEADLINE}</p>"""
    return doc("1 입찰참가신청서", [f1, f2])


# ================================================================== 5 사용인감계
def doc05():
    body = f"""{head("제출서류 5", "사용인감계", True)}{company_table()}
<p class="body">위 법인은 아래 사용인감을 「{e(D.NOTICE)}」 입찰 참가 및 이에 따른 협약 체결에 관한 일체의 서류에 사용하고자
신고합니다. 이 인감의 사용으로 생기는 모든 책임은 당사가 집니다.</p>
<div class="seals">
<div><b>사용인감</b><span class="mk">(인감날인)</span><small>입찰 · 협약 서류에 사용</small></div>
<div><b>법인인감</b><span></span><small>인감증명서상 등록 인감</small></div>
</div>
<p class="note" style="margin-top:8pt">※ 첨부: 법인 인감증명서 1부({D.INGAM_DATE} 발급)</p>{sign()}"""
    return doc("5 사용인감계", [body])


# ================================================================== 8 실적 — 실적표 + [별지 제2호]
def doc08():
    rows = "".join(f'<tr><td>{i}</td><td style="white-space:nowrap">{d}</td><td class="l">{e(nm)}</td><td>{e(reg)}</td><td class="r">{n:,}</td><td class="l">{e(ev)}</td></tr>'
                   for i, (d, nm, reg, n, ev) in enumerate(GW_RECS, 1))
    tot = sum(r[3] for r in GW_RECS)
    p1 = f"""{head("제출서류 8", "최근 3년간 주관사 실적 증빙서류")}
<p class="note" style="margin-top:8pt">제출: {D.COMPANY} (사업자등록번호 {D.BIZ_NO} · 대표이사 {D.CEO})</p>
<h2>1. 최근 3년 1,000세대 이상 입주박람회 주관 실적</h2>
<p class="note" style="margin:0 0 5pt">기준: 공고일({D.NOTICE_DATE}) 기준 최근 3년(2023.10.10 ~ 2026.10.10) · 1,000세대 이상 공동주택 입주박람회 주관.
시기·세대수는 NICE디앤비 CLIP 기업신용평가보고서(평가 {D.NICE_DATE}) ‘연혁’과 해당 단지 입주예정자협의회 공식 카페의 주관사 명의 공지 기준입니다.</p>
<table class="t"><thead><tr><th style="width:5%">No</th><th style="width:15%">연혁 기재 시기</th><th>단지명</th><th style="width:13%">지역</th><th style="width:10%">세대수</th><th style="width:18%">근거</th></tr></thead>
<tbody>{rows}<tr class="sum"><td colspan="4">합계 {len(GW_RECS)}개 단지</td><td class="r">{tot:,}</td><td></td></tr></tbody></table>
<p class="note">※ 연혁 기재 시기는 NICE 보고서·카페 공지 기준이며, 실제 박람회 일정·장소는 [별지 제2호]에 단지별로 적었습니다(레이카운티 · 센트럴사하는 1·2차 2회 개최).</p>
<div class="box"><b>공고 3항 수임 실적</b> &nbsp; 요건: 입찰공고일 이전 1,000세대 이상 단지 5개 이상 수임 &nbsp;→&nbsp; 최근 3년만 <b>{len(GW_RECS)}개 단지 · {tot:,}세대</b> &nbsp; <span class="ok">충족</span><br>
3년 이전을 포함한 1,000세대 이상 주관 실적은 <b>9개 단지 · 18,261세대</b>입니다(붙임 실적 확약서).</div>
<h2>2. 붙임</h2>
<ol style="list-style:none;font-size:10pt;line-height:1.8">
<li>① [별지 제2호] 최근 3년간 실적증명서</li>
<li>② NICE디앤비 CLIP 기업신용평가보고서 ‘연혁’ 발췌 — 1매</li>
<li>③ 대표이사 실적 확약서 — 입예협 공식 카페 주관사 공지 캡처 2매(입주민 닉네임 동·호수 가림)</li>
<li>입예협 요청 시 계약서 · 실적 확인서 · 정산 자료를 지체 없이 추가 제출합니다.</li></ol>"""
    vr = ""
    for d, nm, reg, n, ev in GW_RECS:
        sch, plc = VENUE.get(nm, (None, None))
        vr += (f'<tr><td>{e(nm)}</td><td style="text-align:right">{n:,}</td>'
               f'<td style="white-space:nowrap">{e(sch).replace(chr(10), "<br>") if sch else todo(f"{nm} 행사일정")}</td><td>{e(plc) if plc else todo(f"{nm} 행사장소")}</td></tr>')
    yy, mm, dd = ymd()
    p2 = f"""<div class="form"><div class="no">[별지 제2호]</div><h1 style="letter-spacing:.15em">최근 3년간 실적증명서</h1>
<table class="ft" style="font-size:10pt"><tr><th>단지명</th><th>세대수</th><th>행사일정</th><th>행사장소</th></tr>{vr}</table>
{form_tail2()}</div>"""
    return doc("8 최근 3년간 주관사 실적 증빙서류", [p1, p2])


# ================================================================== 11 서약서 및 별지 서식 [별지 제3 ~ 6호]
def doc11():
    f3 = [
        "담합 및 불공정행위 금지 : 입찰가격의 유지 또는 특정업체의 선정을 목적으로 담합하거나, 협정·결의·합의 등 자유로운 경쟁을 부당하게 저해하는 일체의 불공정 행위를 하지 않겠습니다.",
        "금품·향응 제공 금지 : 입찰, 선정, 계약체결 및 계약이행 전 과정(행사 종료 이후 포함)에 있어 귀 협의회 관계자, 심사위원, 관련 업무 종사자 등에게 직·간접적으로 금품·향응·편의 또는 기타 부당한 이익을 제공하지 않겠습니다.",
        "계약취소 및 손해배상 책임 : 입찰 또는 계약과 관련하여 뇌물 제공, 담합, 허위서류 제출 등 중대한 위반사실이 확인될 경우, 귀 협의회의 낙찰자 결정 취소·계약 취소 또는 계약 해지를 수용하며, 이로 인해 발생하는 손해에 대한 배상 책임을 부담할 것을 확약합니다.",
        "윤리경영 및 하도급 준수 : 임직원 및 협력업체의 담합·금품제공 등 불공정 행위를 방지하기 위한 윤리경영 기준을 마련하고, 불법 하도급·명의대여·재하도급 등의 행위를 하지 않겠습니다.",
        "자료제출 및 조사 협조 : 본 입찰 및 계약 이행과 관련하여 귀 협의회가 요청하는 자료 제출, 서류 열람, 사실 확인 등에 성실히 협조하겠습니다.",
    ]
    s3 = f"""<div class="form"><div class="no">[별지 제3호]</div><h1>청렴계약이행서약서</h1>
<p class="tx" style="margin-top:0">당사는 부패 없는 투명한 기업경영과 공정한 거래질서 확립이 사회적 신뢰와 지속가능한 발전의 핵심 요소임을 깊이 인식하고, 「{SITE} 입주예정자협의회」가 실시하는 입주박람회 주관사 선정 입찰에 참여함에 있어 청렴계약제의 취지에 적극 동참하고자 다음 사항을 성실히 이행할 것을 서약합니다.</p>
<ol style="font-size:10.4pt">{"".join(f"<li>{i}. {x}</li>" for i, x in enumerate(f3, 1))}</ol>
<p class="tx" style="font-size:10.4pt">위 청렴계약서약은 상호신뢰를 바탕으로 한 약속으로서 반드시 지킬 것이며, 이를 위반할 경우 입찰참가자격 제한, 협약 해지 또는 해제 등 귀 협의회의 조치에 대하여 손해배상을 청구하거나 민·형사상 어떠한 이의도 제기하지 않을 것을 서약합니다.</p>
{form_tail2()}</div>"""
    s4 = f"""<div class="form"><div class="no">[별지 제4호]</div><h1>비밀유지 서약서</h1>
<p class="tx" style="margin-top:20pt">귀 입주예정자협의회에서 실시하는 「입주박람회 주관사 선정 입찰공고」에 참가함에 있어, 당사는 본 입찰 과정에서 취득한 일체의 사항(입주예정자 개인정보, 협의회 내부 운영정보, 타사 제안 내용 등 포함)에 대하여 비밀을 준수할 것을 서약합니다.</p>
<p class="tx">또한 이를 위반할 경우 향후 귀 협의회가 실시하는 모든 입찰에서의 참가 제한은 물론, 귀 협의회의 손해배상 청구에 대하여 어떠한 이의도 제기하지 않을 것을 확약하며 본 서약서를 제출합니다.</p>
<div style="height:60pt"></div>{form_tail2()}</div>"""
    s5 = f"""<div class="form"><div class="no">[별지 제5호]</div><h1 style="letter-spacing:.12em">분쟁발생 시 책임배상 이행각서</h1>
<p class="tx" style="margin-top:20pt">당사는 「{SITE} 입주예정자협의회」가 실시하는 입주박람회 주관사 선정 입찰에 참여함에 있어, 입주박람회 진행 과정에서 입주예정자와 공동구매 참여업체 간 계약 체결 이후 발생하는 A/S, 하자보수, 서비스 이행 등과 관련한 분쟁이 발생할 경우, 주관사로서 이에 대한 책임을 부담하고 문제해결 및 손해배상 등 필요한 조치를 성실히 이행할 것을 확약합니다.</p>
<p class="tx">본 각서는 계약 체결 전·후 및 계약 종료 이후에도 본 입주박람회와 관련하여 발생한 상기 분쟁에 대하여 유효하며, 이에 대한 귀 입주예정자협의회의 정당한 조치에 대하여 이의를 제기하지 않을 것을 서약합니다.</p>
<div style="height:40pt"></div>{form_tail2()}</div>"""
    s6 = f"""<div class="form"><div class="no">[별지 제6호]</div><h1 style="letter-spacing:.15em">입찰결과 승복 서약서</h1>
<p class="tx" style="margin-top:14pt">당사는 「{SITE} 입주예정자협의회」의 협약자 선정 방식 및 공고문 내용과 본 입찰에 관련된 방침에 이의가 없음을 확약하며, 공정한 심사와 객관적인 내부 절차에 의한 입찰 진행상의 제반 결정에 어떠한 이의를 제기하지 않고 수락할 것을 확약합니다.</p>
<p class="tx">귀 협의회가 평가를 위해 구성한 평가위원과 평가방법 및 평가기준에 따른 결과에 대해서도 어떠한 이의를 제기하지 않겠으며, 사업자 선정 전까지도 귀 협의회의 추가 요청 내용과 계약체결에 따른 증빙 서류 제출 등 제반 유의사항을 준수할 것을 확약합니다.</p>
<p class="tx">주관사로 선정될 경우, 사업 전체를 타인(타사)에게 일괄 도급하지 않으며, 계약 이후라도 일괄 도급한 사실이 적발될 경우 계약이 해지되어도 민사 소송 등 이의를 일절 제기하지 않겠습니다.</p>
<p class="tx">주관사 미선정 시 {SITE}에 대한 별도의 입주박람회 주관 및 공동구매 등 행사 개최를 일절 하지 않을 것을 서약합니다.</p>
{form_tail2()}</div>"""
    s7 = f"""<div class="form"><h1 style="letter-spacing:.3em">서 약 서</h1>
<p class="tx" style="margin-top:20pt">당사는 「{e(D.NOTICE)}」({D.NOTICE_DATE})에 따라 입찰에 참가하면서 아래 사항을 서약합니다.</p>
<ol style="font-size:10.8pt"><li>1. 당사가 제출한 서류 일체는 반환되지 않음을 확인하며, 반환을 요구하지 않겠습니다(공고 8항 1).</li>
<li>2. 제안서 평가 결과 및 선정 결과에 대하여 어떠한 이의도 제기하지 않겠습니다(공고 8항 5).</li>
<li>3. 제출 서류에 허위 사실이 발견될 경우 계약 체결 이후라도 무효 처리됨을 확인합니다(공고 8항 1).</li></ol>
<div style="height:50pt"></div>{form_tail2()}</div>"""
    return doc("11 서약서 및 별지 서식", [s3, s4, s5, s6, s7])



# ================================================================== 8 붙임 — NICE 연혁 발췌
FONTS = os.path.join(HERE, "..", "통합제안서", "fonts")
NAVY, GOLD, GRAY, LINE = (0.051, 0.118, 0.2), (0.78, 0.66, 0.42), (0.36, 0.4, 0.46), (0.79, 0.81, 0.84)
CLIP_TITLE = fitz.Rect(0, 0, 595, 76)
CLIP_HIST = fitz.Rect(36, 321, 560, 511)
ROWS_RECENT = (398, 506)     # 연혁 표 중 최근 3년 주관 실적 6행(2023/11 ~ 2026/07) — 한 행 18pt
CLIP_FOOT = fitz.Rect(36, 800, 560, 828)


def annex07(nice_path, out_path):
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
    text(L + 23, 51.5, "붙임 ②", 8.5, "b", GOLD, "c")
    text(R, 51.5, "제출서류 8 최근 3년간 주관사 실적 증빙서류", 8.5, "r", GRAY, "r")
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
            ("원본 분량", f"전 {len(nice)}쪽 (요청 시 전문 제출)")]
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
    sx = (L + R) / 2 - 14 + F["b"].text_length(who, fontsize=11) / 2 + 30
    text(sx, y + 52, "(인)", 10, "r", GRAY)
    out.set_metadata({"title": "붙임 ② NICE 기업신용평가보고서 연혁 발췌", "author": D.COMPANY})
    out.save(out_path, garbage=4, deflate=True)



# ------------------------------------------------------------------ PDF
def to_pdf(html_path, pdf_path):
    subprocess.run([find_chrome(), "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=8000", f"--print-to-pdf={pdf_path}", pathlib.Path(html_path).as_uri()],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def render(name, html_text):
    h = os.path.join(HERE, PFX + name + ".html")
    pathlib.Path(h).write_text(html_text, encoding="utf-8")
    p = h[:-5] + ".pdf"
    to_pdf(h, p)
    return p


def merge(out_name, parts, title):
    out = fitz.open()
    for p in parts:
        out.insert_pdf(p if isinstance(p, fitz.Document) else fitz.open(p))
    out.set_metadata({"title": title, "author": D.COMPANY})
    path = os.path.join(HERE, PFX + out_name + ".pdf")
    out.save(path, garbage=4, deflate=True)
    return path

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    final = "--final" in sys.argv
    if len(args) < 2:
        sys.exit(__doc__)
    nice, seal_path = args[0], args[1]
    import stamp as ST
    seal = ST.seal_png(seal_path)

    def stamped(p):
        out, n = ST.stamp(seal, p)
        assert n >= 1, f"날인 자리 없음: {p}"
        return out

    res = {}
    res["01"] = stamped(render("01_입찰참가신청서", doc01()))
    biz = fitz.open(f"{EV}/사업자등록증.pdf")
    for pg_ in biz:
        for a in list(pg_.annots()):  # 발급 뒤 덧붙인 '세금계산서 발행정보' 스탬프 주석 — 원본 칸을 가리므로 뺀다
            pg_.delete_annot(a)
    res["02"] = merge("02_사업자등록증", [biz], "2 사업자등록증 사본")
    # 3 통장 사본 — 원본 스캔(통장 크기)을 A4 가운데에 그대로 배치
    bank = fitz.open(f"{EV}/법인통장_사본.pdf")
    b3 = fitz.open()
    pg = b3.new_page(width=595.28, height=841.89)
    r = bank[0].rect
    sc = min((595.28 - 120) / r.width, (841.89 - 200) / r.height)
    w, h = r.width * sc, r.height * sc
    pg.show_pdf_page(fitz.Rect((595.28 - w) / 2, 90, (595.28 + w) / 2, 90 + h), bank, 0)
    res["03"] = merge("03_법인통장_사본", [b3], "3 법인사업자 통장 사본")
    res["04"] = merge("04_법인등기부등본", [f"{EV}/법인등기부등본.pdf"], "4 법인등기부등본")
    render("05_사용인감계", doc05())  # 양식(HTML) — 제출본은 법인인감 실물 날인 스캔(10.15)
    gam = "/tmp/claude-0/-home-user-edge-company/a96d9eb6-5244-5d3f-9f1b-6f379ac2a82c/scratchpad/seal_scan/지웰_사용인감계_날인.pdf"
    res["05"] = merge("05_인감증명서_사용인감계", ["/tmp/claude-0/-home-user-edge-company/a96d9eb6-5244-5d3f-9f1b-6f379ac2a82c/scratchpad/v3/ingam_1008_masked.pdf", gam],
                      "5 인감증명서 및 사용인감계")
    res["06"] = merge("06_국세_지방세_완납증명서", [f"{EV}/국세_납세증명서.pdf", f"{EV}/지방세_납세증명서.pdf"], "6 국세 및 지방세 완납증명서")
    res["07"] = merge("07_4대보험_가입자명부", ["/tmp/claude-0/-home-user-edge-company/a96d9eb6-5244-5d3f-9f1b-6f379ac2a82c/scratchpad/cs_sub/엣지컴퍼니_철산역자이_06_4대보험_사업장가입자명부.pdf", f"{EV}/4대보험_완납증명서.pdf"],
                      "7 4대 보험 가입자 명부 및 4대 보험 완납증명서")
    p08 = stamped(render("08_실적증빙", doc08()))
    ann = os.path.join(HERE, PFX + "08_붙임_NICE연혁발췌.pdf")
    annex07(nice, ann)
    ann = stamped(ann)
    hw = os.path.join(HERE, PFX + "실적확약서.pdf")
    assert os.path.exists(hw), "hwakyak.py 지웰 <capture_dir> 2026.10.15 먼저"
    hw_s, _ = ST.stamp(seal, hw)
    res["08"] = merge("08_최근3년_실적증빙_직인", [p08, ann, hw_s], "8 최근 3년간 주관사 실적 증빙서류")
    res["11"] = stamped(render("11_서약서_별지3_6", doc11()))
    for k, v in res.items():
        print(k, os.path.basename(v), len(fitz.open(v)), "p")
    if TODOS:
        print(f"[확인 필요 {len(set(TODOS))}칸]", " / ".join(sorted(set(TODOS))))
        if final:
            sys.exit("--final: 확인 필요 칸이 남아 있음")


if __name__ == "__main__":
    main()
