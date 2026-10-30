# AI 주관사업부 오피스 시안 — 고급 일러스트형 (2배로 그려 줄여서 매끈하게)
# 실행: python office_mock.py --skin 귀여운직원_v1 [-o 저장.png]   · 스킨 = skins/<이름>/chibi.py
import json, random, datetime, os, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
import argparse
ap = argparse.ArgumentParser(); ap.add_argument("--skin", default="귀여운직원_v1"); ap.add_argument("-o", "--out", default="")
ARGS = ap.parse_args(); SKIN = ARGS.skin
OUT = ARGS.out or os.path.join(HERE, f"office_{SKIN}.png")
W, H, K = 1600, 1230, 2
random.seed(11)

def mix(a, b, t):
    a = [int(a[i:i+2], 16) for i in (1, 3, 5)]; b = [int(b[i:i+2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))
_F = {}
def F(sz, bold=True):
    k = (sz, bold)
    if k not in _F: _F[k] = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf" if bold else "C:/Windows/Fonts/malgun.ttf", int(sz * K))
    return _F[k]

base = Image.new("RGBA", (W * K, H * K), "#efe8dc")
D = ImageDraw.Draw(base)
TS = []; SC = 0.72                                   # 캐릭터 · 책상 크기 비율
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
def tlen(t, sz, bold=True): return D.textlength(t, font=F(sz, bold)) / K

# 바닥 무늬 (테라조)
for _ in range(9000):
    x, y = random.uniform(0, W), random.uniform(0, H); r_ = random.uniform(0.6, 1.8)
    el([x - r_, y - r_, x + r_, y + r_], random.choice(["#e3d9c9", "#f6f1e8", "#ddd2c0", "#e9e1d3"]))

TEAM = {
    "scout":    ("01", "개척",     "#d9a441", 4, "공고 감시 · 공고 분석 · 단지 · 카페"),
    "analysis": ("02", "착수분석", "#5f95db", 5, "손익 · 행사장 · 주관사 연구"),
    "build":    ("03", "제작",     "#5cb87a", 8, "제안서 · 제출서류 · 비주얼"),
    "audit":    ("04", "검증",     "#e07a68", 6, "검수 · 법무 · 비주얼 QA · 법정"),
    "mail":     ("05", "발송",     "#a77fd6", 4, "발송 담당 · 메일 · 보관함 · GIF"),
    "pt":       ("06", "PT",       "#e6ad3c", 4, "PT 코치 · 대본 · 예상 질문"),
    "retro":    ("07", "결과·관제", "#4fb8b0", 4, "마감 관제 · 결과 분석"),
}
WORK = {"scout": (1, "notice_watch.py"), "analysis": (0, ""), "build": (2, "build_군포.py"),
        "audit": (5, "독립 검수관 × 5 · full.txt 대조"), "mail": (1, "mail_군포.html"),
        "pt": (2, "오산 PT 대본"), "retro": (1, "입찰현황판.md")}
CX = [24, 417, 810, 1203]; CW = 373
R1, R2, R3, RH, RH3 = 96, 416, 736, 300, 470
ROOMS = [("scout", CX[0], R1), ("analysis", CX[1], R1), ("build", CX[2], R1), ("audit", CX[3], R1),
         ("mail", CX[0], R2), ("pt", CX[1], R2), ("retro", CX[2], R2)]
BOSS = (CX[3], R2); GX, GY, GW = CX[0], R3, CX[3] + CW - CX[0]
WALNUT, WALNUT_D, GOLD, NAVY, CREAM = "#7a5236", "#5b3d2a", "#c9a45c", "#1b2433", "#fbf6ec"

# ── 그림자 (방마다 부드럽게) ──
sh = Image.new("RGBA", base.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
for x, y, w, h in [(x, y, CW, RH) for _, x, y in ROOMS] + [(BOSS[0], BOSS[1], CW, RH), (GX, GY, GW, RH3)]:
    sd.rounded_rectangle(P(x + 2, y + 10, x + w - 2, y + h + 8), radius=22 * K, fill=(60, 40, 20, 70))
base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14 * K)))

def floor(x, y, w, h):
    fl = Image.new("RGBA", (w * K, h * K)); fd = ImageDraw.Draw(fl)
    tones = ["#d6a676", "#d0a06f", "#dbad7f", "#cd9b69"]
    ph = 22
    for i, yy in enumerate(range(0, h, ph)):
        fd.rectangle([0, yy * K, w * K, (yy + ph) * K], fill=tones[i % 4])
        fd.line([0, yy * K, w * K, yy * K], fill="#bd8c5e", width=K)
        off = (i * 97) % 150
        for xx in range(off, w, 150): fd.line([xx * K, yy * K, xx * K, (yy + ph) * K], fill="#c3915f", width=K)
        for _ in range(6):                               # 나뭇결
            gx = random.uniform(0, w); gy = yy + random.uniform(4, ph - 4)
            fd.line([gx * K, gy * K, (gx + random.uniform(20, 60)) * K, gy * K], fill="#c99868", width=1)
    m = Image.new("L", fl.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w * K - 1, h * K - 1], radius=20 * K, fill=255)
    base.paste(fl, (x * K, y * K), m)

def shell(x, y, w, h, wall_h=78):
    floor(x, y, w, h)
    rr([x, y, x + w, y + wall_h], 20, "#f7f0e4"); rect([x, y + 40, x + w, y + wall_h], "#f7f0e4")
    for xx in range(int(x) + 14, int(x + w) - 10, 18): line([(xx, y + 6), (xx, y + wall_h - 18)], "#f1e8d8", 1)   # 벽지 줄무늬
    rect([x, y + wall_h - 16, x + w, y + wall_h - 2], "#eadfcb"); rect([x, y + wall_h - 17, x + w, y + wall_h - 16], "#dccfb7")
    rect([x, y + wall_h - 3, x + w, y + wall_h + 1], WALNUT)
    rr([x, y, x + w, y + h], 20, None, WALNUT_D, 3)

def rug(x0, y0, x1, y1, color):
    rr([x0, y0, x1, y1], 16, mix(color, CREAM, 0.62))
    rr([x0 + 7, y0 + 7, x1 - 7, y1 - 7], 12, None, mix(color, WALNUT_D, 0.15), 2)
    rr([x0 + 12, y0 + 12, x1 - 12, y1 - 12], 9, None, mix(GOLD, CREAM, 0.2), 1)
    for i in range(int(x0) + 22, int(x1) - 18, 26):                 # 술 장식
        line([(i, y0 - 4), (i, y0)], mix(color, CREAM, 0.3), 1.5); line([(i, y1), (i, y1 + 4)], mix(color, CREAM, 0.3), 1.5)

def plant(cx, by, s=1.0):
    rr([cx - 15 * s, by - 26 * s, cx + 15 * s, by], 7 * s, "#f4f0e8", "#cbbfaa", 1.5)
    rect([cx - 15 * s, by - 22 * s, cx + 15 * s, by - 19 * s], GOLD)
    leaves = [(-14, -44, 16, 30), (6, -50, 16, 32), (-4, -62, 14, 30), (14, -36, 14, 24), (-22, -32, 14, 22)]
    for i, (dx, dy, lw, lh) in enumerate(leaves):
        c = ["#3f8f5a", "#4fa36a", "#367d4e", "#5bb377", "#2f6f45"][i]
        el([cx + dx * s - lw * s / 2, by + dy * s - lh * s / 2, cx + dx * s + lw * s / 2, by + dy * s + lh * s / 2], c)
        line([(cx + dx * s, by + dy * s - lh * s / 3), (cx + dx * s, by + dy * s + lh * s / 3)], mix(c, "#ffffff", 0.25), 1)

def frame(x0, y0, x1, y1, inner="#ffffff"):
    rr([x0, y0, x1, y1], 3, GOLD); rr([x0 + 3, y0 + 3, x1 - 3, y1 - 3], 2, inner)

def bookshelf(x0, y0, w, h=50):
    rr([x0, y0, x0 + w, y0 + h], 4, WALNUT); rect([x0 + 4, y0 + 4, x0 + w - 4, y0 + h - 4], "#5f3f2b")
    for sy in (y0 + 4, y0 + h / 2):
        bx = x0 + 6
        while bx < x0 + w - 8:
            bw = random.choice([4, 5, 6, 7]); bh = random.uniform(h / 2 - 12, h / 2 - 6)
            rect([bx, sy + (h / 2 - 4 - bh), bx + bw, sy + h / 2 - 4], random.choice(["#b85c4c", "#5677a8", "#d9b25f", "#6b9a6a", "#8d6bb0", "#e8dcc4", "#2f3b52"]))
            bx += bw + 1
        rect([x0 + 4, sy + h / 2 - 4, x0 + w - 4, sy + h / 2 - 1], WALNUT)

def sconce(x, y):
    rr([x - 3, y, x + 3, y + 10], 2, GOLD); el([x - 9, y - 10, x + 9, y + 4], "#fff3cf", GOLD, 1.5)

def props(key, x, y, w):
    R = x + w - 18
    if key == "scout":
        frame(R - 112, y + 14, R - 8, y + 62, "#f3ead2")
        el([R - 100, y + 22, R - 62, y + 44], "#a8d2a0"); el([R - 70, y + 30, R - 22, y + 56], "#a9cbe8"); el([R - 96, y + 40, R - 76, y + 54], "#bcdcae")
        for px, py in ((R - 82, y + 30), (R - 46, y + 42), (R - 30, y + 26)): el([px - 4, py - 4, px + 4, py + 4], "#d9493b", "#ffffff", 1)
    elif key == "analysis":
        rr([R - 120, y + 12, R - 6, y + 64], 6, "#ffffff", "#c9ced6", 2)
        for i, hh in enumerate((18, 30, 24, 38)): rr([R - 108 + i * 15, y + 56 - hh, R - 98 + i * 15, y + 56], 2, ["#5f95db", "#e07a68", "#5cb87a", "#e6ad3c"][i])
        D.pieslice(P(R - 46, y + 20, R - 14, y + 52), 0, 250, fill="#5f95db"); D.pieslice(P(R - 46, y + 20, R - 14, y + 52), 250, 360, fill="#e6ad3c")
        el([R - 37, y + 29, R - 23, y + 43], "#ffffff")
    elif key == "build":
        bookshelf(R - 150, y + 12, 70); bookshelf(R - 74, y + 12, 70)
    elif key == "audit":
        bookshelf(R - 150, y + 12, 80)
        frame(R - 58, y + 12, R - 6, y + 64, "#fbf5e6")
        cx_ = R - 32; line([(cx_, y + 22), (cx_, y + 54)], "#a88238", 2.5); line([(cx_ - 18, y + 28), (cx_ + 18, y + 28)], "#a88238", 2.5)
        for sx in (cx_ - 16, cx_ + 16): line([(sx, y + 28), (sx, y + 38)], "#a88238", 1); D.chord(P(sx - 8, y + 32, sx + 8, y + 46), 0, 180, fill="#d9b25f")
        rr([cx_ - 10, y + 52, cx_ + 10, y + 57], 2, "#a88238")
    elif key == "mail":
        rr([R - 140, y + 12, R - 6, y + 64], 4, WALNUT)
        for i in range(6):
            for j in range(2):
                bx, by = R - 136 + i * 22, y + 16 + j * 24
                rect([bx, by, bx + 19, by + 20], "#5f3f2b")
                if (i + j) % 3: rr([bx + 3, by + 8, bx + 16, by + 18], 1, "#fbf6ec"); poly([(bx + 3, by + 8), (bx + 16, by + 8), (bx + 9.5, by + 13)], "#e9dfcc")
                elif (i * j) % 2 == 0: rr([bx + 3, by + 8, bx + 16, by + 18], 1, "#e7d4f5")
    elif key == "pt":
        rect([R - 150, y + 8, R - 4, y + 12], "#4a4f5a")
        rr([R - 146, y + 12, R - 8, y + 64], 3, "#ffffff", "#cfd4dc", 1.5)
        rr([R - 136, y + 20, R - 70, y + 26], 2, "#e6ad3c"); rr([R - 136, y + 32, R - 84, y + 36], 2, "#c8ccd4"); rr([R - 136, y + 42, R - 92, y + 46], 2, "#c8ccd4"); rr([R - 136, y + 52, R - 100, y + 56], 2, "#c8ccd4")
        el([R - 58, y + 22, R - 18, y + 58], "#f6e2b4"); D.pieslice(P(R - 58, y + 22, R - 18, y + 58), 270, 30, fill="#e6ad3c")
    elif key == "retro":
        for i in range(3):
            mx = R - 162 + i * 54
            rr([mx, y + 14, mx + 50, y + 60], 4, "#1d2330", "#3a4252", 2)
            pts = [(mx + 6 + k * 8, y + 50 - ((k * 7 + i * 5) % 22)) for k in range(6)]
            line(pts, "#4fb8b0", 2)
        el([R - 210, y + 18, R - 176, y + 52], "#ffffff", GOLD, 3); line([(R - 193, y + 35), (R - 193, y + 24)], NAVY, 2); line([(R - 193, y + 35), (R - 184, y + 38)], NAVY, 2)

exec(open(os.path.join(HERE, "skins", SKIN, "chibi.py"), encoding="utf-8").read())     # 스킨: new_look · chibi · BOSS_LOOK
AWAY = {"audit": 1}; REPORT = {}

def status_dot(x, y, on):
    if on:
        el([x - 11, y - 11, x + 11, y + 11], (60, 200, 110, 70)); el([x - 7, y - 7, x + 7, y + 7], "#34c46c", "#ffffff", 2.5)
    else:
        el([x - 6, y - 6, x + 6, y + 6], "#c3c8d0", "#ffffff", 2)

def bubble(cx, bottom, t, bg="#ffffff", sz=14):
    tw = tlen(t, sz); w = tw + 24; h = sz + 16; x0 = cx - w / 2; y0 = bottom - h - 9
    rr([x0 + 1, y0 + 3, x0 + w + 1, y0 + h + 3], 12, (0, 0, 0, 40))
    rr([x0, y0, x0 + w, y0 + h], 12, bg, "#d8cdbb", 1.5)
    poly([(cx - 7, y0 + h - 1), (cx + 7, y0 + h - 1), (cx, y0 + h + 9)], bg)
    text((x0 + 12, y0 + 6), t, sz, INK)

def plaque(x, y, no, name, color, badge=None):
    w = tlen(name, 19) + (78 if no else 44)
    rr([x, y, x + w, y + 36], 10, NAVY)
    if no:
        el([x + 7, y + 6, x + 31, y + 30], color); text((x + 19, y + 18), no, 11, "#ffffff", anchor="mm")
        text((x + 40, y + 6), name, 19, "#fbf3e2")
    else:
        rr([x + 10, y + 11, x + 20, y + 25], 3, color); text((x + 28, y + 6), name, 19, "#fbf3e2")
    if badge:
        bt, on = badge; bw = tlen(bt, 13) + 20
        rr([x + 2, y + 42, x + 2 + bw, y + 64], 11, "#2f9a5a" if on else "#a7adb7"); text((x + 12, y + 44), bt, 13, "#ffffff")

def desk_room(key, x, y):
    no, name, color, n, sub = TEAM[key]; busy, label = WORK[key]
    shell(x, y, CW, RH); props(key, x, y, CW)
    rug(x + 22, y + 98, x + CW - 22, y + RH - 26, color)
    top = (n + 1) // 2; bot = n - top; per = max(top, bot); sp = 74
    tw = per * sp + 16; tx = x + CW / 2 - tw / 2; ty = y + 150
    seats = [("t", tx + 8 + sp / 2 + i * sp) for i in range(top)] + [("b", tx + 8 + sp / 2 + i * sp) for i in range(bot)]
    order = [i for i, s in enumerate(seats) if s[0] == "t"] + [i for i, s in enumerate(seats) if s[0] == "b"]
    occ = set(order[:busy])
    looks = [new_look(key, i) for i in range(len(seats))]
    away = set(order[busy:busy + AWAY.get(key, 0)])          # 본부장실에 보고하러 간 자리
    shirt = mix(color, "#ffffff", 0.12)
    heads = []; TS.append((x + CW / 2, ty + 40, SC))
    for i, (side, sx) in enumerate(seats):                               # 위 줄: 의자 → 사람
        if side != "t": continue
        rr([sx - 30, ty - 52, sx + 30, ty + 6], 18, "#3d414c", "#2a2d35", 2); rr([sx - 22, ty - 46, sx + 22, ty - 36], 5, "#4b505c")
        if i in away: REPORT.update(look=looks[i], shirt=shirt, room=name); heads.append((sx, ty - 24 - 36, "away")); continue
        chibi(sx, ty - 24, shirt, looks[i], i in occ); heads.append((sx, ty - 24 - 36, i in occ))
    rr([tx, ty - 2, tx + tw, ty + 34], 8, "#9a6844"); rr([tx, ty + 22, tx + tw, ty + 40], 7, "#6e4630")    # 책상
    line([(tx + 8, ty + 1), (tx + tw - 8, ty + 1)], "#b78258", 2)
    for i, (side, sx) in enumerate(seats):
        on = i in occ
        if side == "t":
            if on:
                rr([sx - 21, ty - 8, sx + 21, ty + 12], 3, "#dfe3e8", "#b6bcc5", 1.5); el([sx - 4, ty - 2, sx + 4, ty + 6], mix(color, "#ffffff", 0.2))
                el([sx - 27, ty + 6, sx - 17, ty + 15], looks[i]["skin"], INK, 1.5); el([sx + 17, ty + 6, sx + 27, ty + 15], looks[i]["skin"], INK, 1.5)
            else:
                rr([sx - 21, ty + 6, sx + 21, ty + 12], 2, "#cfd4db", "#b6bcc5", 1)
                rr([sx + 22, ty + 2, sx + 32, ty + 13], 2, "#ffffff", "#c9bfae", 1); arc([sx + 29, ty + 4, sx + 36, ty + 11], 270, 90, "#c9bfae", 1.5)
                arc([sx + 22, ty - 10, sx + 30, ty], 90, 270, "#d9d2c6", 1.5)
        else:
            rr([sx - 24, ty + 4, sx + 24, ty + 30], 4, "#2a2f3a"); rr([sx - 6, ty + 30, sx + 6, ty + 34], 1, "#8a8f99")
            if on:
                rr([sx - 20, ty + 7, sx + 20, ty + 27], 2, mix(color, "#ffffff", 0.55))
                for k in range(3): rr([sx - 16, ty + 11 + k * 5, sx - 16 + (26 - k * 6), ty + 13 + k * 5], 1, mix(color, INK, 0.1))
            else:
                rr([sx - 20, ty + 7, sx + 20, ty + 27], 2, "#3a404c")
    for i, (side, sx) in enumerate(seats):                               # 아래 줄: 사람(뒷모습) → 의자
        if side != "b": continue
        if i in away: REPORT.update(look=looks[i], shirt=shirt, room=name)
        else: chibi(sx, ty + 66, shirt, looks[i], i in occ, back=True)
        rr([sx - 30, ty + 88, sx + 30, ty + 128], 16, "#3d414c", "#2a2d35", 2); rr([sx - 22, ty + 94, sx + 22, ty + 102], 5, "#4b505c")
        heads.append((sx + 30, ty + 50, "away" if i in away else i in occ))
    heads = [(*TF(hx, hy), on) for hx, hy, on in heads]; TS.pop()
    if per < 4: plant(x + 44, y + RH - 12, 0.9)
    plant(x + CW - 40, y + RH - 12, 0.9)
    # 이름표 · 설명
    plaque(x + 14, y + 12, no, name, color, (f"작업 {busy} / {n}석", busy > 0))
    sw = tlen(sub, 11, False) + 20; rr([x + CW / 2 - sw / 2, y + RH - 20, x + CW / 2 + sw / 2, y + RH - 4], 8, (251, 246, 236, 225)); text((x + CW / 2, y + RH - 12), sub, 11, "#7a5f48", bold=False, anchor="mm")
    for hx, hy, on in heads:
        if on == "away":
            cxx = hx - 30 * SC if hy > y + 180 else hx; cyy = hy + 18 if hy > y + 180 else hy + 24
            tw_ = tlen("보고 중", 12) + 34; rr([cxx - tw_ / 2, cyy - 12, cxx + tw_ / 2, cyy + 12], 12, NAVY, GOLD, 1.5)
            el([cxx - tw_ / 2 + 8, cyy - 5, cxx - tw_ / 2 + 18, cyy + 5], GOLD); text((cxx + 8, cyy), "보고 중", 12, "#ffe7a6", anchor="mm")
        else: status_dot(hx, hy, on)
    lead = [h for h in heads if h[2] is True]
    if lead:
        hx, hy, _ = lead[1] if key == "audit" else lead[0]
        bw_ = tlen(label, 14) + 24; bubble(min(max(hx, x + 122 + bw_ / 2), x + CW - 12 - bw_ / 2), hy - 14, label)

for key, x, y in ROOMS: desk_room(key, x, y)

# ── 본부장실 ──
bx, by = BOSS
shell(bx, by, CW, RH)
rr([bx + CW - 140, by + 12, bx + CW - 18, by + 64], 4, WALNUT)
rr([bx + CW - 136, by + 16, bx + CW - 22, by + 60], 2, "#cfe6f3")
for i, (bw_, bh_) in enumerate(((16, 26), (12, 34), (20, 20), (14, 30), (18, 24), (12, 18))):
    xx = bx + CW - 134 + i * 19; rect([xx, by + 60 - bh_, xx + bw_, by + 60], mix("#9bb3c8", "#ffffff", 0.2 * (i % 2)))
line([(bx + CW - 79, by + 16), (bx + CW - 79, by + 60)], WALNUT, 3)
bookshelf(bx + 150, by + 12, 70)
rug(bx + 30, by + 98, bx + CW - 30, by + RH - 26, "#b48a5a")
cx = bx + CW / 2; ty = by + 158
TS.append((cx, ty + 10, 0.8))
rr([cx - 34, ty - 66, cx + 34, ty + 6], 22, "#5a2f25", "#3a1d16", 2); rr([cx - 26, ty - 58, cx + 26, ty - 44], 7, "#73402f")
chibi(cx, ty - 26, "#2b3550", BOSS_LOOK, True, suit=BOSS_LOOK.get("suit", False))
rr([cx - 96, ty - 4, cx + 96, ty + 36], 8, "#7a4a2e"); rr([cx - 96, ty + 22, cx + 96, ty + 42], 7, "#5a3420"); line([(cx - 88, ty), (cx + 88, ty)], "#a06a44", 2)
rr([cx - 22, ty - 10, cx + 22, ty + 12], 3, "#dfe3e8", "#b6bcc5", 1.5); el([cx - 4, ty - 4, cx + 4, ty + 4], GOLD)
el([cx - 33, ty + 4, cx - 23, ty + 13], "#ffdcc2", INK, 1.5); el([cx + 23, ty + 4, cx + 33, ty + 13], "#ffdcc2", INK, 1.5)
rr([cx + 46, ty + 2, cx + 82, ty + 14], 3, GOLD); text((cx + 64, ty + 8), "본부장", 8, NAVY, anchor="mm")
rr([cx - 80, ty + 2, cx - 52, ty + 16], 2, "#fbf6ec", "#d9cfbf", 1)
TS.pop()
rr([bx + 56, by + RH - 74, bx + 196, by + RH - 34], 16, "#9c5a3c", "#6e3a26", 2); rr([bx + 66, by + RH - 68, bx + 186, by + RH - 52], 8, "#b56d4b")      # 가죽 소파
el([bx + 216, by + RH - 66, bx + 262, by + RH - 40], "#7a4a2e"); el([bx + 232, by + RH - 62, bx + 246, by + RH - 52], "#ffffff", "#c9bfae", 1)
plant(bx + CW - 40, by + RH - 12, 0.9)
plaque(bx + 14, by + 12, "", "본부장실", GOLD)
RX, RY = bx + 84, ty - 6
TS.append((RX, RY, SC)); chibi(RX, RY, REPORT["shirt"], REPORT["look"], True, stand=True, paper=True); TS.pop()
status_dot(RX + 22, RY - 32, True)
bubble(bx + 112, RY - 40, f"{REPORT['room']} 결과 보고드립니다")
bubble(cx + 92, ty - 44, "확인! 수고했어요", bg="#fff6dc")
# 검증 ↔ 본부장실 동선 (실제 화면에선 걸어갔다 돌아옴)
gx_ = CX[3] + CW / 2; line([(gx_ - 90, R1 + RH - 2), (gx_ - 90, R2 + 2)], GOLD, 2); line([(gx_ + 90, R1 + RH - 2), (gx_ + 90, R2 + 2)], GOLD, 2)
pw = 220; rr([gx_ - pw / 2, R1 + RH - 3, gx_ + pw / 2, R2 + 3], 12, NAVY, GOLD, 1.5); text((gx_, (R1 + RH + R2) / 2), "▼ 보고하러 감   ·   ▲ 자리로 복귀", 11, "#ffe7a6", anchor="mm")

# ── 상황실 ──
shell(GX, GY, GW, RH3, wall_h=72)
plaque(GX + 14, GY + 14, "", "상황실 · 단지 현황판", GOLD, ("입찰현황판.md 실시간", True))
LX = GX + GW - 470
rr([LX, GY + 16, LX + 440, GY + 50], 17, "#fffaf0", "#dccfb7", 1.5)
el([LX + 315, GY + 26, LX + 329, GY + 40], GOLD, "#ffffff", 2.5); text((LX + 336, GY + 23), "본부장실 보고 중", 13, INK)
status_dot(LX + 22, GY + 33, True); text((LX + 40, GY + 23), "작업 중", 13, INK)
status_dot(LX + 122, GY + 33, False); text((LX + 138, GY + 23), "자리 대기 (노트북 닫힘)", 13, INK)
BX0, BY0, BX1, BY1 = GX + 20, GY + 86, GX + GW - 20, GY + RH3 - 18
rr([BX0 - 4, BY0 - 4, BX1 + 4, BY1 + 4], 14, GOLD)
rr([BX0, BY0, BX1, BY1], 11, "#141c2b")
for i in range(40): line([(BX0 + 4, BY0 + 4 + i), (BX1 - 4, BY0 + 4 + i)], mix("#1f2a3f", "#141c2b", i / 40), 1)
rows = json.load(open(os.path.join(HERE, "board_snap.json"), encoding="utf-8"))
STG = [("scout", "#d9a441"), ("analysis", "#5f95db"), ("build", "#5cb87a"), ("audit", "#e07a68"),
       ("ready", "#ef8a3c"), ("mail", "#a77fd6"), ("pt", "#e6ad3c"), ("retro", "#4fb8b0")]
today = datetime.date.today(); y = BY0 + 14; RIGHT = BX0 + 1080
pt = next((q for q in rows if q["pt_ok"]), None)
if pt:
    dd = (datetime.date.fromisoformat(pt["pt_date"]) - today).days
    rr([BX0 + 14, y, RIGHT, y + 38], 10, "#3a3018", GOLD, 1.5)
    rr([BX0 + 24, y + 7, BX0 + 128, y + 31], 12, GOLD); text((BX0 + 76, y + 19), "2차 PT 확정", 13, "#2a2210", anchor="mm")
    text((BX0 + 142, y + 8), f"{pt['name']}    11.08(일) {pt['pt_time']}    {pt['pt_place']}", 17, "#ffe7a6")
    rr([RIGHT - 70, y + 7, RIGHT - 12, y + 31], 12, GOLD); text((RIGHT - 41, y + 19), f"D-{dd}", 13, "#2a2210", anchor="mm")
    y += 50
cols = [BX0 + 24, BX0 + 140, BX0 + 300, BX0 + 390, BX0 + 780]
for c, t in zip(cols, ["단지", "마감", "D-day", "단계   개척 · 착수 · 제작 · 검증 · 발송대기 · 발송 · PT · 결과", "PT 일정"]):
    text((c, y), t, 12, "#7f8aa0")
y += 24
ROWH = 32; allrows = [q for q in rows if not q["pt_ok"]]; vis = int((BY1 - 20 - y) // ROWH); show = allrows[:vis]
TBL_TOP = y - 6
for q in show:
    line([(BX0 + 16, y - 4), (RIGHT, y - 4)], "#222c3e", 1)
    text((cols[0], y), q["site"], 16, "#ffffff")
    text((cols[1], y + 1), q["due"].split(" (")[0].split("까지")[0][:15], 13, "#c3cbd8", bold=False)
    if q["done"]: rr([cols[2], y, cols[2] + 50, y + 22], 11, "#2c6e4c"); text((cols[2] + 25, y + 11), "제출", 11, "#d9f5e4", anchor="mm")
    else:
        dd = q["dday"]; rr([cols[2], y, cols[2] + 50, y + 22], 11, "#c9483b" if dd <= 3 else "#5a6273"); text((cols[2] + 25, y + 11), f"D-{dd}", 11, "#ffffff", anchor="mm")
    st = q["stage"] or "analysis"; idx = [s_[0] for s_ in STG].index(st)
    for i, (_, c) in enumerate(STG):
        px = cols[3] + 12 + i * 44; py = y + 11
        if i < len(STG) - 1: line([(px + 6, py), (px + 38, py)], c if i < idx else "#2c3547", 2)
        if i < idx: el([px - 5, py - 5, px + 5, py + 5], c)
        elif i == idx: el([px - 12, py - 12, px + 12, py + 12], mix(c, "#141c2b", 0.6)); el([px - 8, py - 8, px + 8, py + 8], c, "#ffffff", 2)
        else: el([px - 4, py - 4, px + 4, py + 4], None, "#3f4a5e", 1.5)
    text((cols[4], y + 2), q["pt"][:30], 13, "#f2cf7a" if q["pt_date"] else "#7f8aa0", bold=False)
    y += ROWH
def scrollbar(x, top, bot, shown, total):          # 많으면 스크롤 (보이는 비율만큼 손잡이)
    rr([x - 4, top, x + 4, bot], 4, "#232d40")
    th = max(30, (bot - top) * min(1, shown / max(total, 1)))
    rr([x - 4, top, x + 4, top + th], 4, "#8592ab")
scrollbar(RIGHT - 2, TBL_TOP, BY1 - 16, len(show), len(allrows))
text((RIGHT - 16, TBL_TOP - 22), f"{len(allrows) + (1 if pt else 0)}개 단지 · 스크롤", 11, "#66718a", bold=False, anchor="ra")
# 다가오는 일정
PX = RIGHT + 22
rr([PX, BY0 + 14, BX1 - 14, BY1 - 14], 12, "#1b2436", "#2b3549", 1.5)
text((PX + 18, BY0 + 26), "다가오는 일정", 16, "#ffffff")
ev = []
for q in rows:
    if not q["done"] and q["dday"] is not None and q["dday"] >= 0: ev.append((today + datetime.timedelta(days=q["dday"]), "마감", q["site"], "#c9483b", "#ffffff"))
    if q["pt_date"] and datetime.date.fromisoformat(q["pt_date"]) >= today:
        ev.append((datetime.date.fromisoformat(q["pt_date"]), "PT 확정" if q["pt_ok"] else "PT", q["site"], GOLD if q["pt_ok"] else "#6d5a30", "#2a2210" if q["pt_ok"] else "#f2dca0"))
yy = BY0 + 62; evs = sorted(ev); evis = int((BY1 - 30 - yy) // 32)
scrollbar(BX1 - 26, BY0 + 58, BY1 - 26, evis, len(evs))
for dte, kind, site, c, fg in evs[:evis]:
    dd = (dte - today).days
    text((PX + 18, yy), f"{dte.month}.{dte.day:02d}({'월화수목금토일'[dte.weekday()]})", 13, "#c3cbd8", bold=False)
    kw = tlen(kind, 11) + 16; rr([PX + 112, yy, PX + 112 + kw, yy + 21], 10, c); text((PX + 112 + kw / 2, yy + 10.5), kind, 11, fg, anchor="mm")
    text((PX + 112 + kw + 10, yy + 1), site, 14, "#ffffff")
    text((BX1 - 40, yy + 1), f"D-{dd}", 13, "#ff8a7a" if dd <= 3 else "#7f8aa0", anchor="ra")
    yy += 32

# ── 맨 위 띠 ──
for i in range(80): line([(0, i), (W, i)], mix("#1b2433", "#263247", i / 80), 1)
line([(0, 79), (W, 79)], GOLD, 2)
text((28, 18), "AI 주관사업부 오피스", 26, "#fbf3e2")
text((32 + tlen("AI 주관사업부 오피스", 26) + 12, 30), "EDGE COMPANY · 입주박람회 주관사", 13, GOLD, bold=False)
now = datetime.datetime.now(); cxm = W / 2 + 40
rr([cxm - 112, 12, cxm + 112, 68], 28, "#fbf6ec", GOLD, 2)
el([cxm - 94, 25, cxm - 66, 53], "#f3b63e", "#e09a20", 2)
text((cxm - 56, 15), now.strftime("%H:%M"), 30, NAVY)
text((cxm + 48, 31), f"{now.month}.{now.day}({'월화수목금토일'[now.weekday()]})", 13, "#8a7258")
nwork = sum(v[0] for v in WORK.values()); x = cxm + 132
for t, c in ((f"작업 중  {nwork}", "#2f9a5a"), ("내 답 대기  0", "#5a6273"), ("오늘 끝남  2", "#2f6fd0")):
    w_ = tlen(t, 15) + 40; rr([x, 22, x + w_, 58], 18, c); el([x + 12, 34, x + 24, 46], "#ffffff"); text((x + 30, 28), t, 15, "#ffffff"); x += w_ + 10
rr([W - 150, 22, W - 24, 58], 18, "#263247", "#3a4660", 1.5); el([W - 138, 34, W - 126, 46], "#5fe39a"); text((W - 118, 28), "서버 연결됨", 14, "#c8f2d8")

base.convert("RGB").resize((W, H), Image.LANCZOS).save(OUT, quality=95); print(OUT)
