# -*- coding: utf-8 -*-
"""엘리프 한신더휴 수원 입주박람회 주관사 제안 — 제안 참여 규정 제4조 제출서류 ① ~ ⑰ 생성기(A4 세로) · PDF 1개 병합.

제4조: 아래 서류를 '번호 순서대로' PDF로 이메일(elifhanshinthehue@naver.com) 제출 · 제목 '엘리프 한신더휴 수원 주관사 제안서 – 업체명' · 마감 2026.10.30(금) 18:00.
  00 제출서류 목록(번호 · 쪽) — 통합 PDF 맨 앞(안내용)
  ①  사업자등록증 사본(2026.10.23)              ②  법인 등기부등본(2026.10.23 · 1개월 · 대표 주소 가림)
  ③  4대 보험 가입자 명부(2026.10.23 · 가림)     ④  기업신용평가서(NICE 표지 + 전문 · 대표 외 임직원 생년월일 가림)
  ⑤  최근 1년 보증보험 증권(협의회-주관사 간) = 0건 안내 + 다른 용역 계약보증 1건(가림) + 협약 후 발급 확약
  ⑥  최근 3년 1,000세대 이상 수임 실적 증빙 = 안내 + A NICE 연혁 발췌 + B 공식 행사일정(BEXCO · CECO)
  ⑦  전담인력 배치 확약서(자유)                   ⑧  대표 계약서 = 안내(최근 1년 체결분 없음) + 가장 최근 협약서(2025.08.02 · 가림) + 이 단지 환불 규정
  ⑨  A/S 및 사후관리 계획서(자유) + 붙임 건축 기술 자문 협약서 사본(2쪽)  ⑩  입찰 제안서 = build_el.py 밝은 시안
  ⑪  국세 · 지방세 완납 증명서(2026.10.23 · 지방세 휴대번호 가림)
  ⑫  인감증명서(2026.10.26 · 가림) + 사용인감계  ⑬  별지 1 · 2 · 3           ⑭  별지 4 · 5
  ⑮  하자 보수 이행각서(자유)   ⑯(원문 ⑭) 비밀 유지 서약서(자유)   ⑰(원문 ⑮) 이의 제기 금지 서약서(자유)

날인: 별지 1 ~ 5 = '반드시 법인 인감 날인' → 법인인감은 디지털로 만들지 않는다(규칙 4).
  - 작업/'법인인감_날인출력용_6쪽.pdf'(별지 1 · 2 · 3 · 4 · 5 + 사용인감계)를 출력 → 법인인감 날인 → 스캔(6쪽 PDF) → SEAL_SCAN 경로 → 다시 실행.
  - 스캔이 없으면 별지에도 직인을 찍은 '_직인본'을 만든다(내용 확인용 · 제출 전 스캔 교체).
  - 자유 양식(⑦ ⑧ 안내 ⑨ ⑮ ⑯ ⑰ · ⑤ ⑥ 안내) = 사용인감(직인) · ⑫ 사용인감계로 신고.
출력: 작업/ = 중간 파일 · 제출본/ = 통합 PDF 1개(메일용 저용량본 없음) · 작업/제출현황.txt(내부용)
사용: python docs_el.py <투명 직인.png> [--final]    (결과 PDF · HTML은 깃 제외)
"""
import html
import io
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
PFX = "엣지컴퍼니_엘리프한신더휴수원_"
ST = D.SITE
SITE = ST["name"]
FORM_TO = "엘리프 한신더휴 수원 입주예정자협의회"   # 별지 원문 표기
CASE = "엘리프 한신더휴 수원 입주박람회 주관사 선정"   # 별지 2 · 3 건명
TODOS = []

SP = D.SP   # 증빙 · 직인 · 스캔 폴더 — 본부장 PC = C:\본부장 안 빌드자료(10-28) · 없으면 클라우드 스크래치패드
EV = f"{SP}/evidence"                 # 증빙 원본(깃 제외) — 2026.10.23 발급본(사업자등록증 · 등기부 · 국세 · 지방세)
EVN = f"{SP}/evidence_nr"             # 2026.10.23 · 10.26 발급본(나리벡 때 받은 것)
NICE_SRC = f"{EV}/NICE_기업신용평가.pdf"
ROSTER = f"{SP}/cs_sub/엣지컴퍼니_4대보험_사업장가입자명부_20261023_가림.pdf"   # 2026.10.23 발급 13명 · 성명 가운데 글자 · 주민번호 뒷자리 가림
INGAM = f"{EVN}/법인인감증명서.pdf"   # 2026.10.26 발급 · 주민번호 뒷자리 가림본(나리벡 06과 같은 파일)
DNB = f"{EV}/건축자문_협약서_가림.pdf"   # 건축 분야 기술 자문 업무협약서(2026.10.28 · 양측 날인 · 을 상호 · 사업자번호 · 주소 · 대표 · 도장 가림) 2쪽 = ⑨ 붙임
DNB_CO = "주식회사 디엔비파트너스건축사사무소"   # 협약서 원문 상호(본부장 10-29 '상단 업체명은 가림 안 해도 돼')
DNB_NAME = "디엔비파트너스건축사사무소 · 건축 분야 기술 자문 협력사(업무협약 2026.10.28 · 사본 붙임)"   # 본부장 결정 10-28 표기
SGI_IMG = os.path.join(HERE, "assets_ins", "os_sgi_bond_masked.png")   # SGI 계약보증보험증권 1쪽(가림)
R500_DOC = D.R500_DOC                 # 주관사 협약서 3건(센터포인트 · 드파인 센텀 · 디에트르 더퍼스트 순) — 상대방 성명 · 연락처 · 계좌 가림본
CAPS_EL = [("e편한세상 송도 더퍼스트비치", f"{SP}/hw/cap/bexco_songdo.png", "BEXCO 공식 행사일정", "2024.06.14 ~ 16", "BEXCO 제2전시장"),
           ("에코델타 대성베르힐", os.path.join(HERE, "assets_ins", "bx_daesung.png"), "BEXCO 공식 행사일정", "2025.11.28 ~ 30", "BEXCO 제2전시장"),
           ("창원 센트럴 아이파크", os.path.join(HERE, "assets_ins", "ceco_changwon.png"), "창원컨벤션센터(CECO) 공식 행사일정", "2026.07.03 ~ 05", "CECO 제2전시장")]
WORK = os.path.join(HERE, "작업")
SUBMIT = os.path.join(HERE, "제출본")
P10 = os.path.join(HERE, PFX + "입주박람회_주관사_제안서_밝은시안.pdf")   # ⑩ 제안서 = 밝은 시안(tools/light_build.py)
SEAL_SCAN = D.EL_SEAL_SCAN or f"{SP}/seal_scan/엘리프_별지1-5_사용인감계_법인인감.pdf"   # 6쪽 = 별지 1 · 2 · 3 · 4 · 5 · 사용인감계

_priv = os.path.join(HERE, "org_private.json")  # 깃 제외(생년월일)
PRIV = json.load(open(_priv, encoding="utf-8")) if os.path.exists(_priv) else {}
MGR_BIRTH = D.MGR_BIRTH or PRIV.get("mgr_birth")
R3 = D.EL_REC
R3_N, R3_HH = len(R3), sum(r[1] for r in R3)
STAFF12 = sum(n for _, n, _ in D.STAFF)


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
.sf{color:#111;font-size:11pt;line-height:1.8}
.sf .no{font-size:10pt;color:#333}
.sf h1{text-align:center;font-size:20pt;letter-spacing:.25em;color:#111;margin:10pt 0 14pt}
.sf .ft{width:100%;border-collapse:collapse;font-size:10.4pt}
.sf .ft th,.sf .ft td{border:.8pt solid #333;padding:6pt 9pt;vertical-align:middle;line-height:1.5}
.sf .ft th{background:#F2F2F2;font-weight:700;text-align:center;white-space:nowrap;width:22%}
.sf p.tx{margin-top:14pt;text-indent:10pt;text-align:justify;line-height:1.85}
.sf .dt{text-align:center;margin-top:20pt;font-size:12pt;letter-spacing:.15em}
.sf span.mk{color:#fff;font-size:4pt}
.sf .nt{font-size:9pt;color:#333;margin-top:6pt;line-height:1.55}
.sf .seal2{display:grid;grid-template-columns:1fr 1fr;border:.8pt solid #333;border-top:0}
.sf .seal2 div{height:118pt;border-right:.8pt solid #333;display:flex;align-items:center;justify-content:center;position:relative}
.sf .seal2 div:last-child{border-right:0}
.sf .sgr{width:70%;margin:14pt 0 0 auto;font-size:11pt;line-height:2.2}
.sf .to2{margin-top:22pt;text-align:center;font-size:13pt;font-weight:800;letter-spacing:.04em}
.f5 th,.f5 td{padding:3pt 6pt!important;font-size:9.1pt!important;line-height:1.34!important}
.f5x .sgx{margin-top:4pt!important}.f5x .sgx .bx{width:62pt;height:62pt}.f5x .sgx .bx b{top:34pt}.f5x .sgx .ln{line-height:1.85;font-size:10.4pt}.f5x h1{font-size:18pt!important}
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


def seal_tail(top=20, co="법인명"):
    """별지 1 ~ 5 꼬리(원문): 법인명(업체명) · 주소 · 대표자 + '직인 또는 인감' 칸 → 법인 인감 안내 → 날짜 → 귀 중."""
    yy, mm, dd = ymd()
    return (f'<div class="sgx" style="margin-top:{top}pt"><div class="ln">{co} : <b>{D.COMPANY}</b><br>주 &nbsp;소 : {D.ADDRESS}<br>대표자 : <b>대표이사 {D.CEO}</b></div>'
            f'<div class="bx"><i>직 인<br>또는<br>인 감</i><b>(인)</b></div></div>'
            '<div class="warn">※ 반드시 법인 인감 날인 요망. 요건 불충족 시 제안 참가 불가함.</div>'
            f'<div class="dt">{yy}년 &nbsp; {mm}월 &nbsp; {dd}일</div>'
            f'<div class="to2">{FORM_TO} 귀 중</div>')


def birth(v, who):
    return e(v) if v else todo(f"{who} 생년월일 — 본부장님 확인")


# ================================================================== ⑬ [별지서식1] 제안 참가 신청서
def form1():
    m = D.MANAGER
    body = f"""<div class="form"><div class="no">[별지서식1]</div><h1>제안 참가 신청서</h1>
<table class="ft">
<tr><th>사 업 명</th><td colspan="4">엘리프 한신더휴 수원 입주예정자협의회<br>입주박람회 주관사 선정</td></tr>
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
    return doc("⑬ 제안 참가 신청서 [별지서식1]", [body])


# ================================================================== ⑬ [별지서식2] 확약서 — 원문 그대로
def form2():
    paras = [
        f"본 업체(제안사)는 {FORM_TO} 입주박람회 주관사 선정 입찰에 참여함에 있어, 귀 협의회의 협약대상자 선정 방식 및 공고문 내용과 본 입찰에 관련된 귀 협의회의 방침에 이의가 없음을 확약하며, 아래의 내용을 준수하고 이행할 것임을 엄숙히 서약합니다.",
        "본 제안 참여와 관련하여 제출된 모든 증빙 자료는 신의성실의 원칙에 입각하여 진실하게 작성하였으며, 귀 협의회의 제안서 평가 및 협상 결과 등에 대하여 어떠한 이의도 제기하지 않겠습니다.",
        "협약대상자(주관사)로 선정될 경우, 주관 업무의 전부 또는 일부를 어떠한 형태로든 타사(타인)에 도급(재하도급, 재하청) 또는 양도하지 않으며, 협약 체결 이후라도 이러한 사실이 적발될 경우 즉시 협약이 해지됨을 감수하고 이에 대해 민·형사상 어떠한 이의도 제기하지 않겠습니다.",
        f"{FORM_TO}가 평가를 위해 구성한 평가 임원진과 평가 방법 및 기준에 따른 최종 결과에 절대 승복하며, 협약대상자 선정 전까지 귀 협의회의 추가 요청 내용과 협약 체결에 따른 증빙 서류 제출 등 제반 유의사항을 철저히 준수할 것을 확약합니다.",
    ]
    body = f"""<div class="form"><div class="no">[별지서식2]</div><h1 style="letter-spacing:.6em">확 약 서</h1>
<div class="cs">&lt;건명: {CASE}&gt;</div>
{"".join(f'<p class="tx" style="margin-top:9pt">{x}</p>' for x in paras)}
{seal_tail(26, "업체명")}</div>"""
    return doc("⑬ 확약서 [별지서식2]", [body])


# ================================================================== ⑬ [별지서식3] 청렴이행각서 — 원문 그대로
def form3():
    paras = [
        f"본 업체(제안사)는 {FORM_TO}에서 시행하는 「입주박람회 주관사 선정」 입찰에 참여함에 있어, 입주박람회 기획·운영, 협력업체 유치·관리, 사후 A/S·민원 대응 및 입주지원 등(입찰 공고문 및 지침서에 포함된 업무 일체)의 협약 사항을 성실히 이행할 것입니다.",
        "만일 당사의 귀책사유가 발생할 경우 전적으로 당사가 책임질 것이며, 이에 대해 어떠한 이의도 제기하지 않을 것임을 서약합니다.",
        "당사 임직원과 파견 대리인은 관계 법령과 규정에 저해되는 일체의 불공정한 행위를 하지 않을 것이며, 협의회 임원진이나 입주민을 상대로 어떠한 형태의 금품 제공, 향응, 압력 또는 부당한 청탁도 행사하지 않겠습니다.",
        f"본 청렴협약 서약은 상호 신뢰를 바탕으로 한 약속으로서 반드시 지킬 것이며, 이를 위반할 경우 제안 참가 자격 박탈, 협약 해지 또는 해제 등 {FORM_TO}의 어떠한 조치에 대해서도 손해배상을 청구하거나 민·형사상 이의를 제기하지 않을 것을 확약합니다.",
    ]
    body = f"""<div class="form"><div class="no">[별지서식3]</div><h1>청렴이행각서</h1>
<div class="cs">&lt;건명: {CASE}&gt;</div>
{"".join(f'<p class="tx" style="margin-top:9pt">{x}</p>' for x in paras)}
{seal_tail(26, "업체명")}</div>"""
    return doc("⑬ 청렴이행각서 [별지서식3]", [body])


# ================================================================== ⑭ [별지서식4] 입주박람회 운영 실적표
def form4():
    rows = "".join(f'<tr><td>{e(nm)}</td><td class="c">{n:,}</td><td class="c" style="font-size:9.6pt">{e(when).replace(chr(10), "<br>")}</td>'
                   f'<td style="font-size:8.8pt">{e(where)} · {e(ev)}</td></tr>' for nm, n, when, where, ev in R3)
    body = f"""<style>.f4 th,.f4 td{{padding:5pt 7pt!important;font-size:10pt!important;line-height:1.4!important}}</style>
<div class="form"><div class="no">[별지서식4]</div><h1 style="letter-spacing:.12em">입주박람회 운영 실적표</h1>
<table class="ft f4"><thead><tr><th>단지명</th><th style="width:11%">세대수</th><th style="width:25%">개최시기</th><th style="width:30%">비고</th></tr></thead>
<tbody>{rows}<tr><th>합계 {R3_N}건</th><th>{R3_HH:,}</th><th colspan="2" style="font-weight:400;font-size:9pt">센트럴사하는 1차 · 2차 박람회를 함께 기재(건수는 단지 기준)</th></tr></tbody></table>
<div style="font-size:9.4pt;color:#222;margin-top:8pt;line-height:1.6">※ 실적 중 공고일 기준 최근 3년간 1,000세대 이상 단지의 입주박람회 수행 실적을 기재<br>
- 허위 기재시 즉시 탈락처리<br>
<span style="color:#555">제안사 기재: 공고일 {D.NOTICE_DATE} 기준 최근 3년 = 2023.10.21 이후 개최 · 세대수 = NICE 연혁 기재값 · 단지 공식 세대수 · 증빙 = 제출서류 ⑥ · 레이카운티 2차(2023.10.21 ~ 22)는 기준일 경계라 넣지 않음</span></div>
{seal_tail(20, "업체명")}</div>"""
    return doc("⑭ 입주박람회 운영 실적표 [별지서식4]", [body])


# ================================================================== ⑭ [별지서식5] 자기 평가서 — 공고일 기준 · 제안서 07장 '자기 평가서 10항목'과 같은 값
def self_eval():
    bond = getattr(D, "EL_BOND_AMT", None)   # 별지 5 ⑤ 보증보험 발생 가능 금액(억원) — 보험대리점 서면 확인서 숫자
    return [
        ("1. 회사 운영 기간", "4 년 7 개월", f"법인 설립 · 개업 {D.FOUNDED} · 공고일 {D.NOTICE_DATE} 기준(사업자등록증 · 법인등기부등본) · 최근 3년 1,000세대 이상 입주박람회 {R3_N}건 수행(별지 4)"),
        ("2. 법인등기부등본 상 자본금 규모", "2 억원", f"법인등기부등본({D.ISSUE['reg']} 발급) 자본금 2억원"),
        ("3. 4대보험 가입자 명부 기준 정직원 수", "13 인", "4대보험 사업장 가입자 명부(2026.10.23 발급) · 공고일 기준 가입자 13명(대표이사 포함)"),
        ("4. 신용평가사 발행 기업신용평가서 등급", "BB- 등급", f"NICE디앤비 기업신용평가 · 평가일 {D.NICE_DATE} · 현금흐름등급 A · 연 1회 정기 평가(재무제표 기준)"),
        ("5. 보증보험 발생 가능 금액", (f"{bond} 억원" if bond else "협약 후<br>SGI 심사로 확정"),   # 10-28: 확인서 없음 → 금액 없이 적음(날인 스캔 6쪽과 같은 글자)
         "현재 확정 금액 없음 · 협약 체결 후 서울보증보험(SGI) 심사로 금액 확정 · 협의회를 피보험자로 계약이행 · 하자보증보험(보증기간 24개월) 발급 · 증권 사본 제출 · 발급 이력 = 계약보증보험증권 1건(2026.09.07 · 다른 용역 · 제출서류 ⑤)"),
        ("6. 최근 3년간 1,000세대 이상 수임 실적", f"{R3_N} 건", f"공고일 기준 최근 3년 개최 1,000세대 이상 {R3_N}건 · {R3_HH:,}세대(별지 4 · 증빙 = 제출서류 ⑥) · 수임 후 개최 예정 1,000세대 이상 2곳은 건수에 넣지 않음"),
        ("7. 우리 단지만을 위한 전담 인력 배치 정직원 수", "1 인", "전담 PM 1명(4대보험 명부 등재 정직원) · 1회차 박람회 · C3 입주 · 2회차 준비가 겹치는 2027.09 ~ 2028.04에는 1명 추가(2명) · 확약서 = 제출서류 ⑦"),
        ("8. 최근 1년간 보증보험 증권 발행건 수", "0 건", "협의회 - 주관사 간 발행 0건(제4조 ⑤ 기준) · 별도로 다른 용역의 계약보증보험증권 1건(2026.09.07 · 입주박람회 협약 이행보증 아님 · 제출서류 ⑤)"),
        ("9. 입주민과 업체간 계약 및 환불 규정",
         f"계약금 {D.DEPOSIT_MAX}% 상한(맞춤 제작 · 본사 규정 품목 예외 - 적용 품목은 업체 선정 때 협의회 승인 후 단가표 · 계약서에 표시) · 취소 기한 안 전액 환불(시공일 7일 전 · 15일 전 · 맞춤 제작은 출고 지시 전) · 환불 3영업일 이내 · 잔금은 시공 · 설치 확인 후 · 카드 · 현금 같은 단가 · 최저가 차액 10배(1건당 최대 50만원 · 주관사 지급)",
         "계약 취소 · 환불 규정 전문 = 제출서류 ⑧"),
        ("10. 컴플레인 혹은 A/S 발생시 처리방안 및 대응",
         f"한 창구 접수(콜센터 {D.TEL} 평일 09:00 ~ 18:00 · 카페 · 카카오채널 365일) → 24시간 안 1차 회신(주말 · 공휴일 = 다음 영업일 12시) → 48시간 안 방문 일정 확정(긴급 하자 우선 배정) → 업체가 24시간 무응답이면 주관사 개입 · 사실 확인 뒤 먼저 보상 → 도산 시 대체 업체 이관(무상 A/S 기간 안 비용 주관사) · 무상 A/S 시공 품목 최소 2년 · 건설 하자는 시공사 처리(주관사 정리 · 전달 · 추적)",
         "A/S 및 사후관리 계획서 = 제출서류 ⑨"),
    ]


def form5():
    rows = ""
    for item, val, note in self_eval():
        wide = item.startswith(("9.", "10."))
        rows += (f'<tr><th style="text-align:left;font-size:9.4pt">{e(item)}</th>'
                 + (f'<td colspan="2" style="font-size:8.9pt;line-height:1.45">{val}<br><span style="color:#555">({e(note)})</span></td></tr>' if wide else
                    f'<td class="c" style="width:15%;font-weight:800">{val}</td><td style="font-size:8.7pt;line-height:1.42">{e(note)}</td></tr>'))
    body = f"""<div class="form f5x"><div class="no">[별지서식5]</div><h1 style="margin:0 0 6pt;letter-spacing:.3em">자기 평가서</h1>
<table class="ft f5"><thead><tr><th style="width:27%">항 &nbsp; 목</th><th style="width:15%">평가내용</th><th>보충설명(필요시)</th></tr></thead>
<tbody>{rows}</tbody></table>
<div style="font-size:8.3pt;color:#333;margin-top:4pt;line-height:1.45">1. 자기 평가서 작성 시 공고일 기준으로 작성하며, 보충 설명이 필요 시 ‘보충설명’란에 기재.<br>
2. 자기 평가서는 제안자에 대한 평가기준이 되므로 만약 허위의 사실을 기재하는 경우 해당 업체에게 민형사상 책임을 물을 수 있으며 허위 기재가 발각될 시 즉시 무효 처리함.</div>
{seal_tail(6, "업체명").replace('class="dt"', 'class="dt" style="margin-top:6pt"').replace('class="to2"', 'class="to2" style="margin-top:8pt"').replace('class="warn"', 'class="warn" style="margin-top:3pt"')}</div>"""
    return doc("⑭ 자기 평가서 [별지서식5]", [body])


# ================================================================== ⑫ 사용인감계(자유 양식 · 별지 없음)
def form_gam():
    yy, mm, dd = ymd()
    body = f"""<div class="sf"><h1 style="letter-spacing:.45em">사 용 인 감 계</h1>
<table class="ft"><tr><th>상호(법인명)</th><td>{D.COMPANY}</td></tr>
<tr><th>사업자등록번호</th><td>{D.BIZ_NO}</td></tr>
<tr><th>법인등록번호</th><td>{D.CORP_NO}</td></tr>
<tr><th>본점(사업장) 소재지</th><td>{D.ADDRESS}</td></tr>
<tr><th>대표자 성명</th><td>{D.CEO}</td></tr></table>
<table class="ft" style="border-top:0"><tr><th style="width:50%">사 용 인 감</th><th>법 인 인 감</th></tr></table>
<div class="seal2"><div><span class="mk">(인감날인)</span></div><div></div></div>
<p class="tx">위 사용인감은 당사가 {FORM_TO}의 「입주박람회 주관사 선정」 제안에 참여함에 있어 전담인력 배치 확약서, A/S 및 사후관리 계획서, 하자 보수 이행각서, 비밀 유지 서약서, 이의 제기 금지 서약서 등 제안 관련 서류와 협약 체결에 관한 서류에 사용하는 인감임을 신고합니다.</p>
<p class="tx" style="margin-top:6pt">당사는 위 사용인감을 날인하여 행한 모든 행위에 대하여 법인인감을 날인하여 행한 것과 동일하게 일체의 책임을 지겠습니다.</p>
<div class="dt" style="margin-top:14pt">{yy}년 &nbsp; {mm}월 &nbsp; {dd}일</div>
<div class="sgr">신 고 인<br>상 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 호 : {D.COMPANY}<br>대 표 자 : 대표이사 {D.CEO} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; (인)</div>
<div class="to2">{FORM_TO} 귀중</div>
<p class="nt" style="margin-top:10pt">※ 별지서식 1 ~ 5는 법인인감으로 날인했고, 자유 양식 서류는 위 사용인감으로 날인했습니다. 법인인감증명서(2026.10.26 발급 · 주민번호 뒷자리 가림)를 앞에 붙였습니다.</p></div>"""
    return doc("⑫ 사용인감계", [body])


# ================================================================== ⑤ 최근 1년 보증보험 증권(협의회 - 주관사 간) — 0건 안내 + 발급 이력 + 협약 후 발급 확약
def doc05():
    p1 = f"""{head("제출서류 ⑤", "최근 1년간 발행한 보증보험 증권(협의회와 주관사 간) — 0건 안내 및 발급 확약")}
<div class="box"><b>최근 1년간 입주예정자협의회와 주관사 간에 발행한 보증보험 증권: 0건</b><br>
제4조 ⑤가 정한 서류(협의회 - 주관사 간 증권)는 최근 1년 안에 발행한 것이 없습니다. 없는 서류를 있는 것처럼 만들지 않고, 대신 아래 근거를 함께 냅니다.</div>
<h2>1. 보증보험 발급 이력(다른 용역 계약)</h2>
<table class="t"><tbody>
<tr><td class="k" style="width:24%">증권</td><td class="l">서울보증보험 <b>계약보증보험증권</b> · 발급 2026.09.07 · 주계약 = 광고대행 용역(다음 쪽 사본 · 상대방 · 금액 · 증권번호 일부 가림)</td></tr>
<tr><td class="k">의미</td><td class="l">보증보험사의 발급 심사를 통과한 사실을 보여 드리는 자료입니다. <b>입주박람회 협약 이행보증 증권이 아닙니다.</b></td></tr>
</tbody></table>
<h2>2. 선정되면 — 협의회를 피보험자로 발급</h2>
<table class="t"><tbody>
<tr><td class="k" style="width:24%">보증</td><td class="l">계약이행 · 하자보증보험 · 보증기간 24개월</td></tr>
<tr><td class="k">피보험자</td><td class="l">{FORM_TO}</td></tr>
<tr><td class="k">시기 · 제출</td><td class="l">협약 체결 후 보험사로부터 발급받아 증권 사본을 귀 협의회에 제출(금액 · 기산일 · 보증 대상은 협약 때 귀 협의회와 확정)</td></tr>
<tr><td class="k">행사배상책임보험</td><td class="l">회차별 박람회 기간 행사장 기준 가입 · 개장 전 증권 사본 제출</td></tr>
</tbody></table>
<p class="body">당사는 위와 같이 최근 1년간 귀 협의회와 같은 입주예정자협의회를 피보험자로 한 보증보험 증권 발행이 없음을 밝히며, 협약 대상자로 선정되면 협약 체결 후 귀 협의회를 피보험자로 하는 계약이행 · 하자보증보험증권을 발급받아 제출할 것을 확약합니다. 이를 이행하지 않으면 귀 협의회의 협약 해지 등 조치를 이의 없이 따르겠습니다.</p>
{sign()}"""
    p2 = f"""{head("제출서류 ⑤ · 붙임", "보증보험 발급 이력 — 서울보증보험 계약보증보험증권 사본")}
<p class="note" style="margin-top:6pt">다른 용역 계약(광고대행 용역)의 계약보증보험증권 1쪽 — 상대방 · 보험료 · 증권번호 뒷자리 · 가입금액은 가렸습니다. 입주박람회 협약 이행보증 증권이 아닙니다. 가림 없는 원본은 요청 시 열람.</p>
<div style="margin-top:8pt;border:1px solid #C9CED6;padding:6pt;text-align:center"><img src="../assets_ins/{os.path.basename(SGI_IMG)}" style="max-width:100%;max-height:200mm"></div>"""
    return doc("⑤ 보증보험 증권 0건 안내 · 발급 확약", [p1, p2])


# ================================================================== ④ 기업신용평가서 표지
def doc04_cover(n_pages):
    body = f"""{head("제출서류 ④", "기업신용평가서 — NICE디앤비 기업신용평가")}
<table class="t" style="margin-top:14pt"><tbody>
<tr><td class="k" style="width:22%">평가 기관</td><td class="l">NICE디앤비(신용평가업체) · CLIP 기업신용평가보고서(관리번호 11125949-202605-001)</td></tr>
<tr><td class="k">평가 대상</td><td class="l">{D.COMPANY} ({D.BIZ_NO})</td></tr>
<tr><td class="k">신용등급</td><td class="l"><b>BB-</b> · 현금흐름등급 <b>A</b></td></tr>
<tr><td class="k">평가일 · 유효기간</td><td class="l">{D.NICE_DATE} · ~2027.06.18 — 연 1회 정기 평가(재무제표 기준)의 최근 평가</td></tr>
<tr><td class="k">첨부</td><td class="l">보고서 전문 {n_pages}쪽(원본 13쪽 ‘경영진 현황’의 대표 외 임직원 2명 생년월일만 개인정보 보호를 위해 가림)</td></tr>
</tbody></table>
<p class="note" style="margin-top:8pt">※ 보고서의 본사 주소는 본점 이전(2026.07 등기) 전 주소이고, 종업원 수와 경영진 현황은 평가 당시(2026.05) 기준입니다. 현재 등기 사항은 제출서류 ① · ②와 같습니다.</p>
<p class="note">※ 별지 5 자기 평가서 4번(신용등급)의 근거 자료입니다. 연혁(원본 9쪽)은 제출서류 ⑥ 증빙 A에도 발췌해 붙였습니다.</p>"""
    return doc("④ 기업신용평가서 표지", [body])


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
    p = out("04_2_NICE_전문_가림.pdf")
    d.save(p, garbage=GARBAGE, deflate=True)
    return p

# ================================================================== ⑥ 최근 3년 1,000세대 이상 수임 실적 증빙 — 안내
def doc06_cover():
    cap_of = {c[0]: k for k, c in enumerate(CAPS_EL, 1)}
    nice_set = {"창원 센트럴 아이파크", "두산위브더제니스 오션시티", "춘천 학곡지구 중해마루힐 포레스트", "양정자이더샵SK VIEW 1·2단지", "두산위브더제니스 센트럴사하"}
    rows = ""
    for i, (nm, n, when, where, _ev) in enumerate(R3, 1):
        ev = (["NICE 연혁(A)"] if nm in nice_set else []) + ([f"공식 행사일정(B-{cap_of[nm]})"] if nm in cap_of else [])
        rows += (f'<tr><td>{i}</td><td class="l">{e(nm)}</td><td class="r">{n:,}</td><td>{e(when).replace(chr(10), "<br>")}</td><td class="l">{e(where)}</td>'
                 f'<td class="l" style="font-size:8.4pt">{" · ".join(ev)}</td></tr>')
    body = f"""{head("제출서류 ⑥", "최근 3년간 1,000세대 이상 주관사 수임 실적 — 증빙 안내")}
<p class="note" style="margin-top:4pt">기준: 제안 참여 규정 제3조 ④ · 별지 4 · 별지 5의 6번 — 공고일({D.NOTICE_DATE}) 기준 최근 3년(2023.10.21 이후) 안에 박람회를 연 1,000세대 이상 공동주택. 세대수는 NICE 연혁 기재값 · 단지 공식 세대수.</p>
<table class="t" style="margin-top:6pt;font-size:8.9pt"><thead><tr><th style="width:5%">No</th><th>단지명</th><th style="width:9%">세대수</th><th style="width:20%">개최 시기</th><th style="width:17%">장소</th><th style="width:22%">증빙</th></tr></thead>
<tbody>{rows}<tr class="sum"><td colspan="2">합계 {R3_N}건 (별지 4와 같음)</td><td class="r">{R3_HH:,}</td><td colspan="3"></td></tr></tbody></table>
<ol class="pl" style="margin-top:8pt"><li class="sm">증빙 A. NICE디앤비 기업신용평가보고서(평가 {D.NICE_DATE}) ‘연혁’ 발췌 — 1쪽(전문은 제출서류 ④) · 연혁 날짜 = 보고서 기재 월(실제 행사일은 위 표)</li>
<li class="sm">증빙 B. 박람회장 공식 행사일정 캡처 — {" · ".join(f"B-{k} {e(c[0])}({e(c[2].split('(')[0].strip())})" for k, c in enumerate(CAPS_EL, 1))} · 주최 · 주관란 = 엣지컴퍼니 · 화면 그대로</li></ol>
<p class="note">※ 레이카운티(4,470세대)는 2차 박람회가 2023.10.21 ~ 22로 공고일 기준 3년 경계라 건수에 넣지 않았습니다(연혁에는 기재). 수임 후 개최 예정인 1,000세대 이상 2곳(2027 입주 예정)도 넣지 않았습니다. 협의회가 요청하면 협약서 원본 · 정산 자료 등을 지체 없이 추가 제출합니다.</p>
<p class="body" style="font-size:9.8pt;margin-top:6pt;line-height:1.65">위 실적은 사실과 다름이 없음을 확인하며, 허위로 확인될 경우 제안 참여 규정 제9조(제안의 무효)와 공고 6항 (3)에 따른 어떠한 조치도 이의 없이 따르겠습니다.</p>
{sign().replace('class="sign"', 'class="sign" style="margin-top:6pt"').replace('class="to"', 'class="to" style="margin-top:8pt"')}"""
    return doc("⑥ 수임 실적 증빙 안내", [body])


def doc06_caps():
    items = "".join(
        f'<div class="bxc"><div class="bh"><b>B-{k}</b> {e(nm)} <span>· {e(kind)} · {e(per)} · {e(hall)}</span></div>'
        f'<img src="{pathlib.Path(f).as_uri()}" alt=""></div>' for k, (nm, f, kind, per, hall) in enumerate(CAPS_EL, 1))
    sec = (head("제출서류 ⑥ · 증빙 B", "박람회장 공식 행사일정 캡처")
           + '<p class="note" style="margin-top:4pt">출처: 벡스코(BEXCO) 홈페이지 ‘행사일정’ 상세 화면 · 창원컨벤션센터(CECO) 홈페이지 ‘전체일정’ 화면 · 주최 · 주관란 = 주식회사 엣지컴퍼니 · 화면 그대로(가공 없음)</p>'
           + f'<div class="bxs">{items}</div>')
    css = CSS + (".bxs{display:flex;flex-direction:column;gap:8pt;margin-top:8pt}.bxc{border:1px solid #c9ced6;border-radius:3pt;padding:6pt 7pt}"
                 ".bh{font-size:10pt;margin-bottom:4pt}.bh b{color:#9A7B3F;margin-right:4pt}.bh span{color:#555;font-size:9pt}"
                 ".bxc img{display:block;width:100%;max-height:68mm;object-fit:contain;object-position:left top}")
    return doc("⑥ 증빙 B 공식 행사일정", [sec], css)


# ⑥ 증빙 A — NICE 원본 9쪽 연혁 발췌(북수원 docs_bs.annex_nice와 같은 방식)
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
    text(L + 23, 51.5, "증빙 A", 8.5, "b", GOLD, "c")
    text(R, 51.5, "제출서류 ⑥ · 1,000세대 이상 수임 실적 증빙", 8.5, "r", GRAY, "r")
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
            ("원본 분량", f"전 {len(nice)}쪽 (전문은 제출서류 ④)")]
    x0, x1, xk, rh = L + 186, R, L + 186 + 70, 24
    for i, (k, v) in enumerate(info):
        y = top + i * rh
        pg.draw_rect(fitz.Rect(x0, y, xk, y + rh), color=LINE, fill=(0.945, 0.929, 0.894), width=0.6)
        pg.draw_rect(fitz.Rect(xk, y, x1, y + rh), color=LINE, width=0.6)
        text(x0 + 8, y + 15.5, k, 8.8, "b")
        text(xk + 8, y + 15.5, v, 8.8, "r", (0.1, 0.14, 0.2))
    y = top + len(info) * rh + 18
    text(x0, y, "금색 테두리 = 1,000세대 이상 박람회 주관 기록", 8.8, "r", GRAY)
    text(x0, y + 13, "(별지 4: 센트럴사하 · 양정자이 · 춘천 · 오션시티 · 창원)", 8.8, "r", GRAY)
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
    text((L + R) / 2, y + 6, "※ 연혁 날짜 = NICE 보고서 기재 월 · 실제 행사일은 별지 4 · 레이카운티(2차 2023.10.21 ~ 22)는 공고일 기준 3년 경계라 별지 4에서 뺌", 7.4, "r", GRAY, "c")
    y += 14
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
    o.set_metadata({"title": "증빙 A NICE 기업신용평가보고서 연혁 발췌", "author": D.COMPANY})
    o.save(out_path, garbage=GARBAGE, deflate=True)
    return out_path

# ================================================================== ⑦ 전담인력 배치 확약서(자유 양식)
def doc07():
    rows = [
        ("총괄 책임자", "1명", f"{D.MANAGER[1]} · 관리감독 · 협약", "협약 체결일 ~ 협약 종료일"),
        ("전담 PM", "1명 · 정직원", "협의회 연락 · 건의 관리표 · 일정 · 보고 - 이 단지만 맡음(4대보험 명부 등재자 중 협약 시 지정)", "협약 체결일 ~ 협약 종료일"),
        ("겹침 기간 추가", "1명 · 정직원", "1회차(C3) 박람회 · C3 입주 · 2회차(D3) 준비가 겹치는 기간", "2027.09 ~ 2028.04"),
        ("업무 분담", f"4개 팀 {STAFF12}명(겸임)", "영업 2 · 행사관리 4 · 이벤트 3 · 대외지원 3", "회차별"),
        ("박람회 현장", "현장 책임자 1명 + 운영 인력(예시 약 21명)", "회차별 박람회 기간 상주 · 안내 · 주차 · 안전", "회차마다 2 ~ 3일"),
    ]
    tr = "".join(f'<tr><td class="k">{e(a)}</td><td>{e(b)}</td><td class="l">{e(c)}</td><td>{e(d)}</td></tr>' for a, b, c, d in rows)
    body = f"""{head("제출서류 ⑦", "전담인력 배치 확약서")}
<p class="body">당사는 「{e(D.NOTICE)}」에 따라 협약 대상자로 선정되면, 협약 체결일부터 협약 종료일(블록 · 품목별 공동구매 무상 A/S 보증 만료일 중 가장 늦은 날)까지 아래 인력을 배치할 것을 확약합니다.</p>
<table class="t" style="margin-top:10pt"><thead><tr><th style="width:15%">구분</th><th style="width:20%">인원</th><th>역할</th><th style="width:21%">기간</th></tr></thead><tbody>{tr}</tbody></table>
<ol class="pl" style="margin-top:10pt">
<li>1. 별지 5 자기 평가서 7번(우리 단지만을 위한 전담 인력 배치 정직원 수) = <b>1인</b>이며, 2027.09 ~ 2028.04에는 1명을 더해 2명을 배치합니다.</li>
<li>2. 현장 책임자 · 전담 PM · 주요 협력업체를 바꿀 때는 귀 협의회의 사전 서면 동의를 받으며, 동의 전에는 바꾸지 않습니다(제안 참여 규정 제12조 ③).</li>
<li>3. 주관 업무를 도급 · 재하도급 · 양도하지 않습니다(별지 2). 테이블 · 의자 렌탈, 운송, 경비, 촬영 같은 물품 · 장비 임차와 단순 용역은 주관 업무가 아니며, 그 목록을 귀 협의회에 미리 알립니다.</li>
<li>4. ‘전담’은 PM에만 씁니다. 업무 분담 4개 팀 {STAFF12}명은 다른 단지 업무와 겸임하며, 개인 연락처는 협약 시 제출합니다.</li></ol>
{sign()}"""
    return doc("⑦ 전담인력 배치 확약서", [body])


# ================================================================== ⑧ 대표 계약서 — 안내(최근 1년 체결분 없음) · 가장 최근 협약서 · 환불 규정
def doc08_cover():
    body = f"""{head("제출서류 ⑧", "계약 취소 및 환불 규정 확인 가능한 대표 계약서 — 안내")}
<div class="box"><b>최근 1년(2025.10.21 이후) 안에 입주예정자협의회와 체결한 주관사 계약서: 없음</b><br>
가장 최근 체결본은 2025.08.02(에코델타시티 디에트르 더퍼스트 입주예정자협의회 · 업무협약서)입니다. 없는 서류를 있는 것처럼 만들지 않고, 대신 아래 두 가지를 냅니다.</div>
<table class="t" style="margin-top:10pt"><tbody>
<tr><td class="k" style="width:24%">⑧-1</td><td class="l">가장 최근 체결한 협의회 - 주관사 협약서 사본(2025.08.02 · 상대방 대표자 성명 · 연락처 · 계좌 가림)</td></tr>
<tr><td class="k">⑧-2</td><td class="l">이 단지에 그대로 적용할 <b>계약 취소 · 환불 규정</b>(제1 ~ 10조 · 별표) — 협약 시 협약서에 첨부하고 모든 공동구매 계약서에 붙입니다</td></tr>
</tbody></table>
<p class="note" style="margin-top:8pt">※ 규정 핵심: 계약금 {D.DEPOSIT_MAX}% 상한(맞춤 제작 · 본사 규정 품목 예외) · 취소 기한 안 전액 환불 · 환불 3영업일 이내 · 잔금은 시공 · 설치 확인 후 · 업체 불이행 시 주관사 선보상 · 최저가 차액 10배(1건당 최대 50만원 · 주관사 지급). 협의회가 요청하면 다른 협약서 원본도 열람하실 수 있습니다.</p>
{sign()}"""
    return doc("⑧ 대표 계약서 안내", [body])


CANCEL_7 = "청소·줄눈, 탄성코트, 유리막코팅, 선반·잡물, 음식물처리기, 인덕션, 벽걸이TV, LED조명"
CANCEL_15 = "미세방충망, 인테리어, 단열필름, 시스템에어컨, 포장이사"
CUSTOM = "커튼·블라인드, 중문, 안전방충망, 맞춤가구"


def doc08_rule():
    arts = [
        ("제1조 (목적)", None, f"이 규정은 {D.COMPANY}(이하 ‘주관사’)가 주관하는 {SITE} 입주박람회(1회차 C3 블록 · 2회차 D3 블록) 및 공동구매(이하 ‘공동구매’)에서 입주예정자(이하 ‘계약자’)와 참여업체 사이에 체결되는 계약의 계약금·잔금 지급 조건과 취소·환불 기준을 정하여 계약자의 권리를 보호함을 목적으로 한다."),
        ("제2조 (적용 범위)", ["공동구매를 통해 체결된 모든 품목의 계약에 적용한다. 박람회 현장 계약과 온라인 박람회(폐쇄몰) 계약을 모두 포함한다.",
                           "참여업체는 이 규정을 계약서에 반영하고 계약 체결 전에 계약자에게 설명하여야 한다.",
                           "브랜드 본사 직영 품목(가전·가구 등), 렌탈·보험·통신, 사전점검 대행은 각 본사 계약 규정을 따르되, 그 내용을 계약 전에 서면으로 고지하여야 한다."]),
        ("제3조 (계약금)", [f"계약금은 계약 총액의 <b>{D.DEPOSIT_MAX}% 이하</b>로 한다(계약금 {D.DEPOSIT_MAX}% 상한제). 다만 세대 실측 후 제작하는 맞춤 제작 품목({CUSTOM} 등)과 제2조 ③의 본사 규정 품목은 예외로 하며, 적용 품목과 계약금은 업체 선정 때 협의회 승인을 받아 단가표 · 계약서에 미리 표시한다.",
                         "계약금과 잔금 모두 카드 결제 시 현금가와 <b>동일한 가격</b>을 적용하며, 현금 결제 시 현금영수증을 발행한다."]),
        ("제4조 (잔금 지급 조건)", ["잔금은 <b>시공·설치가 끝나고 계약자가 확인한 후</b> 지급한다. 제품만 납품하는 품목은 납품·설치 확인 후 지급한다.",
                             "시공 결과 확인 시 하자·미시공 부분이 있으면 계약자는 해당 부분의 보수가 끝난 후 잔금을 지급할 수 있다."]),
        ("제5조 (취소·환불 기준)", ["품목별 취소 가능 기한은 [별표]와 같다. 기한 안에 취소하면 납부한 금액 <b>전액</b>을 환불한다.",
                             f"맞춤 제작 품목({CUSTOM})은 출고 지시 전까지 참여업체와 협의하여 취소한다. 브랜드 가전·가구는 미제작·출고 지시 전에는 전액 취소·환불한다.",
                             "참여업체가 사전 해피콜을 이행하지 않은 경우, 계약자 미동의 주문제작 건을 포함한 <b>모든 품목은 당일 취소·환불</b>할 수 있다(공급사 귀책).",
                             "입주 · 사전점검 일정이 바뀌어 시공일을 다시 잡는 경우에는 위약금 없이 일정을 재조정한다.",
                             "취소 기한이 지난 뒤의 취소는 실제 발생한 자재·제작 비용만 공제할 수 있으며, 참여업체는 공제 내역을 서면으로 제시하여야 한다. 주관사는 공제 내역의 적정성을 검토한다.",
                             "시공 지연, 계약과 다른 제품·시공(계약서상 ‘A’ 물품을 ‘B’ 물품으로 바꾼 경우 포함), 하자 미보수 등 참여업체 귀책으로 계약을 해지하는 경우에는 기한과 관계없이 납부 금액 전액을 환불한다."]),
        ("제6조 (취소 신청 및 환급)", ["취소는 참여업체 또는 주관사 콜센터 · 공식카페 신문고 · 카카오채널로 신청하며, 문자·메신저 등 기록이 남는 방법으로 한다.",
                                "환불금은 취소 확정일로부터 <b>3영업일 이내</b>에 지급하고, 카드 결제분은 같은 기한 안에 승인 취소한다.",
                                "주관사는 환불 완료 여부를 계약자에게 확인(해피콜)한다."]),
        ("제7조 (불이행 시 조치 및 주관사 책임)", ["참여업체가 취소·환불을 지연하거나 거부하면 계약자는 주관사 콜센터에 접수할 수 있다. 주관사는 사실을 확인한 뒤 계약자에게 피해 금액을 <b>먼저 보상</b>하고, 참여업체와는 계약 조항에 따라 정산한다(참여업체 특약이행각서 준용).",
                                      "불이행 업체에는 1단계 홍보정지, 2단계 해당 업체 공동구매 계약 총액의 10% 배상, 3단계 자격박탈 및 협의회 승인을 받아 전 계약을 대체업체로 이관하는 페널티를 차례로 부과하며, 1회차에서 페널티를 받은 업체는 2회차에 참가하지 못한다.",
                                      "참여업체가 도산하거나 연락이 끊긴 경우 계약자 동의를 받아 대체 업체로 사후관리를 이관하고, 무상 A/S 기간 안의 그 비용은 주관사가 부담한다.",
                                      "주관사의 보상 재원으로 하자 예치금 최대 1억원(엣지컴퍼니 자산으로 예치 · 예치 방식은 협약 때 확정)과 계약이행 · 하자보증보험(보증기간 24개월, 금액 · 기산일은 협약 때 확정)을 둔다."]),
        ("제8조 (가격 보호 — 최저가 차액 10배 보상)", [f"공동구매 품목과 브랜드·모델명이 같은 새 제품이 계약 후 7일 이내에 인근({ST['local']}) 오프라인 매장에서 더 낮은 정상 판매가로 실제 판매된 사실이 구매 영수증(판매 매장 사업자 정보 · 모델명 · 금액 기재)으로 확인되고 주관사가 해당 매장에 판매 사실을 확인하면, 주관사는 차액의 10배를 보상하고 참여업체는 판매가를 조정한다(보상금은 주관사 부담 · 참여업체 부담을 늘리지 않음).",
                                             "보상액은 1건당 50만원(해당 품목 계약금액이 더 적으면 그 금액)을 넘지 않는다(같은 세대 · 같은 품목에는 1회). 견적서 · 가격표 · 구두 안내 가격은 보상 근거가 되지 않는다.",
                                             "온라인·홈쇼핑 판매, 시공 품목, 카드 청구할인·사은품·결합할인, 전시·리퍼 상품, 법인 특판, 한정 수량 행사가는 비교 대상에서 제외한다.",
                                             "계약자는 주관사 콜센터에 접수하고, 주관사는 사실 확인 후 7일 이내에 보상금을 지급한다."]),
        ("제9조 (고지)", None, "주관사는 이 규정을 박람회장 · 온라인 박람회에 게시하고, 입주예정자협의회 카페에는 협의회 승인 후 게시하며, 모든 공동구매 계약서에 첨부한다."),
        ("제10조 (효력)", None, "이 규정은 협약 체결일부터 협약 종료일(입주박람회 종료 및 공동구매 하자 A/S 보증 기간 만료 시 · 블록 · 품목별 무상 A/S 만료일 중 가장 늦은 날)까지 체결된 계약에 적용하며, 협약 종료 후에도 해당 계약의 이행·보증 기간 동안 효력을 가진다."),
    ]
    out_ = []
    for a in arts:
        if a[1]:
            out_.append(f'<div class="art"><h3>{a[0]}</h3><ol>' + "".join(f"<li>{'①②③④⑤⑥⑦⑧'[i]} {x}</li>" for i, x in enumerate(a[1])) + "</ol></div>")
        else:
            out_.append(f'<div class="art"><h3>{a[0]}</h3><p>{e(a[2])}</p></div>')
    table = f"""<h2>[별표] 품목별 취소 가능 기한 (시공일 기준)</h2>
<table class="t"><thead><tr><th style="width:24%">취소 가능 기한</th><th>품목</th></tr></thead><tbody>
<tr><td class="k" style="text-align:center">시공일 7일 전까지</td><td class="l">{CANCEL_7}</td></tr>
<tr><td class="k" style="text-align:center">시공일 15일 전까지</td><td class="l">{CANCEL_15}</td></tr>
<tr><td class="k" style="text-align:center">출고 지시 전까지</td><td class="l">맞춤 제작 품목({CUSTOM})은 업체와 협의 후 취소 · 브랜드 가전·가구(미제작 시)</td></tr>
<tr><td class="k" style="text-align:center">본사 규정 품목</td><td class="l">렌탈 · 보험 · 통신 · 사전점검 대행 · 브랜드 본사 직영 품목 - 각 본사 계약 규정(계약 전 서면 고지)</td></tr>
<tr><td class="k" style="text-align:center">당일 취소 가능</td><td class="l">사전 해피콜 미이행 시 모든 품목(공급사 귀책)</td></tr>
</tbody></table>
<p class="note">※ 품목 구성은 블록별 수요조사 결과에 따라 협의회 승인으로 확정되며, 추가 품목의 기한은 성격이 같은 품목의 기한을 따른다.</p>"""
    summary = (f'<div class="box"><b>핵심 요약</b> &nbsp; 계약금 {D.DEPOSIT_MAX}% 이하(맞춤 제작 · 본사 규정 품목 예외) · 현금·카드 동일가 · 잔금은 시공·설치 확인 후 · '
               "품목별 취소 기한 안 전액 환불 · 환불 3영업일 이내 · 업체 불이행 시 주관사 선보상 · 최저가 차액 10배(주관사 지급)</div>")
    return doc("⑧-2 계약 취소 · 환불 규정", [head("제출서류 ⑧-2", "계약 취소 및 환불 규정 — 이 단지 적용본") + summary + "".join(out_) + table + sign()])


# ================================================================== ⑨ A/S 및 사후관리 계획서(자유 양식)
def doc09():
    p1 = f"""{head("제출서류 ⑨", "A/S 및 사후관리 계획서")}
<div class="box"><b>요약(별지 5의 10번과 같은 문장)</b> &nbsp; 한 창구 접수 → <b>24시간 안 1차 회신</b>(주말 · 공휴일 = 다음 영업일 12시) → <b>48시간 안 방문 일정 확정</b>(방문일은 입주민과 협의한 날 · 긴급 하자 우선 배정) → 업체가 24시간 안에 응하지 않으면 주관사 개입 · 사실 확인 뒤 먼저 보상 → 업체 도산 · 연락 두절 시 대체 업체 이관(무상 A/S 기간 안 비용 주관사) · 무상 A/S = 시공 품목 최소 2년 · 건설 하자는 시공사 처리(주관사는 정리 · 공문 전달 · 추적)</div>
<h2>1. 범위 — 책임부터 나눕니다</h2>
<table class="t"><thead><tr><th style="width:22%">구분</th><th>책임 주체</th><th style="width:34%">주관사가 하는 일</th></tr></thead><tbody>
<tr><td class="k">공동구매 품목 하자 · A/S</td><td class="l">주관사 · 참여업체(박람회 1 · 2회차 계약 전체)</td><td class="l">접수 · 기한 관리 · 선보상 · 이관 · 보고</td></tr>
<tr><td class="k">건설 하자(세대 · 공용부)</td><td class="l">시공사 — 접수는 시공사 하자 접수 창구</td><td class="l">협의회가 모은 목록 정리 · 공문 초안 · 전달 · 진행 추적(판정 · 보수 · 소송 대리 아님)</td></tr>
<tr><td class="k">법률 판단 · 분쟁</td><td class="l">협의회 법률 자문사</td><td class="l">필요한 자료 정리 · 전달</td></tr>
<tr><td class="k">건설 하자 기술 검토</td><td class="l">시공사(보수 책임) · {e(DNB_NAME)}</td><td class="l">협의회 요청 시 자문 의견 전달 · 현장 확인 동행</td></tr>
</tbody></table>
<h2>2. 기간 — 블록 · 품목별 만료일</h2>
<table class="t"><thead><tr><th style="width:22%">구분</th><th>1회차 · C3 블록</th><th>2회차 · D3 블록</th></tr></thead><tbody>
<tr><td class="k">입주(예정)</td><td>2027.12</td><td>2028.04</td></tr>
<tr><td class="k">시공 품목</td><td colspan="2">무상 A/S 최소 2년(시공 · 설치 완료일부터 · 계약서에 품목별 기간 기재)</td></tr>
<tr><td class="k">브랜드 제품</td><td colspan="2">제조사 보증 기간 + 설치 하자는 설치 업체 보증 · 제조사 장기 보증은 제조사 창구로 연결</td></tr>
<tr><td class="k">용역(청소 등)</td><td colspan="2">재시공 · 재방문 기준을 계약서에 기재</td></tr>
<tr><td class="k">협약 종료일</td><td colspan="2"><b>블록 · 품목별 무상 A/S 만료일 중 가장 늦은 날</b> — 날짜 없는 무제한 지원으로 남기지 않음(공고 2-(1))</td></tr>
</tbody></table>
<h2>3. 접수 창구</h2>
<table class="t"><tbody>
<tr><td class="k" style="width:22%">한 창구</td><td class="l">주관 콜센터 {D.TEL}(평일 09:00 ~ 18:00) · 공식카페 신문고 · 카카오채널(365일 접수) · 블록별 입주 지정기간 단지 안 상주 창구(위치 · 시간은 협의회 · 관리주체가 정함)</td></tr>
<tr><td class="k">기록</td><td class="l">접수 번호 · 세대 · 품목 · 업체 · 접수 시각 · 회신 · 방문 · 완료 · 지연 사유를 대장에 기록 · 협의회 요청 시 원자료 열람</td></tr>
</tbody></table>"""
    p2 = f"""{head("제출서류 ⑨ · 2", "A/S 및 사후관리 계획서 — 처리 기한 · 거점 · 담보 · 보고")}
<h2>4. 처리 기한</h2>
<table class="t"><thead><tr><th style="width:28%">단계</th><th>기한 · 방법</th></tr></thead><tbody>
<tr><td class="k">1차 회신</td><td class="l">접수 후 <b>24시간 안</b>(주말 · 공휴일 접수 = 다음 영업일 12시까지)</td></tr>
<tr><td class="k">방문 일정 확정</td><td class="l">접수 후 <b>48시간 안</b> 방문 일정 확정 · 방문은 입주민과 협의한 날 · 누수 · 전기 등 긴급 하자는 우선 배정</td></tr>
<tr><td class="k">업체 무응답</td><td class="l">업체가 24시간 안에 응하지 않으면 주관사가 개입 · 사실 확인 뒤 입주민께 먼저 보상하고 업체와 나중에 정산</td></tr>
<tr><td class="k">업체 도산 · 연락 두절</td><td class="l">계약자 동의를 받아 동종 대체 업체로 이관(협의회 승인) · 무상 A/S 기간 안 이관 비용은 주관사 부담</td></tr>
<tr><td class="k">완료 확인</td><td class="l">수리 · 재시공 후 세대 확인 → 해피콜로 종결</td></tr>
</tbody></table>
<h2>5. 관리 · 출동 거점</h2>
<table class="t"><tbody>
<tr><td class="k" style="width:28%">관리 거점</td><td class="l">경인 지사(경기도 평택시 비전동 866-3 · 상설 쇼룸) — 시공 · A/S 관리 · 출동 · 계약과 책임은 울산 본사</td></tr>
<tr><td class="k">출동</td><td class="l">경인 지사 + 공개 입찰로 뽑은 {ST['local']}권 참여 시공업체 · 직영 품목(조명 · 실링팬 · 커튼)은 본사 시공팀</td></tr>
</tbody></table>
<h2>6. 이행 담보</h2>
<table class="t"><tbody>
<tr><td class="k" style="width:28%">보증보험</td><td class="l">계약이행 · 하자보증보험 보증기간 24개월 · 협의회 피보험자 · 협약 후 발급(금액 · 기산일 · 보증 대상은 협약 때 확정)</td></tr>
<tr><td class="k">참여업체</td><td class="l">특약이행각서 9개 항(하자보수 이관 · 보증 기간 · 지연 배상 등) 징구 · 1회차 A/S 기준 미달 업체는 2회차 참가 제외</td></tr>
<tr><td class="k">선보상 재원</td><td class="l">하자 예치금 최대 1억원(엣지컴퍼니 자산 · 예치 방식은 협약 때 확정)</td></tr>
</tbody></table>
<h2>7. 보고</h2>
<table class="t"><tbody>
<tr><td class="k" style="width:28%">입주 지정기간</td><td class="l">블록별 주 1회 — 공동구매 A/S 접수 · 처리 현황 + 건설 하자 전달 · 진행 현황</td></tr>
<tr><td class="k">그 이후</td><td class="l">월 1회 — 협약 종료일까지</td></tr>
<tr><td class="k">결과보고서</td><td class="l">회차별 박람회 결과보고서 = 종료 후 30일 안(2회) · 최종 결과 보고서 = 협약 종료 후 30일 안</td></tr>
</tbody></table>
{sign()}"""
    return doc("⑨ A/S 및 사후관리 계획서", [p1, p2])


def doc09_annex():
    """본부장 10-29 'A안': 협약서 사본 앞 요지 1쪽(원문 조항 그대로 줄임 · 새 약속 없음) — 을 상호는 여기 적음(제9조 ② 동의)."""
    rows = [
        ("당사자", f"갑 {D.COMPANY} · 을 <b>{DNB_CO}</b>"),
        ("체결 · 날인", "2026.10.28 · 갑 · 을 기명날인(사본 2쪽 다음 장)"),
        ("기간", "체결일부터 1년 · 만료 1개월 전 종료 통지가 없으면 1년씩 연장 · 이미 시작된 단지는 그 단지 협약이 끝날 때까지(제10조)"),
        ("적용", "갑이 주관사로 선정되어 협의회와 협약한 단지 · 갑이 범위를 서면 요청하고 을이 수락하면 시작(제2조)"),
        ("분야 · 자문인", "건축(설계 · 건설사업관리) · 을 소속 건축사 또는 건축 분야 건설기술인 · 단지별 성명 · 자격 · 소속 서면 통지(제3조)"),
        ("자문 업무", "① 공정별 건축 기술 자문 · 협의회 질의 기술 검토 ② 하자 취약 부위 · 마감 품질 확인(사업주체가 허용하는 범위의 현장 확인) "
                     "③ 설계도서 · 설계변경 · 마감재 사양 검토 의견 ④ 기술 검토 의견서 작성 · 협의회 회의 참석 · 설명 — 협의회 또는 갑이 요청할 때(제4조)"),
        ("하지 않는 일", "법정 감리 · 하자 판정 · 보수 · 소송 대리 · 별도 설계 · 감리 용역 — 건설 하자의 보수 책임은 사업주체 · 시공사(제4조 ③)"),
        ("회신 기한", "요청받은 날부터 7영업일 안 서면 회신 · 현장 확인은 일정 협의 후 방문(제5조)"),
        ("협의회 비용", "을은 자문 대가를 협의회 · 입주예정자에게 청구하지 않음(제6조 ③)"),
        ("공정성", "그 단지의 시행 · 시공 · 분양 관계사 · 감리자 · 협의회 임원과 이해관계 없음을 서면 확인(제7조) · "
                  "비밀유지 · 개인정보 보호 · 입찰 관련 협의회 임원 · 입주예정자 개별 접촉 금지(제8조)"),
        ("표기", "‘건축 분야 기술 자문 협력사’ · ‘전속’ · ‘독점’ 표현 쓰지 않음(제9조 ④)"),
    ]
    body = f"""{head("제출서류 ⑨ · 붙임", "건축 분야 기술 자문 업무협약 — 요지")}
<div class="box">⑨ 범위 표 ‘건설 하자 기술 검토’ 줄의 협력사와 맺은 협약입니다. 아래는 협약서 조항을 줄여 옮긴 것이고, 다음 2쪽이 날인한 협약서 사본입니다.</div>
<table class="t" style="margin-top:10pt"><tbody>
{"".join(f'<tr><td class="k" style="width:20%">{a}</td><td class="l">{b}</td></tr>' for a, b in rows)}
</tbody></table>
<p class="note" style="margin-top:8pt">※ 사본의 을 사업자등록번호 · 주소 · 대표자 · 날인은 가렸습니다(가림 없는 원본은 요청 시 열람). 자문인 성명 · 자격증 사본은 협의회가 요청하면 제출합니다(제9조 ①).</p>
{sign()}"""
    return doc("⑨ 붙임 건축 자문 협약 요지", [body])


def clean_scan(src, dst):
    """사본 스캔 보정(본부장 10-29 'A안'): 회색 바탕 → 흰색 · 기울기만 바로잡음(글자 · 가림 · 날인은 그대로)."""
    import io
    from PIL import Image, ImageOps
    d, o = fitz.open(src), fitz.open()
    for pg in d:
        im = Image.open(io.BytesIO(d.extract_image(pg.get_images()[0][0])["image"])).convert("RGB")
        g = ImageOps.invert(im.convert("L").point(lambda v: 255 if v > 200 else v))
        best = max((_rowvar(g.rotate(a / 10)), a / 10) for a in range(-15, 16))[1]   # -1.5° ~ +1.5° · 0.1° 단위
        if best:
            im = im.rotate(best, resample=Image.BICUBIC, fillcolor=(255, 255, 255))
        im = im.point(lambda v: 255 if v >= 214 else round(v * 255 / 214))   # 바탕 214 이상 = 흰색 · 나머지는 같은 비율로 밝힘
        buf = io.BytesIO(); im.save(buf, "JPEG", quality=88)
        np_ = o.new_page(width=pg.rect.width, height=pg.rect.height)
        np_.insert_image(np_.rect, stream=buf.getvalue())
        print(f"  사본 보정 {pg.number + 1}쪽 · 기울기 {best:+.1f}°")
    o.save(dst, garbage=GARBAGE, deflate=True)
    return dst


def _rowvar(g):
    """가로 줄 투영의 분산 — 글줄이 수평일 때 가장 큼(기울기 찾기)."""
    s = g.resize((g.width // 6, g.height // 6))
    w, h = s.size
    px = s.load()
    rows = [sum(px[x, y] for x in range(w)) for y in range(h)]
    m = sum(rows) / h
    return sum((r - m) ** 2 for r in rows)


# ================================================================== ⑮ 하자 보수 이행각서(자유 양식)
def doc15():
    items = [
        "참여업체마다 특약이행각서(하자보수 이관 · 보증 기간 · 지연 배상 등 9개 항)를 받아 두고, 그 이행을 관리합니다.",
        "참여업체가 하자 접수 후 24시간 안에 응하지 않으면 당사가 개입하여, 사실 확인 뒤 입주예정자에게 먼저 보상하고 업체와 나중에 정산합니다.",
        "참여업체가 폐업하거나 연락이 끊기면 계약자 동의를 받아 동종 대체 업체로 하자보수를 이관하며, 무상 A/S 기간 안의 이관 비용은 당사가 부담합니다.",
        "무상 A/S 기간은 시공 품목 최소 2년으로 하고(브랜드 제품은 제조사 보증 · 용역은 재시공 기준), 품목별 기간을 계약서에 적습니다.",
        "<b>대상 밖</b>: 시공사가 책임지는 건설 하자(세대 마감 · 설비 · 공용부)는 이 각서의 보수 대상이 아니며, 당사는 협의회가 모은 목록의 정리 · 공문 전달 · 처리 추적만 합니다.",
        "이행 담보로 협약 후 귀 협의회를 피보험자로 계약이행 · 하자보증보험(보증기간 24개월)을 발급받아 증권 사본을 제출합니다.",
        "위 사항을 위반하면 협약 해지와 손해배상 청구를 이의 없이 받아들입니다.",
    ]
    lis = "".join(f"<li>{i}. {x}</li>" for i, x in enumerate(items, 1))
    body = f"""{head("제출서류 ⑮", "하자 보수 이행각서", True)}
<p class="body">당사는 「{e(D.NOTICE)}」의 제안 참가 자격 ⑥(공동구매 제품 전체에 대한 계약 이행 등의 명확한 하자담보 이행 능력)과 관련하여, {SITE} 공동구매 박람회(1회차 C3 블록 · 2회차 D3 블록)에서 입주예정자가 참여업체와 맺은 <b>공동구매 제품 전체</b>의 하자에 대해, 계약서에 적은 무상 A/S 기간 동안 다음을 이행할 것을 각서합니다.</p>
<ol class="pl">{lis}</ol>
{sign()}"""
    return doc("⑮ 하자 보수 이행각서", [body])


# ================================================================== ⑯(원문 ⑭) 비밀 유지 서약서(자유 양식)
def doc16():
    items = [
        "당사는 본 제안 과정에서 귀 협의회로부터 받은 단지 정보 · 자료 · 입주예정자 정보와 제안 · 평가 과정에서 알게 된 정보를 이 제안 목적 외에 사용하지 않습니다(제안 참여 규정 제13조).",
        "위 정보를 제3자에게 제공하지 않으며, 협약 후 참여업체에도 업무에 필요한 범위만 제공하고 같은 의무를 지워 관리 · 감독합니다.",
        "<b>당사 본사의 다른 사업부(조명 · 커튼 · 실링팬 등) 영업에도 쓰지 않습니다.</b>",
        "선정되지 않으면 결과 통지 후 7일 안에, 선정되면 협약 종료 후에 받은 자료를 파기하고 그 사실을 귀 협의회에 알립니다.",
        "위반으로 귀 협의회 또는 입주예정자에게 손해가 생기면 민 · 형사상 모든 책임을 집니다.",
    ]
    lis = "".join(f"<li>{i}. {x}</li>" for i, x in enumerate(items, 1))
    body = f"""{head("제출서류 ⑯ (원문 번호 ⑭)", "비밀 유지 서약서", True)}
<p class="body">당사는 「{e(D.NOTICE)}」에 참여함에 있어 다음 사항을 지킬 것을 서약합니다.</p>
<ol class="pl">{lis}</ol>
{sign()}"""
    return doc("⑯ 비밀 유지 서약서", [body])


# ================================================================== ⑰(원문 ⑮) 입찰 결과에 대한 이의 제기 금지 서약서(자유 양식)
def doc17():
    items = [
        "귀 협의회가 정한 업체 선정 기준 · 평가 방법 · 평가 임원진 구성에 대하여 일체의 이의를 제기하지 않습니다(공고 6항 (1)).",
        "1차 서류 적격심사 · 2차 PT 평가 결과와 최종 협약대상자 선정 결과에 대하여 민 · 형사상 어떠한 이의도 제기하지 않습니다(제안 참여 규정 제11조 ③ · 별지 2).",
        "심사에서 탈락하더라도 평가 결과(점수 · 순위 등)를 공개하지 않는 것(제6조 ④)에 동의합니다.",
        "접수 마감 이후 서류 보완 · 변경을 요구하지 않으며, 제출 서류의 반환을 요구하지 않습니다(공고 6항 (2) · 제6조 ③).",
    ]
    lis = "".join(f"<li>{i}. {x}</li>" for i, x in enumerate(items, 1))
    body = f"""{head("제출서류 ⑰ (원문 번호 ⑮)", "입찰 결과에 대한 이의 제기 금지 서약서", True)}
<p class="body">당사는 「{e(D.NOTICE)}」에 참여함에 있어 다음 사항을 서약합니다.</p>
<ol class="pl">{lis}</ol>
{sign()}"""
    return doc("⑰ 이의 제기 금지 서약서", [body])


# ================================================================== 00 제출서류 목록(통합 PDF 맨 앞)
def doc00(spans, have_scan):
    yy, mm, dd = ymd()
    rows = "".join(f'<tr><td>{no}</td><td class="l">{e(t)}</td><td class="l" style="font-size:8.4pt">{e(note)}</td><td>{a}{"" if a == b else f" ~ {b}"}</td></tr>'
                   for no, t, note, a, b in spans)
    body = f"""{head("제출서류 목록", "입주박람회 주관사 제안 · 제출서류 (제안 참여 규정 제4조)")}
<table class="info" style="margin-top:10pt"><tr><th>제안사</th><td>{D.COMPANY} · 대표이사 {D.CEO}</td><th>책임자</th><td>{D.MANAGER[1]} {D.MANAGER[0]}</td></tr>
<tr><th>접수</th><td colspan="3">{D.SUBMIT_TO} · 마감 {D.DEADLINE} · 제목 “{e(D.MAIL_TITLE)}”</td></tr></table>
<table class="t" style="margin-top:8pt;font-size:8.8pt"><thead><tr><th style="width:6%">No</th><th style="width:36%">제출 서류(제4조)</th><th>내용 · 발급일</th><th style="width:12%">이 파일 쪽</th></tr></thead><tbody>{rows}</tbody></table>
<p class="note" style="margin-top:6pt">※ 모든 서류를 제4조 번호 순서대로 PDF 1개로 병합했습니다(PDF 책갈피 = 번호별). 원문에 ⑭ · ⑮가 두 번 나와 뒤의 두 서류(비밀 유지 서약서 · 이의 제기 금지 서약서)를 ⑯ · ⑰로 적었습니다(순서는 원문 그대로).</p>
<p class="note">※ {"별지 1 ~ 5와 사용인감계는 법인인감 날인본입니다" if have_scan else "별지 1 ~ 5의 날인은 확인용 직인입니다(법인인감 날인본으로 교체 예정)"} · 자유 양식 서류는 사용인감(⑫ 사용인감계로 신고) · 4대보험 명부 · 신용평가서 · 인감증명서 · 등기부 · 지방세 증명서의 개인정보는 가렸습니다.</p>
<div class="sign" style="margin-top:10pt"><div class="d">{yy}년 {mm}월 {dd}일</div><div class="who">{D.COMPANY}</div></div>"""
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

def rejpeg(pg, q=85):
    """화소 가림 뒤 PNG로 커진 이미지를 JPEG로 되돌림 — 더 작아질 때만(상주 10-26)."""
    for x in {im[0] for im in pg.get_images(full=True)}:
        pm = fitz.Pixmap(pg.parent, x)
        if pm.alpha or pm.n > 3:
            pm = fitz.Pixmap(fitz.csRGB, pm)
        jb = pm.tobytes("jpeg", jpg_quality=q)
        if len(jb) < len(pg.parent.xref_stream_raw(x)) * 0.8:
            pg.replace_image(x, stream=jb)


def masked(src, name, rects):  # {쪽: [Rect]} — 화소까지 지움(상주 법정 1차 좌표 · 같은 원본)
    d_ = fitz.open(src)
    for pno, rs in rects.items():
        for r_ in rs:
            d_[pno].add_redact_annot(fitz.Rect(*r_), fill=(0.6, 0.6, 0.6))
        d_[pno].apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS)
        rejpeg(d_[pno])
    o_ = out(name)
    d_.save(o_, garbage=GARBAGE, deflate=True)
    return o_


def relabel_one(src, page, dst, old, new, title):
    """협약서 사본 1쪽(고양 '제출서류 9 · 별첨 3-k' 머리글) → 엘리프 머리글 · 제목(본문 이미지는 그대로)."""
    d = fitz.open(src)
    d.select([page])
    pg = d[0]
    F = fitz.Font(fontfile=os.path.join(FONTS, "Pretendard-Bold.ttf"))
    hits = pg.search_for(old)
    assert len(hits) == 1, (old, hits)
    r = hits[0]
    full = pg.search_for(old + f"-{page + 1} (협약일 순)")
    rr = full[0] if full else r
    pg.add_redact_annot(fitz.Rect(rr.x0 - 1, rr.y0 - 1, rr.x1 + 1, rr.y1 + 1), fill=(1, 1, 1))
    pg.add_redact_annot(fitz.Rect(40, 52.5, 560, 76.5), fill=(1, 1, 1))
    pg.apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS)
    rejpeg(pg)
    tw = fitz.TextWriter(pg.rect)
    tw.append((rr.x0, rr.y1 - 2.2), new, font=F, fontsize=round(rr.height * 0.72, 1))
    tw.write_text(pg, color=(0.6, 0.48, 0.25))
    tw = fitz.TextWriter(pg.rect)
    tw.append((43, 71), title, font=F, fontsize=16)
    tw.write_text(pg, color=(0.051, 0.118, 0.2))
    d.save(dst, garbage=GARBAGE, deflate=True)
    return dst



def annex_label(src, dst, label):
    """붙임 사본(스캔 이미지) 위 여백에 '제출서류 ⑨ · 붙임' 머리글 한 줄 · 쪽 번호만 얹음(본문 · 가림은 그대로)."""
    d = fitz.open(src)
    F = fitz.Font(fontfile=os.path.join(FONTS, "Pretendard-Bold.ttf"))
    for i, pg in enumerate(d):
        tw = fitz.TextWriter(pg.rect)
        tw.append((36, 20), f"{label} · {i + 1}/{len(d)}", font=F, fontsize=7.6)
        tw.write_text(pg, color=(0.6, 0.48, 0.25))
    d.set_metadata({"title": label, "author": D.COMPANY})
    d.save(dst, garbage=GARBAGE, deflate=True)
    return dst

def evidence_check():
    t = fitz.open(f"{EV}/사업자등록증.pdf")[0].get_text()
    assert "2026 년10 월23 일" in t and "전시,박람회및행사대행업" in t, "사업자등록증 발급일 · 종목 확인 실패"
    t = fitz.open(f"{EV}/국세_납세증명서.pdf")[0].get_text()
    assert "2026 년10 월23 일" in t and "2026 년11 월22 일" in t, "국세 납세증명서 발급일 · 유효기간 확인 실패"
    assert len(fitz.open(ROSTER)) == 2, "4대보험 가입자 명부(2026.10.23 · 가림본) 2쪽 확인 실패"
    assert len(fitz.open(R500_DOC)) == 3, "주관사 협약서 3건 확인 실패"
    assert os.path.exists(DNB) and len(fitz.open(DNB)) == 2, f"건축 기술 자문 협약서 사본(2쪽 · 을 정보 가림) 확인 실패: {DNB}"
    for p in (f"{EV}/법인등기부등본.pdf", f"{EV}/지방세_납세증명서.pdf", NICE_SRC, SGI_IMG, P10, INGAM) + tuple(c[1] for c in CAPS_EL):
        assert os.path.exists(p), f"없음: {p}"


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

    # ---- 별지 1 ~ 5 + 사용인감계(법인인감 날인 출력용 6쪽 — 사용인감계는 사용인감 칸만 디지털 직인)
    F = [("13_1_별지1_제안참가신청서", form1()), ("13_2_별지2_확약서", form2()), ("13_3_별지3_청렴이행각서", form3()),
         ("14_1_별지4_운영실적표", form4()), ("14_2_별지5_자기평가서", form5())]
    raw = [fit(render(n, h), 1) for n, h in F]
    gam_raw = stamped(fit(render("12_2_사용인감계_직인전", form_gam()), 1))
    if TODOS:
        print("[노란 칸]", " / ".join(dict.fromkeys(TODOS)))
        if final:
            sys.exit("--final: 노란 칸이 남아 있어 멈춤")
    pr = fitz.open()
    for p in raw + [gam_raw]:
        pr.insert_pdf(fitz.open(p))
    pr.set_metadata({"title": "법인인감 날인 출력용 6쪽(별지 1 ~ 5 · 사용인감계)", "author": D.COMPANY})
    pr.save(out("법인인감_날인출력용_6쪽.pdf"), garbage=GARBAGE, deflate=True)
    have_scan = os.path.exists(SEAL_SCAN)
    if have_scan:
        sc = fitz.open(SEAL_SCAN)
        assert len(sc) == 6, f"법인인감 스캔은 6쪽(별지 1 · 2 · 3 · 4 · 5 · 사용인감계 순)이어야 함: {SEAL_SCAN}"
        forms, gam = [(SEAL_SCAN, [i]) for i in range(5)], (SEAL_SCAN, [5])
    else:
        forms, gam = [(stamped(p), None) for p in raw], (gam_raw, None)
    # ---- 증빙 · 자유 양식
    biz = fitz.open(f"{EV}/사업자등록증.pdf")
    for pg_ in biz:
        for a in list(pg_.annots()):
            pg_.delete_annot(a)
    biz_p = out("01_사업자등록증.pdf")
    biz.save(biz_p, garbage=GARBAGE, deflate=True)
    reg_p = masked(f"{EV}/법인등기부등본.pdf", "02_법인등기부등본_가림.pdf", {1: [(203, 163, 556, 177), (30, 176, 50, 187)]})
    ltax_p = masked(f"{EV}/지방세_납세증명서.pdf", "11_2_지방세_납세증명서_가림.pdf", {0: [(118, 229, 194, 242)]})
    nice04 = nice_full(NICE_SRC)
    c04 = fit(render("04_1_표지", doc04_cover(len(fitz.open(nice04)))), 1)
    d05 = stamped(fit(render("05_보증보험_0건_발급확약", doc05()), 2))
    c06 = stamped(fit(render("06_1_실적증빙_안내", doc06_cover()), 1))
    a06 = stamped(annex_nice(NICE_SRC, out("06_2_증빙A_NICE연혁발췌.pdf")))
    b06 = fit(render("06_3_증빙B_공식행사일정", doc06_caps()), 1, 2)
    d07 = stamped(fit(render("07_전담인력_배치_확약서", doc07()), 1))
    c08 = stamped(fit(render("08_1_대표계약서_안내", doc08_cover()), 1))
    m08 = relabel_one(R500_DOC, 2, out("08_2_최근협약서_20250802.pdf"), "제출서류 9 · 별첨 3", "제출서류 ⑧-1 · 가장 최근 체결 협약서(2025.08.02)",
                      "협의회 - 주관사 협약서 사본(가장 최근 체결본)")
    r08 = stamped(fit(render("08_3_계약취소_환불규정", doc08_rule()), 2, 3))
    d09 = stamped(fit(render("09_AS_사후관리_계획서", doc09()), 2))
    a09 = stamped(fit(render("09_2_붙임_건축자문_협약_요지", doc09_annex()), 1))
    n09 = annex_label(clean_scan(DNB, out("09_3_건축자문_협약서_보정.pdf")), out("09_3_붙임_건축자문_협약서_가림.pdf"),
                      "제출서류 ⑨ · 붙임 — 건축 분야 기술 자문 업무협약서 사본(2026.10.28 · 을 정보 가림)")
    d15 = stamped(fit(render("15_하자보수_이행각서", doc15()), 1))
    d16 = stamped(fit(render("16_비밀유지_서약서", doc16()), 1))
    d17 = stamped(fit(render("17_이의제기_금지_서약서", doc17()), 1))
    nP = len(fitz.open(P10))

    def plan():
        """(번호, 이름, 내용, [(pdf, 쪽 목록 또는 None, 책갈피)])"""
        return [
            ("①", "사업자등록증 사본", f"{D.ISSUE['biz']} 발급 · 종목 전시, 박람회 및 행사 대행업", [(biz_p, None, None)]),
            ("②", "법인 등기부등본(최근 1개월 이내)", f"{D.ISSUE['reg']} 발급 · 자본금 2억원 · 대표 주소 가림", [(reg_p, None, None)]),
            ("③", "4대 보험 가입자 명부", "2026.10.23 발급 · 13명 · 성명 · 주민번호 가림", [(ROSTER, None, None)]),
            ("④", "기업신용평가서", f"NICE디앤비 · BB- · 현금흐름 A · 평가 {D.NICE_DATE}(유효기간 안)",
             [(c04, None, "표지"), (nice04, None, "NICE 기업신용평가보고서 전문(가림)")]),
            ("⑤", "최근 1년간 발행한 보증보험 증권(협의회와 주관사 간)", "0건 안내 · 다른 용역 계약보증 1건 사본(가림) · 협약 후 발급 확약", [(d05, None, None)]),
            ("⑥", "최근 3년간 1,000세대 이상 주관사 수임 실적 증빙서류", f"{R3_N}건 · {R3_HH:,}세대 · 안내 + A NICE 연혁 + B 공식 행사일정",
             [(c06, None, "증빙 안내"), (a06, None, "증빙 A NICE 연혁 발췌"), (b06, None, "증빙 B 공식 행사일정")]),
            ("⑦", "전담인력 배치 확약서", "전담 PM 1명 + 2027.09 ~ 2028.04 1명 추가", [(d07, None, None)]),
            ("⑧", "계약취소 및 환불규정 확인 가능한 대표 계약서", "최근 1년 체결분 없음 안내 · 가장 최근 협약서(2025.08.02) · 이 단지 환불 규정",
             [(c08, None, "안내"), (m08, None, "⑧-1 가장 최근 체결 협약서"), (r08, None, "⑧-2 계약 취소 · 환불 규정")]),
            ("⑨", "A/S 및 사후관리 계획서", f"범위 · 기간 · 접수 · 처리 기한 · 거점 · 담보 · 보고 · 붙임 = {DNB_NAME}",
             [(d09, None, "A/S 및 사후관리 계획서"), (a09, None, "붙임 · 건축 분야 기술 자문 업무협약 요지"), (n09, None, "붙임 · 건축 분야 기술 자문 업무협약서 사본")]),
            ("⑩", "입찰 제안서", f"{nP}쪽", [(P10, None, None)]),
            ("⑪", "국세 및 지방세 완납 증명서", f"국세 {D.ISSUE['tax']} · 지방세 {D.ISSUE['ltax']} 발급(유효 ~2026.11.22)",
             [(f"{EV}/국세_납세증명서.pdf", None, "국세 납세증명서"), (ltax_p, None, "지방세 납세증명서(휴대번호 가림)")]),
            ("⑫", "인감증명서 및 사용인감계(최근 1개월 이내)", f"법인인감증명서 {D.INGAM_DATE} 발급(주민번호 뒷자리 가림) · 사용인감계",
             [(INGAM, None, "법인인감증명서"), (gam[0], gam[1], "사용인감계")]),
            ("⑬", "참가신청서 및 확약서, 청렴이행각서(별지서식 1 · 2 · 3)", "원문 그대로 · " + ("법인인감 날인" if have_scan else "확인용 직인"),
             [(forms[0][0], forms[0][1], "별지서식1 제안 참가 신청서"), (forms[1][0], forms[1][1], "별지서식2 확약서"), (forms[2][0], forms[2][1], "별지서식3 청렴이행각서")]),
            ("⑭", "적격심사 자기평가서 및 입주박람회 운영 실적표(별지서식 4 · 5)", f"별지 4 실적 {R3_N}건 · 별지 5 자기 평가서 10항목",
             [(forms[3][0], forms[3][1], "별지서식4 운영 실적표"), (forms[4][0], forms[4][1], "별지서식5 자기 평가서")]),
            ("⑮", "하자 보수 이행각서", "공동구매 제품 전체 · 1 · 2회차", [(d15, None, None)]),
            ("⑯", "비밀 유지 서약서(원문 번호 ⑭)", "제13조 · 본사 다른 사업부 영업에도 쓰지 않음", [(d16, None, None)]),
            ("⑰", "입찰 결과에 대한 이의 제기 금지 서약서(원문 번호 ⑮)", "6항 (1) · 제11조 ③", [(d17, None, None)]),
        ]

    def assemble():
        items = plan()
        spans, toc, pg0 = [], [], 2
        for no, name, note, parts in items:
            n = sum(len(pl) if pl else len(fitz.open(p)) for p, pl, _ in parts)
            spans.append((no, name, note, pg0, pg0 + n - 1))
            pg0 += n
        p00 = fit(render("00_제출서류목록", doc00(spans, have_scan)), 1)
        o = fitz.open()
        o.insert_pdf(fitz.open(p00))
        toc.append([1, "제출서류 목록", 1])
        docs = {}
        src_txt = page_texts(p00)
        for (no, name, note, parts), (_n, _nm, _no, a, _b) in zip(items, spans):
            toc.append([1, f"{no} {name}", a])
            pg = a
            for p, pl, bm in parts:
                d = docs.setdefault(p, fitz.open(p))
                sel = pl if pl else list(range(len(d)))
                if bm:
                    toc.append([2, bm, pg])
                runs, cur = [], [sel[0]]
                for i in sel[1:]:
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
        o.set_metadata({"title": f"{D.COMPANY} · {SITE} 주관사 제안서 · 제출서류 ① ~ ⑰", "author": D.COMPANY})
        name = "[주식회사 엣지컴퍼니]_엘리프한신더휴수원_주관사_제안서" + ("" if have_scan else "_직인본") + ".pdf"
        path = os.path.join(SUBMIT, name)
        o.save(path, garbage=2, deflate=True, deflate_fonts=True, deflate_images=True, use_objstms=1)  # garbage=3(중복 객체 합치기)은 크롬 PDF끼리 글꼴이 섞여 글자가 깨짐(10-26 목록 + ④ 표지 확인)
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
        lines.append(f"{no} {name} — p.{a}" + ("" if a == b else f" ~ {b}") + f" · {note}")
    lines += ["", f"통합본: {full}  {len(fitz.open(full))}쪽 · {mb_f:.1f}MB"]
    if not have_scan:
        lines += ["", f"조치: 법인인감 — 작업/{PFX}법인인감_날인출력용_6쪽.pdf 출력 → 6쪽 모두 법인인감 날인(사용인감계는 법인인감 칸 · 대표자 (인)) → 스캔(6쪽 PDF) → {SEAL_SCAN} 에 두고 다시 실행"]
    if TODOS:
        lines += ["", "노란 칸: " + " / ".join(dict.fromkeys(TODOS))]
    text = "\n".join(lines) + "\n"
    pathlib.Path(WORK, "제출현황.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
