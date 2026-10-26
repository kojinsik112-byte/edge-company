# -*- coding: utf-8 -*-
"""상주 자이르네 입주박람회 주관사 선정 입찰 — 공고 5항 제출 서류 생성기(A4 세로) · 번호 순서대로 PDF 1개 병합.

5항: 아래 서류를 번호 순서대로 1개의 PDF 파일로 병합해 협의회 이메일(alwayspcs@hanmail.net) 제출 · 마감 2026.10.28(수) 17:00.
  00 제출서류 목록(쪽 번호 · 안내용, 통합 PDF 맨 앞)
  1  입찰참가신청서(협의회 소정 양식)
  2  사업자등록증 사본 · 법인등기부등본(2026.10.14 발급)
  3  국세 · 지방세 납세증명서(2026.10.14 발급 · 유효 ~11.13 = 마감일 현재 유효)
  4  [별지1호] 이해관계 신고 및 청렴 서약서(1 · 2항 '없음' — 본부장 10-16)
  5  법인인감증명서(2026.10.15 · 대표자 주민번호 뒷자리 가림) + [별지4호] 사용인감계
  6  [별지2호] 전담 책임자 · 분야별 전문가 명단 + 증빙(전기공사업 등록증 · 4대보험 가입자 명부 · 자격증 · 협력 계약서 = 본부장 제공 대기)
  7  [별지3호] 입주박람회 주관 실적 증명서(8건 · data.SJ_REC) + 증빙 안내 · A 주관사 협약서 3 · B 공식 행사일정 · 카페 공지 · C NICE 연혁 발췌
  8  회사소개서 = 표지 + 업무 수행 제안서 01장 '회사소개'
  9  업무 수행 제안서 = build_sj.py(120쪽)

날인: 신청서 · 별지1 ~ 3호 대표자 '(인감)' 칸 = 사용인감(직인 투명 PNG) → 5에 별지4호 사용인감계를 붙인다(공고 5항 5).
  - 사용인감계: 사용인감 칸만 디지털 직인 → 작업/'별지4호_사용인감계_출력용.pdf' 출력 → 법인인감 칸 · 신고인 (인)에 법인인감 실물 날인 → 스캔(1쪽)을
    SEAL_SCAN 경로에 두면 그 스캔으로 바꿔 최종본(파일명 = 공고 형식)을 만든다. 스캔이 없으면 출력용을 그대로 넣은 '_직인본'.
  - 법인인감은 디지털로 만들지 않는다.
출력: 작업/ = 중간 파일 · 제출본/ = 통합 PDF 1개(메일용 저용량본은 만들지 않음 — 본부장 10-20) · 작업/제출현황.txt(내부용 — 첨부 금지)
사용: python docs_sj.py <투명 직인.png> [--final]    (결과 PDF · HTML은 깃 제외 — .gitignore)
"""
import html
import io
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
PFX = "엣지컴퍼니_상주자이르네_"
SITE = D.SITE["name"]
FORM_TO = "상주 자이르네 입주예정자협의회 회장 귀하"   # 양식 원문 표기
try:  # 별지2호 전문가 성명 · 자격번호 · 재직증명서 대상 — org_private.json(깃 제외 · 본부장 10-26)
    import json as _json
    PRIV = _json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "org_private.json")))
except (OSError, ValueError):
    PRIV = {}
TODOS = []

SP = "/tmp/claude-0/-home-user-edge-company/a96d9eb6-5244-5d3f-9f1b-6f379ac2a82c/scratchpad"
EV = os.environ.get("SJ_EVIDENCE", f"{SP}/evidence")  # 증빙 원본(깃 제외)
NICE_SRC = f"{EV}/NICE_기업신용평가.pdf"
ROSTER = f"{SP}/cs_sub/엣지컴퍼니_4대보험_사업장가입자명부_20261023_가림.pdf"   # 2026.10.23 발급(13명) · 성명 가운데 글자 · 주민번호 뒷자리 가림본 — 본부장 10-23
R500_DOC = D.R500_DOC   # 주관사 협약서 3건(센터포인트 · 드파인 센텀 · 디에트르 더퍼스트) — 상대방 성명 · 연락처 · 계좌 가림본
EXPERT_DIR = f"{SP}/sangju/experts"   # 별지2호 증빙(자격증 사본 · 재직증명서 · 협력 계약서) — 본부장 제공 시 여기에 PDF로(파일명 순서대로 붙임)
WORK = os.path.join(HERE, "작업")
SUBMIT = os.path.join(HERE, "제출본")
P09 = os.path.join(HERE, "엣지컴퍼니_상주자이르네_입주박람회_주관사_업무수행제안서_밝은시안.pdf")  # 본부장 10-21: 제출본 = 밝은 버전(tools/light_build.py)
SEAL_SCAN = getattr(D, "SEAL_SCAN", None) or f"{SP}/seal_scan/상주_사용인감계_날인.pdf"   # 별지4호 사용인감계 법인인감 실물 날인 스캔(1쪽)


def todo(x):
    TODOS.append(x)
    return f'<mark class="todo">{e(x)}</mark>'


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
h1{font-size:19pt;font-weight:800;color:#0D1E33;margin-top:12pt;line-height:1.3}
h1.c{text-align:center;font-size:21pt;letter-spacing:.2em;margin-top:16pt}
.case{font-size:9.5pt;color:#5B6676;margin-top:3pt}
.info{width:100%;border-collapse:collapse;margin-top:12pt;font-size:9.8pt}
.info th{width:17%;background:#F1EDE4;color:#0D1E33;font-weight:700;text-align:left;padding:5pt 9pt;border:.6pt solid #D5CCB9;white-space:nowrap}
.info td{padding:5pt 9pt;border:.6pt solid #D5CCB9}
h2{font-size:12pt;font-weight:800;color:#0D1E33;margin:13pt 0 5pt;padding-left:8pt;border-left:3.5pt solid #C8A86A;line-height:1.3;break-after:avoid}
.t{width:100%;border-collapse:collapse;font-size:9.3pt;line-height:1.45}
.t th{background:#0D1E33;color:#fff;font-weight:700;padding:4pt 6pt;border:.6pt solid #0D1E33;text-align:center}
.t td{padding:3.4pt 6pt;border:.6pt solid #C9CED6;text-align:center;vertical-align:middle}
.t td.l{text-align:left}.t td.r{text-align:right;font-variant-numeric:tabular-nums}
.t tr{break-inside:avoid}
.t td.k{font-weight:700;background:#F6F7F9;text-align:left;white-space:nowrap}
.t tr.sum td{background:#F1EDE4;font-weight:800}
.box{border:1pt solid #C8A86A;background:#FBF8F1;border-radius:4pt;padding:7pt 11pt;margin-top:10pt;font-size:9.8pt;line-height:1.65}
.box b{color:#0D1E33}
p.body{margin-top:12pt;font-size:10.5pt;line-height:1.85}
.note{font-size:8.8pt;color:#5B6676;margin-top:5pt;line-height:1.55}
ol.pl{list-style:none;margin-top:8pt}
ol.pl li{padding-left:16pt;text-indent:-16pt;margin-top:5pt;font-size:10.2pt;line-height:1.72}
ol.pl li.sm{font-size:9.2pt;margin-top:2pt;line-height:1.5}
.sign{margin-top:16pt;text-align:center;break-inside:avoid}
.sign .d{font-size:11pt;letter-spacing:.06em}
.sign .who{margin-top:6pt;font-size:12pt;font-weight:700}
.sign .seal{color:#5B6676;font-size:10pt;font-weight:400;margin-left:30pt}
.to{margin-top:18pt;text-align:center;font-size:12.5pt;font-weight:800;color:#0D1E33}
.art h3{font-size:10.5pt;font-weight:800;color:#0D1E33;margin-top:7pt}
.art ol{list-style:none;margin-top:2pt}.art li{font-size:9.4pt;line-height:1.6;padding-left:13pt;text-indent:-13pt;margin-top:1pt}
.art p{font-size:9.4pt;line-height:1.6;margin-top:2pt}
/* 지침서 별지 서식 — 흑백 */
.form{color:#111;font-size:11pt;line-height:1.85}
.form .no{font-size:10pt;color:#333}
.form h1{text-align:center;font-size:21pt;letter-spacing:.3em;color:#111;margin:14pt 0 12pt}
.form .cs{text-align:center;font-size:11pt;margin-bottom:12pt}
.form .ft{width:100%;border-collapse:collapse;font-size:10.3pt}
.form .ft th,.form .ft td{border:.8pt solid #333;padding:6.5pt 8pt;vertical-align:middle;line-height:1.5}
.form .ft th{background:#F2F2F2;font-weight:700;text-align:center;white-space:nowrap}
.form .ft td.c{text-align:center}
.form p.tx{margin-top:14pt;text-indent:10pt;text-align:justify}
.form .dt{text-align:center;margin-top:22pt;font-size:12pt;letter-spacing:.15em}
.form .to2{margin-top:30pt;text-align:center;font-size:13pt;font-weight:800;line-height:1.6;letter-spacing:.04em}
.form .sgx{display:flex;justify-content:center;align-items:center;gap:26pt;margin-top:20pt}
.form .sgx .ln{font-size:11.3pt;line-height:2.25}
.form .sgx .bx{width:80pt;height:80pt;border:1pt solid #333;position:relative;flex:none}
.form .sgx .bx i{position:absolute;left:0;right:0;top:6pt;text-align:center;font-style:normal;font-size:8.5pt;color:#777;line-height:1.25}
.form .sgx .bx b{position:absolute;left:0;right:0;top:44pt;text-align:center;font-weight:400;font-size:10pt;color:#999}
.form .warn{font-size:9pt;color:#444;margin-top:8pt;text-align:center}
.form .ft.r2 th,.form .ft.r2 td{padding:5pt 7pt;font-size:10pt}
.form .ft td.on{font-weight:800;background:#FFF6DC}
"""
CSS += r"""
/* 상주 협의회 소정 양식(docx) — 흑백 */
.sf{color:#111;font-size:11pt;line-height:1.8}
.sf .no{font-size:10pt;color:#333}
.sf h1{text-align:center;font-size:20pt;letter-spacing:.25em;color:#111;margin:10pt 0 14pt}
.sf .ft{width:100%;border-collapse:collapse;font-size:10.4pt}
.sf .ft th,.sf .ft td{border:.8pt solid #333;padding:6pt 9pt;vertical-align:middle;line-height:1.5}
.sf .ft th{background:#F2F2F2;font-weight:700;text-align:center;white-space:nowrap;width:22%}
.sf .ft td.c{text-align:center}
.sf .ft.g th{width:auto}.sf .ft.g td{text-align:center;padding:5pt 6pt;font-size:10pt}
.sf p.tx{margin-top:14pt;text-indent:10pt;text-align:justify;line-height:1.85}
.sf .dt{text-align:center;margin-top:20pt;font-size:12pt;letter-spacing:.15em}
.sf .sg{width:68%;margin:16pt auto 0;border-collapse:collapse;font-size:10.6pt}
.sf .sg th,.sf .sg td{border:.8pt solid #333;padding:6pt 10pt}
.sf .sg th{background:#F2F2F2;width:30%;text-align:center;font-weight:700}
.sf .sg td.sl{position:relative}
.sf .sg td.sl .ik{float:right;color:#555}
.sf span.mk{color:#fff;font-size:4pt}
.sf .to2{margin-top:22pt;text-align:center;font-size:13pt;font-weight:800;letter-spacing:.04em}
.sf .it{margin-top:8pt;line-height:1.75;font-size:10.6pt}
.sf .it p{margin-top:7pt;padding-left:14pt;text-indent:-14pt}
.sf .ck{font-weight:800}
.sf h3{font-size:11pt;margin:12pt 0 4pt}
.sf .nt{font-size:9pt;color:#333;margin-top:6pt;line-height:1.55}
.sf .seal2{display:grid;grid-template-columns:1fr 1fr;border:.8pt solid #333;border-top:0}
.sf .seal2 div{height:118pt;border-right:.8pt solid #333;display:flex;align-items:center;justify-content:center;position:relative}
.sf .seal2 div:last-child{border-right:0}
.sf .sgr{width:70%;margin:14pt 0 0 auto;font-size:11pt;line-height:2.2}
"""

HEAD = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{t}</title>'
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">'
        '<style>{css}</style></head><body>')


def doc(title, sections, css=CSS):
    return HEAD.format(t=e(title), css=css) + "".join(f'<section class="pg">{s}</section>' for s in sections) + "</body></html>"


def head(label, title, center=False):
    return (f'<div class="top"><div class="lb">{e(label)}</div><div class="co">{D.COMPANY} · 입주박람회 주관사 선정 입찰</div></div>'
            f'<h1 class="{"c" if center else ""}">{e(title)}</h1>'
            f'<div class="case" style="{"text-align:center" if center else ""}">건명 : {e(D.NOTICE)}</div>')


def ymd():
    return D.SIGN_DATE


def date_line():
    yy, mm, dd = ymd()
    return f'<div class="dt">{yy}년 &nbsp; {mm}월 &nbsp; {dd}일</div>'


def sign_box():
    """양식 꼬리: 업체명 · 대표자 (인감) · 사업자등록번호 표 → 귀하. 대표자 칸 = 사용인감(직인) 자리."""
    return (f'<table class="sg"><tr><th>업 체 명</th><td>{D.COMPANY}</td></tr>'
            f'<tr><th>대 표 자</th><td class="sl">대표이사 {D.CEO}<span class="ik">(인감)<span class="mk">(인감날인)</span></span></td></tr>'
            f'<tr><th>사업자등록번호</th><td>{D.BIZ_NO}</td></tr></table>'
            f'<div class="to2">{FORM_TO}</div>')


def chk(on, *labels):
    return " &nbsp;".join(f'<span class="ck">{"☑" if i == on else "□"}</span> {lb}' for i, lb in enumerate(labels))


# ================================================================== 1 · 입찰참가신청서(협의회 소정 양식)
def form_app():
    m = D.MANAGER
    body = f"""<div class="sf"><h1>입찰참가신청서</h1>
<table class="ft">
<tr><th>업 체 명</th><td>{D.COMPANY}</td></tr>
<tr><th>대 표 자</th><td>대표이사 {D.CEO}</td></tr>
<tr><th>사업자등록번호</th><td>{D.BIZ_NO}</td></tr>
<tr><th>법인등록번호</th><td>{D.CORP_NO}</td></tr>
<tr><th>본사 소재지</th><td>{D.ADDRESS}</td></tr>
<tr><th>설립(개업)일</th><td>{D.FOUNDED.replace('.', '. ')}.</td></tr>
<tr><th>상시 종업원 수</th><td>{STAFF_N} 명</td></tr>
<tr><th>전담 책임자(PM)</th><td>성명 : {m[0]} &nbsp;&nbsp;&nbsp;&nbsp; 직위 : {m[1]}</td></tr>
<tr><th>연 락 처</th><td>휴대전화 : {m[2]} &nbsp;&nbsp;&nbsp;&nbsp; 전자우편 : {D.EMAIL}</td></tr>
</table>
<p class="tx">당사는 「상주 자이르네 입주예정자협의회 입주박람회 주관사 선정 입찰 공고」의 내용을 모두 숙지하고 이에 동의하며, 위와 같이 입찰 참가를 신청합니다.</p>
{date_line()}
{sign_box()}</div>"""
    return doc("1 입찰참가신청서", [body])


# ================================================================== 4 · [별지1호] 이해관계 신고 및 청렴 서약서
def form1():
    no1 = chk(0, "없음", "있음 (내용 : &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; )")
    body = f"""<div class="sf"><div class="no">[별지1호]</div><h1 style="letter-spacing:.12em">이해관계 신고 및 청렴 서약서</h1>
<p class="tx" style="margin-top:4pt">당사는 상주 자이르네 입주예정자협의회 입주박람회 주관사 선정 입찰에 참가함에 있어 다음과 같이 신고하고 서약합니다.</p>
<div class="it">
<p>1. 본 단지 시행사 · 시공사 · 분양대행사 · 옵션업체와의 이해관계(하도급 · 협력업체 등록, 지분, 친인척 관계 등) : &nbsp;{no1}</p>
<p>2. 협의회 임원 및 그 가족과의 이해관계 : &nbsp;{no1}</p>
<p>3. 입찰부터 협약 이행까지 협의회 임원 · 운영위원 개인에게 금품이나 향응을 제공하지 않겠습니다.</p>
<p>4. 공동구매 품목의 판매를 이유로 단지의 기본 사양 개선을 방해하거나 시행사 · 시공사의 입장을 대변하지 않겠습니다.</p>
<p>5. 선정되지 않는 경우 상주 자이르네 입주예정자를 대상으로 별도의 박람회 · 공동구매를 하지 않으며, 입찰에 든 비용을 협의회에 청구하지 않겠습니다.</p>
<p>6. 위 내용이 사실과 다르거나 서약을 위반한 경우 선정 취소 및 협약 해지에 이의를 제기하지 않겠습니다.</p>
</div>
{date_line()}
{sign_box()}</div>"""
    return doc("4 별지1호 이해관계 신고 및 청렴 서약서", [body])


# ================================================================== 6 · [별지2호] 전담 책임자 및 분야별 전문가 명단
def form2():
    m = D.MANAGER
    rows = ""
    for i, (f_, kind, nm, lic, org) in enumerate(D.EXPERTS, 1):
        pv = PRIV.get("experts_sj", {}).get(f_, {})
        nm, lic = nm or pv.get("nm"), lic or pv.get("lic")
        if kind == "직접":
            nm_ = e(nm) if nm else todo("성명 — 본부장 확인")
            lic_ = e(lic) if lic else todo("자격 · 등록번호")
            org_ = e(org or D.COMPANY)
        else:
            nm_ = e(nm) if nm else todo("협력 계약 후 기재")
            lic_ = e(lic) if lic else todo("자격 · 등록번호")
            org_ = e(org) if org else todo("협력 법인")
        rows += (f'<tr><td>{i}</td><td>{f_}</td><td>{nm_}</td><td style="font-size:9.4pt">{lic_}</td><td style="font-size:9.4pt">{org_}</td>'
                 f'<td style="white-space:nowrap">{chk(0 if kind == "직접" else 1, "직접", "협력")}</td></tr>')
    rows += '<tr><td>7</td><td></td><td></td><td></td><td></td><td style="white-space:nowrap">□ 직접 &nbsp;□ 협력</td></tr>'
    body = f"""<div class="sf"><div class="no">[별지2호]</div><h1 style="letter-spacing:.1em;font-size:18pt">전담 책임자 및 분야별 전문가 명단</h1>
<h3>■ 전담 책임자</h3>
<table class="ft"><tr><th>성명 / 직위</th><td>{m[0]} / {m[1]}</td></tr>
<tr><th>경력 요약</th><td style="font-size:10pt">{e(D.PM_CAREER)}</td></tr></table>
<h3>■ 분야별 전문가 (건축 · 토목 · 조경 · 전기 · 기계설비 · 소방 등)</h3>
<table class="ft g"><tr><th style="width:7%">번호</th><th style="width:11%">분야</th><th style="width:17%">성명</th><th>자격(등록번호)</th><th style="width:19%">소속</th><th style="width:17%">고용 형태</th></tr>{rows}</table>
<p class="nt">※ 해당 분야 전문가가 없는 경우 빈칸으로 두되, 그 밖의 분야는 추가 기재 가능 / 자격증 사본 및 재직증명서 또는 협력 계약서 사본 첨부</p>
<p class="tx" style="margin-top:8pt">당사는 위 인력을 상주 자이르네 업무에 배치하며, 교체 시에는 협의회와 사전에 협의하겠습니다.</p>
{date_line().replace('margin-top:20pt', '')}
{sign_box()}</div>"""
    return doc("6 별지2호 전담 책임자 및 분야별 전문가 명단", [body])


def doc06_emp():
    """별지2호 사내 전문가 재직증명서 — 1인 1쪽 · 재직 시작 = 4대보험 명부 자격취득일."""
    yy, mm, dd = ymd()
    pages = []
    for nm, birth, field, lic, since in PRIV.get("emp_sj", []):
        pages.append(f"""<div class="top"><div class="lb">제출서류 6 · 별지2호 증빙</div><div class="co">{D.COMPANY}</div></div>
<h1 class="c" style="letter-spacing:.6em;font-size:24pt;margin-top:26pt">재 직 증 명 서</h1>
<table class="info" style="margin-top:26pt;font-size:10.6pt">
<tr><th>성 &nbsp; &nbsp; 명</th><td>{e(nm)}</td><th>출생 연도</th><td>{e(birth)}</td></tr>
<tr><th>소 &nbsp; &nbsp; 속</th><td>{D.COMPANY}</td><th>분 &nbsp; &nbsp; 야</th><td>{e(field)}</td></tr>
<tr><th>자 &nbsp; &nbsp; 격</th><td colspan="3">{e(lic)}</td></tr>
<tr><th>재직 기간</th><td colspan="3">{e(since)} ~ 현재</td></tr>
<tr><th>용 &nbsp; &nbsp; 도</th><td colspan="3">상주 자이르네 입주박람회 주관사 선정 입찰 · 별지2호 분야별 전문가 증빙</td></tr>
</table>
<p class="body" style="text-align:center;margin-top:34pt;font-size:12pt">위 사람은 현재 당사에 재직하고 있음을 증명합니다.</p>
<div class="sign" style="margin-top:40pt"><div class="d">{yy}년 {mm}월 {dd}일</div>
<div class="who" style="margin-top:14pt">{D.COMPANY}</div>
<div class="who" style="font-weight:400;font-size:11pt">{D.ADDRESS}</div>
<div class="who">대표이사 &nbsp; {D.CEO}<span class="seal">(인)</span></div></div>
<p class="note" style="margin-top:40pt">※ 재직 시작일 = 4대보험 사업장 가입자 명부(2026.10.23 발급 · 앞 쪽)의 자격취득일 · 자격증 · 경력증 사본은 뒤에 붙임 · 대표이사는 법인등기부(제출서류 2)로 갈음</p>""")
    return doc("6 재직증명서", pages) if pages else None


# ================================================================== 7 · [별지3호] 입주박람회 주관 실적 증명서
EVI = {  # 단지 → 증빙 번호(아래 doc07_cover · 증빙 묶음 순서와 같게)
    "e편한세상 에코델타 센터포인트": "A-1 · B-4", "부산 드파인 센텀": "A-2", "디에트르 더 퍼스트": "A-3",
    "영주자이 시그니처": "B-1", "창원 센트럴 아이파크": "B-2 · C", "에코델타 대성베르힐": "B-3",
    "두산위브더제니스 오션시티": "C", "레이카운티": "C",
}
CAPS7 = [  # (단지, 파일(assets_ins/), 출처, 기간, 장소)
    ("영주자이 시그니처", "cafe_yeongju.png", "입주자 공식 카페 ‘엣지컴퍼니 공지사항’ 게시판(입주민 닉네임 가림)", "2026.08.29 ~ 30", "영주 그랜드컨벤션"),
    ("창원 센트럴 아이파크", "ceco_changwon.png", "창원컨벤션센터(CECO) 공식 행사일정", "2026.07.03 ~ 05", "CECO 제2전시장"),
    ("에코델타 대성베르힐", "bx_daesung.png", "BEXCO 공식 행사일정", "2025.11.28 ~ 30", "BEXCO 제2전시장 4(D-F)홀"),
    ("e편한세상 에코델타 센터포인트", "bx_centerpoint.png", "BEXCO 공식 행사일정", "2025.02.14 ~ 16", "BEXCO 제2전시장 4E, F홀"),
]


def form3():
    rows = "".join(f'<tr><td>{i}</td><td style="font-size:9.6pt">{e(nm)}</td><td style="font-size:9.2pt">{e(loc)}</td><td>{n:,}</td>'
                   f'<td style="font-size:9.2pt">{e(when)}</td><td style="font-size:8.8pt">{e(who)}</td><td style="font-size:9pt">증빙 {EVI[nm]}</td></tr>'
                   for i, (nm, loc, n, when, who, _ev) in enumerate(D.SJ_REC, 1))
    body = f"""<div class="sf"><div class="no">[별지3호]</div><h1 style="letter-spacing:.12em;font-size:19pt">입주박람회 주관 실적 증명서</h1>
<h3>■ 공식 입주박람회 주관 실적 (해당 단지 협의회 · 입주자대표회의와 협약한 행사에 한함)</h3>
<table class="ft g"><tr><th style="width:6%">번호</th><th style="width:20%">단지명</th><th style="width:15%">소재지</th><th style="width:8%">세대수</th><th style="width:15%">행사기간</th><th>협약 상대</th><th style="width:10%">비고</th></tr>{rows}</table>
<p class="nt">※ 실적별 협약서 사본 등 증빙을 첨부하며, 증빙이 없는 실적은 인정하지 않음 &nbsp;→ 비고의 증빙 번호 = 뒤에 붙인 증빙(A 주관사 협약서 · B 공식 행사일정 · 카페 공지 · C NICE 기업신용평가 연혁)</p>
<p class="tx" style="text-align:center;text-indent:0;margin-top:12pt">위 실적이 사실과 다름없음을 확인합니다.</p>
{date_line().replace('margin-top:20pt', 'margin-top:10pt')}
{sign_box()}</div>"""
    return doc("7 별지3호 입주박람회 주관 실적 증명서", [body])


def doc07_cover():
    rows = ""
    for i, (nm, _loc, n, when, _who, ev) in enumerate(D.SJ_REC, 1):
        rows += (f'<tr><td>{i}</td><td class="l">{e(nm)}</td><td class="r">{n:,}</td><td>{e(when)}</td><td>{EVI[nm]}</td>'
                 f'<td class="l" style="font-size:8.4pt">{e(ev)}</td></tr>')
    body = f"""{head("제출서류 7 · 증빙", "별지3호 주관 실적 — 증빙 안내")}
<table class="t" style="margin-top:10pt;font-size:9pt"><thead><tr><th style="width:5%">No</th><th>단지명</th><th style="width:8%">세대수</th><th style="width:18%">행사기간</th><th style="width:11%">증빙 번호</th><th style="width:33%">증빙 내용</th></tr></thead>
<tbody>{rows}<tr class="sum"><td colspan="2">합계 {len(D.SJ_REC)}건 (별지3호와 같음)</td><td class="r">{sum(r[2] for r in D.SJ_REC):,}</td><td colspan="3"></td></tr></tbody></table>
<ol class="pl" style="margin-top:10pt">
<li class="sm">증빙 A. 주관사 협약서 사본 3건(협약일 순) — A-1 e편한세상 에코델타 센터포인트(2023.04.03) · A-2 부산 드파인 센텀(2023.12.20) · A-3 에코델타시티 디에트르 더퍼스트(2025.08.02) · 상대방 대표자 성명 · 연락처 · 계좌 가림</li>
<li class="sm">증빙 B. 공식 행사일정 · 입주자 카페 공지 캡처 — {" · ".join(f"B-{k} {e(c[0])}" for k, c in enumerate(CAPS7, 1))} · 주최 · 주관란 또는 공지 작성자 = 엣지컴퍼니</li>
<li class="sm">증빙 C. NICE디앤비 기업신용평가보고서(평가 {D.NICE_DATE}) ‘연혁’ 발췌 — 레이카운티 · 두산위브더제니스 오션시티 · 창원 센트럴 아이파크 주관 기재</li></ol>
<p class="note">※ 세대수 = NICE 연혁 기재값 · 단지 공식 세대수 · 레이카운티는 2차(2023.10.21 ~ 22) 행사. 협의회가 요청하면 협약서 원본 · 정산 자료 등을 지체 없이 추가 제출합니다.</p>
<p class="body" style="font-size:9.8pt;margin-top:8pt;line-height:1.65">위 증빙은 원본과 같으며, 실적이 사실과 다르면 공고 7항에 따라 선정 이후라도 협약 해지를 이의 없이 받아들이겠습니다.</p>
<div class="sign" style="margin-top:8pt"><div class="d">{ymd()[0]}년 {ymd()[1]}월 {ymd()[2]}일</div><div class="who">{D.COMPANY} &nbsp; 대표이사 &nbsp; {D.CEO}<span class="seal">(인)</span></div></div>"""
    return doc("7 증빙 안내", [body])


def doc07_caps():
    items = "".join(
        f'<div class="bxc"><div class="bh"><b>B-{k}</b> {e(nm)} <span>· {e(kind)} · {e(per)} · {e(hall)}</span></div>'
        f'<img src="../assets_ins/{f}" alt=""></div>' for k, (nm, f, kind, per, hall) in enumerate(CAPS7, 1))
    sec1 = (head("제출서류 7 · 증빙 B", "공식 행사일정 · 입주자 카페 공지 캡처")
            + '<p class="note" style="margin-top:4pt">출처: 단지 입주자 공식 카페 · 창원컨벤션센터(CECO) · 벡스코(BEXCO) 홈페이지 행사일정 화면 그대로(입주민 닉네임만 가림)</p>'
            + f'<div class="bxs">{items}</div>')
    css = CSS + (".bxs{display:flex;flex-direction:column;gap:8pt;margin-top:8pt}.bxc{border:1px solid #c9ced6;border-radius:3pt;padding:6pt 7pt;break-inside:avoid}"
                 ".bh{font-size:10pt;margin-bottom:4pt}.bh b{color:#9A7B3F;margin-right:4pt}.bh span{color:#555;font-size:8.8pt}"
                 ".bxc img{display:block;width:100%;max-height:92mm;object-fit:contain;object-position:left top}")
    return doc("7 증빙 B 공식 행사일정 · 카페 공지", [sec1], css)


# ================================================================== 5 · [별지4호] 사용인감계
def form4():
    yy, mm, dd = ymd()
    body = f"""<div class="sf"><div class="no">[별지4호]</div><h1 style="letter-spacing:.45em">사 용 인 감 계</h1>
<table class="ft"><tr><th>상호(법인명)</th><td>{D.COMPANY}</td></tr>
<tr><th>사업자등록번호</th><td>{D.BIZ_NO}</td></tr>
<tr><th>법인등록번호</th><td>{D.CORP_NO}</td></tr>
<tr><th>본점(사업장) 소재지</th><td>{D.ADDRESS}</td></tr>
<tr><th>대표자 성명</th><td>{D.CEO}</td></tr></table>
<table class="ft" style="border-top:0"><tr><th style="width:50%">사 용 인 감</th><th>법 인 인 감(개인사업자는 대표자 인감)</th></tr></table>
<div class="seal2"><div><span class="mk">(인감날인)</span></div><div></div></div>
<p class="tx">위 사용인감은 당사가 상주 자이르네 입주예정자협의회의 「입주박람회 주관사 선정 입찰」에 참가함에 있어 입찰참가신청서, [별지1호] ~ [별지3호] 등 입찰 관련 서류와 협약 체결에 관한 서류에 사용하는 인감임을 신고합니다.</p>
<p class="tx" style="margin-top:6pt">당사는 위 사용인감을 날인하여 행한 모든 행위에 대하여 법인인감(대표자 인감)을 날인하여 행한 것과 동일하게 일체의 책임을 지겠습니다.</p>
<div class="dt" style="margin-top:14pt">{yy}년 &nbsp; {mm}월 &nbsp; {dd}일</div>
<div class="sgr">신 고 인<br>상 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 호 : {D.COMPANY}<br>대 표 자 : 대표이사 {D.CEO} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; (인)</div>
<div class="to2" style="margin-top:12pt">상주 자이르네 입주예정자협의회 귀중</div>
<p class="nt" style="margin-top:10pt">※ 작성 안내 1. 사용인감 칸에는 입찰참가신청서 및 별지 서식에 날인한 인감을 날인합니다. 2. 법인인감 칸에는 인감증명서상의 인감을 날인하고, 대표자 (인) 란에도 같은 인감을 날인합니다. 3. 개인사업자는 법인인감 칸에 대표자 본인의 인감을 날인하며, 법인등록번호는 적지 않습니다. 4. 인감증명서(제출일 기준 3개월 이내 발급분)를 함께 제출합니다.</p></div>"""
    return doc("5 별지4호 사용인감계", [body])


# ================================================================== 8 · 회사소개서 표지 — 본문 = 업무 수행 제안서 01장 '회사소개'
def doc08_cover(pages_note):
    body = f"""<div style="height:240mm;display:flex;flex-direction:column;justify-content:space-between">
<div><div class="top"><div class="lb">제출서류 8</div><div class="co">{D.COMPANY}</div></div>
<div style="margin-top:70pt;font-size:12pt;letter-spacing:.3em;color:#9A7B3F;font-weight:700">COMPANY PROFILE</div>
<h1 style="font-size:34pt;letter-spacing:.25em;margin-top:8pt">회 사 소 개 서</h1>
<div style="font-size:15pt;font-weight:700;color:#0D1E33;margin-top:4pt">입주박람회 전문 주관사 · {D.COMPANY}</div>
<div style="width:60pt;height:3pt;background:#C8A86A;margin-top:18pt"></div>
<table class="t" style="margin-top:22pt;font-size:10pt"><tbody>
<tr><td class="k" style="width:24%">상호 · 대표</td><td class="l">{D.COMPANY} · 대표이사 {D.CEO}</td></tr>
<tr><td class="k">설립</td><td class="l">{D.FOUNDED} · 자본금 2억원 · NICE BB- · 현금흐름 A</td></tr>
<tr><td class="k">본사 · 연락처</td><td class="l">{D.ADDRESS} · 대표전화 {D.TEL} · {D.EMAIL}</td></tr>
<tr><td class="k">업종 · 등록</td><td class="l">전시 · 박람회 및 행사 대행업 · 광고대행업 · {D.ELEC_LICENSE} · ISO 9001 · 14001 · 45001</td></tr>
<tr><td class="k">주관 실적</td><td class="l">공식 입주박람회 주관 {len(D.SJ_REC)}건 · {sum(r[2] for r in D.SJ_REC):,}세대(별지3호) · 경북 북부 자이 단지 763세대 박람회 주관</td></tr>
</tbody></table>
<p class="note" style="margin-top:10pt">구성: {e(pages_note)} — 업무 수행 제안서(제출서류 9) 01장 ‘회사소개’와 같은 내용입니다.</p></div>
<div style="text-align:right;font-size:10pt;color:#5B6676">제출처 : 상주 자이르네 입주예정자협의회<br>2026.10</div></div>"""
    return doc("8 회사소개서", [body])


# ================================================================== 00 · 제출서류 목록(통합 PDF 맨 앞)
def doc00(spans):
    yy, mm, dd = ymd()
    rows = "".join(f'<tr><td>{no}</td><td class="l">{e(t)}</td><td class="l" style="font-size:8.6pt">{note}</td><td>{a}{"" if a == b else f" ~ {b}"}</td></tr>'
                   for no, t, note, a, b in spans)
    body = f"""{head("제출서류 목록", "입주박람회 주관사 선정 입찰 · 제출 서류 (공고 5항)")}
<table class="info" style="margin-top:10pt"><tr><th>입찰 참가</th><td>{D.COMPANY} · 대표이사 {D.CEO}</td><th>전담 책임자</th><td>{D.MANAGER[1]} {D.MANAGER[0]} · {D.MANAGER[2]}</td></tr>
<tr><th>접수</th><td colspan="3">{D.SUBMIT_TO} · 마감 {D.DEADLINE} · 제목 “{e(D.MAIL_TITLE)}”</td></tr></table>
<table class="t" style="margin-top:10pt"><thead><tr><th style="width:6%">No</th><th style="width:36%">제출 서류(공고 5항)</th><th>내용 · 발급일</th><th style="width:13%">이 파일 쪽</th></tr></thead><tbody>{rows}</tbody></table>
<p class="note" style="margin-top:8pt">※ 공고 5항 번호 순서대로 PDF 1개로 병합했습니다(PDF 책갈피 = 번호별). 납세증명서는 마감일 현재 유효기간 안, 법인인감증명서는 제출일 기준 3개월 안 발급분입니다.</p>
<p class="note">※ 입찰참가신청서 · 별지1 ~ 3호의 날인은 사용인감이며, 별지4호 사용인감계에 법인인감과 함께 신고했습니다. 4대보험 명부 · 인감증명서의 개인정보는 가렸습니다.</p>
<div class="sign" style="margin-top:14pt"><div class="d">{yy}년 {mm}월 {dd}일</div><div class="who">{D.COMPANY}</div></div>"""
    return doc("00 제출서류 목록", [body])


# ------------------------------------------------------------------ PDF · 날인 · 병합(북수원 docs_bs.py와 같은 방식)
GARBAGE = 3  # garbage=4는 크롬 PDF Type3 글꼴 글자가 빠지는 경우가 있음(분당 10-14 확인)


def out(name):
    return os.path.join(WORK, PFX + name)


def to_pdf(html_path, pdf_path):
    subprocess.run([find_chrome(), "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=8000", f"--print-to-pdf={pdf_path}", pathlib.Path(html_path).as_uri()],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def render(name, html_text):
    h = out(name + ".html")
    pathlib.Path(h).write_text(html_text, encoding="utf-8")
    p = h[:-5] + ".pdf"
    to_pdf(h, p)
    return p


def page_texts(d_or_path):
    d = d_or_path if isinstance(d_or_path, fitz.Document) else fitz.open(d_or_path)
    return [p.get_text() for p in d]


def seal_image(path, px=360):
    """직인 PNG — 배경 투명(알파 있음)이면 그대로, 흰 배경이면 stamp.seal_png로 투명 처리. 360px로 줄여 용량을 줄인다."""
    from PIL import Image
    import stamp as ST_
    im = Image.open(path)
    raw = open(path, "rb").read() if (im.mode == "RGBA" and im.getextrema()[3][0] == 0) else ST_.seal_png(path)
    im = Image.open(io.BytesIO(raw))
    im.thumbnail((px, px), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return buf.getvalue()


def stamp(seal, pdf_path):
    """'(인)' 가운데에 직인(54pt) — 저장 garbage=3 · 글자 대조."""
    import stamp as ST_
    d = fitz.open(pdf_path)
    before = page_texts(d)
    n = 0
    for page in d:
        for mark in ST_.MARKS:
            hits = page.search_for(mark)
            if not hits:
                continue
            for r in hits:
                c = fitz.Point((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2)
                s = ST_.SIZE / 2
                page.insert_image(fitz.Rect(c.x - s, c.y - s, c.x + s, c.y + s), stream=seal, overlay=True)
                n += 1
            break
    o = pdf_path[:-4] + "_직인.pdf"
    d.save(o, garbage=GARBAGE, deflate=True)
    assert page_texts(o) == before, f"날인 뒤 글자가 달라짐: {o}"
    return o, n


def fit(path, lo, hi=None):
    k = len(fitz.open(path))
    assert lo <= k <= (hi or lo), f"{os.path.basename(path)}: {k}쪽(예상 {lo}{'' if hi is None else f' ~ {hi}'}쪽) — 내용이 넘침"
    return path


# 증빙 C — NICE 원본 9쪽 연혁 발췌(고양 docs_gy.annex_nice와 같은 방식)
FONTS = os.path.join(HERE, "..", "통합제안서", "fonts")
NAVY, GOLD, GRAY, LINE = (0.051, 0.118, 0.2), (0.78, 0.66, 0.42), (0.36, 0.4, 0.46), (0.79, 0.81, 0.84)
CLIP_TITLE = fitz.Rect(0, 0, 595, 76)
CLIP_HIST = fitz.Rect(36, 321, 560, 511)
ROWS_RECENT = (398, 506)     # 연혁 표 중 입주박람회 주관 6행(2023/11 ~ 2026/07)
CLIP_FOOT = fitz.Rect(36, 800, 560, 828)


def annex_nice(nice_path, out_path):
    nice = fitz.open(nice_path)
    o = fitz.open()
    pg = o.new_page(width=595.28, height=841.89)
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
    text(L + 23, 51.5, "증빙 C", 8.5, "b", GOLD, "c")
    text(R, 51.5, "제출서류 7 · 별지3호 주관 실적 증빙", 8.5, "r", GRAY, "r")
    pg.draw_line((L, 64), (R, 64), color=NAVY, width=2)
    text(L, 92, "NICE디앤비 기업신용평가보고서 ‘연혁’ 발췌", 17, "b")
    text(L, 110, f"건명 : {D.NOTICE}", 8.8, "r", GRAY)
    top = 126
    cover = fitz.Rect(L, top, L + 168, top + 168 * 842 / 595)
    pg.show_pdf_page(cover, nice, 0)
    pg.draw_rect(cover, color=LINE, width=0.6)
    info = [("보고서명", "CLIP 기업신용평가보고서"), ("발행 기관", "NICE디앤비 (dun & bradstreet)"),
            ("평가 대상", f"{D.COMPANY} ({D.BIZ_NO})"), ("관리번호", "11125949-202605-001"),
            ("평가완료일", D.NICE_DATE), ("발췌 범위", "9쪽 ‘04 영업 현황(기업개요)’ 중 ‘연혁’"),
            ("원본 분량", f"전 {len(nice)}쪽 (요청 시 전문 제출)")]
    x0, x1, xk, rh = L + 186, R, L + 186 + 70, 24
    for i, (k, v) in enumerate(info):
        y = top + i * rh
        pg.draw_rect(fitz.Rect(x0, y, xk, y + rh), color=LINE, fill=(0.945, 0.929, 0.894), width=0.6)
        pg.draw_rect(fitz.Rect(xk, y, x1, y + rh), color=LINE, width=0.6)
        text(x0 + 8, y + 15.5, k, 8.8, "b")
        text(xk + 8, y + 15.5, v, 8.8, "r", (0.1, 0.14, 0.2))
    y = top + len(info) * rh + 18
    text(x0, y, "금색 테두리 = 입주박람회 주관 기재 6행", 8.8, "r", GRAY)
    text(x0, y + 13, "(별지3호: 레이카운티 · 오션시티 · 창원)", 8.8, "r", GRAY)
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
    yy, mm, dd = ymd()
    text((L + R) / 2, y + 26, f"{yy}년 {mm}월 {dd}일", 10, "r", (0.1, 0.14, 0.2), "c")
    who = f"{D.COMPANY}   대표이사   {D.CEO}"
    text((L + R) / 2 - 14, y + 52, who, 11, "b", NAVY, "c")
    sx = (L + R) / 2 - 14 + F["b"].text_length(who, fontsize=11) / 2 + 30
    text(sx, y + 52, "(인)", 10, "r", GRAY)
    o.set_metadata({"title": "증빙 C NICE 기업신용평가보고서 연혁 발췌", "author": D.COMPANY})
    o.save(out_path, garbage=GARBAGE, deflate=True)
    return out_path


def relabel(src, dst, old, new, title=None):
    """협약서 사본 머리글(고양 '제출서류 9 · 별첨 3-k') → 상주 '제출서류 7 · 증빙 A-k' — 머리글 글자만 지우고 새로 쓴다(본문 이미지는 그대로)."""
    d = fitz.open(src)
    F = fitz.Font(fontfile=os.path.join(FONTS, "Pretendard-Bold.ttf"))
    for i, pg in enumerate(d):
        hits = pg.search_for(old)
        assert len(hits) == 1, (i, old, hits)
        r = hits[0]
        full = pg.search_for(old + f"-{i + 1} (협약일 순)")
        rr = full[0] if full else r
        pg.add_redact_annot(fitz.Rect(rr.x0 - 1, rr.y0 - 1, rr.x1 + 1, rr.y1 + 1), fill=(1, 1, 1))
        pg.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
        tw = fitz.TextWriter(pg.rect)
        tw.append((rr.x0, rr.y1 - 2.2), new.format(k=i + 1), font=F, fontsize=round(rr.height * 0.72, 1))
        tw.write_text(pg, color=(0.6, 0.48, 0.25))
        if title:  # 제목은 이미지에 박혀 있음(고양 '최근 3년 500세대 이상 …') → 흰 판으로 덮고 상주 제목을 쓴다(아래 금선은 그대로)
            pg.draw_rect(fitz.Rect(40, 52.5, 560, 76.5), color=None, fill=(1, 1, 1), overlay=True)
            tw = fitz.TextWriter(pg.rect)
            tw.append((43, 71), title, font=F, fontsize=16)
            tw.write_text(pg, color=(0.051, 0.118, 0.2))
    d.save(dst, garbage=GARBAGE, deflate=True)
    return dst


def ch01_pages(pdf):
    """제안서 01장(간지 + '0 1 . 회사소개' 쪽)과 마지막 연락처 쪽 — 지명원 본문."""
    d = fitz.open(pdf)
    idx = [i for i, p in enumerate(d) if "0 1 . 회사소개" in p.get_text()[:200]]
    assert idx and idx == list(range(idx[0], idx[-1] + 1)), idx
    return list(range(idx[0] - 1, idx[-1] + 1)) + [len(d) - 1]


def staff_n():
    return 13   # 상시 종업원 수 = 4대보험 사업장 가입자 명부(2026.10.23) 13명 — 같은 명부를 제출서류 6에 붙임


STAFF_N = staff_n()


def evidence_check():
    t = fitz.open(f"{EV}/사업자등록증.pdf")[0].get_text()
    assert "2026 년10 월14 일" in t and "전시,박람회및행사대행업" in t, "사업자등록증 발급일 · 종목 확인 실패"
    t = fitz.open(f"{EV}/국세_납세증명서.pdf")[0].get_text()
    assert "2026 년10 월14 일" in t and "2026 년11 월13 일" in t, "국세 납세증명서 발급일 · 유효기간 확인 실패"
    assert len(fitz.open(ROSTER)) == 2, "4대보험 가입자 명부(2026.10.23 · 가림본) 2쪽 확인 실패"
    assert len(fitz.open(R500_DOC)) == 3, "주관사 협약서 3건 확인 실패"
    for p in (f"{EV}/법인등기부등본.pdf", f"{EV}/지방세_납세증명서.pdf", f"{EV}/법인인감증명서.pdf", f"{EV}/전기공사업_등록증.pdf", NICE_SRC, P09):
        assert os.path.exists(p), f"없음: {p}"
    for c in CAPS7:
        assert os.path.exists(os.path.join(HERE, "assets_ins", c[1])), c[1]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    final = "--final" in sys.argv
    if not args:
        sys.exit(__doc__)
    evidence_check()
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(SUBMIT, exist_ok=True)
    seal = seal_image(args[0])

    def stamped(p, n_expect=1):
        o, n = stamp(seal, p)
        assert n == n_expect, f"날인 자리 {n}곳(예상 {n_expect}): {p}"
        return o

    # ---- 서식(사용인감 = 직인) · 사용인감계 출력용
    f_app = stamped(fit(render("1_입찰참가신청서", form_app()), 1))
    f1 = stamped(fit(render("4_별지1호_이해관계신고_청렴서약서", form1()), 1))
    f2 = stamped(fit(render("6_1_별지2호_전담책임자_전문가명단", form2()), 1))
    f3 = stamped(fit(render("7_1_별지3호_주관실적증명서", form3()), 1))
    if TODOS:
        print("[노란 칸]", " / ".join(dict.fromkeys(TODOS)))
        if final:
            sys.exit("--final: 노란 칸이 남아 있어 멈춤")
    gam_print = out("5_2_별지4호_사용인감계_출력용.pdf")   # 사용인감 칸에만 디지털 직인 — 이 파일만 출력해 법인인감 실물 날인
    os.replace(stamped(fit(render("5_2_별지4호_사용인감계_직인전", form4()), 1)), gam_print)
    have_scan = os.path.exists(SEAL_SCAN)
    if have_scan:
        assert len(fitz.open(SEAL_SCAN)) == 1, f"사용인감계 스캔은 1쪽이어야 함: {SEAL_SCAN}"
    gam = SEAL_SCAN if have_scan else gam_print
    biz = fitz.open(f"{EV}/사업자등록증.pdf")
    for pg_ in biz:
        for a in list(pg_.annots()):  # 발급 뒤 덧붙인 스탬프 주석이 원본 칸을 가리지 않게
            pg_.delete_annot(a)
    biz_p = out("2_1_사업자등록증.pdf")
    biz.save(biz_p, garbage=GARBAGE, deflate=True)
    c7 = stamped(fit(render("7_2_증빙안내", doc07_cover()), 1))
    a7 = relabel(R500_DOC, out("7_3_증빙A_주관사협약서.pdf"), "제출서류 9 · 별첨 3", "제출서류 7 · 증빙 A-{k} (협약일 순)", "공식 입주박람회 주관 실적 — 주관사 협약서 사본")
    b7 = fit(render("7_4_증빙B_행사일정_카페공지", doc07_caps()), 1, 2)
    n7 = stamped(annex_nice(NICE_SRC, out("7_5_증빙C_NICE연혁발췌.pdf")))
    ch = ch01_pages(P09)
    c8 = fit(render("8_1_회사소개서_표지", doc08_cover(f"표지 + 회사소개 {len(ch)}쪽(숫자 · 연혁 · 법인 서류 · 인증 · 대표자 · 조직 · 본사 관리 · 현장 체계 · 실적 · 추천과 협약 · 연락처)")), 1)
    ex6 = sorted(os.path.join(EXPERT_DIR, f) for f in (os.listdir(EXPERT_DIR) if os.path.isdir(EXPERT_DIR) else []) if f.lower().endswith(".pdf"))
    emp_html = doc06_emp()
    emp6 = stamped(fit(render("6_4_재직증명서_전문가", emp_html), len(PRIV["emp_sj"])), len(PRIV["emp_sj"])) if emp_html else None

    items = [  # (번호, 이름, 내용, [(pdf, 쪽 목록 또는 None, 책갈피)])
        ("1", "입찰참가신청서 (협의회 소정 양식)", "사용인감 날인", [(f_app, None, None)]),
        ("2", "사업자등록증 사본 · 법인등기부등본", f"사업자등록증 {D.ISSUE['biz']} · 등기부등본 {D.ISSUE['reg']} 발급",
         [(biz_p, None, "사업자등록증"), (f"{EV}/법인등기부등본.pdf", None, "법인등기부등본")]),
        ("3", "국세 · 지방세 납세증명서", f"국세 {D.ISSUE['tax']} · 지방세 {D.ISSUE['ltax']} 발급 · 유효 ~2026.11.13(마감일 현재 유효)",
         [(f"{EV}/국세_납세증명서.pdf", None, "국세 납세증명서"), (f"{EV}/지방세_납세증명서.pdf", None, "지방세 납세증명서")]),
        ("4", "[별지1호] 이해관계 신고 및 청렴 서약서", "1 · 2항 없음 · 사용인감 날인", [(f1, None, None)]),
        ("5", "인감증명서 · [별지4호] 사용인감계", f"법인인감증명서 {D.INGAM_DATE} 발급(주민번호 뒷자리 가림) · 사용인감계"
         + ("(법인인감 날인)" if have_scan else " — " + todo("법인인감 실물 날인 스캔 교체 전")),
         [(f"{EV}/법인인감증명서.pdf", None, "법인인감증명서"), (gam, None, "별지4호 사용인감계")]),
        ("6", "[별지2호] 전담 책임자 및 분야별 전문가 명단", "전담 책임자 · 6개 분야 · 증빙: 전기공사업 등록증 · 4대보험 가입자 명부"
         + (f" · 재직증명서 {len(PRIV.get('emp_sj', []))} · 자격증 사본 {len(ex6)}건" if ex6 else " — " + todo("자격증 사본 · 협력 계약서 첨부 대기")),
         [(f2, None, "별지2호 명단"), (f"{EV}/전기공사업_등록증.pdf", None, "전기공사업 등록증(전기 · 직접)"), (ROSTER, None, "4대보험 사업장 가입자 명부(재직 · 가림)")]
         + ([(emp6, None, "재직증명서(사내 전문가)")] if emp6 else [])
         + [(p, None, os.path.splitext(os.path.basename(p))[0]) for p in ex6]),
        ("7", "[별지3호] 입주박람회 주관 실적 증명서", f"{len(D.SJ_REC)}건 · {sum(r[2] for r in D.SJ_REC):,}세대 · 증빙 A 협약서 3 · B 행사일정 · 카페 공지 4 · C NICE 연혁",
         [(f3, None, "별지3호 실적 증명서"), (c7, None, "증빙 안내"), (a7, None, "증빙 A 주관사 협약서"), (b7, None, "증빙 B 행사일정 · 카페 공지"), (n7, None, "증빙 C NICE 연혁 발췌")]),
        ("8", "회사소개서", f"표지 + 업무 수행 제안서 01장 회사소개 {len(ch)}쪽", [(c8, None, "표지"), (P09, ch, "회사소개")]),
        ("9", "업무 수행 제안서", f"{len(fitz.open(P09))}쪽 · ① 시공 단계 품질 · 하자 예방 ② 입주 준비 ③ 박람회(업체 선정 · 가격 검증) ④ A/S · 민원 ⑤ 협의회 지원",
         [(P09, None, None)]),
    ]
    spans, toc, pg0 = [], [], 2
    for no, name, note, parts in items:
        n = sum(len(pl) if pl else len(fitz.open(p)) for p, pl, _ in parts)
        spans.append((no, name, note, pg0, pg0 + n - 1))
        pg0 += n
    p00 = fit(render("00_제출서류목록", doc00(spans)), 1)
    o = fitz.open()
    o.insert_pdf(fitz.open(p00))
    toc.append([1, "제출서류 목록", 1])
    docs = {}
    src_txt = page_texts(p00)
    for (no, name, note, parts), (_n, _nm, _no, a, _b) in zip(items, spans):
        toc.append([1, f"{no}. {name}", a])
        pg = a
        for p, pl, bm in parts:
            d = docs.setdefault(p, fitz.open(p))
            sel = pl if pl else list(range(len(d)))
            if bm:
                toc.append([2, bm, pg])
            runs, cur = [], [sel[0]]
            for i in sel[1:]:  # 연속 구간은 한 번에(쪽마다 넣으면 글꼴 · 사진이 쪽 수만큼 복제돼 느려짐)
                if i == cur[-1] + 1:
                    cur.append(i)
                else:
                    runs.append(cur)
                    cur = [i]
            runs.append(cur)
            for r in runs:
                o.insert_pdf(d, from_page=r[0], to_page=r[-1])
            src_txt += [d[i].get_text() for i in sel]
            pg += len(sel)
    o.set_toc(toc)
    o.set_metadata({"title": f"{D.COMPANY} · {SITE} 입주박람회 주관사 선정 입찰 서류 1 ~ 9", "author": D.COMPANY})
    for f in os.listdir(SUBMIT):
        if f.endswith(".pdf"):
            os.remove(os.path.join(SUBMIT, f))
    name = D.FILE_NAME if (have_scan and not TODOS) else D.FILE_NAME[:-4] + "_직인본.pdf"
    path = os.path.join(SUBMIT, name)
    o.save(path, garbage=GARBAGE, deflate=True, deflate_fonts=True, deflate_images=True, use_objstms=1)
    bad = [i + 1 for i, (x, y) in enumerate(zip(src_txt, page_texts(path))) if x != y]
    assert not bad, f"합친 뒤 글자가 달라진 쪽 {bad[:10]}"
    assert len(fitz.open(path)) == pg0 - 1
    mb = os.path.getsize(path) / 1e6
    lines = [f"[제출 현황 · 내부용 — 첨부 금지] {SITE} · 접수 {D.SUBMIT_TO} · 제목 {D.MAIL_TITLE} · 파일명 {D.FILE_NAME} · 마감 {D.DEADLINE}", ""]
    for no, nm, note, a, b in spans:
        lines.append(f"{no:>2}. {nm} — p.{a}" + ("" if a == b else f" ~ {b}") + " · " + note.replace('<mark class="todo">', "[").replace("</mark>", "]"))
    lines += ["", f"통합본: {path}  {len(fitz.open(path))}쪽 · {mb:.1f}MB"]
    if not have_scan:
        lines += ["", f"조치: 별지4호 사용인감계 — 작업/{PFX}5_2_별지4호_사용인감계_출력용.pdf(1쪽) 출력 → 법인인감 칸 · 신고인 (인)에 법인인감 날인 → 스캔(1쪽 PDF) → {SEAL_SCAN} 에 두고 다시 실행"]
    if TODOS:
        lines += ["", "노란 칸(본부장 확인): " + " / ".join(dict.fromkeys(TODOS)), f"별지2호 증빙(자격증 사본 · 재직증명서 · 협력 계약서) PDF → {EXPERT_DIR}/ 에 두고 data.EXPERTS 성명 · 자격 · 소속을 채운 뒤 다시 실행"]
    text = "\n".join(lines) + "\n"
    pathlib.Path(WORK, "제출현황.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
