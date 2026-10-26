"""업체별 시공 단가표 HTML — 재계산된 엑셀(업체별_작성용·가전가구_특가)을 읽어 생성.
사용: build_vendor_page.py <xlsx> <sigong.json> <out_dir>
  → 검토용(업체명 포함): vendor_review.html(게시용 본문) / 업체별_검토용.html(완전 문서)
  → 공개용(코드만):     vendor_public.html / 입주박람회_시공단가표_업체별.html
"""
import json, sys, html, os
import openpyxl

XLSX, DATA, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
E = html.escape
data = json.load(open(DATA))
item_group = {it["item"]: g["name"] for g in data["groups"] for it in g["items"]}
group_order = [g["name"] for g in data["groups"]]

wb = openpyxl.load_workbook(XLSX, data_only=True)
ws = wb["업체별_작성용"]
items = {}  # item -> list of vendor dicts (엑셀 행 순서 유지)
for r in range(5, ws.max_row + 1):
    v = [ws.cell(r, c).value for c in range(1, 11)]
    if not v[0] or not v[1]:
        continue
    items.setdefault(v[0], []).append(dict(item=v[0], code=v[1], name=v[2] or "", scope=v[3] or "", normal=v[4],
                                           ndesc=v[5] or "", premium=v[6], pdesc=v[7] or "", note=v[8] or "",
                                           check=v[9] or ""))
sp = wb["가전가구_특가"]
special = {}
for r in range(5, sp.max_row + 1):
    v = [sp.cell(r, c).value for c in range(1, 14)]
    if not v[0] or not v[1]:
        continue
    special.setdefault(v[0], []).append(dict(code=v[1], name=v[2] or "", p1=v[3], n1=v[4], s1=v[5], p2=v[8], s2=v[10]))


def price(v):
    if v in (None, ""):
        return '<span class="tbd">현장 제시</span>'
    if isinstance(v, (int, float)):
        return f'<b>{int(v):,}</b><i>만원</i>'
    if str(v).strip() == "-":
        return '<span class="dash">-</span>'
    return f'<span class="txt">{E(str(v))}</span>'


def build(show_names):
    out = []
    for gname in group_order:
        its = [i for i in items if item_group.get(i) == gname]
        if not its:
            continue
        out.append(f'<tr class="grp"><th colspan="{4 if show_names else 3}">{E(gname)}</th></tr>')
        for it in its:
            vs = items[it]
            head = vs[0]
            mats = " · ".join(x for x in (f"일반 {head['ndesc']}" if head["ndesc"] else "",
                                          f"프리미엄 {head['pdesc']}" if head["pdesc"] else "") if x)
            out.append(f'<tr class="ih"><td colspan="{4 if show_names else 3}"><b>{E(it)}</b>'
                       f'<span class="sc">{E(head["scope"])}</span>'
                       f'{f"<small>{E(mats)}</small>" if mats else ""}</td></tr>')
            for v in vs:
                diff = v["scope"] != head["scope"]
                extra = f'<small>{E(v["scope"])}</small>' if diff else ""
                who = f'<td class="vd"><b>{E(v["code"])}</b>{extra}</td>'
                if show_names:
                    flag = ""
                    if v["note"].startswith("직전 행사"):
                        flag = '<em class="chip warn">참가 확인</em>'
                    elif v["check"] in ("미확인", ""):
                        flag = '<em class="chip">가격 확인 전</em>'
                    who += f'<td class="nm">{E(v["name"])}{flag}</td>'
                prem = price(v["premium"])
                out.append(f'<tr class="vr">{who}<td class="pr"><div class="p">{price(v["normal"])}</div></td>'
                           f'<td class="pr prem"><div class="p">{prem}</div></td></tr>')
    # 가전·가구
    sp_rows = []
    for cat, vs in special.items():
        if show_names:
            cells = "".join(f'<li><b>{E(v["code"])}</b> {E(v["name"])}'
                            f'<span>{E(v["p1"]) + " " + (str(v["s1"]) + "만원" if v["s1"] else "") if v["p1"] else "특가 제출 대기"}</span></li>'
                            for v in vs)
        else:
            cells = "".join(f'<li><b>{E(v["code"])}</b>'
                            f'<span>{E(v["p1"]) + " " + (str(v["s1"]) + "만원" if v["s1"] else "") if v["p1"] else "현장 공개"}</span></li>'
                            for v in vs)
        sp_rows.append(f'<div class="spc"><h3>{E(cat)} <small>{len(vs)}곳</small></h3><ul>{cells}</ul></div>')
    return "\n".join(out), "\n".join(sp_rows)


STYLE = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
  /* 종이 A4 컨셉(단일 테마). 품목 머리줄에 공통 범위, 그 아래 업체 A·B·C 한 줄씩. */
  :root {
    --navy:#12345e; --ink:#141414; --mute:#5b6676; --line:#b9c4d2; --zebra:#f6f8fb;
    --desk:#e6e9ee; --paper:#ffffff; --tint:#e8f1fb; --warn:#a4570a; --warnbg:#fdf1e2;
    --sans:'Noto Sans KR','맑은 고딕','Malgun Gothic','Apple SD Gothic Neo',sans-serif;
    color-scheme: light;
  }
  @page { size: A4 portrait; margin: 8mm; }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--desk); color:var(--ink); font-family:var(--sans);
         -webkit-print-color-adjust:exact; print-color-adjust:exact; padding-block:16px;
         padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px)); }
  .page { width:100%; max-width:198mm; margin:0 auto; background:var(--paper); padding:6mm 6mm 5mm;
          box-shadow:0 4px 14px rgba(18,52,94,.14); }
  .head { background:var(--navy); color:#fff; padding:12px 14px; border-radius:2px; display:flex; flex-wrap:wrap;
          gap:8px 16px; align-items:flex-end; justify-content:space-between; }
  .head h1 { margin:0; font-size:22px; font-weight:900; letter-spacing:-.4px; text-wrap:balance; }
  .head p { margin:4px 0 0; font-size:12px; font-weight:500; opacity:.92; }
  .box { background:#fff; color:var(--navy); font-weight:900; font-size:12px; padding:5px 10px; border-radius:2px; white-space:nowrap; }
  .box u { text-decoration:none; display:inline-block; min-width:90px; border-bottom:2px solid var(--navy); }
  .review { margin:10px 0 0; padding:8px 10px; background:var(--warnbg); color:var(--warn); font-size:12px;
            font-weight:700; border-radius:2px; line-height:1.5; }
  .legend { display:flex; flex-wrap:wrap; gap:6px 14px; margin:10px 2px 6px; font-size:11.5px; color:var(--mute); }
  .legend b { color:var(--navy); }
  table { width:100%; border-collapse:collapse; font-variant-numeric:tabular-nums; }
  thead th { background:var(--navy); color:#fff; font-size:12.5px; font-weight:700; padding:7px 6px; border:1px solid var(--navy); }
  tr.grp th { background:var(--navy); color:#fff; text-align:left; font-size:12px; font-weight:900; letter-spacing:.08em;
              padding:5px 8px; border:1px solid var(--navy); }
  tr.ih td { background:var(--tint); padding:6px 8px; border:1px solid var(--line); }
  tr.ih b { color:var(--navy); font-size:14px; font-weight:900; margin-right:8px; }
  tr.ih .sc { font-size:12.5px; font-weight:500; }
  tr.ih small { display:block; color:var(--mute); font-size:11px; margin-top:1px; }
  tr.vr td { border:1px solid var(--line); padding:4px 8px; font-size:12.5px; vertical-align:middle; }
  td.vd { width:22%; }
  td.vd b { font-weight:900; font-size:13px; }
  td.vd small, td.nm small { display:block; color:var(--mute); font-size:11px; }
  td.nm { width:28%; }
  td.pr { text-align:center; width:25%; }
  td.pr .p b { font-size:16px; font-weight:900; }
  td.pr .p i { font-style:normal; font-size:11px; font-weight:700; margin-left:1px; }
  td.prem .p b { color:var(--navy); }
  .txt { font-size:12.5px; font-weight:900; }
  .tbd, .dash { font-size:12px; font-weight:700; color:var(--mute); }
  .chip { display:inline-block; margin-left:6px; padding:0 6px; border-radius:9px; font-style:normal; font-size:10.5px;
          font-weight:700; color:var(--mute); border:1px solid var(--line); white-space:nowrap; }
  .chip.warn { color:var(--warn); border-color:var(--warn); background:var(--warnbg); }
  .special { margin-top:12px; border:2px solid var(--navy); border-radius:2px; padding:9px 12px; }
  .special > p { margin:0 0 6px; font-size:12.5px; } .special > p strong { color:var(--navy); font-size:14px; font-weight:900; margin-right:8px; }
  .spwrap { display:grid; grid-template-columns:repeat(auto-fit, minmax(160px, 1fr)); gap:8px 14px; }
  .spc { min-width:0; } .spc h3 { margin:0 0 3px; font-size:13px; color:var(--navy); font-weight:900; }
  .spc h3 small { color:var(--mute); font-weight:500; font-size:11px; }
  .spc ul { margin:0; padding:0; list-style:none; font-size:12px; line-height:1.6; }
  .spc li span { color:var(--mute); margin-left:6px; font-size:11px; }
  .notes { margin:9px 2px 0; padding:0; list-style:none; font-size:11px; color:var(--mute); line-height:1.6; }
  .foot { margin-top:8px; display:flex; justify-content:space-between; flex-wrap:wrap; gap:4px; font-size:11px;
          color:var(--mute); border-top:1px solid var(--line); padding-top:6px; }
  .foot b { color:var(--navy); }
  @media (max-width:560px) {
    .page { padding:12px 10px; } .head h1 { font-size:19px; }
    table, tbody { display:block; } thead { display:none; }
    tr.grp, tr.ih { display:block; } tr.grp th, tr.ih td { display:block; }
    tr.grp { margin-top:10px; }
    tr.vr { display:grid; grid-template-columns:1fr 1fr; border:1px solid var(--line); border-top:none; }
    tr.vr td { border:none; width:auto !important; }
    td.vd, td.nm { grid-column:1 / -1; padding-bottom:0; }
    td.nm { padding-top:0; }
    td.pr { background:var(--zebra); margin:4px 4px 6px 8px; border-radius:2px; }
    td.prem { margin:4px 8px 6px 4px; }
    td.pr::before { content:"일반"; display:block; font-size:10.5px; font-weight:700; color:var(--mute); }
    td.prem::before { content:"프리미엄"; }
  }
  @media print {
    body { background:#fff; padding:0; } .page { max-width:none; box-shadow:none; padding:0; }
    tr { break-inside:avoid; } tr.ih { break-after:avoid; }
  }
</style>
"""


def page(show_names):
    body_rows, sp = build(show_names)
    cols = "<th>업체</th><th>업체명</th><th>일반</th><th>프리미엄</th>" if show_names else "<th>업체</th><th>일반</th><th>프리미엄</th>"
    title = "업체별 시공 단가표 검토본" if show_names else "업체별 시공 단가표"
    review = ('<p class="review">검토용 — 업체명 포함(외부 배포 금지). 가격은 품목 대표가가 자동으로 들어간 초안이며, '
              '업체별 확인 후 엑셀에서 다른 업체만 덮어쓰면 이 표가 갱신됩니다. '
              '<em class="chip warn">참가 확인</em> = 직전 행사 무상 등록 업체.</p>') if show_names else ""
    body = f"""
<div class="page">
  <header class="head">
    <div><h1>{'입주박람회 업체별 시공 단가표' if not show_names else '업체별 시공 단가표 (검토용)'}</h1>
    <p>전용 84㎡(34평) 기준 · 박람회 현장 계약가 · 품목별 업체 A·B·C</p></div>
    <div class="box">단지 <u>&nbsp;</u></div>
  </header>
  {review}
  <div class="legend"><span><b>일반</b> 기본 시공 범위</span><span><b>프리미엄</b> 상위 자재·범위 확장</span>
  <span>업체명은 박람회 현장 부스에서 확인</span></div>
  <table>
    <thead><tr>{cols}</tr></thead>
    <tbody>
{body_rows}
    </tbody>
  </table>
  <section class="special">
    <p><strong>가전 · 가구 · 안마의자</strong>업체별 대표 특가 1~2개 사전 공개 · 그 외 전 품목 박람회 현장 공개</p>
    <div class="spwrap">{sp}</div>
  </section>
  <ul class="notes">
    <li>※ 표기 금액은 84㎡ 기준이며 평형·현장 여건·자재에 따라 달라질 수 있습니다. 최종 금액은 업체 현장 견적서 기준입니다.</li>
    <li>※ 추가 범위·옵션과 '현장 제시' 항목은 박람회 현장에서 업체별로 안내합니다.</li>
  </ul>
  <div class="foot"><span>주관 <b>㈜엣지컴퍼니</b></span><span>{"검토본 v1.5 · 2026.10" if show_names else "2026.10 기준"}</span></div>
</div>
"""
    return title, body


for show, art, full in ((True, "vendor_review.html", "업체별_시공단가표_검토용.html"),
                        (False, "vendor_public.html", "입주박람회_시공단가표_업체별.html")):
    title, body = page(show)
    open(os.path.join(OUT, art), "w").write(
        f'<title>{title}</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n' + STYLE + body)
    open(os.path.join(OUT, full), "w").write(
        '<!DOCTYPE html>\n<html lang="ko">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<title>{title}</title>\n' + STYLE + '</head>\n<body>\n' + body + '</body>\n</html>\n')
print("items", len(items), "vendor rows", sum(len(v) for v in items.values()), "special", sum(len(v) for v in special.values()))
