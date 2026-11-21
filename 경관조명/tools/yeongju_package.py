"""영주자이 정문 문주 + 잔디 정원 묶음 견적서 (공무팀 제출용).

회장 지시(2026-11-21): 문주·정원 두 공종만 묶어, 원래 금액(공종별 견적 합계)에서 950만 원대로 할인해 제출.
회장 지시: 문주·정원 그림과 메인 사진도 넣을 것.
구성 = 표지(메인 사진·대표컷) → 「겨울빛의 문」 1쪽 → 「별빛이 머무는 정원」 1쪽 → 묶음 요약 견적 1쪽
       → 별첨 공종별 세부 견적서 2부(yeongju_build.py 와 같은 양식).
사진은 제안서 빌더(yeongju_proposal.py)가 만든 수정본(오타·제목 통일)과 품목 크롭을 그대로 쓴다 — 제안서를 먼저 빌드할 것.
실행: python 경관조명/tools/yeongju_package.py
"""
from __future__ import annotations

import html
import sys
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import yeongju_build as yb  # noqa: E402
import yeongju_proposal as yp  # noqa: E402

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


# ───────────── 앞부분: 표지 + 테마 2쪽 (A4 세로) ─────────────
PAGES = {  # 테마 이름 → (페이지 머리 영문, 대표컷, 다른 각도 3컷)
    "겨울빛의 문": ("GATE", "겨울빛의 문", ["자이 게이트의 별빛 조명-3", "별빛의 초대, 영주자이 입구-2", "우측 시점의 별빛 입구-4"]),
    "별빛이 머무는 정원": ("GARDEN", "별빛이 머무는 정원 야경-2", ["나무 곁의 별빛 정원-4", "별빛이 머무는 정원, 새로운 각도-3", "초승달 아래 별빛 정원-1"]),
}
COVER_PAIR = [("겨울빛의 문", "별빛이 머무는 정문 야경-1", "정문 문주"), ("별빛이 머무는 정원", "나무 곁의 별빛 정원-4", "잔디 정원")]

INTRO_CSS = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Noto Sans KR", "Malgun Gothic", sans-serif; color: #1d2430; }
section { width: 210mm; height: 297mm; overflow: hidden; position: relative; page-break-after: always; background: #fbfaf7; }
.eb { font-size: 7.6pt; letter-spacing: 3.2px; color: #b8913a; font-weight: 500; }
.cvtop { padding: 19mm 16mm 8mm; }
.cvtop h1 { font-family: "Noto Serif KR", serif; font-weight: 600; font-size: 29pt; line-height: 1.32; margin: 4mm 0 4mm; letter-spacing: 1px; }
.cvsub { font-size: 10.6pt; color: #4a5563; margin: 0; line-height: 1.6; }
.cvsub em { font-style: normal; color: #b8913a; font-weight: 600; }
.cvmain { width: 210mm; height: 118.1mm; object-fit: cover; display: block; }
.cvcap { padding: 2.5mm 16mm 0; font-size: 8.2pt; color: #8a7a55; }
.cvpair { display: grid; grid-template-columns: 1fr 1fr; gap: 5mm; padding: 7mm 16mm 0; }
.cvpair figure { margin: 0; }
.cvpair img { width: 100%; height: 49mm; object-fit: cover; display: block; }
.cvpair figcaption { font-size: 9pt; color: #4a5563; margin-top: 2mm; }
.cvpair figcaption b { font-family: "Noto Serif KR", serif; font-size: 11pt; color: #1d2430; margin-right: 1.5mm; }
.cvfoot { position: absolute; left: 16mm; right: 16mm; bottom: 14mm; display: flex; justify-content: space-between; align-items: flex-end;
          border-top: 1.4px solid #b8913a; padding-top: 4mm; font-size: 9pt; color: #4a5563; line-height: 1.7; }
.cvfoot .to { font-size: 10.5pt; font-weight: 700; color: #1d2430; }
.cvfoot .brand { text-align: right; } .cvfoot .brand b { font-family: "Noto Serif KR", serif; font-size: 14pt; color: #1d2430; }
.tp { padding: 13mm 13mm 11mm; }
.tphd { display: flex; justify-content: space-between; align-items: baseline; border-bottom: 0.8px solid #d9cfb8; padding-bottom: 2.5mm; margin-bottom: 4.5mm; }
.tphd .br { font-size: 8pt; color: #9aa3b2; }
.hero { width: 100%; height: 103.5mm; object-fit: cover; display: block; }
.tpbody { display: grid; grid-template-columns: 62mm 1fr; gap: 7mm; margin: 5.5mm 0 5mm; }
.tag { display: inline-block; font-size: 7.6pt; color: #fff; background: #b8913a; padding: 0.4mm 2.4mm; }
.tpbody h2 { font-family: "Noto Serif KR", serif; font-size: 21pt; font-weight: 600; margin: 2mm 0 1mm; }
.where { font-size: 8.2pt; color: #6b7280; }
.tg { font-family: "Noto Serif KR", serif; font-size: 10.5pt; color: #8a6d2f; margin: 3mm 0 0; line-height: 1.5; }
.concept { font-size: 9.6pt; line-height: 1.75; margin: 0 0 2.5mm; color: #374151; }
.tpbody ul { margin: 0; padding-left: 4.5mm; } .tpbody li { font-size: 9pt; line-height: 1.65; color: #374151; }
.gal3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 3.5mm; }
.gal3 img { width: 100%; height: 33mm; object-fit: cover; display: block; }
.ithd { margin: 5mm 0 2.5mm; display: flex; align-items: baseline; gap: 3mm; }
.ithd h3 { font-family: "Noto Serif KR", serif; font-size: 11pt; margin: 0; font-weight: 600; }
.ithd span { font-size: 7.6pt; color: #9aa3b2; }
.its { display: grid; gap: 3mm; }
.it { background: #fff; border: 0.6px solid #e6e1d6; }
.it img { width: 100%; height: 22mm; object-fit: cover; display: block; background: #0b1020; }
.it div { padding: 1.6mm 2mm 2mm; } .it b { display: block; font-size: 8.2pt; line-height: 1.35; } .it span { font-size: 7.6pt; color: #b8913a; font-weight: 600; }
.gal3 img { height: 41mm; } .it img { height: 33mm; } .ithd { margin: 7mm 0 3mm; } .tpbody { margin: 6.5mm 0 6.5mm; }
.tpfoot { position: absolute; left: 13mm; right: 13mm; bottom: 9mm; font-size: 7.2pt; color: #9aa3b2; text-align: center; border-top: 0.6px solid #e2dccd; padding-top: 2mm; }
"""


def intro_html(img_dir: Path) -> str:
    img_dir.mkdir(parents=True, exist_ok=True)

    def jpg(src: Path, name: str) -> str:
        dst = img_dir / f"{name}.jpg"
        Image.open(src).convert("RGB").save(dst, quality=86)
        return dst.as_uri()

    def shot(theme: str, stem: str) -> str:
        return jpg(yp.FIXED / theme / f"{stem}.png", f"{theme}_{stem}".replace(" ", "_").replace(",", ""))

    co = yb.COMPANY
    cover = yp.OUT / "표지.png"
    pair = "".join(f'<figure><img src="{shot(t, s)}"><figcaption><b>「{t}」</b>{w}</figcaption></figure>' for t, s, w in COVER_PAIR)
    pages = [f'''<section class="cv"><div class="cvtop"><div class="eb">YEONGJU Xi SIGNATURE · WINTER LIGHTING</div>
<h1>영주자이의 겨울,<br>빛으로 맞이합니다</h1>
<p class="cvsub">정문 문주 <em>「겨울빛의 문」</em>과 잔디 정원 <em>「별빛이 머무는 정원」</em> — 제안 및 견적</p></div>
<img class="cvmain" src="{jpg(cover, "cover")}">
<div class="cvcap">영주자이 시그니처 경관조명 전체 구상 — 이번 제안은 정문 문주와 잔디 정원입니다.</div>
<div class="cvpair">{pair}</div>
<div class="cvfoot"><div><span class="to">{TO}</span><br>{yb.DATE}</div>
<div class="brand"><b>{co["상호"]}</b><br>{co["면허"]} · ☎ {co["전화"]}</div></div></section>''']
    themes = {t["name"]: t for t in yp.THEMES}
    for name, (en, hero, gal) in PAGES.items():
        t = themes[name]
        pts = "".join(f"<li>{html.escape(x)}</li>" for x in t["points"])
        gal_html = "".join(f'<img src="{shot(name, s)}">' for s in gal)
        items = "".join(f'<div class="it"><img src="{(yp.IMG / f"{c}.jpg").as_uri()}"><div><b>{html.escape(n)}</b><span>{html.escape(q)}</span></div></div>'
                        for c, n, _, q in t["items"])
        pages.append(f'''<section class="tp"><div class="tphd"><span class="eb">WINTER LIGHTING · {en}</span><span class="br">{co["상호"]}</span></div>
<img class="hero" src="{shot(name, hero)}">
<div class="tpbody"><div><span class="tag">{t["kind"]}</span><h2>{html.escape(name)}</h2><div class="where">{html.escape(t["where"])}</div>
<p class="tg">{html.escape(t["tagline"])}</p></div>
<div><p class="concept">{html.escape(t["concept"])}</p><ul>{pts}</ul></div></div>
<div class="gal3">{gal_html}</div>
<div class="ithd"><h3>구성 품목</h3><span>수량·규격은 별첨 견적서 기준</span></div>
<div class="its" style="grid-template-columns: repeat({len(t["items"])}, 1fr)">{items}</div>
<div class="tpfoot">{co["상호"]} · {co["면허"]} · ☎ {co["전화"]} · 이미지는 설치 예상 연출이며 실제 시공과 차이가 있을 수 있습니다.</div></section>''')
    return (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{NAME}</title>'
            f'<style>{INTRO_CSS}</style></head><body>{"".join(pages)}</body></html>')


def main():
    qs = [{q["key"]: q for q in yb.QUOTES}[k] for k in KEYS]
    hdir = yb.OUT / "_html"
    hdir.mkdir(parents=True, exist_ok=True)
    ip = hdir / "묶음_문주정원_앞부분.html"
    ip.write_text(intro_html(hdir / "pkg_img"), encoding="utf-8")
    intro_pdf = hdir / "묶음_문주정원_앞부분.pdf"
    yb.to_pdf(ip, intro_pdf)
    doc, n = summary_html(qs)
    hp = hdir / "묶음_문주정원_요약.html"
    hp.write_text(doc, encoding="utf-8")
    summary_pdf = hdir / "묶음_문주정원_요약.pdf"
    yb.to_pdf(hp, summary_pdf)
    parts = [intro_pdf, summary_pdf]
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
    with fitz.open(intro_pdf) as a, fitz.open(summary_pdf) as b:
        first = f"앞부분 {a.page_count}쪽 · 요약 {b.page_count}"
    print(f"공종별 합계 {n['listed']:,} → 할인 {n['disc']:,} ({n['disc'] / n['listed']:.1%}) → 공급가 {n['supply']:,} "
          f"(VAT포함 {n['supply'] + n['vat']:,}) / 철거 {n['removal']:,}")
    print(f"요약 {first}쪽 · 전체 {pages}쪽 -> {final}")


if __name__ == "__main__":
    main()
