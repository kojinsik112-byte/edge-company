"""영주자이 정문 문주 + 잔디 정원 묶음 견적서 (공무팀 제출용).

회장 지시(2026-11-21): 문주·정원 두 공종만 묶어, 원래 금액(공종별 견적 합계)에서 950만 원대로 할인해 제출.
1쪽 = 묶음 요약(공종별 금액 → 묶음 할인 → 최종 금액) / 별첨 = 공종별 세부 견적서 2부(yeongju_build.py 와 같은 양식).
실행: python 경관조명/tools/yeongju_package.py
"""
from __future__ import annotations

import html
import sys
from pathlib import Path

import fitz  # PyMuPDF

sys.path.insert(0, str(Path(__file__).parent))
import yeongju_build as yb  # noqa: E402

PACKAGE_SUPPLY = 9_500_000  # 묶음 최종 공급가액(부가세 별도) — 회장 '950만원대로 할인'
KEYS = ["2_겨울빛의문_정문문주", "3_별빛이머무는정원"]
TO = "영주자이 시그니처 현장 공무팀 귀중"
NAME = "(엣지컴퍼니) 영주자이 정문 문주·정원 윈터라이팅 견적서_261121"
DESC = {
    "2_겨울빛의문_정문문주": "고드름 커튼 32m · 네온 라인 · 눈꽃·별 모티브 · 원뿔 트리 2 · 소나무 5그루 은하수",
    "3_별빛이머무는정원": "사슴 2 · 토끼 2 · 대형 별 · 빛 구슬 2 · 꽂이형 별 6 · 나무 행잉 9",
}

CSS = yb.CSS + """
.amount .was { font-size: 9pt; color: #9aa3b2; text-align: right; }
.amount .was s { margin-left: 1.5mm; }
.badge { display: inline-block; background: #b8913a; color: #fff; font-size: 7.4pt; letter-spacing: 1px; padding: 0.5mm 2.2mm; margin-left: 2mm; vertical-align: 1px; }
tr.disc td { color: #9a6b12; font-weight: 600; }
.attach { margin-top: 2mm; font-size: 8.2pt; color: #4a5563; }
.optline { margin-top: 2.5mm; border: 0.8px dashed #c9b98f; padding: 2mm 4mm; font-size: 8.4pt; display: flex; justify-content: space-between; align-items: center; }
.optline .eb { margin-right: 3mm; }
.optline b { font-family: "Noto Serif KR", serif; font-size: 10pt; white-space: nowrap; }
@page { size: A4; margin: 10mm 13mm 8mm; }
.mast h1 { font-size: 22pt; }
.project { margin: 3mm 0 2.5mm; } .project .th { font-size: 14pt; }
.info { gap: 5mm; } .info td { padding: 0.8mm 0; }
.amount { margin: 3mm 0 2mm; padding: 2.5mm 5mm; }
.sect { margin-top: 3.5mm; } .sect h3 { margin: 0.4mm 0 1.2mm; font-size: 10.5pt; }
table.q td { padding: 1.2mm 1.8mm; } tr.grand td { padding-top: 1.6mm; }
ol.terms li { padding: 0.6mm 0 0.6mm 7mm; font-size: 8.2pt; } ol.terms li::before { top: 0.6mm; }
.sign { margin-top: 3mm; line-height: 1.7; } .foot { margin-top: 3mm; }
.mast { padding-bottom: 2.5mm; } .info td { padding: 0.6mm 0; }
.endrow { display: flex; justify-content: space-between; align-items: flex-end; margin-top: 2.5mm; page-break-inside: avoid; }
.endrow .attach { margin: 0 0 1.5mm; max-width: 52%; }
.endrow .sign { margin-top: 0; line-height: 1.6; } .endrow .sig { font-size: 21pt; }
.foot { margin-top: 2mm; padding-top: 1.2mm; } ol.terms li { padding: 0.45mm 0 0.45mm 7mm; } .optline { margin-top: 2mm; padding: 1.6mm 4mm; }
"""


def summary_html(qs: list[dict]) -> tuple[str, dict]:
    ts = [yb.calc(q) for q in qs]
    listed = sum(t["supply"] for t in ts)
    supply = PACKAGE_SUPPLY
    disc = listed - supply
    vat = supply // 10
    removal = [(q, yb.calc(q["철거"])["supply"]) for q in qs if q.get("철거")]
    co = yb.COMPANY
    sup = "".join(f'<tr><td class="k">{k}</td><td>{html.escape(v)}</td></tr>' for k, v in co.items())

    def theme(q):
        th, _, sub = q["title"].partition(" — ")
        return th[2:], sub

    rows = []
    for q, t in zip(qs, ts):
        nm, sub = theme(q)
        rows.append(f'<tr><td><b>「{nm}」</b> {sub}<div class="spec">{DESC[q["key"]]}</div></td>'
                    f'<td class="n">{t["supply"]:,}</td></tr>')
    rm_txt = " · ".join(f"{theme(q)[1]} {v:,}" for q, v in removal)
    terms = [
        "묶음 할인은 두 공종을 함께 발주하고 같은 기간에 설치할 때 적용하며, 한 공종만 발주하시면 별첨 공종별 금액을 적용합니다.",
        "별첨 견적서 2부의 품목·수량·단가 기준이며, 현장 실측 후 정산합니다.",
        "석재·경계석에 타공하지 않고 수목은 못·스테이플 없이 시공하며, 기존 조명·사인·조형물은 그대로 유지합니다.",
        "점등 기간 중 불량 조명은 무상 교체합니다. 1차 전원은 발주처 제공 조건이며, 전기요금은 제외합니다.",
        "공정: 발주 후 자재 입고 약 3주, 현장 설치 3일(정문 문주 2일 · 잔디 정원 1일).",
        "결제: 계약금 50% / 설치 완료 후 50%.",
    ]
    body = f'''<div class="mast"><div><div class="eb">QUOTATION</div><h1>견 적 서</h1></div>
<div class="brand"><b>{co["상호"]}</b><span>{co["면허"]}</span></div></div><div class="rule2"></div>
<div class="project"><div class="eb">PROJECT · PACKAGE</div><div class="pj">영주자이 시그니처 윈터라이팅 — 정문 문주 · 잔디 정원 묶음</div>
<div class="th"><em>「겨울빛의 문」</em> + <em>「별빛이 머무는 정원」</em></div></div>
<div class="info"><table>
<tr><td class="k">수신</td><td class="to">{TO}</td></tr>
<tr><td class="k">건명</td><td>영주자이 시그니처 정문 문주·잔디 정원 윈터라이팅 설치 (묶음)</td></tr>
<tr><td class="k">견적일</td><td>{yb.DATE}</td></tr>
<tr><td class="k">유효기간</td><td>견적일로부터 15일</td></tr></table>
<div class="sup"><table>{sup}</table></div></div>
<div class="amount"><div><div class="lb">견적 금액 · 부가세 별도<span class="badge">묶음 특별 할인</span></div>
<div class="kr">금 {yb.korean_won(supply)}원정</div></div>
<div><div class="was">공종별 합계<s>₩ {listed:,}</s></div><div class="big">₩ {supply:,}</div><div class="vat">부가세 포함 ₩ {supply + vat:,}</div></div></div>
<div class="sect"><div class="eb">SUMMARY</div><h3>공종별 금액과 묶음 할인 <span class="spec">부가세 별도 · 단위 원</span></h3>
<table class="q"><tr><th style="width:78%">공종 · 내용</th><th class="n">금액</th></tr>
{"".join(rows)}
<tr class="tot"><td>공종별 견적 합계</td><td class="n">{listed:,}</td></tr>
<tr class="disc"><td>묶음 특별 할인 <span class="spec">두 공종 동시 발주·동시 설치 조건</span></td><td class="n">−{disc:,}</td></tr>
<tr class="grand"><td>공급가액 <span class="spec">부가세 별도</span></td><td class="n">{supply:,}</td></tr>
<tr class="calc"><td>부가가치세 10%</td><td class="n">{vat:,}</td></tr>
<tr class="grand2"><td>합계 <span class="spec">부가세 포함</span></td><td class="n">{supply + vat:,}</td></tr></table></div>
<div class="optline"><div><span class="eb">OPTION</span>선택 항목 — 시즌 종료 후 철거 <span class="spec">({rm_txt} · 할인 미적용 · 부가세 별도)</span></div>
<b>₩ {sum(v for _, v in removal):,}</b></div>
<div class="sect"><div class="eb">TERMS</div><h3>견적 조건</h3><ol class="terms">{"".join(f"<li>{html.escape(x)}</li>" for x in terms)}</ol></div>
<div class="endrow"><div class="attach">별첨 — 공종별 세부 견적서 2부<br>「겨울빛의 문」 정문 문주 · 「별빛이 머무는 정원」 잔디 정원</div>
<div class="sign">위와 같이 견적합니다.<br>{yb.DATE}<br><b>{co["상호"]}</b> 대표 {co["대표"]}<span class="sig">{co["대표"]}</span></div></div>
<div class="foot">{co["상호"]} · {co["면허"]} · 사업자등록번호 {co["사업자등록번호"]} · {co["주소"]} · ☎ {co["전화"]}</div>'''
    doc = (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{NAME}</title>'
           f'<style>{CSS}</style></head><body>{body}</body></html>')
    return doc, dict(listed=listed, disc=disc, supply=supply, vat=vat, removal=sum(v for _, v in removal))


def main():
    qs = [{q["key"]: q for q in yb.QUOTES}[k] for k in KEYS]
    hdir = yb.OUT / "_html"
    hdir.mkdir(parents=True, exist_ok=True)
    doc, n = summary_html(qs)
    hp = hdir / "묶음_문주정원_요약.html"
    hp.write_text(doc, encoding="utf-8")
    parts = [hdir / "묶음_문주정원_요약.pdf"]
    yb.to_pdf(hp, parts[0])
    for q in qs:  # 별첨 세부 견적서는 최신 데이터로 다시 생성
        qp = hdir / f"견적서_{q['key']}.html"
        qp.write_text(yb.quote_html(q), encoding="utf-8")
        parts.append(hdir / f"묶음_별첨_{q['key']}.pdf")
        yb.to_pdf(qp, parts[-1])
    out = fitz.open()
    for p in parts:
        with fitz.open(p) as d:
            out.insert_pdf(d)
    final = yb.OUT / f"{NAME}.pdf"
    out.save(final)
    pages = out.page_count
    out.close()
    first = fitz.open(parts[0]).page_count
    print(f"공종별 합계 {n['listed']:,} → 할인 {n['disc']:,} ({n['disc'] / n['listed']:.1%}) → 공급가 {n['supply']:,} "
          f"(VAT포함 {n['supply'] + n['vat']:,}) / 철거 {n['removal']:,}")
    print(f"요약 {first}쪽 · 전체 {pages}쪽 -> {final}")


if __name__ == "__main__":
    main()
