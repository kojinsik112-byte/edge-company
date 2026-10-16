# -*- coding: utf-8 -*-
"""오산세교아테라 입주박람회 주관사 입찰 — 공고 4항 제출서류 16종 생성기(A4 세로). 분당 docs_bd.py 방식(읽기만 · 수정 금지).

  01 입찰 신청서(자유양식 + 제출서류 16종 목록 · 상태)       02 사업자등록증 + 법인통장 사본
  03 법인등기부등본                                        04 법인인감증명서(10.15 가림본) + 사용인감계
  05 배상책임보험 증권(KB 영업배상 · 시설소유관리자) + 표지(현재 가입 내용 · 행사주최자배상책임 가입 계획 — 정직하게)
  06 계좌 잔액증명서(2026.10.14 발행 · 10.13 기준 · 계좌 끝자리 가림본)
  07 국세 · 지방세 완납증명서                              08 4대보험 가입자 명부(가림본) + 완납증명서 2종
  09 기업신용평가(NICE 표지 + 발췌 4쪽 · 대표 외 임직원 생년월일 가림)
  10 공동구매 입찰제안서 = build_os.py 결과 그대로(제출본 = 원본 · 작업/ = 메일용 사본)
  11 업무 이행 각서                                         12 최근 3년 500세대 이상 실적표 + NICE 연혁 발췌 + 실적 확약서(붙임 캡처 3)
  13 협약이행증권 10부 — 파일 없음(본부장: 안 함 · 01 목록에 '해당 없음 — 협약 시 협의'만)
  14 A/S 이행각서                                           15 하자 보수 대응 방안 상세 계획서(제안서와 같은 기준)
  16 선정 결과 이의 제기 금지 서약서
가산점 3 협의회 평가표 · 추천서는 보유분 없음 → 만들지 않는다(보고만).

날인: 직인(배경 투명 PNG) = 사용인감 — 신청서 · 각서 · 서약서 · 계획서 · 실적 문서의 '(인)' 자리(../동탄파라곤3차/stamp.py와 같은 자리 · 크기).
  04 사용인감계는 사용인감 칸만 디지털 직인 → 작업/04_2_사용인감계_출력용.pdf. 법인인감 칸 · 대표자 (인)은 본부장 실물 날인 스캔(data.SEAL_SCAN)으로 교체.
  법인인감은 디지털로 만들지 않는다 · 분당 · 탕정 · 지웰 날인 스캔은 그 단지 전용이라 쓰지 않는다.

조치 필요(TODO) — 없으면 노란 칸 · [확인 필요]로 집계하고 그 서류는 제출본/에 넣지 않는다(--final이면 파일을 쓰기 전에 멈춤)
  04 사용인감계: data.SEAL_SCAN(오산용 실물 날인 스캔 1쪽) — 본부장 제공 대기
  12 실적 증빙: 500세대 이상 '진행' 12개 단지 증빙 → data.R500_DOC(본부장 준비 PDF)
  01 신청서: 04 · 12가 끝나면 노란 칸이 사라짐(목록이 그 상태를 적음)

출력: 작업/ = 중간 파일(HTML · 직인 전 PDF · 출력용 · 지금 상태 그대로의 01 ~ 16) + 제출현황.txt(내부용 — 첨부 금지)
      제출본/ = 조치 끝난 서류만 '엣지컴퍼니_오산세교아테라_NN_항목.pdf'(_직인 없음) · ZIP = 이 폴더의 엣지컴퍼니_오산세교아테라_제출서류.zip(제출본 기준)
사용: python docs_os.py <직인.png> [--final]     (결과 PDF · HTML · ZIP은 깃 제외 — .gitignore)
"""
import ast
import html
import importlib.util
import io
import os
import pathlib
import shutil
import subprocess
import sys
import zipfile

import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "요약제안서"), os.path.join(HERE, "..", "동탄파라곤3차")]
import data as D  # noqa: E402
from build import find_chrome  # noqa: E402

e = html.escape
PFX = "엣지컴퍼니_오산세교아테라_"
ST = D.SITE
SITE = ST["name"]
TODOS = []

SP = "/tmp/claude-0/-home-user-edge-company/a96d9eb6-5244-5d3f-9f1b-6f379ac2a82c/scratchpad"
EV = os.environ.get("OS_EVIDENCE", f"{SP}/evidence")  # 증빙 원본(깃 제외)
ROSTER = f"{SP}/cs_sub/엣지컴퍼니_철산역자이_06_4대보험_사업장가입자명부.pdf"  # 10.02 명부 가림본(성명 가운데 글자 · 주민번호 뒷자리, 픽셀로 굳힘)
KB = f"{EV}/KB_영업배상책임보험_시설소유관리자_20261014.pdf"
CAP_DIR = f"{SP}/hw/cap"  # 실적 확약서 캡처 원본(가림본 assets_ins/cafe_*.png가 없을 때만)
WORK = os.path.join(HERE, "작업")
SUBMIT = os.path.join(HERE, "제출본")
ZIP = os.path.join(HERE, PFX + "제출서류.zip")
P10 = os.path.join(HERE, PFX + "입주박람회_주관사_제안서.pdf")
P10_MAIL = os.path.join(HERE, PFX + "입주박람회_주관사_제안서_메일용.pdf")

# KB손해보험 증권(2026.10.14 발급) 기재값 — 표지(05)에 옮겨 적는다. 증권 원문과 다르면 assert로 멈춤(evidence_check)
KBV = dict(no="2026-6774341(000)", product="영업배상책임보험", cover="시설소유관리자배상책임", insured=D.COMPANY,
           period="2026.10.14 24:00 ~ 2027.10.14 24:00 (365일)", place="울산 울주군 청량읍 온산로 615-1, 2층 · 3층 (본사 사업장 · 사무용빌딩 · 시설면적 328.86㎡)",
           bi="대인 1인당 1억원 · 1사고당 3억원", pd="대물 1사고당 1억원", med="구내치료비 1인당 100만원 · 1사고당 300만원",
           ded="자기부담금(공제금액) 1사고당 10만원(대인 · 대물)", issued="2026.10.14")


def todo(x):
    TODOS.append(x)
    return f'<mark class="todo">{e(x)}</mark>'


def _from_build_os(names):
    """build_os.py 모듈 수준 상수(환불 규정 · 컴플레인 처리 기준)를 실행 없이 읽는다 — 제안서와 같은 기준(분당 방식)."""
    tree = ast.parse(pathlib.Path(HERE, "build_os.py").read_text(encoding="utf-8"))
    ns = {"D": D, "ST": ST}
    for node in tree.body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id in names):
            exec(compile(ast.Module([node], []), "build_os.py", "exec"), ns)
    miss = [n for n in names if n not in ns]
    assert not miss, f"build_os.py에서 찾지 못함: {miss}"
    return ns


RULE = _from_build_os(["_C7", "_C15", "_CU", "CPL", "MON"])
_clean = lambda s: s.replace("[[", "").replace("]]", "")  # noqa: E731 — 제안서 강조 표시 제거

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
.t.ls{font-size:8.7pt;line-height:1.35}ol.pl li.sm{font-size:9.2pt;margin-top:2pt;line-height:1.5}.t.ls td{padding:2pt 5pt}
.t tr.jg td{background:#FBF8F1}.t tr.jg td.g{color:#9A7B3F;font-weight:800}
.t tr.sum td{background:#F1EDE4;font-weight:800}
.t td.st{font-weight:800;white-space:nowrap}.t td.st.ok{color:#1F6B3A}.t td.st.na{color:#5B6676}.t td.st.td{color:#9A6A00}
.box{border:1pt solid #C8A86A;background:#FBF8F1;border-radius:4pt;padding:7pt 11pt;margin-top:10pt;font-size:9.8pt;line-height:1.65}
.box b{color:#0D1E33}
.box.warn{border-color:#9AA3B0;background:#F6F7F9}
p.body{margin-top:12pt;font-size:10.5pt;line-height:1.85}
.note{font-size:8.8pt;color:#5B6676;margin-top:5pt;line-height:1.55}
ol.pl{list-style:none;margin-top:8pt}
ol.pl li{padding-left:16pt;text-indent:-16pt;margin-top:5pt;font-size:10.2pt;line-height:1.72}
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
.ap .sgt{margin:14pt 0 0 auto;border-collapse:collapse;font-size:11.5pt;line-height:2.75}
.ap .sgt td{padding:0 6pt;vertical-align:middle;white-space:nowrap}
.ap .sgt td.w{vertical-align:top;padding-right:12pt}
.ap .to2{margin-top:26pt;text-align:center;font-size:13pt;font-weight:800}
/* 사용인감계 */
.seals{display:grid;grid-template-columns:1fr 1fr;gap:18pt;margin-top:14pt}
.seals div{border:.8pt solid #9AA3B0;height:122pt;display:flex;flex-direction:column;align-items:center;justify-content:space-between;padding:8pt}
.seals b{font-size:10.5pt;color:#0D1E33}
.seals span.mk{color:#ECEEF1;font-size:5pt}
.seals small{font-size:8.5pt;color:#5B6676}
"""

HEAD = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{t}</title>'
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">'
        '<style>{css}</style></head><body>')


def doc(title, sections, css=CSS):
    return HEAD.format(t=e(title), css=css) + "".join(f'<section class="pg">{s}</section>' for s in sections) + "</body></html>"


def head(label, title, center=False):
    return (f'<div class="top"><div class="lb">{e(label)}</div><div class="co">{D.COMPANY} · 입주박람회 주관사</div></div>'
            f'<h1 class="{"c" if center else ""}">{e(title)}</h1>'
            f'<div class="case" style="{"text-align:center" if center else ""}">건명 : {e(D.NOTICE)} ({D.NOTICE_DATE} 공고)</div>')


def sign(prefix=""):
    yy, mm, dd = D.SIGN_DATE
    return (f'<div class="sign"><div class="d">{yy}년 {mm}월 {dd}일</div>'
            f'<div class="who">{prefix}{D.COMPANY} &nbsp; 대표이사 &nbsp; {D.CEO}<span class="seal">(인)</span></div></div>'
            f'<div class="to">{e(D.CLIENT)} 귀중</div>')


def company_info(extra=""):
    m = D.MANAGER
    return (f'<table class="info"><tr><th>상호</th><td>{D.COMPANY}</td><th>대표자</th><td>대표이사 {D.CEO}</td></tr>'
            f'<tr><th>사업자등록번호</th><td>{D.BIZ_NO}</td><th>법인등록번호</th><td>{D.CORP_NO}</td></tr>'
            f'<tr><th>본사 소재지</th><td colspan="3">{D.ADDRESS}</td></tr>'
            f'<tr><th>담당자</th><td colspan="3">{m[1]} {m[0]} · {m[2]} · {D.EMAIL}</td></tr>{extra}</table>')


def pledge(no, title, lead, items, tail=""):
    """각서 · 서약서 공통(11 · 14 · 16) — 1쪽 · 사용인감 날인."""
    lis = "".join(f"<li>{i}. {x}</li>" for i, x in enumerate(items, 1))
    return doc(f"{no} {title}", [f"""{head(f"제출서류 {no}", title, True)}{company_info()}
<p class="body">{lead}</p><ol class="pl">{lis}</ol>{tail}{sign()}"""])


# ------------------------------------------------------------------ 상태 점검(파일을 쓰기 전에)
def _scan_ok(path):
    return bool(path) and os.path.exists(path) and len(fitz.open(path)) == 1


def readiness():
    seal = _scan_ok(D.SEAL_SCAN)
    r500 = bool(D.R500_DOC) and os.path.exists(D.R500_DOC)
    ok = {"04": seal, "12": r500}
    ok["01"] = seal and r500
    miss = []
    if not seal:
        miss.append("04 사용인감계 — 본부장 실물 날인 스캔 대기(오산용 · 1쪽 PDF) → data.py SEAL_SCAN에 경로 · 출력 양식은 작업/04_2_사용인감계_출력용.pdf")
    if not r500:
        miss.append("12 실적 증빙 — 500세대 이상 '진행' 12개 단지 증빙 자료 본부장 준비 중 → data.py R500_DOC에 PDF 경로")
    if not ok["01"]:
        miss.append("01 신청서 — 위 04 · 12가 끝나면 목록의 노란 칸이 사라짐(다시 실행)")
    return ok, miss


def evidence_check():
    """증빙 원본이 기재값과 맞는지 — 날짜 · 번호를 글자로 확인할 수 있는 것만."""
    t = fitz.open(KB)[0].get_text()
    for k in ("2026- 6774341", "영업배상책임보험", "시설소유관리자배상책임", "100,000,000", "300,000,000", "328.86", "2027년 10월 14일 24:00"):
        assert k in t, f"KB 증권 글자 확인 실패: {k}"
    t = fitz.open(f"{EV}/사업자등록증.pdf")[0].get_text()
    assert "2026 년10 월14 일" in t and "전시,박람회및행사대행업" in t, "사업자등록증 발급일 · 종목 확인 실패"
    t = fitz.open(f"{EV}/국세_납세증명서.pdf")[0].get_text()
    assert "2026 년10 월14 일" in t and "2026 년11 월13 일" in t, "국세 납세증명서 발급일 · 유효기간 확인 실패"
    for p in (ROSTER, f"{EV}/법인인감증명서.pdf", f"{EV}/잔액증명서_1013_가림.pdf", P10, P10_MAIL):
        assert os.path.exists(p), f"없음: {p}"
    assert len(fitz.open(ROSTER)) == 2, "명부 가림본 쪽수"


# ================================================================== 01 입찰 신청서 + 제출서류 목록
def submit_rows(n):
    """(번호, 공고 4항 서류, 제출 내용, 상태) — 상태: 제출 / 해당 없음 / 조치 중(노란 칸)."""
    seal = _scan_ok(D.SEAL_SCAN)
    r500 = bool(D.R500_DOC) and os.path.exists(D.R500_DOC)
    bal_issue, bal_base = D.BALANCE
    return [
        ("1", "입찰 신청서(자유양식)", "본 서류 · 제출서류 목록 포함", "제출"),
        ("2", "법인 사업자등록증 & 통장 사본", f"사업자등록증 {D.ISSUE['biz']} 발급(울산세무서) · 법인 명의 우리은행 기업자유예금 통장 사본", "제출"),
        ("3", "법인등기부 등본", f"등기사항전부증명서 {D.ISSUE['reg']} 발급", "제출"),
        ("4", "인감증명서", f"법인 인감증명서 {D.INGAM_DATE} 발급(대표자 주민등록번호 뒷자리 가림) · 사용인감계(서류 날인 인감 신고)"
         + ("" if seal else " · " + todo("사용인감계 — 본부장 실물 날인 스캔 받으면 교체")), "제출" if seal else "조치 중"),
        ("5", "행사주최자배상책임보험 가입증명서",
         f"현재 가입 = KB손해보험 영업배상책임보험(시설소유관리자배상책임 · 본사 사업장 · 2026.10.14 ~ 2027.10.14) 증권 사본 · "
         "행사주최자배상책임은 박람회 확정 시 행사 기간 · 장소에 맞춰 특약 추가 가입(입예협 요청 시 가입증명서 제출) — 표지에 설명", "제출(현 가입 증권)"),
        ("6", "공고일 이후 발행 계좌 잔고증명서", f"우리은행 잔액증명서 {bal_issue} 발행({bal_base} 기준 잔액) · 계좌번호 끝자리 가림", "제출"),
        ("7", "국세 및 지방세 완납 증명서", f"국세 {D.ISSUE['tax']} · 지방세 {D.ISSUE['ltax']} 발급(유효 ~2026.11.13 · 최근 1개월 이내)", "제출"),
        ("8", "4대 보험 가입증명서 및 정직원 8인 이상 가입명부",
         f"4대 사회보험 사업장 가입자 명부({D.ROSTER_DATE} 발급 · 10명, 대표이사 포함 · 성명 가운데 글자 · 주민등록번호 뒷자리 가림) · "
         f"4대 사회보험료 완납증명서(건강 · 연금) · 고용 · 산재보험료 완납증명서(근로복지공단) 각 {D.WANNAP_DATE} 발급", "제출"),
        ("9", "기업신용평가(최근년도평가)", f"NICE디앤비 CLIP 기업신용평가보고서 · 평가 {D.NICE_DATE}(유효 ~2027.06.18) · 신용등급 BB- · 현금흐름 A · "
         f"표지 + 발췌 {len(NICE_PAGES)}쪽(원본 24쪽 · 전문은 요청 시 제출)", "제출"),
        ("10", "공동구매 입찰제안서(자유양식)", f"입주박람회 주관사 제안서 {n['10']}쪽", "제출"),
        ("11", "업무 이행 각서", "제안 내용 이행 · 사용인감 날인본(법인인감 날인 원본은 협약 시 제출)", "제출"),
        ("12", "최근 3년 500세대 이상 행사 실적 및 공동구매 증빙자료",
         f"실적표 {len(D.RECENT3_500)}개 단지 · {sum(r[2] for r in D.RECENT3_500):,}세대(1,000세대 이상 주관 {sum(1 for r in D.RECENT3_500 if r[3])} · 진행 "
         f"{sum(1 for r in D.RECENT3_500 if not r[3])}) · 별첨 NICE 연혁 발췌 · 실적 확약서(붙임 카페 공지 2 · BEXCO 행사일정 1)"
         + ("" if r500 else " · " + todo("진행 12개 단지 증빙 — 본부장 준비 중")), "제출" if r500 else "조치 중"),
        ("13", "최근 3년 500세대 이상 협약이행증권 협의회 발행본 10부 이상", "해당 없음 — 협약 시 입예협과 협의해 이행 담보 방안 마련", "해당 없음"),
        ("14", "A/S 이행각서", "사용인감 날인", "제출"),
        ("15", "하자 보수 대응 방안 상세 계획서", f"{n['15']}쪽 · 제안서(제출서류 10)와 같은 기준", "제출"),
        ("16", "선정 결과 이의 제기 금지 서약서", "사용인감 날인", "제출"),
    ]


def doc01(n):
    m = D.MANAGER
    yy, mm, dd = D.SIGN_DATE
    p1 = f"""<div class="ap"><h1>입찰 신청서</h1>
<table class="ft"><tr><th>입 찰 건 명</th><td>{SITE} 입주박람회 주관사 업체 선정<br>
<span style="font-size:9pt;color:#555">{e(D.CLIENT)} · {D.NOTICE_DATE} 공고 · 접수 마감 {D.DEADLINE}</span></td></tr></table>
<h3>■ 신청업체</h3>
<table class="ft"><tr><th>상 &nbsp; &nbsp; 호</th><td>{D.COMPANY}</td><th>대 표 자</th><td>대표이사 {D.CEO}</td></tr>
<tr><th>사업자등록번호</th><td>{D.BIZ_NO}</td><th>법인등록번호</th><td>{D.CORP_NO}</td></tr>
<tr><th>본사 소재지</th><td colspan="3">{D.ADDRESS}</td></tr>
<tr><th>설 립 일</th><td>{D.FOUNDED}</td><th>대표 전화</th><td>{D.TEL}</td></tr>
<tr><th>이 메 일</th><td colspan="3">{D.EMAIL}</td></tr></table>
<h3>■ 담당(책임)자</h3>
<table class="ft"><tr><th>성 &nbsp; &nbsp; 명</th><td>{m[0]}</td><th>직 &nbsp; &nbsp; 위</th><td>{m[1]}</td></tr>
<tr><th>휴 대 전 화</th><td>{m[2]}</td><th>이 메 일</th><td>{D.EMAIL}</td></tr></table>
<p class="tx">당사는 「{e(D.NOTICE)}」({D.NOTICE_DATE})에 따른 {SITE} 입주박람회 주관사 선정 입찰에 참가하고자, 공고문의 참가자격 · 제출서류 · 심사 절차 · 유의사항을 충분히 숙지하고 공고 사항을 모두 수락합니다. 주관사로 선정될 경우 협약 내용을 성실히 이행할 것을 확약하며, 공고 4항 제출서류를 붙임과 같이 첨부하여 입찰 참가를 신청합니다.</p>
<p style="margin-top:8pt;font-size:10pt">붙임 &nbsp;제출서류 목록 1부(다음 쪽).</p>
<div class="dt">{yy}년 &nbsp; {mm}월 &nbsp; {dd}일</div>
<table class="sgt"><tr><td rowspan="2" class="w">신청인</td><td>상 &nbsp; &nbsp; 호 :</td><td><b>{D.COMPANY}</b></td></tr>
<tr><td>대 표 자 :</td><td><b>대표이사 {D.CEO}</b><span style="margin-left:34pt;position:relative;top:4pt">(인)</span></td></tr></table>
<div class="to2">{e(D.CLIENT)} 귀중</div></div>"""
    cls = {"제출": "ok", "해당 없음": "na"}
    rows = "".join(f'<tr><td>{no}</td><td class="l">{e(t)}</td><td class="l">{r}</td>'
                   f'<td class="st {cls.get(s, "ok" if s.startswith("제출") else "td")}">{e(s)}</td></tr>' for no, t, r, s in submit_rows(n))
    p2 = f"""{head("입찰 신청서 붙임", "제출서류 목록")}
<h2>공고 4항 제출서류 16종 (공고 순서 · 번호 그대로)</h2>
<table class="t ls"><thead><tr><th style="width:5%">No</th><th style="width:27%">서류 (공고 4항)</th><th>제출 내용 · 발급일</th><th style="width:11%">상태</th></tr></thead><tbody>{rows}</tbody></table>
<p class="note">※ 파일 이름은 ‘엣지컴퍼니_오산세교아테라_번호_서류명.pdf’로 공고 순서와 같습니다. 13은 제출 파일이 없습니다(이행 담보 방안은 협약 시 입예협과 협의).</p>
<p class="note">※ 신청서 · 각서 · 서약서 · 계획서 · 실적 서류의 날인은 사용인감입니다(제출서류 4 사용인감계에 법인인감과 함께 신고).</p>
<p class="note">※ 9 기업신용평가보고서(평가 {D.NICE_DATE})의 본사 주소는 본점 이전(2026.07.02 등기) 전 주소이고, 종업원 수는 평가 당시(2026.05) 기준입니다. 현재 본점은 위 소재지와 같습니다(제출서류 2 · 3).</p>
<p class="note">※ 접수: {D.SUBMIT_TO} · 메일 제목 「{D.MAIL_TITLE}」 · 마감 {D.DEADLINE}</p>"""
    return doc("01 입찰 신청서", [p1, p2])


# ================================================================== 04 사용인감계(출력용 — 법인인감 칸은 실물 날인)
def doc04_seal():
    body = f"""{head("제출서류 4", "사용인감계", True)}
{company_info(f'<tr><th>용도</th><td colspan="3">{SITE} 입주박람회 주관사 선정 입찰 참가 및 협약 체결 일체({D.NOTICE_DATE} 공고)</td></tr>')}
<p class="body">위 법인은 아래 인감을 사용인감으로 신고하며, 위 용도의 서류(입찰 신청서 · 업무 이행 각서 · A/S 이행각서 · 하자 보수 대응 방안 상세 계획서 · 이의 제기 금지 서약서 · 실적 서류 등)에 사용합니다.
이 인감의 사용으로 생기는 모든 책임은 당사가 집니다.</p>
<div class="seals">
<div><b>사용인감</b><span class="mk">(인감날인)</span><small>입찰 · 협약 서류에 사용</small></div>
<div><b>법인인감</b><span></span><small>인감증명서상 등록 인감</small></div>
</div>
<p class="note" style="margin-top:8pt">※ 첨부: 법인 인감증명서 1부({D.INGAM_DATE} 발급 — 앞 쪽)</p>{sign()}"""
    return doc("4 사용인감계", [body])


# ================================================================== 05 배상책임보험 — 표지(정직하게) + 증권
def doc05():
    k = KBV
    rows = [("보험회사 · 상품", f"KB손해보험 · {k['product']}(일반보험 증권 · {k['issued']} 발급)"), ("증권번호", k["no"]),
            ("담보", f"{k['cover']} 특별약관 · 구내치료비 특별약관"), ("계약자 · 피보험자", k["insured"]), ("보험기간", k["period"]),
            ("보장 대상 시설", k["place"]), ("보상한도", f"{k['bi']} · {k['pd']} · {k['med']}"), ("자기부담", k["ded"])]
    tb = "".join(f'<tr><td class="k" style="width:22%">{a}</td><td class="l">{e(b)}</td></tr>' for a, b in rows)
    body = f"""{head("제출서류 5", "배상책임보험 가입 현황 및 행사주최자배상책임보험 가입 계획")}
<div class="box warn" style="margin-top:14pt"><b>먼저 밝힙니다.</b> 공고 4항 5는 ‘행사주최자배상책임보험 가입증명서’입니다.
현재 당사가 가입한 보험은 <b>본사 사업장의 영업배상책임보험(시설소유관리자배상책임)</b>이며, 이 증권은 행사주최자배상책임보험이 아닙니다.
행사주최자배상책임은 박람회 일정 · 장소가 정해져야 가입할 수 있어, 아래 계획대로 가입하겠습니다.</div>
<h2>1. 현재 가입 — 영업배상책임보험(시설소유관리자배상책임) · 증권 사본 첨부(다음 쪽)</h2>
<table class="t kv"><tbody>{tb}</tbody></table>
<p class="note">※ 위 내용은 첨부 증권의 기재 그대로입니다. 보장 대상 시설은 증권에 적힌 울산 본사 사업장입니다.</p>
<h2>2. 행사주최자배상책임보험 — 가입 계획</h2>
<table class="t kv"><tbody>
<tr><td class="k" style="width:22%">가입 시점</td><td class="l">박람회 확정 시(일정 · 장소 확정 후) — 행사 기간 · 장소에 맞춰 <b>특약 추가 가입</b></td></tr>
<tr><td class="k">담보 범위</td><td class="l">박람회 행사 중 관람객 등 제3자의 신체 · 재물 사고(제안서 ‘입주박람회 운영 계획’ 쪽과 같음)</td></tr>
<tr><td class="k">제출</td><td class="l">입예협 요청 시 가입증명서 제출</td></tr>
</tbody></table>
<p class="body" style="font-size:10pt">당사는 위 내용이 사실임을 확인하며, 선정될 경우 위 계획대로 행사주최자배상책임보험에 가입하겠습니다.</p>
{sign()}"""
    return doc("5 배상책임보험 가입 현황 및 행사주최자배상책임보험 가입 계획", [body])


# ================================================================== 09 NICE 표지 + 발췌(분당 14 ③ 방식 — 대표 외 임직원 생년월일 가림)
NICE_MASK = {12: [(170, 148.5, 228, 163.5), (170, 166.5, 228, 181.5)]}  # 원본 13쪽 '주요 경영진' 생년월일 칸 — 대표 외 임직원 2명
NICE_PAGES = [0, 2, 8]  # 본부장 10-16: 13쪽 '경영진 현황' 삭제 · 원본 1 표지 · 3 신용평가 요약 · 9 기업개요 · 연혁 · 13 경영진(가림)


def doc09_cover():
    body = f"""{head("제출서류 9", "기업신용평가 (최근년도 평가)")}
<table class="t kv" style="margin-top:14pt"><tbody>
<tr><td class="k" style="width:22%">보고서</td><td class="l">NICE디앤비 CLIP 기업신용평가보고서(관리번호 11125949-202605-001)</td></tr>
<tr><td class="k">평가 대상</td><td class="l">{D.COMPANY} ({D.BIZ_NO})</td></tr>
<tr><td class="k">평가일 · 유효기간</td><td class="l">{D.NICE_DATE} · ~2027.06.18 — 당사의 가장 최근 평가</td></tr>
<tr><td class="k">결과</td><td class="l">신용등급 BB- · 현금흐름등급 A</td></tr>
<tr><td class="k">첨부 범위</td><td class="l">원본 24쪽 중 {len(NICE_PAGES)}쪽 — 원본 1쪽 표지 · 3쪽 기업신용평가 요약 · 9쪽 기업개요 · 연혁</td></tr>
<tr><td class="k">개인정보</td><td class="l">원본 13쪽 대표 외 임직원 2명의 생년월일은 개인정보 보호를 위해 가렸습니다.</td></tr>
</tbody></table>
<p class="note" style="margin-top:8pt">※ 보고서의 본사 주소는 본점 이전(2026.07.02 등기) 전 주소이고, 종업원 수는 평가 당시(2026.05) 기준입니다. 현재 본점 · 등기 사항은 제출서류 2 · 3과 같습니다.</p>
<p class="note">※ 보고서 전문(24쪽)은 협의회가 요청하시면 바로 제출하겠습니다. 실적 근거인 연혁(원본 9쪽)은 제출서류 12에도 발췌해 붙였습니다.</p>"""
    return doc("9 기업신용평가", [body])


def nice_extract(nice_path):
    d = fitz.open(nice_path)
    assert len(d) == 24, f"NICE 보고서 {len(d)}쪽 — 가림 좌표 · 발췌 쪽 다시 확인"
    for i, rects in NICE_MASK.items():
        pg = d[i]
        assert any(x["width"] == 2477 and x["height"] == 3502 for x in pg.get_image_info()), "NICE 13쪽 이미지가 다름 — 가림 좌표 다시 확인"
        for r in rects:
            pg.add_redact_annot(fitz.Rect(*r), fill=(0.82, 0.82, 0.82))
        pg.apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS)
    d.select(NICE_PAGES)
    p = out("09_2_NICE_발췌_가림.pdf")
    d.save(p, garbage=GARBAGE, deflate=True)
    return p


# ================================================================== 11 업무 이행 각서
DUTY = [  # (분야, 이행 내용) — 제안서(제출서류 10)에 적은 조건 그대로
    ("계약 보호", f"계약금 {D.DEPOSIT_MAX}% 이하 · 카드 · 현금 동일가 · 잔금은 시공 · 설치 확인 후 · 품목별 취소 기한 안 전액 환불(업체 귀책은 기한과 관계없이) · 환불 3영업일 이내"),
    ("가격 검증", "단가표 박람회 전 공개 · 시중가 · 온라인 최저가 검수 · 최저가 차액 10배 보상(환불 규정 제8조 — 동일 브랜드 · 모델 새 제품, 온라인 판매 · 시공 품목 등 제외)"),
    ("하자 · A/S", "한 창구 접수 · 24시간 안에 1차 회신 · 48시간 하자보수 원칙 · 무상 A/S 최소 2년(업체 · 품목별 상이, 계약서 명시) · 업체 미응답 시 주관사 선보상 · 업체 도산 시 동종업체 이관(A/S 비용 주관사 부담)"),
    ("보상 재원", "하자 예치금 최대 1억원(엣지컴퍼니 자산 · 금액은 단지 규모와 입예협 협의로 결정) · 협약 이행 담보 방안은 협약 시 입예협과 협의해 마련"),
    ("세대 혜택", "발전지원금 6,000만원 상당 — 세대 혜택 패키지(안)로 집행 · 주관사 부담 · 공구가 전가 · 공용부 기증 없음"),
    ("직영 · 투명", "주관 업무 재위탁 · 명의 대여 없음 · 사전 공개 단가 = 박람회장 단가 = 온라인 박람회 단가 · 계약 · 환불 · A/S · 하자 처리 현황 정례 보고"),
    ("일정 · 보고", "월별 업무 타임테이블(2026.10 ~ 입주 후 1년) · 박람회 결과보고서 · 최종 결과 보고서"),
]


def doc11():
    tb = "".join(f'<tr><td class="k" style="width:15%">{a}</td><td class="l">{e(b)}</td></tr>' for a, b in DUTY)
    items = [
        "제안서 조건 = PT 조건 = 협약서 조건으로 하고, 선정 이후 PT · 협약 과정에서 제안 조건을 입주예정자에게 불리하게 바꾸지 않겠습니다.",
        "아래 주요 이행 사항을 협약서에 반영하고 협약 기간(입주 후 1년 · 각 계약의 보증 기간 포함) 동안 이행하겠습니다. ‘(안)’으로 표기한 항목(박람회 일정 · 장소, 품목 · 업체, 세대 혜택 구성 등)은 수요조사 결과와 입예협 협의로 확정합니다.",
        "협약을 이행하지 않을 경우 공고 7항 3에 따른 협약 해지와 차순위 업체 선정을 이의 없이 받아들이고, 당사 귀책으로 입주예정자 또는 입예협에 손해가 발생하면 배상하겠습니다.",
        "본 각서는 사용인감(제출서류 4 사용인감계)으로 날인하여 제출하며, 법인인감을 날인한 원본은 협약 시 제출하겠습니다(공고 4항 11).",
    ]
    tail = f'<h3 class="s" style="margin-top:10pt">주요 이행 사항 (제안서 기재 조건)</h3><table class="t kv"><tbody>{tb}</tbody></table>'
    return pledge("11", "업무 이행 각서",
                  f"당사는 {e(D.CLIENT)}의 입주박람회 주관사 선정 입찰에 제출한 공동구매 입찰제안서(제출서류 10)의 내용을 성실히 이행할 것을 다음과 같이 각서합니다.",
                  items, tail)


# ================================================================== 14 A/S 이행각서
def doc14():
    items = [
        "무상 A/S 기간은 최소 2년(업체 · 품목별 상이)으로 하고, 품목별 기간을 공동구매 계약서에 명시하겠습니다. 제조사 보증이 더 길면 그 기간을 따릅니다.",
        f"A/S 접수는 주관사 한 창구(콜센터 {D.TEL} 평일 09:00 ~ 18:00 · 카페 신문고 · 카카오채널 · 홈페이지 365일)로 받고, 주관 창구를 입주 후 1년간 운영하겠습니다. 이후에도 각 계약의 보증 기간 동안 같은 기준을 유지합니다.",
        "접수 후 24시간 안에 1차 회신하고, 48시간 하자보수를 원칙으로 처리하며, 완료 후 해피콜로 확인하겠습니다.",
        "참여업체가 A/S에 응하지 않거나 지연하면 당사가 사실을 확인한 뒤 입주민에게 먼저 보상하고, 참여업체와는 계약 조항에 따라 정산하겠습니다.",
        "참여업체가 도산 · 폐업한 경우 동종업체로 A/S를 이관하고, 그 비용은 당사가 전액 부담하겠습니다.",
        "참여업체에 A/S를 이유로 한 예치금 · 추가 보증금 · 상담 인력을 요구하지 않고, 콜센터 운영비는 당사가 부담하겠습니다(업체 부담 가중 없는 제도 · 공고 5항 5).",
        "A/S 접수 · 처리 · 지연 사유를 기록하여 입예협 정례 보고와 박람회 결과보고서 · 최종 결과 보고서에 담겠습니다.",
    ]
    tail = '<p class="body" style="font-size:10pt">위 사항을 이행하지 않아 입주예정자에게 손해가 발생한 경우 당사가 배상 책임을 지겠습니다.</p>'
    return pledge("14", "A/S 이행각서",
                  f"당사는 {e(D.CLIENT)}의 입주박람회 · 공동구매를 주관하면서, 참여업체가 납품 · 시공 · 설치한 품목의 A/S를 다음과 같이 이행할 것을 각서합니다.",
                  items, tail)


# ================================================================== 16 이의 제기 금지 서약서
def doc16():
    items = [
        "1차 서류 심사, 2차 프레젠테이션 심사, 입예협의 최종 선정 절차와 그 결과에 대하여 어떠한 이의도 제기하지 않겠습니다(공고 3항 11 · 7항 1).",
        "선정 방법이 비공개임을 이해하며, 심사 내용 · 점수의 공개를 요구하지 않겠습니다.",
        "제출한 서류의 반환을 요구하지 않겠습니다(공고 7항 1).",
        "제출 서류가 허위이거나 입찰 과정에 문제가 확인되면 협약 체결 이후라도 협약 해지 등 입예협의 조치를 받아들이겠습니다(공고 7항 2).",
        "공고에 명시되지 않은 사항은 입예협의 결정에 따르며, 이에 대하여 이의를 제기하지 않겠습니다(공고 7항 4).",
    ]
    return pledge("16", "선정 결과 이의 제기 금지 서약서",
                  f"당사는 {e(D.CLIENT)}가 시행하는 입주박람회 주관사 선정 입찰에 참가하면서 공고문({D.NOTICE_DATE})의 심사 절차와 유의사항을 숙지하였으며, 다음 사항을 서약합니다.",
                  items)


# ================================================================== 15 하자 보수 대응 방안 상세 계획서
DEFECT = [  # 제안서 '하자 접수, 책임부터 나눕니다' 쪽과 같은 내용
    ("건설사 시공 · 공용부", "세대 마감 · 설비 하자, 공용부 시설", f"시공사({ST['builder']}) · 사업주체 하자 처리 창구", "접수 대행 · 회신 추적 · 현장 확인 지원 · 정기 보고"),
    ("공동구매 납품 · 시공", "박람회에서 계약한 품목의 설치 · 제품 하자", "참여업체 + 주관사 책임(특약이행각서)", "48시간 하자보수 원칙 · 업체 미응답 시 개입 · 선보상"),
    ("업체 부도 · 미시공", "참여업체 폐업 · 연락 두절 · 시공 중단", "주관사 책임 처리", "동종업체 이관 · A/S 비용 주관사 부담 · 하자 예치금"),
    ("성능 향상 · 추가 설치", "조경 · 조명 · 집기 개선, 시설 추가", "입예협 · 관리주체 결정 사항", "하자와 구분 · 도면 · 예산 · 운영비 검토 자료만 지원"),
]
OATH9 = [  # 제안서 '입주박람회 특약이행각서(예시)' 9개 항 — 문구는 입예협 협의 후 확정
    ("이관 의무", "관련 법령에 따른 하자보수 이관 의무를 이행한다."), ("이관 대상", "설비 · 마감공사 등 입주민 하자 발생 시 보수 범위를 명시한다."),
    ("하자 통보", "하자 통보는 서면(내용증명 · 전자문서)으로 하며 근거를 남긴다."), ("계약 해지", "계약 해지 시 중도 정산 및 포기 각서를 작성한다."),
    ("보증 기간", "하자 접수 기간(최소 2년)과 보증 책임 · 조치 의무를 명문화한다."), ("연대책임", "폐업 · 도산 시 별도 계약 없이도 하자보수를 즉시 승인한다."),
    ("지연 배상", "비용 지급 기한과 불이행 시 지연배상금 · 손해배상을 따른다."), ("민원 처리", "민원 발생 시 즉시 처리하고 결과를 보고한다."),
    ("주관사 이관", f"도산 시 {D.COMPANY}의 사후관리 · 하자보수 이관에 동의한다."),
]
REPORT = [  # 제안서 '보고는 항목과 시점을 정해 둡니다' 쪽과 같은 내용
    ("하자처리 현황 보고", "입주 후 정기(주기는 입예협과 협의)", "하자 접수 · 처리 완료 · 지연 건과 사유 · 재접수"),
    ("입주박람회 결과보고서", "박람회 종료 후", "공동구매 진행현황 · A/S 접수현황 · 하자처리 현황 · 민원처리 결과"),
    ("최종 결과 보고서", "입주 후 1년 운영 관리 종료 시", "계약 · 환불 · A/S · 하자 처리 결과 · 하자 예치금 사용 내역"),
]


def doc15():
    mon = {m: (a, b) for m, a, b in RULE["MON"]}
    stages = [  # (시기, 단계, 하자 대응 업무) — 월별 타임테이블(제안서 07장)의 해당 행 + 하자 관련 행동
        ("2027.04", "업체 심사", "4단계 심사 · 입예협 최종 컨펌 · 참여업체 전원 특약이행각서(9개 항) 징구 — 각서를 내지 않은 업체는 참여 불가"),
        ("2027.06 ~ 07", "계약 조건 확정", "표준 계약서에 취소 · 환불 규정 · 품목별 무상보증기간 · 포함 조건(설치 · 철거 · 배송 · A/S) 명시 · 단가표 공개"),
        ("2027.08 ~ 09", "박람회 · 실측", "59㎡ 4개 타입별 실측 · 납품 · 시공 일정 관리표 작성 — 치수 · 사양 오류를 시공 전에 줄임"),
        ("2027.09 ~ 10", "사전점검", _clean(mon["2027.09 ~ 10"][0]) + " · 건설사 하자는 시공사 창구로 접수 대행 · 회신 추적"),
        ("2027.11", "입주 · 시공", "시공 · 설치 → 세대 검수 서명 → 하자 · 미시공은 보수 후 잔금 → 해피콜 · 하자 접수 창구 운영"),
        ("입주 후 1년", "이행 관리", "A/S · 하자 이행 관리 · 정기 보고 → 최종 결과 보고서"),
        ("1년 이후", "보증 기간", "주관 창구 운영 종료 후에도 각 계약의 보증 기간 동안 취소 · 환불 규정 효력 유지(제10조) · 업체 보증 이행"),
    ]
    assert "사전점검" in mon["2027.09 ~ 10"][0] and "입주 후 1년" in mon, "build_os.py MON 행이 바뀜 — doc15 단계표 다시 확인"
    flow = "".join(f'<div><b>{a}</b>{b}</div>' + ("" if i == 5 else "<i>›</i>") for i, (a, b) in enumerate([
        ("① 접수", "콜센터 · 카페 · 카카오 · 홈페이지 한 창구 · 기록"), ("② 유형 분류", "시공사 하자 · 공동구매 · 업체 사정 · 성능 향상"),
        ("③ 책임 주체 연결", "참여업체 · 시공사 · 입예협"), ("④ 기한 추적", "24시간 1차 회신 · 48시간 하자보수"),
        ("⑤ 미응답 시 선보상", "주관사가 먼저 보상 후 업체 정산"), ("⑥ 완료 · 보고", "해피콜 · 결과보고서")]))
    p = f"""{head("제출서류 15", "하자 보수 대응 방안 상세 계획서")}
<div class="box"><b>핵심 요약</b> &nbsp; 한 창구 접수 → <b>24시간 안에 1차 회신</b> → <b>48시간 하자보수 원칙</b> → 업체 미응답 시 <b>주관사 선보상</b> → 해피콜 종결 ·
무상 A/S 최소 2년(업체 · 품목별 상이, 계약서 명시) · 주관 창구 입주 후 1년 · 하자 예치금 최대 1억원(엣지컴퍼니 자산) · 업체 도산 시 동종업체 이관(A/S 비용 주관사 부담)</div>
<p class="note">공고 대응: 2항 심사 2(신뢰성 — 하자이행) · 3항 9(하자 · A/S · 분쟁 손해배상) · 4항 15 · 5항 가산점 5(A/S 정책). 아래 기준은 공동구매 입찰제안서(제출서류 10)의 하자보증 · 주관 콜센터 · 맞춤 제안 장과 같습니다.</p>

<h2>1. 대응 원칙</h2>
<table class="t kv"><tbody>
<tr><td class="k" style="width:19%">책임 구분</td><td class="l">시공 하자를 공동구매 업체에 떠넘기지 않고, 공동구매 하자를 시공사 탓으로 돌리지 않습니다 — 접수 즉시 유형부터 나눕니다.</td></tr>
<tr><td class="k">기한 관리</td><td class="l">24시간 1차 회신 · 48시간 하자보수 원칙 · 지연 건은 사유와 함께 기록하고 보고합니다.</td></tr>
<tr><td class="k">입주민 먼저</td><td class="l">업체가 응하지 않아도 주관사가 먼저 보상하고, 업체와는 계약 조항에 따라 나중에 정산합니다.</td></tr>
<tr><td class="k">업체 부담 관리</td><td class="l">콜센터 비용은 주관사 부담 · 업체 예치금 · 추가 보증금 없음 — A/S 비용이 공구가로 옮겨 가지 않게 합니다.</td></tr>
</tbody></table>

<h2>2. 접수 창구와 처리 기한</h2>
<table class="t kv"><tbody>
<tr><td class="k" style="width:19%">한 창구 접수</td><td class="l">주관 콜센터 {D.TEL}(평일 09:00 ~ 18:00) · 온라인 365일 접수(카페 신문고 · 카카오채널 · 홈페이지) — 접수 내용은 모두 기록합니다.</td></tr>
<tr><td class="k">회신 · 처리</td><td class="l"><b>24시간 안에 1차 회신</b> · <b>48시간 하자보수 원칙</b> · 처리 후 해피콜로 완료 확인(시공 품목은 입주민 확인 서명)</td></tr>
<tr><td class="k">책임자</td><td class="l">{D.MANAGER[1]} {D.MANAGER[0]}(총괄 책임 · {D.MANAGER[2]}) · 단지 전담 PM 1명 지정(성명 · 연락처는 협약 시 제출) · 대외지원팀이 민원 · 하자 접수와 시공사 협의 자료 담당</td></tr>
<tr><td class="k">운영 기간</td><td class="l">주관 창구는 입주 후 1년 운영 · 품목 무상 A/S 최소 2년(업체 · 품목별 상이) · 협약 종료 후에도 해당 계약의 이행 · 보증 기간 동안 규정 효력 유지</td></tr>
<tr><td class="k">현장 거리</td><td class="l">{ST['local']} 시공업체 우선 선정 — 48시간 A/S가 가능한 거리 · 입주 집중기에는 단지 안 임시 상주 창구(입예협 · 관리주체 협의) · 전기 · 조명은 당사({D.ELEC_LICENSE})가 직접 검토 · 시공</td></tr>
</tbody></table>

<h2>3. 하자 유형별 처리 책임 구분</h2>
<table class="t"><thead><tr><th style="width:17%">접수 유형</th><th style="width:24%">예</th><th style="width:26%">처리 책임</th><th>주관사 역할</th></tr></thead><tbody>
{"".join(f'<tr><td class="k">{a}</td><td class="l">{b}</td><td class="l">{c}</td><td class="l">{d}</td></tr>' for a, b, c, d in DEFECT)}
</tbody></table>

<h2>4. 단계별 하자 대응 일정 ({SITE} · 입주 {ST['movein']})</h2>
<table class="t"><thead><tr><th style="width:15%">시기</th><th style="width:14%">단계</th><th>하자 예방 · 대응 업무</th></tr></thead><tbody>
{"".join(f'<tr><td class="k" style="text-align:center">{a}</td><td>{b}</td><td class="l">{e(c)}</td></tr>' for a, b, c in stages)}
</tbody></table>
<p class="note">※ 일정은 제안서 월별 업무 타임테이블과 같고, 박람회 · 사전점검 일정은 입예협 · 시공사와 확정합니다. 입주가 늦어지면 일정도 함께 조정합니다.</p>

<h2>5. 처리 절차와 유형별 처리 기준</h2>
<div class="flow">{flow}</div>
<table class="t" style="margin-top:7pt"><thead><tr><th style="width:17%">품목</th><th style="width:22%">컴플레인 예시</th><th>해결 방법</th><th style="width:17%">처리 기준</th></tr></thead><tbody>
{"".join(f'<tr><td class="k">{a}</td><td class="l">{b}</td><td class="l">{c}</td><td>{d}</td></tr>' for a, b, c, d in RULE["CPL"])}
</tbody></table>
<p class="note">※ 민원 처리에 쓰는 개인정보는 처리 목적에만 쓰고, 입예협 보고에는 동 · 호수 · 연락처를 싣지 않습니다.</p>

<h2>6. 참여업체 하자보증 관리 — 특약이행각서 9개 항(참여 조건)</h2>
<table class="t"><thead><tr><th style="width:5%">No</th><th style="width:15%">항목</th><th>내용</th><th style="width:5%">No</th><th style="width:15%">항목</th><th>내용</th></tr></thead><tbody>
{"".join('<tr>' + "".join(f'<td>{i + 1}</td><td class="k">{OATH9[i][0]}</td><td class="l">{OATH9[i][1]}</td>' if i < 9 else '<td></td><td></td><td></td>' for i in (r, r + 5)) + '</tr>' for r in range(5))}
</tbody></table>
<p class="note">※ 각서 문구는 입예협 협의 후 확정 · 업체 전원에게 최종 확정 시 징구(물품공급계약서 · 청렴이행서약서와 함께). 불이행 업체 패널티: 1단계 홍보정지 → 2단계 총액 10% 배상 → 3단계 자격박탈 · 입예협 승인 후 전 계약 대체업체 이관.</p>

<h2>7. 손해배상 · 보상 재원</h2>
<table class="t kv"><tbody>
<tr><td class="k" style="width:19%">주관사 선보상</td><td class="l">참여업체가 하자보수 · 취소 · 환불을 지연하거나 거부하면, 주관사가 사실을 확인한 뒤 계약자에게 피해 금액을 <b>먼저 보상</b>하고 참여업체와는 계약 조항에 따라 정산합니다(환불 규정 제7조 · 특약이행각서).</td></tr>
<tr><td class="k">업체 도산 · 미시공</td><td class="l">동종업체로 사후관리를 이관하고, 그 A/S 비용은 주관사가 전액 부담합니다.</td></tr>
<tr><td class="k">하자 예치금</td><td class="l">최대 1억원 — 엣지컴퍼니 자산으로 예치(참여업체에게 걷은 돈이 아님) · 선보상 재원 · 사용 내역 공개. 예치 금액은 단지 규모와 입예협 협의로 정합니다.</td></tr>
<tr><td class="k">이행 담보</td><td class="l">협약 시 입예협과 협의해 이행 담보 방안을 마련합니다.</td></tr>
<tr><td class="k">행사 중 사고</td><td class="l">박람회 확정 시 행사 기간 · 장소에 맞춰 행사주최자배상책임보험 특약을 추가 가입합니다(제출서류 5 · 입예협 요청 시 가입증명서 제출).</td></tr>
<tr><td class="k">가격 보호</td><td class="l">최저가 차액 10배 보상(환불 규정 제8조 — 동일 브랜드 · 모델 새 제품, 계약 후 7일 이내 인근({ST['local']}) 오프라인 매장 정상 판매가 / 제외: 온라인 · 홈쇼핑 판매 · 시공 품목 · 행사가 등).</td></tr>
</tbody></table>

<h2>8. 보고 · 공개</h2>
<table class="t"><thead><tr><th style="width:22%">보고</th><th style="width:26%">시점</th><th>담는 내용</th></tr></thead><tbody>
{"".join(f'<tr><td class="k">{a}</td><td>{b}</td><td class="l">{c}</td></tr>' for a, b, c in REPORT)}
</tbody></table>
<p class="body" style="font-size:10pt;margin-top:10pt">당사는 위 계획을 모든 공동구매 계약서와 참여업체 특약이행각서에 반영하고, 협약 시 입예협과 협의하여 협약서에 그대로 적겠습니다.</p>
{sign()}"""
    return doc("15 하자 보수 대응 방안 상세 계획서", [p])


# ================================================================== 12 최근 3년 500세대 이상 실적 + 증빙
EV_OF = {  # 1,000세대 이상 주관 8개 단지의 증빙(별첨 번호)
    "e편한세상 송도 더퍼스트비치": "BEXCO 공식 행사일정(별첨 2 붙임 3)",
    "에코델타 대성베르힐": "입주자 모임 카페 주관사 공지(별첨 2 붙임 2)",
}


def doc12_cover():
    r5 = D.RECENT3_500
    r500 = bool(D.R500_DOC) and os.path.exists(D.R500_DOC)
    nice_names = {r[1] for r in D.RECENT3}
    rows = ""
    for i, (m, nm, n, j) in enumerate(r5, 1):
        if j:
            ev = EV_OF.get(nm) or ("NICE 연혁(별첨 1) · 실적 확약서(별첨 2)" if nm in nice_names else None)
            assert ev, f"주관 단지 증빙 없음: {nm}"
        else:
            _have = getattr(D, "R500_HAVE", {})
            ev = _have[nm] if (r500 and nm in _have) else ("요청 시 제출" if r500 else todo("증빙 자료 본부장 준비 중"))
        rows += (f'<tr class="{"jg" if j else ""}"><td>{i}</td><td>{m}</td><td class="l">{e(nm)}</td><td class="r">{n:,}</td>'
                 f'<td class="g">{"주관" if j else "진행"}</td><td class="l">{ev}</td></tr>')
    tot, nj = sum(r[2] for r in r5), sum(1 for r in r5 if r[3])
    hj = sum(r[2] for r in r5 if r[3])
    body = f"""{head("제출서류 12", "최근 3년 500세대 이상 행사 실적 및 공동구매 증빙자료")}
<p class="note" style="margin-top:6pt">기준: 공고 3항 6 · 4항 12 — 최근 3년 이내 500세대 이상 공동주택 입주박람회(공동구매 포함) 진행 · 단지 입주 연월 2023.10 ~ 2026.12(2027년 입주 예정 단지 제외) · 단지명 · 세대수는 당사 수임 목록 기준.</p>
<table class="t ls" style="margin-top:6pt"><thead><tr><th style="width:5%">No</th><th style="width:10%">입주</th><th>단지명</th><th style="width:10%">세대수</th><th style="width:7%">구분</th><th style="width:34%">증빙</th></tr></thead>
<tbody>{rows}
<tr class="sum"><td colspan="3">합계 {len(r5)}개 단지 (그중 1,000세대 이상 주관 {nj}개 단지 · {hj:,}세대)</td><td class="r">{tot:,}</td><td></td><td></td></tr></tbody></table>
<div class="box"><b>공고 3항 6 대비</b> &nbsp; 요건: 최근 3년 이내 500세대 이상 입주박람회 진행 10회 이상 &nbsp;→&nbsp; <b>{len(r5)}개 단지 · {tot:,}세대</b><br>
‘주관’ = 당사가 입주박람회 주관사로 수행한 1,000세대 이상 단지(NICE 연혁 · BEXCO 행사일정 · 단지 카페 공지로 확인) · ‘진행’ = 당사 수임으로 입주박람회 · 공동구매를 진행한 단지.{(' · 증빙 첨부 주관 ' + str(nj) + ' + 진행 ' + str(len(getattr(D, 'R500_HAVE', {}))) + ' = <b>' + str(nj + len(getattr(D, 'R500_HAVE', {}))) + '회</b>(10회 충족)') if r500 else ''}</div>
<ol class="pl" style="margin-top:6pt"><li style="font-weight:800;color:#0D1E33">별첨</li>
<li class="sm">별첨 1. NICE디앤비 기업신용평가보고서 ‘연혁’ 발췌 — 1쪽(주관 실적 6개 단지 · 보고서는 제출서류 9)</li>
<li class="sm">별첨 2. 실적 확약서(1,000세대 이상 입주박람회 주관 10개 단지) — 붙임 1 · 2 단지 카페 주관사 공지 캡처(입주민 닉네임 가림) · 붙임 3 BEXCO 공식 행사일정 캡처</li>
<li class="sm">별첨 3. 500세대 이상 진행 단지 증빙 자료 — {"첨부" if r500 else todo("본부장 준비 중")}</li>
</ol>
<p class="note">※ 입예협 요청 시 계약서 · 정산 자료 등 증빙을 지체 없이 추가 제출합니다. 주관 시기(NICE 연혁)와 입주 연월은 다를 수 있습니다.</p>
<p class="body" style="font-size:10pt;margin-top:6pt">위 실적은 사실과 다름이 없음을 확인하며, 허위로 확인될 경우 공고 6항 4 · 7항 2에 따른 어떠한 조치도 이의 없이 따르겠습니다.</p>{sign().replace('class="sign"', 'class="sign" style="margin-top:6pt"').replace('class="to"', 'class="to" style="margin-top:8pt"')}"""
    return doc("12 최근 3년 500세대 이상 행사 실적 및 공동구매 증빙자료", [body])


# 별첨 1 — NICE 원본 9쪽 연혁 발췌(탕정 docs_tj.annex07과 같은 방식 · 오산 표기)
FONTS = os.path.join(HERE, "..", "통합제안서", "fonts")
NAVY, GOLD, GRAY, LINE = (0.051, 0.118, 0.2), (0.78, 0.66, 0.42), (0.36, 0.4, 0.46), (0.79, 0.81, 0.84)
CLIP_TITLE = fitz.Rect(0, 0, 595, 76)
CLIP_HIST = fitz.Rect(36, 321, 560, 511)
ROWS_RECENT = (398, 506)     # 연혁 표 중 최근 3년 주관 실적 6행(2023/11 ~ 2026/07)
CLIP_FOOT = fitz.Rect(36, 800, 560, 828)


def annex12_nice(nice_path, out_path):
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
    text(R, 51.5, "제출서류 12 최근 3년 500세대 이상 행사 실적 및 공동구매 증빙자료", 8.5, "r", GRAY, "r")
    pg.draw_line((L, 64), (R, 64), color=NAVY, width=2)
    text(L, 92, "NICE디앤비 기업신용평가보고서 ‘연혁’ 발췌", 17, "b")
    text(L, 110, f"건명 : {D.NOTICE} ({D.NOTICE_DATE} 공고)", 8.8, "r", GRAY)
    top = 126
    cover = fitz.Rect(L, top, L + 168, top + 168 * 842 / 595)
    pg.show_pdf_page(cover, nice, 0)
    pg.draw_rect(cover, color=LINE, width=0.6)
    info = [("보고서명", "CLIP 기업신용평가보고서"), ("발행 기관", "NICE디앤비 (dun & bradstreet)"),
            ("평가 대상", f"{D.COMPANY} ({D.BIZ_NO})"), ("관리번호", "11125949-202605-001"),
            ("평가완료일", D.NICE_DATE), ("발췌 범위", "9쪽 ‘04 영업 현황(기업개요)’ 중 ‘연혁’"),
            ("원본 분량", f"전 {len(nice)}쪽 (발췌 · 표지는 제출서류 9)")]
    x0, x1, xk, rh = L + 186, R, L + 186 + 70, 24
    for i, (k, v) in enumerate(info):
        y = top + i * rh
        pg.draw_rect(fitz.Rect(x0, y, xk, y + rh), color=LINE, fill=(0.945, 0.929, 0.894), width=0.6)
        pg.draw_rect(fitz.Rect(xk, y, x1, y + rh), color=LINE, width=0.6)
        text(x0 + 8, y + 15.5, k, 8.8, "b")
        text(xk + 8, y + 15.5, v, 8.8, "r", (0.1, 0.14, 0.2))
    y = top + len(info) * rh + 18
    text(x0, y, "아래 연혁 중 금색 테두리 6행이 공고일 기준 최근 3년", 8.8, "r", GRAY)
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
    yy, mm, dd = D.SIGN_DATE
    text((L + R) / 2, y + 26, f"{yy}년 {mm}월 {dd}일", 10, "r", (0.1, 0.14, 0.2), "c")
    who = f"{D.COMPANY}   대표이사   {D.CEO}"
    text((L + R) / 2 - 14, y + 52, who, 11, "b", NAVY, "c")
    sx = (L + R) / 2 - 14 + F["b"].text_length(who, fontsize=11) / 2 + 30
    text(sx, y + 52, "(인)", 10, "r", GRAY)
    o.set_metadata({"title": "별첨 1 NICE 기업신용평가보고서 연혁 발췌", "author": D.COMPANY})
    o.save(out_path, garbage=GARBAGE, deflate=True)
    return out_path


# 별첨 2 — 실적 확약서(분당 14 ④ 방식): 탕정 hwakyak.py의 실적 · 캡처 목록을 읽기만 한다
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


def doc12_hwakyak():
    hw = _hwakyak()
    yy, mm, dd = D.SIGN_DATE
    for f, _t, _u, _w, boxes in hw.CAPS:  # 가림본이 없으면 원본 캡처에서 다시 가림(픽셀로 굳힘)
        dst = os.path.join(HERE, "assets_ins", "cafe_" + f)
        if not os.path.exists(dst):
            hw.mask(os.path.join(CAP_DIR, f), boxes, dst)
    # 분당과 같은 표기: 사상 붙임은 '입주민 소통 카페'의 주관사 게시판(입예협 공식 카페 아님)
    src_fix = {"입예협 카페 공지 (붙임 1)": "입주민 카페 주관사 게시판 (붙임 1)", "입예협 카페 공지 (붙임 2)": "입주자 모임 카페 주관사 공지 (붙임 2)"}
    recs = [(a, b, c, n, src_fix.get(s, s)) for a, b, c, n, s in hw.RECS]
    assert any("입주민 카페" in r[4] for r in recs), "사상 근거 표기 — 탕정 hwakyak.py RECS 문구가 바뀜"
    rows = "".join(f'<tr><td>{i}</td><td>{e(a)}</td><td class="l">{e(b)}</td><td>{e(c)}</td><td class="r">{n:,}</td><td class="l">{e(s)}</td></tr>'
                   for i, (a, b, c, n, s) in enumerate(recs, 1))
    tot = sum(r[3] for r in recs)
    assert (len(recs), tot) == (10, 19563), "실적 확약서 합계가 제안서(10개 단지 · 19,563세대)와 다름"
    p1 = f"""<section class="pg">
<div style="font-size:9pt;color:#9A7B3F;font-weight:700;letter-spacing:.1em">별첨 2 · 제출서류 12</div>
<h1>실 적 확 약 서</h1><div class="sub">1,000세대 이상 공동주택 입주박람회 주관 실적</div>
<table class="info"><tr><th>상호</th><td>{D.COMPANY}</td><th>대표이사</th><td>{D.CEO}</td></tr>
<tr><th>소재지</th><td colspan="3">{D.ADDRESS}</td></tr>
<tr><th>제출처</th><td colspan="3">{e(D.CLIENT)}</td></tr></table>
<p class="body">당사는 「{e(D.NOTICE)}」 3항 6 · 4항 12와 관련하여, 1,000세대 이상 공동주택 단지의 입주박람회 주관 실적을 아래와 같이 제출하며 기재 내용이 사실임을 확약합니다.</p>
<table class="t"><tr><th>연번</th><th>주관 시기</th><th>단지명</th><th>지역</th><th>세대수</th><th>근거</th></tr>{rows}
<tr class="sum"><td colspan="4">합계 {len(recs)}개 단지</td><td class="r">{tot:,}</td><td></td></tr></table>
<div class="note">※ 근거: NICE 기업신용평가보고서(평가일 {D.NICE_DATE}) '연혁'(별첨 1 · 원본 9쪽) · 단지 카페(입주민 · 입주자 모임 카페)의 주관사 명의 공지 · BEXCO 공식 행사일정(붙임). 세대수는 NICE 연혁 기재값(카페 공지 · BEXCO 근거 3개 단지는 단지 공식 총세대수). 공고 기준 최근 3년 밖(2023.10 이전) 2개 단지를 포함한 전체 주관 실적입니다.</div>
<ol><li>위 실적은 당사가 입주박람회 주관사로서 직접 수행한 것입니다.</li>
<li>귀 협의회가 요청하면 계약서, 실적 확인서, 정산 자료 등 증빙을 지체 없이 제출하겠습니다.</li>
<li>기재 내용이 사실과 다른 것으로 밝혀지면 공고 6항 4 · 7항 2에 따른 입찰 무효 · 협약 해지 등 모든 조치를 이의 없이 받아들이겠습니다.</li></ol>
<div class="sign"><div class="d">{yy}년 &nbsp;{mm}월 &nbsp;{dd}일</div>
{D.COMPANY}<br><b>대표이사 &nbsp;{" ".join(D.CEO)}</b><span style="margin-left:48pt">(인)</span></div>
<div class="to">{e(D.CLIENT)} 귀중</div></section>"""
    caps = ""
    for f, title, url, what, boxes in hw.CAPS:
        kind = ("전시장 공식 행사일정 캡처" if f.startswith("bexco") else
                "입주민 소통 카페 주관사 게시판 캡처" if f.startswith("sasang") else "입주자 모임 카페 주관사 공지 캡처")
        caps += (f'<section class="pg"><h2>실적 확약서 붙임 · {kind}</h2><div class="cap"><h3>{e(title)}</h3>'
                 f'<div class="u">{e(url)}{" · 입주민 닉네임(동·호수)은 개인정보 보호를 위해 가림" if boxes else ""}</div><div class="k">{e(what)}</div>'
                 f'<img src="../assets_ins/cafe_{f}"></div></section>')  # HTML은 작업/ 아래
    return f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>실적 확약서</title><style>{hw.CSS}{HW_FIT}</style></head><body>{p1}{caps}</body></html>'


# ------------------------------------------------------------------ PDF · 날인 · 병합(분당 docs_bd.py와 같은 방식)
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
    """'(인감날인)' 또는 '(인)' 가운데에 직인(54pt) — 저장 garbage=3 · 글자 대조."""
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


NAMES = {  # 제출본 파일 이름(공고 4항 번호 · 항목)
    "01": "01_입찰신청서", "02": "02_사업자등록증_통장사본", "03": "03_법인등기부등본", "04": "04_인감증명서_사용인감계",
    "05": "05_배상책임보험_증권_가입계획", "06": "06_계좌잔고증명서", "07": "07_국세_지방세_완납증명서",
    "08": "08_4대보험_가입자명부_완납증명서", "09": "09_기업신용평가", "10": "10_공동구매_입찰제안서", "11": "11_업무이행각서",
    "12": "12_최근3년_500세대이상_실적_공동구매증빙", "14": "14_AS_이행각서", "15": "15_하자보수_대응방안_상세계획서",
    "16": "16_선정결과_이의제기_금지서약서",
}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    final = "--final" in sys.argv
    if not args:
        sys.exit(__doc__)
    seal_path = args[0]
    nice_src = f"{EV}/NICE_기업신용평가.pdf"
    assert os.path.getmtime(P10_MAIL) >= os.path.getmtime(P10), "제안서 메일용이 원본보다 오래됨 — mail_lite.py 다시"
    assert len(fitz.open(P10_MAIL)) == len(fitz.open(P10)), "제안서 메일용 쪽수가 원본과 다름"
    evidence_check()

    ok, miss = readiness()
    if miss:
        print(f"[확인 필요 {len(miss)}건]\n  - " + "\n  - ".join(miss))
        if final:
            sys.exit("--final: 확인 필요 건이 남아 있어 파일을 쓰지 않고 멈춤")
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(SUBMIT, exist_ok=True)
    seal = seal_image(seal_path)

    def stamped(p, n_expect=1):
        o, n = stamp(seal, p)
        assert n == n_expect, f"날인 자리 {n}곳(예상 {n_expect}): {p}"
        return o

    res, n = {}, {"10": len(fitz.open(P10))}
    res["15"] = stamped(fit(render("15_하자보수_대응방안_상세계획서", doc15()), 2, 4))
    n["15"] = len(fitz.open(res["15"]))
    res["01"] = stamped(fit(render("01_입찰신청서", doc01(n)), 2))
    biz = fitz.open(f"{EV}/사업자등록증.pdf")
    for pg_ in biz:
        for a in list(pg_.annots()):  # 발급 뒤 덧붙인 스탬프 주석이 원본 칸을 가리지 않게
            pg_.delete_annot(a)
    res["02"] = merge(NAMES["02"], [biz, f"{EV}/법인통장_사본.pdf"], "2 사업자등록증 · 법인 통장 사본")
    res["03"] = merge(NAMES["03"], [f"{EV}/법인등기부등본.pdf"], "3 법인등기부등본")
    gam_print = out("04_2_사용인감계_출력용.pdf")  # 사용인감 칸에만 디지털 직인 — 이 파일만 출력해 법인인감 실물 날인
    os.replace(stamped(fit(render("04_2_사용인감계_직인전", doc04_seal()), 1)), gam_print)
    gam = D.SEAL_SCAN if ok["04"] else gam_print
    res["04"] = merge(NAMES["04"], [f"{EV}/법인인감증명서.pdf", gam], "4 인감증명서 · 사용인감계")
    res["05"] = merge(NAMES["05"], [stamped(fit(render("05_1_표지", doc05()), 1)), KB], "5 배상책임보험 증권 · 행사주최자배상책임보험 가입 계획")
    res["06"] = merge(NAMES["06"], [f"{EV}/잔액증명서_1013_가림.pdf"], "6 계좌 잔액증명서")
    # 본부장 10-16: 06 발급일(2026.10.14 = 공고일 이후)에 형광펜 표시 — 내용은 그대로, 노란 반투명 띠만 얹음
    _d = fitz.open(res["06"]); _p = _d[0]
    _a = _p.add_rect_annot(fitz.Rect(361, 631.5, 495, 647.5))  # 곱하기(Multiply) 합성 → 글자는 진하게 남고 바탕만 노랗게
    _a.set_colors(stroke=None, fill=(1, 0.93, 0.2)); _a.set_border(width=0); _a.set_blendmode(fitz.PDF_BM_Multiply); _a.set_opacity(0.85); _a.update()
    _d.save(res["06"] + ".tmp", garbage=3, deflate=True); _d.close(); os.replace(res["06"] + ".tmp", res["06"])
    res["07"] = merge(NAMES["07"], [f"{EV}/국세_납세증명서.pdf", f"{EV}/지방세_납세증명서.pdf"], "7 국세 · 지방세 완납증명서")
    res["08"] = merge(NAMES["08"], [ROSTER, f"{EV}/4대보험_완납증명서.pdf", f"{EV}/고용산재_완납증명서.pdf"], "8 4대보험 가입자 명부 · 완납증명서")
    res["09"] = merge(NAMES["09"], [fit(render("09_1_표지", doc09_cover()), 1), nice_extract(nice_src)], "9 기업신용평가(NICE)")
    res["10"] = out(NAMES["10"] + "_메일용.pdf")  # 작업/ = 메일용 사본(13MB) · 제출본/ = 원본(아래)
    shutil.copyfile(P10_MAIL, res["10"])
    res["11"] = stamped(fit(render("11_업무이행각서", doc11()), 1))
    a1 = stamped(annex12_nice(nice_src, out("12_2_별첨1_NICE연혁발췌.pdf")))
    parts12 = [stamped(fit(render("12_1_실적표", doc12_cover()), 1)), a1, stamped(fit(render("12_3_별첨2_실적확약서", doc12_hwakyak()), 4))]
    names12 = ["실적표(20개 단지)", "별첨 1 NICE 연혁 발췌", "별첨 2 실적 확약서 · 붙임 1 ~ 3"]
    if ok["12"]:
        parts12.append(D.R500_DOC)
        names12.append("별첨 3 진행 단지 증빙")
    toc, pg0 = [], 1
    for nm, p in zip(names12, parts12):
        toc.append([1, nm, pg0])
        pg0 += len(fitz.open(p))
    res["12"] = merge(NAMES["12"], parts12, "12 최근 3년 500세대 이상 행사 실적 및 공동구매 증빙자료", toc)
    res["14"] = stamped(fit(render("14_AS_이행각서", doc14()), 1))
    res["16"] = stamped(fit(render("16_선정결과_이의제기_금지서약서", doc16()), 1))

    # ---- 제출본/: 조치 끝난 서류만(지난 실행 파일은 지우고 다시) · 10은 원본
    for f in os.listdir(SUBMIT):
        if f.endswith(".pdf"):
            os.remove(os.path.join(SUBMIT, f))
    lines = [f"[제출 현황 · 내부용 — 첨부 금지] {SITE} · 접수 {D.SUBMIT_TO} · 제목 {D.MAIL_TITLE} · 마감 {D.DEADLINE}", ""]
    print("\n[작업본 — 공고 4항 순서 · 지금 상태 그대로]")
    attach = []
    for k in sorted(res, key=int):
        v = res[k]
        good = ok.get(k, True)
        src = P10 if k == "10" else v
        msg = f"{k} {'제출 가능' if good else '조치 필요'}  {PFX}{NAMES[k]}.pdf  {len(fitz.open(src))}p  {os.path.getsize(src) / 1e6:.2f}MB"
        print(msg)
        lines.append(msg)
        if good:
            dst = os.path.join(SUBMIT, PFX + NAMES[k] + ".pdf")
            shutil.copyfile(src, dst)
            attach.append(dst)
    lines.append("13 해당 없음 — 파일 없음(협약 시 입예협과 협의해 이행 담보 방안 마련)")
    if os.path.exists(ZIP):
        os.remove(ZIP)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for p in attach:
            z.write(p, os.path.basename(p))
    zmb = os.path.getsize(ZIP) / 1e6
    full = sum(os.path.getsize(P10 if k == "10" else v) for k, v in res.items()) / 1e6
    lite = sum(os.path.getsize(v) for v in res.values()) / 1e6
    lines += ["", f"ZIP(제출본 {len(attach)}개): {ZIP}  {zmb:.1f}MB",
              f"16종 모두 찼을 때(지금 작업본 기준) PDF 합계: 원본 제안서 {full:.1f}MB · 메일용 제안서 {lite:.1f}MB"]
    if miss:
        lines += ["", "조치 필요:"] + [f"  - {m}" for m in miss]
    text = "\n".join(lines) + "\n"
    pathlib.Path(WORK, "제출현황.txt").write_text(text, encoding="utf-8")
    print("\n" + "\n".join(lines[-(len(miss) + 4 if miss else 3):]))
    if TODOS:
        u = list(dict.fromkeys(TODOS))
        print(f"[노란 칸 {len(u)}개]", " / ".join(u))


if __name__ == "__main__":
    main()
