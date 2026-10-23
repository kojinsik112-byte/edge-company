# -*- coding: utf-8 -*-
"""고양창릉 S-5BL 입주박람회 주관사 입찰 — 공고 ◆필수 제출서류 생성기(A4 세로). 순서 · 번호 = [별지 서식 제6호] 서류 제출 목록표.

  00 서류 제출 목록표 [별지 6호]                       01 입찰 참가 신청서 [별지 1호]
  02 사업자등록증                                      03 법인등기부등본
  04 지방세 완납 증명서                                05 국세 완납 증명서
  06 법인인감증명서(10.15 · 주민번호 뒷자리 가림본)
  07 대표이사 범죄사실증명서 — 본부장 10-19: 회보서 대신 갈음 안내 + 대표자 결격사유 부존재 서약서(분당 방식) · 회보서는 서류심사 합격 시 지참 열람
  08 주관사 제안서 = build_gy.py 결과 그대로(제출본 = 원본)
  09 최근 3년간 주관사 실적 총괄표 [별지 2호] + 실적 증빙 안내 + 별첨 1 NICE 연혁 발췌 · 별첨 2 실적 확약서(붙임 캡처 3) · 별첨 3 주관사 협약서 3건 · 별첨 4 BEXCO 행사일정 5곳(2쪽)
  09-2 4대 보험 완납증명서(건강 · 연금 + 고용 · 산재)
  10 하자 보수 이행 각서 [별지 3호]                    11 청렴계약 이행 준수 서약서 [별지 4호]
  12 영업배상책임보험 증서(KB · 시설소유관리자)
  13 계약이행보증보험 — 주관사 선정 후(파일 없음)
  14 서약서(이의 제기 금지) [별지 5호]                 15 신용평가서 상세내역(NICE 전문 24쪽 · 대표 외 임직원 생년월일 가림)
  16 사업장 및 조직현황(공고 필수 제출서류 · 목록표 밖)  17 기타 · 요약제안서(선택 자료)
별지는 서식(hwp) 문구를 그대로 옮기고 빈칸만 채운다(별지 3 '상단 금액'은 '상당 금액' 오타로 보고 고침). 숫자 · 약속은 data.py와 제안서(08)에 이미 쓴 것만.

날인: 서식이 '직인 또는 인감'이라 직인(배경 투명 PNG)을 '(인)' 자리에 찍는다(../동탄파라곤3차/stamp.py와 같은 자리 · 크기).
  법인인감은 디지털로 만들지 않는다 — 실물 인감을 원하면 작업/의 '_직인전' 파일을 출력해 날인 · 스캔.

조치 필요(TODO) — 노란 칸 · [확인 필요]로 집계하고 그 서류는 제출본/에 넣지 않는다(--final이면 파일을 쓰기 전에 멈춤)
  01 별지 1 책임자(주관사업 총괄 본부장) 생년월일 → org_private.json 'mgr_birth'
  09 별지 2 협약서 3개 단지(센터포인트 · 드파인 센텀 · 디에트르)의 박람회 일정 · 행사 장소 → data.EXPO_VENUE

출력: 작업/ = 중간 파일(HTML · 직인 전 PDF · 지금 상태 그대로의 00 ~ 17) + 제출현황.txt(내부용 — 첨부 금지)
      제출본/ = 조치 끝난 서류만 '엣지컴퍼니_고양창릉S5_NN_항목.pdf' · ZIP = 공고 '폴더별 .zip' — 번호_항목/ 폴더마다 해당 PDF
사용: python docs_gy.py <직인.png> [--final]     (결과 PDF · HTML · ZIP은 깃 제외 — .gitignore)
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
import zipfile

import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "요약제안서"), os.path.join(HERE, "..", "동탄파라곤3차")]
import data as D  # noqa: E402
from build import find_chrome  # noqa: E402

e = html.escape
PFX = "엣지컴퍼니_고양창릉S5_"
ST = D.SITE
SITE = ST["name"]
FORM_TO = "창릉신도시 S5 입주예정자협의회"      # 서식(별지 1 ~ 6) 원문 표기 그대로
TODOS = []

SP = "/tmp/claude-0/-home-user-edge-company/a96d9eb6-5244-5d3f-9f1b-6f379ac2a82c/scratchpad"
EV = os.environ.get("GY_EVIDENCE", f"{SP}/evidence")  # 증빙 원본(깃 제외)
ROSTER = f"{SP}/cs_sub/엣지컴퍼니_4대보험_사업장가입자명부_20261023_가림.pdf"   # 2026.10.23 발급 13명 · 가림본(깃 제외) — 16에 붙임
KB = f"{EV}/KB_영업배상책임보험_시설소유관리자_20261014.pdf"
NICE_SRC = f"{EV}/NICE_기업신용평가.pdf"
CAP_DIR = f"{SP}/hw/cap"  # 실적 확약서 캡처 원본(가림본 assets_ins/cafe_*.png가 없을 때만)
WORK = os.path.join(HERE, "작업")
SUBMIT = os.path.join(HERE, "제출본")
ZIP = os.path.join(HERE, PFX + "제출서류.zip")
# 본부장 10-21: 제출본 = 밝은 버전(tools/light_build.py) · 메일용 경량본은 쓰지 않음(원본 그대로 대용량 첨부)
P08 = os.path.join(HERE, PFX + "입주박람회_주관사_제안서_밝은시안.pdf")
P17 = os.path.join(HERE, PFX + "요약제안서_밝은시안.pdf")  # summary_gy.py(본부장 10-17: 공고 서류에 없어도 요약본은 만든다)

_priv = os.path.join(HERE, "org_private.json")  # 깃 제외(생년월일 · 실명)
PRIV = json.load(open(_priv, encoding="utf-8")) if os.path.exists(_priv) else {}
CEO_BIRTH = D.CEO_BIRTH or PRIV.get("ceo_birth")
MGR_BIRTH = D.MGR_BIRTH or PRIV.get("mgr_birth")


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
.t.ls{font-size:8.7pt;line-height:1.35}ol.pl li.sm{font-size:9.2pt;margin-top:2pt;line-height:1.5}.t.ls td{padding:2pt 5pt}
.t tr.jg td{background:#FBF8F1}.t tr.jg td.g{color:#9A7B3F;font-weight:800}
.t tr.sum td{background:#F1EDE4;font-weight:800}
.t tr.gh td{background:#0D1E33;color:#fff;font-weight:800;text-align:left;font-size:8.6pt;letter-spacing:.02em}
.box{border:1pt solid #C8A86A;background:#FBF8F1;border-radius:4pt;padding:7pt 11pt;margin-top:10pt;font-size:9.8pt;line-height:1.65}
.box b{color:#0D1E33}
p.body{margin-top:12pt;font-size:10.5pt;line-height:1.85}
.note{font-size:8.8pt;color:#5B6676;margin-top:5pt;line-height:1.55}
ol.pl{list-style:none;margin-top:8pt}
ol.pl li{padding-left:16pt;text-indent:-16pt;margin-top:5pt;font-size:10.2pt;line-height:1.72}
.sign{margin-top:16pt;text-align:center;break-inside:avoid}
.sign .d{font-size:11pt;letter-spacing:.06em}
.sign .who{margin-top:6pt;font-size:12pt;font-weight:700}
.sign .seal{color:#5B6676;font-size:10pt;font-weight:400;margin-left:30pt}
.to{margin-top:18pt;text-align:center;font-size:12.5pt;font-weight:800;color:#0D1E33}
/* 공고 별지 서식 — 흑백 */
.form{color:#111;font-size:11pt;line-height:1.85}
.form .no{font-size:10pt;color:#333}
.form h1{text-align:center;font-size:21pt;letter-spacing:.3em;color:#111;margin:14pt 0 16pt}
.form .ft{width:100%;border-collapse:collapse;font-size:10.3pt}
.form .ft th,.form .ft td{border:.8pt solid #333;padding:6.5pt 8pt;vertical-align:middle;line-height:1.5}
.form .ft th{background:#F2F2F2;font-weight:700;text-align:center;white-space:nowrap}
.form .ft td.c{text-align:center}
.form p.tx{margin-top:14pt;text-indent:10pt;text-align:justify}
.form ol{list-style:none;margin-top:8pt}
.form ol li{padding-left:16pt;text-indent:-16pt;margin-top:6pt;text-align:justify}
.form .dt{text-align:center;margin-top:22pt;font-size:12pt;letter-spacing:.15em}
.form .sg{margin:20pt 0 0 50%;font-size:11.5pt;line-height:3.0}
.form .to2{margin-top:44pt;text-align:center;font-size:13pt;font-weight:800;line-height:1.6}
.form .sgx{display:flex;justify-content:center;align-items:center;gap:26pt;margin-top:20pt}
.form .sgx .ln{font-size:11.3pt;line-height:2.25}
.form .sgx .bx{width:80pt;height:80pt;border:1pt solid #333;position:relative;flex:none}
.form .sgx .bx i{position:absolute;left:0;right:0;top:6pt;text-align:center;font-style:normal;font-size:8.5pt;color:#777;line-height:1.25}
.form .sgx .bx b{position:absolute;left:0;right:0;top:44pt;text-align:center;font-weight:400;font-size:10pt;color:#999}
.form .warn{font-size:9pt;color:#444;margin-top:8pt;text-align:center}
.form .ft.r2 th,.form .ft.r2 td{padding:5pt 7pt;font-size:10pt}
/* 조직도(16) — 본부장 칸은 CEO → 4개 팀 줄기에서 오른쪽으로(제안서 조직 구성 쪽과 같은 배치) */
.oc{margin-top:8pt;display:flex;flex-direction:column;align-items:center}
.oc .ceo{border:1.4pt solid #C8A86A;border-radius:50%;width:78pt;height:78pt;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#0D1E33;color:#fff}
.oc .ceo i{font-style:normal;font-size:7.5pt;color:#D9C9A3}.oc .ceo b{font-size:15pt;color:#EBCB8F;line-height:1.1}.oc .ceo span{font-size:9pt;letter-spacing:.2em}
.oc .gmr{position:relative;width:100%;height:30pt}
.oc .gmr:before{content:'';position:absolute;left:50%;top:0;bottom:0;width:1.4pt;background:#C8A86A}
.oc .gm{position:absolute;left:calc(50% + 26pt);top:6pt;border:1.2pt solid #C8A86A;border-radius:5pt;padding:2pt 10pt;font-size:9.5pt;background:#fff}
.oc .gm:before{content:'';position:absolute;right:100%;top:50%;width:26pt;height:1.2pt;background:#C8A86A}
.oc .gm em{font-style:normal;color:#9A7B3F;font-weight:700;margin-right:6pt}
.oc .bar{width:75.6%;height:12pt;border:1.4pt solid #C8A86A;border-bottom:0;border-radius:0}
.oc .tms{display:grid;grid-template-columns:repeat(4,1fr);gap:7pt;width:100%}
.oc .tm{border:.8pt solid #C8A86A;border-radius:5pt;padding:5pt 6pt;text-align:center;background:#FBF8F1}
.oc .tm b{display:block;font-size:10pt;color:#0D1E33}.oc .tm b em{font-style:normal;color:#9A7B3F;margin-left:3pt}
.oc .tm small{display:block;font-size:8pt;color:#5B6676;line-height:1.35;margin-top:2pt}
"""

HEAD = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{t}</title>'
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">'
        '<style>{css}</style></head><body>')


def doc(title, sections, css=CSS):
    return HEAD.format(t=e(title), css=css) + "".join(f'<section class="pg">{s}</section>' for s in sections) + "</body></html>"


def head(label, title, center=False):
    return (f'<div class="top"><div class="lb">{e(label)}</div><div class="co">{D.COMPANY} · 입주박람회 주관사</div></div>'
            f'<h1 class="{"c" if center else ""}">{e(title)}</h1>'
            f'<div class="case" style="{"text-align:center" if center else ""}">건명 : {e(D.NOTICE)}</div>')


def ymd():
    return D.SIGN_DATE


def sign():
    yy, mm, dd = ymd()
    return (f'<div class="sign"><div class="d">{yy}년 {mm}월 {dd}일</div>'
            f'<div class="who">{D.COMPANY} &nbsp; 대표이사 &nbsp; {D.CEO}<span class="seal">(인)</span></div></div>'
            f'<div class="to">{FORM_TO} 귀하</div>')


def seal_tail(warn=True):
    """별지 1 · 4 · 5 서식 꼬리(원문): 업체명 · 주소 · 대표자 + '직인 또는 인감' 칸 → 날짜 → 귀하."""
    yy, mm, dd = ymd()
    w = '<div class="warn">※ 반드시 업체 인감 날인 요망. 요건 불충족 시 입찰 참가 불가함.</div>' if warn else ""
    return (f'<div class="sgx"><div class="ln">업체명 : <b>{D.COMPANY}</b><br>주 &nbsp;소 : {D.ADDRESS}<br>대표자 : <b>대표이사 {D.CEO}</b></div>'
            f'<div class="bx"><i>직 인<br>또는<br>인 감</i><b>(인)</b></div></div>{w}'
            f'<div class="dt">{yy}년 &nbsp; {mm}월 &nbsp; {dd}일</div>'
            f'<div class="to2">{FORM_TO} 귀하</div>')


def birth(v, who):
    return e(v) if v else todo(f"{who} 생년월일 — 본부장님 확인")


# ------------------------------------------------------------------ 상태 점검(파일을 쓰기 전에)
def venue_missing():  # 별지 2 = 주관 전 단지
    return [nm for _m, nm, _n, j in D.RECENT3_500 if not all(D.EXPO_VENUE.get(nm) or (None, None))]


def readiness():
    ok = {"01": bool(MGR_BIRTH), "09": not venue_missing(), "17": os.path.exists(P17)}
    miss = []
    if not ok["01"]:
        miss.append("01 별지 1 — 책임자(주관사업 총괄 본부장) 생년월일 → org_private.json 'mgr_birth'(깃 제외)에 넣고 다시 실행")
    if not ok["09"]:
        miss.append("09 별지 2 — 박람회 일정 · 행사 장소 미확인: " + " · ".join(venue_missing()) + " → data.py EXPO_VENUE")
    if not ok["17"]:
        miss.append("17 요약제안서 — summary_gy.py 먼저")
    return ok, miss


def evidence_check():
    """증빙 원본이 기재값과 맞는지 — 날짜 · 번호를 글자로 확인할 수 있는 것만."""
    t = fitz.open(KB)[0].get_text()
    for k in ("2026- 6774341", "영업배상책임보험", "시설소유관리자배상책임", "100,000,000", "300,000,000", "2027년 10월 14일 24:00"):
        assert k in t, f"KB 증권 글자 확인 실패: {k}"
    t = fitz.open(f"{EV}/사업자등록증.pdf")[0].get_text()
    assert "2026 년10 월14 일" in t and "전시,박람회및행사대행업" in t, "사업자등록증 발급일 · 종목 확인 실패"
    t = fitz.open(f"{EV}/국세_납세증명서.pdf")[0].get_text()
    assert "2026 년10 월14 일" in t and "2026 년11 월13 일" in t, "국세 납세증명서 발급일 · 유효기간 확인 실패"
    for p in (f"{EV}/법인인감증명서.pdf", f"{EV}/법인등기부등본.pdf", f"{EV}/지방세_납세증명서.pdf", f"{EV}/4대보험_완납증명서.pdf",
              f"{EV}/고용산재_완납증명서.pdf", NICE_SRC, D.R500_DOC, P08):
        assert os.path.exists(p), f"없음: {p}"
    assert len(fitz.open(D.R500_DOC)) == len(D.R500_HAVE) == 3, "협약서 3건"


# ================================================================== 00 서류 제출 목록표 [별지 6호]
def list_rows(n):
    """(번호, 서식 제출 서류명(원문), 제출 O/X, 비고) — 별지 6 순서 그대로 + 공고 필수 제출서류 중 목록표 밖 1건 · 기타 1건."""
    r5j = [r for r in D.RECENT3_500 if r[3]]
    return [
        ("1", "입찰 참가 신청서【별지서식 제1호】", "O", f"필수 · 참여인력 {D.STAFF_LEAD + sum(c for _, c, _ in D.STAFF)}명 · 책임자 {D.MANAGER[1]}"),
        ("2", "사업자 등록증", "O", f"필수 · {D.ISSUE['biz']} 발급(울산세무서)"),
        ("3", "법인등기부등본", "O", f"필수 · {D.ISSUE['reg']} 발급(최근 1개월 이내)"),
        ("4", "지방세 완납 증명서", "O", f"필수 · {D.ISSUE['ltax']} 발급"),
        ("5", "국세 완납 증명서", "O", f"필수 · {D.ISSUE['tax']} 발급(유효 ~2026.11.13)"),
        ("6", "법인인감증명서", "O", f"필수 · {D.INGAM_DATE} 발급(최근 1개월 이내 · 대표자 주민등록번호 뒷자리 가림)"),
        ("7", "대표이사 범죄사실증명서(서류심사 합격한 주관사 해당)", "O", "대표자 결격사유 부존재 서약서로 먼저 제출 · 회보서는 서류심사 합격 시 대표 지참 열람(형실효법 제6조 · 제10조)"),
        ("8", "주관사 제안서", "O", f"필수 · {n['08']}쪽"),
        ("9", "최근 3년간 500세대 이상 주관사 실적 총괄표【별지서식 2호】", "O",
         f"필수 · 주관 {len(r5j)}개 단지 · {sum(r[2] for r in D.RECENT3_500):,}세대 · 증빙: NICE 연혁 발췌 · 실적 확약서 · 주관사 협약서 {len(D.R500_HAVE)}건"),
        ("9", "4대 보험 완납증명서", "O", f"필수 · 건강 · 연금(국민건강보험공단) · 고용 · 산재(근로복지공단) 각 {D.WANNAP_DATE} 발급"),
        ("10", "하자보수(환불)이행각서【별지서식 제3호】", "O", "필수"),
        ("11", "청렴계약 이행 준수 서약서【별지서식 제4호】", "O", "필수"),
        ("12", "영업배상책임보험 증서", "O", "필수 · KB손해보험 영업배상책임보험(시설소유관리자) · 2026.10.14 ~ 2027.10.14"),
        ("13", "계약이행보증보험(주관사 선정후)", "X", "주관사 선정 후 협의회를 피보험자로 발급 · 발급 시점 · 기간은 입주 일정에 맞춰 입예협과 확인 후 제출"),
        ("14", "이의를 제기하지 않겠다는 서약서【별지서식 제5호】", "O", "필수"),
        ("15", "신용평가회사가 발급한 신용평가서 상세내역", "O", f"필수 · NICE디앤비 기업신용평가보고서 전문 {n['15n']}쪽 · 평가 {D.NICE_DATE} · BB- · 현금흐름 A"),
        ("16", "사업장 및 조직현황", "O", "공고 필수 제출서류(목록표 밖) · 사업장 · 면허 · 인증 · 조직 · 전담 배치(안) · 붙임 4대보험 가입자 명부(2026.10.23)"),
        ("17", "기타 · 요약제안서", "O", "선택 자료 · 제안서(8) 내용 요약"),
    ]


def doc00(n):
    yy, mm, dd = ymd()
    rows = "".join(f'<tr><td class="c">{no}</td><td>{e(t)}</td><td class="c">{"O" if s == "O" else ""}</td><td class="c">{"X" if s == "X" else ""}</td>'
                   f'<td class="bg">{e(r)}</td></tr>' for no, t, s, r in list_rows(n))
    body = f"""<style>.l6 th,.l6 td{{padding:3.2pt 6pt!important;font-size:9.6pt!important;line-height:1.38!important}}.l6 td.bg{{font-size:8.3pt!important;color:#333}}</style>
<div class="form"><div class="no">[별지 서식 제6호]</div><h1 style="margin:6pt 0 8pt">서류 제출 목록표</h1>
<p style="font-size:11pt;margin-bottom:6pt">업체명 : <b>{D.COMPANY}</b></p>
<table class="ft r2 l6"><thead><tr><th rowspan="2" style="width:6%">NO</th><th rowspan="2">제출 서류명</th><th colspan="2">제출/미제출</th><th rowspan="2" style="width:33%">비고</th></tr>
<tr><th style="width:8%">제출(O)</th><th style="width:8%">미제출(X)</th></tr></thead><tbody>{rows}</tbody></table>
<p class="note" style="color:#444">※ 7은 결격사유 부존재 서약서로 먼저 제출하고 회보서는 서류심사 합격 시 열람으로 확인하며, 13 계약이행보증보험은 주관사 선정 후 입주 일정에 맞춰 입예협과 발급 시점을 확인해 제출합니다. 16은 공고 ◆필수 제출서류의 ‘사업장 및 조직현황’, 17은 선택 자료입니다.
ZIP 안의 폴더 이름은 위 번호 · 서류명과 같습니다(‘9’ 두 건은 09 · 09-2).</p>
<div class="dt" style="margin-top:10pt">{yy}년 &nbsp; {mm}월 &nbsp; {dd}일</div>
<div class="to2" style="margin-top:12pt">{FORM_TO} 귀하</div></div>"""
    return doc("00 서류 제출 목록표", [body])


# ================================================================== 01 입찰 참가 신청서 [별지 1호]
def doc01():
    m = D.MANAGER
    n_staff = D.STAFF_LEAD + sum(c for _, c, _ in D.STAFF)
    body = f"""<div class="form"><div class="no">[별지 서식 제1호]</div><h1>입찰 참가 신청서</h1>
<table class="ft">
<tr><th>입 찰 명</th><td colspan="4">창릉신도시 S5 주관사 선정 입찰 공고</td></tr>
<tr><th rowspan="4">신청업체</th><th>업 체 명</th><td>{D.COMPANY}</td><th>대표자명</th><td>{D.CEO}</td></tr>
<tr><th>참여인력</th><td>{n_staff} 명</td><th>사업자등록번호</th><td>{D.BIZ_NO}</td></tr>
<tr><th>법인등록번호</th><td colspan="3">{D.CORP_NO}</td></tr>
<tr><th>주 &nbsp; &nbsp; &nbsp; 소</th><td colspan="3">{D.ADDRESS}</td></tr>
<tr><th rowspan="4">책임자</th><th>성 &nbsp; &nbsp; &nbsp; 명</th><td>{m[0]}</td><th>생년월일</th><td>{birth(MGR_BIRTH, "책임자")}</td></tr>
<tr><th>부 &nbsp; &nbsp; &nbsp; 서</th><td>주관사업</td><th>휴대전화</th><td>{m[2]}</td></tr>
<tr><th>직 &nbsp; &nbsp; &nbsp; 위</th><td>총괄 본부장</td><th>전 &nbsp; &nbsp; 화</th><td>{D.TEL}</td></tr>
<tr><th>전자메일(E-mail)</th><td>{D.EMAIL}</td><th>F A X</th><td>—</td></tr>
</table>
<p class="tx">본 업체는 주관사 입찰에 참여하고자 “{FORM_TO}”에서 정한 입찰 공고사항을 모두 승낙하고 제출서류를 첨부하여 주관사 선정 조건 및 지시 사항을 준수하겠음을 확약하며 입찰에 참가 신청합니다.</p>
{seal_tail()}</div>"""
    return doc("01 입찰 참가 신청서", [body])


# ================================================================== 07 대표이사 범죄사실증명서 — 갈음 안내 + 결격사유 부존재 서약서(분당 docs_bd 07 · 14 ① 방식 · 본부장 10-19)
def doc07():
    yy, mm, dd = ymd()
    items = [
        "금고 이상의 실형을 선고받고 그 집행이 끝나거나(집행이 끝난 것으로 보는 경우를 포함합니다) 집행이 면제된 날부터 2년이 지나지 않은 사람에 해당하지 않습니다.",
        "금고 이상의 형의 집행유예를 선고받고 그 유예기간 중에 있는 사람에 해당하지 않습니다.",
        "파산선고를 받고 복권되지 않은 사람에 해당하지 않습니다.",
        "사기 · 횡령 · 배임 · 업무방해 등 업무와 관련된 범죄로 형을 선고받고 그 형이 실효되지 않은 사람에 해당하지 않습니다.",
        "당사와 대표자는 금품 · 향응 제공, 담합, 불법 · 부정한 영업, 타 단지 입주박람회의 중대한 계약불이행으로 계약 해지 · 선정 취소된 이력이 없습니다(공고 ◆입찰 참가 제한).",
    ]
    p1 = f"""{head("제출서류 7", "대표이사 범죄사실증명서")}
<div class="box" style="margin-top:18pt;font-size:10.4pt;line-height:1.75"><b>범죄경력회보서 사본 대신 서약서를 먼저 제출합니다</b><br>
① 공고 별지 6은 대표이사 범죄사실증명서를 ‘서류심사 합격한 주관사 해당’으로 정하고 있습니다.<br>
② 「형의 실효 등에 관한 법률」은 범죄경력 조회와 그 회보를 법에서 정한 경우로 제한하고(제6조), 범죄경력자료를 목적 외로 취득 · 사용하는 것을 금지 · 처벌하도록 정하고 있습니다(제10조). 본인이 발급받는 회보서에도 ‘목적 외 사용 시 취득 · 사용자 처벌’ 안내가 인쇄되어 있습니다.<br>
③ 이에 회보서 사본 대신 <b>다음 쪽 대표자 결격사유 부존재 서약서</b>를 지금 제출합니다.<br>
④ 서류심사에 합격하여 귀 협의회가 요청하시면, 대표이사가 회보서를 지참하여 열람으로 확인하실 수 있게 하겠습니다.</div>
<p class="note" style="margin-top:10pt">※ 근거: 공고 ◆필수 제출서류 7 · [별지 서식 제6호] 7번 · 형의 실효 등에 관한 법률 제6조 · 제10조</p>"""
    lis = "".join(f'<li style="margin-top:5pt;font-size:10.4pt;line-height:1.7">{"①②③④⑤"[i]} {x}</li>' for i, x in enumerate(items))
    p2 = f"""{head("제출서류 7", "대표자 결격사유 부존재 서약서", True)}
<table class="info" style="margin-top:16pt"><tr><th>상호</th><td>{D.COMPANY}</td><th>법인등록번호</th><td>{D.CORP_NO}</td></tr>
<tr><th>대표자 성명</th><td>대표이사 {D.CEO}</td><th>생년월일</th><td>{birth(CEO_BIRTH, "대표자")}</td></tr>
<tr><th>본사 소재지</th><td colspan="3">{D.ADDRESS}</td></tr></table>
<p class="body">본인은 {D.COMPANY}의 대표이사로서 「{e(D.NOTICE)}」에 참가하면서, 당사와 본인이 공고의 입찰 참가 제한 사유에 해당하지 않음을 서약합니다.
아울러 대표이사 범죄사실증명서와 관련하여, 공동주택관리법상 동별 대표자 결격사유(제14조제4항)를 참고한 아래 기준(①~③)과 업무 관련 범죄 기준(④), 공고 입찰 참가 제한 사항(⑤)을 스스로 확인하였습니다.</p>
<div class="art" style="margin-top:8pt"><ol class="pl" style="font-size:10.4pt">{lis}</ol></div>
<p class="body">위 내용이 사실과 다르거나 중요한 사항을 누락한 것으로 확인될 경우, 선정 이후라도 공고 입찰 참가 제한(제출서류의 허위사실)에 따른 <b>선정 제외 · 계약 해지</b> 등 귀 협의회의 조치를 이의 없이 받아들이겠습니다.
귀 협의회가 요청하시면 관련 법령이 허용하는 범위에서 확인 서류를 지체 없이 제출하겠습니다(범죄경력회보서는 대표이사가 지참하여 열람으로 확인).</p>
{sign()}"""
    return doc("07 대표이사 범죄사실증명서 · 결격사유 부존재 서약서", [p1, p2])


# ================================================================== 09 [별지 2호] 실적 총괄표 + 증빙 안내
def _expo(nm):
    sch, plc = D.EXPO_VENUE.get(nm) or (None, None)
    if not sch:  # 일정 미확인(장소만 확인된 단지 포함)
        sg = D.R500_SIGNED.get(nm)
        return (((f'<span style="color:#555">협약 {sg}</span> ' if sg else ""))
                + todo(getattr(D, "EXPO_ASK", {}).get(nm, "일정 확인")),
                e(plc) if plc else todo("장소 확인"))
    return e(sch).replace("\n", "<br>"), e(plc)  # 구분(입주박람회 · 공동구매)은 열 제목에 한 번


def doc09_form():
    # 본부장 10-19: 20개 단지 한 목록 · 입주 순 — 모두 당사 주관
    rs = sorted(D.RECENT3_500, key=lambda r: r[0])
    rows = ""
    for m, nm, n, j in rs:
        sch, plc = _expo(nm)
        assert j, nm
        tag = ""
        rows += f'<tr><td>{e(nm)} <span style="color:#555">({m})</span>{tag}</td><td class="c">{n:,}</td><td class="c" style="font-size:8.6pt">{sch}</td><td class="c">{plc}</td></tr>'
    tot = sum(r[2] for r in rs)
    yy, mm, dd = ymd()
    body = f"""<style>.b2 th,.b2 td{{padding:1.6pt 5pt!important;font-size:8.8pt!important;line-height:1.28!important}}</style>
<div class="form"><div class="no">[별지 서식 제2호]</div><h1 style="letter-spacing:.12em;margin:6pt 0 10pt">최근 3년간 주관사 실적 총괄표</h1>
<table class="ft r2 b2"><thead><tr><th>아파트명 (입주일)</th><th style="width:10%">세대수</th><th style="width:37%">박람회 일정<br><span style="font-weight:400;font-size:8pt">(구분: 입주박람회 · 공동구매)</span></th><th style="width:19%">행사 장소</th></tr></thead>
<tbody>{rows}<tr><th>합계 {len(rs)}개 단지</th><th>{tot:,}</th><th colspan="2"></th></tr></tbody></table>
<div style="font-size:8.8pt;color:#444;margin-top:4pt;line-height:1.5">※ 세대수가 500세대 이상인 아파트 기준으로 작성<br>
※ 박람회 일정에는 공동구매, 입주박람회 등 구분 기재<br>
※ 20개 단지 모두 당사 주관 · 입주 연월 순<br>
※ 증빙할 수 있는 협약서 또는 수임 실적 증명서 등 스캔본 별도 추가 제출 — 다음 쪽 ‘실적 증빙 안내’ · 별첨 1 ~ 4</div>
<p class="tx" style="text-align:center;text-indent:0;margin-top:8pt">이상 사실과 다름이 없습니다.</p>
<div class="dt" style="margin-top:4pt">{yy}년 &nbsp; {mm}월 &nbsp; {dd}일</div>
<div class="sg" style="margin-top:4pt;line-height:2.2">주관사 : <b>{D.COMPANY}</b><br>대표자 : <b>대표이사 {D.CEO}</b><span style="margin-left:40pt">(인)</span></div>
<div class="to2" style="margin-top:10pt">{FORM_TO} 귀하</div></div>"""
    return doc("09 최근 3년간 주관사 실적 총괄표", [body])


EV_OF = {  # 1,000세대 이상 주관 중 NICE 연혁 밖 2개 단지의 증빙
    "e편한세상 송도 더퍼스트비치": "BEXCO 공식 행사일정(별첨 2 붙임 3)",
    "에코델타 대성베르힐": "입주자 모임 카페 주관사 공지(별첨 2 붙임 2)",
}


def doc09_cover():
    r5 = D.RECENT3_500
    nice_names = {r[1] for r in D.RECENT3}
    big = {r[1] for r in D.RECENT3_OS}
    have = list(D.R500_HAVE)
    grp = [(None, None, sorted(r5, key=lambda r: r[0]))]  # 본부장 10-19: 한 목록 · 입주 순
    rows, i, n_ev = "", 0, 0
    bx = {c[0]: k for k, c in enumerate(D.EXPO_CAPS, 1)}
    src = {c[0]: ("UECO 공식 행사일정" if "UECO" in c[2] else "CECO 공식 행사일정" if "CECO" in c[2] else "입주자 공식 카페 공지" if "카페" in c[2] else "BEXCO 공식 행사일정") for c in D.EXPO_CAPS}
    for gno, gname, rs in grp:
        for m, nm, n, j in rs:
            i += 1
            if j and nm in big:
                ev = EV_OF.get(nm) or ("NICE 연혁(별첨 1) · 실적 확약서(별첨 2)" if nm in nice_names else None)
                assert ev, f"주관 단지 증빙 없음: {nm}"
            elif j and nm in D.R500_HAVE:
                ev = f"주관사 협약서(별첨 3-{sorted(have, key=lambda k: D.R500_SIGNED[k]).index(nm) + 1} · 협약 {D.R500_SIGNED[nm]})"
            elif j and nm in bx:
                ev = f"{src[nm].split('(입주민')[0]}(별첨 4-{bx[nm]})"
            elif j:
                assert nm in D.JUGWAN_ADD, nm
                ev = "요청 시 제출(박람회 일정 · 장소는 별지 2)"
            else:
                ev = "요청 시 제출"
            if j and nm in bx and "별첨 4" not in ev:
                ev += f" · {src[nm].split(' ')[0]}(별첨 4-{bx[nm]})"
            n_ev += 1 if j and not ev.startswith("요청") else 0
            rows += (f'<tr class="{"jg" if j else ""}"><td>{i}</td><td>{m}</td><td class="l">{e(nm)}</td><td class="r">{n:,}</td>'
                     f'<td class="g">주관</td><td class="l">{ev}</td></tr>')
    tot = sum(r[2] for r in r5)
    nj, hj = sum(1 for r in r5 if r[3]), sum(r[2] for r in r5 if r[3])
    body = f"""{head("제출서류 9", "최근 3년간 주관 실적 — 실적 증빙 안내")}
<p class="note" style="margin-top:4pt">기준: 공고 입찰 참가자격 ‘최근 3년 이내 500세대 이상 공동주택 입주박람회 주관 또는 운영실적’ · 입주 연월 2023.10 ~ 2026.12(2027년 입주 예정 단지 제외) · 단지명 · 세대수는 당사 실적 목록 기준.</p>
<style>.t.ls.r9 td{{padding:.5pt 5pt;font-size:8.5pt;line-height:1.3}}.t.ls.r9 th{{font-size:8.8pt}}.pl li.sm{{font-size:8.6pt!important;margin:0!important}}.t.ls.r9 tr.gh td{{padding:1.5pt 6pt}}h1{{font-size:16.5pt!important;margin-top:8pt!important}}.box{{margin-top:6pt!important;padding:5pt 10pt!important;font-size:9.3pt!important}}</style>
<table class="t ls r9" style="margin-top:6pt"><thead><tr><th style="width:5%">No</th><th style="width:10%">입주</th><th>단지명</th><th style="width:10%">세대수</th><th style="width:7%">구분</th><th style="width:36%">증빙</th></tr></thead>
<tbody>{rows}
<tr class="sum"><td colspan="3">합계 {len(r5)}개 단지 (모두 주관)</td><td class="r">{tot:,}</td><td></td><td></td></tr></tbody></table>
<div class="box"><b>참가자격 대비</b> &nbsp; 최근 3년 500세대 이상 주관 또는 운영 실적 &nbsp;→&nbsp; <b>주관 {nj}개 단지(증빙 첨부 {n_ev}개 단지) · 충족</b> (전체 {len(r5)}개 단지 · {tot:,}세대)<br>
‘주관’ = 당사가 주관사로 수행 — 1,000세대 이상 {len(big)}개 단지 + 주관사 협약서 {len(have)}개 단지 + 500 ~ 999세대 {len(D.JUGWAN_ADD)}개 단지</div>
<ol class="pl" style="margin-top:3pt"><li class="sm">별첨 1. NICE디앤비 기업신용평가보고서 ‘연혁’ 발췌 — 1쪽(보고서 전문은 제출서류 15)</li>
<li class="sm">별첨 2. 실적 확약서(1,000세대 이상 입주박람회 주관 10개 단지 · 최근 3년 8 + 2023.10 이전 2) — 붙임 1 · 2 단지 카페 주관사 공지 캡처(입주민 닉네임 가림) · 붙임 3 BEXCO 공식 행사일정 캡처</li>
<li class="sm">별첨 3. 500세대 이상 주관사 협약서 — {" · ".join(f"3-{k + 1} {e(nm)}" for k, nm in enumerate(sorted(have, key=lambda k: D.R500_SIGNED[k])))} — 협약일 순(상대방 대표자 성명 · 서명 가림, 3-2 특약 금액 가림)</li>
<li class="sm">별첨 4. {CAP_TITLE()}(주최/주관란에 엣지컴퍼니 기재) — {len(D.EXPO_CAPS)}곳 · 표의 ‘별첨 4-n’</li>
</ol>
<p class="note">※ 증빙 미첨부 단지(‘요청 시 제출’)는 요청 시 계약서 · 정산 자료를 지체 없이 추가 제출합니다. 주관 시기(NICE 연혁)와 입주 연월은 다를 수 있습니다.</p>
<p class="body" style="font-size:9.6pt;margin-top:2pt;line-height:1.6">위 실적은 사실과 다름이 없음을 확인하며, 허위로 확인될 경우 공고 ‘입찰 참가 제한’(제출서류 · 제안내용의 허위사실)에 따른 어떠한 조치도 이의 없이 따르겠습니다.</p>{sign().replace('class="sign"', 'class="sign" style="margin-top:2pt"').replace('class="to"', 'class="to" style="margin-top:4pt"')}"""
    return doc("09 실적 증빙 안내", [body])


# 별첨 1 — NICE 원본 9쪽 연혁 발췌(오산 docs_os.annex12_nice와 같은 방식 · 고양 표기)
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
    text(R, 51.5, "제출서류 9 최근 3년간 주관사 실적 총괄표 · 증빙", 8.5, "r", GRAY, "r")
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
            ("원본 분량", f"전 {len(nice)}쪽 (전문은 제출서류 15)")]
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


# 별첨 2 — 실적 확약서: 탕정 hwakyak.py의 실적 · 캡처 목록을 읽기만 한다(오산과 같은 방식)
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
    assert any("입주민 카페" in r[4] for r in recs), "사상 근거 표기 — 탕정 hwakyak.py RECS 문구가 바뀜"
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
<p class="body">당사는 「{e(D.NOTICE)}」의 입찰 참가자격(주관 · 운영 실적)과 관련하여, 1,000세대 이상 공동주택 단지의 입주박람회 주관 실적을 아래와 같이 제출하며 기재 내용이 사실임을 확약합니다.</p>
<table class="t"><tr><th>연번</th><th>주관 시기</th><th>단지명</th><th>지역</th><th>세대수</th><th>근거</th></tr>{rows}
<tr class="sum"><td colspan="4">합계 {len(recs)}개 단지</td><td class="r">{tot:,}</td><td></td></tr></table>
<div class="note">※ 근거: NICE 기업신용평가보고서(평가일 {D.NICE_DATE}) '연혁'(별첨 1 · 원본 9쪽) · 단지 카페(입주민 · 입주자 모임 카페)의 주관사 명의 공지 · BEXCO 공식 행사일정(붙임). 세대수는 NICE 연혁 기재값(카페 공지 · BEXCO 근거 3개 단지는 단지 공식 총세대수). 최근 3년 밖(2023.10 이전) 2개 단지를 포함한 전체 주관 실적입니다.</div>
<ol><li>위 실적은 당사가 입주박람회 주관사로서 직접 수행한 것입니다.</li>
<li>귀 협의회가 요청하면 계약서, 실적 확인서, 정산 자료 등 증빙을 지체 없이 제출하겠습니다.</li>
<li>기재 내용이 사실과 다른 것으로 밝혀지면 공고 ‘입찰 참가 제한’에 따른 모든 조치를 이의 없이 받아들이겠습니다.</li></ol>
<div class="sign"><div class="d">{yy}년 &nbsp;{mm}월 &nbsp;{dd}일</div>
{D.COMPANY}<br><b>대표이사 &nbsp;{" ".join(D.CEO)}</b><span style="margin-left:48pt">(인)</span></div>
<div class="to">{FORM_TO} 귀하</div></section>"""
    caps = ""
    for f, title, url, what, boxes in hw.CAPS:
        kind = ("전시장 공식 행사일정 캡처" if f.startswith("bexco") else
                "입주민 소통 카페 주관사 게시판 캡처" if f.startswith("sasang") else "입주자 모임 카페 주관사 공지 캡처")
        caps += (f'<section class="pg"><h2>실적 확약서 붙임 · {kind}</h2><div class="cap"><h3>{e(title)}</h3>'
                 f'<div class="u">{e(url)}{" · 입주민 닉네임(동·호수)은 개인정보 보호를 위해 가림" if boxes else ""}</div><div class="k">{e(what)}</div>'
                 f'<img src="../assets_ins/cafe_{f}"></div></section>')  # HTML은 작업/ 아래
    return f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>실적 확약서</title><style>{hw.CSS}{HW_FIT}</style></head><body>{p1}{caps}</body></html>'


def CAP_SRC():
    k = []
    if any(c[2].startswith("BEXCO") for c in D.EXPO_CAPS): k.append("벡스코(BEXCO) 홈페이지 ‘행사일정’ 상세 화면")
    if any("UECO" in c[2] for c in D.EXPO_CAPS): k.append("울산전시컨벤션센터(UECO) 홈페이지 ‘전체일정’ 화면")
    if any("CECO" in c[2] for c in D.EXPO_CAPS): k.append("창원컨벤션센터(CECO) 홈페이지 ‘전체일정’ 화면")
    if any("카페" in c[2] for c in D.EXPO_CAPS): k.append("단지 입주자 공식 카페 ‘엣지컴퍼니 공지사항’ 게시판")
    return " · ".join(k)


def CAP_TITLE():
    return "BEXCO 공식 행사일정 캡처" if all(c[2].startswith("BEXCO") for c in D.EXPO_CAPS) else "박람회장 공식 행사일정 · 카페 공지 캡처"


def doc09_bexco():  # 별첨 4 — 한 장에 2 ~ 3곳(본부장 10-19: 서류 수를 늘리지 않게 묶음 · 안 되면 나눔)
    from PIL import Image
    caps = []
    for k, (nm, f, kind, per, hall) in enumerate(D.EXPO_CAPS, 1):
        w, h = Image.open(os.path.join(HERE, "assets_ins", f)).size
        caps.append((k, nm, f, kind, per, hall, 2 if h > w else 1))  # 세로 캡처 = 2칸
    tot_w = sum(c[-1] for c in caps)
    npg = max(1, -(-tot_w // 3))
    pages, cur, cw, left = [], [], 0, tot_w
    for c in caps:
        tgt = -(-left // (npg - len(pages))) if npg > len(pages) else 3
        if cur and cw + c[-1] > tgt:
            pages.append(cur); left -= cw; cur, cw = [], 0
            tgt = -(-left // max(1, npg - len(pages)))
        cur.append(c); cw += c[-1]
    if cur: pages.append(cur)
    secs = []
    for pi, cs in enumerate(pages):
        items = "".join(
            f'<div class="bxc{" tall" if wt == 2 else ""}"><div class="bh"><b>4-{k}</b> {e(nm)} <span>· {e(kind)} · {e(per)} · {e(hall)}</span></div>'
            f'<img src="../assets_ins/{f}" alt=""></div>' for k, nm, f, kind, per, hall, wt in cs)
        secs.append(head("제출서류 9 · 별첨 4", f"{CAP_TITLE()} ({pi + 1}/{len(pages)})")
                    + f'<p class="note" style="margin-top:4pt">출처: {CAP_SRC()} · 주최 · 주관란 = 주식회사 엣지컴퍼니 · 화면 그대로{"(입주민 닉네임만 가림)" if any("카페" in c[2] for c in D.EXPO_CAPS) else "(가공 없음)"}</p>'
                    + f'<div class="bxs">{items}</div>')
    css = CSS + (".bxs{display:flex;flex-direction:column;gap:7pt;margin-top:6pt}.bxc{border:1px solid #c9ced6;border-radius:3pt;padding:5pt 6pt}"
                 ".bh{font-size:10pt;margin-bottom:4pt}.bh b{color:#9A7B3F;margin-right:4pt}.bh span{color:#555;font-size:9pt}"
                 ".bxc img{display:block;width:100%;max-height:58mm;object-fit:contain;object-position:left top}.bxc.tall img{max-height:130mm}")
    return doc("09 별첨 4 박람회 공식 행사일정 · 카페 공지", secs, css), len(pages)


# ================================================================== 10 하자 보수 이행 각서 [별지 3호]
def doc10():
    yy, mm, dd = ymd()
    body = f"""<div class="form"><div class="no">[별지 서식 제3호]</div><h1>하자 보수 이행 각서</h1>
<table class="ft">
<tr><th style="width:20%">업 체 명</th><td>{D.COMPANY}</td><th style="width:16%">직 &nbsp; 위</th><td>대표이사</td></tr>
<tr><th>성 &nbsp; &nbsp; 명</th><td>{D.CEO}</td><th>생년월일</th><td>{birth(CEO_BIRTH, "대표자")}</td></tr>
<tr><th>본 사 주 소</th><td colspan="3">{D.ADDRESS}</td></tr></table>
<p class="tx" style="margin-top:24pt">{FORM_TO}(이하 ‘입예협’)에서 시행하는 공동구매 행사로 인해 발생하는 사후 하자 보수를 이행함에 있어 계약(또는 협약) 일반조건에 따라 하자 보증기간 내에 주관한 행사에 참여한 업체가 납품한 공사 및 물품에 대해 하자가 발생할 시에는 즉시 실제 발생한 하자 보수 또는 원상 복귀에 대한 상당 금액을 변상할 것을 서약합니다.</p>
<div class="dt" style="margin-top:40pt">{yy}년 &nbsp; {mm}월 &nbsp; {dd}일</div>
<div class="sg" style="margin-top:26pt">주관사 : <b>{D.COMPANY}</b><br>대표자 : <b>대표이사 {D.CEO}</b><span style="margin-left:48pt">(인)</span></div>
<div class="to2" style="margin-top:70pt">{FORM_TO} 귀하</div></div>"""
    return doc("10 하자 보수 이행 각서", [body])


# ================================================================== 11 청렴계약 이행 준수 서약서 [별지 4호]
def doc11():
    items = [
        "유리한 입찰가격 또는 특정인의 낙찰을 위한 담합을 하거나 다른 업체와 협정, 결의, 합의하여 입찰의 자유경쟁을 부당하게 저해하는 일체의 불공정한 행위를 하지 않겠습니다.",
        "입찰, 계약 체결 및 계약 이행 과정에서 관계직원에게 직‧간접적으로 금품‧향응 등의 뇌물이나 부당한 이익을 제공하지 않겠습니다.",
        "입찰, 계약 체결 및 계약 이행과 관련하여 관계 직원에게 뇌물을 제공한 사실이 드러날 경우에는, 계약 체결 이전의 경우에는 낙찰자 결정 취소, 행사 개최 전에는 계약 취소, 행사 개최 이후에는 협의회에서 전체 또는 일부 계약을 해지하여도 감수하며 민‧형사상 일체 이의를 제기하지 않겠습니다.",
        "공동구매 및 입주 박람회 관련 하도급 계약 체결 및 이행에 있어서 하도급자로부터 금품을 수수하거나 부당 또는 불공정한 행위를 하지 아니하겠습니다.",
        "관계법령과 규정에 저해되는 일체의 불공정한 행위는 물론, 어떠한 압력이나 청탁도 행사하지 않겠습니다.",
        "입예협 운영위원과 회원들에게 직･간접적으로 금품이나 선물, 향응이나 접대 등을 제공하지 않겠습니다.",
    ]
    body = f"""<div class="form" style="font-size:10.6pt;line-height:1.75"><div class="no">[별지 서식 제4호]</div><h1 style="margin:8pt 0 10pt">청렴계약 이행 준수 서약서</h1>
<p class="tx" style="margin-top:0">{FORM_TO} 주관사 선정 입찰에 참여한 당 업체는 「부패 없는 투명한 기업 경영과 공정한 사회」 취지에 적극 호응하여 {FORM_TO}에서 시행하는 『주관사 선정』에 참여함에 있어 당사 임직원과 대리인은</p>
<ol>{"".join(f"<li>{i}. {x}</li>" for i, x in enumerate(items, 1))}</ol>
<p class="tx">위 청렴계약 이행 서약은 상호 신뢰를 바탕으로 한 약속으로써 반드시 지킬 것이며, 이를 위반할 경우 입찰 참가 자격 제한, 협약 해지 또는 해제 등 {FORM_TO}의 조치에 대해 손해배상을 청구하거나 민･형사상 어떠한 이의도 제기하지 않을 것을 서약합니다</p>
{seal_tail().replace('class="sgx"', 'class="sgx" style="margin-top:12pt"').replace('class="dt"', 'class="dt" style="margin-top:12pt"').replace('class="to2"', 'class="to2" style="margin-top:16pt"')}</div>"""
    return doc("11 청렴계약 이행 준수 서약서", [body])


# ================================================================== 14 서약서(이의 제기 금지) [별지 5호]
def doc14():
    items = [
        "위 입찰에 참여한 당 업체는 창릉신도시 S5 입예협의 협약자 선정 방식 및 공고문 내용과 본 입찰에 관련된 창릉신도시 S5 입예협의 방침에 이의가 없음을 확약하며, 공정한 심사와 객관적인 내부 절차에 의한 입찰 진행상의 제반 결정에 어떠한 이의를 제기하지 않고 수락할 것을 확약합니다.",
        "창릉신도시 S5 입예협이 평가를 위해 구성한 평가 위원과 평가 방법 및 평가 기준에 따른 결과에 대해서도 어떠한 이의를 제기하지 않겠으며, 사업자 선정전까지도 창릉신도시 S5 입예협의 추가 요청 내용과 계약 체결에 따른 증빙 서류 제출 등 제반 유의사항을 준수할 것을 확약합니다.",
        "주관사로 선정될 경우, 사업 전체를 타인(타사)에게 일괄 도급하지 않으며, 계약 이후라도 일괄 도급한 사실이 적발될 경우, 계약이 해지되어도 민사 소송 등 이의를 일절 제기하지 않겠습니다.",
        "주관사 미선정 시 창릉신도시 S5에 대한 별도의 입주 박람회 주관 및 공동구매 등 행사 개최를 일절 하지 않을 것을 서약합니다.",
    ]
    body = f"""<div class="form"><div class="no">[별지 서식 제5호]</div><h1 style="letter-spacing:.5em">서 약 서</h1>
<p style="font-size:11.5pt;margin:0 0 6pt">입 찰 명 : 창릉신도시 S5 주관사 입찰 선정</p>
<ol>{"".join(f"<li>{i}. {x}</li>" for i, x in enumerate(items, 1))}</ol>
{seal_tail().replace('class="sgx"', 'class="sgx" style="margin-top:26pt"')}</div>"""
    return doc("14 서약서", [body])


# ================================================================== 15 신용평가서 상세내역 — 표지 + NICE 전문(대표 외 임직원 생년월일 가림)
NICE_MASK = {12: [(170, 148.5, 228, 163.5), (170, 166.5, 228, 181.5)]}  # 원본 13쪽 '주요 경영진' 생년월일 칸 — 대표 외 임직원 2명


def doc15_cover(n_pages):
    body = f"""{head("제출서류 15", "신용평가서 상세내역")}
<table class="t" style="margin-top:14pt"><tbody>
<tr><td class="k" style="width:22%">보고서</td><td class="l">NICE디앤비 CLIP 기업신용평가보고서(관리번호 11125949-202605-001) — <b>전문 {n_pages}쪽</b></td></tr>
<tr><td class="k">평가 대상</td><td class="l">{D.COMPANY} ({D.BIZ_NO})</td></tr>
<tr><td class="k">평가일 · 유효기간</td><td class="l">{D.NICE_DATE} · ~2027.06.18 — 당사의 가장 최근 평가</td></tr>
<tr><td class="k">결과</td><td class="l">신용등급 BB- · 현금흐름등급 A</td></tr>
<tr><td class="k">구성</td><td class="l">기업신용평가 요약 · Summary · 재무분석 · 영업 현황(기업개요 · 연혁 · 사업장 · 인증) · 경영진 현황 · 금융정보 · 재무제표 · 신용등급 정의</td></tr>
<tr><td class="k">개인정보</td><td class="l">원본 13쪽 ‘경영진 현황’의 대표 외 임직원 2명 생년월일은 개인정보 보호를 위해 가렸습니다(그 밖의 내용은 원본 그대로).</td></tr>
</tbody></table>
<p class="note" style="margin-top:8pt">※ 보고서의 본사 주소는 본점 이전(2026.07.02 등기) 전 주소이고, 종업원 수와 경영진 현황은 평가 당시(2026.05) 기준입니다. 주관사업 총괄 본부장({D.MANAGER[0]})은 평가 이후 합류했습니다. 현재 본점 · 등기 사항은 제출서류 2 · 3과 같고, 현재 조직은 제출서류 16과 같습니다.</p>
<p class="note">※ 실적 근거인 연혁(원본 9쪽)은 제출서류 9 별첨 1에도 발췌해 붙였습니다.</p>"""
    return doc("15 신용평가서 상세내역", [body])


def nice_full(nice_path):
    d = fitz.open(nice_path)
    assert len(d) == 24, f"NICE 보고서 {len(d)}쪽 — 가림 좌표 다시 확인"
    for i, rects in NICE_MASK.items():
        pg = d[i]
        assert any(x["width"] == 2477 and x["height"] == 3502 for x in pg.get_image_info()), "NICE 13쪽 이미지가 다름 — 가림 좌표 다시 확인"
        for r in rects:
            pg.add_redact_annot(fitz.Rect(*r), fill=(0.82, 0.82, 0.82))
        pg.apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS)
    p = out("15_2_NICE_전문_가림.pdf")
    d.save(p, garbage=GARBAGE, deflate=True)
    return p


# ================================================================== 16 사업장 및 조직현황
BIZ_TYPES = "건설업(전기공사) · 도매 및 소매업(조명자재 · 전기자재 / 전자상거래소매업) · 서비스업(부동산분양 · 광고대행업 / 전시 · 박람회 및 행사대행업)"


def doc16():
    n_in = D.STAFF_LEAD + sum(c for _, c, _ in D.STAFF)
    tms = "".join(f'<div class="tm"><b>{e(n)}<em>{c}명</em></b><small>{e(r)}</small></div>' for n, c, r in D.STAFF)
    rows = [("대표이사", 1, "경영 총괄 · 주관 박람회 현장 점검 · 진두지휘"),
            ("주관사업 총괄 본부장", 1, "입찰 · 협약 · 주관 업무 총괄(본 건 책임자 · PT 참석)")] + [(n, c, r) for n, c, r in D.STAFF]
    tb = "".join(f'<tr><td class="k">{e(a)}</td><td>{b}명</td><td class="l">{e(c)}</td></tr>' for a, b, c in rows)
    ext = " · ".join(a for a, _ in D.STAFF_EXT)
    body = f"""{head("제출서류 16", "사업장 및 조직현황")}
<h2>1. 사업장 현황</h2>
<table class="t"><tbody>
<tr><td class="k" style="width:19%">상호 · 대표자</td><td class="l">{D.COMPANY} · 대표이사 {D.CEO}</td></tr>
<tr><td class="k">사업자 · 법인 번호</td><td class="l">사업자등록번호 {D.BIZ_NO} · 법인등록번호 {D.CORP_NO}</td></tr>
<tr><td class="k">설립(개업)</td><td class="l">{D.FOUNDED} · 자본금 2억원(2026.04 증자 · 등기부)</td></tr>
<tr><td class="k">본사 · 쇼룸</td><td class="l">{D.ADDRESS} (본점 = 사업장 · 2층 · 3층 임차 · 시설면적 328.86㎡ — 영업배상책임보험 증권 기재)</td></tr>
<tr><td class="k">업태 · 종목</td><td class="l">{BIZ_TYPES} — 사업자등록증 기재</td></tr>
<tr><td class="k">면허 · 인증</td><td class="l">{D.ELEC_LICENSE}(2022.05) · ISO 9001 · 14001 · 45001(2025.08 · 박람회 기획 · 대행, 전기 · 조명공사)</td></tr>
<tr><td class="k">신용 · 보험</td><td class="l">NICE디앤비 BB- · 현금흐름 A(평가 {D.NICE_DATE} · 제출서류 15) · KB손해보험 영업배상책임보험(2026.10.14 ~ 2027.10.14 · 제출서류 12)</td></tr>
<tr><td class="k">연락처</td><td class="l">대표전화 {D.TEL} · {D.EMAIL} · 책임자 {D.MANAGER[1]} {D.MANAGER[0]} {D.MANAGER[2]}</td></tr>
</tbody></table>
<h2>2. 조직 현황 — 임직원 {n_in}명(정규직 13 + 인턴 1 · 4대보험 가입 13명 · 2026.10.23 명부 · 붙임)</h2>
<div class="oc"><div class="ceo"><i>㈜엣지컴퍼니</i><b>CEO</b><span>대표이사</span></div>
<div class="gmr"><div class="gm"><em>주관사업</em><b>총괄 본부장</b></div></div>
<div class="bar"></div><div class="tms">{tms}</div></div>
<table class="t" style="margin-top:8pt"><thead><tr><th style="width:24%">구분</th><th style="width:9%">인원</th><th>담당 업무</th></tr></thead><tbody>{tb}
<tr class="sum"><td>합계</td><td>{n_in}명</td><td class="l">팀 · 인원 · 역할은 협약 시 명단으로 확정</td></tr></tbody></table>
<p class="note">분야별 외부 전문 협력: {e(ext)} — 자문 · 촬영 등 전문 업무이며 사업 전체를 일괄 도급하지 않습니다(별지 5).</p>
<h2>3. {SITE} 전담 배치 (안)</h2>
<table class="t"><tbody>
<tr><td class="k" style="width:19%">책임자</td><td class="l">{D.MANAGER[1]} {D.MANAGER[0]} — 협의회 소통 · PT 참석(발표 · 질의) · 협약 이행 총괄(공고: PT에는 실제 업무 책임자 참석)</td></tr>
<tr><td class="k">전담 PM</td><td class="l">단지 전담 PM 1명 지정 — 성명 · 연락처는 협약 시 제출</td></tr>
<tr><td class="k">박람회 현장</td><td class="l">현장 운영 인력 약 21명(행사 규모별 변동 · 안내 · 보안 등 외부 인력 포함) + 주관사 운영팀 상주</td></tr>
<tr><td class="k">민원 · A/S 창구</td><td class="l">주관 콜센터 {D.TEL}(평일 09:00 ~ 18:00) · 카페 신문고 · 카카오채널 · 홈페이지 365일 접수 — 입주 후 1년 운영</td></tr>
</tbody></table>
<p class="note">※ NICE 보고서(제출서류 15)의 종업원 수 · 경영진은 평가 당시(2026.05) 기준이며, 현재 조직은 위와 같습니다. 붙임: 4대보험 사업장 가입자 명부(2026.10.23 발급 · 13명 · 성명 가운데 글자 · 주민등록번호 뒷자리 가림).</p>
{sign().replace('class="sign"', 'class="sign" style="margin-top:8pt"').replace('class="to"', 'class="to" style="margin-top:8pt"')}"""
    return doc("16 사업장 및 조직현황", [body])


# ------------------------------------------------------------------ PDF · 날인 · 병합(오산 docs_os.py와 같은 방식)
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


ORDER = ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "09-2", "10", "11", "12", "14", "15", "16", "17"]
NAMES = {  # 제출본 파일 · ZIP 폴더 이름(별지 6 번호 · 서류명)
    "00": "00_서류제출목록표", "01": "01_입찰참가신청서", "02": "02_사업자등록증", "03": "03_법인등기부등본",
    "04": "04_지방세_완납증명서", "05": "05_국세_완납증명서", "06": "06_법인인감증명서", "07": "07_대표이사_범죄사실증명서_결격사유서약서", "08": "08_주관사_제안서",
    "09": "09_최근3년_주관사실적_총괄표_증빙", "09-2": "09-2_4대보험_완납증명서", "10": "10_하자보수_이행각서",
    "11": "11_청렴계약_이행준수_서약서", "12": "12_영업배상책임보험_증서", "14": "14_이의제기_금지_서약서",
    "15": "15_신용평가서_상세내역", "16": "16_사업장_및_조직현황", "17": "17_기타_요약제안서",
}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    final = "--final" in sys.argv
    if not args:
        sys.exit(__doc__)
    seal_path = args[0]
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

    res = {}
    # 본부장 10-22: '반드시 업체 인감 날인' 서식(별지 1 · 4 · 5) = 실물 법인인감 날인 스캔 3쪽(순서 1 · 4 · 5)이 있으면 그 쪽으로 바꾼다 · 나머지는 직인
    GY_SCAN = getattr(D, "SEAL_SCAN", None) or f"{SP}/seal_scan/고양_별지1_4_5_법인인감.pdf"

    def scanned(i, name, fallback):
        if not os.path.exists(GY_SCAN):
            return fallback()
        sc = fitz.open(GY_SCAN)
        assert len(sc) == 3, f"고양 법인인감 스캔은 3쪽(별지 1 · 4 · 5)이어야 함: {GY_SCAN}"
        o = fitz.open()
        o.insert_pdf(sc, from_page=i, to_page=i)
        p = out(name + "_법인인감.pdf")
        o.save(p, garbage=GARBAGE, deflate=True)
        return p
    nice15 = nice_full(NICE_SRC)
    n = {"08": len(fitz.open(P08)), "15n": len(fitz.open(nice15))}
    res["00"] = fit(render("00_서류제출목록표", doc00(n)), 1)
    res["01"] = scanned(0, "01_입찰참가신청서", lambda: stamped(fit(render("01_입찰참가신청서", doc01()), 1)))
    biz = fitz.open(f"{EV}/사업자등록증.pdf")
    for pg_ in biz:
        for a in list(pg_.annots()):  # 발급 뒤 덧붙인 스탬프 주석이 원본 칸을 가리지 않게
            pg_.delete_annot(a)
    res["02"] = merge(NAMES["02"], [biz], "2 사업자등록증")
    res["03"] = merge(NAMES["03"], [f"{EV}/법인등기부등본.pdf"], "3 법인등기부등본")
    res["04"] = merge(NAMES["04"], [f"{EV}/지방세_납세증명서.pdf"], "4 지방세 완납 증명서")
    res["05"] = merge(NAMES["05"], [f"{EV}/국세_납세증명서.pdf"], "5 국세 완납 증명서")
    res["06"] = merge(NAMES["06"], [f"{EV}/법인인감증명서.pdf"], "6 법인인감증명서")
    res["07"] = stamped(fit(render("07_대표이사_범죄사실증명서_결격사유서약서", doc07()), 2))
    res["08"] = out(NAMES["08"] + ".pdf")
    shutil.copyfile(P08, res["08"])
    a1 = stamped(annex_nice(NICE_SRC, out("09_3_별첨1_NICE연혁발췌.pdf")))
    _b4 = doc09_bexco()
    parts9 = [stamped(fit(render("09_1_별지2_실적총괄표", doc09_form()), 1)), stamped(fit(render("09_2_실적증빙_안내", doc09_cover()), 1)), a1,
              stamped(fit(render("09_4_별첨2_실적확약서", doc09_hwakyak()), 4)), D.R500_DOC, fit(render("09_5_별첨4_BEXCO", _b4[0]), _b4[1])]
    names9 = ["[별지 2호] 최근 3년간 주관사 실적 총괄표", f"실적 증빙 안내(주관 {sum(1 for r in D.RECENT3_500 if r[3])}개 단지 · 증빙 첨부 {D._EV_N})", "별첨 1 NICE 연혁 발췌",
              "별첨 2 실적 확약서 · 붙임 1 ~ 3", f"별첨 3 주관사 협약서 {len(D.R500_HAVE)}건(협약일 순)", f"별첨 4 {CAP_TITLE()} {len(D.EXPO_CAPS)}곳"]
    toc, pg0 = [], 1
    for nm, p in zip(names9, parts9):
        toc.append([1, nm, pg0])
        pg0 += len(fitz.open(p))
    res["09"] = merge(NAMES["09"], parts9, "9 최근 3년간 주관사 실적 총괄표 · 증빙", toc)
    res["09-2"] = merge(NAMES["09-2"], [f"{EV}/4대보험_완납증명서.pdf", f"{EV}/고용산재_완납증명서.pdf"], "9 4대 보험 완납증명서")
    res["10"] = stamped(fit(render("10_하자보수_이행각서", doc10()), 1))
    res["11"] = scanned(1, "11_청렴계약_이행준수_서약서", lambda: stamped(fit(render("11_청렴계약_이행준수_서약서", doc11()), 1)))
    res["12"] = merge(NAMES["12"], [KB], "12 영업배상책임보험 증서")
    res["14"] = scanned(2, "14_이의제기_금지_서약서", lambda: stamped(fit(render("14_이의제기_금지_서약서", doc14()), 1)))
    res["15"] = merge(NAMES["15"], [fit(render("15_1_표지", doc15_cover(n["15n"])), 1), nice15], "15 신용평가서 상세내역(NICE 전문)",
                      [[1, "표지", 1], [1, "NICE디앤비 CLIP 기업신용평가보고서 전문", 2]])
    # 본부장 10-23: 4대보험 사업장 가입자 명부(2026.10.23 · 13명 · 가림본)를 16에 붙임 — 조직현황 인원의 증빙
    s16 = stamped(fit(render("16_사업장_및_조직현황", doc16()), 1, 2))
    s16d = fitz.open(stream=open(s16, "rb").read(), filetype="pdf")
    assert len(fitz.open(ROSTER)) == 2, "4대보험 가입자 명부(2026.10.23 · 가림본) 2쪽 확인 실패"
    res["16"] = merge(NAMES["16"], [s16d, ROSTER], "16 사업장 및 조직현황 · 붙임 4대보험 가입자 명부",
                      [[1, "사업장 및 조직현황", 1], [1, "붙임 · 4대보험 사업장 가입자 명부(2026.10.23)", len(s16d) + 1]])
    if ok["17"]:
        res["17"] = out(NAMES["17"] + ".pdf")
        shutil.copyfile(P17, res["17"])

    # ---- 서식 날인용 출력본(본부장 10-19): 직인 찍기 전 서식만 한 파일로 — 출력 → 실물 인감 날인 → 스캔
    PRINT_SRC = ["01_입찰참가신청서", "07_대표이사_범죄사실증명서_결격사유서약서", "09_1_별지2_실적총괄표", "09_2_실적증빙_안내",
                 "09_3_별첨1_NICE연혁발췌", "09_4_별첨2_실적확약서", "10_하자보수_이행각서", "11_청렴계약_이행준수_서약서",
                 "14_이의제기_금지_서약서", "16_사업장_및_조직현황"]
    pr, toc, pg0 = fitz.open(), [], 1
    for nm in PRINT_SRC:
        d_ = fitz.open(out(nm + ".pdf"))
        toc.append([1, nm, pg0]); pg0 += len(d_); pr.insert_pdf(d_)
    pr.set_toc(toc); pr.set_metadata({"title": "서식 날인용 출력본(직인 전)", "author": D.COMPANY})
    pr.save(out("서식날인_출력용.pdf"), garbage=GARBAGE, deflate=True)
    print(f"[출력용] {PFX}서식날인_출력용.pdf {len(pr)}쪽 — '(인)' 자리에 실물 인감 날인 후 스캔")

    # ---- 제출본/: 조치 끝난 서류만(지난 실행 파일은 지우고 다시) · 08은 원본
    for f in os.listdir(SUBMIT):
        if f.endswith(".pdf"):
            os.remove(os.path.join(SUBMIT, f))
    lines = [f"[제출 현황 · 내부용 — 첨부 금지] {SITE} · 접수 {D.SUBMIT_TO} · 제목 {D.MAIL_TITLE} · 마감 {D.DEADLINE}", ""]
    print("\n[작업본 — 별지 6 순서 · 지금 상태 그대로]")
    attach = []
    for k in [k for k in ORDER if k in res]:
        v = res[k]
        good = ok.get(k, True)
        src = P08 if k == "08" else v
        msg = f"{k} {'제출 가능' if good else '조치 필요'}  {PFX}{NAMES[k]}.pdf  {len(fitz.open(src))}p  {os.path.getsize(src) / 1e6:.2f}MB"
        print(msg)
        lines.append(msg)
        if good:
            dst = os.path.join(SUBMIT, PFX + NAMES[k] + ".pdf")
            shutil.copyfile(src, dst)
            attach.append((k, dst))
    lines += ["13 계약이행보증보험 — 주관사 선정 후 제출(파일 없음)"]
    if os.path.exists(ZIP):
        os.remove(ZIP)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:  # 공고: '제출서류는 보기좋게 폴더별로 .zip'
        for k, p in attach:
            z.write(p, f"{NAMES[k]}/{os.path.basename(p)}")
    zmb = os.path.getsize(ZIP) / 1e6
    lines += ["", f"ZIP(제출본 {len(attach)}개 · 폴더별): {ZIP}  {zmb:.1f}MB"]
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
