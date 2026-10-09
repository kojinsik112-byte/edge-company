# -*- coding: utf-8 -*-
"""아산 탕정 푸르지오 센터파크 입주박람회 주관사 입찰 — 공고 7항 제출서류 중 직접 작성하는 문서(A4 세로).

  01 입찰 참가 신청서 [별지 1호] + 제출서류 목록     03 사용인감계(인감증명서와 함께 제출)
  06 하자보수 및 계약 이행 각서 [별지 2호]           07 입주박람회 실적 증빙(+별첨 1 NICE 연혁 발췌 · 별첨 2 실적 확약서)
  08 이의 제기 금지 서약서 [별지 3호]                09 계약 취소 · 환불 규정
  11 청렴계약 이행준수 서약서 [별지 4호]             12 입주박람회 성과 및 성공사례 자료(카페 이벤트 포함)
  14 기타 입찰제안 자료(요약 제안서 · 회사소개서)
별지 1~4호는 공고문 양식 문구를 그대로 옮기고 빈칸만 채운다. 숫자·약속은 data.py와 입찰제안서(05)에 이미 쓴 것만 옮긴다(새 약속 없음).
03 사용인감계는 사용인감 칸만 디지털 날인, 법인인감 칸·서명란 (인)은 등록 법인인감 실물을 찍어 스캔한다(디지털로 법인인감을 만들지 않는다).
별지 1호는 원문대로 대표자 줄에 (인)이 없고 오른쪽 ‘인감 대조필 ㊞’ 칸에 날인한다(숨은 표시 ‘(인감날인)’ — stamp.py는 이것을 찾으면 같은 쪽 ‘(인)’(대리인 칸)은 찍지 않는다).

사용: python docs_tj.py <NICE.pdf> <직인.png> [--final]
  --final : '확인 필요' 칸(재발급 발급일 · 생년월일 등)이 남아 있으면 멈춘다.
  NICE 원본·직인·인감이 들어간 결과물은 깃에 올리지 않는다(.gitignore: *.pdf, 엣지컴퍼니_*.html).
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
PFX = "엣지컴퍼니_탕정푸르지오센터파크_"
SITE = "아산 탕정 푸르지오 센터파크"
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


_p05 = os.path.join(HERE, PFX + "05_입주박람회_입찰제안서.pdf")
PROP = fitz.open(_p05) if os.path.exists(_p05) else None


def submit_rows():
    n05 = len(PROP) if PROP else 118
    return [
        ("01", "입찰 신청서 [별지서식 제 1호]", "본 서류", "1부"),
        ("02", "법인 사업자등록증 및 등기부등본 사본", f"사업자등록증 {issued('biz', '사업자등록증')} · 등기부등본 {issued('reg', '등기부등본')}", "각 1부"),
        ("03", "법인 인감증명서 및 사용인감계", f"인감증명서 {D.INGAM_DATE} 발급 · 사용인감계", "1부"),
        ("04", "국세 및 지방세 완납 증명서", f"국세 {issued('tax', '국세 납세증명서')} · 지방세 {issued('ltax', '지방세 납세증명서')}", "각 1부"),
        ("05", "입주박람회 입찰제안서", f"{n05}쪽", "1부"),
        ("06", "하자보수 및 계약 이행 각서 [별지서식 제 2호]", "", "1부"),
        ("07", "입주박람회 실적 및 공동구매 증빙자료(최근 3년간 실적 증명서)", "별첨 1 NICE 연혁 발췌 · 별첨 2 실적 확약서(카페 공지 붙임)", "1부"),
        ("08", "선정 결과 이의 제기 금지 서약서 [별지서식 제 3호]", "", "1부"),
        ("09", "계약자의 계약 취소 건에 대한 환불 규정", "제1 ~ 10조 · 별표", "1부"),
        ("10", "회사 기업신용평가서", f"NICE디앤비 CLIP · 평가 {D.NICE_DATE} (유효 ~2027.06.18)", "1부"),
        ("11", "청렴 계약 이행각서 [별지서식 제 4호]", "", "1부"),
        ("12", "입주박람회 성과 및 성공사례 자료(카페 이벤트 등 포함)", "", "1부"),
        ("13", "가장 최근 진행된 공동구매 물품 단가비교표", "가능한 경우 제출 항목 — " + todo("제출 여부 본부장 확인"), "-"),
        ("14", "기타 입찰제안에 필요한 자료", "자격 확약서(5항 4·6) · 요약 제안서 · 회사소개서", "1부"),
    ]


# ================================================================== 01 입찰 참가 신청서 [별지 1호]
def doc01():
    ag = D.AGENT
    agent = (f'직 위 : {e(ag[0])}<br><span class="ln"></span>성 명 : {e(ag[1])} &nbsp; (인)' if ag else
             '직 위 : <br><span class="ln"></span>성 명 : &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; (인)')
    yy, mm, dd = ymd()
    f1 = f"""<div class="form"><div class="no">[별지서식 제 1호]</div><h1>입찰 참가 신청서</h1>
<table class="ft">
<tr><th>입 찰 명</th><td colspan="4">“{SITE}” 주관사 선정 입찰 공고</td></tr>
<tr><th rowspan="3">신청인</th><th>업체명</th><td class="v">{D.COMPANY}</td><th>법인등록번호</th><td class="v">{D.CORP_NO}</td></tr>
<tr><th>주소</th><td>{D.ADDRESS}</td><th>전화번호</th><td>{D.TEL}</td></tr>
<tr><th>대표자명</th><td>{D.CEO}</td><th>대표자 생년월일</th><td>{birth()}</td></tr>
<tr><th>(입찰)<br>대리인</th><td colspan="4" class="agent">본 입찰에 관한 일체의 권한을 다음의 자에게 위임합니다.<br><span class="ln"></span>{agent}</td></tr>
</table>
<p class="tx">“{SITE}” 주관사 선정 입찰에 참여하고자 귀 입예협에서 정한 입찰 공고사항을 모두 승낙하고 제출서류를 첨부하며, 주관사 선정 입찰 조건 및 지시 사항을 준수하겠음을 확약하고 입찰에 참가하고자 신청합니다.</p>
<div class="chk"><div style="flex:1;font-size:11.5pt;line-height:2.2">주 &nbsp;소 : {D.ADDRESS}<br>상 &nbsp;호 : <b>{D.COMPANY}</b><br>대표자 : <b>대표이사 {D.CEO}</b></div>
<table class="stamp"><tr><td>인 &nbsp;감</td><td class="sl" rowspan="2">㊞<br><span class="mk">(인감날인)</span></td></tr><tr><td>대조필</td></tr></table></div>
<div class="dt">{yy}년 &nbsp; {mm}월 &nbsp; {dd}일</div>
<div class="to2">{SITE}<br>입주예정자협의회 귀중</div></div>"""
    rows = "".join(f'<tr><td>{n}</td><td class="l">{e(t)}</td><td class="l">{r}</td><td>{q}</td></tr>' for n, t, r, q in submit_rows())
    f2 = f"""{head("입찰 신청서 붙임", "제출서류 목록")}
<h2>공고 7항 제출서류 (공고 순서)</h2>
<table class="t"><thead><tr><th style="width:6%">No</th><th>서류</th><th style="width:38%">비고</th><th style="width:7%">부수</th></tr></thead><tbody>{rows}</tbody></table>
<p class="note">※ 공고 7항 15): 모든 제출 서류는 입찰공고일({D.NOTICE_DATE}) 이후 발급분 기준. 단, 10 기업신용평가서는 평가 유효기간(~2027.06.18) 안의 최신 평가본입니다. 2차 심사 시 원본을 제출합니다(원본과 동등한 효력이 있는 서류 제외).</p>
<p class="note">※ 10 기업신용평가서의 본사 주소는 본점 이전(2026.07.02 등기) 전 주소입니다. 현재 본점은 위 소재지와 같습니다.</p>
<p class="note">※ 메일 제출: {D.SUBMIT_TO} · 제목 「[아산탕정 푸르지오 센터파크 입찰 참가]_{D.COMPANY}」 · 마감 {D.DEADLINE}</p>"""
    return doc("01 입찰 참가 신청서", [f1, f2])


# ================================================================== 03 사용인감계
def doc03():
    body = f"""{head("제출서류 03", "사용인감계", True)}{company_table()}
<p class="body">위 법인은 아래 사용인감을 「{e(D.NOTICE)}」 입찰 참가 및 이에 따른 협약 체결에 관한 일체의 서류에 사용하고자
신고합니다. 이 인감의 사용으로 생기는 모든 책임은 당사가 집니다.</p>
<div class="seals">
<div><b>사용인감</b><span class="mk">(인감날인)</span><small>입찰 · 협약 서류에 사용</small></div>
<div><b>법인인감</b><span></span><small>인감증명서상 등록 인감</small></div>
</div>
<p class="note" style="margin-top:8pt">※ 첨부: 법인 인감증명서 1부({D.INGAM_DATE} 발급)</p>{sign()}"""
    return doc("03 사용인감계", [body])


# ================================================================== 06 하자보수 및 계약 이행 각서 [별지 2호]
def doc06():
    body = f"""<div class="form"><div class="no">[별지서식 제 2호]</div><h1>하자보수 및 계약 이행 각서</h1>
<table class="ft"><tr><th>업 체 명</th><td>{D.COMPANY}</td><th>직 위</th><td>대표이사</td></tr>
<tr><th>성 명</th><td>{D.CEO}</td><th>생 년 월 일</th><td>{birth()}</td></tr>
<tr><th>본 사 주 소</th><td colspan="3">{D.ADDRESS}</td></tr></table>
<p class="tx" style="margin-top:26pt">“{SITE}” 입주예정자협의회에서 시행하는 공동구매 행사와 관련하여 발생하는 사후 하자보수를 이행함에 있어, 계약(또는 협약) 일반조건에 따라 하자보증기간 내 주관한 행사에 참여한 업체가 납품한 공사 또는 물품에 하자가 발생한 경우, 당사는 해당 업체와 연대하여 즉시 하자보수 및 원상복구를 이행하고, 이로 인하여 발생한 모든 손해에 대하여 배상할 것을 서약합니다.</p>
{form_tail()}</div>"""
    return doc("06 하자보수 및 계약 이행 각서", [body])


# ================================================================== 07 입주박람회 실적 증빙
CAFE_DAESUNG = ("2024.11 ~ 2025.12", "에코델타 대성베르힐", "부산 에코델타시티", 1120)


def doc07():
    recs = [(d, nm, reg, n, "NICE 연혁(별첨 1)") for d, nm, reg, n in D.RECENT3]
    recs.append(CAFE_DAESUNG + ("입예협 카페 공지(별첨 2 붙임 ②)",))
    recs.sort(key=lambda r: r[0])
    rows = "".join(
        f'<tr><td>{i}</td><td style="white-space:nowrap">{d}</td><td class="l">{e(nm)}</td><td>{e(reg)}</td><td class="r">{n:,}</td>'
        f'<td class="l">{e(ev)}</td></tr>'
        for i, (d, nm, reg, n, ev) in enumerate(recs, 1))
    total = sum(r[3] for r in recs)
    body = f"""{head("제출서류 07", "입주박람회 실적 및 공동구매 증빙자료")}
<p class="note" style="margin-top:8pt">제출: {D.COMPANY} (사업자등록번호 {D.BIZ_NO} · 대표이사 {D.CEO})</p>
<h2>1. 최근 3년 1,000세대 이상 입주박람회 주관 실적</h2>
<p class="note" style="margin:0 0 5pt">기준: 공고일({D.NOTICE_DATE}) 기준 최근 3년(2023.10.06 ~ 2026.10.06) · 1,000세대 이상 공동주택 입주박람회 주관(박람회 · 공동구매 · 사후관리 수행).
시기·세대수는 NICE디앤비 CLIP 기업신용평가보고서(평가 {D.NICE_DATE}) ‘연혁’과 해당 단지 입주예정자협의회 공식 카페의 주관사 명의 공지 기준입니다.</p>
<table class="t"><thead><tr><th style="width:5%">No</th><th style="width:13%">주관 시기</th><th>단지명</th><th style="width:12%">지역</th>
<th style="width:10%">세대수</th><th style="width:24%">증빙</th></tr></thead>
<tbody>{rows}
<tr class="sum"><td colspan="4">합계 {len(recs)}개 단지</td><td class="r">{total:,}</td><td></td></tr></tbody></table>
<div class="box"><b>공고 5항 17) 대비</b> &nbsp; 요건: 1,000세대 이상 공동주택 3개 단지 이상 입주컨설팅 · 입주박람회 수행 실적
&nbsp;→&nbsp; 최근 3년만 <b>{len(recs)}개 단지 · {total:,}세대</b> &nbsp; <span class="ok">충족</span><br>
3년 이전을 포함한 1,000세대 이상 주관 실적은 <b>9개 단지 · 18,261세대</b>입니다(별첨 2 실적 확약서).</div>
<h2>2. 별첨 증빙</h2>
<ol style="list-style:none;font-size:10pt;line-height:1.8">
<li>별첨 1. NICE디앤비 CLIP 기업신용평가보고서 ‘연혁’ 발췌 — 1매 (보고서 전문은 제출서류 10)</li>
<li>별첨 2. 대표이사 실적 확약서 — 1매 · 붙임: 입예협 공식 카페 주관사 공지 캡처 2매(입주민 닉네임 동·호수 가림)</li>
<li>입예협 요청 시 계약서 · 실적 확인서 · 정산 자료를 지체 없이 추가 제출합니다(공고 5항 13).</li></ol>
<p class="body" style="font-size:10pt">위 실적은 사실과 다름이 없음을 확인하며, 허위로 확인될 경우 공고 6항 5) · 8항 4)에 따른 어떠한 조치도 이의 없이 따르겠습니다.</p>{sign()}"""
    return doc("07 입주박람회 실적 및 공동구매 증빙자료", [body])


# ================================================================== 08 이의 제기 금지 서약서 [별지 3호]
def doc08():
    items = [
        "입찰 참가신청과 관련하여 작성된 모든 증빙자료는 신의성실의 원칙에 입각하여 작성하였으며, 귀사의 제안서 평가 및 협상 결과 등에 대하여 어떠한 이의도 제기하지 않겠습니다.",
        "협의회의 평가 결과에 대하여 부당하게 이의를 제기하거나 계약자 선정 통보에 불응한 경우 관계법령에 따라 부정 사업자로 제재 등 어떠한 처분도 감수하겠습니다.",
        "주관사로 선정될 경우, 사업 전체를 타인(타사)에게 일괄 도급하지 않으며, 계약 이후라도 일괄 도급한 사실이 적발될 경우, 계약이 해지되어도 민사 소송 등 이의를 일절 제기하지 않겠습니다.",
        "주관사 미 선정 시 입주예정자협의회의 승인 없이 공식 주관사 또는 협력업체로 오인될 수 있는 홍보 및 영업행위를 하지 않을 것을 서약합니다.",
    ]
    lis = "".join(f"<li>{i}. {x}</li>" for i, x in enumerate(items, 1))
    body = f"""<div class="form"><div class="no">[별지서식 제 3호]</div><h1>이의 제기 금지 서약서</h1>
<p class="tx">본 업체는 {SITE} 입주예정자협의회에서 진행하는 주관사 선정, 행사 주관 및 사후관리 위탁 제안과 관련하여 아래 내용을 준수하고 이행할 것을 확약하며 본 서약서를 제출합니다.</p>
<ol>{lis}</ol>{form_tail()}</div>"""
    return doc("08 이의 제기 금지 서약서", [body])


# ================================================================== 09 계약 취소 · 환불 규정
CANCEL_7 = "청소·줄눈, 탄성코트, 유리막코팅, 선반·잡물, 음식물처리기, 인덕션, 벽걸이TV, LED조명"
CANCEL_15 = "미세방충망, 인테리어, 단열필름, 시스템에어컨, 포장이사"
CUSTOM = "커튼·블라인드, 중문, 안전방충망, 맞춤가구"


def doc09():
    arts = [
        ("제1조 (목적)", None,
         f"이 규정은 {D.COMPANY}(이하 ‘주관사’)가 주관하는 {SITE} 입주박람회 및 공동구매(이하 ‘공동구매’)에서 "
         "입주예정자(이하 ‘계약자’)와 참여업체 사이에 체결되는 계약의 계약금·잔금 지급 조건과 취소·환불 기준을 정하여 계약자의 권리를 보호함을 목적으로 한다."),
        ("제2조 (적용 범위)", [
            "공동구매를 통해 체결된 모든 품목의 계약에 적용한다. 박람회 현장 계약과 온라인 박람회(폐쇄몰) 계약을 모두 포함한다.",
            "참여업체는 이 규정을 계약서에 반영하고 계약 체결 전에 계약자에게 설명하여야 한다.",
            "브랜드 본사 직영 품목(가전·가구 등)과 사전점검 대행은 각 본사 계약 규정을 따르되, 그 내용을 계약 전에 서면으로 고지하여야 한다.",
        ]),
        ("제3조 (계약금)", [
            f"계약금은 계약 총액의 <b>{D.DEPOSIT_MAX}% 이하</b>로 한다(계약금 {D.DEPOSIT_MAX}% 상한제).",
            "계약금과 잔금 모두 카드 결제 시 현금가와 <b>동일한 가격</b>을 적용하며, 현금 결제 시 현금영수증을 발행한다.",
        ]),
        ("제4조 (잔금 지급 조건)", [
            "잔금은 <b>시공·설치가 끝나고 계약자가 확인한 후</b> 지급한다. 제품만 납품하는 품목은 납품·설치 확인 후 지급한다.",
            "참여업체가 입찰 때 약속한 기대매출을 넘긴 경우의 실적 비례 추가할인은 잔금에서 차감한다. 품목별 할인율은 입예협과 검토해 정한다.",
            "시공 결과 확인 시 하자·미시공 부분이 있으면 계약자는 해당 부분의 보수가 끝난 후 잔금을 지급할 수 있다.",
        ]),
        ("제5조 (취소·환불 기준)", [
            "품목별 취소 가능 기한은 [별표]와 같다. 기한 안에 취소하면 납부한 금액 <b>전액</b>을 환불한다.",
            f"맞춤 제작 품목({CUSTOM})은 출고 지시 전까지 참여업체와 협의하여 취소한다. 브랜드 가전·가구는 미제작·출고 지시 전에는 전액 취소·환불한다.",
            "참여업체가 사전 해피콜을 이행하지 않은 경우, 계약자 미동의 주문제작 건을 포함한 <b>모든 품목은 당일 취소·환불</b>할 수 있다(공급사 귀책).",
            "인테리어는 시공일 15일 전까지 취소할 수 있으며, 세부 조건은 참여업체가 계약 전에 서면으로 고지하여야 한다.",
            "취소 기한이 지난 뒤의 취소는 실제 발생한 자재·제작 비용만 공제할 수 있으며, 참여업체는 공제 내역을 서면으로 제시하여야 한다. 주관사는 공제 내역의 적정성을 검토한다.",
            "시공 지연, 계약과 다른 제품·시공, 하자 미보수 등 참여업체 귀책으로 계약을 해지하는 경우에는 기한과 관계없이 납부 금액 전액을 환불한다.",
        ]),
        ("제6조 (취소 신청 및 환급)", [
            "취소는 참여업체 또는 주관사 콜센터 · 공식카페 신문고 · 카카오채널로 신청하며, 문자·메신저 등 기록이 남는 방법으로 한다.",
            "환불금은 취소 확정일로부터 <b>3영업일 이내</b>에 지급하고, 카드 결제분은 같은 기한 안에 승인 취소한다.",
            "주관사는 환불 완료 여부를 계약자에게 확인(해피콜)한다.",
        ]),
        ("제7조 (불이행 시 조치 및 주관사 책임)", [
            "참여업체가 취소·환불을 지연하거나 거부하면 계약자는 주관사 콜센터에 접수할 수 있다. 주관사는 사실을 확인한 뒤 계약자에게 피해 금액을 <b>먼저 보상</b>하고, 참여업체와는 계약 조항에 따라 정산한다(하자보수 및 계약 이행 각서 [별지서식 제 2호] 준용).",
            "불이행 업체에는 1단계 홍보정지, 2단계 총액 10% 배상, 3단계 자격박탈 및 입예협 승인을 받아 전 계약을 대체업체로 이관하는 패널티를 차례로 부과한다.",
            "참여업체가 도산한 경우 동종업체로 사후관리를 이관하고, 그 A/S 비용은 주관사가 전액 부담한다.",
            "주관사의 보상 재원으로 하자 예치금 최대 1억원(엣지컴퍼니 자산으로 예치)과 이행보증보험(2년 · 최대 10억원)을 둔다.",
        ]),
        ("제8조 (가격 보호 — 최저가 차액 10배 보상)", [
            "공동구매 품목과 브랜드·모델명이 같은 새 제품이 계약 후 7일 이내에 인근(아산·천안권) 오프라인 매장에서 "
            "더 낮은 정상 판매가로 판매된 사실이 견적서·영수증으로 확인되면, 참여업체는 차액의 10배를 보상하고 판매가를 조정한다.",
            "온라인·홈쇼핑 판매, 시공 품목, 카드 청구할인·사은품·결합할인, 전시·리퍼 상품, 법인 특판, 한정 수량 행사가는 비교 대상에서 제외한다.",
            "계약자는 주관사 콜센터에 접수하고, 주관사는 사실 확인 후 7일 이내에 보상이 이행되도록 관리한다.",
        ]),
        ("제9조 (고지)", None,
         "주관사는 이 규정을 박람회장 · 온라인 박람회에 게시하고, 입주예정자협의회 카페에는 입예협 승인 후 게시하며, 모든 공동구매 계약서에 첨부한다."),
        ("제10조 (효력)", None,
         "이 규정은 협약 체결일부터 협약 종료일(입주 후 1년)까지 체결된 계약에 적용하며, 협약 종료 후에도 해당 계약의 이행·보증 기간 동안 효력을 가진다."),
    ]
    out = []
    for a in arts:
        h, items = a[0], a[1]
        if items:
            lis = "".join(f"<li>{'①②③④⑤⑥⑦⑧'[i]} {x}</li>" for i, x in enumerate(items))
            out.append(f'<div class="art"><h3>{h}</h3><ol>{lis}</ol></div>')
        else:
            out.append(f'<div class="art"><h3>{h}</h3><p>{e(a[2])}</p></div>')
    table = f"""<h2>[별표] 품목별 취소 가능 기한 (시공일 기준)</h2>
<table class="t"><thead><tr><th style="width:24%">취소 가능 기한</th><th>품목</th></tr></thead><tbody>
<tr><td class="k" style="text-align:center">시공일 7일 전까지</td><td class="l">{CANCEL_7}</td></tr>
<tr><td class="k" style="text-align:center">시공일 15일 전까지</td><td class="l">{CANCEL_15}</td></tr>
<tr><td class="k" style="text-align:center">출고 지시 전까지</td><td class="l">맞춤 제작 품목({CUSTOM})은 업체와 협의 후 취소 · 브랜드 가전·가구(미제작 시)</td></tr>
<tr><td class="k" style="text-align:center">당일 취소 가능</td><td class="l">사전 해피콜 미이행 시 모든 품목(공급사 귀책)</td></tr>
</tbody></table>
<p class="note">※ 품목 구성은 입주예정자협의회 수요조사 결과에 따라 확정되며, 추가 품목의 기한은 성격이 같은 품목의 기한을 따른다.</p>"""
    summary = f"""<div class="box"><b>핵심 요약</b> &nbsp; 계약금 {D.DEPOSIT_MAX}% 이하 · 현금·카드 동일가 · 잔금은 시공·설치 확인 후 ·
품목별 취소 기한 안 전액 환불(맞춤 제작은 출고 지시 전 업체 협의) · 환불 3영업일 이내 · 업체 불이행 시 주관사 선보상</div>"""
    return doc("09 계약 취소 · 환불 규정", [head("제출서류 09", "공동구매 계약 취소 · 환불 규정") + summary + "".join(out) + table + sign()])


# ================================================================== 11 청렴계약 이행준수 서약서 [별지 4호]
def doc11():
    items = [
        "유리한 입찰가격 또는 특정인의 낙찰을 위한 담합을 하거나 다른 업체와 협정, 결의, 합의하여 입찰의 자유경쟁을 부당하게 저해하는 일체의 불공정한 행위를 하지 않겠습니다.",
        "참여업체간 상호 비방 또는 흑색선전행위, 과대선전은 물론 부정한 방법, 공정한 경쟁을 저해하는 행위를 하지 않겠으며, 타 업체의 관련 업무를 일체 방해하지 않겠습니다.",
        "입찰, 계약 체결, 계약 이행, 행사 개최 및 완료와 관련하여 입예협에서 요구하는 자료 제출, 서류 열람, 현장 확인 등 활동에 적극 협조하겠습니다.",
        "위법행위가 발견되었을 경우나, 위 각 호를 위반하는 경우에는 선정취소, 형사고발 등 입예협의 결정에 일체의 이의를 제기하지 않겠습니다.",
        "[공동구매 및 입주박람회] 관련 하도급 계약 체결 및 이행에 있어서 하도급자로부터 금품을 수수하거나 부당 또는 불공정한 행위를 하지 아니하겠습니다.",
    ]
    lis = "".join(f"<li>{i}. {x}</li>" for i, x in enumerate(items, 1))
    body = f"""<div class="form"><div class="no">[별지서식 제 4호]</div><h1>청렴계약 이행준수 서약서</h1>
<p class="tx">{SITE} 입주예정자협의회에서 시행하는 입찰, 계약체결 및 계약이행 과정에 있어서 당사 임직원과 대리인은</p>
<ol>{lis}</ol>
<p class="tx">위 청렴 계약 이행 서약은 상호 신뢰를 바탕으로 한 약속으로서 반드시 지킬 것이며, 낙찰자로 결정될 시 본 서약 내용을 그대로 계약조건으로 계약하여 이행하고, 입찰 참가 자격 제한, 계약 해지 등 협의회의 조치와 관련하여 당사는 협의회를 상대로 손해배상을 청구하거나, 배제하는 입찰에 관하여 민‧형사상 일체 이의제기를 하지 않을 것을 서약합니다.</p>
{form_tail()}</div>"""
    return doc("11 청렴계약 이행준수 서약서", [body])


# ================================================================== 12 성과 및 성공사례 자료
# 입찰제안서(05)에서 성과·사례 쪽만 제목으로 찾아 붙인다(쪽 번호가 바뀌어도 안전).
CASE_PAGES = ["숫자로 보는 엣지컴퍼니", "주관 성공사례 · 수임실적", "2,000세대 이상 초대형 단지를 맡아 왔습니다", "대단지 운영 경험",
              "사진으로 보는 주관 단지 2023 ~ 2026", "한 단지가 아니라 한 신도시를 맡습니다", "타 단지 협의회의 추천과 감사",
              "행사 밖에서도 현장 지원", "입예협 카페 홍보 콘텐츠 제작", "입주민 후기 · 실시간 응대 화면", "실제 박람회 현장"]
CAFE = [  # (캡처 파일, 단지, 카페 주소, [(날짜, 글 제목 — 캡처 화면 원문 그대로(이모티콘 제외), 댓글 수)]) — 07 붙임과 같은 순서(사상 → 대성)
    ("cafe_sasang_2.png", "부산사상 중흥S-클래스 그랜드센트럴 (1,572세대)", "cafe.naver.com/f-e/cafes/30121620/menus/111",
     [("2022.12.14", "[주관사 댓글 이벤트] 알찬 입주 박람회를 위한 수요조사 및 대규모 댓글 이벤트 진행합니다(마감)", "268"),
      ("2022.12.31", "사상 중흥 S-클래스 입주민 여러분 한 해 수고 많으셨습니다^^ -주관사 일동-", "1"),
      ("2023.01.16", "입주 설명회에 많은 입주민분들이 참석해 주셔서 너무 감사드립니다.", "-"),
      ("2023.02.03", "입주박람회 일정 및 박람회 개최 기념 댓글 이벤트 안내입니다.", "543"),
      ("2023.02.20", "사상중흥S-클래스 그랜드 센트럴 입주박람회 날짜 장소 및 혜택 안내드립니다.", "12"),
      ("2023.03.01", "입주박람회 혜택 총정리와 박람회장 선착순 방문 혜택 내용입니다", "17")]),
    ("cafe_daesung.png", "에코델타 대성베르힐 (1,120세대)", "cafe.naver.com/f-e/cafes/30960655/menus/126",
     [("2024.11.08", "주관사 주식회사 엣지컴퍼니 인사드립니다.", "14"),
      ("2024.11.08", "에코델타 대성베르힐 드론영상 최초공개 합니다.", "39"),
      ("2024.12.07", "엣지컴퍼니 이벤트.1)주관사 선정 기념 응원 댓글이벤트!! 선착순 500세대 진행합니다 GOGO!!", "426"),
      ("2025.01.09", "주관사 선정 댓글선착순 500세대 커피쿠폰 증정 안내", "9"),
      ("2025.11.19", "[에코델타 대성베르힐 점등식 공개]", "5"),
      ("2025.11.24", "입주박람회 사전 이벤트 안내 – 요즘 가장 인기 있는 ‘휴젠뜨’ 공동구매 사전조사!", "81"),
      ("2025.11.26", "에코델타 대성베르힐, 80여 업체가 참여하는 ‘최강 혜택’의 입주박람회 개막", "1"),
      ("2025.11.30", "불편을 드려 죄송합니다 – 입주박람회 긴급 안전 안내", "-"),
      ("2025.12.02", "대성베르힐 입주박람회의 성료 안내 및 주관사 업무 안내", "3")]),
]


def find_pages(titles):
    idx = []
    for t in titles:
        hit = [i for i, p in enumerate(PROP) if (lambda x: x.startswith("EG") and t in x[:400])(p.get_text().replace("\n", " ").strip())]
        assert hit, f"제안서에서 쪽을 찾지 못함: {t}"
        idx.append(hit[0])
    return idx


def doc12_cover():
    rows = "".join(f'<tr><td colspan="3" class="l" style="background:#F1EDE4;font-weight:800">붙임 {k}. {e(nm)}</td></tr>'
                   + "".join(f'<tr><td style="white-space:nowrap">{d}</td><td class="l">{e(t)}</td><td>{e(c)}</td></tr>' for d, t, c in ev)
                   for k, (_, nm, _, ev) in enumerate(CAFE, 1))
    pages = find_pages(CASE_PAGES) if PROP else []
    lst = " · ".join(f"{t}({i + 1}쪽)" for t, i in zip(CASE_PAGES, pages))
    body = f"""{head("제출서류 12", "입주박람회 성과 및 성공사례 자료")}
<div class="box"><b>요약</b> &nbsp; 누적 주관·수임 <b>67개 단지 · 56,361세대</b>(전신 실적 포함, 2027년 입주 예정 단지까지) ·
1,000세대 이상 주관 <b>9개 단지 · 18,261세대</b> · 최대 단일 단지 <b>레이카운티 4,470세대</b> · 사송 · 에코델타 신도시 연속 수임</div>
<h2>1. 입예협 카페 이벤트 · 공지 사례 (붙임 캡처)</h2>
<table class="t"><thead><tr><th style="width:13%">날짜</th><th>글 제목 — 카페 화면 원문(작성자: 주관사 엣지컴퍼니)</th><th style="width:9%">댓글</th></tr></thead><tbody>{rows}</tbody></table>
<p class="note">※ 단지별 입예협 공식 카페 화면 그대로입니다(붙임 1 · 2). 입주민 닉네임의 동 · 호수와 캡처 계정 닉네임은 개인정보 보호를 위해 가렸습니다.</p>
<h2>2. 성공사례 · 현장 자료 (입찰제안서 발췌)</h2>
<p style="font-size:9.8pt;line-height:1.8">{e(lst)}</p>
<p class="note">※ 사진 속 단지 · 행사는 타 단지 실제 운영 사례이며, 세부는 입찰제안서(제출서류 05) 해당 쪽과 같습니다.</p>"""
    caps = [f'<h2>붙임 {i}. {e(nm)} 입예협 카페</h2><p class="note">{e(url)} · 입주민 닉네임(동·호수) 가림</p>'
            f'<img src="assets_ins/{f}" style="display:block;max-width:100%;max-height:228mm;margin:6pt auto 0;border:.6pt solid #C9CED6">'
            for i, (f, nm, url, _) in enumerate(CAFE, 1)]
    return doc("12 입주박람회 성과 및 성공사례 자료", [body] + caps)


# ================================================================== 14-1 입찰 참가 자격 확약서(공고 5항 4·6)
def doc_qual():
    body = f"""{head("제출서류 14-1", "입찰 참가 자격 확약서", True)}{company_table()}
<p class="body">당사는 {e(D.CLIENT)}의 「{e(D.NOTICE)}」({D.NOTICE_DATE}) 입찰에 참가하면서, 공고 5항 입찰자격 중 아래 사항이 사실임을 확약합니다.</p>
<table class="t" style="margin-top:10pt"><thead><tr><th style="width:12%">공고 5항</th><th>입찰 자격</th><th style="width:18%">당사 현황</th></tr></thead><tbody>
<tr><td>4)</td><td class="l">최근 5년간 법규 위반으로 벌금 이상의 형사처분을 받지 아니한 회사</td><td>해당 사항 없음</td></tr>
<tr><td>6)</td><td class="l">공고일 기준 공동구매 및 입주박람회와 관련하여 예비입주자 또는 입예협과 분쟁 및 소송이 없는 회사</td><td>해당 사항 없음</td></tr>
</tbody></table>
<p class="body" style="font-size:10pt">위 내용이 사실과 다른 것으로 밝혀질 경우 공고 6항 5) · 8항 4) · 9항 1)에 따른 선정 무효 · 계약 해지 등 귀 협의회의 조치를 이의 없이 따르겠습니다.</p>{sign()}"""
    return doc("14-1 입찰 참가 자격 확약서", [body])


# ================================================================== 14 기타 입찰제안 자료
def doc14_cover():
    body = f"""{head("제출서류 14", "기타 입찰제안 자료")}
<p class="body">공고 7항 14)에 따라 입찰제안 검토에 도움이 되는 자료를 첨부합니다.</p>
<table class="t" style="margin-top:10pt"><thead><tr><th style="width:8%">No</th><th>자료</th><th style="width:40%">내용</th></tr></thead><tbody>
<tr><td>1</td><td class="l">입찰 참가 자격 확약서</td><td class="l">공고 5항 4) · 6) 해당 사항 없음 확약 (대표이사 날인)</td></tr>
<tr><td>2</td><td class="l">요약 제안서</td><td class="l">입찰제안서(05)의 핵심을 한 권으로 정리</td></tr>
<tr><td>3</td><td class="l">회사소개서</td><td class="l">연혁 · 조직 구성 · 주관 실적 · 자격과 증빙</td></tr>
</tbody></table>"""
    return doc("14 기타 입찰제안 자료", [body])


# ================================================================== 07 별첨 1 — NICE 연혁 발췌(철산 docs_cs.annex08과 같은 방식)
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
    text(L + 23, 51.5, "별첨 1", 8.5, "b", GOLD, "c")
    text(R, 51.5, "제출서류 07 입주박람회 실적 및 공동구매 증빙자료", 8.5, "r", GRAY, "r")
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
            ("원본 분량", f"전 {len(nice)}쪽 (전문은 제출서류 10)")]
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
    out.set_metadata({"title": "별첨 1 NICE 기업신용평가보고서 연혁 발췌", "author": D.COMPANY})
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
    assert PROP is not None, "입찰제안서(05) PDF가 없음 — build_tangjeong.py 먼저"

    def stamped(p):
        out, n = ST.stamp(seal, p)
        assert n >= 1, f"날인 자리 없음: {p}"
        return out

    res = {}
    res["01"] = stamped(render("01_입찰참가신청서", doc01()))
    res["03s"] = stamped(render("03_사용인감계", doc03()))
    res["06"] = stamped(render("06_하자보수_계약이행각서", doc06()))
    # 07 = 실적표 + 별첨 1 NICE 발췌 + 별첨 2 실적 확약서(붙임 카페 캡처)
    p07 = stamped(render("07_실적증빙", doc07()))
    ann = os.path.join(HERE, PFX + "07_별첨1_NICE연혁발췌.pdf")
    annex07(nice, ann)
    ann = stamped(ann)
    hw = os.path.join(HERE, PFX + "실적확약서.pdf")
    assert os.path.exists(hw), "hwakyak.py 탕정 <capture_dir> 2026.10.22 먼저"
    hw_s, n = ST.stamp(seal, hw)
    res["07"] = merge("07_실적및공동구매증빙_별첨포함_직인", [p07, ann, hw_s], "07 입주박람회 실적 및 공동구매 증빙자료")
    res["08"] = stamped(render("08_이의제기금지서약서", doc08()))
    res["09"] = stamped(render("09_계약취소_환불규정", doc09()))
    res["11"] = stamped(render("11_청렴계약이행서약서", doc11()))
    cov12 = render("12_성과_성공사례_표지", doc12_cover())
    sel = fitz.open()
    for i in find_pages(CASE_PAGES):
        sel.insert_pdf(PROP, from_page=i, to_page=i)
    res["12"] = merge("12_성과_성공사례", [cov12, sel], "12 입주박람회 성과 및 성공사례 자료")
    cov14 = render("14_기타_표지", doc14_cover())
    qual = stamped(render("14_1_자격확약서", doc_qual()))
    res["14"] = merge("14_기타_요약제안서_회사소개서", [cov14, qual, os.path.join(HERE, PFX + "요약제안서.pdf"), os.path.join(HERE, PFX + "회사소개서.pdf")],
                      "14 기타 입찰제안 자료 (요약 제안서 · 회사소개서)")
    for k, v in res.items():
        print(k, os.path.basename(v), len(fitz.open(v)), "p")
    if TODOS:
        print(f"[확인 필요 {len(set(TODOS))}칸]", " / ".join(sorted(set(TODOS))))
        if final:
            sys.exit("--final: 확인 필요 칸이 남아 있음")


if __name__ == "__main__":
    main()
