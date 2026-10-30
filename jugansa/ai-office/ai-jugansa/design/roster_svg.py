# SVG 스킨 캐릭터 전체 보기 — python roster_svg.py [--style A|B|C] [--only 루피,조로] [-o 저장.png]
# 크롬(헤드리스)으로 HTML을 그대로 찍는다 (2배 해상도)
import os, sys, argparse, subprocess, importlib.util, html

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--skin", default="원피스직원_v1"); ap.add_argument("--style", default="A"); ap.add_argument("--only", default="")
ap.add_argument("-o", "--out", default="")
A = ap.parse_args()
spec = importlib.util.spec_from_file_location("sc", os.path.join(HERE, "skins", A.skin, "svg_chars.py")); sc = importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)
if hasattr(sc, "set_style"): sc.set_style(A.style)
TEAMS = [("boss", "본부장실", "#c9a45c"), ("scout", "01 개척", "#d9a441"), ("analysis", "02 착수분석", "#5f95db"), ("build", "03 제작", "#5cb87a"),
         ("audit", "04 검증", "#e07a68"), ("mail", "05 발송", "#a77fd6"), ("pt", "06 PT", "#e6ad3c"), ("retro", "07 결과·관제", "#4fb8b0")]
cells = [("boss", sc.BOSS_LOOK)] + [(t, lk) for t, _, _ in TEAMS[1:] for lk in sc.ROSTER[t]]
if A.only: cells = [c for c in cells if any(c[1]["name"].startswith(o) for o in A.only.split(","))]
tinfo = {k: (n, c) for k, n, c in TEAMS}
title = getattr(sc, "STYLE_NAME", {}).get(A.style, A.style)
cards = []
for i, (t, lk) in enumerate(cells):
    tn, tc = tinfo[t]
    cards.append(f'<div class="card{" boss" if t == "boss" else ""}"><div class="fig">{sc.svg(lk, i, team=None if t == "boss" else tc)}</div>'
                 f'<div class="nm">{html.escape(lk["name"])}</div><div class="tg" style="background:{tc}">{tn}</div></div>')
cols = 6 if len(cells) > 6 else len(cells)
W = cols * 250 + 40
page = f'''<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;background:#f3ede2;font-family:"Malgun Gothic",sans-serif;width:{W}px}}
.hd{{background:linear-gradient(#1b2433,#263247);color:#fbf3e2;padding:18px 28px 14px;border-bottom:2px solid #c9a45c}}
.hd b{{font-size:28px}} .hd span{{display:block;color:#c9a45c;font-size:14px;margin-top:6px}}
.grid{{display:grid;grid-template-columns:repeat({cols},238px);gap:12px;padding:16px 20px 24px}}
.card{{background:#fffaf2;border:1.5px solid #e3d8c6;border-radius:16px;height:372px;display:flex;flex-direction:column;align-items:center}}
.card.boss{{background:#fff4d6;border:3px solid #c9a45c}}
.fig{{width:226px;height:300px;margin-top:4px}} .fig svg{{width:100%;height:100%}}
.nm{{font-weight:700;font-size:17px;color:#2b2018;margin-top:4px}} .tg{{color:#fff;font-weight:700;font-size:12px;border-radius:10px;padding:2px 10px;margin-top:5px}}
</style></head><body><div class="hd"><b>원피스직원 v1 · {html.escape(title)}</b><span>본부장 1 + 팀원 {len(cells) - 1}명 · 팀 완장 색 = 사무실 색 · 본부장 PC 전용</span></div>
<div class="grid">{"".join(cards)}</div></body></html>'''
rows = (len(cells) + cols - 1) // cols
H = 90 + rows * 384 + 30
hp = os.path.join(HERE, "skins", A.skin, f"roster_{A.style}.html")
open(hp, "w", encoding="utf-8").write(page)
out = A.out or os.path.join(HERE, "skins", A.skin, f"roster_{A.style}.png")
chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--screenshot={out}", f"--window-size={W},{H}",
                "--force-device-scale-factor=2", "file:///" + hp.replace("\\", "/")], check=True, capture_output=True)
print(out, W, H)
