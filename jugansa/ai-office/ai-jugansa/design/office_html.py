# AI 주관사업부 오피스 v4 시안 — 3D 입체 사무실(뒷벽 · 옆벽 · 원근 바닥 · 조명) + 사무실 스킨 + 캐릭터 스킨
# 실행: python office_html.py --office 월넛라운지 --skin 원피스직원_v1 [-o 저장.png]   (크롬 헤드리스로 2배 해상도 저장)
import os, json, math, random, html, argparse, subprocess, importlib.util, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument("--office", default="월넛라운지"); ap.add_argument("--skin", default="원피스직원_v1"); ap.add_argument("-o", "--out", default=""); ap.add_argument("--assets", default="")
A = ap.parse_args()
from office_skins import OFFICE_SKINS
OS = OFFICE_SKINS[A.office]
spec = importlib.util.spec_from_file_location("sc", os.path.join(HERE, "skins", A.skin, "svg_chars.py")); sc = importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)
sc.POSES["type"] = ([(-28, 54), (-38, 84), (-31, 102)], [(28, 54), (38, 84), (31, 102)])   # 앉아서 키보드 — 손이 노트북 양옆에 보이게
random.seed(7)
ASSETS = A.assets          # 실제 오피스 화면용: 배경(bg.svg) · 자리별 캐릭터 그림 · 배치(layout.json)를 이 폴더에 쓴다
LAYOUT = {"W": 1600, "H": 1300, "seats": {}, "rooms": {}, "boss": {}, "board": {}, "gaps": [R1 + 0, 0]} if False else None
def sprite(fname, box, inner):
    bx, by, bw, bh = box
    open(os.path.join(ASSETS, fname), "w", encoding="utf-8").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{bx:.1f} {by:.1f} {bw:.1f} {bh:.1f}" width="{bw:.1f}" height="{bh:.1f}">{inner}</svg>')
    return {"file": fname, "x": round(bx, 1), "y": round(by, 1), "w": round(bw, 1), "h": round(bh, 1)}

W, H = 1600, 1300
TEAM = {
    "scout":    ("01", "개척",     "#d9a441", 4, "공고 감시 · 공고 분석 · 단지 · 카페"),
    "analysis": ("02", "착수분석", "#5f95db", 5, "손익 · 행사장 · 주관사 연구"),
    "build":    ("03", "제작",     "#5cb87a", 8, "제안서 · 제출서류 · 비주얼"),
    "audit":    ("04", "검증",     "#e07a68", 6, "검수 · 법무 · 비주얼 QA · 법정"),
    "mail":     ("05", "발송",     "#a77fd6", 4, "발송 담당 · 메일 · 보관함 · GIF"),
    "pt":       ("06", "PT",       "#e6ad3c", 4, "PT 코치 · 대본 · 예상 질문"),
    "retro":    ("07", "결과·관제", "#4fb8b0", 4, "마감 관제 · 결과 분석"),
}
WORK = {"scout": (1, "notice_watch.py"), "analysis": (0, ""), "build": (2, "build_군포.py"), "audit": (5, "독립 검수관 × 5 · full.txt 대조"),
        "mail": (1, "mail_군포.html"), "pt": (2, "오산 PT 대본"), "retro": (1, "입찰현황판.md")}
AWAY = {"audit": 1}
CX = [20, 416, 812, 1208]; CW = 366; CORR = 30            # 방 사이 좁은 복도
R1, R2, RH, R3, RH3 = 100, 470, 340, 840, 430
LAYOUT = {"W": W, "H": H, "seats": {}, "rooms": {}, "boss": {}, "board": {},
          "corrY": [R1 + RH + CORR / 2, R2 + RH + CORR / 2], "corrX": [CX[i] + CW + CORR / 2 for i in range(3)]}
DOORS = {}       # (방 x, y) → 문 안쪽 · 바깥쪽 좌표
ROOMS = [("scout", CX[0], R1), ("analysis", CX[1], R1), ("build", CX[2], R1), ("audit", CX[3], R1),
         ("mail", CX[0], R2), ("pt", CX[1], R2), ("retro", CX[2], R2)]
mix = sc.mix
FONT = 'font-family="Malgun Gothic, sans-serif"'
P, DEFS = [], []
_n = [0]
def nid(): _n[0] += 1; return _n[0]
def T(x, y, t, sz, fill, w=700, anchor="start", extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" {FONT} font-size="{sz}" font-weight="{w}" fill="{fill}" text-anchor="{anchor}" {extra}>{html.escape(str(t))}</text>'
def tw(t, sz):    # 대략 글자 폭 (한글 1 · 영숫자 0.58)
    return sum(sz * (1.0 if ord(ch) > 0x2E80 else 0.58) for ch in str(t))
def poly(pts, fill, extra=""): return f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="{fill}" {extra}/>'
def lerp(a, b, t): return a + (b - a) * t
def grad(kind, stops, **kw):
    i = nid(); at = " ".join(f'{k}="{v}"' for k, v in kw.items())
    DEFS.append(f'<{kind} id="g{i}" {at}>' + "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{op}"/>' for o, c, op in stops) + f'</{kind}>')
    return f"url(#g{i})"

# ───────────── 방(3D 상자) ─────────────
def door(x, y, w, h, dx, wb, bh, side):
    """옆벽 앞쪽에 문 하나 (원근 따라 기울어진 평행사변형) · 걸어 나가는 자리 기록"""
    ex, ix = (x + w, x + w - dx) if side == "right" else (x, x + dx)
    B = lambda t: (lerp(ex, ix, t), lerp(y + h, wb, t)); Hh = lambda t: lerp(h, bh, t) * 0.6
    t1, t2 = 0.1, 0.58; (b1x, b1y), (b2x, b2y) = B(t1), B(t2); h1, h2 = Hh(t1), Hh(t2)
    fr = {"월넛라운지": ("#3a2418", "#8a5a3c"), "마블펜트하우스": ("#b89a74", "#d6bf9c"), "나이트스카이": ("#1a2236", "#3a4a6a")}[A.office]
    g = poly([(b1x, b1y + 2), (b2x, b2y + 2), (b2x, b2y - h2 - 4), (b1x, b1y - h1 - 4)], OS["trim"])
    g += poly([(b1x, b1y), (b2x, b2y), (b2x, b2y - h2), (b1x, b1y - h1)], fr[0])
    m = lambda a, b_, t: lerp(a, b_, t)
    for k in (0.08, 0.52):                                   # 문짝 두 칸
        u1, u2 = k, k + 0.4
        q = [(m(b1x, b2x, 0.12), m(b1y, b2y, 0.12) - m(h1, h2, 0.12) * u1), (m(b1x, b2x, 0.88), m(b1y, b2y, 0.88) - m(h1, h2, 0.88) * u1),
             (m(b1x, b2x, 0.88), m(b1y, b2y, 0.88) - m(h1, h2, 0.88) * u2), (m(b1x, b2x, 0.12), m(b1y, b2y, 0.12) - m(h1, h2, 0.12) * u2)]
        g += poly(q, fr[1])
    hx, hy = m(b1x, b2x, 0.8), m(b1y, b2y, 0.8) - m(h1, h2, 0.8) * 0.46
    g += f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="2.6" fill="{OS["trim"] if not OS["glass"] else "#c9a45c"}"/>'
    g += poly([(b1x, b1y), (b2x, b2y), (b2x - (8 if side == "right" else -8), b2y + 3), (b1x - (14 if side == "right" else -14), b1y + 4)], "#000000", 'opacity=".12"')
    sx_, sy_ = m(b1x, b2x, 0.5), m(b1y, b2y, 0.5) - m(h1, h2, 0.5) - 14          # 문 위 표지
    g += f'<rect x="{sx_ - 15:.1f}" y="{sy_ - 6:.1f}" width="30" height="12" rx="3" fill="#1b2433"/>' + T(sx_, sy_ + 3.5, "문", 9, "#ffe7a6", anchor="middle")
    cx, cy = (b1x + b2x) / 2, (b1y + b2y) / 2
    ox = x + w + CORR / 2 if side == "right" else x - CORR / 2
    g += f'<rect x="{ox - 11:.1f}" y="{cy - 9:.1f}" width="22" height="16" rx="3" fill="{OS["trim"]}" opacity=".35"/>'        # 복도 쪽 문 앞 매트
    DOORS[(x, y)] = {"in": [round(cx + (-34 if side == "right" else 34), 1), round(cy - 2, 1)], "out": [round(x + w + CORR / 2 if side == "right" else x - CORR / 2, 1), round(cy - 2, 1)],
                     "colX": round(x + w + CORR / 2 if side == "right" else x - CORR / 2, 1)}
    return g

def corridors():
    c, run = OS["floor2"], mix(OS["trim"], OS["floor"], 0.55)
    g = []
    for i in range(3):          # 세로 복도
        xx = CX[i] + CW
        g.append(f'<rect x="{xx}" y="{R1 - 6}" width="{CORR}" height="{R3 - R1 + 6}" fill="{c}"/><rect x="{xx + CORR / 2 - 3}" y="{R1}" width="6" height="{R3 - R1 - 4}" rx="3" fill="{run}" opacity=".7"/>')
    for yy in (R1 + RH, R2 + RH):   # 가로 복도
        g.append(f'<rect x="{CX[0] - 6}" y="{yy}" width="{CX[3] + CW - CX[0] + 12}" height="{CORR}" fill="{c}"/><rect x="{CX[0]}" y="{yy + CORR / 2 - 3}" width="{CX[3] + CW - CX[0]}" height="6" rx="3" fill="{run}" opacity=".7"/>')
    for i in range(3):
        for yy in (R1 + RH, R2 + RH):
            xx = CX[i] + CW; g.append(f'<rect x="{xx}" y="{yy}" width="{CORR}" height="{CORR}" fill="{c}"/><circle cx="{xx + CORR / 2}" cy="{yy + CORR / 2}" r="5" fill="{run}"/>')
    return g

def shell(x, y, w, h, dx=44, bh=150, team=None, door_side=None):
    top, wb = y + 10, y + 10 + bh; cid = nid()
    DEFS.append(f'<clipPath id="c{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18"/></clipPath>')
    g = [f'<rect x="{x + 3}" y="{y + 10}" width="{w}" height="{h}" rx="18" fill="#000" opacity=".22" filter="url(#blur)"/>', f'<g clip-path="url(#c{cid})">']
    g.append(poly([(x, y), (x + w, y), (x + w - dx, top), (x + dx, top)], OS["ceil"]))
    # 뒷벽
    g.append(f'<rect x="{x + dx}" y="{top}" width="{w - 2 * dx}" height="{bh}" fill="{grad("linearGradient", [(0, OS["wall"], 1), (1, OS["wall2"], 1)], x1=0, y1=0, x2=0, y2=1)}"/>')
    if OS["side_kind"] == "panel":
        for xx in range(int(x + dx) + 24, int(x + w - dx), 26): g.append(f'<rect x="{xx}" y="{top}" width="1.6" height="{bh - 22}" fill="{OS["wall_line"]}" opacity=".55"/>')
    elif OS["night"]:
        for xx in range(int(x + dx) + 18, int(x + w - dx), 30): g.append(f'<rect x="{xx}" y="{top}" width="1" height="{bh - 22}" fill="{OS["wall_line"]}" opacity=".28"/>')
    else:
        for _ in range(5):
            vx = random.uniform(x + dx, x + w - dx); vy = random.uniform(top, wb - 30)
            g.append(f'<path d="M {vx:.0f},{vy:.0f} q {random.uniform(20, 50):.0f},{random.uniform(-10, 14):.0f} {random.uniform(50, 110):.0f},{random.uniform(-6, 20):.0f}" stroke="{OS["wall_line"]}" stroke-width="1.2" fill="none" opacity=".7"/>')
    g.append(f'<rect x="{x + dx}" y="{wb - 22}" width="{w - 2 * dx}" height="3" fill="{OS["trim"]}" opacity=".85"/><rect x="{x + dx}" y="{wb - 6}" width="{w - 2 * dx}" height="6" fill="{mix(OS["wall2"], "#000000", 0.25)}"/>')
    if team and OS["night"]: g.append(f'<rect x="{x + dx}" y="{wb - 4}" width="{w - 2 * dx}" height="3" fill="{team}" opacity=".9"/><rect x="{x + dx}" y="{wb - 14}" width="{w - 2 * dx}" height="12" fill="{team}" opacity=".18"/>')
    # 옆벽 (창 또는 패널)
    for side in (-1, 1):
        if side == -1: q = [(x, y), (x + dx, top), (x + dx, wb), (x, y + h)]
        else: q = [(x + w, y), (x + w - dx, top), (x + w - dx, wb), (x + w, y + h)]
        if OS["side_kind"] == "panel":
            g.append(poly(q, grad("linearGradient", [(0, OS["side2"], 1), (1, OS["side"], 1)], x1=0 if side == -1 else 1, y1=0, x2=1 if side == -1 else 0, y2=0)))
        else:
            sky = [(0, "#0b1430", 1), (0.6, "#1c2c55", 1), (1, "#2a3a64", 1)] if OS["night"] else [(0, "#a9d2f0", 1), (0.7, "#d8ecf8", 1), (1, "#eef6fb", 1)]
            g.append(poly(q, grad("linearGradient", sky, x1=0, y1=0, x2=0, y2=1)))
            ex = x if side == -1 else x + w; ix = x + dx if side == -1 else x + w - dx
            for _ in range(70 if OS["night"] else 14):      # 바깥 도시
                t = random.uniform(0.08, 0.92); v = random.uniform(0.45, 0.95)
                px = lerp(ex, ix, t); ty = lerp(y, top, t); by_ = lerp(y + h, wb, t); py = lerp(ty, by_, v)
                if OS["night"]: g.append(f'<rect x="{px:.1f}" y="{py:.1f}" width="2" height="2" fill="{random.choice(["#ffd88a", "#fff2c8", "#9fd3ff"])}" opacity=".85"/>')
                else: g.append(f'<rect x="{px - 2:.1f}" y="{py:.1f}" width="{random.uniform(3, 6):.1f}" height="{by_ - py:.1f}" fill="#9fb6cc" opacity=".45"/>')
            for t in (0.0, 0.34, 0.67, 1.0):
                px = lerp(ex, ix, t); g.append(f'<line x1="{px:.1f}" y1="{lerp(y, top, t):.1f}" x2="{px:.1f}" y2="{lerp(y + h, wb, t):.1f}" stroke="{OS["trim"]}" stroke-width="{3 if t in (0.0, 1.0) else 2}"/>')
            g.append(f'<line x1="{ex}" y1="{lerp(y, y + h, 0.62):.1f}" x2="{ix}" y2="{lerp(top, wb, 0.62):.1f}" stroke="{OS["trim"]}" stroke-width="1.6" opacity=".7"/>')
    # 바닥 (원근)
    fq = [(x + dx, wb), (x + w - dx, wb), (x + w, y + h), (x, y + h)]
    g.append(poly(fq, OS["floor"]))
    lanes = {"herring": 14, "marble": 6, "stone": 8}[OS["floor_kind"]]
    for i in range(lanes):
        if i % 2: continue
        a0, a1 = i / lanes, (i + 1) / lanes
        g.append(poly([(lerp(x + dx, x + w - dx, a0), wb), (lerp(x + dx, x + w - dx, a1), wb), (lerp(x, x + w, a1), y + h), (lerp(x, x + w, a0), y + h)], OS["floor2"]))
    rows = 7 if OS["floor_kind"] == "herring" else 4
    for k in range(1, rows):
        f = (k / rows) ** 1.45; yy = lerp(wb, y + h, f)
        g.append(f'<line x1="{lerp(x + dx, x, f):.1f}" y1="{yy:.1f}" x2="{lerp(x + w - dx, x + w, f):.1f}" y2="{yy:.1f}" stroke="{OS["floor_line"]}" stroke-width="1" opacity=".8"/>')
    if OS["floor_kind"] == "stone":
        g.append(poly(fq, grad("linearGradient", [(0, "#ffffff", 0), (1, "#ffffff", 0.07)], x1=0, y1=0, x2=0, y2=1)))
    # 벽 조명 · 바닥 빛 웅덩이
    lg = grad("radialGradient", [(0, OS["light"], OS["light_op"]), (1, OS["light"], 0)])
    for fx in (0.28, 0.72):
        g.append(f'<ellipse cx="{x + w * fx:.1f}" cy="{lerp(wb, y + h, 0.55):.1f}" rx="{w * 0.26:.1f}" ry="{(y + h - wb) * 0.32:.1f}" fill="{lg}"/>')
    sg = grad("radialGradient", [(0, OS["sconce"], 0.7), (1, OS["sconce"], 0)])
    for sx in (x + dx + 22, x + w - dx - 22):
        g.append(f'<ellipse cx="{sx}" cy="{top + 46}" rx="26" ry="34" fill="{sg}"/><rect x="{sx - 4}" y="{top + 36}" width="8" height="16" rx="3" fill="{OS["trim"]}"/><path d="M {sx - 9},{top + 36} L {sx + 9},{top + 36} L {sx + 6},{top + 26} L {sx - 6},{top + 26} Z" fill="{OS["sconce"]}"/>')
    if door_side: g.append(door(x, y, w, h, dx, wb, bh, door_side))
    return g, (top, wb, dx)

def close(g, x, y, w, h):
    g.append("</g>")
    g.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="none" stroke="{OS["trim"]}" stroke-width="3"/>')
    if OS["glass"]: g.append(f'<rect x="{x + 6}" y="{y + 4}" width="{w - 12}" height="2" rx="1" fill="#ffffff" opacity=".5"/>')
    return g

def plant(cx, by, s=1.0):
    g = f'<path d="M {cx - 14 * s},{by - 26 * s} L {cx + 14 * s},{by - 26 * s} L {cx + 11 * s},{by} L {cx - 11 * s},{by} Z" fill="{"#f2efe8" if not OS["night"] else "#2a3040"}" stroke="{OS["trim"]}" stroke-width="1.4"/>'
    for i, (dx_, dy, rx, ry, rot) in enumerate([(-12, -44, 8, 20, -30), (10, -48, 8, 22, 28), (0, -58, 7, 22, 0), (-20, -34, 7, 16, -55), (20, -36, 7, 16, 55)]):
        c = ["#2f7d4a", "#3f9a5a", "#2a6e42", "#4aa866", "#358a50"][i]
        g += f'<ellipse cx="{cx + dx_ * s}" cy="{by + dy * s}" rx="{rx * s}" ry="{ry * s}" fill="{c}" transform="rotate({rot} {cx + dx_ * s} {by + dy * s})"/>'
    return g

def plaque(x, y, no, name, color, badge=None, sub=None):
    w = tw(name, 19) + (56 if no else 36); s = f'<rect x="{x}" y="{y}" width="{w}" height="34" rx="9" fill="{OS["plaque"]}" stroke="{OS["trim"]}" stroke-width="1.4"/>'
    if no: s += f'<circle cx="{x + 18}" cy="{y + 17}" r="11" fill="{color}"/>' + T(x + 18, y + 21.5, no, 11, "#ffffff", anchor="middle") + T(x + 36, y + 24, name, 19, OS["plaque_text"])
    else: s += f'<rect x="{x + 10}" y="{y + 10}" width="10" height="14" rx="3" fill="{color}"/>' + T(x + 28, y + 24, name, 19, OS["plaque_text"])
    if badge:
        bt, on = badge; bw = tw(bt, 13) + 20
        s += f'<rect x="{x + w + 8}" y="{y + 6}" width="{bw}" height="22" rx="11" fill="{"#2f9a5a" if on else "#8a909c"}"/>' + T(x + w + 18, y + 22, bt, 13, "#ffffff")
    return s

def bubble(cx, bottom, t, bg="#ffffff", sz=13):
    w = tw(t, sz) + 22; h = sz + 14; x0 = cx - w / 2; y0 = bottom - h - 9
    return (f'<rect x="{x0 + 1}" y="{y0 + 3}" width="{w}" height="{h}" rx="11" fill="#000" opacity=".18"/><rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="11" fill="{bg}" stroke="#d8cdbb" stroke-width="1.2"/>'
            f'<path d="M {cx - 6},{y0 + h - 1} L {cx + 6},{y0 + h - 1} L {cx},{y0 + h + 8} Z" fill="{bg}"/>' + T(cx, y0 + h - 8, t, sz, "#2b2018", anchor="middle"))

def dot(x, y, state):
    if state == "on": return f'<circle cx="{x}" cy="{y}" r="10" fill="#34c46c" opacity=".25"/><circle cx="{x}" cy="{y}" r="6" fill="#34c46c" stroke="#ffffff" stroke-width="2"/>'
    if state == "away": return f'<circle cx="{x}" cy="{y}" r="6" fill="#c9a45c" stroke="#ffffff" stroke-width="2"/>'
    return f'<circle cx="{x}" cy="{y}" r="5" fill="#b4bac4" stroke="#ffffff" stroke-width="1.6"/>'

def char(lk, cx, desk_y, s, team, working, pose="type", stand=False):
    n = nid()
    if stand:
        sv = sc.svg(lk, n, team=team, working=working, pose=pose, size=(240 * s, 400 * s))
        return sv.replace("<svg ", f'<svg x="{cx - 120 * s:.1f}" y="{desk_y - 385 * s:.1f}" ', 1)
    sv = sc.svg(lk, n, team=team, working=working, pose=pose, size=(240 * s, 292 * s), view="-120 -180 240 292")
    return sv.replace("<svg ", f'<svg x="{cx - 120 * s:.1f}" y="{desk_y - 280 * s:.1f}" ', 1)

DESK = {"월넛라운지": ("#9a6844", "#6e4630", "#b78258"), "마블펜트하우스": ("#f7f6f2", "#2a2d33", "#ffffff"), "나이트스카이": ("#2a3142", "#161b26", "#c9a45c")}[A.office]
def desk(x0, x1, yt, depth=12, panel=22):
    top, front, edge = DESK
    return (f'<polygon points="{x0 + 8},{yt - depth} {x1 - 8},{yt - depth} {x1},{yt} {x0},{yt}" fill="{top}" stroke="{mix(front, "#000000", 0.2)}" stroke-width="1"/>'
            f'<rect x="{x0}" y="{yt}" width="{x1 - x0}" height="{panel}" fill="{front}"/><rect x="{x0}" y="{yt}" width="{x1 - x0}" height="2" fill="{edge}" opacity=".8"/>'
            f'<rect x="{x0 + 6}" y="{yt + panel}" width="6" height="8" fill="{front}"/><rect x="{x1 - 12}" y="{yt + panel}" width="6" height="8" fill="{front}"/>')

def chair(cx, yt, s):
    c = "#2b2a33" if not OS["night"] else "#3a3448"
    return f'<rect x="{cx - 38 * s:.1f}" y="{yt - 150 * s:.1f}" width="{76 * s:.1f}" height="{150 * s:.1f}" rx="{18 * s:.1f}" fill="{c}"/><rect x="{cx - 30 * s:.1f}" y="{yt - 142 * s:.1f}" width="{60 * s:.1f}" height="{10 * s:.1f}" rx="{4 * s:.1f}" fill="#ffffff" opacity=".12"/>'

def laptop(cx, yt, s, on, team):
    w, h = 54 * s, 30 * s
    g = f'<rect x="{cx - w / 2:.1f}" y="{yt - h:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{3 * s:.1f}" fill="#d9dde3" stroke="#9aa3ad" stroke-width="1"/>'
    if on: g += f'<circle cx="{cx}" cy="{yt - h / 2:.1f}" r="{4.5 * s:.1f}" fill="{team}"/><ellipse cx="{cx}" cy="{yt - h - 4:.1f}" rx="{w * 0.7:.1f}" ry="{8 * s:.1f}" fill="{team}" opacity=".15"/>'
    else: g = f'<rect x="{cx - w / 2:.1f}" y="{yt - 5 * s:.1f}" width="{w:.1f}" height="{5 * s:.1f}" rx="2" fill="#c9ced6"/>' + f'<rect x="{cx + w / 2 + 4:.1f}" y="{yt - 14 * s:.1f}" width="{11 * s:.1f}" height="{13 * s:.1f}" rx="2" fill="#ffffff" stroke="#c9bfae"/>'
    return g

# ───────────── 방별 벽 장식 ─────────────
def decor(key, x, w, top, dx):
    R = x + w - dx - 14; s = ""; gold = "#c9a45c"
    fr = lambda a, b, c, d, inner="#ffffff": f'<rect x="{a}" y="{b}" width="{c - a}" height="{d - b}" rx="3" fill="{gold}"/><rect x="{a + 4}" y="{b + 4}" width="{c - a - 8}" height="{d - b - 8}" rx="2" fill="{inner}"/>'
    if key == "scout":
        s += fr(R - 118, top + 16, R, top + 96, "#efe6c8") + f'<path d="M {R - 104},{top + 50} q 20,-22 44,-8 q 18,10 30,-6 l 6,30 q -30,18 -52,6 q -18,-8 -28,6 Z" fill="#a8d2a0"/><path d="M {R - 60},{top + 74} q 22,-10 40,4 l -2,12 q -20,4 -38,-4 Z" fill="#a9cbe8"/>'
        s += "".join(f'<circle cx="{a}" cy="{b}" r="4" fill="#d9493b" stroke="#fff" stroke-width="1.2"/>' for a, b in ((R - 84, top + 44), (R - 44, top + 62), (R - 28, top + 38)))
    elif key == "analysis":
        s += f'<rect x="{R - 130}" y="{top + 14}" width="130" height="86" rx="6" fill="#ffffff" opacity=".92" stroke="#c9ced6" stroke-width="2"/>'
        s += "".join(f'<rect x="{R - 118 + i * 17}" y="{top + 88 - hh}" width="11" height="{hh}" rx="2" fill="{c}"/>' for i, (hh, c) in enumerate(((22, "#5f95db"), (38, "#e07a68"), (30, "#5cb87a"), (50, "#e6ad3c"))))
        s += f'<circle cx="{R - 30}" cy="{top + 54}" r="22" fill="#5f95db"/><path d="M {R - 30},{top + 54} L {R - 30},{top + 32} A 22,22 0 0 1 {R - 9},{top + 60} Z" fill="#e6ad3c"/><circle cx="{R - 30}" cy="{top + 54}" r="10" fill="#ffffff"/>'
    elif key in ("build", "audit"):
        bw = 150 if key == "build" else 96; bx = R - bw - (64 if key == "audit" else 0)
        s += f'<rect x="{bx}" y="{top + 12}" width="{bw}" height="92" rx="4" fill="#4a2f22"/>'
        for row in range(3):
            yy = top + 16 + row * 30; xx = bx + 6
            while xx < bx + bw - 10:
                bwid = random.choice([6, 7, 8, 9]); bh_ = random.uniform(18, 25)
                col = random.choice(["#8e2f28", "#5a1f1a", "#9c3a2e", "#3b2a1f", "#2f3b52"]) if key == "audit" else random.choice(["#b85c4c", "#5677a8", "#d9b25f", "#6b9a6a", "#8d6bb0", "#e8dcc4", "#2f3b52"])
                s += f'<rect x="{xx}" y="{yy + 26 - bh_:.1f}" width="{bwid}" height="{bh_:.1f}" fill="{col}"/>'; xx += bwid + 1
            s += f'<rect x="{bx + 4}" y="{yy + 26}" width="{bw - 8}" height="3" fill="#6e4630"/>'
        if key == "audit":
            s += fr(R - 56, top + 14, R, top + 98, "#fbf5e6"); c = R - 28
            s += f'<path d="M {c},{top + 26} L {c},{top + 84} M {c - 20},{top + 36} L {c + 20},{top + 36}" stroke="#a88238" stroke-width="3"/>' + "".join(f'<path d="M {c + d - 9},{top + 50} A 9,9 0 0 0 {c + d + 9},{top + 50} Z" fill="#d9b25f"/><path d="M {c + d},{top + 36} L {c + d - 8},{top + 50} M {c + d},{top + 36} L {c + d + 8},{top + 50}" stroke="#a88238" stroke-width="1"/>' for d in (-18, 18))
    elif key == "mail":
        s += f'<rect x="{R - 150}" y="{top + 14}" width="150" height="88" rx="4" fill="#4a2f22"/>'
        for i in range(6):
            for j in range(3):
                bx, by = R - 146 + i * 24.5, top + 18 + j * 27.5
                s += f'<rect x="{bx}" y="{by}" width="21" height="24" fill="#2e1d14"/>'
                if (i + j) % 3: s += f'<rect x="{bx + 3}" y="{by + 10}" width="15" height="11" fill="#fbf6ec"/><path d="M {bx + 3},{by + 10} L {bx + 10.5},{by + 16} L {bx + 18},{by + 10}" stroke="#d8cdbb" fill="none"/>'
    elif key == "pt":
        s += f'<rect x="{R - 156}" y="{top + 8}" width="156" height="4" fill="#3a3f48"/><rect x="{R - 150}" y="{top + 12}" width="144" height="88" fill="#ffffff" stroke="#cfd4dc"/>'
        s += f'<rect x="{R - 138}" y="{top + 24}" width="70" height="7" rx="2" fill="#e6ad3c"/>' + "".join(f'<rect x="{R - 138}" y="{top + 40 + k * 12}" width="{60 - k * 8}" height="5" rx="2" fill="#c8ccd4"/>' for k in range(4))
        s += f'<circle cx="{R - 40}" cy="{top + 58}" r="24" fill="#f6e2b4"/><path d="M {R - 40},{top + 58} L {R - 40},{top + 34} A 24,24 0 0 1 {R - 17},{top + 64} Z" fill="#e6ad3c"/>'
    elif key == "retro":
        for i in range(3):
            mx = R - 176 + i * 59
            s += f'<rect x="{mx}" y="{top + 18}" width="55" height="40" rx="4" fill="#141a26" stroke="#3a4252" stroke-width="2"/>'
            pts = " ".join(f"{mx + 6 + k * 9},{top + 50 - ((k * 7 + i * 5) % 22)}" for k in range(6))
            s += f'<polyline points="{pts}" fill="none" stroke="#4fb8b0" stroke-width="2"/>'
        s += f'<circle cx="{R - 88}" cy="{top + 82}" r="13" fill="#ffffff" stroke="{gold}" stroke-width="3"/><path d="M {R - 88},{top + 82} L {R - 88},{top + 74} M {R - 88},{top + 82} L {R - 82},{top + 85}" stroke="#1b2433" stroke-width="2"/>'
    return s

# ───────────── 팀 사무실 ─────────────
def team_room(key, x, y):
    no, name, color, n, sub = TEAM[key]; busy, label = WORK[key]
    g, (top, wb, dx) = shell(x, y, CW, RH, team=color, door_side="left" if x == CX[3] else "right")
    g.append(decor(key, x, CW, top, dx))
    rug_c = mix(color, OS["floor"], OS["rug_mix"])
    g.append(poly([(x + 70, wb + 22), (x + CW - 70, wb + 22), (x + CW - 30, y + RH - 10), (x + 30, y + RH - 10)], rug_c, f'stroke="{OS["trim"]}" stroke-width="1.6" opacity=".95"'))
    back, front = (n + 1) // 2, n // 2
    looks = sc.ROSTER[key]; order = list(range(n)); occ = set(order[:busy]); away = set() if ASSETS else set(order[busy:busy + AWAY.get(key, 0)])
    mx = max(back, front); sp = min(100, (CW - 70) / mx); sf = min(0.46, sp / 205)
    rows = [(back, y + 222, sf * 0.84, sp * 0.86, 0), (front, y + 306, sf, sp, back)]
    heads, report = [], None
    for cnt, yt, s, sp, off in rows:
        if not cnt: continue
        cx0 = x + CW / 2 - (cnt - 1) * sp / 2
        g.append(desk(cx0 - sp / 2 - 6, cx0 + (cnt - 1) * sp + sp / 2 + 6, yt, panel=int(70 * s)))
        for j in range(cnt):
            i = off + j; sx = cx0 + j * sp
            g.append(chair(sx, yt, s))
            if ASSETS:
                n_ = sc.ROSTER[key][i]; hy = yt - (230 if n_["hat"] else 172) * s; box = (sx - 120 * s, yt - 280 * s, 240 * s, 280 * s + 8)
                seat = {"team": key, "i": i, "name": n_["name"], "hx": round(sx, 1), "hy": round(hy, 1), "fx": round(sx, 1), "fy": round(yt + 4, 1),
                        "work": sprite(f"seat_{key}_{i}_work.svg", box, char(n_, sx, yt, s, color, True) + laptop(sx, yt, s, True, color)),
                        "idle": sprite(f"seat_{key}_{i}_idle.svg", box, char(n_, sx, yt, s, color, False) + laptop(sx, yt, s, False, color))}
                st_svg = sc.svg(n_, nid(), team=color, working=True, pose="side", size=(240 * 0.34, 400 * 0.34))
                open(os.path.join(ASSETS, f"stand_{key}_{i}.svg"), "w", encoding="utf-8").write(st_svg)
                seat["stand"] = {"file": f"stand_{key}_{i}.svg", "w": 240 * 0.34, "h": 400 * 0.34, "feet": (205 + 180) / 400}
                LAYOUT["seats"].setdefault(key, []).append(seat); continue
            if i in away:
                report = looks[i]; heads.append((sx, yt - 120 * s, "away")); g.append(laptop(sx, yt, s, False, color)); continue
            g.append(char(looks[i], sx, yt, s, color, i in occ))
            g.append(laptop(sx, yt, s, i in occ, color)); heads.append((sx, yt - (230 if looks[i]["hat"] else 172) * s, "on" if i in occ else "off"))
    g.append(plant(x + 26, y + RH - 14, 0.9)); g.append(plant(x + CW - 26, y + RH - 14, 0.9))
    g = close(g, x, y, CW, RH)
    g.append(plaque(x + dx + 8, top + 8, no, name, color))
    if ASSETS:
        LAYOUT["rooms"][key] = {"x": x, "y": y, "w": CW, "h": RH, "badge": [x + dx + 8, top + 48], "door": DOORS[(x, y)], "row": 0 if y == R1 else 1, "name": name, "color": color, "n": n}
        return g, None
    g.append(f'<rect x="{x + dx + 8}" y="{top + 48}" width="{tw(f"작업 {busy} / {n}석", 13) + 20}" height="22" rx="11" fill="{"#2f9a5a" if busy else "#8a909c"}"/>' + T(x + dx + 18, top + 64, f"작업 {busy} / {n}석", 13, "#ffffff"))
    for hx, hy, st in heads:
        g.append(dot(hx + 18, hy, st))
        if st == "away": g.append(f'<rect x="{hx - 28}" y="{hy + 6}" width="56" height="22" rx="11" fill="#1b2433" stroke="#c9a45c"/>' + T(hx, hy + 21, "보고 중", 12, "#ffe7a6", anchor="middle"))
    lead = [h for h in heads if h[2] == "on"]
    if lead:
        hx, hy, _ = lead[1] if key == "audit" and len(lead) > 1 else lead[0]
        bw = tw(label, 13) + 22; g.append(bubble(min(max(hx, x + 20 + bw / 2), x + CW - 20 - bw / 2), hy - 8, label))
    return g, report

# ───────────── 본부장실 ─────────────
def boss_room(x, y, reporter):
    g, (top, wb, dx) = shell(x, y, CW, RH, door_side="left")
    if not OS["glass"]:
        g.append(f'<rect x="{x + CW - dx - 150}" y="{top + 12}" width="136" height="96" rx="4" fill="#4a2f22"/><rect x="{x + CW - dx - 146}" y="{top + 16}" width="128" height="88" fill="#bcd6ea"/>')
        g.append("".join(f'<rect x="{x + CW - dx - 144 + i * 21}" y="{top + 104 - hh}" width="17" height="{hh}" fill="#9fb6cc"/>' for i, hh in enumerate((40, 58, 30, 66, 46, 36))))
        g.append(f'<rect x="{x + CW - dx - 84}" y="{top + 16}" width="4" height="88" fill="#4a2f22"/>')
    else:
        g.append(f'<rect x="{x + CW - dx - 120}" y="{top + 18}" width="106" height="80" rx="4" fill="{mix(OS["wall"], "#000000", 0.15)}" stroke="{OS["trim"]}"/>' + T(x + CW - dx - 67, top + 66, "EDGE", 20, OS["trim"], 800, "middle", 'letter-spacing="3"'))
    g.append(poly([(x + 60, wb + 26), (x + CW - 60, wb + 26), (x + CW - 24, y + RH - 10), (x + 24, y + RH - 10)], mix("#b48a5a", OS["floor"], 0.4), f'stroke="{OS["trim"]}" stroke-width="1.6"'))
    cx, yt, s = x + CW / 2 + 40, y + 268, 0.5
    g.append(f'<rect x="{cx - 50 * s:.1f}" y="{yt - 190 * s:.1f}" width="{100 * s:.1f}" height="{190 * s:.1f}" rx="{24 * s:.1f}" fill="#5a2f25"/>')
    if ASSETS:
        LAYOUT["boss"] = {"sprite": sprite("boss_work.svg", (cx - 90, yt - 280 * s, 180, 280 * s + 8), char(sc.BOSS_LOOK, cx, yt, s, None, True, pose="type") + laptop(cx - 62, yt, 0.4, True, "#c9a45c")),
                          "hx": cx, "hy": yt - 232 * s, "spot": [x + 96, y + RH - 20], "door": DOORS[(x, y)], "room": {"x": x, "y": y, "w": CW, "h": RH}, "name": sc.BOSS_LOOK["name"]}
    else: g.append(char(sc.BOSS_LOOK, cx, yt, s, None, True, pose="type"))
    top_, front, edge = DESK
    g.append(f'<polygon points="{cx - 100},{yt - 14} {cx + 100},{yt - 14} {cx + 112},{yt} {cx - 112},{yt}" fill="{top_}" stroke="{mix(front, "#000000", 0.2)}"/><rect x="{cx - 112}" y="{yt}" width="224" height="40" fill="{front}"/><rect x="{cx - 112}" y="{yt}" width="224" height="2" fill="{edge}"/>')
    g.append(f'<rect x="{cx + 40}" y="{yt + 8}" width="52" height="14" rx="2" fill="#c9a45c"/>' + T(cx + 66, yt + 19, "본부장", 9, "#1b2433", 800, "middle"))
    if not ASSETS: g.append(laptop(cx - 62, yt, 0.4, True, "#c9a45c"))
    if reporter and not ASSETS: g.append(char(reporter, x + 96, y + RH - 20, 0.34, TEAM["audit"][2], True, pose="hold", stand=True))
    g.append(plant(x + CW - 26, y + RH - 14, 0.9))
    g = close(g, x, y, CW, RH)
    g.append(plaque(x + dx + 8, top + 8, "", "본부장실", "#c9a45c"))
    if ASSETS: return g
    if reporter: g.append(bubble(x + 120, y + RH - 16 - 385 * 0.34 + 34, f"{reporter['name']}: 검증 결과 보고드립니다", sz=12))
    g.append(bubble(cx + 50, yt - 240 * s, "확인! 수고했어!", bg="#fff6dc", sz=12))
    g.append(dot(cx + 30, yt - 232 * s, "on"))
    gx = CX[3] + CW / 2
    return g

# ───────────── 상황실 (현황판) ─────────────
def board_room(x, y, w, h):
    g, (top, wb, dx) = shell(x, y, w, h, dx=60, bh=372)
    BX0, BY0, BX1, BY1 = x + dx + 18, top + 52, x + w - dx - 18, wb - 30
    g.append(f'<rect x="{BX0 - 5}" y="{BY0 - 5}" width="{BX1 - BX0 + 10}" height="{BY1 - BY0 + 10}" rx="14" fill="{OS["board_frame"]}"/><rect x="{BX0}" y="{BY0}" width="{BX1 - BX0}" height="{BY1 - BY0}" rx="10" fill="{grad("linearGradient", [(0, "#1d2740", 1), (1, OS["board"], 1)], x1=0, y1=0, x2=0, y2=1)}"/>')
    if ASSETS:
        LAYOUT["board"] = {"x": BX0, "y": BY0, "w": BX1 - BX0, "h": BY1 - BY0}
        g.append(plant(x + 40, y + h - 10, 1.0)); g.append(plant(x + w - 40, y + h - 10, 1.0)); g = close(g, x, y, w, h)
        g.append(plaque(x + dx + 18, top + 10, "", "상황실 · 단지 현황판", "#c9a45c"))
        g.append(f'<rect x="{x + dx + 270}" y="{top + 16}" width="150" height="22" rx="11" fill="#2f9a5a"/>' + T(x + dx + 345, top + 32, "입찰현황판.md 실시간", 12, "#ffffff", anchor="middle"))
        lx = x + w - dx - 470
        g.append(f'<rect x="{lx}" y="{top + 12}" width="452" height="30" rx="15" fill="#fffaf0" stroke="#dccfb7"/>' + dot(lx + 20, top + 27, "on") + T(lx + 34, top + 32, "작업 중", 13, "#2b2018")
                 + dot(lx + 112, top + 27, "off") + T(lx + 124, top + 32, "자리 대기(눈 감고 휴식)", 13, "#2b2018") + dot(lx + 300, top + 27, "away") + T(lx + 312, top + 32, "본부장실 보고 중", 13, "#2b2018"))
        return g
    rows = json.load(open(os.path.join(HERE, "board_snap.json"), encoding="utf-8")); today = datetime.date.today()
    STG = [("scout", "#d9a441"), ("analysis", "#5f95db"), ("build", "#5cb87a"), ("audit", "#e07a68"), ("ready", "#ef8a3c"), ("mail", "#a77fd6"), ("pt", "#e6ad3c"), ("retro", "#4fb8b0")]
    RIGHT = BX0 + 1010; yy = BY0 + 14; pt = next((q for q in rows if q["pt_ok"]), None)
    if pt:
        dd = (datetime.date.fromisoformat(pt["pt_date"]) - today).days
        g.append(f'<rect x="{BX0 + 14}" y="{yy}" width="{RIGHT - BX0 - 14}" height="36" rx="9" fill="#3a3018" stroke="#c9a45c" stroke-width="1.4"/><rect x="{BX0 + 24}" y="{yy + 7}" width="100" height="22" rx="11" fill="#c9a45c"/>' + T(BX0 + 74, yy + 23, "2차 PT 확정", 12, "#2a2210", anchor="middle"))
        g.append(T(BX0 + 138, yy + 25, f"{pt['name']}    11.08(일) {pt['pt_time']}    {pt['pt_place']}", 17, "#ffe7a6"))
        g.append(f'<rect x="{RIGHT - 66}" y="{yy + 7}" width="54" height="22" rx="11" fill="#c9a45c"/>' + T(RIGHT - 39, yy + 23, f"D-{dd}", 12, "#2a2210", anchor="middle")); yy += 50
    cols = [BX0 + 24, BX0 + 130, BX0 + 290, BX0 + 380, BX0 + 760]
    for c, t in zip(cols, ["단지", "마감", "D-day", "단계   개척 · 착수 · 제작 · 검증 · 발송대기 · 발송 · PT · 결과", "PT 일정"]): g.append(T(c, yy + 12, t, 11, "#7f8aa0"))
    yy += 22; allr = [q for q in rows if not q["pt_ok"]]; RH_ = 27; vis = int((BY1 - 14 - yy) // RH_)
    for q in allr[:vis]:
        g.append(f'<line x1="{BX0 + 16}" y1="{yy - 3}" x2="{RIGHT}" y2="{yy - 3}" stroke="#222c3e"/>')
        g.append(T(cols[0], yy + 16, q["site"], 15, "#ffffff")); g.append(T(cols[1], yy + 16, q["due"].split(" (")[0].split("까지")[0][:15], 12, "#c3cbd8", 400))
        if q["done"]: g.append(f'<rect x="{cols[2]}" y="{yy + 2}" width="48" height="20" rx="10" fill="#2c6e4c"/>' + T(cols[2] + 24, yy + 16, "제출", 11, "#d9f5e4", anchor="middle"))
        else: g.append(f'<rect x="{cols[2]}" y="{yy + 2}" width="48" height="20" rx="10" fill="{"#c9483b" if q["dday"] <= 3 else "#5a6273"}"/>' + T(cols[2] + 24, yy + 16, f"D-{q['dday']}", 11, "#ffffff", anchor="middle"))
        st = q["stage"] or "analysis"; idx = [k for k, _ in STG].index(st)
        for i, (_, c) in enumerate(STG):
            px, py = cols[3] + 12 + i * 42, yy + 12
            if i < len(STG) - 1: g.append(f'<line x1="{px + 6}" y1="{py}" x2="{px + 36}" y2="{py}" stroke="{c if i < idx else "#2c3547"}" stroke-width="2"/>')
            if i < idx: g.append(f'<circle cx="{px}" cy="{py}" r="5" fill="{c}"/>')
            elif i == idx: g.append(f'<circle cx="{px}" cy="{py}" r="11" fill="{c}" opacity=".35"/><circle cx="{px}" cy="{py}" r="7" fill="{c}" stroke="#fff" stroke-width="2"/>')
            else: g.append(f'<circle cx="{px}" cy="{py}" r="4" fill="none" stroke="#3f4a5e" stroke-width="1.5"/>')
        g.append(T(cols[4], yy + 16, q["pt"][:28], 12, "#f2cf7a" if q["pt_date"] else "#7f8aa0", 400)); yy += RH_
    tr_t, tr_b = BY0 + 60, BY1 - 16; th = max(30, (tr_b - tr_t) * min(1, vis / max(1, len(allr))))
    g.append(f'<rect x="{RIGHT - 4}" y="{tr_t}" width="7" height="{tr_b - tr_t}" rx="3.5" fill="#232d40"/><rect x="{RIGHT - 4}" y="{tr_t}" width="7" height="{th:.0f}" rx="3.5" fill="#8592ab"/>')
    PX = RIGHT + 22
    g.append(f'<rect x="{PX}" y="{BY0 + 14}" width="{BX1 - PX - 14}" height="{BY1 - BY0 - 28}" rx="10" fill="#1b2436" stroke="#2b3549"/>' + T(PX + 16, BY0 + 40, "다가오는 일정", 15, "#ffffff"))
    ev = []
    for q in rows:
        if not q["done"] and q["dday"] is not None and q["dday"] >= 0: ev.append((today + datetime.timedelta(days=q["dday"]), "마감", q["site"], "#c9483b", "#ffffff"))
        if q["pt_date"] and datetime.date.fromisoformat(q["pt_date"]) >= today:
            ev.append((datetime.date.fromisoformat(q["pt_date"]), "PT 확정" if q["pt_ok"] else "PT", q["site"], "#c9a45c" if q["pt_ok"] else "#6d5a30", "#2a2210" if q["pt_ok"] else "#f2dca0"))
    ey = BY0 + 64
    for dte, kind, site, c, fg in sorted(ev)[:int((BY1 - 20 - ey) // 30)]:
        dd = (dte - today).days; kw = tw(kind, 11) + 14
        g.append(T(PX + 16, ey + 14, f"{dte.month}.{dte.day:02d}({'월화수목금토일'[dte.weekday()]})", 12, "#c3cbd8", 400))
        g.append(f'<rect x="{PX + 100}" y="{ey}" width="{kw}" height="20" rx="10" fill="{c}"/>' + T(PX + 100 + kw / 2, ey + 14, kind, 11, fg, anchor="middle"))
        g.append(T(PX + 108 + kw, ey + 15, site, 14, "#ffffff")); g.append(T(BX1 - 28, ey + 15, f"D-{dd}", 12, "#ff8a7a" if dd <= 3 else "#7f8aa0", 700, "end")); ey += 30
    # 바닥: 소파 · 화분
    g.append(plant(x + 40, y + h - 10, 1.0)); g.append(plant(x + w - 40, y + h - 10, 1.0))
    g = close(g, x, y, w, h)
    g.append(plaque(x + dx + 18, top + 10, "", "상황실 · 단지 현황판", "#c9a45c"))
    g.append(f'<rect x="{x + dx + 270}" y="{top + 16}" width="150" height="22" rx="11" fill="#2f9a5a"/>' + T(x + dx + 345, top + 32, "입찰현황판.md 실시간", 12, "#ffffff", anchor="middle"))
    lx = x + w - dx - 470
    g.append(f'<rect x="{lx}" y="{top + 12}" width="452" height="30" rx="15" fill="#fffaf0" stroke="#dccfb7"/>' + dot(lx + 20, top + 27, "on") + T(lx + 34, top + 32, "작업 중", 13, "#2b2018")
             + dot(lx + 112, top + 27, "off") + T(lx + 124, top + 32, "자리 대기(눈 감고 휴식)", 13, "#2b2018") + dot(lx + 300, top + 27, "away") + T(lx + 312, top + 32, "본부장실 보고 중", 13, "#2b2018"))
    return g

# ───────────── 맨 위 띠 ─────────────
def header():
    g = [f'<rect x="0" y="0" width="{W}" height="80" fill="{grad("linearGradient", [(0, OS["header"], 1), (1, OS["header2"], 1)], x1=0, y1=0, x2=0, y2=1)}"/><rect x="0" y="78" width="{W}" height="2" fill="#c9a45c"/>']
    g.append(T(28, 48, "AI 주관사업부 오피스", 26, "#fbf3e2") + T(312, 46, f"EDGE COMPANY · {OS['name']} · {sc.STYLE_NAME.get('B', '')}", 13, "#c9a45c", 400))
    now = datetime.datetime.now(); cx = W / 2 + 70
    g.append(f'<rect x="{cx - 112}" y="12" width="224" height="56" rx="28" fill="#fbf6ec" stroke="#c9a45c" stroke-width="2"/><circle cx="{cx - 80}" cy="40" r="14" fill="#f3b63e" stroke="#e09a20" stroke-width="2"/>')
    g.append(T(cx - 56, 52, now.strftime("%H:%M"), 30, "#1b2433") + T(cx + 50, 46, f"{now.month}.{now.day}({'월화수목금토일'[now.weekday()]})", 13, "#8a7258"))
    nwork = sum(v[0] for v in WORK.values()); x = cx + 132
    for t, c in ((f"작업 중  {nwork}", "#2f9a5a"), ("내 답 대기  0", "#5a6273"), ("오늘 끝남  2", "#2f6fd0")):
        w = tw(t, 15) + 40; g.append(f'<rect x="{x}" y="22" width="{w}" height="36" rx="18" fill="{c}"/><circle cx="{x + 18}" cy="40" r="6" fill="#fff"/>' + T(x + 30, 46, t, 15, "#ffffff")); x += w + 10
    g.append(f'<rect x="{W - 150}" y="22" width="126" height="36" rx="18" fill="#263247" stroke="#3a4660"/><circle cx="{W - 132}" cy="40" r="6" fill="#5fe39a"/>' + T(W - 118, 46, "서버 연결됨", 14, "#c8f2d8"))
    return g

body, report = corridors(), None
for key, x, y in ROOMS:
    g, rep = team_room(key, x, y); body += g; report = report or rep
body += boss_room(CX[3], R2, report)
body += board_room(CX[0], R3, CX[3] + CW - CX[0], RH3)
if ASSETS:
    bg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs><filter id="blur" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="8"/></filter>{"".join(DEFS)}</defs>'
          f'<rect width="{W}" height="{H}" fill="{OS["bg"]}"/>' + "".join(body) + "</svg>")
    open(os.path.join(ASSETS, "bg.svg"), "w", encoding="utf-8").write(bg)
    LAYOUT.update(office=A.office, office_name=OS["name"], skin=A.skin, header=OS["header"], header2=OS["header2"], bg=OS["bg"], board_bg=OS["board"])
    json.dump(LAYOUT, open(os.path.join(ASSETS, "layout.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("assets", ASSETS, sum(len(v) for v in LAYOUT["seats"].values()), "seats"); raise SystemExit
HDR = "".join(header())
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs><filter id="blur" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="8"/></filter>{"".join(DEFS)}</defs>'
       f'<rect width="{W}" height="{H}" fill="{OS["bg"]}"/>' + HDR + "".join(body) + "</svg>")
page = f'<!doctype html><html><head><meta charset="utf-8"><style>body{{margin:0;background:{OS["bg"]}}}</style></head><body>{svg}</body></html>'
hp = os.path.join(HERE, f"office_{A.office}.html"); open(hp, "w", encoding="utf-8").write(page)
out = os.path.abspath(A.out or os.path.join(HERE, f"office_{A.office}_{A.skin}.png"))
subprocess.run([r"C:\Program Files\Google\Chrome\Application\chrome.exe", "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--screenshot={out}",
                f"--window-size={W},{H}", "--force-device-scale-factor=2", "file:///" + hp.replace("\\", "/")], check=True, capture_output=True)
print(out)
