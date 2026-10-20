# -*- coding: utf-8 -*-
"""판교테크노밸리 중흥S-클래스 입주지원 주관사 입찰 — 공고 5항 제출서류 12종 생성기(A4 세로 · 본부장 10-20).

  01 입찰참가신청서 [별지서식 제1호]                 02 제안서(build_pg.py 결과 원본)
  03 법인 사업자등록증 & 통장 사본                   04 법인등기부 등본
  05 인감증명서(대표자 주민번호 뒷자리 가림본)        06 국세 및 지방세 완납 증명서
  07 4대 보험 가입증명서(사업장 가입자 명부 가림본 + 완납증명서)
  08 청렴협약이행각서 [별지서식 제2호]               09 계약자의 계약취소 건에 대한 환불규정
  10 하자보수 A/S 이행각서(자유양식)                 11 기업신용평가서(NICE 전문 · 대표 외 임직원 생년월일 가림)
  12 최근 2년 재무제표 및 손익계산서 — 본부장 제공 파일(FIN_FILES)이 있으면 합침, 없으면 '조치 필요'
별지 1 · 2는 공고 서식 문구를 그대로 옮기고 빈칸(일자 · 법인명 · 주소 · 대표자)만 채운다. 날인 = 직인 투명 PNG를 '(직인 또는 인감)' 자리에.
법인인감은 디지털로 만들지 않는다 — 실물 인감 날인을 원하면 작업/의 '서식날인_출력용.pdf'를 출력해 날인 · 스캔.

출력: 작업/ = 중간 파일 · 제출현황.txt(내부용) / 제출본/ = 조치 끝난 서류만 '엣지컴퍼니_판교테크노밸리중흥S_NN_항목.pdf' · ZIP(공고 순서)
사용: python docs_pg.py <직인.png> [--final]     (결과 PDF · HTML · ZIP은 깃 제외 — .gitignore)
"""
import html
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
PFX = "엣지컴퍼니_판교테크노밸리중흥S_"
ST = D.SITE
SITE = ST["name"]
FORM_TO = "판교테크노밸리 중흥S-클래스 입주예정자협의회"
CASE = "판교테크노밸리 중흥S-클래스 입주예정자협의회 주관사 선정"   # 별지 1 · 2 '건 명' 원문
TODOS = []

SP = "/tmp/claude-0/-home-user-edge-company/a96d9eb6-5244-5d3f-9f1b-6f379ac2a82c/scratchpad"
EV = os.environ.get("PG_EVIDENCE", f"{SP}/evidence")  # 증빙 원본(깃 제외)
NICE_SRC = f"{EV}/NICE_기업신용평가.pdf"
ROSTER = f"{SP}/cs_sub/엣지컴퍼니_철산역자이_06_4대보험_사업장가입자명부.pdf"  # 10.02 명부 가림본(성명 가운데 글자 · 주민번호 뒷자리, 픽셀로 굳힘)
FIN_FILES = [f for f in (f"{EV}/재무제표_2024.pdf", f"{EV}/재무제표_2025.pdf") if os.path.exists(f)]  # 본부장 제공(최근 2년 재무제표 · 손익계산서)
WORK = os.path.join(HERE, "작업")
SUBMIT = os.path.join(HERE, "제출본")
ZIP = os.path.join(HERE, PFX + "제출서류.zip")
P02 = os.path.join(HERE, PFX + "입주지원_주관사_제안서.pdf")


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
.art{margin-top:7pt;break-inside:avoid}
.art h3{font-size:10.6pt;font-weight:800;color:#0D1E33}
.art p{margin-top:2pt}
.art ol{list-style:none;margin-top:2pt}
.art ol li{padding-left:16pt;text-indent:-16pt;margin-top:2pt}
"""

HEAD = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{t}</title>'
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">'
        '<style>{css}</style></head><body>')


def doc(title, sections, css=CSS):
    return HEAD.format(t=e(title), css=css) + "".join(f'<section class="pg">{s}</section>' for s in sections) + "</body></html>"


def head(label, title, center=False):
    return (f'<div class="top"><div class="lb">{e(label)}</div><div class="co">{D.COMPANY} · 입주지원 주관사</div></div>'
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


def form_tail():
    """별지 1 · 2 꼬리(원문): 2026년 월 일 → 법인명 · 주소 · 대표자 (직인 또는 인감)."""
    yy, mm, dd = ymd()
    return (f'<div class="dt" style="margin-top:30pt">{yy}년 &nbsp; {mm}월 &nbsp; {dd}일</div>'
            f'<div class="sgx" style="margin-top:22pt"><div class="ln">법 인 명 : <b>{D.COMPANY}</b><br>주 &nbsp; &nbsp; 소 : {D.ADDRESS}<br>대 표 자 : <b>대표이사 {D.CEO}</b></div>'
            f'<div class="bx"><i>직인 또는<br>인감</i><b>(인)</b></div></div>')


# ================================================================== 01 입찰참가신청서 [별지서식 제1호]
def doc01():
    body = f"""<div class="form"><div class="no">[별지서식 제1호]</div><h1>입찰참가신청서</h1>
<p style="text-align:center;font-size:11.5pt">&lt;건 명 : {CASE}&gt;</p>
<p class="tx" style="margin-top:22pt">귀 입주예정자협의회에서 실시하는 입주관련 주관사 선정에 소정의 양식을 갖추어 입찰참여 신청서를 제출하며, 만일 제출한 서류가 허위 또는 부정한 방법으로 작성된 사실이 확인될 경우에는 귀 협의회에서 정한 바에 따라 처리하여도 아무런 이의를 제기하지 않겠음을 확약합니다.</p>
<p class="tx">그리고 귀 협의회의 평가를 위해 구성한 평가위원과 평가방법 및 평가기준에 따른 결과에 대해서도 어떠한 이의를 제기하지 않겠으며, 사업자 선정 전까지도 귀 협의회의 요청 내용과 협약체결에 따른 증빙 서류 제출 등 제반 유의사항을 준수할 것을 확약합니다.</p>
{form_tail()}</div>"""
    return doc("01 입찰참가신청서", [body])


# ================================================================== 08 청렴협약이행각서 [별지서식 제2호]
def doc08():
    body = f"""<div class="form"><div class="no">[별지서식 제2호]</div><h1>청렴협약이행각서</h1>
<p style="text-align:center;font-size:11.5pt">&lt;건 명 : {CASE}&gt;</p>
<p class="tx" style="margin-top:22pt">위 건 입찰에 참여한 본 주관사는 판교테크노밸리 중흥S-클래스 입주예정자협의회에서 시행하는 「주관사 선정」에 참여함에 있어 공동구매 및 입주박람회 참여업체 선정 및 관리, 사후 하자보수 및 A/S, 행사 지원 등(입찰 공고문에 포함하고 있는 업무 일체)의 업무를 성실히 이행할 것입니다.</p>
<p class="tx">본 주관사의 귀책사유 발생시 전적으로 본 주관사의 책임이며, 어떠한 이의도 제기치 않을 것임을 서약합니다. 또한 본 주관사 임직원과 대리인은 관계법령과 규정에 저해되는 일체의 불공정한 행위는 물론, 어떠한 압력이나 청탁도 행사하지 않겠습니다.</p>
<p class="tx">위 청렴협약 서약은 상호신뢰를 바탕으로 한 약속으로서 반드시 지킬 것이며, 이를 위반할 경우 입찰참가자격 제한, 협약해지 또는 해제 등 판교테크노밸리 중흥S-클래스 입주예정자협의회의 조치에 대하여 손해배상을 청구하거나 민·형사상 어떠한 이의도 제기하지 않을 것을 서약합니다.</p>
{form_tail()}</div>"""
    return doc("08 청렴협약이행각서", [body])


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
            "주관사의 보상 재원으로 하자 예치금 최대 1억원(엣지컴퍼니 자산으로 예치)과 협약이행증권 · 하자보증 보험증권(12개월 이상, 금액은 협약 때 확정)을 둔다.",
        ]),
        ("제8조 (가격 보호 — 최저가 차액 10배 보상)", [
            f"공동구매 품목과 브랜드·모델명이 같은 새 제품이 계약 후 7일 이내에 인근({ST['local']}) 오프라인 매장에서 "
            "더 낮은 정상 판매가로 실제 판매된 사실이 구매 영수증(판매 매장 사업자 정보 · 모델명 · 금액 기재)으로 확인되고 "
            "주관사가 해당 매장에 판매 사실을 확인하면, 참여업체는 차액의 10배를 보상하고 판매가를 조정한다.",
            "보상액은 1건당 해당 품목의 계약금액을 넘지 않으며, 1건당 최대 보상액은 협약 시 입예협과 협의해 정한다(같은 세대 · 같은 품목에는 1회). 견적서 · 가격표 · 구두 안내 가격은 보상 근거가 되지 않는다.",
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
    return doc("09 계약 취소 · 환불 규정", [head("제출서류 9", "공동구매 계약 취소 · 환불 규정") + summary + "".join(out) + table + sign()])



# ================================================================== 10 하자보수 A/S 이행각서(자유양식)
def doc10():
    items = [
        "주관사는 판교테크노밸리 중흥S-클래스 입주박람회 · 공동구매(이하 ‘공동구매’)에서 계약된 모든 품목의 하자보수 · A/S를 참여업체와 함께 책임지며, 입주민의 접수는 주관사 한 창구(콜센터 · 공식카페 신문고 · 카카오채널)로 받는다.",
        "하자 · A/S 접수 시 <b>24시간 이내</b> 1차 회신하고, <b>48시간 이내 하자보수</b>를 원칙으로 한다. 부품 수급 등으로 늦어지면 사유와 완료 예정일을 입주민에게 알린다.",
        "무상 A/S 기간은 <b>최소 2년</b>(제조사 보증이 더 길면 그 기간)으로 하고, 품목별 기간을 계약서에 명시한다. 주관사 접수 창구는 입주 후 1년 운영한다.",
        "참여업체 전원은 하자보수 이관 · 보증 기간 · 지연 배상을 정한 특약이행각서(9개 항)에 서명해야 참여할 수 있다.",
        "참여업체가 기한 안에 응하지 않으면 주관사가 입주민에게 <b>먼저 보상</b>하고 업체와 나중에 정산한다.",
        "참여업체가 폐업 · 도산 · 연락 두절되면 주관사가 동종업체로 하자보수를 이관하고, 그 A/S 비용은 주관사가 <b>전액 부담</b>한다.",
        "주관사는 협약 시 협의회를 피보험자로 협약이행증권 · 하자보증 보험증권을 <b>12개월 이상</b>으로 발급해 제출한다(금액은 협약 때 확정).",
        "하자 · A/S 접수 · 처리 현황은 입주 후 <b>월 1회</b> 협의회에 보고하고, 운영 종료 시 최종 결과 보고서를 제출한다.",
        "위 사항을 이행하지 않으면 협약 해지 · 손해배상 등 협의회의 조치를 받아들이며 어떠한 이의도 제기하지 않는다.",
    ]
    body = f"""{head("제출서류 10", "하자보수 A/S 이행각서")}
<table class="info"><tr><th>주 관 사</th><td>{D.COMPANY} (사업자등록번호 {D.BIZ_NO})</td></tr>
<tr><th>대 표 자</th><td>대표이사 {D.CEO}</td></tr><tr><th>주 &nbsp; &nbsp; 소</th><td>{D.ADDRESS}</td></tr>
<tr><th>대 상</th><td>{SITE} {ST['households']}세대 입주박람회 · 공동구매 전 품목</td></tr></table>
<p class="body">당사는 {FORM_TO}(이하 ‘협의회’)와 체결할 주관 협약에 따라 공동구매 품목의 사후 하자보수 및 A/S를 아래와 같이 이행할 것을 각서합니다.</p>
<ol class="pl">{"".join(f"<li>{i}. {x}</li>" for i, x in enumerate(items, 1))}</ol>
{sign()}"""
    return doc("10 하자보수 A/S 이행각서", [body])


# ================================================================== 11 기업신용평가서 — 표지 + NICE 전문(대표 외 임직원 생년월일 가림)
NICE_MASK = {12: [(170, 148.5, 228, 163.5), (170, 166.5, 228, 181.5)]}  # 원본 13쪽 '주요 경영진' 생년월일 칸 — 대표 외 임직원 2명


def doc15_cover(n_pages):
    body = f"""{head("제출서류 11", "기업신용평가서")}
<table class="t" style="margin-top:14pt"><tbody>
<tr><td class="k" style="width:22%">보고서</td><td class="l">NICE디앤비 CLIP 기업신용평가보고서(관리번호 11125949-202605-001) — <b>전문 {n_pages}쪽</b></td></tr>
<tr><td class="k">평가 대상</td><td class="l">{D.COMPANY} ({D.BIZ_NO})</td></tr>
<tr><td class="k">평가일 · 유효기간</td><td class="l">{D.NICE_DATE} · ~2027.06.18 — 당사의 가장 최근 평가</td></tr>
<tr><td class="k">결과</td><td class="l">신용등급 BB- · 현금흐름등급 A</td></tr>
<tr><td class="k">구성</td><td class="l">기업신용평가 요약 · Summary · 재무분석 · 영업 현황(기업개요 · 연혁 · 사업장 · 인증) · 경영진 현황 · 금융정보 · 재무제표 · 신용등급 정의</td></tr>
<tr><td class="k">개인정보</td><td class="l">원본 13쪽 ‘경영진 현황’의 대표 외 임직원 2명 생년월일은 개인정보 보호를 위해 가렸습니다(그 밖의 내용은 원본 그대로).</td></tr>
</tbody></table>
<p class="note" style="margin-top:8pt">※ 보고서의 본사 주소는 본점 이전(2026.07.02 등기) 전 주소이고, 종업원 수와 경영진 현황은 평가 당시(2026.05) 기준입니다. 주관사업 총괄 본부장({D.MANAGER[0]})은 평가 이후 합류했습니다. 현재 본점 · 등기 사항은 제출서류 3 · 4와 같습니다.</p>
"""
    return doc("11 기업신용평가서", [body])


def nice_full(nice_path):
    d = fitz.open(nice_path)
    assert len(d) == 24, f"NICE 보고서 {len(d)}쪽 — 가림 좌표 다시 확인"
    for i, rects in NICE_MASK.items():
        pg = d[i]
        assert any(x["width"] == 2477 and x["height"] == 3502 for x in pg.get_image_info()), "NICE 13쪽 이미지가 다름 — 가림 좌표 다시 확인"
        for r in rects:
            pg.add_redact_annot(fitz.Rect(*r), fill=(0.82, 0.82, 0.82))
        pg.apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS)
    p = out("11_2_NICE_전문_가림.pdf")
    d.save(p, garbage=GARBAGE, deflate=True)
    return p



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


ORDER = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
NAMES = {  # 제출본 파일 · ZIP 폴더 이름(공고 5항 번호 · 서류명)
    "01": "01_입찰참가신청서", "02": "02_제안서", "03": "03_사업자등록증_통장사본", "04": "04_법인등기부등본",
    "05": "05_인감증명서", "06": "06_국세_지방세_완납증명서", "07": "07_4대보험_가입증명서", "08": "08_청렴협약이행각서",
    "09": "09_계약취소_환불규정", "10": "10_하자보수_AS_이행각서", "11": "11_기업신용평가서", "12": "12_최근2년_재무제표_손익계산서",
}


def evidence_check():
    t = fitz.open(f"{EV}/사업자등록증.pdf")[0].get_text()
    assert "2026 년10 월14 일" in t and "전시,박람회및행사대행업" in t, "사업자등록증 발급일 · 종목 확인 실패"
    t = fitz.open(f"{EV}/국세_납세증명서.pdf")[0].get_text()
    assert "2026 년10 월14 일" in t and "2026 년11 월13 일" in t, "국세 납세증명서 발급일 · 유효기간 확인 실패"
    for p in (f"{EV}/법인인감증명서.pdf", f"{EV}/법인등기부등본.pdf", f"{EV}/지방세_납세증명서.pdf", f"{EV}/법인통장_사본.pdf",
              f"{EV}/4대보험_완납증명서.pdf", f"{EV}/고용산재_완납증명서.pdf", ROSTER, NICE_SRC, P02):
        assert os.path.exists(p), f"없음: {p}"
    assert len(fitz.open(ROSTER)) == 2, "명부 가림본 쪽수"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    final = "--final" in sys.argv
    if not args:
        sys.exit(__doc__)
    evidence_check()
    miss = [] if FIN_FILES else ["12 최근 2년 재무제표 · 손익계산서 — 본부장 제공 파일 없음(evidence/재무제표_2024.pdf · 재무제표_2025.pdf)"]
    if miss:
        print(f"[확인 필요 {len(miss)}건]\n  - " + "\n  - ".join(miss))
        if final:
            sys.exit("--final: 확인 필요 건이 남아 있어 파일을 쓰지 않고 멈춤")
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(SUBMIT, exist_ok=True)
    seal = seal_image(args[0])

    def stamped(p, n_expect=1):
        o, n = stamp(seal, p)
        assert n == n_expect, f"날인 자리 {n}곳(예상 {n_expect}): {p}"
        return o

    res = {}
    res["01"] = stamped(fit(render("01_입찰참가신청서", doc01()), 1))
    res["02"] = P02
    biz = fitz.open(f"{EV}/사업자등록증.pdf")
    for pg_ in biz:
        for a in list(pg_.annots()):  # 발급 뒤 덧붙인 스탬프 주석이 원본 칸을 가리지 않게
            pg_.delete_annot(a)
    res["03"] = merge(NAMES["03"], [biz, f"{EV}/법인통장_사본.pdf"], "3 법인 사업자등록증 · 통장 사본")
    res["04"] = merge(NAMES["04"], [f"{EV}/법인등기부등본.pdf"], "4 법인등기부 등본")
    res["05"] = merge(NAMES["05"], [f"{EV}/법인인감증명서.pdf"], "5 인감증명서")
    res["06"] = merge(NAMES["06"], [f"{EV}/국세_납세증명서.pdf", f"{EV}/지방세_납세증명서.pdf"], "6 국세 및 지방세 완납 증명서")
    res["07"] = merge(NAMES["07"], [ROSTER, f"{EV}/4대보험_완납증명서.pdf", f"{EV}/고용산재_완납증명서.pdf"], "7 4대 보험 가입증명서(가입자 명부 · 완납증명서)")
    res["08"] = stamped(fit(render("08_청렴협약이행각서", doc08()), 1))
    res["09"] = stamped(fit(render("09_계약취소_환불규정", doc09()), 2, 3))
    res["10"] = stamped(fit(render("10_하자보수_AS_이행각서", doc10()), 1))
    nice11 = nice_full(NICE_SRC)
    res["11"] = merge(NAMES["11"], [fit(render("11_1_표지", doc15_cover(len(fitz.open(nice11)))), 1), nice11], "11 기업신용평가서(NICE 전문)",
                      [[1, "표지", 1], [1, "NICE디앤비 CLIP 기업신용평가보고서 전문", 2]])
    if FIN_FILES:
        res["12"] = merge(NAMES["12"], FIN_FILES, "12 최근 2년 재무제표 및 손익계산서")

    # 서식 날인용 출력본(직인 전) — 출력 → 실물 인감 날인 → 스캔
    pr = fitz.open()
    for nm in ["01_입찰참가신청서", "08_청렴협약이행각서", "09_계약취소_환불규정", "10_하자보수_AS_이행각서"]:
        pr.insert_pdf(fitz.open(out(nm + ".pdf")))
    pr.save(out("서식날인_출력용.pdf"), garbage=GARBAGE, deflate=True)

    for f in os.listdir(SUBMIT):
        if f.endswith(".pdf"):
            os.remove(os.path.join(SUBMIT, f))
    lines = [f"[제출 현황 · 내부용 — 첨부 금지] {SITE} · 접수 {D.SUBMIT_TO} · 제목 {D.MAIL_TITLE} · 마감 {D.DEADLINE}", ""]
    attach = []
    for k in ORDER:
        if k not in res:
            lines.append(f"{k} 조치 필요  {PFX}{NAMES[k]}.pdf — 파일 없음")
            continue
        src = res[k]
        lines.append(f"{k} 제출 가능  {PFX}{NAMES[k]}.pdf  {len(fitz.open(src))}p  {os.path.getsize(src) / 1e6:.2f}MB")
        dst = os.path.join(SUBMIT, PFX + NAMES[k] + ".pdf")
        shutil.copyfile(src, dst)
        attach.append((k, dst))
    if os.path.exists(ZIP):
        os.remove(ZIP)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for k, p in attach:
            z.write(p, os.path.basename(p))
    lines += ["", f"ZIP(제출본 {len(attach)}개): {ZIP}  {os.path.getsize(ZIP) / 1e6:.1f}MB"]
    text = "\n".join(lines) + "\n"
    pathlib.Path(WORK, "제출현황.txt").write_text(text, encoding="utf-8")
    print(text)
    if TODOS:
        print("[노란 칸]", " / ".join(dict.fromkeys(TODOS)))


if __name__ == "__main__":
    main()
