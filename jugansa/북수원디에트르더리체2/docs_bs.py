# -*- coding: utf-8 -*-
"""북수원 이목지구 디에트르 더리체2차 입주박람회 주관사 제안 — 제안지침서 제4조 제출서류 생성기(A4 세로) · PDF 1개 병합.

제4조: 아래 서류를 번호 순서대로 PDF 1개로 병합해 이메일(theriche222@gmail.com) 제출. 발행일 1개월 이내(계획서 · 지명원 · 환불 규정 제외).
  00 제출서류 목록(표지 · 쪽 번호)                      — 통합 PDF 맨 앞(안내용)
  1  참가신청서 [별지 1] · 확약서 [별지 2] · 청렴이행각서 [별지 3]
  2  적격심사 자기평가서 [별지 5] · 입주박람회 운영 실적표 [별지 4]   (별지 5의 4번 = 별지 4와 같은 값 · data.BS_REC · SELF_EVAL)
  3  사업자등록증 · 법인등기부등본(2026.10.14 발급)
  4  입주박람회 운영계획서 = build_bs.py 제안서
  5  이행보증보험증권 발급 가능 확인 · 행사배상책임보험 가입 확약서(자체) + SGI 계약보증보험증권 발급 이력(가림본) + KB 영업배상책임보험(본사 시설 · 참고)
  6  신용평가등급 확인서 = NICE디앤비 기업신용평가보고서(표지 + 전문 · 대표 외 임직원 생년월일 가림)
  7  4대보험 사업장 가입자 명부(2026.10.02 · 성명 · 주민번호 가림) + 재직증명서(현장 책임자)
  8  국세 · 지방세 완납 증명서(2026.10.14 발급)
  9  1,000세대 이상 수행 실적 증빙 — 안내 + 별첨 1 NICE 연혁 발췌 · 별첨 2 실적 확약서(붙임 캡처 3) · 별첨 3 박람회장 공식 행사일정(대성 · 창원)
  10 지명원(회사소개서) = 표지 + 제안서 01장 '회사소개'
  11 계약금 환불 규정(제1 ~ 10조 · 별표)

날인: 별지 1 ~ 5는 '직인 또는 인감' 칸 + '※ 반드시 법인 인감 날인 요망' → 법인인감은 디지털로 만들지 않는다.
  - 작업/ '별지1-5_법인인감_날인출력용.pdf'(5쪽)를 출력 → 법인인감 날인 → 스캔해 data.SEAL_SCAN 경로에 두면 그 스캔으로 바꿔 '최종본'을 만든다.
  - 스캔이 없으면 별지에도 직인(투명 PNG)을 찍은 '_직인본'을 만든다(내용 확인용 · 제출 전 법인인감 스캔 교체 권장).
  - 그 밖의 자체 서류(5 · 7 재직증명서 · 9 · 10 · 11)는 직인.
출력: 작업/ = 중간 파일 · 제출본/ = 통합 PDF 1개(메일용 저용량본은 만들지 않음 — 본부장 10-20) · 제출현황.txt(내부용 — 첨부 금지)
사용: python docs_bs.py <투명 직인.png> [--final]    (결과 PDF · HTML은 깃 제외 — .gitignore)
"""
import html
import importlib.util
import io
import json
import os
import pathlib
import shutil
import subprocess
import sys

import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "요약제안서"), os.path.join(HERE, "..", "동탄파라곤3차")]
import data as D  # noqa: E402
from build import find_chrome  # noqa: E402

e = html.escape
PFX = "엣지컴퍼니_북수원디에트르더리체2_"
ST = D.SITE
SITE = ST["name"]
FORM_TO = "북수원 이목지구 디에트르 더리체2차 입주예정자협의회"   # 별지 원문 표기
CASE = "북수원 이목지구 디에트르 더리체2차 입주박람회 주관사 선정"   # 별지 2 · 3 건명
TODOS = []

SP = "/tmp/claude-0/-home-user-edge-company/a96d9eb6-5244-5d3f-9f1b-6f379ac2a82c/scratchpad"
EV = os.environ.get("BS_EVIDENCE", f"{SP}/evidence")  # 증빙 원본(깃 제외)
KB = f"{EV}/KB_영업배상책임보험_시설소유관리자_20261014.pdf"
NICE_SRC = f"{EV}/NICE_기업신용평가.pdf"
ROSTER = f"{SP}/cs_sub/엣지컴퍼니_철산역자이_06_4대보험_사업장가입자명부.pdf"   # 2026.10.02 발급 · 성명 가운데 글자 · 주민번호 뒷자리 가림본(철산 06 · 지웰 07과 같은 파일)
SGI_IMG = os.path.join(HERE, "assets_ins", "os_sgi_bond_masked.png")   # SGI 계약보증보험증권 1쪽 — 상대방 · 보험료 · 증권번호 뒷자리 · 가입금액 가림
CAP_DIR = f"{SP}/hw/cap"
WORK = os.path.join(HERE, "작업")
SUBMIT = os.path.join(HERE, "제출본")
P04 = os.path.join(HERE, PFX + "입주박람회_주관사_제안서_밝은시안.pdf")  # 본부장 10-21: 제출본 = 밝은 버전(tools/light_build.py)
INGAM = f"{EV}/법인인감증명서.pdf"   # 기존 법인인감증명서(D.INGAM_DATE 발급 · 주민번호 뒷자리 가림본) — 본부장 10-20 '기존 것 사용'
SEAL_SCAN = getattr(D, "SEAL_SCAN", None) or f"{SP}/seal_scan/북수원_별지1-5_법인인감.pdf"   # 별지 1 ~ 5 법인인감 날인 스캔(5쪽 · 순서 = 별지 1 · 2 · 3 · 5 · 4)

_priv = os.path.join(HERE, "org_private.json")  # 깃 제외(생년월일 · 실명)
PRIV = json.load(open(_priv, encoding="utf-8")) if os.path.exists(_priv) else {}
CEO_BIRTH = D.CEO_BIRTH or PRIV.get("ceo_birth")
MGR_BIRTH = D.MGR_BIRTH or PRIV.get("mgr_birth")
MGR_JOIN = getattr(D, "MGR_JOIN", "2026.09.28")   # 현장 책임자(주관사업 총괄 본부장) 입사일 — 본부장 확인값(10-19 메모)


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

HEAD = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{t}</title>'
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">'
        '<style>{css}</style></head><body>')


def doc(title, sections, css=CSS):
    return HEAD.format(t=e(title), css=css) + "".join(f'<section class="pg">{s}</section>' for s in sections) + "</body></html>"


def head(label, title, center=False):
    return (f'<div class="top"><div class="lb">{e(label)}</div><div class="co">{D.COMPANY} · 입주박람회 주관사 제안</div></div>'
            f'<h1 class="{"c" if center else ""}">{e(title)}</h1>'
            f'<div class="case" style="{"text-align:center" if center else ""}">건명 : {e(D.NOTICE)}</div>')


def ymd():
    return D.SIGN_DATE


def sign(to=True):
    yy, mm, dd = ymd()
    return (f'<div class="sign"><div class="d">{yy}년 {mm}월 {dd}일</div>'
            f'<div class="who">{D.COMPANY} &nbsp; 대표이사 &nbsp; {D.CEO}<span class="seal">(인)</span></div></div>'
            + (f'<div class="to">{FORM_TO} 귀 중</div>' if to else ""))


def seal_tail(top=20):
    """별지 1 ~ 5 꼬리(원문): 법인명 · 주소 · 대표자 + '직인 또는 인감' 칸 → 법인 인감 안내 → 날짜 → 귀 중."""
    yy, mm, dd = ymd()
    return (f'<div class="sgx" style="margin-top:{top}pt"><div class="ln">법인명 : <b>{D.COMPANY}</b><br>주 &nbsp;소 : {D.ADDRESS}<br>대표자 : <b>대표이사 {D.CEO}</b></div>'
            f'<div class="bx"><i>직 인<br>또는<br>인 감</i><b>(인)</b></div></div>'
            '<div class="warn">※ 반드시 법인 인감 날인 요망. 요건 불충족 시 제안 참가 불가함.</div>'
            f'<div class="dt">{yy}년 &nbsp; {mm}월 &nbsp; {dd}일</div>'
            f'<div class="to2">{FORM_TO} 귀 중</div>')


def birth(v, who):
    return e(v) if v else todo(f"{who} 생년월일 — 본부장님 확인")


# ================================================================== 1 · [별지 1] 제안 참가 신청서
def form1():
    m = D.MANAGER
    body = f"""<div class="form"><div class="no">[별지서식1]</div><h1>제안 참가 신청서</h1>
<table class="ft">
<tr><th>사 업 명</th><td colspan="4">북수원 이목지구 디에트르 더리체2차<br>입주예정자협의회 입주박람회 주관사 선정</td></tr>
<tr><th rowspan="5">신청기관</th><th>법 &nbsp; 인 &nbsp; 명</th><td colspan="3">{D.COMPANY}</td></tr>
<tr><th>대 표 자 명</th><td colspan="3">대표이사 {D.CEO}</td></tr>
<tr><th>사업자등록번호</th><td colspan="3">{D.BIZ_NO}</td></tr>
<tr><th>법인등록번호</th><td colspan="3">{D.CORP_NO}</td></tr>
<tr><th>주 &nbsp; &nbsp; &nbsp; 소</th><td colspan="3">{D.ADDRESS}</td></tr>
<tr><th rowspan="4">책임자</th><th>성 &nbsp; &nbsp; &nbsp; 명</th><td>{m[0]}</td><th>생년월일</th><td>{birth(MGR_BIRTH, "책임자")}</td></tr>
<tr><th>부 &nbsp; &nbsp; &nbsp; 서</th><td>주관사업</td><th>휴대전화</th><td>{m[2]}</td></tr>
<tr><th>직 &nbsp; &nbsp; &nbsp; 위</th><td>총괄 본부장</td><th>전 &nbsp; &nbsp; 화</th><td>{D.TEL}</td></tr>
<tr><th>전자메일(E-mail)</th><td>{D.EMAIL}</td><th>F A X</th><td>없음</td></tr>
</table>
<p class="tx">본 업체는 “입주박람회 기획·운영 및 협력업체 유치·관리, 입주지원 등 업무협약” 제안에 참여하고자 “{FORM_TO}”에서 정한 제안요청사항을 모두 승낙하고 제출서류를 첨부하여 입주박람회 주관 업무를 성실히 수행하고자 본 제안서를 제출합니다.</p>
{seal_tail(18)}</div>"""
    return doc("1 제안 참가 신청서 [별지 1]", [body])


# ================================================================== 1 · [별지 2] 확약서
def form2():
    paras = [
        f"본 업체(제안사)는 {FORM_TO} 입주박람회 주관사 선정 입찰에 참여함에 있어, 귀 협의회의 협약대상자 선정 방식 및 공고문 내용과 본 입찰에 관련된 귀 협의회의 방침에 이의가 없음을 확약하며, 아래의 내용을 준수하고 이행할 것임을 엄숙히 서약합니다.",
        "본 제안 참여와 관련하여 제출된 모든 증빙 자료는 신의성실의 원칙에 입각하여 진실하게 작성하였으며, 귀 협의회의 제안서 평가 및 협상 결과 등에 대하여 어떠한 이의도 제기하지 않겠습니다.",
        "협약대상자(주관사)로 선정될 경우, 주관 업무의 전부 또는 일부를 어떠한 형태로든 타사(타인)에 도급(재하도급, 재하청) 또는 양도하지 않으며, 협약 체결 이후라도 이러한 사실이 적발될 경우 즉시 협약이 해지됨을 감수하고 이에 대해 민·형사상 어떠한 이의도 제기하지 않겠습니다.",
        "북수원 이목지구 디에트르 더 리체 2 입주예정자협의회가 평가를 위해 구성한 평가 임원진과 평가 방법 및 기준에 따른 최종 결과에 절대 승복하며, 협약대상자 선정 전까지 귀 협의회의 추가 요청 내용과 협약 체결에 따른 증빙 서류 제출 등 제반 유의사항을 철저히 준수할 것을 확약합니다.",
    ]
    body = f"""<div class="form"><div class="no">[별지서식2]</div><h1 style="letter-spacing:.6em">확 약 서</h1>
<div class="cs">&lt;건명: {CASE}&gt;</div>
{"".join(f'<p class="tx" style="margin-top:9pt">{x}</p>' for x in paras)}
{seal_tail(26)}</div>"""
    return doc("1 확약서 [별지 2]", [body])


# ================================================================== 1 · [별지 3] 청렴이행각서
def form3():
    paras = [
        f"본 업체(제안사)는 {FORM_TO}에서 시행하는 「입주박람회 주관사 선정」 입찰에 참여함에 있어, 입주박람회 기획·운영, 협력업체 유치·관리, 사후 A/S·민원 대응 및 입주지원 등(입찰 공고문 및 지침서에 포함된 업무 일체)의 협약 사항을 성실히 이행할 것입니다.",
        "만일 당사의 귀책사유가 발생할 경우 전적으로 당사가 책임질 것이며, 이에 대해 어떠한 이의도 제기하지 않을 것임을 서약합니다.",
        "당사 임직원과 파견 대리인은 관계 법령과 규정에 저해되는 일체의 불공정한 행위를 하지 않을 것이며, 협의회 임원진이나 입주민을 상대로 어떠한 형태의 금품 제공, 향응, 압력 또는 부당한 청탁도 행사하지 않겠습니다.",
        "본 청렴협약 서약은 상호 신뢰를 바탕으로 한 약속으로서 반드시 지킬 것이며, 이를 위반할 경우 제안 참가 자격 박탈, 협약 해지 또는 해제 등 북수원 이목지구 디에트르 더 리체2 입주예정자협의회의 어떠한 조치에 대해서도 손해배상을 청구하거나 민·형사상 이의를 제기하지 않을 것을 확약합니다.",
    ]
    body = f"""<div class="form"><div class="no">[별지서식3]</div><h1>청렴이행각서</h1>
<div class="cs">&lt;건명: {CASE}&gt;</div>
{"".join(f'<p class="tx" style="margin-top:9pt">{x}</p>' for x in paras)}
{seal_tail(26)}</div>"""
    return doc("1 청렴이행각서 [별지 3]", [body])


# ================================================================== 2 · [별지 5] 적격심사 평가표(자기평가 1 ~ 4)
CRIT = [  # 평가 항목 · 평가내용 칸 · 배점 · 기준(점수, 문구) · 비고(증빙)
    ("1. 신용평가등급", "등급", 10, [(10, "BBB 등급 이상"), (5, "BB 등급 이상"), (3, "BB 등급 미만")], "최근 신용평가<br>등급 확인서"),
    ("2. 회사설립연도<br>(공고일 기준)", "년 개월", 10, [(10, "10년 이상"), (5, "5년 이상"), (3, "5년 미만")], "등기부 등본"),
    ("3. 인력보유 현황<br>(공고일 기준 4대보험 가입자)", "인", 10, [(10, "10인 이상"), (5, "5인 이상"), (3, "5인 미만")], "4대보험가입자명부"),
    ("4. 3년 내 1,000세대 이상<br>입주박람회 운영 실적", "건", 10, [(10, "10건 이상"), (5, "5건 이상"), (3, "5건 미만")], "협약서 사본 등<br>실적 증빙서류"),
]


def form5():
    se = D.SELF_EVAL
    assert len(se) == 4 and se[3][1] == f"{len(D.BS_REC)}건", "별지 5의 4번은 별지 4 건수와 같아야 함(별지 5 주석 3)"
    rows = ""
    for (item, _u, pts, crit, ev), (_n, val, score, _src) in zip(CRIT, se):
        assert score in [c[0] for c in crit], (item, score)
        for k, (p, c) in enumerate(crit):
            on = ' class="c on"' if p == score else ' class="c"'
            mk = "● " if p == score else ""
            rows += "<tr>"
            if k == 0:
                rows += (f'<th rowspan="3" style="text-align:left;font-size:9.6pt">{item}</th><td rowspan="3" class="c"><b>{e(val)}</b></td>'
                         f'<td rowspan="3" class="c">{pts}</td>')
            on2 = ' class="on"' if p == score else ""
            rows += f'<td{on}>{mk}{p}</td><td{on2}>{c}</td>'
            if k == 0:
                rows += f'<td rowspan="3" class="c" style="font-size:9pt">기재<br>{ev}</td>'
            rows += "</tr>"
    total = sum(x[2] for x in se)
    rows += ('<tr><th rowspan="3" style="text-align:left;font-size:9.6pt">5. 입주박람회 운영계획 평가<br><span style="font-weight:400;font-size:8.6pt">(A/S·하자보증 정책, 입주민 혜택 등 입예협 내부 평가)</span></th>'
             '<td rowspan="3" class="c">서류제출</td><td rowspan="3" class="c">20</td><td class="c">20</td><td>내부평가 1위 업체</td>'
             '<td rowspan="3" class="c" style="font-size:9pt">입예협 기재<br>제안서 또는<br>입주박람회 운영계획서</td></tr>'
             '<tr><td class="c">15</td><td>내부평가 2위 업체</td></tr><tr><td class="c">10</td><td>내부평가 3위 이하 업체</td></tr>')
    rows += (f'<tr><th style="text-align:left">자기평가 총평점</th><td colspan="4">상기 내용으로 자기 평가하여 평점 합산을 우측에 기재 '
             f'<b style="margin-left:6pt">(1 ~ 4번 합계)</b></td><td class="c on" style="font-size:12pt">{total}</td></tr>')
    rows += ('<tr><th rowspan="3" style="text-align:left;font-size:9.6pt">6. PT 제안평가</th><td rowspan="3" class="c">PT 발표<br>종합 평가</td>'
             '<td rowspan="3" class="c">40</td><td class="c">40</td><td>1순위</td><td rowspan="3" class="c" style="font-size:9pt">입예협에서<br>기재</td></tr>'
             '<tr><td class="c">30</td><td>2순위</td></tr><tr><td class="c">20</td><td>3순위</td></tr>'
             '<tr><th style="text-align:left">총 평점</th><td colspan="4" class="c">-</td><td class="c" style="font-size:9pt">입예협에서 기재</td></tr>')
    body = f"""<style>.f5 th,.f5 td{{padding:2.3pt 6pt!important;font-size:9.3pt!important;line-height:1.3!important}}.form .sgx .bx{{width:70pt;height:70pt}}.form .sgx .bx b{{top:38pt}}.form .sgx .ln{{line-height:2.0}}</style>
<div class="form"><div class="no">[별지서식5]</div><h1 style="margin:0 0 6pt">적격심사 평가표</h1>
<table class="ft f5"><thead><tr><th style="width:24%">항 &nbsp; 목</th><th style="width:12%">평가내용</th><th style="width:7%">배 점</th><th colspan="2">평 &nbsp; 점</th><th style="width:17%">비 &nbsp; 고</th></tr></thead>
<tbody>{rows}</tbody></table>
<div style="font-size:8.3pt;color:#333;margin-top:4pt;line-height:1.45">1. 제안참여업체는 상기 “4번” 까지만 기재하고, “5번, 6번 항목 및 총 평점”은 입예협에서 기재함.<br>
2. 업체별 적격심사 평가표는 제안자에 대한 평가기준이 되므로 만약 허위의 사실을 기재하는 경우 해당 업체에게 민형사상 책임을 물을 수 있으며 허위 기재가 발각될 시 즉시 무효 처리함.<br>
3. ‘4. 입주박람회 운영 실적’은 ‘별지서식4’에 기입한 내용과 동일하여야 함.<br>
<span style="color:#555">※ 제안사 기재: ● = 해당 평점 · 1 신용 BB-(NICE디앤비 평가 {D.NICE_DATE}) · 2 설립 {D.FOUNDED}(공고일 {D.NOTICE_DATE} 기준 4년 7개월) · 3 4대보험 가입자 10인(가입자 명부 2026.10.02) · 4 별지 4의 {len(D.BS_REC)}건</span></div>
{seal_tail(8).replace('class="dt"', 'class="dt" style="margin-top:8pt"').replace('class="to2"', 'class="to2" style="margin-top:12pt"').replace('class="warn"', 'class="warn" style="margin-top:4pt"')}</div>"""
    return doc("2 적격심사 평가표 [별지 5]", [body])


# ================================================================== 2 · [별지 4] 입주박람회 운영 실적표
def form4():
    rows = "".join(f'<tr><td>{e(nm)}</td><td class="c">{n:,}</td><td class="c" style="font-size:9.6pt">{e(when).replace(chr(10), "<br>")}</td>'
                   f'<td style="font-size:8.8pt">{e(where)} · {e(ev)}</td></tr>' for nm, n, when, where, ev in D.BS_REC)
    tot = sum(r[1] for r in D.BS_REC)
    body = f"""<style>.f4 th,.f4 td{{padding:5pt 7pt!important;font-size:10pt!important;line-height:1.4!important}}</style>
<div class="form"><div class="no">[별지서식4]</div><h1 style="letter-spacing:.12em">입주박람회 운영 실적표</h1>
<table class="ft f4"><thead><tr><th>단지명</th><th style="width:11%">세대수</th><th style="width:25%">개최시기</th><th style="width:30%">비고</th></tr></thead>
<tbody>{rows}<tr><th>합계 {len(D.BS_REC)}건</th><th>{tot:,}</th><th colspan="2" style="font-weight:400;font-size:9pt">레이카운티 · 센트럴사하는 1차 · 2차 박람회를 함께 기재(건수는 단지 기준)</th></tr></tbody></table>
<div style="font-size:9.4pt;color:#222;margin-top:8pt;line-height:1.6">※ 실적 중 공고일 기준 최근 3년간 1,000세대 이상 단지의 입주박람회 수행 실적을 기재<br>
- 입증 가능한 타 아파트 협약(계약)서 사본 또는 증빙자료 (후면 첨부) — 제출서류 9(별첨 1 ~ 3)<br>
- 허위 기재시 즉시 탈락처리</div>
{seal_tail(20)}</div>"""
    return doc("2 입주박람회 운영 실적표 [별지 4]", [body])


# ================================================================== 5 · 이행보증보험증권 발급 가능 확인 · 행사배상책임보험 가입 확약서
def doc05():
    from PIL import Image  # noqa: F401
    p1 = f"""{head("제출서류 5", "이행보증보험증권 발급 가능 확인 및 행사배상책임보험 가입 확약서")}
<h2>1. 이행보증보험증권 — 발급 가능</h2>
<table class="t"><tbody>
<tr><td class="k" style="width:24%">발급 근거</td><td class="l">서울보증보험(SGI) <b>계약보증보험증권 발급 이력</b> — 발급일 2026.09.07 · 보증 종목 계약보증보험(용역 계약) — 다음 쪽 증권 사본(상대방 · 금액 · 증권번호 일부 가림)</td></tr>
<tr><td class="k">이번 협약</td><td class="l">협약 체결 시 <b>귀 협의회를 피보험자</b>로 하는 이행(하자)보증보험증권을 보험사로부터 발급받아 제출</td></tr>
<tr><td class="k">보증 금액 · 기간</td><td class="l">협약 시 귀 협의회와 협의하여 확정(제안서: 2년 · 최대 10억원 범위)</td></tr>
</tbody></table>
<h2>2. 행사배상책임보험 — 협약 시 가입 확약(현재 미가입)</h2>
<table class="t"><tbody>
<tr><td class="k" style="width:24%">가입 대상</td><td class="l">행사배상책임보험(행사 주최자 · 주관자 배상책임) — 박람회장 내 제3자 신체 · 재물 손해 담보</td></tr>
<tr><td class="k">가입 시기</td><td class="l">협약 체결 후 박람회 일정 · 장소 확정 시 박람회 기간(설치 · 철거일 포함)을 담보하도록 가입</td></tr>
<tr><td class="k">제출</td><td class="l">박람회 개최 전까지 증권 사본을 귀 협의회에 제출</td></tr>
<tr><td class="k">현재 가입 보험(참고)</td><td class="l">KB손해보험 영업배상책임보험(시설소유관리자 · 본사 사업장, 2026.10.14 ~ 2027.10.14) — 행사배상책임과 별개 · 증권 사본 첨부</td></tr>
</tbody></table>
<p class="body">당사는 「{e(D.NOTICE)}」 제안참여규정 제3조 ⑨와 관련하여, 위와 같이 이행보증보험증권 발급이 가능하며 협약 체결 시 이를 발급하여 제출하고, 행사배상책임보험은 협약 체결 시 가입하여 박람회 개최 전까지 증권 사본을 제출할 것을 확약합니다. 이를 이행하지 않을 경우 귀 협의회의 협약 해지 등 조치를 이의 없이 따르겠습니다.</p>
{sign()}"""
    p2 = f"""{head("제출서류 5 · 붙임", "이행보증보험증권 발급 이력 — 서울보증보험 계약보증보험증권 사본")}
<p class="note" style="margin-top:6pt">다른 용역 계약(광고대행 용역)의 계약보증보험증권 1쪽 — 상대방 · 보험료 · 증권번호 뒷자리 · 가입금액은 가렸습니다. 입주박람회 협약 이행보증 증권이 아니며, 보증보험사 발급 이력을 보여 드리는 자료입니다. 가림 없는 원본은 요청 시 열람.</p>
<div style="margin-top:8pt;border:1px solid #C9CED6;padding:6pt;text-align:center"><img src="../assets_ins/{os.path.basename(SGI_IMG)}" style="max-width:100%;max-height:200mm"></div>"""
    return doc("5 이행보증보험증권 발급 가능 확인 · 행사배상책임보험 가입 확약서", [p1, p2])


# ================================================================== 6 · 신용평가등급 확인서(NICE 표지 + 전문)
NICE_MASK = {12: [(170, 148.5, 228, 163.5), (170, 166.5, 228, 181.5)]}  # 원본 13쪽 '주요 경영진' 생년월일 칸 — 대표 외 임직원 2명


def doc06_cover(n_pages):
    body = f"""{head("제출서류 6", "신용평가등급 확인서 — NICE디앤비 기업신용평가")}
<table class="t" style="margin-top:14pt"><tbody>
<tr><td class="k" style="width:22%">평가 기관</td><td class="l">NICE디앤비(공인 신용평가기관) · CLIP 기업신용평가보고서(관리번호 11125949-202605-001)</td></tr>
<tr><td class="k">평가 대상</td><td class="l">{D.COMPANY} ({D.BIZ_NO})</td></tr>
<tr><td class="k">신용등급</td><td class="l"><b>BB-</b> · 현금흐름등급 <b>A</b></td></tr>
<tr><td class="k">평가일 · 유효기간</td><td class="l">{D.NICE_DATE} · ~2027.06.18 — 당사의 가장 최근 평가(연 1회 평가)</td></tr>
<tr><td class="k">첨부</td><td class="l">보고서 전문 {n_pages}쪽(원본 13쪽 ‘경영진 현황’의 대표 외 임직원 2명 생년월일만 개인정보 보호를 위해 가림)</td></tr>
</tbody></table>
<p class="note" style="margin-top:8pt">※ 보고서의 본사 주소는 본점 이전(2026.07 등기) 전 주소이고, 종업원 수와 경영진 현황은 평가 당시(2026.05) 기준입니다. 현재 등기 사항은 제출서류 3과 같습니다.</p>
<p class="note">※ 별지 5 적격심사 1번(신용평가등급)의 근거 자료입니다. 연혁(원본 9쪽)은 제출서류 9 별첨 1에도 발췌해 붙였습니다.</p>"""
    return doc("6 신용평가등급 확인서", [body])


def nice_full(nice_path):
    d = fitz.open(nice_path)
    assert len(d) == 24, f"NICE 보고서 {len(d)}쪽 — 가림 좌표 다시 확인"
    for i, rects in NICE_MASK.items():
        pg = d[i]
        assert any(x["width"] == 2477 and x["height"] == 3502 for x in pg.get_image_info()), "NICE 13쪽 이미지가 다름 — 가림 좌표 다시 확인"
        for r in rects:
            pg.add_redact_annot(fitz.Rect(*r), fill=(0.82, 0.82, 0.82))
        pg.apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS)
    p = out("06_2_NICE_전문_가림.pdf")
    d.save(p, garbage=GARBAGE, deflate=True)
    return p


# ================================================================== 7 · 재직증명서(현장 책임자)
def doc07_emp():
    m = D.MANAGER
    yy, mm, dd = ymd()
    body = f"""<div class="top"><div class="lb">제출서류 7</div><div class="co">{D.COMPANY}</div></div>
<h1 class="c" style="letter-spacing:.6em;font-size:24pt;margin-top:26pt">재 직 증 명 서</h1>
<table class="info" style="margin-top:26pt;font-size:10.6pt">
<tr><th>성 &nbsp; &nbsp; 명</th><td>{m[0]}</td><th>생년월일</th><td>{birth(MGR_BIRTH, "책임자")}</td></tr>
<tr><th>소 &nbsp; &nbsp; 속</th><td>주관사업</td><th>직 &nbsp; &nbsp; 위</th><td>총괄 본부장</td></tr>
<tr><th>재직 기간</th><td colspan="3">{MGR_JOIN} ~ 현재</td></tr>
<tr><th>담당 업무</th><td colspan="3">입주박람회 주관 업무 총괄 · 본 건 현장 책임자(제안 참가 신청서 책임자 · 2차 PT 발표)</td></tr>
<tr><th>용 &nbsp; &nbsp; 도</th><td colspan="3">{FORM_TO} 입주박람회 주관사 제안 제출용</td></tr>
</table>
<p class="body" style="text-align:center;margin-top:34pt;font-size:12pt">위 사람은 현재 당사에 재직하고 있음을 증명합니다.</p>
<div class="sign" style="margin-top:40pt"><div class="d">{yy}년 {mm}월 {dd}일</div>
<div class="who" style="margin-top:14pt">{D.COMPANY}</div>
<div class="who" style="font-weight:400;font-size:11pt">{D.ADDRESS}</div>
<div class="who">대표이사 &nbsp; {D.CEO}<span class="seal">(인)</span></div></div>
<p class="note" style="margin-top:40pt">※ 4대보험 사업장 가입자 명부(앞 쪽)는 2026.10.02 발급본으로, 현장 책임자는 그 뒤 반영 예정입니다. 전담 인력 명단은 협약 시 제출합니다(제안서 · 제출서류에는 개인정보를 적지 않음 — 제안참여규정 제6조 ②).</p>"""
    return doc("7 재직증명서", [body])


# ================================================================== 9 · 1,000세대 이상 수행 실적 증빙
CAPS9 = [c for c in D.EXPO_CAPS if c[0] in {r[0] for r in D.BS_REC}]   # 별첨 3 — 박람회장 공식 행사일정(대성베르힐 BEXCO · 창원 CECO)


def doc09_cover():
    big_nice = {r[1] for r in D.RECENT3}
    cap_of = {c[0]: k for k, c in enumerate(CAPS9, 1)}
    rows = ""
    for i, (nm, n, when, where, _ev) in enumerate(D.BS_REC, 1):
        ev = []
        if nm in big_nice:
            ev.append("NICE 연혁(별첨 1)")
        ev.append("실적 확약서(별첨 2)")
        if nm == "e편한세상 송도 더퍼스트비치":
            ev.append("BEXCO 행사일정(별첨 2 붙임 3)")
        if nm == "에코델타 대성베르힐":
            ev.append("카페 공지(별첨 2 붙임 2)")
        if nm in cap_of:
            ev.append(f"공식 행사일정(별첨 3-{cap_of[nm]})")
        rows += (f'<tr><td>{i}</td><td class="l">{e(nm)}</td><td class="r">{n:,}</td><td>{e(when).replace(chr(10), "<br>")}</td><td class="l">{e(where)}</td>'
                 f'<td class="l" style="font-size:8.4pt">{" · ".join(ev)}</td></tr>')
    tot = sum(r[1] for r in D.BS_REC)
    body = f"""{head("제출서류 9", "최근 3년간 1,000세대 이상 입주박람회 수행 실적 — 증빙 안내")}
<p class="note" style="margin-top:4pt">기준: 제안참여규정 제3조 ④ · 별지 4 · 별지 5 적격심사 4 — 공고일({D.NOTICE_DATE}) 기준 최근 3년 안에 개최한 1,000세대 이상 공동주택 입주박람회. 세대수는 NICE 연혁 기재값.</p>
<table class="t" style="margin-top:6pt;font-size:8.9pt"><thead><tr><th style="width:5%">No</th><th>단지명</th><th style="width:9%">세대수</th><th style="width:20%">개최 시기</th><th style="width:15%">장소</th><th style="width:28%">증빙</th></tr></thead>
<tbody>{rows}<tr class="sum"><td colspan="2">합계 {len(D.BS_REC)}건 (별지 4와 같음)</td><td class="r">{tot:,}</td><td colspan="3"></td></tr></tbody></table>
<ol class="pl" style="margin-top:8pt"><li class="sm">별첨 1. NICE디앤비 기업신용평가보고서 ‘연혁’ 발췌 — 1쪽(전문은 제출서류 6)</li>
<li class="sm">별첨 2. 실적 확약서 — 1,000세대 이상 입주박람회 주관 10개 단지(최근 3년 8 + 2023.10 이전 2) · 붙임 1 · 2 단지 카페 주관사 공지 캡처(입주민 닉네임 가림) · 붙임 3 BEXCO 공식 행사일정 캡처</li>
<li class="sm">별첨 3. 박람회장 공식 행사일정 캡처 — {" · ".join(f"3-{k} {e(c[0])}({e(c[2].split('(')[0])})" for k, c in enumerate(CAPS9, 1))} — 주최 · 주관란 엣지컴퍼니</li></ol>
<p class="note">※ 레이카운티는 1차(2023.08) · 2차(2023.10) 중 공고일 기준 3년 안인 2차만 셌습니다. 요청하시면 협약서 · 정산 자료 등을 지체 없이 추가 제출합니다.</p>
<p class="body" style="font-size:9.8pt;margin-top:6pt;line-height:1.65">위 실적은 사실과 다름이 없음을 확인하며, 허위로 확인될 경우 제안참여규정 제10조(제안의 무효)에 따른 어떠한 조치도 이의 없이 따르겠습니다.</p>
{sign().replace('class="sign"', 'class="sign" style="margin-top:6pt"').replace('class="to"', 'class="to" style="margin-top:8pt"')}"""
    return doc("9 수행 실적 증빙 안내", [body])


# 별첨 1 — NICE 원본 9쪽 연혁 발췌(고양 docs_gy.annex_nice와 같은 방식)
FONTS = os.path.join(HERE, "..", "통합제안서", "fonts")
NAVY, GOLD, GRAY, LINE = (0.051, 0.118, 0.2), (0.78, 0.66, 0.42), (0.36, 0.4, 0.46), (0.79, 0.81, 0.84)
CLIP_TITLE = fitz.Rect(0, 0, 595, 76)
CLIP_HIST = fitz.Rect(36, 321, 560, 511)
ROWS_RECENT = (398, 506)     # 연혁 표 중 최근 3년 주관 실적 6행(2023/11 ~ 2026/07)
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
    text(L + 23, 51.5, "별첨 1", 8.5, "b", GOLD, "c")
    text(R, 51.5, "제출서류 9 · 1,000세대 이상 수행 실적 증빙", 8.5, "r", GRAY, "r")
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
            ("원본 분량", f"전 {len(nice)}쪽 (전문은 제출서류 6)")]
    x0, x1, xk, rh = L + 186, R, L + 186 + 70, 24
    for i, (k, v) in enumerate(info):
        y = top + i * rh
        pg.draw_rect(fitz.Rect(x0, y, xk, y + rh), color=LINE, fill=(0.945, 0.929, 0.894), width=0.6)
        pg.draw_rect(fitz.Rect(xk, y, x1, y + rh), color=LINE, width=0.6)
        text(x0 + 8, y + 15.5, k, 8.8, "b")
        text(xk + 8, y + 15.5, v, 8.8, "r", (0.1, 0.14, 0.2))
    y = top + len(info) * rh + 18
    text(x0, y, "아래 연혁 중 금색 테두리 6행이 최근 3년", 8.8, "r", GRAY)
    text(x0, y + 13, "1,000세대 이상 입주박람회 주관 실적입니다.", 8.8, "r", GRAY)
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
    o.set_metadata({"title": "별첨 1 NICE 기업신용평가보고서 연혁 발췌", "author": D.COMPANY})
    o.save(out_path, garbage=GARBAGE, deflate=True)
    return out_path


# 별첨 2 — 실적 확약서: 탕정 hwakyak.py의 실적 · 캡처 목록을 읽기만 한다(고양과 같은 방식)
def _hwakyak():
    path = os.path.join(HERE, "..", "탕정푸르지오센터파크", "hwakyak.py")
    saved, dwb = list(sys.path), sys.dont_write_bytecode
    sys.dont_write_bytecode = True  # 탕정 폴더에 캐시 파일을 만들지 않는다
    try:
        spec = importlib.util.spec_from_file_location("_hwakyak_tj", path)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
    finally:
        sys.path[:] = saved
        sys.dont_write_bytecode = dwb
    return m


HW_FIT = "p.body{margin:8pt 0 5pt;line-height:1.75}.t td{padding:2.2pt 5pt}ol{margin-top:6pt;line-height:1.6}.sign{margin-top:8pt;line-height:1.85}.to{margin-top:6pt}"


def doc09_hwakyak():
    hw = _hwakyak()
    yy, mm, dd = ymd()
    for f, _t, _u, _w, boxes in hw.CAPS:  # 가림본이 없으면 원본 캡처에서 다시 가림(픽셀로 굳힘)
        dst = os.path.join(HERE, "assets_ins", "cafe_" + f)
        if not os.path.exists(dst):
            hw.mask(os.path.join(CAP_DIR, f), boxes, dst)
    src_fix = {"입예협 카페 공지 (붙임 1)": "입주민 카페 주관사 게시판 (붙임 1)", "입예협 카페 공지 (붙임 2)": "입주자 모임 카페 주관사 공지 (붙임 2)"}
    recs = [(a, b, c, n, src_fix.get(s, s)) for a, b, c, n, s in hw.RECS]
    rows = "".join(f'<tr><td>{i}</td><td>{e(a)}</td><td class="l">{e(b)}</td><td>{e(c)}</td><td class="r">{n:,}</td><td class="l">{e(s)}</td></tr>'
                   for i, (a, b, c, n, s) in enumerate(recs, 1))
    tot = sum(r[3] for r in recs)
    assert (len(recs), tot) == (10, 19563), "실적 확약서 합계가 제안서(10개 단지 · 19,563세대)와 다름"
    p1 = f"""<section class="pg">
<div style="font-size:9pt;color:#9A7B3F;font-weight:700;letter-spacing:.1em">별첨 2 · 제출서류 9</div>
<h1>실 적 확 약 서</h1><div class="sub">1,000세대 이상 공동주택 입주박람회 주관 실적</div>
<table class="info"><tr><th>상호</th><td>{D.COMPANY}</td><th>대표이사</th><td>{D.CEO}</td></tr>
<tr><th>소재지</th><td colspan="3">{D.ADDRESS}</td></tr>
<tr><th>제출처</th><td colspan="3">{FORM_TO}</td></tr></table>
<p class="body">당사는 「{SITE} 입주박람회 주관사 선정」 제3조 ④(1,000세대 이상 입주박람회 수행 실적)와 관련하여, 1,000세대 이상 공동주택 입주박람회 주관 실적을 아래와 같이 제출하며 기재 내용이 사실임을 확약합니다.</p>
<table class="t"><tr><th>연번</th><th>주관 시기</th><th>단지명</th><th>지역</th><th>세대수</th><th>근거</th></tr>{rows}
<tr class="sum"><td colspan="4">합계 {len(recs)}개 단지</td><td class="r">{tot:,}</td><td></td></tr></table>
<div class="note">※ 근거: NICE 연혁(평가일 {D.NICE_DATE} · 별첨 1) · 단지 카페 주관사 명의 공지 · BEXCO 공식 행사일정(붙임). 세대수는 NICE 연혁 기재값(카페 · BEXCO 근거 3개 단지는 공식 총세대수). 2023.10 이전 2개 단지를 포함한 전체 실적이며, 별지 4에는 공고일 기준 3년 안 8건만 적었습니다.</div>
<ol><li>위 실적은 당사가 입주박람회 주관사로서 직접 수행한 것입니다.</li>
<li>귀 협의회가 요청하면 계약서, 실적 확인서, 정산 자료 등 증빙을 지체 없이 제출하겠습니다.</li>
<li>기재 내용이 사실과 다르면 제안참여규정 제10조(제안의 무효)에 따른 조치를 이의 없이 받아들이겠습니다.</li></ol>
<div class="sign"><div class="d">{yy}년 &nbsp;{mm}월 &nbsp;{dd}일</div>
{D.COMPANY}<br><b>대표이사 &nbsp;{" ".join(D.CEO)}</b><span style="margin-left:48pt">(인)</span></div>
<div class="to">{FORM_TO} 귀 중</div></section>"""
    caps = ""
    for f, title, url, what, boxes in hw.CAPS:
        kind = ("전시장 공식 행사일정 캡처" if f.startswith("bexco") else
                "입주민 소통 카페 주관사 게시판 캡처" if f.startswith("sasang") else "입주자 모임 카페 주관사 공지 캡처")
        caps += (f'<section class="pg"><h2>실적 확약서 붙임 · {kind}</h2><div class="cap"><h3>{e(title)}</h3>'
                 f'<div class="u">{e(url)}{" · 입주민 닉네임(동·호수)은 개인정보 보호를 위해 가림" if boxes else ""}</div><div class="k">{e(what)}</div>'
                 f'<img src="../assets_ins/cafe_{f}"></div></section>')  # HTML은 작업/ 아래
    return f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>실적 확약서</title><style>{hw.CSS}{HW_FIT}</style></head><body>{p1}{caps}</body></html>'


def doc09_caps():  # 별첨 3 — 박람회장 공식 행사일정(한 장)
    items = "".join(
        f'<div class="bxc"><div class="bh"><b>3-{k}</b> {e(nm)} <span>· {e(kind)} · {e(per)} · {e(hall)}</span></div>'
        f'<img src="../assets_ins/{f}" alt=""></div>' for k, (nm, f, kind, per, hall) in enumerate(CAPS9, 1))
    sec = (head("제출서류 9 · 별첨 3", "박람회장 공식 행사일정 캡처")
           + '<p class="note" style="margin-top:4pt">출처: 벡스코(BEXCO) 홈페이지 ‘행사일정’ 상세 화면 · 창원컨벤션센터(CECO) 홈페이지 ‘전체일정’ 화면 · 주최 · 주관란 = 주식회사 엣지컴퍼니 · 화면 그대로(가공 없음)</p>'
           + f'<div class="bxs">{items}</div>')
    css = CSS + (".bxs{display:flex;flex-direction:column;gap:9pt;margin-top:8pt}.bxc{border:1px solid #c9ced6;border-radius:3pt;padding:6pt 7pt}"
                 ".bh{font-size:10pt;margin-bottom:4pt}.bh b{color:#9A7B3F;margin-right:4pt}.bh span{color:#555;font-size:9pt}"
                 ".bxc img{display:block;width:100%;max-height:100mm;object-fit:contain;object-position:left top}")
    return doc("9 별첨 3 박람회장 공식 행사일정", [sec], css)


# ================================================================== 10 · 지명원(회사소개서) 표지 — 본문 = 제안서 01장 '회사소개'
def doc10_cover(pages_note):
    body = f"""<div style="height:240mm;display:flex;flex-direction:column;justify-content:space-between">
<div><div class="top"><div class="lb">제출서류 10</div><div class="co">{D.COMPANY}</div></div>
<div style="margin-top:70pt;font-size:12pt;letter-spacing:.3em;color:#9A7B3F;font-weight:700">COMPANY PROFILE</div>
<h1 style="font-size:34pt;letter-spacing:.25em;margin-top:8pt">지 명 원</h1>
<div style="font-size:15pt;font-weight:700;color:#0D1E33;margin-top:4pt">회사소개서 · 입주박람회 전문 주관사</div>
<div style="width:60pt;height:3pt;background:#C8A86A;margin-top:18pt"></div>
<table class="t" style="margin-top:22pt;font-size:10pt"><tbody>
<tr><td class="k" style="width:24%">상호 · 대표</td><td class="l">{D.COMPANY} · 대표이사 {D.CEO}</td></tr>
<tr><td class="k">설립</td><td class="l">{D.FOUNDED} · 자본금 2억원 · NICE BB- · 현금흐름 A</td></tr>
<tr><td class="k">본사 · 연락처</td><td class="l">{D.ADDRESS} · 대표전화 {D.TEL} · {D.EMAIL}</td></tr>
<tr><td class="k">업종 · 등록</td><td class="l">전시 · 박람회 및 행사 대행업 · 광고대행업 · {D.ELEC_LICENSE} · ISO 9001 · 14001 · 45001</td></tr>
<tr><td class="k">주관 실적</td><td class="l">2023년 이후 1,000세대 이상 입주박람회 주관 10개 단지 · 19,563세대(최근 3년 8건 · 16,274세대)</td></tr>
</tbody></table>
<p class="note" style="margin-top:10pt">구성: {e(pages_note)} — 입주박람회 운영계획서(제출서류 4) 01장 ‘회사소개’와 같은 내용입니다.</p></div>
<div style="text-align:right;font-size:10pt;color:#5B6676">제출처 : {FORM_TO}<br>2026.10</div></div>"""
    return doc("10 지명원(회사소개서)", [body])


# ================================================================== 11 · 계약금 환불 규정
CANCEL_7 = "청소·줄눈, 탄성코트, 유리막코팅, 선반·잡물, 음식물처리기, 인덕션, 벽걸이TV, LED조명"
CANCEL_15 = "미세방충망, 인테리어, 단열필름, 시스템에어컨, 포장이사"
CUSTOM = "커튼·블라인드, 중문, 안전방충망, 맞춤가구"


def doc11():
    arts = [
        ("제1조 (목적)", None,
         f"이 규정은 {D.COMPANY}(이하 ‘주관사’)가 주관하는 {SITE} 입주박람회 및 공동구매(이하 ‘공동구매’)에서 "
         "입주예정자(이하 ‘계약자’)와 참여업체 사이에 체결되는 계약의 계약금·잔금 지급 조건과 취소·환불 기준을 정하여 계약자의 권리를 보호함을 목적으로 한다."),
        ("제2조 (적용 범위)", [
            "공동구매를 통해 체결된 모든 품목의 계약에 적용한다. 박람회 현장 계약과 온라인 박람회(폐쇄몰) 계약을 모두 포함한다.",
            "참여업체는 이 규정을 계약서에 반영하고 계약 체결 전에 계약자에게 설명하여야 한다.",
            "브랜드 본사 직영 품목(가전·가구 등), 렌탈·보험·통신, 사전점검 대행은 각 본사 계약 규정을 따르되, 그 내용을 계약 전에 서면으로 고지하여야 한다.",
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
            "참여업체가 취소·환불을 지연하거나 거부하면 계약자는 주관사 콜센터에 접수할 수 있다. 주관사는 사실을 확인한 뒤 계약자에게 피해 금액을 <b>먼저 보상</b>하고, 참여업체와는 계약 조항에 따라 정산한다(참여업체 특약이행각서 준용).",
            "불이행 업체에는 1단계 홍보정지, 2단계 총액 10% 배상, 3단계 자격박탈 및 입예협 승인을 받아 전 계약을 대체업체로 이관하는 패널티를 차례로 부과한다.",
            "참여업체가 도산한 경우 동종업체로 사후관리를 이관하고, 그 A/S 비용은 주관사가 전액 부담한다.",
            "주관사의 보상 재원으로 하자 예치금 최대 1억원(엣지컴퍼니 자산으로 예치)과 이행보증보험(2년 · 최대 10억원 범위, 금액은 협약 때 단지 규모에 맞춰 확정)을 둔다.",
        ]),
        ("제8조 (가격 보호 — 최저가 차액 10배 보상)", [
            f"공동구매 품목과 브랜드·모델명이 같은 새 제품이 계약 후 7일 이내에 인근({ST['local']}) 오프라인 매장에서 "
            "더 낮은 정상 판매가로 실제 판매된 사실이 구매 영수증(판매 매장 사업자 정보 · 모델명 · 금액 기재)으로 확인되고 "
            "주관사가 해당 매장에 판매 사실을 확인하면, 참여업체는 차액의 10배를 보상하고 판매가를 조정한다.",
            "보상액은 1건당 50만원(해당 품목 계약금액이 더 적으면 그 금액)을 넘지 않으며, 최대 금액은 협약 시 입예협과 협의해 조정할 수 있다(같은 세대 · 같은 품목에는 1회). 견적서 · 가격표 · 구두 안내 가격은 보상 근거가 되지 않는다.",
            "온라인·홈쇼핑 판매, 시공 품목, 카드 청구할인·사은품·결합할인, 전시·리퍼 상품, 법인 특판, 한정 수량 행사가는 비교 대상에서 제외한다.",
            "계약자는 주관사 콜센터에 접수하고, 주관사는 사실 확인 후 7일 이내에 보상이 이행되도록 관리한다.",
        ]),
        ("제9조 (고지)", None,
         "주관사는 이 규정을 박람회장 · 온라인 박람회에 게시하고, 입주예정자협의회 카페에는 입예협 승인 후 게시하며, 모든 공동구매 계약서에 첨부한다."),
        ("제10조 (효력)", None,
         "이 규정은 협약 체결일부터 협약 종료일(입주박람회 종료 및 공동구매 하자 A/S 보증 기간 만료 시)까지 체결된 계약에 적용하며, 협약 종료 후에도 해당 계약의 이행·보증 기간 동안 효력을 가진다."),
    ]
    out_ = []
    for a in arts:
        h, items = a[0], a[1]
        if items:
            lis = "".join(f"<li>{'①②③④⑤⑥⑦⑧'[i]} {x}</li>" for i, x in enumerate(items))
            out_.append(f'<div class="art"><h3>{h}</h3><ol>{lis}</ol></div>')
        else:
            out_.append(f'<div class="art"><h3>{h}</h3><p>{e(a[2])}</p></div>')
    table = f"""<h2>[별표] 품목별 취소 가능 기한 (시공일 기준)</h2>
<table class="t"><thead><tr><th style="width:24%">취소 가능 기한</th><th>품목</th></tr></thead><tbody>
<tr><td class="k" style="text-align:center">시공일 7일 전까지</td><td class="l">{CANCEL_7}</td></tr>
<tr><td class="k" style="text-align:center">시공일 15일 전까지</td><td class="l">{CANCEL_15}</td></tr>
<tr><td class="k" style="text-align:center">출고 지시 전까지</td><td class="l">맞춤 제작 품목({CUSTOM})은 업체와 협의 후 취소 · 브랜드 가전·가구(미제작 시)</td></tr>
<tr><td class="k" style="text-align:center">본사 규정 품목</td><td class="l">렌탈 · 보험 · 통신 · 사전점검 대행 · 브랜드 본사 직영 품목 - 각 본사 계약 규정(계약 전 서면 고지)</td></tr>
<tr><td class="k" style="text-align:center">당일 취소 가능</td><td class="l">사전 해피콜 미이행 시 모든 품목(공급사 귀책)</td></tr>
</tbody></table>
<p class="note">※ 품목 구성은 입주예정자협의회 수요조사 결과에 따라 확정되며, 추가 품목의 기한은 성격이 같은 품목의 기한을 따른다.</p>"""
    summary = f"""<div class="box"><b>핵심 요약</b> &nbsp; 계약금 {D.DEPOSIT_MAX}% 이하 · 현금·카드 동일가 · 잔금은 시공·설치 확인 후 ·
품목별 취소 기한 안 전액 환불(맞춤 제작은 출고 지시 전 업체 협의) · 환불 3영업일 이내 · 업체 불이행 시 주관사 선보상</div>"""
    return doc("11 계약금 환불 규정", [head("제출서류 11", "입주민 계약 취소 시 적용할 계약금 환불 규정") + summary + "".join(out_) + table + sign()])


# ================================================================== 00 · 제출서류 목록(통합 PDF 맨 앞)
def doc00(spans):
    yy, mm, dd = ymd()
    rows = "".join(f'<tr><td>{no}</td><td class="l">{e(t)}</td><td class="l" style="font-size:8.6pt">{e(note)}</td><td>{a}{"" if a == b else f" ~ {b}"}</td></tr>'
                   for no, t, note, a, b in spans)
    body = f"""{head("제출서류 목록", "입주박람회 주관사 제안 · 제출서류 (제안참여규정 제4조)")}
<table class="info" style="margin-top:10pt"><tr><th>제안사</th><td>{D.COMPANY} · 대표이사 {D.CEO}</td><th>책임자</th><td>{D.MANAGER[1]} {D.MANAGER[0]} · {D.MANAGER[2]}</td></tr>
<tr><th>접수</th><td colspan="3">{D.SUBMIT_TO} · 마감 2026.10.25(일) 24:00 · 제목 “{e(D.MAIL_TITLE)}”</td></tr></table>
<table class="t" style="margin-top:10pt"><thead><tr><th style="width:6%">No</th><th style="width:37%">제출 서류(제4조)</th><th>내용 · 발급일</th><th style="width:13%">이 파일 쪽</th></tr></thead><tbody>{rows}</tbody></table>
<p class="note" style="margin-top:8pt">※ 모든 서류를 번호 순서대로 PDF 1개로 병합했습니다(PDF 책갈피 = 번호별). 발행일 1개월 이내 서류만 냈습니다(운영계획서 · 지명원 · 환불 규정 제외 · 신용평가는 연 1회 평가의 최근 평가).</p>
<p class="note">※ {"별지 1 ~ 5는 법인 인감 날인본입니다" if os.path.exists(SEAL_SCAN) else "별지 1 ~ 5의 날인은 직인입니다"} · 법인인감증명서({D.INGAM_DATE} 발급)는 1번에 첨부했습니다. 개인정보는 별지 1 · 재직증명서의 책임자 생년월일 외에는 적지 않았고, 4대보험 명부 · 신용평가서 · 인감증명서의 개인정보는 가렸습니다.</p>
<div class="sign" style="margin-top:14pt"><div class="d">{yy}년 {mm}월 {dd}일</div><div class="who">{D.COMPANY}</div></div>"""
    return doc("00 제출서류 목록", [body])


# ------------------------------------------------------------------ PDF · 날인 · 병합(고양 docs_gy.py와 같은 방식)
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


def evidence_check():
    """증빙 원본이 기재값과 맞는지 — 날짜 · 번호를 글자로 확인할 수 있는 것만."""
    t = fitz.open(f"{EV}/사업자등록증.pdf")[0].get_text()
    assert "2026 년10 월14 일" in t and "전시,박람회및행사대행업" in t, "사업자등록증 발급일 · 종목 확인 실패"
    t = fitz.open(f"{EV}/국세_납세증명서.pdf")[0].get_text()
    assert "2026 년10 월14 일" in t and "2026 년11 월13 일" in t, "국세 납세증명서 발급일 · 유효기간 확인 실패"
    t = fitz.open(KB)[0].get_text()
    assert "영업배상책임보험" in t and "2027년 10월 14일 24:00" in t, "KB 증권 글자 확인 실패"
    assert len(fitz.open(ROSTER)) == 2, "4대보험 가입자 명부(2026.10.02 · 가림본) 2쪽 확인 실패"   # 이미지 PDF — 글자 확인 불가(철산 06 · 지웰 07과 같은 파일)
    for p in (f"{EV}/법인등기부등본.pdf", f"{EV}/지방세_납세증명서.pdf", NICE_SRC, SGI_IMG, P04, INGAM):
        assert os.path.exists(p), f"없음: {p}"


def ch01_pages(pdf):
    """제안서 01장(간지 + '0 1 . 회사소개' 쪽)과 마지막 연락처 쪽 — 지명원 본문."""
    d = fitz.open(pdf)
    idx = [i for i, p in enumerate(d) if "0 1 . 회사소개" in p.get_text()[:200]]
    assert idx and idx == list(range(idx[0], idx[-1] + 1)), idx
    return list(range(idx[0] - 1, idx[-1] + 1)) + [len(d) - 1]


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

    # ---- 별지 1 ~ 5(직인 전 = 법인인감 날인 출력용 · 직인본 = 확인용)
    F = [("01_1_별지1_제안참가신청서", form1()), ("01_2_별지2_확약서", form2()), ("01_3_별지3_청렴이행각서", form3()),
         ("02_1_별지5_적격심사_평가표", form5()), ("02_2_별지4_운영실적표", form4())]
    raw = [fit(render(n, h), 1) for n, h in F]
    if TODOS:
        print("[노란 칸]", " / ".join(dict.fromkeys(TODOS)))
        if final:
            sys.exit("--final: 노란 칸이 남아 있어 멈춤")
    pr = fitz.open()
    for p in raw:
        pr.insert_pdf(fitz.open(p))
    pr.set_metadata({"title": "별지 1 ~ 5 법인인감 날인 출력용", "author": D.COMPANY})
    pr.save(out("별지1-5_법인인감_날인출력용.pdf"), garbage=GARBAGE, deflate=True)
    have_scan = os.path.exists(SEAL_SCAN)
    if have_scan:
        sc = fitz.open(SEAL_SCAN)
        assert len(sc) == 5, f"법인인감 스캔은 5쪽(별지 1 · 2 · 3 · 5 · 4 순)이어야 함: {SEAL_SCAN}"
        forms = [SEAL_SCAN]
    else:
        forms = [stamped(p) for p in raw]
    # ---- 3 · 5 · 6 · 7 · 8 · 9 · 10 · 11
    biz = fitz.open(f"{EV}/사업자등록증.pdf")
    for pg_ in biz:
        for a in list(pg_.annots()):  # 발급 뒤 덧붙인 스탬프 주석이 원본 칸을 가리지 않게
            pg_.delete_annot(a)
    biz_p = out("03_1_사업자등록증.pdf")
    biz.save(biz_p, garbage=GARBAGE, deflate=True)
    d05 = stamped(fit(render("05_1_보증보험_발급가능_행사보험_확약서", doc05()), 2))
    nice06 = nice_full(NICE_SRC)
    c06 = fit(render("06_1_표지", doc06_cover(len(fitz.open(nice06)))), 1)
    emp = stamped(fit(render("07_2_재직증명서", doc07_emp()), 1))
    c09 = stamped(fit(render("09_1_실적증빙_안내", doc09_cover()), 1))
    a1 = stamped(annex_nice(NICE_SRC, out("09_2_별첨1_NICE연혁발췌.pdf")))
    a2 = stamped(fit(render("09_3_별첨2_실적확약서", doc09_hwakyak()), 4))
    a3 = fit(render("09_4_별첨3_공식행사일정", doc09_caps()), 1)
    ch = ch01_pages(P04)
    c10 = fit(render("10_1_지명원_표지", doc10_cover(f"표지 + 회사소개 {len(ch)}쪽(숫자 · 연혁 · 법인 서류 · 인증 · 대표자 · 조직 · 지역 거점 · 협력 네트워크 · 실적 · 추천과 협약 · 연락처)")), 1)
    r11 = stamped(fit(render("11_계약금_환불규정", doc11()), 2, 3))

    def plan():
        """(번호, 이름, 내용, [(pdf, 쪽 목록 또는 None, 책갈피)])"""
        p04 = P04
        return [
            ("1", "참가신청서 · 확약서 · 청렴이행각서 (별지 1 · 2 · 3)", ("법인 인감 날인" if have_scan else "직인 날인") + f" · 법인인감증명서 {D.INGAM_DATE} 발급(주민번호 뒷자리 가림) 첨부",
             ([(forms[0], [0, 1, 2], None)] if have_scan else [(forms[0], None, "별지 1 제안 참가 신청서"), (forms[1], None, "별지 2 확약서"), (forms[2], None, "별지 3 청렴이행각서")])
             + [(INGAM, None, "법인인감증명서")]),
            ("2", "적격심사 자기평가서 · 운영 실적표 (별지 5 · 4)", f"자기평가 1 ~ 4번 {sum(x[2] for x in D.SELF_EVAL)}점 · 실적 {len(D.BS_REC)}건",
             [(forms[0], [3, 4], None)] if have_scan else [(forms[3], None, "별지 5 적격심사 평가표"), (forms[4], None, "별지 4 운영 실적표")]),
            ("3", "사업자등록증 사본 및 법인등기부등본", f"사업자등록증 {D.ISSUE['biz']} · 등기부등본 {D.ISSUE['reg']} 발급",
             [(biz_p, None, "사업자등록증"), (f"{EV}/법인등기부등본.pdf", None, "법인등기부등본")]),
            ("4", "입주박람회 운영계획서", f"제안서 {len(fitz.open(P04))}쪽(행사 개요 · 장소 · 일정 · 협력업체 · 홍보 · 인력 · 안전 · A/S · 민원 · 입주지원 · 협의회 지원)",
             [(p04, None, "입주박람회 운영계획서(제안서)")]),
            ("5", "이행보증보험증권 발급 가능 확인서 · 행사배상책임보험 가입 확약서", "확약서 · SGI 증권 발급 이력(가림) · KB 영업배상책임(참고)",
             [(d05, None, "발급 가능 확인 · 가입 확약서"), (KB, None, "참고 · KB 영업배상책임보험(본사 시설)")]),
            ("6", "민간제출용 신용평가등급 확인서", f"NICE디앤비 BB- · 현금흐름 A · 평가 {D.NICE_DATE}",
             [(c06, None, "표지"), (nice06, None, "NICE 기업신용평가보고서 전문(가림)")]),
            ("7", "4대보험 가입자명부 및 재직증명서", "가입자 명부 2026.10.02(10명 · 가림) · 재직증명서(현장 책임자)",
             [(ROSTER, None, "4대보험 사업장 가입자 명부"), (emp, None, "재직증명서(현장 책임자)")]),
            ("8", "국세 및 지방세 완납 증명서", f"국세 {D.ISSUE['tax']} · 지방세 {D.ISSUE['ltax']} 발급(유효 ~2026.11.13)",
             [(f"{EV}/국세_납세증명서.pdf", None, "국세 납세증명서"), (f"{EV}/지방세_납세증명서.pdf", None, "지방세 납세증명서")]),
            ("9", "최근 3년간 1,000세대 이상 입주박람회 수행 실적 증빙자료", f"{len(D.BS_REC)}건 · 안내 + NICE 연혁 · 실적 확약서 · 공식 행사일정",
             [(c09, None, "증빙 안내"), (a1, None, "별첨 1 NICE 연혁 발췌"), (a2, None, "별첨 2 실적 확약서 · 붙임 1 ~ 3"), (a3, None, "별첨 3 공식 행사일정")]),
            ("10", "지명원 (회사소개서)", f"표지 + 운영계획서 01장 회사소개 {len(ch)}쪽",
             [(c10, None, "표지"), (p04, ch, "회사소개")]),
            ("11", "입주민 계약 취소 시 적용할 계약금 환불 규정", "제1 ~ 10조 · 별표",
             [(r11, None, "계약금 환불 규정")]),
        ]

    def assemble():
        items = plan()
        # 1차: 쪽 범위 계산(목록 1쪽 + 각 서류)
        spans, toc, pg0 = [], [], 2
        for no, name, note, parts in items:
            n = sum(len(pl) if pl else len(fitz.open(p)) for p, pl, _ in parts)
            spans.append((no, name, note, pg0, pg0 + n - 1))
            pg0 += n
        lst = stamped if False else (lambda p: p)
        p00 = lst(fit(render("00_제출서류목록", doc00(spans)), 1))
        o = fitz.open()
        o.insert_pdf(fitz.open(p00))
        toc.append([1, "제출서류 목록", 1])
        docs = {}  # 같은 파일은 한 Document로 — 지명원(10)이 운영계획서(4)의 글꼴 · 사진을 다시 싣지 않게
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
        o.set_metadata({"title": f"{D.COMPANY} · {SITE} 입주박람회 주관사 제안서 · 제출서류 1 ~ 11", "author": D.COMPANY})
        name = PFX + "입주박람회_주관사_제안서_제출서류" + ("" if have_scan else "_직인본") + ".pdf"
        path = os.path.join(SUBMIT, name)
        o.save(path, garbage=GARBAGE, deflate=True, deflate_fonts=True, deflate_images=True, use_objstms=1)  # 객체 스트림 · 글꼴 압축(글자 그대로 · 아래 대조)
        bad = [i + 1 for i, (x, y) in enumerate(zip(src_txt, page_texts(path))) if x != y]
        assert not bad, f"합친 뒤 글자가 달라진 쪽 {bad[:10]}"
        assert len(fitz.open(path)) == pg0 - 1
        return path, spans

    for f in os.listdir(SUBMIT):
        if f.endswith(".pdf"):
            os.remove(os.path.join(SUBMIT, f))
    full, spans = assemble()
    mb_f = os.path.getsize(full) / 1e6
    lines = [f"[제출 현황 · 내부용 — 첨부 금지] {SITE} · 접수 {D.SUBMIT_TO} · 제목 {D.MAIL_TITLE} · 마감 {D.DEADLINE}", ""]
    for no, name, note, a, b in spans:
        lines.append(f"{no:>2}. {name} — p.{a}" + ("" if a == b else f" ~ {b}") + f" · {note}")
    lines += ["", f"통합본: {full}  {len(fitz.open(full))}쪽 · {mb_f:.1f}MB"]
    if not have_scan:
        lines += ["", f"조치 권장: 별지 1 ~ 5 법인인감 — 작업/{PFX}별지1-5_법인인감_날인출력용.pdf(5쪽) 출력 → 법인인감 날인 → 스캔(5쪽 PDF) → {SEAL_SCAN} 에 두고 다시 실행"]
    text = "\n".join(lines) + "\n"
    pathlib.Path(WORK, "제출현황.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
