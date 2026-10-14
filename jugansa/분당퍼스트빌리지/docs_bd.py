# -*- coding: utf-8 -*-
"""e편한세상 분당 퍼스트빌리지 입주박람회 주관사 입찰 — 공고 7항 제출서류 14종 생성기(A4 세로).

  01 입찰참가 신청서(자유양식 + 제출서류 목록)         02 입주박람회 주관사 제안서 = build_bd.py 산출물(목록에만 표기)
  03 사업자등록증 사본                                04 법인등기부등본 · 법인인감증명서
  05 국세 · 지방세 완납증명서                          06 4대보험 완납증명서(+ 고용·산재 완납 · 참고 가입자 명부)
  07 대표자 범죄사실확인서                             08 품목 환불 기준 및 사후관리 · 하자 대응 방안서
  09 ~ 13 [서식 1 ~ 5] — 공고 원문 양식(문구 · 배치) 그대로, 빈칸만 채움
  14 기타 — ① 대표자 결격사유 부존재 서약서 ② 요약제안서 ③ 서울보증 계약보증보험증권 사본 ④ NICE 기업신용평가보고서
          ⑤ 실적 확약서(붙임 카페 공지 · BEXCO 행사일정) — 제안서가 '실적 증빙은 제출서류 14'라고 적었으므로 함께 묶는다(HW_IN_14)
08 방안서의 환불 규정(제1 ~ 10조 · 별표)과 민원 처리 기준은 build_bd.py의 _ARTS1 · _ARTS2 · _C7 · _C15 · _CU · CPL을
그대로 읽어 쓴다(같은 기준 — 제안서 문구를 고치면 다음 빌드에 자동 반영).
직인(배경 투명 PNG)은 신청서 · 방안서 · 서식 1 ~ 5 · 결격사유 서약서 · 실적 확약서의 '(인)' 자리에 찍는다(../동탄파라곤3차/stamp.py).
법인인감은 디지털로 만들지 않는다(실물만).

조치 필요 자리(노란 표시 → [확인 필요] 집계, --final이면 멈춤)
  4 법인인감증명서: 보유본 2026.10.08 = 공고일(10.12) 이전 → 재발급본을 EV/법인인감증명서.pdf로 두고 data.py INGAM_DATE 기재
  7 범죄사실확인서: 대표 본인 발급본을 EV/대표자_범죄경력회보서.pdf로 두거나, 협의회가 서약서 갈음을 승인하면 CRIME_SUBST에 승인 내용 기재

사용: python docs_bd.py <NICE.pdf> <직인.png> [--final]
  결과 PDF · HTML은 깃 제외(.gitignore: *.pdf, 엣지컴퍼니_*.html).
"""
import ast
import html
import importlib.util
import json
import os
import pathlib
import re
import subprocess
import sys

import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "요약제안서"), os.path.join(HERE, "..", "동탄파라곤3차")]
import data as D  # noqa: E402
from build import find_chrome  # noqa: E402

e = html.escape
PFX = "엣지컴퍼니_분당퍼스트빌리지_"
ST = D.SITE
SITE = ST["name"]  # e편한세상 분당 퍼스트빌리지
TODOS = []

SP = "/tmp/claude-0/-home-user-edge-company/a96d9eb6-5244-5d3f-9f1b-6f379ac2a82c/scratchpad"
EV = os.environ.get("BD_EVIDENCE", f"{SP}/evidence")      # 증빙 원본(깃 제외)
ROSTER = f"{SP}/cs_sub/엣지컴퍼니_철산역자이_06_4대보험_사업장가입자명부.pdf"  # 성명 가운데 글자 · 주민번호 뒷자리 가림본(2026.10.02 발급)
SGI = f"{EV}/SGI_계약보증보험증권_세종스마트시티_20260907.pdf"
INGAM_PDF = f"{EV}/법인인감증명서.pdf"          # 공고일(10.12) 이후 재발급본을 이 이름으로 두면 04에 자동으로 들어간다
CRIME_PDF = f"{EV}/대표자_범죄경력회보서.pdf"    # 대표 본인 발급본(주민번호 뒷자리 가림 후)을 이 이름으로 두면 07에 자동으로 들어간다
CRIME_SUBST = None  # 협의회가 '결격사유 부존재 서약서로 갈음'을 승인하면 승인 내용(예: "2026.10.16 협의회 메일 회신")
HW_IN_14 = True     # 14에 ⑤ 실적 확약서(카페 공지 · BEXCO 붙임) 포함 — 제안서 p12 · 9항 대응표가 '실적 증빙 = 제출서류 14'로 적음
CAP_DIR = f"{SP}/hw/cap"  # 실적 확약서 캡처 원본(가림본이 assets_ins/cafe_*.png에 없을 때만 사용)


def todo(x):
    TODOS.append(x)
    return f'<mark class="todo">{e(x)}</mark>'


def _ceo_birth():
    """대표 생년월일 — 개인정보라 저장소에 두지 않는다. 깃 제외 org_private.json('ceo_birth')에서만 읽는다(이 폴더 → 탕정 · 지웰, 읽기만).
    이 폴더에 org_private.json을 새로 만들지 않는다: reorg.py가 그 파일이 있으면 조직도에 실명을 넣는다."""
    for d in (HERE, os.path.join(HERE, "..", "탕정푸르지오센터파크"), os.path.join(HERE, "..", "지웰엘리움양주덕계역")):
        p = os.path.join(d, "org_private.json")
        if os.path.exists(p):
            v = json.load(open(p, encoding="utf-8")).get("ceo_birth")
            if v:
                return v
    return None


CEO_BIRTH = D.CEO_BIRTH or _ceo_birth()


def _from_build_bd(names):
    """build_bd.py의 모듈 수준 상수(환불 규정 조문 · 별표 품목 · 컴플레인 처리 기준)를 실행 없이 그대로 읽는다 — 제안서와 같은 기준."""
    tree = ast.parse(pathlib.Path(HERE, "build_bd.py").read_text(encoding="utf-8"))
    ns = {"D": D, "ST": ST}
    for node in tree.body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id in names):
            exec(compile(ast.Module([node], []), "build_bd.py", "exec"), ns)
    miss = [n for n in names if n not in ns]
    assert not miss, f"build_bd.py에서 찾지 못함: {miss}"
    return ns


RULE = _from_build_bd(["_C7", "_C15", "_CU", "_ARTS1", "_ARTS2", "CPL"])

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
h3.s{font-size:10.4pt;font-weight:800;color:#0D1E33;margin:8pt 0 3pt;break-after:avoid}
.t{width:100%;border-collapse:collapse;font-size:9.3pt;line-height:1.45}
.t th{background:#0D1E33;color:#fff;font-weight:700;padding:4pt 6pt;border:.6pt solid #0D1E33;text-align:center}
.t td{padding:3.4pt 6pt;border:.6pt solid #C9CED6;text-align:center;vertical-align:middle}
.t td.l{text-align:left}.t td.r{text-align:right;font-variant-numeric:tabular-nums}
.t tr{break-inside:avoid}
.t td.k{font-weight:700;background:#F6F7F9;text-align:left;white-space:nowrap}
.box{border:1pt solid #C8A86A;background:#FBF8F1;border-radius:4pt;padding:7pt 11pt;margin-top:10pt;font-size:9.8pt;line-height:1.65}
.box b{color:#0D1E33}
p.body{margin-top:12pt;font-size:10.5pt;line-height:1.85}
.note{font-size:8.8pt;color:#5B6676;margin-top:5pt;line-height:1.55}
.art{margin-top:6pt;break-inside:avoid}
.art h4{font-size:10.2pt;font-weight:800;color:#0D1E33}
.art p,.art li{font-size:9.6pt;line-height:1.58}
.art ol{list-style:none;margin-top:1pt}
.art ol li{padding-left:14pt;text-indent:-14pt;margin-top:1pt}
.flow{display:flex;align-items:stretch;gap:4pt;margin-top:4pt;font-size:8.8pt;line-height:1.35}
.flow div{flex:1;border:.8pt solid #C8A86A;border-radius:4pt;padding:5pt 5pt;background:#FBF8F1;text-align:center}
.flow div b{display:block;color:#0D1E33;font-size:9.2pt;margin-bottom:1pt}
.flow i{font-style:normal;color:#9A7B3F;font-weight:800;align-self:center}
.sign{margin-top:16pt;text-align:center;break-inside:avoid}
.sign .d{font-size:11pt;letter-spacing:.06em}
.sign .who{margin-top:6pt;font-size:12pt;font-weight:700}
.sign .seal{color:#5B6676;font-size:10pt;font-weight:400;margin-left:30pt}
.to{margin-top:18pt;text-align:center;font-size:12.5pt;font-weight:800;color:#0D1E33}
/* 신청서(자유양식) */
.ap{color:#111;font-size:10.5pt;line-height:1.8}
.ap h1{text-align:center;font-size:22pt;letter-spacing:.45em;color:#111;margin:6pt 0 12pt}
.ap .ft{width:100%;border-collapse:collapse;font-size:10pt;margin-top:4pt}
.ap .ft th,.ap .ft td{border:.8pt solid #333;padding:5.5pt 9pt;vertical-align:middle;line-height:1.5}
.ap .ft th{background:#F2F2F2;font-weight:700;text-align:center;white-space:nowrap;width:19%}
.ap h3{font-size:11pt;margin:13pt 0 3pt}
.ap p.tx{margin-top:13pt;text-indent:10pt;text-align:justify;line-height:1.9}
.ap .dt{text-align:center;margin-top:20pt;font-size:12pt;letter-spacing:.15em}
.ap .sgt{margin:14pt 0 0 auto;border-collapse:collapse;font-size:11.5pt;line-height:2.3}
.ap .sgt td{padding:0 6pt;vertical-align:middle;white-space:nowrap}
.ap .sgt td.w{vertical-align:top;padding-right:12pt}
table.t.kv{break-inside:avoid}
.ap .to2{margin-top:26pt;text-align:center;font-size:13pt;font-weight:800}
/* 조치 필요 자리 */
.act{border:2.5pt solid #E0B400;background:#FFF8D6;border-radius:6pt;padding:16pt 18pt;margin-top:22pt}
.act .bd{display:inline-block;background:#FFE066;color:#0D1E33;font-weight:800;font-size:10pt;padding:2pt 9pt;border-radius:3pt;letter-spacing:.08em}
.act h1{font-size:18pt;margin-top:8pt}
.act ul{margin:10pt 0 0 14pt;font-size:10.4pt;line-height:1.85}
"""

# 공고 [서식 1 ~ 5] 원본 양식(공고 PDF 6 ~ 10쪽) — 회색 제목 띠 · 10pt 본문(줄 간격 넓게) · 4행 표(업체명/주소/대표자 (인)/연락처) · 날짜 · 귀중
FORM_CSS = r"""
@page{size:A4;margin:20mm 21mm 14mm 18mm}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Malgun Gothic','맑은 고딕','Pretendard',sans-serif;color:#111;font-size:10pt;word-break:keep-all;
  -webkit-print-color-adjust:exact;print-color-adjust:exact}
.sf{height:736pt;display:flex;flex-direction:column}
.sf .hd{background:#D9D9D9;padding:6pt 8pt 6pt 4pt;font-size:13pt;font-weight:700;line-height:1.4}
.sf p{margin-top:14pt;line-height:31pt;font-size:10pt}
.sf p.f{margin-top:4pt}
.sf table{width:100%;border-collapse:collapse;margin-top:22pt}
.sf th{width:91pt;background:#F2F2F2;border:.8pt solid #666;font-weight:700;font-size:10pt;height:37pt;text-align:center;white-space:pre}
.sf td{border:.8pt solid #666;padding:0 10pt;font-size:10pt}
.sf tr.rep th,.sf tr.rep td{height:51pt}
.sf td .in{float:right;font-weight:700;font-size:10.6pt;margin-right:16pt}
.sf .dt{margin-top:auto;padding-top:40pt;text-align:center;font-size:11pt;white-space:pre}
.sf .to{margin:66pt 0 30pt;text-align:center;font-size:12pt;font-weight:700}
"""

HEAD = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{t}</title>'
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">'
        '<style>{css}</style></head><body>')


def doc(title, sections, css=CSS):
    return HEAD.format(t=e(title), css=css) + "".join(f'<section class="pg">{s}</section>' for s in sections) + "</body></html>"


def ymd():
    return D.SIGN_DATE


def head(label, title, center=False):
    return (f'<div class="top"><div class="lb">{e(label)}</div><div class="co">{D.COMPANY} · 입주박람회 주관사</div></div>'
            f'<h1 class="{"c" if center else ""}">{e(title)}</h1>'
            f'<div class="case" style="{"text-align:center" if center else ""}">건명 : {e(D.NOTICE)} ({D.NOTICE_DATE} 공고)</div>')


def sign(prefix=""):
    yy, mm, dd = ymd()
    return (f'<div class="sign"><div class="d">{yy}년 {mm}월 {dd}일</div>'
            f'<div class="who">{prefix}{D.COMPANY} &nbsp; 대표이사 &nbsp; {D.CEO}<span class="seal">(인)</span></div></div>'
            f'<div class="to">{e(D.CLIENT)} 귀중</div>')


def issued(key, label):
    v = D.ISSUE.get(key)
    return f"{v} 발급" if v else todo(f"{label} 재발급일(공고일 이후)")


# ------------------------------------------------------------------ 파일 경로
def out(name):
    return os.path.join(HERE, PFX + name)


P02 = out("02_입주박람회_주관사_제안서.pdf")
P02_HTML = out("02_입주박람회_주관사_제안서.html")
P14_SUM = out("14_요약제안서.pdf")
P14_SUM_HTML = out("14_요약제안서.html")

N01 = "01_입찰참가신청서"
N03 = "03_사업자등록증_사본"
N04 = "04_법인등기부등본_법인인감증명서"
N05 = "05_국세_지방세_완납증명서"
N06 = "06_4대보험_완납증명서"
N07 = "07_대표자_범죄사실확인서"
N08 = "08_품목환불기준_사후관리_하자대응_방안서"
FORMS = [  # (제출 번호, 파일 이름, 서식 번호, 제목, [본문 문단], 번호 목록)
    ("09", "09_입찰결과_평가절차_확인서약서_서식1", 1, "입찰 결과 및 평가 절차 확인 서약서", [
        f"당사는 {SITE} 입주예정자협의회에서 시행하는 입주박람회 주관사 선정 입찰에 참가함에 있어 입찰 진행 절차와 평가 및 선정 결과에 대하여 입주예정자협의회의 결정과 해석에 따를 것을 서약합니다.",
        "또한 입찰공고문 · 제출서류 · 평가기준 및 최종 선정 결과는 입주예정자협의회의 결정에 따르며 부정한 행위 또는 허위 사실이 확인될 경우 선정 취소 및 손해배상 책임을 부담할 것에 동의합니다.",
        "단 절차적 문의사항에 한해 협의회 내부 기준에 따라 검토할 수 있으며 법령에서 정한 범위를 초과하여 입찰자의 권리를 제한하지 않습니다.",
    ], []),
    ("10", "10_하자보수_사후관리_이행각서_서식2", 2, "하자보수 및 사후관리 이행각서", [
        f"당사는 {SITE} 입주예정자협의회에서 시행하는 입주박람회 행사와 관련하여 당사 또는 당사가 섭외·관리한 참여업체가 납품·시공·설치한 물품과 공사에 하자가 발생할 경우 계약 조건과 보증기간에 따라 신속히 하자보수 또는 원상복구가 이루어질 수 있도록 성실히 관리·지원할 것을 서약합니다.",
        "하자보수 지연 또는 미이행으로 입주예정자에게 손해가 발생한 경우 당사는 입예협의 정당한 요청에 성실히 응하고 참여업체와 함께 필요한 조치를 이행할 것을 확약합니다.",
    ], []),
    ("11", "11_비밀유지서약서_서식3", 3, "비밀유지 서약서", [
        "당사는 귀 협의회에서 실시하는 입주박람회 주관사 선정 입찰에 참가함에 있어 본 입찰 과정에서 취득한 입주예정자 정보 · 협의회 내부자료 · 평가 및 협의 내용 · 참여업체 조건 등 일체의 정보를 제3자에게 누설하거나 본 입찰 목적 외로 사용하지 않을 것을 서약합니다.",
        "이를 위반할 경우 향후 귀 협의회에서 시행하는 모든 입찰과 협약에서 제외될 수 있음을 인식하며 귀 협의회와 입주예정자에게 발생한 손해에 대하여 민·형사상 책임을 부담할 것을 확약합니다.",
    ], []),
    ("12", "12_패찰시_개별박람회_단지영업행위_금지서약서_서식4", 4, "패찰 시 개별 입주박람회 및 단지 영업행위 금지 서약서", [
        f"당사는 {SITE} 입주박람회 주관사 선정 입찰에서 최종 선정되지 않을 경우 본 단지 입주예정자를 대상으로 별도의 입주박람회 · 사전예약 · 방문판매 · 온라인 단체영업 또는 이와 유사한 영업행위를 진행하지 않을 것을 서약합니다.",
        "이를 위반하여 입주예정자 혼선 · 가격질서 저해 · 입예협 공식 행사 운영 방해 또는 손해가 발생할 경우 당사는 관련 손해배상과 입예협의 정보공개 조치 등에 이의를 제기하지 않을 것을 확약합니다.",
        "단 입주예정자협의회의 사전 서면 승인 또는 공식 요청이 있는 경우는 예외로 합니다.",
    ], []),
    ("13", "13_청렴계약_이행준수서약서_서식5", 5, "청렴계약 이행 준수 서약서", [
        f"당사는 {SITE} 입주예정자협의회에서 시행하는 입주박람회 주관사 선정 입찰에 참여함에 있어 공정하고 투명한 거래질서 확립을 위하여 다음 사항을 준수할 것을 서약합니다.",
    ], [
        "유리한 입찰 또는 특정인의 낙찰을 위한 담합 · 협정 · 합의 등 자유경쟁을 부당하게 저해하는 일체의 불공정 행위를 하지 않겠습니다.",
        "입찰·계약 체결 과정에서 입예협 운영진과 회원에게 직·간접적으로 금품·향응 등 부당한 이익을 제공하지 않겠습니다.",
        "입주박람회 운영 시 모든 참여업체에 균등한 기회를 제공하며 품목별 참여업체 간 부당한 가격 담합, 특정 업체의 독점을 유도하는 행위, 동종업체 비방, 입주민의 선택권을 제한하는 행위를 하지 않겠습니다.",
        "본 서약을 위반할 경우 입찰 참가자격 제한 · 협약 해지 등 입예협의 조치에 대하여 민·형사상 어떠한 이의도 제기하지 않을 것을 확약합니다.",
    ]),
]
N14 = "14_기타_결격사유서약서_요약제안서_보증증권_신용평가"


def p02_pages():
    return len(fitz.open(P02)) if os.path.exists(P02) else None


def p14_sum_pages():
    return len(fitz.open(P14_SUM)) if os.path.exists(P14_SUM) else None


# ================================================================== 01 입찰참가 신청서(자유양식) + 제출서류 목록
def submit_rows(n08):
    n02 = p02_pages()
    ingam = (f"법인인감증명서 {D.INGAM_DATE} 발급" if D.INGAM_DATE else
             todo("법인인감증명서 — 공고일(10.12) 이후 발급본으로 교체(보유본 10.08 발급)"))
    if os.path.exists(CRIME_PDF):
        crime = "범죄·수사경력 회보서 — 대표자 본인 발급본(범죄경력회보서 발급시스템)"
    elif CRIME_SUBST:
        crime = f"협의회 승인({e(CRIME_SUBST)})에 따라 14 ① 대표자 결격사유 부존재 서약서로 갈음"
    else:
        crime = todo("대표자 범죄사실확인서 — 대표 본인 발급본 또는 협의회 승인 시 결격사유 서약서(14 ①)로 갈음")
    n14 = ["① 대표자 결격사유 부존재 서약서(공고 9항)", f"② 요약제안서 {p14_sum_pages() or ''}쪽",
           "③ 서울보증 계약보증보험증권 사본(보증증권 발급 이력 · 공고 4항 8)", f"④ NICE디앤비 기업신용평가보고서(평가 {D.NICE_DATE})"]
    if HW_IN_14:
        n14.append("⑤ 실적 확약서(1,000세대 이상 주관 10개 단지 · 붙임 카페 공지 · BEXCO 행사일정)")
    return [
        ("1", "입찰참가 신청서", "자유양식 · 본 서류(제출서류 목록 포함)", "1부"),
        ("2", "입주박람회 주관사 제안서", (f"{n02}쪽 · " if n02 else "") + "공고 8항 필수 포함 9항목 대응표 수록", "1부"),
        ("3", "사업자등록증 사본", f"{issued('biz', '사업자등록증')}(공고일 이후)", "1부"),
        ("4", "법인등기부등본 · 법인인감증명서", f"등기사항전부증명서(현재 유효사항) {issued('reg', '등기부등본')} · {ingam}", "각 1부"),
        ("5", "국세 및 지방세 완납증명서", f"국세 {issued('tax', '국세 납세증명서')} · 지방세 {issued('ltax', '지방세 납세증명서')}(유효 ~2026.11.13)", "각 1부"),
        ("6", "4대보험 사업장 가입증명서 또는 완납증명서", f"4대 사회보험료 완납증명서(건강·연금, {D.WANNAP_DATE} 발급) · 고용·산재보험료 완납증명서(근로복지공단, {D.WANNAP_DATE} 발급) · 참고: 사업장 가입자 명부", "1부"),
        ("7", "대표자 범죄사실확인서", crime, "1부"),
        ("8", "품목 환불 기준 및 사후관리·하자 대응 방안서", f"취소·환불 규정(제1 ~ 10조 · 별표) · 하자 대응 체계 · 민원 대응 절차 · {n08}쪽", "1부"),
        ("9", "입찰 결과 및 평가 절차 확인 서약서", "[서식 1]", "1부"),
        ("10", "하자보수 및 사후관리 이행각서", "[서식 2]", "1부"),
        ("11", "비밀유지 서약서", "[서식 3]", "1부"),
        ("12", "패찰 시 개별 입주박람회 및 단지 영업행위 금지 서약서", "[서식 4]", "1부"),
        ("13", "청렴계약 이행 준수 서약서", "[서식 5]", "1부"),
        ("14", "기타 입예협이 필요하다고 인정하는 자료", "<br>".join(n14), "선택"),
    ]


def doc01(n08):
    m = D.MANAGER
    yy, mm, dd = ymd()
    p1 = f"""<div class="ap"><h1>입찰 참가 신청서</h1>
<table class="ft"><tr><th>입 찰 건 명</th><td>{SITE} 입주예정자협의회 입주박람회 주관사 선정<br>
<span style="font-size:9pt;color:#555">입예협 공고 제2026-1호 · {D.NOTICE_DATE} 공고 · 접수 마감 {D.DEADLINE}</span></td></tr></table>
<h3>■ 신청업체</h3>
<table class="ft"><tr><th>상 &nbsp; &nbsp; 호</th><td>{D.COMPANY}</td><th>대 표 자</th><td>대표이사 {D.CEO}</td></tr>
<tr><th>사업자등록번호</th><td>{D.BIZ_NO}</td><th>법인등록번호</th><td>{D.CORP_NO}</td></tr>
<tr><th>본사 소재지</th><td colspan="3">{D.ADDRESS}</td></tr>
<tr><th>설 립 일</th><td>{D.FOUNDED}</td><th>대표 전화</th><td>{D.TEL}</td></tr>
<tr><th>이 메 일</th><td colspan="3">{D.EMAIL}</td></tr></table>
<h3>■ 담당(책임)자</h3>
<table class="ft"><tr><th>성 &nbsp; &nbsp; 명</th><td>{m[0]}</td><th>직 &nbsp; &nbsp; 위</th><td>{m[1]}</td></tr>
<tr><th>휴 대 전 화</th><td>{m[2]}</td><th>이 메 일</th><td>{D.EMAIL}</td></tr></table>
<p class="tx">당사는 「{SITE} 입주예정자협의회」가 공고한 입주박람회 주관사 선정 입찰(입예협 공고 제2026-1호)에 참가하고자, 공고문과 제출서류 및 평가·협약 조건을 충분히 숙지하고 공고 사항을 모두 수락합니다. 주관사로 선정될 경우 협약 내용을 성실히 이행할 것을 확약하며, 공고 7항 제출서류를 붙임과 같이 첨부하여 입찰 참가를 신청합니다.</p>
<p style="margin-top:8pt;font-size:10pt">붙임 &nbsp;제출서류 목록 1부(다음 쪽).</p>
<div class="dt">{yy}년 &nbsp; {mm}월 &nbsp; {dd}일</div>
<table class="sgt"><tr><td rowspan="2" class="w">신청인</td><td>상 &nbsp; &nbsp; 호 :</td><td><b>{D.COMPANY}</b></td></tr>
<tr><td>대 표 자 :</td><td><b>대표이사 {D.CEO}</b><span style="margin-left:34pt">(인)</span></td></tr></table>
<div class="to2">{SITE} 입주예정자협의회 귀중</div></div>"""
    rows = "".join(f'<tr><td>{n}</td><td class="l">{e(t)}</td><td class="l">{r}</td><td>{q}</td></tr>' for n, t, r, q in submit_rows(n08))
    p2 = f"""{head("입찰참가 신청서 붙임", "제출서류 목록")}
<h2>공고 7항 제출서류 (공고 순서 · 번호 그대로)</h2>
<table class="t"><thead><tr><th style="width:6%">No</th><th style="width:31%">서류 (공고 7항)</th><th>제출 내용 · 발급일</th><th style="width:7%">부수</th></tr></thead><tbody>{rows}</tbody></table>
<p class="note">※ 3 · 4 · 6은 공고일({D.NOTICE_DATE}) 이후 발급본, 5는 유효기간 이내 발급본입니다. 파일 이름은 ‘엣지컴퍼니_분당퍼스트빌리지_번호_서류명.pdf’로 공고 순서와 같습니다.</p>
<p class="note">※ 14 ④ 기업신용평가보고서(평가 {D.NICE_DATE} · 유효 ~2027.06.18)의 본사 주소는 본점 이전(2026.07.02 등기) 전 주소입니다. 현재 본점은 위 신청서의 소재지와 같습니다(제출서류 3 · 4).</p>
<p class="note">※ 접수: {D.SUBMIT_TO} (PDF) · 메일 제목 「{D.MAIL_TITLE}」 · 마감 {D.DEADLINE}</p>"""
    return doc("1 입찰참가 신청서", [p1, p2])


# ================================================================== 4 · 7 조치 필요 자리(제출 전 실제 서류로 교체)
def action_page(no, title, items):
    lis = "".join(f"<li>{x}</li>" for x in items)
    return doc(f"{no} 조치 필요", [f"""{head(f"제출서류 {no}", title)}
<div class="act"><span class="bd">조치 필요 · 제출 전 교체</span><h1>{e(title)}</h1><ul>{lis}</ul></div>"""])


def doc04_action():
    todo("법인인감증명서 — 공고일(10.12) 이후 발급본으로 교체(보유본 10.08 발급)")
    return action_page("4", "법인인감증명서 — 공고일 이후 발급본으로 교체", [
        "공고 7항 4: 법인등기부등본 · 법인인감증명서 각 1부 — <b>공고일(2026.10.12) 이후 발급본</b>.",
        "보유본은 2026.10.08 발급 → 공고일 이전이라 제출할 수 없습니다(이 쪽 앞의 등기부등본은 2026.10.14 발급본).",
        "조치: 법인인감증명서를 다시 발급받아 증빙 폴더에 ‘법인인감증명서.pdf’로 두고, data.py <b>INGAM_DATE</b>에 발급일을 적은 뒤 docs_bd.py를 다시 실행하면 이 쪽이 실제 서류로 바뀝니다.",
        "인감증명서의 개인정보(주민등록번호 뒷자리 등)는 가린 뒤(픽셀로 굳혀) 넣습니다.",
    ])


def doc07_action():
    todo("대표자 범죄사실확인서 — 대표 본인 발급본 또는 협의회 승인 시 결격사유 서약서(14 ①)로 갈음")
    return action_page("7", "대표자 범죄사실확인서 — 대표 본인 발급 또는 서약서 갈음", [
        "공고 7항 7: 대표자 범죄사실확인서 1부 — <b>범죄경력회보서 발급시스템 공식 발급본</b>.",
        "방법 ① 대표자 본인이 경찰청 범죄경력회보서 발급시스템에서 발급(정식 명칭 ‘범죄 · 수사경력 회보서’) → 증빙 폴더에 ‘대표자_범죄경력회보서.pdf’로 두고 docs_bd.py 다시 실행.",
        "방법 ② 협의회가 승인하면 제출서류 14 ① <b>대표자 결격사유 부존재 서약서</b>로 갈음 → docs_bd.py의 CRIME_SUBST에 승인 내용(일자 · 방법)을 적고 다시 실행.",
        "회보서에는 목적 외 사용 시 처벌 문구(형의 실효 등에 관한 법률 제10조)가 인쇄되어 있습니다 — 협의회에 메일로 질의 중(공고 3항: 문의는 접수 이메일로만).",
    ])


def doc07_subst():
    return doc("7 대표자 범죄사실확인서", [f"""{head("제출서류 7", "대표자 범죄사실확인서")}
<div class="box" style="margin-top:18pt;font-size:10.5pt"><b>협의회 승인에 따른 갈음</b><br>
공고 7항 7 대표자 범죄사실확인서는 귀 협의회의 승인({e(CRIME_SUBST)})에 따라 <b>제출서류 14 ① 대표자 결격사유 부존재 서약서</b>로 갈음합니다.
서약 내용이 사실과 다를 경우 공고 9항 11) · 10항 10)에 따른 선정 취소 등 귀 협의회의 조치를 이의 없이 받아들입니다.</div>"""])


# ================================================================== 6 참고 표지(가입자 명부)
def doc06_ref():
    return doc("6 참고", [f"""{head("제출서류 6 · 참고", "4대보험 사업장 가입자 명부 (참고)")}
<div class="box" style="margin-top:16pt;font-size:10.2pt">
공고 7항 6의 제출서류는 앞의 <b>완납증명서 2종</b>입니다 — 4대 사회보험료 완납증명서(국민건강보험공단 · 건강 · 연금, {D.WANNAP_DATE} 발급) ·
고용 · 산재보험료 완납증명서(근로복지공단, {D.WANNAP_DATE} 발급, 자진신고 사업장이라 따로 발급).<br>
다음 쪽 사업장 가입자 명부({D.ROSTER_DATE} 발급)는 임직원 4대보험 가입 현황을 보여 드리는 <b>참고 자료</b>입니다.
성명 가운데 글자와 주민등록번호 뒷자리는 개인정보 보호를 위해 가렸습니다.</div>"""])


# ================================================================== 8 품목 환불 기준 및 사후관리 · 하자 대응 방안서
DEFECT = [  # 제안서 '하자 접수 책임 구분' 쪽과 같은 내용
    ("건설사 시공 · 공용부", "세대 마감 · 설비 하자, 공용부 시설", f"시공사({ST['builder']}) · 사업주체({ST['developer_short']}) 하자 처리 창구", "접수 대행 · 회신 추적 · 현장 확인 지원 · 정기 보고"),
    ("공동구매 납품 · 시공", "박람회에서 계약한 품목의 설치 · 제품 하자", "참여업체 + 주관사 책임([서식 2])", "48시간 하자보수 원칙 · 업체 미응답 시 개입 · 선보상"),
    ("업체 부도 · 미시공", "참여업체 폐업 · 연락 두절 · 시공 중단", "주관사 책임 처리", "동종업체 이관 · A/S 비용 주관사 부담 · 이행보증 · 예치금"),
    ("성능 향상 · 추가 설치", "조경 · 조명 · 집기 개선, 시설 추가", "입예협 · 관리주체 결정 사항", "하자와 구분 · 도면 · 예산 · 운영비 검토 후 추진"),
]
REPORT = [  # 제안서 '보고' 쪽과 같은 내용
    ("정례 진행 보고", "입예협 정례회의마다", "진행 상황 · 미결 건의 목록 · 다음 일정 · 시공사 회신 현황"),
    ("하자처리 현황 보고", "입주 후 정기(주기는 입예협과 협의)", "하자 접수 · 처리 완료 · 지연 건과 사유 · 재접수"),
    ("입주박람회 결과보고서", "박람회 종료 후", "공동구매 진행현황 · A/S 접수현황 · 하자처리 현황 · 민원처리 결과"),
    ("최종 결과 보고서", "입주 후 1년 운영 관리 종료 시", "계약 · 환불 · A/S · 하자 처리 결과 · 하자 예치금 사용 내역"),
]


def _arts(arts):
    o = ""
    for h, items in arts:
        if len(items) == 1:
            o += f'<div class="art"><h4>{h}</h4><p>{items[0]}</p></div>'
        else:
            o += f'<div class="art"><h4>{h}</h4><ol>' + "".join(f"<li>{'①②③④⑤⑥⑦⑧'[i]} {x}</li>" for i, x in enumerate(items)) + "</ol></div>"
    return o


def doc08():
    C7, C15, CU = RULE["_C7"], RULE["_C15"], RULE["_CU"]
    p = f"""{head("제출서류 8", "품목 환불 기준 및 사후관리 · 하자 대응 방안서")}
<div class="box"><b>핵심 요약</b> &nbsp; 계약금 {D.DEPOSIT_MAX}% 이하 · 현금·카드 동일가 · 잔금은 시공·설치 확인 후 · 품목별 취소 기한 안 전액 환불(업체 귀책은 기한과 관계없이) ·
환불 3영업일 이내 · 한 창구 접수 → <b>24시간 안에 1차 회신</b> → <b>48시간 하자보수 원칙</b> · 업체 미응답 시 <b>주관사 선보상</b> · 무상 A/S 최소 2년(업체 · 품목별 상이)</div>
<p class="note">공고 대응: 4항 9) 취소 · 환불 기준과 하자 · 분쟁 대응 절차 · 4항 10) A/S 대책 · 사후보증기간 · 손해배상 · 5항 4) · 10) · 7항 8(취소 · 환불 기준과 민원 대응 절차 포함) · 8항 6) · 9).
아래 기준은 입주박람회 주관사 제안서(제출서류 2)의 계약 취소 · 환불 규정 전문 · 하자 대응 · 주관 콜센터 쪽과 같습니다.</p>
<h2>1. 품목 취소 · 환불 기준 — 계약 취소 · 환불 규정</h2>
{_arts(RULE["_ARTS1"])}{_arts(RULE["_ARTS2"])}
<h3 class="s">[별표] 품목별 취소 가능 기한 (시공일 기준)</h3>
<table class="t"><thead><tr><th style="width:22%">취소 가능 기한</th><th>품목</th></tr></thead><tbody>
<tr><td class="k" style="text-align:center">시공일 7일 전까지</td><td class="l">{C7}</td></tr>
<tr><td class="k" style="text-align:center">시공일 15일 전까지</td><td class="l">{C15}</td></tr>
<tr><td class="k" style="text-align:center">출고 지시 전까지</td><td class="l">맞춤 제작 품목({CU})은 업체와 협의 후 취소 · 브랜드 가전·가구(미제작 시)</td></tr>
<tr><td class="k" style="text-align:center">본사 규정 품목</td><td class="l">렌탈 · 보험 · 통신 · 사전점검 대행 · 브랜드 본사 직영 품목 - 각 본사 계약 규정(계약 전 서면 고지)</td></tr>
<tr><td class="k" style="text-align:center">당일 취소</td><td class="l">사전 해피콜 미이행 시 모든 품목(공급사 귀책)</td></tr>
</tbody></table>
<p class="note">※ 품목 구성은 입예협 수요조사 결과에 따라 확정되며, 추가 품목의 기한은 성격이 같은 품목의 기한을 따릅니다.</p>

<h2>2. 사후관리 · 하자 대응 체계</h2>
<h3 class="s">2-1. 접수 창구와 처리 기한</h3>
<table class="t kv"><tbody>
<tr><td class="k" style="width:19%">한 창구 접수</td><td class="l">주관 콜센터 {D.TEL}(평일 09:00 ~ 18:00) · 온라인 365일 접수(입예협 카페 신문고 · 카카오채널 · 홈페이지) — 접수 내용은 모두 기록합니다.</td></tr>
<tr><td class="k">회신 · 처리</td><td class="l"><b>24시간 안에 1차 회신</b> · <b>48시간 하자보수 원칙</b> · 처리 후 해피콜로 완료 확인(시공 품목은 입주민 확인 서명)</td></tr>
<tr><td class="k">책임자</td><td class="l">{D.MANAGER[1]} {D.MANAGER[0]}(총괄 책임 · {D.MANAGER[2]}) · 단지 전담 PM 1명 지정(성명 · 연락처는 협약 시 제출)</td></tr>
<tr><td class="k">운영 기간</td><td class="l">주관 창구는 입주 후 1년 운영 · 품목 무상 A/S 최소 2년(업체 · 품목별 상이) · 협약 종료 후에도 해당 계약의 이행 · 보증 기간 동안 규정 효력 유지(규정 제10조)</td></tr>
<tr><td class="k">시공 · A/S 거리</td><td class="l">{ST['local']} 시공업체 우선 선정 — 48시간 A/S가 가능한 거리 · 전기 · 조명은 당사({D.ELEC_LICENSE})가 직접 검토 · 시공</td></tr>
</tbody></table>
<h3 class="s">2-2. 하자 유형별 처리 책임 구분</h3>
<table class="t"><thead><tr><th style="width:17%">접수 유형</th><th style="width:24%">예</th><th style="width:26%">처리 책임</th><th>주관사 역할</th></tr></thead><tbody>
{"".join(f'<tr><td class="k">{a}</td><td class="l">{b}</td><td class="l">{c}</td><td class="l">{d}</td></tr>' for a, b, c, d in DEFECT)}
</tbody></table>
<p class="note">※ 시공 하자를 공동구매 업체에 떠넘기지 않고, 공동구매 하자를 시공사 탓으로 돌리지 않습니다. 참여업체는 A/S 기간 · 하자 처리 기준을 계약 조건으로 받아들인 업체만 선정합니다.</p>

<h2>3. 민원 대응 절차</h2>
<div class="flow"><div><b>① 접수</b>콜센터 · 카페 · 카카오 · 홈페이지 한 창구 · 기록</div><i>›</i>
<div><b>② 유형 분류</b>시공사 하자 · 공동구매 · 업체 사정 · 성능 향상</div><i>›</i>
<div><b>③ 책임 주체 연결</b>참여업체 · 시공사 · 입예협</div><i>›</i>
<div><b>④ 기한 추적</b>24시간 1차 회신 · 48시간 하자보수</div><i>›</i>
<div><b>⑤ 미응답 시 선보상</b>주관사가 먼저 보상 후 업체 정산</div><i>›</i>
<div><b>⑥ 완료 · 보고</b>해피콜 · 결과보고서</div></div>
<h3 class="s">민원(컴플레인) 유형별 처리 기준</h3>
<table class="t"><thead><tr><th style="width:17%">품목</th><th style="width:22%">컴플레인 예시</th><th>해결 방법</th><th style="width:17%">처리 기준</th></tr></thead><tbody>
{"".join(f'<tr><td class="k">{a}</td><td class="l">{b}</td><td class="l">{c}</td><td>{d}</td></tr>' for a, b, c, d in RULE["CPL"])}
</tbody></table>
<p class="note">※ 민원 처리에 쓰는 개인정보는 처리 목적에만 쓰고, 입예협 보고에는 동 · 호수 · 연락처를 싣지 않습니다([서식 3] 비밀유지).</p>

<h2>4. 손해배상 · 보상 재원</h2>
<table class="t kv"><tbody>
<tr><td class="k" style="width:19%">주관사 선보상</td><td class="l">참여업체가 취소 · 환불 · 하자보수를 지연하거나 거부하면, 주관사가 사실을 확인한 뒤 계약자에게 피해 금액을 <b>먼저 보상</b>하고 참여업체와는 계약 조항에 따라 정산합니다(규정 제7조 · [서식 2]).</td></tr>
<tr><td class="k">업체 도산 · 미시공</td><td class="l">동종업체로 사후관리를 이관하고, 그 A/S 비용은 주관사가 전액 부담합니다.</td></tr>
<tr><td class="k">하자 예치금</td><td class="l">최대 1억원 — 엣지컴퍼니 자산으로 예치(참여업체에게 걷은 돈이 아님) · 선보상 재원 · 사용 내역 공개. 예치 금액은 단지 규모와 입예협 협의로 정합니다.</td></tr>
<tr><td class="k">이행보증보험</td><td class="l">2년 · 최대 10억원 — 증권 금액은 협약 때 단지 규모에 맞춰 확정하고 증권 실물을 입예협에 제출합니다(공고 4항 8). 보증증권 발급 이력: 서울보증 계약보증보험증권 사본(제출서류 14 ③).</td></tr>
<tr><td class="k">업체 패널티</td><td class="l">1단계 홍보정지 → 2단계 총액 10% 배상 → 3단계 자격박탈 · 입예협 승인을 받아 전 계약을 대체업체로 이관.</td></tr>
<tr><td class="k">가격 보호</td><td class="l">최저가 차액 10배 보상(규정 제8조 — 동일 브랜드 · 모델 · 새 제품 · 계약 후 7일 이내 인근 오프라인 매장 · 온라인 판매 · 시공 품목 등 제외).</td></tr>
</tbody></table>

<h2>5. 보고 · 공개</h2>
<table class="t"><thead><tr><th style="width:22%">보고</th><th style="width:26%">시점</th><th>담는 내용</th></tr></thead><tbody>
{"".join(f'<tr><td class="k">{a}</td><td>{b}</td><td class="l">{c}</td></tr>' for a, b, c in REPORT)}
</tbody></table>
<p class="body" style="font-size:10pt;margin-top:10pt">당사는 위 기준을 모든 공동구매 계약서에 첨부하고, 협약 시 입예협과 협의하여 협약서에 그대로 반영하겠습니다.</p>
{sign()}"""
    return doc("8 품목 환불 기준 및 사후관리 · 하자 대응 방안서", [p])


# ================================================================== 9 ~ 13 [서식 1 ~ 5] — 공고 원문 양식
def form_doc(no, title, paras, items):
    yy, mm, dd = ymd()
    ps = "".join(f'<p class="{"f" if i == 0 else ""}">{e(x)}</p>' for i, x in enumerate(paras))
    ps += "".join(f"<p>{i}. {e(x)}</p>" for i, x in enumerate(items, 1))
    contact = f"{D.TEL} (대표) · {D.MANAGER[2]} ({D.MANAGER[1]} {D.MANAGER[0]})"
    body = f"""<div class="sf"><div class="hd">[ 서식 {no} ]&nbsp;&nbsp; {e(title)}</div>{ps}
<table><tr><th>업 체 명</th><td>{D.COMPANY}</td></tr>
<tr><th>주    소</th><td>{D.ADDRESS}</td></tr>
<tr class="rep"><th>대 표 자</th><td>대표이사 {D.CEO}<span class="in">(인)</span></td></tr>
<tr><th>연 락 처</th><td>{e(contact)}</td></tr></table>
<div class="dt">{yy} 년    {mm} 월    {dd} 일</div>
<div class="to">{SITE} 입주예정자협의회 귀중</div></div>"""
    return doc(f"[서식 {no}] {title}", [body], css=FORM_CSS)


# ================================================================== 14 ① 대표자 결격사유 부존재 서약서
def doc14_1():
    birth = e(CEO_BIRTH) if CEO_BIRTH else todo("대표자 생년월일 — org_private.json(ceo_birth)")
    items = [
        "금고 이상의 실형을 선고받고 그 집행이 끝나거나(집행이 끝난 것으로 보는 경우를 포함합니다) 집행이 면제된 날부터 2년이 지나지 않은 사람에 해당하지 않습니다.",
        "금고 이상의 형의 집행유예를 선고받고 그 유예기간 중에 있는 사람에 해당하지 않습니다.",
        "파산선고를 받고 복권되지 않은 사람에 해당하지 않습니다.",
        "사기 · 횡령 · 배임 · 업무방해 등 업무와 관련된 범죄로 형을 선고받고 그 형이 실효되지 않은 사람에 해당하지 않습니다.",
        f"대표자 본인 및 배우자 또는 직계존비속은 {SITE} 당첨자가 아닙니다(공고 9항 10).",
        "당사와 대표자는 금품 · 향응 제공, 담합, 중대한 법규 위반, 세무 위반 또는 입예협 관련 분쟁으로 계약 해지 · 선정 취소된 이력이 없으며, 현재 입예협과 분쟁 중이지 않습니다(공고 4항 7 · 9항 4 · 7).",
    ]
    lis = "".join(f"<li>{'①②③④⑤⑥'[i]} {x}</li>" for i, x in enumerate(items))
    body = f"""{head("제출서류 14 ①", "대표자 결격사유 부존재 서약서", True)}
<table class="info" style="margin-top:16pt"><tr><th>상호</th><td>{D.COMPANY}</td><th>법인등록번호</th><td>{D.CORP_NO}</td></tr>
<tr><th>대표자 성명</th><td>대표이사 {D.CEO}</td><th>생년월일</th><td>{birth}</td></tr>
<tr><th>본사 소재지</th><td colspan="3">{D.ADDRESS}</td></tr></table>
<p class="body">본인은 {D.COMPANY}의 대표이사로서 「{e(D.NOTICE)}」({D.NOTICE_DATE})에 참가하면서, 당사와 본인이 공고 9항 1) ~ 10)의 입찰 참가 제한 및 무효 사유에 해당하지 않음을 서약합니다.
특히 공고 9항 9)의 ‘대표자 범죄사실확인서를 포함한 제출 서류 검토 결과 업무 진행상 하자나 문제’와 관련하여, 공동주택관리법상 동별 대표자 결격사유(제14조제4항)를 참고한 아래 기준(①~③)과 업무 관련 범죄 기준(④) 및 공고 9항 10 · 4항 7의 사항(⑤ · ⑥)을 스스로 확인하였습니다.</p>
<div class="art" style="margin-top:8pt"><ol style="font-size:10.4pt">{lis.replace("<li>", '<li style="margin-top:5pt;font-size:10.4pt;line-height:1.7">')}</ol></div>
<p class="body">위 내용이 사실과 다르거나 중요한 사항을 누락한 것으로 확인될 경우, 선정 이후라도 공고 9항 11) · 10항 10)에 따른 <b>선정 취소 및 협약 무효 · 해지</b> 등 귀 협의회의 조치를 이의 없이 받아들이겠습니다.
귀 협의회가 요청하면 관련 법령이 허용하는 범위에서 확인 서류를 지체 없이 제출하겠습니다.</p>
{sign("서약인 : ")}"""
    return doc("14 ① 대표자 결격사유 부존재 서약서", [body])


# ================================================================== 14 ③ 보증보험증권 사본 표지
def doc14_3():
    body = f"""{head("제출서류 14 ③", "보증보험증권 발급 이력 (사본)")}
<p class="body">공고 4항 8)은 ‘계약이행보증보험 등 협약 이행에 필요한 보증증권 발행이 가능한 업체’를 참가자격으로 정하고 있습니다.
당사가 서울보증보험에서 보증증권을 발급받은 이력을 확인하실 수 있도록, 보유 중인 계약보증보험증권 사본을 첨부합니다.</p>
<table class="info" style="margin-top:12pt">
<tr><th>증권 종류</th><td colspan="3">계약보증보험증권(인터넷 발급용) · SGI서울보증</td></tr>
<tr><th>증권번호</th><td>100-000-2026 0637 5726</td><th>발급일</th><td>2026.09.07</td></tr>
<tr><th>보험계약자</th><td colspan="3">{D.COMPANY} ({D.BIZ_NO})</td></tr>
<tr><th>보험가입금액</th><td>금 7억 400만원 (보증금율 20%)</td><th>보험기간</th><td>2026.08.13 ~ 2027.08.12</td></tr>
<tr><th>주계약</th><td colspan="3">광고대행용역 계약(계약금액 35억 2천만원) — 당사의 다른 용역 계약에 대한 보증</td></tr>
</table>
<div class="box" style="margin-top:14pt"><b>공고 4항 8) 보증증권 발행 가능 근거</b><br>
· 위 증권은 당사가 보증보험사의 심사를 거쳐 계약보증보험증권을 발급받은 이력을 보여 드리는 자료입니다(본 입찰과 별개의 용역 계약).<br>
· 입주박람회 협약 이행보증은 <b>협약 시 단지 규모에 맞춰 금액을 확정하여 발급</b>하고, 증권 실물을 입예협에 제출합니다(제안서 기준: 이행보증보험 2년 · 최대 10억원).<br>
· 위 증권의 피보험자 · 주계약 정보는 보증 이력 확인 목적으로만 첨부합니다.</div>
<p class="note">※ 첨부: 계약보증보험증권 사본 2쪽(증권 1쪽 · 보험약관 주요 내용 1쪽)</p>"""
    return doc("14 ③ 보증보험증권 사본", [body])


# ================================================================== 14 ⑤ 실적 확약서(붙임 카페 공지 · BEXCO 행사일정) — 탕정 hwakyak.py의 실적 · 캡처 목록을 그대로 읽는다(읽기만)
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


def doc14_5():
    hw = _hwakyak()
    yy, mm, dd = ymd()
    for f, _t, _u, _w, boxes in hw.CAPS:  # 가림본이 없으면 원본 캡처에서 다시 가림(픽셀로 굳힘)
        dst = os.path.join(HERE, "assets_ins", "cafe_" + f)
        if not os.path.exists(dst):
            hw.mask(os.path.join(CAP_DIR, f), boxes, dst)
    rows = "".join(f'<tr><td>{i}</td><td>{e(a)}</td><td class="l">{e(b)}</td><td>{e(c)}</td><td class="r">{n:,}</td><td class="l">{e(s)}</td></tr>'
                   for i, (a, b, c, n, s) in enumerate(hw.RECS, 1))
    tot = sum(r[3] for r in hw.RECS)
    assert (len(hw.RECS), tot) == (10, 19563), "실적 확약서 합계가 제안서(10개 단지 · 19,563세대)와 다름"
    p1 = f"""<section class="pg">
<h1>실 적 확 약 서</h1><div class="sub">1,000세대 이상 공동주택 입주박람회 주관 실적</div>
<table class="info"><tr><th>상호</th><td>{D.COMPANY}</td><th>대표이사</th><td>{D.CEO}</td></tr>
<tr><th>소재지</th><td colspan="3">{D.ADDRESS}</td></tr>
<tr><th>제출처</th><td colspan="3">{e(D.CLIENT)}</td></tr></table>
<p class="body">당사는 「{e(D.NOTICE)}」 4항 4) · 8항 1) · 2)와 관련하여, 1,000세대 이상 공동주택 단지의 입주박람회 주관 실적을 아래와 같이 제출하며 기재 내용이 사실임을 확약합니다.</p>
<table class="t"><tr><th>연번</th><th>주관 시기</th><th>단지명</th><th>지역</th><th>세대수</th><th>근거</th></tr>{rows}
<tr class="sum"><td colspan="4">합계 {len(hw.RECS)}개 단지</td><td class="r">{tot:,}</td><td></td></tr></table>
<div class="note">※ 근거: NICE 기업신용평가보고서(평가일 {D.NICE_DATE}) '연혁'(제출서류 14 ④ 9쪽) · 각 단지 입주예정자협의회 공식 카페의 주관사 명의 공지 · BEXCO 공식 행사일정(붙임). 세대수는 NICE 연혁 기재값(카페 공지 · BEXCO 근거 3개 단지는 단지 공식 총세대수).</div>
<ol><li>위 실적은 당사가 입주박람회 주관사로서 직접 수행한 것입니다.</li>
<li>귀 협의회가 요청하면 계약서, 실적 확인서, 정산 자료 등 증빙을 지체 없이 제출하겠습니다.</li>
<li>기재 내용이 사실과 다른 것으로 밝혀지면 공고 9항 3) · 11) · 10항 10)에 따른 선정 무효 · 협약 취소 등 모든 조치를 이의 없이 받아들이겠습니다.</li></ol>
<div class="sign"><div class="d">{yy}년 &nbsp;{mm}월 &nbsp;{dd}일</div>
{D.COMPANY}<br><b>대표이사 &nbsp;{" ".join(D.CEO)}</b><span style="margin-left:48pt">(인)</span></div>
<div class="to">{e(D.CLIENT)} 귀중</div></section>"""
    caps = ""
    for f, title, url, what, boxes in hw.CAPS:
        kind = "전시장 공식 행사일정 캡처" if f.startswith("bexco") else "입주예정자협의회 카페 주관사 공지 캡처"
        caps += (f'<section class="pg"><h2>실적 확약서 붙임 · {kind}</h2><div class="cap"><h3>{e(title)}</h3>'
                 f'<div class="u">{e(url)}{" · 입주민 닉네임(동·호수)은 개인정보 보호를 위해 가림" if boxes else ""}</div><div class="k">{e(what)}</div>'
                 f'<img src="assets_ins/cafe_{f}"></div></section>')
    return f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>실적 확약서</title><style>{hw.CSS}{HW_FIT}</style></head><body>{p1}{caps}</body></html>'


# ------------------------------------------------------------------ PDF
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


# 저장은 garbage=3까지만: 크롬 PDF의 Type3 글꼴을 garbage=4(같은 객체 합치기)로 저장하면 글자가 빠지는 경우가 있다(10-14 확인: '제출서류 4'의 '4'가 사라짐).
GARBAGE = 3


def page_texts(doc_or_path):
    d = doc_or_path if isinstance(doc_or_path, fitz.Document) else fitz.open(doc_or_path)
    return [p.get_text() for p in d]


def merge(out_name, parts, title, toc=None):
    o, src = fitz.open(), []
    for p in parts:
        d = p if isinstance(p, fitz.Document) else fitz.open(p)
        src += page_texts(d)
        o.insert_pdf(d)
    o.set_metadata({"title": title, "author": D.COMPANY})
    if toc:
        o.set_toc(toc)
    path = out(out_name + ".pdf")
    o.save(path, garbage=GARBAGE, deflate=True)
    bad = [i + 1 for i, (a, b) in enumerate(zip(src, page_texts(path))) if a != b]
    assert not bad, f"합친 뒤 글자가 달라진 쪽 {bad}: {path}"
    return path


def stamp(seal, pdf_path):
    """../동탄파라곤3차/stamp.py와 같은 자리(‘(인감날인)’ 또는 ‘(인)’ 가운데) · 같은 크기로 날인하되, 저장만 garbage=3."""
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


def fit(path, n):
    """넘침 검사 — 쪽수가 정해진 문서가 다음 쪽으로 밀리면 멈춘다."""
    k = len(fitz.open(path))
    assert k == n, f"{os.path.basename(path)}: {k}쪽(예상 {n}쪽) — 내용이 넘침"
    return path


def proposal_todos():
    """제안서 · 요약제안서 HTML에 남은 노란 칸(<mark class="todo">)도 같이 집계한다."""
    for label, h in (("제안서(02)", P02_HTML), ("요약제안서(14 ②)", P14_SUM_HTML)):
        if os.path.exists(h):
            for x in re.findall(r'<mark class="todo">(.*?)</mark>', pathlib.Path(h).read_text(encoding="utf-8")):
                TODOS.append(f"{label}: {html.unescape(re.sub('<[^>]+>', '', x))}")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    final = "--final" in sys.argv
    if len(args) < 2:
        sys.exit(__doc__)
    nice, seal_path = args[0], args[1]
    for p, why in ((P02, "build_bd.py 먼저(제안서)"), (P14_SUM, "build_bd.py 먼저(요약제안서)"), (nice, "NICE 보고서"), (SGI, "서울보증 증권 사본")):
        assert os.path.exists(p), f"없음: {p} — {why}"
    import stamp as ST_
    seal = ST_.seal_png(seal_path)

    def stamped(p, n_expect=1):
        o, n = stamp(seal, p)
        assert n == n_expect, f"날인 자리 {n}곳(예상 {n_expect}): {p}"
        print(f"날인 {n}곳: {os.path.basename(o)}")
        return o

    res = {}
    # 8을 먼저 만들어 쪽수를 신청서 목록에 적는다
    p08 = render(N08, doc08())
    n08 = len(fitz.open(p08))
    assert 2 <= n08 <= 4, f"방안서 {n08}쪽 — 공고 대응 2 ~ 4쪽"
    res["08"] = stamped(p08)
    res["01"] = stamped(fit(render(N01, doc01(n08)), 2))
    res["02"] = P02
    biz = fitz.open(f"{EV}/사업자등록증.pdf")
    for pg_ in biz:
        for a in list(pg_.annots()):  # 발급 뒤 덧붙인 스탬프 주석이 있으면 원본 칸을 가리므로 뺀다
            pg_.delete_annot(a)
    res["03"] = merge(N03, [biz], "3 사업자등록증 사본")
    if D.INGAM_DATE and os.path.exists(INGAM_PDF):
        ingam = INGAM_PDF
    else:
        ingam = fit(render("04_2_법인인감증명서_조치필요", doc04_action()), 1)
    res["04"] = merge(N04, [f"{EV}/법인등기부등본.pdf", ingam], "4 법인등기부등본 · 법인인감증명서")
    res["05"] = merge(N05, [f"{EV}/국세_납세증명서.pdf", f"{EV}/지방세_납세증명서.pdf"], "5 국세 및 지방세 완납증명서")
    ref06 = fit(render("06_3_가입자명부_참고표지", doc06_ref()), 1)
    res["06"] = merge(N06, [f"{EV}/4대보험_완납증명서.pdf", f"{EV}/고용산재_완납증명서.pdf", ref06, ROSTER],
                      "6 4대보험 완납증명서(건강·연금 · 고용·산재) · 참고 가입자 명부")
    if os.path.exists(CRIME_PDF):
        res["07"] = merge(N07, [CRIME_PDF], "7 대표자 범죄사실확인서")
    elif CRIME_SUBST:
        res["07"] = merge(N07, [fit(render("07_1_갈음", doc07_subst()), 1)], "7 대표자 범죄사실확인서(서약서 갈음)")
    else:
        res["07"] = merge(N07, [fit(render("07_1_조치필요", doc07_action()), 1)], "7 대표자 범죄사실확인서(조치 필요)")
    for no, name, fno, title, paras, items in FORMS:
        res[no] = stamped(fit(render(name, form_doc(fno, title, paras, items)), 1))
    # 14 기타 = ① 결격사유 서약서 ② 요약제안서 ③ 보증증권(표지 + 사본) ④ NICE 보고서 (⑤ 실적 확약서)
    s1 = stamped(fit(render("14_1_결격사유부존재서약서", doc14_1()), 1))
    TODOS.append("14 ① 대표자 결격사유 부존재 서약서 — 대표 확인(사실 확인 후 제출)")
    s3 = fit(render("14_3_보증증권_표지", doc14_3()), 1)
    parts = [s1, P14_SUM, s3, SGI, nice]
    names = ["① 대표자 결격사유 부존재 서약서", "② 요약제안서", "③ 서울보증 계약보증보험증권 사본", "④ NICE디앤비 기업신용평가보고서"]
    if HW_IN_14:
        parts.append(stamped(fit(render("14_5_실적확약서", doc14_5()), 4)))
        names.append("⑤ 실적 확약서(붙임 카페 공지 · BEXCO 행사일정)")
    toc, pg0, groups = [], 1, [[s1], [P14_SUM], [s3, SGI], [nice]] + ([[parts[-1]]] if HW_IN_14 else [])
    for nm, g in zip(names, groups):
        toc.append([1, nm, pg0])
        pg0 += sum(len(fitz.open(x)) for x in g)
    res["14"] = merge(N14, parts, "14 기타 입예협이 필요하다고 인정하는 자료", toc)
    proposal_todos()

    print("\n[제출본 — 공고 7항 순서]")
    for k in sorted(res, key=int):
        v = res[k]
        d = fitz.open(v)
        print(f"{k:>2} {os.path.basename(v)}  {len(d)}p  {os.path.getsize(v) / 1e6:.1f}MB")
    if TODOS:
        u = list(dict.fromkeys(TODOS))
        print(f"[확인 필요 {len(u)}칸]", " / ".join(u))
        if final:
            sys.exit("--final: 확인 필요 칸이 남아 있음")


if __name__ == "__main__":
    main()
