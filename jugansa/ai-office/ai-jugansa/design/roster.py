# 스킨 캐릭터 전체 보기 — python roster.py --skin 원피스직원_v1 [-o 저장.png]
import os, sys, math, random, argparse
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument("--skin", default="원피스직원_v1"); ap.add_argument("-o", "--out", default="")
ARGS = ap.parse_args(); SKIN = ARGS.skin
OUT = ARGS.out or os.path.join(HERE, "skins", SKIN, "roster.png")
K = 2
GOLD, NAVY, CREAM = "#c9a45c", "#1b2433", "#fbf6ec"
TEAMS = [("boss", "본부장실", GOLD), ("scout", "01 개척", "#d9a441"), ("analysis", "02 착수분석", "#5f95db"), ("build", "03 제작", "#5cb87a"),
         ("audit", "04 검증", "#e07a68"), ("mail", "05 발송", "#a77fd6"), ("pt", "06 PT", "#e6ad3c"), ("retro", "07 결과·관제", "#4fb8b0")]
SEATS = {"scout": 4, "analysis": 5, "build": 8, "audit": 6, "mail": 4, "pt": 4, "retro": 4}

def mix(a, b, t):
    a = [int(a[i:i+2], 16) for i in (1, 3, 5)]; b = [int(b[i:i+2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))
_F = {}
def F(sz, bold=True):
    k = (sz, bold)
    if k not in _F: _F[k] = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf" if bold else "C:/Windows/Fonts/malgun.ttf", int(sz * K))
    return _F[k]
COLS, CWD, CHT = 6, 260, 250
N = 1 + sum(SEATS.values()); ROWS = math.ceil(N / COLS)
W, H = COLS * CWD + 40, 120 + ROWS * CHT + 30
base = Image.new("RGBA", (W * K, H * K), "#f3ede2"); D = ImageDraw.Draw(base)
TS = []
def TF(x, y):
    for cx, cy, sc in reversed(TS): x, y = cx + (x - cx) * sc, cy + (y - cy) * sc
    return x, y
def SCL():
    m = 1.0
    for _, _, sc in TS: m *= sc
    return m
def P(*v):
    out = []
    for i in range(0, len(v), 2):
        x, y = TF(v[i], v[i + 1]); out += [int(round(x * K)), int(round(y * K))]
    return out
def rr(b, rad, fill=None, outline=None, width=0): D.rounded_rectangle(P(*b), radius=int(rad * K * SCL()), fill=fill, outline=outline, width=max(1, int(width * K * SCL())) if width else 0)
def el(b, fill=None, outline=None, width=0): D.ellipse(P(*b), fill=fill, outline=outline, width=max(1, int(width * K * SCL())) if width else 0)
def rect(b, fill): D.rectangle(P(*b), fill=fill)
def poly(pts, fill): D.polygon([tuple(P(*p)) for p in pts], fill=fill)
def arc(b, a0, a1, fill, width): D.arc(P(*b), a0, a1, fill=fill, width=max(1, int(width * K * SCL())))
def line(pts, fill, width): D.line([tuple(P(*p)) for p in pts], fill=fill, width=max(1, int(width * K * SCL())))
def text(xy, t, sz, fill, bold=True, anchor="la"): D.text(tuple(P(*xy)), t, font=F(sz, bold), fill=fill, anchor=anchor)

exec(open(os.path.join(HERE, "skins", SKIN, "chibi.py"), encoding="utf-8").read())

# 머리 띠
rr([0, 0, W, 96], 0, NAVY); line([(0, 95), (W, 95)], GOLD, 2)
title = {"원피스직원_v1": "원피스직원 v1", "귀여운직원_v1": "귀여운직원 v1"}.get(SKIN, SKIN)
text((28, 18), f"캐릭터 스킨 · {title}", 28, "#fbf3e2")
text((30, 62), f"본부장 1 + 팀원 {N - 1}명 · 팀 완장 색 = 사무실 색 · 사내 오피스 화면 전용", 14, GOLD, bold=False)

cells = [("boss", 0, BOSS_LOOK)] + [(t, i, new_look(t, i)) for t, _, _ in TEAMS[1:] for i in range(SEATS[t])]
tinfo = {k: (n, c) for k, n, c in TEAMS}
for idx, (team, i, lk) in enumerate(cells):
    r_, c_ = divmod(idx, COLS); x0, y0 = 20 + c_ * CWD, 112 + r_ * CHT
    tn, tc = tinfo[team]
    rr([x0 + 6, y0 + 6, x0 + CWD - 6, y0 + CHT - 6], 16, "#fffaf2" if team != "boss" else "#fff4d6", tc if team == "boss" else "#e3d8c6", 3 if team == "boss" else 1.5)
    cx, cy = x0 + CWD / 2, y0 + 88
    el([cx - 40, y0 + CHT - 66, cx + 40, y0 + CHT - 56], "#ece3d3")
    TS.append((cx, cy, 1.32)); chibi(cx, cy, "#2b3550" if team == "boss" else mix(tc, "#ffffff", 0.12), lk, True, suit=lk.get("suit", False), stand=True, team=None if team == "boss" else tc); TS.pop()
    nm = lk.get("name", "")
    text((cx, y0 + CHT - 46), nm, 17, "#2b2018", anchor="mm")
    tw = D.textlength(tn, font=F(12)) / K + 20
    rr([cx - tw / 2, y0 + CHT - 32, cx + tw / 2, y0 + CHT - 12], 10, tc); text((cx, y0 + CHT - 22), tn, 12, "#ffffff", anchor="mm")
base.convert("RGB").resize((W, H), Image.LANCZOS).save(OUT, quality=95); print(OUT, (W, H))
