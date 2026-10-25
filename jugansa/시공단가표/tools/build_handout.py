"""입주민 배포용 A4 시공 단가표 HTML. 같은 데이터(sigong.json)로 artifact용(본문만)과 인쇄용(완전한 문서) 두 벌 생성."""
import json, sys, html

DATA, OUT_ART, OUT_FULL = sys.argv[1], sys.argv[2], sys.argv[3]
data = json.load(open(DATA))
E = html.escape


def price(v):
    if v is None:
        return '<span class="tbd">현장 제시</span>'
    if isinstance(v, (int, float)):
        return f'<b>{int(v):,}</b><i>만원</i>'
    return f'<span class="txt">{E(v)}</span>'


rows = []
for g in data["groups"]:
    rows.append(f'<tr class="grp"><th colspan="4">{E(g["name"])}</th></tr>')
    items = g["items"]
    for i, it in enumerate(items):
        first = i == 0 or items[i - 1]["item"] != it["item"]
        span = 1
        while i + span < len(items) and items[i + span]["item"] == it["item"]:
            span += 1
        opt = f'<small>{E(it["option"])}</small>' if it["option"] else ""
        nd = f'<small>{E(it["normal_desc"])}</small>' if it.get("normal_desc") else ""
        if it["premium"] is not None or it["premium_desc"]:
            desc = f'<small>{E(it["premium_desc"])}</small>' if it["premium_desc"] else ""
            prem = f'<div class="p">{price(it["premium"]) if it["premium"] is not None else ""}</div>{desc}'
        else:
            prem = '<div class="p"><span class="tbd">현장 제시</span></div>'
        item_td = (f'<td class="item" rowspan="{span}">{E(it["item"])}</td>' if span > 1 else
                   f'<td class="item">{E(it["item"])}</td>') if first else ""
        rows.append(
            f'<tr>{item_td}'
            f'<td class="scope">{E(it["scope"])}{opt}</td>'
            f'<td class="pr"><div class="p">{price(it["normal"])}</div>{nd}</td>'
            f'<td class="pr prem">{prem}</td></tr>')
table = "\n".join(rows)

STYLE = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
  /* 종이 한 장 컨셉: 화면에서는 회색 책상 위 A4, 인쇄하면 A4 그대로. 단일 테마(종이). */
  :root {
    --navy:#12345e; --sky:#8fc0f0; --ink:#141414; --mute:#5b6676; --line:#b9c4d2; --zebra:#f6f8fb;
    --desk:#e6e9ee; --paper:#ffffff; --tint:#e8f1fb;
    --sans:'Noto Sans KR','맑은 고딕','Malgun Gothic','Apple SD Gothic Neo',sans-serif;
    color-scheme: light;
  }
  @page { size: A4 portrait; margin: 8mm; }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--desk); color:var(--ink); font-family:var(--sans);
         -webkit-print-color-adjust:exact; print-color-adjust:exact;
         padding-block: 16px;
         padding-left: max(16px, env(safe-area-inset-left, 0px));
         padding-right: max(16px, env(safe-area-inset-right, 0px)); }
  .page { width:100%; max-width:198mm; margin:0 auto; background:var(--paper);
          padding:6mm 6mm 5mm; box-shadow:0 4px 14px rgba(18,52,94,.14); }
  .head { background:var(--navy); color:#fff; padding:12px 14px; border-radius:2px;
          display:flex; flex-wrap:wrap; gap:8px 16px; align-items:flex-end; justify-content:space-between; }
  .head h1 { margin:0; font-size:22px; font-weight:900; letter-spacing:-.4px; text-wrap:balance; }
  .head p { margin:4px 0 0; font-size:12px; font-weight:500; opacity:.92; }
  .box { background:#fff; color:var(--navy); font-weight:900; font-size:12px; padding:5px 10px;
         border-radius:2px; white-space:nowrap; }
  .box u { text-decoration:none; display:inline-block; min-width:90px; border-bottom:2px solid var(--navy); }
  .legend { display:flex; flex-wrap:wrap; gap:6px 14px; margin:10px 2px 6px; font-size:11.5px; color:var(--mute); }
  .legend b { color:var(--navy); }
  .tw { overflow-x:auto; }
  table { width:100%; border-collapse:collapse; min-width:520px; font-variant-numeric:tabular-nums; }
  thead th { background:var(--navy); color:#fff; font-size:12.5px; font-weight:700; padding:7px 6px;
             border:1px solid var(--navy); }
  tr.grp th { background:var(--tint); color:var(--navy); text-align:left; font-size:12px; font-weight:900;
              letter-spacing:.06em; padding:5px 8px; border:1px solid var(--line); }
  td { border:1px solid var(--line); padding:6px 8px; vertical-align:middle; font-size:12.5px; line-height:1.45; }
  td.item[rowspan] { background:var(--paper); }
  td.item { width:15%; font-weight:900; font-size:13.5px; color:var(--navy); white-space:nowrap; }
  td.scope { width:37%; }
  td small { display:block; color:var(--mute); font-size:11px; margin-top:1px; }
  td.pr { width:19%; text-align:center; }
  td.prem { width:29%; }
  td.pr .p b { font-size:17px; font-weight:900; }
  td.pr .p i { font-style:normal; font-size:11.5px; font-weight:700; margin-left:1px; }
  td.prem .p b { color:var(--navy); }
  td.pr .txt { font-size:12.5px; font-weight:900; }
  .tbd { font-size:12px; font-weight:700; color:var(--mute); }
  .dash { color:var(--mute); }
  .special { margin-top:10px; border:2px solid var(--navy); border-radius:2px; padding:9px 12px;
             display:flex; flex-wrap:wrap; gap:4px 16px; align-items:center; }
  .special strong { color:var(--navy); font-size:14px; font-weight:900; }
  .special span { font-size:12.5px; }
  .notes { margin:9px 2px 0; padding:0; list-style:none; font-size:11px; color:var(--mute); line-height:1.6; }
  .foot { margin-top:8px; display:flex; justify-content:space-between; flex-wrap:wrap; gap:4px;
          font-size:11px; color:var(--mute); border-top:1px solid var(--line); padding-top:6px; }
  .foot b { color:var(--navy); }
  @media (max-width:560px) {
    .page { padding:12px 10px; }
    .head h1 { font-size:19px; }
    .tw { overflow:visible; }
    table, tbody { display:block; min-width:0; }
    thead { display:none; }
    tbody tr { display:grid; grid-template-columns:1fr 1fr; gap:0 6px; border:1px solid var(--line); border-top:none; }
    tr.grp { display:block; border:none; margin-top:8px; }
    tr.grp th { display:block; border:1px solid var(--line); }
    td { border:none; padding:5px 8px; width:auto !important; }
    td.item, td.scope { grid-column:1 / -1; }
    td.item { padding-bottom:0; font-size:15px; background:var(--paper); }
    td.pr { background:var(--zebra); border-radius:2px; margin:0 0 8px; }
    td.pr:first-of-type, td.pr:not(.prem) { margin-left:8px; }
    td.prem { margin-right:8px; }
    td.pr::before { content:"일반"; display:block; font-size:10.5px; font-weight:700; color:var(--mute); }
    td.prem::before { content:"프리미엄"; }
  }
  @media print {
    body { background:#fff; padding:0; }
    .page { max-width:none; width:auto; box-shadow:none; padding:0; }
    table { min-width:0; }
    tr { break-inside:avoid; }
  }
</style>
"""

BODY = f"""
<div class="page">
  <header class="head">
    <div>
      <h1>입주박람회 시공 단가표</h1>
      <p>전용 84㎡(34평) 기준 · 박람회 현장 계약가</p>
    </div>
    <div class="box">단지 <u>&nbsp;</u></div>
  </header>
  <div class="legend">
    <span><b>일반</b> 기본 시공 범위</span>
    <span><b>프리미엄</b> 상위 자재·범위 확장</span>
    <span><b>줄눈</b> 일반 = 폴리우레아 · 프리미엄 = 케라폭시</span>
  </div>
  <div class="tw">
  <table>
    <thead><tr><th>품목</th><th>시공 범위</th><th>일반</th><th>프리미엄</th></tr></thead>
    <tbody>
{table}
    </tbody>
  </table>
  </div>
  <section class="special">
    <strong>가전 · 가구 · 안마의자</strong>
    <span>업체별 대표 특가 1~2개 사전 공개 · 그 외 전 품목은 박람회 현장 공개</span>
  </section>
  <ul class="notes">
    <li>※ 표기 금액은 84㎡ 기준 대표 시공가이며 평형·현장 여건·자재에 따라 달라질 수 있습니다.</li>
    <li>※ 추가 범위·옵션과 '현장 제시' 항목은 박람회 현장에서 업체별로 안내합니다. 최종 금액은 업체 견적서 기준입니다.</li>
  </ul>
  <div class="foot"><span>주관 <b>㈜엣지컴퍼니</b></span><span>v1 초안 · 2026.10</span></div>
</div>
"""

HEAD_META = '<title>입주박람회 시공 단가표</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n'
open(OUT_ART, "w").write(HEAD_META + STYLE + BODY)
open(OUT_FULL, "w").write(
    '<!DOCTYPE html>\n<html lang="ko">\n<head>\n<meta charset="UTF-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    '<title>입주박람회 시공 단가표</title>\n' + STYLE + '</head>\n<body>\n' + BODY + '</body>\n</html>\n')
print("ok")
