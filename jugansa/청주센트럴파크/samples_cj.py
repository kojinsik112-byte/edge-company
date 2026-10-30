# -*- coding: utf-8 -*-
"""청주 제안서 견본 이미지 2장 — 군포 gp_bond_sample · gp_gaksu_v(단지명 박힘)와 같은 구성으로 청주 이름을 넣어 다시 그린다.

assets_ins/cj_bond_sample.jpg = 이행(하자)보증보험증권 발급 예정 내용(견본 · 보험사 증권 아님)
assets_ins/cj_gaksu_v.jpg     = 참여업체 특약이행각서 양식
사용: python samples_cj.py
"""
import os
import pathlib
import subprocess
import sys

import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "요약제안서")]
import data as D  # noqa: E402
from build import find_chrome  # noqa: E402

SITE = D.SITE["name"]
CL = D.CLIENT
WORK = os.path.join(HERE, "작업", "_samples")

BOND = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>
@page{{size:A4;margin:0}}*{{box-sizing:border-box;margin:0;padding:0}}
html{{width:210mm;height:297mm;overflow:hidden}}
body{{font-family:'Malgun Gothic',sans-serif;color:#1d2433;width:210mm;height:297mm;padding:9mm 10mm;position:relative;font-size:9pt;overflow:hidden}}
.tag{{display:inline-block;background:#c0392b;color:#fff;font-weight:800;padding:4px 18px;border-radius:5px;font-size:12pt;letter-spacing:.3em}}
.hd{{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:3px solid #1d2433;padding-bottom:3mm;margin-top:3mm}}
h1{{font-size:19pt;font-weight:800;letter-spacing:.04em}}.sub{{font-size:8.5pt;color:#555;margin-top:2mm}}
.no{{text-align:right;font-size:8pt;color:#666;line-height:1.25;white-space:nowrap}}.no b{{display:block;font-size:11pt;color:#1d2433}}
.warn{{border:1.5px solid #c0392b;border-radius:7px;background:#fdf1f0;padding:4mm 5mm;margin:4mm 0;font-size:9pt;line-height:1.6}}
.warn b{{color:#a42a1c}}h2{{font-size:11pt;margin:4mm 0 2mm;border-left:4px solid #c8a86a;padding-left:3mm}}
table{{width:100%;border-collapse:collapse;font-size:9pt}}td{{border:1px solid #cfd5df;padding:1.3mm 3mm;line-height:1.4;vertical-align:middle}}
td.k{{width:28%;background:#eef2f7;font-weight:700}}.g{{color:#999}}
.sig{{display:grid;grid-template-columns:1fr 1fr;gap:9mm;margin-top:4mm}}.sig div{{border:1.2px solid #cfd5df;border-radius:6px;padding:2.5mm 4mm;font-size:9pt;line-height:1.55}}
.ft{{margin-top:4mm;border-top:1px solid #bbb;padding-top:2mm;font-size:7.8pt;color:#666;line-height:1.55}}
.wm{{position:absolute;left:8mm;top:125mm;font-size:40pt;font-weight:800;color:rgba(192,57,43,.13);transform:rotate(-28deg);letter-spacing:.2em;border:5px solid rgba(192,57,43,.13);border-radius:16px;padding:2mm 10mm;white-space:nowrap}}
</style></head><body>
<div class="wm">견본 · SPECIMEN · 실제 증권 아님</div>
<span class="tag">견 본</span>
<div class="hd"><div><h1>이행(하자)보증보험증권 발급 예정 내용</h1>
<div class="sub">{SITE} · 입주박람회 주관 협약 이행 및 공동구매 하자보수 보증 · 주관사 선정 · 계약 후 발급</div></div>
<div class="no">증권번호<b>발급 시 기재</b>발행일<b>협약 체결 후</b></div></div>
<div class="warn">이 문서는 <b>보험사가 발행한 증권이 아닙니다.</b> 협약 체결 시 주식회사 엣지컴퍼니가 보증보험사(서울보증보험 등)에 청약하여 발급받을 증권의 <b>기재 예정 항목을 안내하는 견본</b>입니다. 보험가입금액 · 보험기간 · 보증 내용은 협의회와 협의하여 협약서로 확정하며, 실제 효력은 보험사가 발행한 증권 원본과 약관에 따릅니다.</div>
<h2>기본 사항</h2><table>
<tr><td class="k">보험계약자</td><td>주식회사 엣지컴퍼니 (사업자등록번호 {D.BIZ_NO}) · 대표이사 {D.CEO}</td></tr>
<tr><td class="k">피보험자</td><td>{CL} <span class="g">(고유번호 · 대표자는 발급 시 기재)</span></td></tr>
<tr><td class="k">보증 종목</td><td>☐ 이행(계약)보증 &nbsp; ☐ 하자보수보증 <span class="g">- 협약에서 정한 종목으로 발급</span></td></tr>
<tr><td class="k">보험가입금액</td><td><span class="g">금 &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; 원정</span> - 본 협약 이행보증 금액은 <b>협약 때 단지 규모({D.SITE['households']:,}세대)에 맞춰 협의회와 확정</b></td></tr>
<tr><td class="k">보험기간</td><td><span class="g">20 &nbsp; 년 &nbsp; 월 &nbsp; 일부터 20 &nbsp; 년 &nbsp; 월 &nbsp; 일까지</span> (협약일 ~ 공동구매 품목 A/S 종료일 기준 협의)</td></tr>
<tr><td class="k">보험료 납입</td><td>주관사 전액 부담 · 협의회 부담 없음</td></tr></table>
<h2>보증하는 사항 (주계약 내용)</h2><table>
<tr><td class="k">주계약명</td><td>{SITE} 공동구매 및 입주박람회 기획 · 진행 위탁 계약</td></tr>
<tr><td class="k">계약 당사자</td><td>위탁자 : {CL} &nbsp;/&nbsp; 수탁자 : 주식회사 엣지컴퍼니</td></tr>
<tr><td class="k">계약기간</td><td class="g">협약서에서 정한 협약 기간</td></tr>
<tr><td class="k">계약체결일자</td><td class="g">20 &nbsp; 년 &nbsp; 월 &nbsp; 일</td></tr>
<tr><td class="k">보증 내용</td><td>1. 주관사가 협약서 · 제안서에서 정한 의무(입주박람회 개최, 공급업체 관리, 민원 처리 등)를 이행하지 않아 협의회에 생긴 손해<br>
2. 공동구매 품목의 하자보수 · A/S를 공급업체와 주관사가 기한 안에 이행하지 않아 생긴 손해<br>3. 그 밖에 협약서에 정한 보증 범위 - 보험사 약관 범위 안에서 확정</td></tr></table>
<h2>청구 절차 (안내)</h2><table>
<tr><td class="k">① 사유 발생</td><td>협의회가 주관사에 서면으로 이행 · 시정을 요구 (협약서에 정한 절차)</td></tr>
<tr><td class="k">② 미이행 확인</td><td>정한 기한 안에 이행되지 않은 사실과 손해 내역을 정리</td></tr>
<tr><td class="k">③ 보험금 청구</td><td>{CL}가 증권 원본 · 협약서 · 손해 증빙을 갖추어 보험사에 직접 청구</td></tr>
<tr><td class="k">④ 진위 확인</td><td>발급 후 협의회는 보험사 홈페이지 · 앱에서 증권 진위를 직접 확인할 수 있음</td></tr></table>
<div class="sig"><div><b>보험계약자</b><br>주식회사 엣지컴퍼니 · 대표이사 {D.CEO}<br><span class="g">(발급 시 보험사 증권 원본으로 대체)</span></div>
<div><b>피보험자 확인</b><br>{CL} 회장<br><span class="g">(증권 수령 확인 · 서명)</span></div></div>
<div class="ft">참고 - 당사 보증보험 발급 이력: 서울보증보험 계약보증보험증권 1건(광고대행 용역 계약보증 · 제출 ⑪ 기타 자료에 수록). 입주박람회 협약 이행(하자) 보증은 주관사 선정 · 계약 후 발급하며, 보증보험사 발급 한도는 확인했습니다(2026.10).<br>
견본 작성: 주식회사 엣지컴퍼니 · {D.MANAGER[1]} {D.MANAGER[0]} {D.MANAGER[2]} · {D.EMAIL}</div>
</body></html>"""

ART = [("하자보수 이관 의무", "업체는 관련 법령 및 계약에 따른 하자보수 이관 의무를 성실히 이행한다."),
       ("이관 대상", "설비·마감공사 등 업체가 시공·납품한 품목에서 입주민 하자가 발생하면 계약서에 명시한 보수 범위에 따라 보수한다."),
       ("하자 통보", "하자 통보와 회신은 서면(내용증명·전자문서를 포함한다)으로 하며, 접수 및 처리의 근거를 남긴다."),
       ("계약 해지", "업체 사정으로 계약을 해지하는 경우 중도 정산을 하고, 잔여 권리에 대한 포기 각서를 제출한다."),
       ("보증 기간", "하자 접수 기간은 시공·납품 완료일부터 최소 2년으로 하며, 그 기간 동안 보증 책임과 조치 의무를 진다."),
       ("연대 책임", "업체가 폐업·도산하는 경우 별도 계약 없이도 주관사 또는 주관사가 지정한 동종업체의 하자보수 승계를 승인한다."),
       ("지연 배상", "하자보수 비용의 지급 기한을 지키지 않으면 지연배상금을 지급하며, 그로 인하여 발생한 손해를 배상한다."),
       ("민원 처리", "입주민 민원이 발생하면 즉시 처리하고, 그 결과를 주관사 및 입주예정자협의회에 보고한다."),
       ("주관사 이관 동의", "업체의 도산·연락 두절 등으로 하자보수가 불가능한 경우, 주식회사 엣지컴퍼니의 사후관리·하자보수 이관 및 그 비용의 구상에 동의한다.")]
GAKSU = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>
@page{{size:A4;margin:0}}*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Batang','바탕',serif;color:#111;width:210mm;padding:9mm 20mm 0;font-size:10pt;line-height:1.45}}
h1{{text-align:center;font-size:27pt;letter-spacing:.9em;margin:0 0 6mm;font-weight:700}}
table{{width:100%;border-collapse:collapse;margin-bottom:4mm}}td{{border:1px solid #111;padding:1.5mm 3mm;height:8mm}}td.k{{text-align:center;letter-spacing:.3em;width:22%}}
p{{text-align:justify;margin-bottom:1.6mm}}.c{{text-align:center;letter-spacing:.6em;margin:3mm 0}}
.sg{{margin:3mm 0 0 62mm;line-height:1.9;letter-spacing:.25em}}.to{{text-align:center;font-size:14pt;margin-top:4mm}}
</style></head><body><h1>특약이행각서</h1>
<table><tr><td class="k">상 호</td><td></td><td class="k">대표자</td><td></td></tr>
<tr><td class="k" style="letter-spacing:0">사업자등록번호</td><td></td><td class="k">참여품목</td><td></td></tr>
<tr><td class="k">주 소</td><td colspan="3"></td></tr>
<tr><td class="k">건 명</td><td colspan="3">{SITE} 입주박람회 참여업체 하자보수 · 사후관리 이행</td></tr></table>
<p>당사는 {SITE} 입주박람회(이하 “박람회”)에 참여업체로 참가함에 있어, 박람회를 통하여 입주예정자와 체결한 공동구매 계약의 하자보수 및 사후관리에 관하여 아래 사항을 성실히 이행할 것을 각서합니다.</p>
<p class="c">- 아 래 -</p>
{"".join(f"<p><b>제{i}조({a})</b> {b}</p>" for i, (a, b) in enumerate(ART, 1))}
<p>당사는 위 사항을 위반하는 경우 입주예정자협의회의 승인에 따른 참여 자격 박탈 · 계약 이관 · 손해배상 등 어떠한 조치에도 이의를 제기하지 않겠습니다.</p>
<p style="text-align:center;margin-top:4mm">위 사항을 성실히 이행할 것을 각서합니다.</p>
<p style="text-align:center;letter-spacing:1.2em;margin-top:3mm">20 &nbsp; 년 &nbsp; 월 &nbsp; 일</p>
<div class="sg">각서인<br>상 호<br>사업자번호<br>대 표 자 <span style="margin-left:52mm;letter-spacing:0">(인)</span></div>
<p style="margin-top:4mm">붙임 &nbsp;1. 사업자등록증 사본 1부.<br>&nbsp; &nbsp; &nbsp; &nbsp; 2. 공동구매 계약서 사본 1부. &nbsp; 끝.</p>
<div class="to">주식회사 엣지컴퍼니 대표이사 귀하<br><span style="font-size:13pt">({CL} 귀중)</span></div>
</body></html>"""


def shot(html, name):
    os.makedirs(WORK, exist_ok=True)
    hp, pp = os.path.join(WORK, name + ".html"), os.path.join(WORK, name + ".pdf")
    open(hp, "w", encoding="utf-8").write(html)
    subprocess.run([find_chrome(), "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pp}", pathlib.Path(hp).as_uri()], check=True, capture_output=True, timeout=120)
    d = fitz.open(pp)
    assert d.page_count == 1, (name, d.page_count)
    out = os.path.join(HERE, "assets_ins", name + ".jpg")
    d[0].get_pixmap(dpi=240).save(out, jpg_quality=90)
    print(out)


if __name__ == "__main__":
    shot(BOND, "cj_bond_sample")
    shot(GAKSU, "cj_gaksu_v")
