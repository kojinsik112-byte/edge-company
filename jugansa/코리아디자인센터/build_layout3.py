"""코리아디자인센터 B1 제2관 배치 시안 v3(본부장 10-20 3차) — 전시장 미확정 · 대략 시안 · 업로드 안 함.
규칙: 가구 · 가전 8 × 5m · 나머지 3.5 × 3m · 직영 3곳(엣지조명 · 휴젠뜨 환기 · 실링팬) 10 × 3m = 문 들어가서 바로 오른쪽
· 보험 · 접수처 = 박람회장 밖 입구 오른쪽 · 가운데 = 섬(4 × 2 · 3 × 2) 2개 + 가운데 통로 1개
· 같은 업종 = 바로 옆 · 등 맞댐 · 통로 건너 맞은편 금지(위 · 아래 대각선은 허용) · 가전과 가전 계열(에어컨 · 인덕션 · 냉장고)도 금지.
업체: 안전망 · 방충망 = 한 업체 1곳 · 매트 2 · 줄눈 3 · 탄성 2 · 코팅 2 · 필름 1 · 청소 2 · 새집 1.
A안 = 가구 3 · 가전 2 · 일반 25곳 전부 제2관 안(예비 2칸) / B안 = 가전 1곳 추가(동측 벽 · 기역자 세로변) → 이사 · 통신 · 렌탈은 로비 보험 옆."""
import re

S, W, H, OX, OY = 20, 40, 18.4, 40, 96
G = {"furn": ("#dbeafe", "#2563eb"), "elec": ("#fee2e2", "#dc2626"), "build": ("#fef3c7", "#c08a2d"),
     "life": ("#dcfce7", "#16a34a"), "own": ("#f3e8c8", "#a8843f"), "ops": ("#eef1f5", "#64748b"), "spare": ("#ffffff", "#94a3b8")}
GROUP = {"가구": "furn", "가전": "elec", "에어컨": "elec", "인덕션": "elec", "냉장고·붙박이장": "elec",
         "줄눈": "build", "코팅": "build", "탄성": "build", "필름": "build", "중문": "build", "인테리어": "build",
         "청소": "life", "새집증후군": "life", "매트": "life", "선반": "life", "벽걸이TV": "life", "음식물": "life",
         "이사": "life", "통신": "life", "렌탈": "life", "안전·방충망": "life", "보험": "ops", "접수": "ops", "own": "own", "예비": "spare"}
ELEC = {"가전", "에어컨", "인덕션", "냉장고·붙박이장"}
NEED = {"가구": 3, "가전": 2, "에어컨": 1, "인덕션": 1, "냉장고·붙박이장": 1, "줄눈": 3, "코팅": 2, "탄성": 2, "필름": 1,
        "중문": 1, "인테리어": 1, "청소": 2, "새집증후군": 1, "매트": 2, "선반": 1, "벽걸이TV": 1, "음식물": 1,
        "이사": 1, "통신": 1, "렌탈": 1, "안전·방충망": 1, "보험": 1}


def kind(label):
    return re.sub(r"\s?[A-Z]$", "", label.replace(" ", "")) if label != "예비" else "예비"


def north():  # 기역자 윗변 · 가구 사이 가전
    return [(n, 8 * i, 0, 8, 5) for i, n in enumerate(["가구A", "가전A", "가구B", "가전B", "가구C"])]


def island(x0, cols, top, bot):  # 섬 = 위 줄(북향) + 아래 줄(남향) 등 맞댐
    assert len(top) == len(bot) == cols
    return [(n, x0 + 3.5 * c, 7.2, 3.5, 3) for c, n in enumerate(top)] + [(n, x0 + 3.5 * c, 10.2, 3.5, 3) for c, n in enumerate(bot)]


def south(names):  # 남측 벽 · 직영 부스 오른쪽부터
    return [(n, 16 + 3.5 * k, 15.4, 3.5, 3) for k, n in enumerate(names)]


OWN = ("own", 6, 15.4, 10, 3)  # 문 들어가서 바로 오른쪽(입구 0.5 ~ 6m)
PLANS = {
    "A": dict(
        title="A안 · 가구 3 · 가전 2 — 일반 업체 25곳 전부 제2관 안",
        booths=north() + [OWN]
        + [("안전·방충망A", 0, 7.2, 3, 3.5), ("중문A", 0, 10.7, 3, 3.5)]                                   # 서측 벽
        + island(5, 4, ["청소A", "줄눈A", "탄성A", "코팅A"], ["새집증후군A", "청소B", "줄눈B", "탄성B"])
        + island(21, 4, ["매트A", "필름A", "줄눈C", "코팅B"], ["선반A", "매트B", "벽걸이TV A", "음식물A"])
        + [("에어컨A", 37, 7.2, 3, 3.5), ("인덕션A", 37, 10.7, 3, 3.5), ("냉장고·붙박이장A", 37, 14.2, 3, 3.5)]  # 동측 벽 = 기역자 세로변
        + south(["인테리어A", "이사A", "통신A", "렌탈A", "예비", "예비"]),
        lobby=[("보험A", 13.5, 19.6, 3.5, 2.4)],
        aisles=[(20, 6.1, "통로 2.2m", 0), (20, 14.3, "통로 2.2m", 0), (20, 10.2, "가운데 통로 2m", -90), (4, 12.6, "통로 2m", -90), (36, 12.6, "통로 2m", -90)],
    ),
    "B": dict(
        title="B안 · 가구 3 · 가전 3 — 가전C를 동측 벽(기역자 세로변)에 추가",
        booths=north() + [OWN]
        + [("가전C", 35, 7.2, 5, 8)]                                                                       # 8 × 5m 세로로
        + [("에어컨A", 0, 7.2, 3, 3.5), ("인덕션A", 0, 10.7, 3, 3.5)]                                      # 서측 벽
        + island(5.2, 4, ["청소A", "줄눈A", "탄성A", "코팅A"], ["새집증후군A", "청소B", "줄눈B", "탄성B"])
        + island(21.4, 3, ["매트A", "필름A", "줄눈C"], ["선반A", "매트B", "코팅B"])
        + south(["냉장고·붙박이장A", "중문A", "벽걸이TV A", "인테리어A", "음식물A", "안전·방충망A"]),
        lobby=[("보험A", 13.5, 19.6, 3.5, 2.4), ("이사A", 17.5, 19.6, 3.5, 2.4), ("통신A", 21.5, 19.6, 3.5, 2.4), ("렌탈A", 25.5, 19.6, 3.5, 2.4)],
        aisles=[(20, 6.1, "통로 2.2m", 0), (20, 14.3, "통로 2.2m", 0), (20.3, 10.2, "가운데 통로 2.2m", -90), (4.1, 12.6, "통로 2.2m", -90), (33.45, 11.2, "통로 3.1m", -90)],
    ),
}
GAP, MIN_OV, AISLE = .3, 1.0, 3.6  # 붙음 판정 틈 · 맞은편 판정 겹침 · 통로 폭 상한


def rel(a, b):  # 'touch' = 바로 옆 · 등 맞댐 / 'face' = 통로 건너 맞은편 / None = 대각선 · 떨어짐
    ax0, ay0, aw, ah = a; bx0, by0, bw, bh = b
    ax1, ay1, bx1, by1 = ax0 + aw, ay0 + ah, bx0 + bw, by0 + bh
    ox, oy = min(ax1, bx1) - max(ax0, bx0), min(ay1, by1) - max(ay0, by0)
    gx, gy = max(bx0 - ax1, ax0 - bx1), max(by0 - ay1, ay0 - by1)
    assert not (ox > 1e-6 and oy > 1e-6), f"부스 겹침 {a} {b}"
    for gap, ov in ((gx, oy), (gy, ox)):
        if gap <= GAP and ov > GAP:
            return "touch"
        if GAP < gap <= AISLE and ov > MIN_OV:
            return "face"
    return None


def check(p):
    bs = [b for b in p["booths"] if b[0] not in ("own", "예비")]
    for i, a in enumerate(bs):
        x, y, w, h = a[1:]
        assert 0 <= x and x + w <= W + 1e-6 and 0 <= y and y + h <= H + 1e-6, f"전시장 밖 {a}"
        for b in bs[i + 1:]:
            ka, kb = kind(a[0]), kind(b[0])
            r = rel(a[1:], b[1:])
            if r and (ka == kb or (ka in ELEC and kb in ELEC and "가전" in (ka, kb))):
                raise SystemExit(f"{p['title'][:2]}: {a[0]} · {b[0]} = {'바로 옆/등 맞댐' if r == 'touch' else '맞은편'}")
    got = {}
    for b in bs + p["lobby"]:
        got[kind(b[0])] = got.get(kind(b[0]), 0) + 1
    need = dict(NEED, 가전=NEED["가전"] + (1 if "가전C" in [b[0] for b in bs] else 0))
    assert got == need, {k: (got.get(k), need.get(k)) for k in set(got) | set(need) if got.get(k) != need.get(k)}
    n_in = len(bs) + 3                       # 직영 = 3곳
    return n_in, n_in + len(p["lobby"]), sum(1 for b in p["booths"] if b[0] == "예비")


def r(x, y, w, h, **k):
    a = " ".join(f'{kk.replace("_", "-")}="{v}"' for kk, v in k.items())
    return f'<rect x="{OX + x * S:.1f}" y="{OY + y * S:.1f}" width="{w * S:.1f}" height="{h * S:.1f}" {a}/>'


def t(x, y, s, size=12, w=700, fill="#15233b", rot=0):
    ls = s.split("<br>")
    cx, cy = OX + x * S, OY + y * S
    tr = f' transform="rotate({rot} {cx:.1f} {cy:.1f})"' if rot else ""
    return "".join(f'<text x="{cx:.1f}" y="{cy + (i - (len(ls) - 1) / 2) * (size + 2) + size * .35:.1f}" text-anchor="middle" '
                   f'font-size="{size}" font-weight="{w}" fill="{fill}"{tr}>{l}</text>' for i, l in enumerate(ls))


def svg(p, n_in, n_all):
    sv = [f'<rect x="{OX}" y="{OY}" width="{W * S}" height="{H * S}" fill="#fbfaf7" stroke="#47637a" stroke-width="3"/>',
          f'<rect x="{OX + .5 * S}" y="{OY + H * S - 4}" width="{5.5 * S}" height="8" fill="#c8a35a"/>']  # 입구
    for x, y, s, rot in p["aisles"]:
        sv.append(t(x, y, s, 9.5, 500, "#94a3b8", rot))
    for nm, x, y, w, h in p["booths"] + [("접수", 7, 19.6, 6, 2.4)] + p["lobby"]:
        k = kind(nm)
        f, s_ = G[GROUP.get(k, "ops")]
        dash = ' stroke-dasharray="4 3"' if k == "예비" else ""
        sv.append(r(x + .06, y + .06, w - .12, h - .12, rx=3, fill=f, stroke=s_, stroke_width=1.3).replace("/>", f"{dash}/>"))
        if k == "own":
            for j in (1, 2):
                xx = OX + (x + w / 3 * j) * S
                sv.append(f'<line x1="{xx:.1f}" y1="{OY + (y + .9) * S}" x2="{xx:.1f}" y2="{OY + (y + h - .25) * S}" stroke="{s_}" stroke-opacity=".45" stroke-dasharray="3 3"/>')
            sv.append(t(x + w / 2, y + .5, "엣지컴퍼니 직영 3곳 · 10 × 3m", 9.5, 700, s_))
            for j, s in enumerate(["엣지조명", "휴젠뜨<br>(환기)", "실링팬"]):
                sv.append(t(x + w / 6 * (2 * j + 1), y + 1.85, s, 11))
            continue
        big = k in ("가구", "가전")
        lab = "접수 · 혜택 안내" if k == "접수" else nm.replace("·", "·<br>") if (w < 3.6 and len(nm) > 5) else nm
        sv.append(t(x + w / 2, y + h / 2 - (.45 if big else 0), lab, 15 if big else 10.5, 700, "#94a3b8" if k == "예비" else "#15233b"))
        if big:
            sv.append(t(x + w / 2, y + h / 2 + 1.0, "8 × 5m" + (" (세로)" if h > w else ""), 10.5, 600, s_))
    lx1 = max(x + w for _, x, _, w, _ in p["lobby"])
    sv.append(f'<rect x="{OX + 6.5 * S}" y="{OY + 19.2 * S}" width="{(lx1 - 6.5 + .5) * S}" height="{3.2 * S}" fill="none" stroke="#94a3b8" stroke-dasharray="5 4" rx="6"/>')
    sv.append(t(3.25, 19.3, "입구", 12, 800, "#8a6a2c"))
    sv.append(t((6.5 + lx1 + .5) / 2, 23.3, "박람회장 밖 · 로비(입구 오른쪽)" + (" · 로비 데스크 사용 확인 필요" if len(p["lobby"]) > 1 else ""), 10.5, 600, "#64748b"))
    sv.append(t(20, -1.1, "약 40m", 12, 600, "#47637a"))
    sv.append(t(41.6, 9.2, "약 18m", 12, 600, "#47637a", 90))
    return (f'<svg viewBox="0 0 {W * S + 2 * OX + 10} {OY + 23.8 * S}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{p["title"]}">'
            f'<text x="{OX}" y="34" font-size="19" font-weight="800" fill="#0d1e33">{p["title"]}</text>'
            f'<text x="{OX}" y="58" font-size="12.5" fill="#475569">업체 {n_all}곳 = 제2관 안 {n_in}(직영 3 포함) + 로비 {len(p["lobby"])} · 가구 · 가전 8 × 5m · 그 밖 3.5 × 3m · 전시장 미확정 대략 시안</text>'
            + "".join(sv) + "</svg>")


res = {k: check(p) for k, p in PLANS.items()}
(a_in, a_all, a_sp), (b_in, b_all, _) = res["A"], res["B"]
print("A", res["A"], "B", res["B"])
LEG = "".join(f'<span><i style="background:{G[g][0]};border-color:{G[g][1]}"></i>{s}</span>' for g, s in
              [("furn", "가구"), ("elec", "가전 · 설비 가전"), ("build", "시공(줄눈 · 코팅 · 탄성 · 필름 · 중문 · 인테리어)"),
               ("life", "생활 · 청소 · 서비스"), ("own", "엣지컴퍼니 직영"), ("ops", "접수 · 보험")])
html = f"""<title>코리아디자인센터 배치 시안 v3</title>
<style>
:root{{--bg:#f3f1ec;--fg:#16202e;--sub:#5a6474;--card:#fff;--line:#ddd7cb;--hl:#a8843f}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#0b1522;--fg:#e9edf3;--sub:#9aa6b6;--card:#122135;--line:#24364e;--hl:#d8b46a;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#0b1522;--fg:#e9edf3;--sub:#9aa6b6;--card:#122135;--line:#24364e;--hl:#d8b46a;color-scheme:dark}}
body{{background:var(--bg);color:var(--fg);font-family:"Pretendard","Malgun Gothic",sans-serif;margin:0;padding:20px 16px 40px;line-height:1.55}}
.wrap{{max-width:1000px;margin:0 auto;display:flex;flex-direction:column;gap:14px}}
h1{{font-size:20px;margin:4px 0 0}}.sub{{color:var(--sub);font-size:13.5px;margin:0}}
.plan{{background:#fff;border:1px solid var(--line);border-radius:10px;overflow-x:auto;padding:8px}}.plan svg{{display:block;min-width:760px;width:100%;height:auto}}
.leg{{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:12.5px;color:var(--sub)}}.leg i{{display:inline-block;width:12px;height:12px;border:1.3px solid;border-radius:3px;margin-right:5px;vertical-align:-1px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px}}.card h2{{font-size:14px;margin:0 0 8px}}ul{{margin:0;padding-left:18px;font-size:14px}}
.tw{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;font-size:13.5px;font-variant-numeric:tabular-nums}}th,td{{border-bottom:1px solid var(--line);padding:7px 8px;text-align:left;vertical-align:top}}th{{color:var(--sub);font-weight:600}}
td b{{color:var(--hl)}}
</style>
<div class="wrap">
<div><h1>판교테크노밸리 중흥S-클래스 입주박람회 · 부스 배치 시안 v3</h1>
<p class="sub">코리아디자인센터 B1 제2관(717㎡ · 약 40 × 18m 추정) · 가운데 통로 1개 + 섬 2개 · 같은 업종은 옆 · 등 맞댐 · 맞은편 금지(대각선 허용) — 생성할 때 자동 검사</p></div>
<div class="leg">{LEG}</div>
<div class="plan">{svg(PLANS["A"], a_in, a_all)}</div>
<div class="plan">{svg(PLANS["B"], b_in, b_all)}</div>
<div class="card"><h2>A안 · B안 비교</h2><div class="tw"><table>
<tr><th></th><th>A안 (가구 3 · 가전 2)</th><th>B안 (가구 3 · 가전 3)</th></tr>
<tr><td>업체 수</td><td><b>{a_all}곳</b> = 안 {a_in} + 로비 보험 1 · 예비 {a_sp}칸</td><td><b>{b_all}곳</b> = 안 {b_in} + 로비 {b_all - b_in}(보험 · 이사 · 통신 · 렌탈)</td></tr>
<tr><td>가운데 섬</td><td>4 × 2 + 4 × 2 = 16칸 · 통로 2m</td><td>4 × 2 + 3 × 2 = 14칸 · 통로 2.2m</td></tr>
<tr><td>기역자</td><td>북측 가구 · 가전 5 + 동측 설비 가전 3</td><td>북측 가구 · 가전 5 + 동측 가전C(8 × 5m 세로)</td></tr>
<tr><td>장점</td><td>전 업체가 전시장 안 · 로비 확인 불필요</td><td>가전 1곳(업체당 행사비가 가장 큰 품목) 추가 · 데스크형 서비스는 로비로</td></tr>
<tr><td>확인</td><td>통로 2m(폭 0.2m 좁음)</td><td>로비에 데스크 4개(보험 · 이사 · 통신 · 렌탈) 허용 여부</td></tr>
</table></div></div>
<div class="card"><h2>배치 원칙</h2><ul>
<li>가구 · 가전 = 기역자 · 가구 사이에 가전(가구A · 가전A · 가구B · 가전B · 가구C) · 가전끼리 · 가전과 설비 가전도 붙이거나 마주 보지 않음.</li>
<li>가운데 = 섬 2개 + 가운데 통로 1개 · 섬 위 줄과 아래 줄은 대각선으로만 같은 업종(청소A ↘ 청소B · 매트A ↘ 매트B).</li>
<li>엣지컴퍼니 직영 3곳(엣지조명 · 휴젠뜨 환기 · 실링팬) 10 × 3m = 문 들어가서 바로 오른쪽 · 접수 · 보험 = 박람회장 밖 입구 오른쪽.</li>
<li>업체: 안전망 · 방충망 한 업체 1곳 · 매트 2 · 줄눈 3 · 탄성 2 · 코팅 2 · 필름 1 · 청소 2 · 새집증후군 1.</li></ul></div>
<div class="card"><h2>가구 추가는?</h2><ul>
<li>가구 4 · 가전 3(큰 부스 7개)은 제2관만으로는 어렵습니다 - 서측 벽에 큰 부스를 하나 더 넣으면 섬이 3칸 줄고 입구 동선이 막혀 일반 업체 4곳 이상이 밖으로 밀립니다 → 제3관 일부(499㎡)를 함께 쓸 때 가능.</li>
<li>B안 동측 칸에 가전C 대신 가구D를 넣으면 북측 가구C와 통로를 사이에 두고 마주 봅니다 → 가전이 맞습니다.</li>
<li>치수 · 기둥 · 출입구는 대관 도면으로 다시 맞춥니다.</li></ul></div></div>
"""
open("코리아디자인센터_2관_배치시안_v3.html", "w").write(html)
