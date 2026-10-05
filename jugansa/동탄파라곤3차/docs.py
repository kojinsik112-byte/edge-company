# -*- coding: utf-8 -*-
"""동탄 파라곤3차 입찰 제출서류(A4 세로) — 8) 행사 실적, 9) 계약 취소·환불 규정.

데이터는 data.py 한 곳에서 가져온다(제안서 실적 장과 같은 숫자).
환불 규정은 통합제안서 기본틀 '05.계약조건'·'07.취소/환불 규정'·'하자보증'의 기존 약속을 조항으로 옮긴 것.

사용: python docs.py
"""
import html
import os
import pathlib
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "요약제안서")]
import data as D  # noqa: E402
from build import find_chrome  # noqa: E402

e = html.escape

CSS = r"""
@page{size:A4;margin:13mm 17mm 13mm}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Pretendard','Malgun Gothic','맑은 고딕',sans-serif;color:#1B2433;font-size:10pt;line-height:1.6;
  word-break:keep-all;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.top{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:2.5pt solid #0D1E33;padding-bottom:6pt}
.top .lb{font-size:9pt;font-weight:700;letter-spacing:.18em;color:#9A7B3F}
.top .co{font-size:9pt;color:#5B6676;text-align:right}
h1{font-size:20pt;font-weight:800;color:#0D1E33;margin-top:12pt;letter-spacing:-.01em}
.case{font-size:10pt;color:#5B6676;margin-top:3pt}
.info{width:100%;border-collapse:collapse;margin-top:12pt;font-size:9.8pt}
.info th{width:14%;background:#F1EDE4;color:#0D1E33;font-weight:700;text-align:left;padding:5pt 9pt;border:.6pt solid #D5CCB9}
.info td{padding:5pt 9pt;border:.6pt solid #D5CCB9}
h2{font-size:12pt;font-weight:800;color:#0D1E33;margin:11pt 0 5pt;padding-left:8pt;border-left:3.5pt solid #C8A86A;line-height:1.3}
.t{width:100%;border-collapse:collapse;font-size:9.8pt}
.t th{background:#0D1E33;color:#fff;font-weight:700;padding:4pt 6pt;border:.6pt solid #0D1E33;text-align:center}
.t td{padding:3.6pt 6pt;border:.6pt solid #C9CED6;text-align:center;vertical-align:middle}
.t td.l{text-align:left}
.t td.r{text-align:right;font-variant-numeric:tabular-nums}
.t tr.sum td{background:#F1EDE4;font-weight:800}
.t td.k{font-weight:700;background:#F6F7F9;text-align:left;width:24%}
.box{border:1pt solid #C8A86A;background:#FBF8F1;border-radius:4pt;padding:8pt 11pt;margin-top:10pt;font-size:10pt}
.box b{color:#0D1E33}
.ok{color:#1F7A4D;font-weight:800}
ul.n{list-style:none;margin-top:4pt}
ul.n li{padding-left:14pt;text-indent:-14pt;margin-top:2pt}
.note{font-size:9pt;color:#5B6676;margin-top:5pt}
.art{margin-top:9pt;break-inside:avoid}
.art h3{font-size:10.8pt;font-weight:800;color:#0D1E33}
.art ol{list-style:none;margin-top:2pt}
.art ol li{padding-left:16pt;text-indent:-16pt;margin-top:2pt}
.sign{margin-top:12pt;text-align:center;break-inside:avoid}
.sign .d{font-size:11pt;letter-spacing:.06em}
.sign .who{margin-top:4pt;font-size:12pt;font-weight:700;display:inline-flex;gap:14pt;align-items:center}
.sign .seal{color:#5B6676;font-size:10pt;font-weight:400;margin-left:6pt}
.to{margin-top:26pt;text-align:center;font-size:12.5pt;font-weight:800;color:#0D1E33}
"""


def page(label, title, body):
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{e(title)}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<style>{CSS}</style></head><body>
<div class="top"><div class="lb">{e(label)}</div><div class="co">{D.COMPANY} · 입주박람회 주관사</div></div>
<h1>{e(title)}</h1>
<div class="case">건명 : {e(D.TITLE)}</div>
{body}
<div class="sign"><div class="d">{D.SIGN_DATE[0]}년 {D.SIGN_DATE[1]}월 {D.SIGN_DATE[2]}일</div>
<div class="who"><span>{D.COMPANY} &nbsp; 대표이사 &nbsp; {D.CEO}</span><span class="seal">(인)</span></div></div>
<div class="to">{e(D.CLIENT)} 귀중</div>
</body></html>"""


def company_info():
    return f"""<table class="info">
<tr><th>업체명</th><td>{D.COMPANY}</td><th>대표자</th><td>{D.CEO}</td></tr>
<tr><th>본사 소재지</th><td colspan="3">{D.ADDRESS}</td></tr>
<tr><th>담당자</th><td colspan="3">{D.MANAGER[1]} {D.MANAGER[0]} · {D.MANAGER[2]} · {D.EMAIL}</td></tr>
</table>"""


# ============================================================ 8) 행사 실적
def doc8():
    def rows_of(recs, start=1):
        return "".join(
            f'<tr><td>{i}</td><td>{d}</td><td class="l">{e(nm)}</td><td>{e(reg)}</td><td class="r">{n:,}</td>'
            f'<td style="white-space:nowrap">입주박람회·공동구매 주관</td><td>별첨 1</td></tr>'
            for i, (d, nm, reg, n) in enumerate(recs, start))
    sale = [r for r in D.RECORDS if r[1] not in D.LEASE_RECORDS]
    lease = [r for r in D.RECORDS if r[1] in D.LEASE_RECORDS]
    total = sum(r[3] for r in D.RECORDS)
    head = """<thead><tr><th style="width:5%">No</th><th style="width:10%">주관 시기</th><th>단지명</th><th style="width:10%">지역</th>
<th style="width:10%">세대수</th><th style="width:24%">수행 내용</th><th style="width:9%">증빙</th></tr></thead>"""
    lease_tbl = (f'<table class="t"><tbody>{rows_of(lease, len(sale) + 1)}'
                 '</tbody></table>') if lease else \
        '<table class="t"><tbody><tr><td class="l">해당 없음</td></tr></tbody></table>'
    body = f"""<style>.t td{{padding:3pt 6pt}} h2{{margin:9pt 0 4pt}} .box{{margin-top:8pt;padding:6pt 11pt}} .sign{{margin-top:9pt}} .to{{margin-top:14pt}}</style>
{company_info()}
<h2>1. 일반 분양 아파트 실적</h2>
<p class="note" style="margin:0 0 5pt">기준: 공고일(2026.09.30) 기준 최근 5년(2021.10.01 ~ 2026.09.30), 1,000세대 이상 공동주택 입주박람회·공동구매 주관 실적 (공고 6항 4호).
주관 사실·시기·세대수는 NICE디앤비 CLIP 기업신용평가보고서(평가완료일 2026.06.19) ‘연혁’(별첨 1) 기재 내용과 같습니다.</p>
<table class="t">{head}
<tbody>{rows_of(sale)}
<tr class="sum"><td colspan="4">소계</td><td class="r">{sum(r[3] for r in sale):,}</td><td colspan="2">{len(sale)}건</td></tr>
</tbody></table>
<h2>2. 임대 아파트 실적 (공고 6항 4호 — 별도 구분)</h2>
{lease_tbl}
<div class="box"><b>참가 자격 대비</b> &nbsp; 요건: 1,000세대 이상 입주박람회·공동구매 주관 실적 5회 이상
&nbsp;→&nbsp; 보유: <b>{len(D.RECORDS)}회(분양 {len(sale)} · 임대 {len(lease)}) · 합계 {total:,}세대</b> &nbsp; <span class="ok">충족</span></div>
<h2>3. 별첨 증빙</h2>
<ul class="n">
<li>1. NICE디앤비 CLIP 기업신용평가보고서 ‘연혁’ 발췌 (표지 · 9쪽) — 1매</li>
</ul>
<p style="margin-top:10pt">위 실적은 사실과 다름이 없음을 확인하며, 허위로 확인될 경우 공고 7항에 따른 어떠한 조치도 이의 없이 따르겠습니다.</p>"""
    return page("제출서류 8)", "최근 5년간 1,000세대 이상 행사 실적", body)


# ============================================================ 9) 계약 취소·환불 규정
def doc9():
    arts = [
        ("제1조 (목적)", None,
         f"이 규정은 {D.COMPANY}(이하 ‘주관사’)가 주관하는 동탄2 신도시 신동 A58BL 파라곤3차 입주박람회 및 공동구매(이하 ‘공동구매’)에서 "
         "임차예정자(이하 ‘계약자’)와 참여업체 사이에 체결되는 계약의 계약금·잔금 지급조건과 취소·환불 기준을 정하여 계약자의 권리를 보호함을 목적으로 한다."),
        ("제2조 (적용 범위)", [
            "공동구매를 통해 체결된 모든 품목의 계약에 적용한다. 박람회 현장 계약과 온라인 박람회(폐쇄몰) 계약을 모두 포함한다.",
            "참여업체는 이 규정을 계약서에 반영하고 계약 체결 전에 계약자에게 설명하여야 한다.",
            "브랜드 본사 직영 품목(가전·가구 등)과 사전점검 대행은 각 본사 계약 규정을 따르되, 그 내용을 계약 전에 서면으로 고지하여야 한다.",
        ], None),
        ("제3조 (계약금)", [
            f"계약금은 계약 총액의 <b>{D.DEPOSIT_MAX}% 이하</b>로 한다(계약금 {D.DEPOSIT_MAX}% 상한제).",
            "계약금과 잔금 모두 카드 결제 시 현금가와 <b>동일한 가격</b>을 적용하며, 현금 결제 시 현금영수증을 발행한다.",
        ], None),
        ("제4조 (잔금 지급 조건)", [
            "잔금은 <b>시공·설치가 완료되고 계약자가 확인한 후</b> 지급한다. 제품만 납품하는 품목은 납품·설치 확인 후 지급한다.",
            "판매 실적에 비례한 추가할인(예: 50·100·150세대 계약 시 1·2·3%)은 잔금에서 차감한다.",
            "시공 결과 확인 시 하자·미시공 부분이 있으면 계약자는 해당 부분의 보수가 끝난 후 잔금을 지급할 수 있다.",
        ], None),
        ("제5조 (취소·환불 기준)", [
            "제작·시공(설치) 착수 전에는 <b>100% 해약</b>할 수 있으며, 납부한 계약금 전액을 환불한다. 다만 맞춤 제작 품목은 출고 지시 전까지 참여업체와 협의하여 취소한다.",
            "품목별 취소 가능 기한은 [별표]와 같다. 기한 내 취소 시 납부 금액 전액을 환불한다.",
            "브랜드 가전·가구는 미제작 및 출고 지시 전에는 100% 취소·환불한다.",
            "참여업체가 사전 해피콜을 이행하지 않은 경우, 계약자 미동의 주문제작 건을 포함한 <b>모든 품목은 당일 취소·환불</b>할 수 있다(공급사 100% 귀책).",
            "인테리어는 계약 후 컨셉미팅이 진행된 경우 취소·환불이 제한된다. 참여업체는 이를 계약 전에 서면으로 고지하여야 한다.",
            "취소 기한이 지난 뒤의 취소는 실제 발생한 자재·제작 비용만 공제할 수 있으며, 참여업체는 공제 내역을 서면으로 제시하여야 한다. 주관사는 공제 내역의 적정성을 검토한다.",
            "시공 지연, 계약과 다른 제품·시공, 하자 미보수 등 참여업체 귀책으로 계약을 해지하는 경우에는 기한과 관계없이 납부 금액 전액을 환불한다.",
        ], None),
        ("제6조 (취소 신청 및 환급)", [
            "취소는 참여업체 또는 주관사 콜센터·공식카페 신문고·카카오채널로 신청하며, 문자·메신저 등 기록이 남는 방법으로 한다.",
            "환불금은 취소 확정일로부터 <b>3영업일 이내</b>에 지급하고, 카드 결제분은 같은 기한 안에 승인 취소한다.",
            "주관사는 환불 완료 여부를 계약자에게 확인(해피콜)한다.",
        ], None),
        ("제7조 (불이행 시 조치 및 주관사 책임)", [
            "참여업체가 취소·환불을 지연하거나 거부하면 계약자는 주관사 콜센터에 접수할 수 있다. 주관사는 사실을 확인한 뒤 계약자에게 피해 금액을 <b>먼저 보상</b>하고, 참여업체와는 계약 조항에 따라 정산한다(A/S 이행각서 [별지#3] 준용).",
            "불이행 업체에는 ① 홍보정지 ② 총액 10% 배상 ③ 자격박탈 및 전 계약 이관의 3단계 패널티를 부과한다.",
            "참여업체가 도산한 경우 동종업체로 사후관리를 이관하고, 그 비용은 주관사가 100% 부담한다.",
            "주관사의 보상 재원으로 하자 예치금 현금 1억원(임예협·주관사 공동통장)과 이행보증보험(2년·10억원)을 둔다.",
        ], None),
        ("제8조 (가격 보호 — 최저가 차액 10배 보상)", [
            "공동구매 품목과 브랜드·모델명이 같은 새 제품이 박람회 개최일부터 계약 후 7일까지 동탄·화성·오산 지역 오프라인 매장에서 "
            "더 낮은 정상 판매가로 판매된 사실이 견적서·영수증으로 확인되면, 참여업체는 차액의 10배를 보상하고 판매가를 조정한다.",
            "온라인·홈쇼핑 판매, 시공 품목, 카드 청구할인·사은품·결합할인, 전시·리퍼 상품, 법인 특판, 한정 수량 행사가는 비교 대상에서 제외한다.",
            "계약자는 주관사 콜센터에 접수하고, 주관사는 사실 확인 후 7일 이내에 보상이 이행되도록 관리한다.",
        ], None),
        ("제9조 (고지)", None,
         "주관사는 이 규정을 박람회장·온라인 박람회·임차예정자협의회 카페에 게시하고, 모든 공동구매 계약서에 첨부한다."),
        ("제10조 (효력)", None,
         "이 규정은 협약 체결일부터 협약 종료일(입주 후 1년)까지 체결된 계약에 적용하며, 협약 종료 후에도 해당 계약의 이행·보증 기간 동안 효력을 가진다."),
    ]
    out = []
    for h, items, text in arts:
        if items:
            lis = "".join(f"<li>{'①②③④⑤⑥⑦⑧'[i]} {x}</li>" for i, x in enumerate(items))
            out.append(f'<div class="art"><h3>{h}</h3><ol>{lis}</ol></div>')
        else:
            out.append(f'<div class="art"><h3>{h}</h3><p>{e(text)}</p></div>')
    table = f"""<h2>[별표] 품목별 취소 가능 기한 (시공일 기준)</h2>
<table class="t"><thead><tr><th style="width:24%">취소 가능 기한</th><th>품목</th></tr></thead><tbody>
<tr><td class="k" style="text-align:center">시공일 7일 전까지</td><td class="l">{e(D.CANCEL_7)}</td></tr>
<tr><td class="k" style="text-align:center">시공일 15일 전까지</td><td class="l">시공 품목 — {e(D.CANCEL_15)}</td></tr>
<tr><td class="k" style="text-align:center">출고 지시 전까지</td><td class="l">{e(D.CANCEL_SHIP)}</td></tr>
<tr><td class="k" style="text-align:center">당일 취소 가능</td><td class="l">사전 해피콜 미이행 시 모든 품목</td></tr>
</tbody></table>
<p class="note">※ 품목 구성은 임차예정자협의회 수요조사 결과에 따라 확정되며, 추가 품목의 기한은 성격이 같은 품목의 기한을 따른다.</p>"""
    summary = f"""<div class="box"><b>핵심 요약</b> &nbsp; 계약금 {D.DEPOSIT_MAX}% 이하 · 현금·카드 동일가 · 잔금은 시공·설치 확인 후 ·
제작·시공 전 100% 해약(맞춤 제작은 출고 전 업체 협의) · 환불 3영업일 이내 · 업체 불이행 시 주관사 선보상</div>"""
    return page("제출서류 9)", "공동구매 계약 취소·환불 규정", summary + "".join(out) + table)


def to_pdf(html_path, pdf_path):
    exe = find_chrome()
    if not exe:
        print("크롬/엣지를 찾지 못해 PDF 생략")
        return
    subprocess.run([exe, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=8000", f"--print-to-pdf={pdf_path}", pathlib.Path(html_path).as_uri()],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    for name, fn in [("08_최근5년_1000세대이상_행사실적", doc8), ("09_계약취소_환불규정", doc9)]:
        h = os.path.join(HERE, f"엣지컴퍼니_동탄파라곤3차_{name}.html")
        with open(h, "w", encoding="utf-8") as f:
            f.write(fn())
        p = h[:-5] + ".pdf"
        to_pdf(h, p)
        print("saved", p)


if __name__ == "__main__":
    main()
