# AI 주관사업부 오피스 v4 시안 — 3D 입체 사무실(뒷벽 · 옆벽 · 원근 바닥 · 조명) + 사무실 스킨 + 캐릭터 스킨
# 실행: python office_html.py --office 마블펜트하우스 --skin 원피스직원_v3 [-o 저장.png]   (크롬 헤드리스로 2배 해상도 저장)
import os, json, math, random, html, argparse, subprocess, importlib.util, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument("--office", default="어벤져스사무실"); ap.add_argument("--skin", default="마블직원_v1"); ap.add_argument("-o", "--out", default=""); ap.add_argument("--assets", default="")
A = ap.parse_args()
from office_skins import OFFICE_SKINS, ALIAS
A.office = ALIAS.get(A.office.replace(" ", ""), A.office)      # "기본배경1" · "원피스" · "어벤져스사무실" 로도 부름
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

W, H = 1920, 1440      # 4:3 (본부장 10-31 · 방을 옆으로 넓게)
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
CORR = 64; _free = W - 40 - 3 * CORR
CWS = [430, 520, 0, 389]; CWS[2] = _free - CWS[0] - CWS[1] - CWS[3]     # 03·04 제일 넓게 > 01·02 > 07·본부장(원래 389) > 05·06 제일 좁게 (본부장 10-31)
CX = [20 + sum(CWS[:i]) + i * CORR for i in range(4)]; CW = CWS[0]; CWOF = {CX[i]: CWS[i] for i in range(4)}
R1, RH = 100, 300; R2 = R1 + RH + CORR; R3 = R2 + RH + CORR; RH3 = H - R3 - 25     # 상황판 세로 더 크게 (본부장 10-31)
LAYOUT = {"W": W, "H": H, "seats": {}, "rooms": {}, "boss": {}, "board": {},
          "corrY": [R1 + RH + CORR / 2, R2 + RH + CORR / 2], "corrX": [CX[i] + CWS[i] + CORR / 2 for i in range(3)], "vX": CX[3] - CORR / 2}
DOORS = {}       # (방 x, y) → 문 안쪽 · 바깥쪽 좌표
ROOMS = [("scout", CX[0], R1), ("analysis", CX[0], R2), ("build", CX[1], R1), ("audit", CX[1], R2),      # 세로형 순서 (본부장 10-31)
         ("mail", CX[2], R1), ("pt", CX[2], R2), ("retro", CX[3], R1)]
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
FILTERS = (
    '<filter id="vein" x="0" y="0" width="100%" height="100%"><feTurbulence type="turbulence" baseFrequency="0.0045 0.016" numOctaves="3" seed="11"/>'
    '<feColorMatrix type="matrix" values="0 0 0 0 0.55  0 0 0 0 0.52  0 0 0 0 0.48  -7 0 0 0 1.05"/></filter>'
    '<filter id="vein2" x="0" y="0" width="100%" height="100%"><feTurbulence type="turbulence" baseFrequency="0.009 0.006" numOctaves="3" seed="4"/>'
    '<feColorMatrix type="matrix" values="0 0 0 0 0.62  0 0 0 0 0.6  0 0 0 0 0.56  -8 0 0 0 1.0"/></filter>'
    '<filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3"/></filter>')
def grad(kind, stops, **kw):
    i = nid(); at = " ".join(f'{k}="{v}"' for k, v in kw.items())
    DEFS.append(f'<{kind} id="g{i}" {at}>' + "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{op}"/>' for o, c, op in stops) + f'</{kind}>')
    return f"url(#g{i})"

# ───────────── 방(3D 상자) ─────────────
DOOR_W = 58
def front_glass(x, y, w, h):
    """방 앞쪽 아래 낮은 유리 칸막이 + 오른쪽 끝 유리문 (직원은 이 문으로 아래 복도에 나간다)"""
    gy, gh = y + h - 26, 26; d0 = x + w - 14 - DOOR_W; d1 = d0 + DOOR_W; fr = OS["trim"]; gold = "#c9a45c"
    g = f'<rect x="{x}" y="{gy}" width="{d0 - x}" height="{gh}" fill="#ffffff" opacity=".28"/><rect x="{d1}" y="{gy}" width="{x + w - d1}" height="{gh}" fill="#ffffff" opacity=".28"/>'
    g += f'<rect x="{x}" y="{gy}" width="{w}" height="2.4" fill="{fr}"/>'
    for xx in range(int(x) + 60, int(d0) - 10, 64): g += f'<rect x="{xx}" y="{gy}" width="2" height="{gh}" fill="{fr}" opacity=".55"/>'
    dt = gy - 62                                                   # 문 위끝
    dg = grad("linearGradient", [(0, "#cfe6f4", 0.85), (1, "#8fb9d6", 0.75)], x1=0, y1=0, x2=0, y2=1)
    lg = grad("linearGradient", [(0, "#fff4d6", 0), (1, "#fff4d6", 0.75)], x1=0, y1=0, x2=0, y2=1)
    g += f'<rect x="{d0 - 6}" y="{dt - 6}" width="{DOOR_W + 12}" height="{y + h - dt + 6}" rx="3" fill="{fr}"/>'                     # 문틀 (검은 철제)
    g += f'<rect x="{d0 - 3}" y="{dt - 3}" width="{DOOR_W + 6}" height="{y + h - dt + 3}" rx="2" fill="{gold}"/>'                     # 금색 안쪽 틀
    g += f'<rect x="{d0}" y="{dt}" width="{DOOR_W}" height="{y + h - dt}" fill="{dg}"/><rect x="{d0}" y="{y + h - 22}" width="{DOOR_W}" height="22" fill="{lg}"/>'
    g += f'<rect x="{d0 + DOOR_W / 2 - 1}" y="{dt}" width="2" height="{y + h - dt}" fill="{gold}" opacity=".9"/>'                      # 양문 가운데
    g += f'<path d="M {d0 + 5},{dt + 6} L {d0 + 17},{dt + 6} L {d0 + 5},{dt + 22} Z M {d0 + DOOR_W / 2 + 5},{dt + 6} L {d0 + DOOR_W / 2 + 13},{dt + 6} L {d0 + DOOR_W / 2 + 5},{dt + 16} Z" fill="#ffffff" opacity=".8"/>'
    g += f'<rect x="{d0 + DOOR_W / 2 - 6}" y="{dt + 26}" width="2.6" height="18" rx="1.3" fill="{gold}"/><rect x="{d0 + DOOR_W / 2 + 3.4}" y="{dt + 26}" width="2.6" height="18" rx="1.3" fill="{gold}"/>'
    g += f'<rect x="{d0 + 4}" y="{dt - 22}" width="{DOOR_W - 8}" height="15" rx="3" fill="#1b2433" stroke="{gold}"/>' + T(d0 + DOOR_W / 2, dt - 11, "출입", 10, "#ffe7a6", anchor="middle")
    cx = (d0 + d1) / 2
    DOORS[(x, y)] = {"in": [round(cx, 1), round(y + h - 30, 1)], "out": [round(cx, 1), round(y + h + CORR / 2 + 8, 1)], "aisle": round(cx, 1)}
    return g

def sunny_lion(cx, cy, r=22):
    """써니호 뱃머리 사자: 햇살처럼 뻗은 주황 갈기 · 노란 얼굴 · 큰 코 · 웃는 입"""
    g = "".join(f'<path d="M {cx + r * .7 * math.cos(math.radians(a - 9)):.1f},{cy + r * .7 * math.sin(math.radians(a - 9)):.1f} L {cx + r * 1.28 * math.cos(math.radians(a)):.1f},{cy + r * 1.28 * math.sin(math.radians(a)):.1f} L {cx + r * .7 * math.cos(math.radians(a + 9)):.1f},{cy + r * .7 * math.sin(math.radians(a + 9)):.1f} Z" fill="{"#f08c2c" if k % 2 else "#f6b23a"}" stroke="#7a3a10" stroke-width="1"/>' for k, a in enumerate(range(0, 360, 20)))
    g += f'<circle cx="{cx}" cy="{cy}" r="{r * .78:.1f}" fill="#f6d27a" stroke="#7a3a10" stroke-width="1.6"/>'
    g += "".join(f'<ellipse cx="{cx + sx * r * .28:.1f}" cy="{cy - r * .16:.1f}" rx="{r * .09:.1f}" ry="{r * .13:.1f}" fill="#2a1a0a"/><path d="M {cx + sx * r * .16:.1f},{cy - r * .34:.1f} q {sx * r * .12:.1f},{-r * .08:.1f} {sx * r * .24:.1f},0" stroke="#7a3a10" stroke-width="1.4" fill="none"/>' for sx in (-1, 1))
    g += f'<ellipse cx="{cx}" cy="{cy + r * .06:.1f}" rx="{r * .2:.1f}" ry="{r * .13:.1f}" fill="#c8602a"/><path d="M {cx - r * .32:.1f},{cy + r * .26:.1f} Q {cx},{cy + r * .56:.1f} {cx + r * .32:.1f},{cy + r * .26:.1f}" stroke="#7a3a10" stroke-width="1.6" fill="none"/>'
    g += "".join(f'<path d="M {cx + sx * r * .36:.1f},{cy + r * .14:.1f} l {sx * r * .3:.1f},{-r * .04 + k * r * .08:.1f}" stroke="#7a3a10" stroke-width="1"/>' for sx in (-1, 1) for k in (0, 1))
    return g

def vending(x, yb, body, label):
    """복도 자판기 (가로 46 · 세로 58): 몸통 · 진열창 음료 · 버튼 · 꺼내는 구멍 · 간판"""
    w, h = 46, 58; y = yb - h; dk = mix(body, "#000000", 0.35); lt = mix(body, "#ffffff", 0.3)
    g = f'<ellipse cx="{x + w / 2}" cy="{yb + 1}" rx="{w * .6}" ry="4" fill="#000" opacity=".22"/>'
    g += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{body}" stroke="{dk}" stroke-width="1.6"/><rect x="{x + 2}" y="{y + 2}" width="4" height="{h - 4}" fill="{lt}" opacity=".5"/>'
    g += f'<rect x="{x + 4}" y="{y + 3}" width="{w - 8}" height="9" rx="2" fill="#1b2433"/>' + T(x + w / 2, y + 10.4, label, 7, "#ffe7a6", 800, "middle")
    g += f'<rect x="{x + 5}" y="{y + 15}" width="{w - 18}" height="26" rx="2" fill="#cfeefb" stroke="{dk}" stroke-width="1"/>'
    cols = ["#e0402c", "#3a86e0", "#f2c230", "#5cb87a", "#a75ae0", "#f08c2c"]
    for r in range(3):
        for c in range(4):
            g += f'<rect x="{x + 7 + c * 6.6:.1f}" y="{y + 17 + r * 8.2:.1f}" width="4.6" height="6.6" rx="1.4" fill="{cols[(r * 4 + c) % 6]}"/>'
        g += f'<rect x="{x + 6}" y="{y + 24 + r * 8.2:.1f}" width="{w - 20}" height="1" fill="{dk}" opacity=".6"/>'
    g += "".join(f'<circle cx="{x + w - 8}" cy="{y + 18 + k * 7}" r="2.2" fill="{["#ffffff", "#ffe27a", "#9af4ff"][k]}" stroke="{dk}" stroke-width=".6"/>' for k in range(3))
    g += f'<rect x="{x + w - 11}" y="{y + 39}" width="6" height="2" fill="#1b2433"/>'
    g += f'<rect x="{x + 6}" y="{y + 45}" width="{w - 12}" height="9" rx="2" fill="#1b2433"/><rect x="{x + 8}" y="{y + 46}" width="{w - 16}" height="2" fill="#3a4454"/>'
    return g

def corridors():
    base = mix(OS["trim"], OS["bg"], 0.18) if not OS["night"] else mix(OS["bg"], "#000000", 0.25)
    run, gold = mix(base, "#ffffff", 0.10), OS.get("accent", "#c9a45c")
    lg = grad("radialGradient", [(0, "#fff3d4", 0.30), (1, "#fff3d4", 0)])
    g = []
    hz = [(CX[0] - 8, yy, CX[3] + CWS[3] - CX[0] + 16, CORR) for yy in (R1 + RH, R2 + RH)]          # 가로 복도
    vt = [(CX[i] + CWS[i], R1 - 8, CORR, R3 - R1 + 8) for i in range(3)]                             # 세로 복도
    for rx, ry, rw, rh in hz + vt: g.append(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="{base}"/>')
    for rx, ry, rw, rh in hz:
        g.append(f'<rect x="{rx}" y="{ry + 12}" width="{rw}" height="{rh - 24}" rx="4" fill="{run}"/>'
                 f'<rect x="{rx}" y="{ry + 12}" width="{rw}" height="1.4" fill="{gold}" opacity=".75"/><rect x="{rx}" y="{ry + rh - 13.4}" width="{rw}" height="1.4" fill="{gold}" opacity=".75"/>')
        g.append(f'<rect x="{rx}" y="{ry + 14}" width="{rw}" height="{(rh - 28) / 2}" fill="#ffffff" opacity=".05"/>')
        for k in range(int(rx) + 40, int(rx + rw), 80): g.append(f'<rect x="{k}" y="{ry}" width="1" height="{rh}" fill="#000000" opacity=".18"/>')
    for rx, ry, rw, rh in vt:
        g.append(f'<rect x="{rx + 12}" y="{ry}" width="{rw - 24}" height="{rh}" rx="4" fill="{run}"/>'
                 f'<rect x="{rx + 12}" y="{ry}" width="1.4" height="{rh}" fill="{gold}" opacity=".75"/><rect x="{rx + rw - 13.4}" y="{ry}" width="1.4" height="{rh}" fill="{gold}" opacity=".75"/>')
        g.append(f'<rect x="{rx + 14}" y="{ry}" width="{(rw - 28) / 2}" height="{rh}" fill="#ffffff" opacity=".05"/>')
        for k in range(int(ry) + 40, int(ry + rh), 80): g.append(f'<rect x="{rx}" y="{k}" width="{rw}" height="1" fill="#000000" opacity=".18"/>')
    if OS.get("theme") == "ship":        # 써니호 잔디 갑판 · 나무 테두리
        lawn = grad("linearGradient", [(0, "#7cc45a", 1), (1, "#5aa846", 1)], x1=0, y1=0, x2=0, y2=1)
        for rx, ry, rw, rh in hz + vt:
            g.append(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="{lawn}"/>')
        rnd = random.Random(7)
        for rx, ry, rw, rh in hz + vt:
            for _ in range(int(rw * rh / 90)):
                gx, gy = rx + rnd.uniform(2, rw - 2), ry + rnd.uniform(4, rh - 2)
                g.append(f'<path d="M {gx:.1f},{gy:.1f} l {rnd.uniform(-1.5, 1.5):.1f},-4" stroke="{rnd.choice(["#4a9a3a", "#9ad87a", "#3a8a30"])}" stroke-width="1.1"/>')
        for rx, ry, rw, rh in hz: g.append(f'<rect x="{rx}" y="{ry}" width="{rw}" height="5" fill="#8a5a30"/><rect x="{rx}" y="{ry + rh - 5}" width="{rw}" height="5" fill="#8a5a30"/>')
        for rx, ry, rw, rh in vt: g.append(f'<rect x="{rx}" y="{ry}" width="5" height="{rh}" fill="#8a5a30"/><rect x="{rx + rw - 5}" y="{ry}" width="5" height="{rh}" fill="#8a5a30"/>')
        for i in range(3):
            for yy in (R1 + RH, R2 + RH): g.append(sunny_lion(CX[i] + CWS[i] + CORR / 2, yy + CORR / 2, 17))
        for key, x, y in ROOMS + [("boss", CX[3], R2)]:
            mx = x + CWOF[x] - 14 - DOOR_W
            g.append(f'<rect x="{mx - 4}" y="{y + RH + 6}" width="{DOOR_W + 8}" height="{CORR - 12}" rx="4" fill="#a8703c" stroke="#5a3a1e" stroke-width="1.4"/>' + "".join(f'<rect x="{mx - 4}" y="{y + RH + 6 + k * 9}" width="{DOOR_W + 8}" height="1" fill="#5a3a1e" opacity=".6"/>' for k in range(1, 6)))
        return g
    for i in range(3):                                                                           # 교차점 금색 장식
        for yy in (R1 + RH, R2 + RH):
            cx, cy = CX[i] + CWS[i] + CORR / 2, yy + CORR / 2
            g.append(f'<rect x="{cx - 14}" y="{cy - 14}" width="28" height="28" fill="none" stroke="{gold}" stroke-width="1.4" transform="rotate(45 {cx} {cy})" opacity=".8"/><circle cx="{cx}" cy="{cy}" r="4" fill="{gold}"/>')
    for key, x, y in ROOMS + [("boss", CX[3], R2)]:                                              # 문 앞 매트 · 문틈 빛
        mx = x + CWOF[x] - 14 - DOOR_W
        g.append(f'<rect x="{mx - 4}" y="{y + RH + 3}" width="{DOOR_W + 8}" height="{CORR - 6}" rx="5" fill="{gold}" opacity=".28"/><rect x="{mx}" y="{y + RH + 6}" width="{DOOR_W}" height="{CORR - 12}" rx="4" fill="none" stroke="{gold}" stroke-width="1.2" opacity=".9"/>')
    return g

def shell(x, y, w, h, dx=44, bh=150, team=None, door_side=None):
    top, wb = y + 10, y + 10 + bh; cid = nid()
    DEFS.append(f'<clipPath id="c{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18"/></clipPath>')
    g = [f'<rect x="{x + 3}" y="{y + 10}" width="{w}" height="{h}" rx="18" fill="#000" opacity=".22" filter="url(#blur)"/>', f'<g clip-path="url(#c{cid})">']
    g.append(poly([(x, y), (x + w, y), (x + w - dx, top), (x + dx, top)], OS["ceil"]))
    cove = grad("linearGradient", [(0, "#fff2cf", 0.9), (1, "#fff2cf", 0)], x1=0, y1=0, x2=0, y2=1)
    if OS.get("theme") == "ship":       # 천장 들보
        for t in (0.18, 0.5, 0.82):
            g.append(poly([(lerp(x, x + w, t) - 9, y), (lerp(x, x + w, t) + 9, y), (lerp(x + dx, x + w - dx, t) + 6, top), (lerp(x + dx, x + w - dx, t) - 6, top)], "#3a2414"))
    if OS.get("theme") == "avengers":   # 천장 LED 줄
        g.append(poly([(x + w * .3, y), (x + w * .7, y), (x + w * .66, top), (x + w * .34, top)], "#3aa8ff", 'opacity=".25"'))
    # 뒷벽
    g.append(f'<rect x="{x + dx}" y="{top}" width="{w - 2 * dx}" height="{bh}" fill="{grad("linearGradient", [(0, OS["wall"], 1), (1, OS["wall2"], 1)], x1=0, y1=0, x2=0, y2=1)}"/>')
    if OS.get("wall_kind") == "plank":         # 배 선실: 가로 나무 판자 · 이음새 · 못
        for k, yy in enumerate(range(int(top) + 14, int(wb) - 6, 14)):
            g.append(f'<rect x="{x + dx}" y="{yy}" width="{w - 2 * dx}" height="1.4" fill="{OS["wall_line"]}" opacity=".8"/>')
            for xx in range(int(x + dx) + (30 if k % 2 else 70), int(x + w - dx), 90):
                g.append(f'<rect x="{xx}" y="{yy - 14}" width="1.4" height="14" fill="{OS["wall_line"]}" opacity=".7"/><circle cx="{xx + 5}" cy="{yy - 7}" r="1.2" fill="#3a2414"/><circle cx="{xx - 4}" cy="{yy - 7}" r="1.2" fill="#3a2414"/>')
        g.append(f'<rect x="{x + dx}" y="{top}" width="{w - 2 * dx}" height="{bh}" fill="{grad("linearGradient", [(0, "#ffe0a0", .12), (1, "#000000", .18)], x1=0, y1=0, x2=0, y2=1)}"/>')
    elif OS.get("wall_kind") == "steel":     # 어벤져스: 강철 패널 · 리벳 · 파란 LED 줄
        for xx in range(int(x + dx) + 44, int(x + w - dx), 44): g.append(f'<rect x="{xx}" y="{top}" width="1.6" height="{bh - 22}" fill="#0e131a" opacity=".9"/><rect x="{xx + 1.6}" y="{top}" width="1" height="{bh - 22}" fill="#3a4454" opacity=".7"/>')
        g.append(f'<rect x="{x + dx}" y="{top + (bh - 22) / 2}" width="{w - 2 * dx}" height="1.6" fill="#0e131a"/>')
        lg_ = grad("linearGradient", [(0, "#3aa8ff", .55), (1, "#3aa8ff", 0)], x1=0, y1=0, x2=0, y2=1)
        g.append(f'<rect x="{x + dx}" y="{wb - 30}" width="{w - 2 * dx}" height="3" fill="#7ad0ff"/><rect x="{x + dx}" y="{wb - 27}" width="{w - 2 * dx}" height="14" fill="{lg_}"/>')
    elif OS["side_kind"] == "panel":
        for xx in range(int(x + dx) + 24, int(x + w - dx), 26): g.append(f'<rect x="{xx}" y="{top}" width="1.6" height="{bh - 22}" fill="{OS["wall_line"]}" opacity=".55"/>')
    elif OS["night"]:
        for xx in range(int(x + dx) + 18, int(x + w - dx), 30): g.append(f'<rect x="{xx}" y="{top}" width="1" height="{bh - 22}" fill="{OS["wall_line"]}" opacity=".28"/>')
    elif OS["floor_kind"] == "marble":
        g.append(f'<rect x="{x + dx}" y="{top}" width="{w - 2 * dx}" height="{bh}" filter="url(#vein)" opacity=".55"/>')
    else:
        for _ in range(5):
            vx = random.uniform(x + dx, x + w - dx); vy = random.uniform(top, wb - 30)
            g.append(f'<path d="M {vx:.0f},{vy:.0f} q {random.uniform(20, 50):.0f},{random.uniform(-10, 14):.0f} {random.uniform(50, 110):.0f},{random.uniform(-6, 20):.0f}" stroke="{OS["wall_line"]}" stroke-width="1.2" fill="none" opacity=".7"/>')
    if not OS.get("theme"): g.append(f'<rect x="{x + dx}" y="{top}" width="{w - 2 * dx}" height="38" fill="{cove}"/><rect x="{x + dx}" y="{top}" width="{w - 2 * dx}" height="1.6" fill="#fff6dc"/>')
    if OS.get("theme") == "ship":       # 벽 위 늘어진 밧줄
        g.append(f'<path d="M {x + dx},{top + 6} Q {x + dx + (w - 2 * dx) / 4},{top + 22} {x + w / 2},{top + 6} Q {x + w - dx - (w - 2 * dx) / 4},{top + 22} {x + w - dx},{top + 6}" stroke="#3a2414" stroke-width="5.4" fill="none"/>'
                 f'<path d="M {x + dx},{top + 6} Q {x + dx + (w - 2 * dx) / 4},{top + 22} {x + w / 2},{top + 6} Q {x + w - dx - (w - 2 * dx) / 4},{top + 22} {x + w - dx},{top + 6}" stroke="#d9b070" stroke-width="3.4" fill="none" stroke-dasharray="4 2"/>')
    g.append(f'<rect x="{x + dx}" y="{wb - 22}" width="{w - 2 * dx}" height="3" fill="{OS["trim"]}" opacity=".85"/><rect x="{x + dx}" y="{wb - 6}" width="{w - 2 * dx}" height="6" fill="{mix(OS["wall2"], "#000000", 0.25)}"/>')
    if OS["floor_kind"] == "marble": g.append(f'<rect x="{x + dx}" y="{wb - 7}" width="{w - 2 * dx}" height="1.4" fill="#c9a45c"/>')
    if team and OS["night"]: g.append(f'<rect x="{x + dx}" y="{wb - 4}" width="{w - 2 * dx}" height="3" fill="{team}" opacity=".9"/><rect x="{x + dx}" y="{wb - 14}" width="{w - 2 * dx}" height="12" fill="{team}" opacity=".18"/>')
    # 옆벽 (창 또는 패널)
    for side in (-1, 1):
        if side == -1: q = [(x, y), (x + dx, top), (x + dx, wb), (x, y + h)]
        else: q = [(x + w, y), (x + w - dx, top), (x + w - dx, wb), (x + w, y + h)]
        if OS["side_kind"] == "hull":
            g.append(poly(q, grad("linearGradient", [(0, OS["side2"], 1), (1, OS["side"], 1)], x1=0 if side == -1 else 1, y1=0, x2=1 if side == -1 else 0, y2=0)))
            ex = x if side == -1 else x + w; ix = x + dx if side == -1 else x + w - dx
            for v in [k / 9 for k in range(1, 9)]:
                g.append(f'<line x1="{ex}" y1="{lerp(y, y + h, v):.1f}" x2="{ix}" y2="{lerp(top, wb, v):.1f}" stroke="{OS["wall_line"]}" stroke-width="1.2" opacity=".8"/>')
            for t, v, r in ((0.45, 0.3, 15), (0.5, 0.62, 13)):          # 현창 (바다 · 하늘)
                px = lerp(ex, ix, t); py = lerp(lerp(y, top, t), lerp(y + h, wb, t), v); sea = grad("linearGradient", [(0, "#9fd8f4", 1), (0.5, "#5ab4e0", 1), (0.52, "#1f6aa8", 1), (1, "#164e80", 1)], x1=0, y1=0, x2=0, y2=1)
                g.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{r * 0.62:.1f}" ry="{r}" fill="{sea}" stroke="#c9952a" stroke-width="4"/><ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{r * 0.62:.1f}" ry="{r}" fill="none" stroke="#5a3a14" stroke-width="1.2"/>'
                         f'<path d="M {px - r * .5:.1f},{py + 3:.1f} q {r * .25:.1f},-3 {r * .5:.1f},0 q {r * .25:.1f},3 {r * .5:.1f},0" stroke="#ffffff" stroke-width="1.2" fill="none" opacity=".7"/><ellipse cx="{px - r * .2:.1f}" cy="{py - r * .45:.1f}" rx="{r * .18:.1f}" ry="{r * .2:.1f}" fill="#ffffff" opacity=".6"/>')
        elif OS["side_kind"] == "panel":
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
            if OS.get("theme") == "avengers":   # 창에 뜬 파란 홀로그램 격자
                for v in (0.25, 0.4, 0.55):
                    g.append(f'<line x1="{lerp(ex, ix, .15):.1f}" y1="{lerp(lerp(y, top, .15), lerp(y + h, wb, .15), v):.1f}" x2="{lerp(ex, ix, .85):.1f}" y2="{lerp(lerp(y, top, .85), lerp(y + h, wb, .85), v):.1f}" stroke="#3aa8ff" stroke-width="1" opacity=".45"/>')
    # 바닥 (원근)
    fq = [(x + dx, wb), (x + w - dx, wb), (x + w, y + h), (x, y + h)]
    g.append(poly(fq, OS["floor"]))
    if OS["floor_kind"] == "marble":
        fid = nid(); DEFS.append(f'<clipPath id="f{fid}"><polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in fq)}"/></clipPath>')
        g.append(f'<g clip-path="url(#f{fid})"><rect x="{x}" y="{wb}" width="{w}" height="{y + h - wb}" filter="url(#vein2)" opacity=".5"/></g>')
        for i in range(1, 6):                                                     # 타일 세로 줄 (소실점 향해)
            a = i / 6; g.append(f'<line x1="{lerp(x + dx, x + w - dx, a):.1f}" y1="{wb}" x2="{lerp(x, x + w, a):.1f}" y2="{y + h}" stroke="{OS["floor_line"]}" stroke-width=".9" opacity=".7"/>')
        g.append(poly(fq, grad("linearGradient", [(0, "#ffffff", 0.55), (0.35, "#ffffff", 0.05), (1, "#ffffff", 0.18)], x1=0, y1=0, x2=0, y2=1)))
        for t in (0.2, 0.8):                                                      # 창 빛 반사 줄
            g.append(poly([(lerp(x + dx, x + w - dx, t) - 10, wb), (lerp(x + dx, x + w - dx, t) + 10, wb), (lerp(x, x + w, t) + 22, y + h), (lerp(x, x + w, t) - 22, y + h)], "#ffffff", 'opacity=".22"'))
    if OS["floor_kind"] == "hex":
        fid = nid(); DEFS.append(f'<clipPath id="f{fid}"><polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in fq)}"/></clipPath>'
                                 f'<pattern id="hx{fid}" width="26" height="15" patternUnits="userSpaceOnUse"><path d="M 0,7.5 L 4.3,0 L 13,0 L 17.3,7.5 L 13,15 L 4.3,15 Z M 17.3,7.5 L 26,7.5" fill="none" stroke="#3a4a5e" stroke-width="1"/></pattern>')
        g.append(f'<g clip-path="url(#f{fid})"><rect x="{x}" y="{wb}" width="{w}" height="{y + h - wb}" fill="url(#hx{fid})"/></g>')
        g.append(poly(fq, grad("linearGradient", [(0, "#3aa8ff", 0.16), (0.5, "#3aa8ff", 0), (1, "#ffffff", 0.06)], x1=0, y1=0, x2=0, y2=1)))
        g.append(f'<ellipse cx="{x + w / 2}" cy="{lerp(wb, y + h, .55):.1f}" rx="{w * .3:.1f}" ry="{(y + h - wb) * .22:.1f}" fill="none" stroke="#3aa8ff" stroke-width="1.6" opacity=".35"/>')
    lanes = {"herring": 14, "marble": 0, "stone": 8, "deck": 12, "hex": 0}[OS["floor_kind"]]
    for i in range(lanes):
        if i % 2: continue
        a0, a1 = i / lanes, (i + 1) / lanes
        g.append(poly([(lerp(x + dx, x + w - dx, a0), wb), (lerp(x + dx, x + w - dx, a1), wb), (lerp(x, x + w, a1), y + h), (lerp(x, x + w, a0), y + h)], OS["floor2"]))
    rows = {"herring": 7, "marble": 5, "stone": 4, "deck": 6, "hex": 0}[OS["floor_kind"]]
    for k in range(1, rows):
        f = (k / rows) ** 1.45; yy = lerp(wb, y + h, f)
        g.append(f'<line x1="{lerp(x + dx, x, f):.1f}" y1="{yy:.1f}" x2="{lerp(x + w - dx, x + w, f):.1f}" y2="{yy:.1f}" stroke="{OS["floor_line"]}" stroke-width="1" opacity=".8"/>')
    if OS["floor_kind"] == "deck":           # 갑판 못 자국
        for k in range(1, 6):
            f = (k / 6) ** 1.45; yy = lerp(wb, y + h, f)
            for i in range(1, 12, 2):
                a_ = (i + 0.5) / 12; xx = lerp(lerp(x + dx, x + w - dx, a_), lerp(x, x + w, a_), f)
                g.append(f'<circle cx="{xx:.1f}" cy="{yy - 3:.1f}" r="1.1" fill="#5a3a1e"/>')
    if OS["floor_kind"] == "stone":
        g.append(poly(fq, grad("linearGradient", [(0, "#ffffff", 0), (1, "#ffffff", 0.07)], x1=0, y1=0, x2=0, y2=1)))
    # 벽 조명 · 바닥 빛 웅덩이
    lg = grad("radialGradient", [(0, OS["light"], OS["light_op"]), (1, OS["light"], 0)])
    for fx in (0.28, 0.72):
        g.append(f'<ellipse cx="{x + w * fx:.1f}" cy="{lerp(wb, y + h, 0.55):.1f}" rx="{w * 0.26:.1f}" ry="{(y + h - wb) * 0.32:.1f}" fill="{lg}"/>')
    sg = grad("radialGradient", [(0, OS["sconce"], 0.7), (1, OS["sconce"], 0)])
    for sx in (x + dx + 22, x + w - dx - 22):
        if OS.get("theme") == "ship":       # 걸린 랜턴
            g.append(f'<ellipse cx="{sx}" cy="{top + 50}" rx="28" ry="34" fill="{sg}"/><path d="M {sx},{top + 18} L {sx},{top + 30}" stroke="#3a2414" stroke-width="2"/>'
                     f'<path d="M {sx - 8},{top + 30} L {sx + 8},{top + 30} L {sx + 6},{top + 34} L {sx - 6},{top + 34} Z" fill="#3a2414"/><rect x="{sx - 7}" y="{top + 34}" width="14" height="18" rx="3" fill="#ffd27a" stroke="#3a2414" stroke-width="2"/>'
                     f'<path d="M {sx},{top + 34} L {sx},{top + 52} M {sx - 7},{top + 43} L {sx + 7},{top + 43}" stroke="#3a2414" stroke-width="1.2"/><path d="M {sx - 8},{top + 52} L {sx + 8},{top + 52} L {sx + 5},{top + 56} L {sx - 5},{top + 56} Z" fill="#3a2414"/>')
        elif OS.get("theme") == "avengers": # 세로 파란 라이트 바
            g.append(f'<ellipse cx="{sx}" cy="{top + 50}" rx="18" ry="40" fill="{sg}"/><rect x="{sx - 2.5}" y="{top + 22}" width="5" height="52" rx="2.5" fill="#bfe8ff"/>')
        else: g.append(f'<ellipse cx="{sx}" cy="{top + 46}" rx="26" ry="34" fill="{sg}"/><rect x="{sx - 4}" y="{top + 36}" width="8" height="16" rx="3" fill="{OS["trim"]}"/><path d="M {sx - 9},{top + 36} L {sx + 9},{top + 36} L {sx + 6},{top + 26} L {sx - 6},{top + 26} Z" fill="{OS["sconce"]}"/>')
    return g, (top, wb, dx)

def close(g, x, y, w, h, front=False):
    if front: g.append(front_glass(x, y, w, h))
    g.append("</g>")
    g.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="none" stroke="{OS["trim"]}" stroke-width="3"/>')
    if OS["glass"]: g.append(f'<rect x="{x + 6}" y="{y + 4}" width="{w - 12}" height="2" rx="1" fill="#ffffff" opacity=".5"/>')
    return g

def plant(cx, by, s=1.0):
    if OS.get("theme") == "ship":        # 술통
        w_, h_ = 20 * s, 30 * s
        return (f'<path d="M {cx - w_ * .8},{by - h_} Q {cx - w_ * 1.05},{by - h_ / 2} {cx - w_ * .8},{by} L {cx + w_ * .8},{by} Q {cx + w_ * 1.05},{by - h_ / 2} {cx + w_ * .8},{by - h_} Z" fill="#a8703c" stroke="#3a2414" stroke-width="1.8"/>'
                + "".join(f'<path d="M {cx - w_ * .95:.1f},{by - h_ * f:.1f} L {cx + w_ * .95:.1f},{by - h_ * f:.1f}" stroke="#4a4f5a" stroke-width="2.6"/>' for f in (0.2, 0.8))
                + f'<path d="M {cx - w_ * .4},{by - h_} L {cx - w_ * .4},{by} M {cx + w_ * .3},{by - h_} L {cx + w_ * .3},{by}" stroke="#7a4a24" stroke-width="1.2"/><ellipse cx="{cx}" cy="{by - h_}" rx="{w_ * .8}" ry="{4 * s}" fill="#8a5a30" stroke="#3a2414" stroke-width="1.4"/>')
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
    hc = 280 - 12 / s          # 몸은 책상 윗면 뒤쪽 선에서 자른다 (그 아래는 책상이 가림)
    sv = sc.svg(lk, n, team=team, working=working, pose=pose, size=(240 * s, hc * s), view=f"-120 -180 240 {hc:.2f}")
    sv = sv.replace("<svg ", f'<svg x="{cx - 120 * s:.1f}" y="{desk_y - 280 * s:.1f}" ', 1)
    if pose == "type":         # 손은 책상 위에
        sv += "".join(f'<circle cx="{cx + k * 31 * s:.1f}" cy="{desk_y - 6:.1f}" r="{8.5 * s:.1f}" fill="{lk["skin"]}" stroke="{sc.INK}" stroke-width="{1.4 * s + 0.6:.1f}"/>' for k in (-1, 1))
    return sv

DESK = {"써니호선실": ("#b07a44", "#6a4426", "#e0b070"), "어벤져스본부": ("#2a3240", "#161b24", "#3aa8ff"), "월넛라운지": ("#9a6844", "#6e4630", "#b78258"), "마블펜트하우스": ("#f7f6f2", "#2a2d33", "#ffffff"), "나이트스카이": ("#2a3142", "#161b26", "#c9a45c")}[A.office]
def desk(x0, x1, yt, depth=12, panel=22):
    top, front, edge = DESK; gl = grad("linearGradient", [(0, "#ffffff", 0.0), (1, "#ffffff", 0.7)], x1=0, y1=0, x2=0, y2=1)
    pf = grad("linearGradient", [(0, mix(front, "#ffffff", 0.18), 1), (1, front, 1)], x1=0, y1=0, x2=0, y2=1)
    ed = "#c9a45c" if OS["glass"] and not OS["night"] else edge
    return (f'<ellipse cx="{(x0 + x1) / 2}" cy="{yt + panel + 8}" rx="{(x1 - x0) / 2 + 10}" ry="7" fill="#000" opacity=".16" filter="url(#soft)"/>'
            f'<polygon points="{x0 + 8},{yt - depth} {x1 - 8},{yt - depth} {x1},{yt} {x0},{yt}" fill="{top}" stroke="{mix(front, "#000000", 0.2)}" stroke-width="1"/>'
            f'<polygon points="{x0 + 8},{yt - depth} {x1 - 8},{yt - depth} {x1},{yt} {x0},{yt}" fill="{gl}"/>'
            f'<rect x="{x0}" y="{yt}" width="{x1 - x0}" height="{panel}" fill="{pf}"/><rect x="{x0}" y="{yt}" width="{x1 - x0}" height="2" fill="{ed}" opacity=".9"/>'
            f'<rect x="{x0 + 6}" y="{yt + panel}" width="6" height="8" fill="{front}"/><rect x="{x1 - 12}" y="{yt + panel}" width="6" height="8" fill="{front}"/>')

def chair(cx, yt, s):
    c = "#2b2a33" if not OS["night"] else "#3a3448"
    return f'<rect x="{cx - 38 * s:.1f}" y="{yt - 150 * s:.1f}" width="{76 * s:.1f}" height="{150 * s:.1f}" rx="{18 * s:.1f}" fill="{c}"/><rect x="{cx - 30 * s:.1f}" y="{yt - 142 * s:.1f}" width="{60 * s:.1f}" height="{10 * s:.1f}" rx="{4 * s:.1f}" fill="#ffffff" opacity=".12"/>'

APPLE = ("M 0,-4 C -2,-6.5 -8,-7 -9.5,-2 C -11,3 -7,9.5 -4.5,9.5 C -3,9.5 -1.5,8.6 0,8.6 C 1.5,8.6 3,9.5 4.5,9.5 C 7,9.5 9.5,4.5 9.8,2.4 "
         "C 7.4,1.4 6.6,-2.8 9,-4.6 C 7.2,-7.2 2.4,-6.6 0,-4 Z M 0.6,-5.2 C 0.4,-8.4 2.8,-10.6 5,-10.8 C 5.2,-8 3,-5.6 0.6,-5.2 Z")
def laptop(cx, yt, s, on, team):
    """작업 중 = 실버 노트북을 펼침(뒷면 사과 로고가 하얗게 빛남) · 쉬는 중 = 덮어 둠 + 머그컵"""
    w, h = 58 * s, 36 * s
    if on:
        gid = nid(); DEFS_LOCAL = f'<defs><linearGradient id="lp{gid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#eef1f4"/><stop offset="1" stop-color="#b9c0c8"/></linearGradient></defs>'
        return (DEFS_LOCAL + f'<rect x="{cx - w / 2 - 2:.1f}" y="{yt - 3:.1f}" width="{w + 4:.1f}" height="4" rx="2" fill="#a9b0b8"/>'
                f'<rect x="{cx - w / 2:.1f}" y="{yt - h - 2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{4 * s:.1f}" fill="url(#lp{gid})" stroke="#8f98a3" stroke-width="1"/>'
                f'<ellipse cx="{cx}" cy="{yt - h / 2 - 2:.1f}" rx="{11 * s:.1f}" ry="{11 * s:.1f}" fill="#ffffff" opacity=".55"/>'
                f'<path d="{APPLE}" transform="translate({cx:.1f},{yt - h / 2 - 1:.1f}) scale({0.62 * s + 0.2:.2f})" fill="#ffffff" stroke="#c8ced6" stroke-width=".6"/>')
    return (f'<rect x="{cx - w / 2:.1f}" y="{yt - 6 * s - 2:.1f}" width="{w:.1f}" height="{6 * s + 2:.1f}" rx="2" fill="#c9ced6" stroke="#9aa3ad" stroke-width=".8"/>'
            f'<rect x="{cx + w / 2 + 4:.1f}" y="{yt - 15 * s:.1f}" width="{11 * s:.1f}" height="{14 * s:.1f}" rx="2" fill="#ffffff" stroke="#c9bfae"/><path d="M {cx + w / 2 + 15 * s + 4:.1f},{yt - 12 * s:.1f} q {5 * s:.1f},{3 * s:.1f} 0,{7 * s:.1f}" stroke="#c9bfae" fill="none"/>')

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
    CW = CWOF[x]
    g, (top, wb, dx) = shell(x, y, CW, RH, bh=108, team=color)     # 위쪽 벽을 줄여 책상 · 통로 자리 확보 (본부장 10-31 허용)
    g.append(decor(key, x, CW, top, dx))
    rug_c = mix(color, OS["floor"], OS["rug_mix"])
    g.append(poly([(x + 70, wb + 22), (x + CW - 70, wb + 22), (x + CW - 30, y + RH - 10), (x + 30, y + RH - 10)], rug_c, f'stroke="{mix(rug_c, "#000000", 0.25)}" stroke-width="2" opacity=".95"'))
    g.append(poly([(x + 80, wb + 28), (x + CW - 80, wb + 28), (x + CW - 42, y + RH - 16), (x + 42, y + RH - 16)], "none", 'stroke="#ffffff" stroke-width="1.2" opacity=".55"'))
    back, front = (n + 1) // 2, n // 2
    looks = sc.ROSTER[key]; order = list(range(n)); occ = set(order[:busy]); away = set() if ASSETS else set(order[busy:busy + AWAY.get(key, 0)])
    mx = max(back, front); sp = min(100, (CW - 128) / mx); sf = min(0.46, sp / 205); RCX = x + 30 + (CW - 128) / 2 + 8   # 문 쪽(오른쪽 앞) 비움
    rows = [(back, y + 186, sf * 0.84, sp * 0.86, 0), (front, y + 268, sf, sp, back)]
    heads, report = [], None
    for cnt, yt, s, sp, off in rows:
        if not cnt: continue
        cx0 = RCX - (cnt - 1) * sp / 2
        g.append(desk(cx0 - sp / 2 - 6, cx0 + (cnt - 1) * sp + sp / 2 + 6, yt, panel=int(70 * s)))
        for j in range(cnt):
            i = off + j; sx = cx0 + j * sp
            g.append(chair(sx, yt, s))
            if ASSETS:
                n_ = sc.ROSTER[key][i]; hy = yt - (230 if n_["hat"] else 172) * s; box = (sx - 120 * s, yt - 280 * s, 240 * s, 280 * s + 8)
                seat = {"team": key, "i": i, "name": n_["name"], "hx": round(sx, 1), "hy": round(hy, 1), "fx": round(sx, 1), "fy": round(yt + 4, 1),
                        "work": sprite(f"seat_{key}_{i}_work.svg", box, char(n_, sx, yt, s, color, True) + laptop(sx, yt, s * 1.4, True, color)),
                        "idle": sprite(f"seat_{key}_{i}_idle.svg", box, char(n_, sx, yt, s, color, False) + laptop(sx, yt, s * 1.4, False, color))}
                st_svg = sc.svg(n_, nid(), team=color, working=True, pose="side", size=(240 * 0.34, 400 * 0.34))
                open(os.path.join(ASSETS, f"stand_{key}_{i}.svg"), "w", encoding="utf-8").write(st_svg)
                seat["stand"] = {"file": f"stand_{key}_{i}.svg", "w": 240 * 0.34, "h": 400 * 0.34, "feet": (205 + 180) / 400}
                LAYOUT["seats"].setdefault(key, []).append(seat); continue
            if i in away:
                report = looks[i]; heads.append((sx, yt - 120 * s, "away")); g.append(laptop(sx, yt, s, False, color)); continue
            g.append(char(looks[i], sx, yt, s, color, i in occ))
            g.append(laptop(sx, yt, s, i in occ, color)); heads.append((sx, yt - (230 if looks[i]["hat"] else 172) * s, "on" if i in occ else "off"))
    g.append(plant(x + 26, y + RH - 14, 0.9))
    g = close(g, x, y, CW, RH, front=True)
    g.append(plaque(x + dx + 8, top + 8, no, name, color))
    if ASSETS:
        LAYOUT["rooms"][key] = {"x": x, "y": y, "w": CW, "h": RH, "badge": [x + dx + 8, top + 48], "door": DOORS[(x, y)], "row": 0 if y == R1 else 1, "col": CX.index(x), "name": name, "color": color, "n": n}
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
    CW = CWOF[x]
    g, (top, wb, dx) = shell(x, y, CW, RH, bh=120)
    gold, wal, wal2 = "#c9a45c", "#4a2f22", "#6e4630"
    # 뒷벽: 월넛 포인트 벽 + 금색 회사 로고 · 큰 그림 · 트로피 장식장
    g.append(f'<rect x="{x + 150}" y="{top + 4}" width="126" height="{wb - top - 30}" fill="{wal}"/>' + "".join(f'<rect x="{x + 150 + k * 21}" y="{top + 4}" width="1.2" height="{wb - top - 30}" fill="{wal2}"/>' for k in range(1, 6)))
    g.append(f'<rect x="{x + 166}" y="{top + 18}" width="94" height="40" rx="3" fill="#2a1a12" stroke="{gold}" stroke-width="1.6"/>' + T(x + 213, top + 38, "EDGE", 17, gold, 800, "middle", 'letter-spacing="4"') + T(x + 213, top + 52, "COMPANY", 8, gold, 700, "middle", 'letter-spacing="3"'))
    g.append(f'<rect x="{x + 56}" y="{top + 50}" width="84" height="60" fill="{gold}"/><rect x="{x + 60}" y="{top + 54}" width="76" height="52" fill="#1d2b44"/>'
             f'<circle cx="{x + 82}" cy="{top + 72}" r="12" fill="#e6ad3c" opacity=".9"/><path d="M {x + 60},{top + 98} Q {x + 90},{top + 76} {x + 136},{top + 94} L {x + 136},{top + 106} L {x + 60},{top + 106} Z" fill="#3a6ea8"/><path d="M {x + 60},{top + 104} Q {x + 100},{top + 88} {x + 136},{top + 102} L {x + 136},{top + 106} L {x + 60},{top + 106} Z" fill="#c9a45c" opacity=".8"/>')
    g.append(f'<rect x="{x + 284}" y="{top + 12}" width="30" height="{wb - top - 34}" fill="{wal}"/>' + "".join(
        f'<rect x="{x + 286}" y="{top + 44 + k * 34}" width="26" height="3" fill="{wal2}"/><path d="M {x + 293},{top + 22 + k * 34} L {x + 305},{top + 22 + k * 34} Q {x + 305},{top + 34 + k * 34} {x + 299},{top + 36 + k * 34} Q {x + 293},{top + 34 + k * 34} {x + 293},{top + 22 + k * 34} Z" fill="{gold}"/><rect x="{x + 296}" y="{top + 36 + k * 34}" width="6" height="7" fill="{gold}"/>' for k in range(3)))
    if OS.get("theme") == "ship":        # 밀짚모자 해적단(루피) 깃발: 검은 깃발 · 뒤로 X자 뼈 · 밀짚모자 쓴 해골
        fx, fy, fw, fh = x + 50, top + 40, 100, 74; cx, cy = fx + fw / 2, fy + 40
        g.append(f'<rect x="{fx - 4}" y="{fy - 6}" width="4" height="{fh + 30}" fill="#8a5a30" stroke="#3a2414" stroke-width="1"/><circle cx="{fx - 2}" cy="{fy - 8}" r="4" fill="#e6b84a" stroke="#3a2414" stroke-width="1"/>')
        g.append(f'<path d="M {fx},{fy} Q {fx + fw / 2},{fy - 6} {fx + fw},{fy + 2} Q {fx + fw - 6},{fy + fh / 2} {fx + fw + 2},{fy + fh} Q {fx + fw / 2},{fy + fh - 6} {fx},{fy + fh} Z" fill="#141418" stroke="#000" stroke-width="1.6"/>')
        bone = lambda x1, y1, x2, y2: (f'<path d="M {x1},{y1} L {x2},{y2}" stroke="#f6f4ee" stroke-width="7" stroke-linecap="round"/>'
                                      + "".join(f'<circle cx="{px + ox}" cy="{py + oy}" r="4.4" fill="#f6f4ee"/>' for px, py in ((x1, y1), (x2, y2)) for ox, oy in ((-2.6, 2.6), (2.6, -2.6))))
        g.append(bone(cx - 32, cy - 20, cx + 32, cy + 26) + bone(cx + 32, cy - 20, cx - 32, cy + 26))                       # 해골 뒤 X자 뼈
        g.append(f'<path d="M {cx - 17},{cy - 2} C {cx - 19},{cy - 26} {cx + 19},{cy - 26} {cx + 17},{cy - 2} Q {cx + 16},{cy + 8} {cx + 9},{cy + 10} L {cx + 9},{cy + 18} L {cx - 9},{cy + 18} L {cx - 9},{cy + 10} Q {cx - 16},{cy + 8} {cx - 17},{cy - 2} Z" fill="#f6f4ee" stroke="#000" stroke-width="1.2"/>'
                 f'<ellipse cx="{cx - 7}" cy="{cy - 3}" rx="5" ry="6" fill="#141418"/><ellipse cx="{cx + 7}" cy="{cy - 3}" rx="5" ry="6" fill="#141418"/><path d="M {cx - 2},{cy + 6} L {cx},{cy + 2} L {cx + 2},{cy + 6} Z" fill="#141418"/>'
                 + "".join(f'<path d="M {cx + dx_},{cy + 11} L {cx + dx_},{cy + 18}" stroke="#141418" stroke-width="1.2"/>' for dx_ in (-4.5, 0, 4.5)))       # 해골
        g.append(f'<ellipse cx="{cx}" cy="{cy - 15}" rx="27" ry="5.6" fill="#f2c94c" stroke="#8a6a1a" stroke-width="1.2"/><path d="M {cx - 16},{cy - 15} C {cx - 17},{cy - 36} {cx + 17},{cy - 36} {cx + 16},{cy - 15} Z" fill="#f2c94c" stroke="#8a6a1a" stroke-width="1.2"/>'
                 f'<path d="M {cx - 16},{cy - 20} Q {cx},{cy - 23} {cx + 16},{cy - 20} L {cx + 16},{cy - 15} Q {cx},{cy - 18} {cx - 16},{cy - 15} Z" fill="#d93a2e"/>'
                 f'<path d="M {cx - 10},{cy - 30} Q {cx - 4},{cy - 33} {cx + 2},{cy - 32}" stroke="#ffffff" stroke-width="1.4" fill="none" opacity=".6"/>')       # 밀짚모자
    if OS.get("theme") == "avengers":    # A 엠블럼
        fx, fy = x + 98, top + 80
        g.append(f'<circle cx="{fx}" cy="{fy}" r="34" fill="#0e141e" stroke="#3aa8ff" stroke-width="3"/><circle cx="{fx}" cy="{fy}" r="40" fill="none" stroke="#3aa8ff" stroke-width="1.2" opacity=".5"/>'
                 f'<path d="M {fx - 18},{fy + 22} L {fx + 2},{fy - 26} L {fx + 12},{fy - 26} L {fx + 12},{fy + 22} L {fx + 4},{fy + 22} L {fx + 4},{fy + 8} L {fx - 6},{fy + 8} L {fx - 12},{fy + 22} Z M {fx - 2},{fy} L {fx + 4},{fy} L {fx + 4},{fy - 14} Z" fill="#cfe8ff" fill-rule="evenodd"/>'
                 f'<path d="M {fx - 30},{fy + 4} L {fx + 30},{fy + 4}" stroke="#cfe8ff" stroke-width="3"/>')
    # 바닥: 고급 카펫
    g.append(poly([(x + 58, wb + 22), (x + CW - 58, wb + 22), (x + CW - 22, y + RH - 30), (x + 22, y + RH - 30)], "#7a2f2a", f'stroke="{gold}" stroke-width="2"'))
    g.append(poly([(x + 72, wb + 30), (x + CW - 72, wb + 30), (x + CW - 40, y + RH - 38), (x + 40, y + RH - 38)], "none", f'stroke="{gold}" stroke-width="1.2" opacity=".8"'))
    g.append(f'<ellipse cx="{x + CW / 2}" cy="{(wb + y + RH) / 2 - 4}" rx="44" ry="14" fill="none" stroke="{gold}" stroke-width="1.2" opacity=".7"/>')
    # 뒤쪽 왼편: 가죽 소파 · 탁자 · 스탠드 조명
    sy = y + RH - 62
    g.append(f'<rect x="{x + 30}" y="{sy}" width="84" height="30" rx="11" fill="#5a2f25" stroke="#3a1d16" stroke-width="1.6"/><rect x="{x + 34}" y="{sy + 4}" width="76" height="11" rx="5" fill="#73402f"/>'
             f'<rect x="{x + 26}" y="{sy + 6}" width="10" height="28" rx="4" fill="#4a2620"/><rect x="{x + 108}" y="{sy + 6}" width="10" height="28" rx="4" fill="#4a2620"/>')
    mtx, mty = x + 172, y + RH - 48                       # 원탁 회의 테이블 (책상을 올려 앞쪽 회의 공간 넓힘 · 본부장 10-31)
    for ox in (-38, 38): g.append(f'<rect x="{mtx + ox - 9}" y="{mty - 22}" width="18" height="24" rx="5" fill="#5a2f25"/><rect x="{mtx + ox - 11}" y="{mty}" width="22" height="7" rx="3" fill="#73402f"/>')
    g.append(f'<rect x="{mtx - 3}" y="{mty}" width="6" height="22" fill="#2a1a12"/><ellipse cx="{mtx}" cy="{mty + 22}" rx="14" ry="4" fill="#2a1a12"/><ellipse cx="{mtx}" cy="{mty}" rx="30" ry="9" fill="#f6f2ea" stroke="#c9a45c" stroke-width="1.6"/>'
             f'<rect x="{mtx - 10}" y="{mty - 4}" width="12" height="7" rx="1" fill="#ffffff" stroke="#d8cdbb" stroke-width=".6"/><rect x="{mtx + 6}" y="{mty - 5}" width="5" height="6" rx="1" fill="#c9a45c"/>')
    lg2 = grad("radialGradient", [(0, "#fff1cc", 0.7), (1, "#fff1cc", 0)])
    g.append(f'<ellipse cx="{x + 44}" cy="{wb - 34}" rx="26" ry="22" fill="{lg2}"/><rect x="{x + 43}" y="{wb - 32}" width="2.4" height="64" fill="{gold}"/><path d="M {x + 34},{wb - 30} L {x + 54},{wb - 30} L {x + 50},{wb - 44} L {x + 38},{wb - 44} Z" fill="#fbf3e2" stroke="{gold}"/><ellipse cx="{x + 44}" cy="{wb + 32}" rx="8" ry="2.4" fill="{gold}"/>')
    # 뒤쪽 오른편: 지구본 · 회사 깃발
    g.append(f'<rect x="{x + 300}" y="{wb + 40}" width="3" height="16" fill="{gold}"/><ellipse cx="{x + 301}" cy="{wb + 57}" rx="10" ry="3" fill="{wal}"/><circle cx="{x + 301}" cy="{wb + 28}" r="14" fill="#5f95db" stroke="{gold}" stroke-width="2"/>'
             f'<path d="M {x + 292},{wb + 22} q 6,-6 12,0 q 4,6 -2,12 q -6,2 -8,-4 Z M {x + 304},{wb + 32} q 4,-2 6,2 q -2,4 -6,2 Z" fill="#5cb87a"/>')
    g.append(f'<rect x="{x + 236}" y="{wb - 66}" width="2.4" height="118" fill="{gold}"/><circle cx="{x + 237}" cy="{wb - 68}" r="3" fill="{gold}"/><path d="M {x + 238},{wb - 62} Q {x + 254},{wb - 66} {x + 266},{wb - 58} L {x + 266},{wb - 26} Q {x + 254},{wb - 34} {x + 238},{wb - 30} Z" fill="#1b2433" stroke="{gold}" stroke-width="1"/>' + T(x + 252, wb - 41, "E", 11, gold, 800, "middle"))
    cx, yt, s = x + CW / 2 - 10, y + 162, 0.44
    g.append(f'<rect x="{cx - 50 * s:.1f}" y="{yt - 190 * s:.1f}" width="{100 * s:.1f}" height="{190 * s:.1f}" rx="{24 * s:.1f}" fill="#5a2f25"/>')
    if ASSETS:
        LAYOUT["boss"] = {"sprite": sprite("boss_work.svg", (cx - 90, yt - 280 * s, 180, 280 * s + 8), char(sc.BOSS_LOOK, cx, yt, s, None, True, pose="type") + laptop(cx - 62, yt, 0.4, True, "#c9a45c")),
                          "type": sprite("boss_type.svg", (cx - 90, yt - 280 * s, 180, 280 * s + 8), char(sc.BOSS_LOOK, cx, yt, s, None, True, pose="type") + laptop(cx, yt, s * 1.4, True, "#c9a45c")),   # 노트북을 앞에 펼치고 일함 (평상시 90%)
                          "hx": cx, "hy": yt - 232 * s, "spot": [x + CW - 70, y + RH - 34], "spot2": [x + CW - 118, y + RH - 34], "meet": {"boss": [x + 126, y + RH - 28], "rep": [x + 218, y + RH - 28]},
                          "standAt": [cx + 108, yt + 34], "door": None, "room": {"x": x, "y": y, "w": CW, "h": RH}, "name": sc.BOSS_LOOK["name"]}
        open(os.path.join(ASSETS, "boss_stand.svg"), "w", encoding="utf-8").write(sc.svg(sc.BOSS_LOOK, nid(), working=True, pose="side", size=(240 * 0.36, 400 * 0.36)))
        LAYOUT["boss"]["stand"] = {"file": "boss_stand.svg", "w": 240 * 0.36, "h": 400 * 0.36, "feet": (205 + 180) / 400}
    else: g.append(char(sc.BOSS_LOOK, cx, yt, s, None, True, pose="type"))
    top_, front, edge = DESK
    g.append(f'<polygon points="{cx - 86},{yt - 14} {cx + 86},{yt - 14} {cx + 96},{yt} {cx - 96},{yt}" fill="{top_}" stroke="{mix(front, "#000000", 0.2)}"/><rect x="{cx - 96}" y="{yt}" width="192" height="40" fill="{front}"/><rect x="{cx - 96}" y="{yt}" width="192" height="2" fill="{edge}"/>')
    g.append(f'<rect x="{cx - 96}" y="{yt + 36}" width="192" height="4" fill="#c9a45c"/><rect x="{cx - 92}" y="{yt + 6}" width="2" height="30" fill="#c9a45c" opacity=".6"/><rect x="{cx + 90}" y="{yt + 6}" width="2" height="30" fill="#c9a45c" opacity=".6"/>')
    g.append(f'<rect x="{cx - 26}" y="{yt + 12}" width="52" height="16" rx="2" fill="#c9a45c"/>' + T(cx, yt + 24, "총괄 본부장", 9, "#1b2433", 800, "middle"))
    g.append(f'<rect x="{cx + 52}" y="{yt - 12}" width="8" height="10" rx="2" fill="#2a1a12"/><path d="M {cx + 54},{yt - 12} l -3,-9 M {cx + 58},{yt - 12} l 4,-8" stroke="#c9a45c" stroke-width="1.4"/><rect x="{cx + 66}" y="{yt - 9}" width="16" height="7" rx="1" fill="#f6f2ea"/>')
    if not ASSETS: g.append(laptop(cx - 62, yt, 0.4, True, "#c9a45c"))
    if reporter and not ASSETS: g.append(char(reporter, x + CW - 112, y + RH - 36, 0.34, TEAM["audit"][2], True, pose="hold", stand=True))
    g = close(g, x, y, CW, RH, front=True)
    g.append(plaque(x + dx + 8, top + 8, "", "본부장실", "#c9a45c"))
    if ASSETS: LAYOUT["boss"]["door"] = DOORS[(x, y)]; return g
    if reporter: g.append(bubble(x + CW - 150, y + RH - 36 - 130, f"{reporter['name']}: 검증 결과 보고드립니다", sz=12))
    g.append(bubble(cx + 50, yt - 240 * s, "확인! 수고했어!", bg="#fff6dc", sz=12))
    g.append(dot(cx + 30, yt - 232 * s, "on"))
    gx = CX[3] + CWS[3] / 2
    return g

# ───────────── 상황실 (현황판) ─────────────
def board_room(x, y, w, h):
    g, (top, wb, dx) = shell(x, y, w, h, dx=60, bh=h - 24)
    BX0, BY0, BX1, BY1 = x + dx + 18, top + 48, x + w - dx - 18, wb - 12
    g.append(f'<rect x="{BX0 - 5}" y="{BY0 - 5}" width="{BX1 - BX0 + 10}" height="{BY1 - BY0 + 10}" rx="14" fill="{OS["board_frame"]}"/><rect x="{BX0}" y="{BY0}" width="{BX1 - BX0}" height="{BY1 - BY0}" rx="10" fill="{grad("linearGradient", [(0, "#1d2740", 1), (1, OS["board"], 1)], x1=0, y1=0, x2=0, y2=1)}"/>')
    if ASSETS:
        LAYOUT["board"] = {"x": BX0, "y": BY0, "w": BX1 - BX0, "h": BY1 - BY0}
        g.append(plant(x + 40, y + h - 10, 1.0)); g.append(plant(x + w - 40, y + h - 10, 1.0)); g = close(g, x, y, w, h)
        g.append(plaque(x + dx + 18, top + 10, "", "상황실 · 단지 현황판", "#c9a45c"))
        if OS.get("theme") == "ship": g.append(sunny_lion(x + w / 2 - 40, top + 24, 22) + T(x + w / 2 - 6, top + 32, "THOUSAND SUNNY", 13, "#ffe7b0", 800, "start", 'letter-spacing="2"'))
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

def sea_bg():         # 원피스 배경: 바깥 바다 물결
    if OS.get("theme") != "ship": return ""
    rnd = random.Random(3); g = f'<rect width="{W}" height="{H}" fill="{grad("linearGradient", [(0, "#8ad0ec", 1), (1, "#3a8ac0", 1)], x1=0, y1=0, x2=0, y2=1)}"/>'
    for _ in range(140):
        x0, y0 = rnd.uniform(0, W), rnd.uniform(90, H)
        g += f'<path d="M {x0:.0f},{y0:.0f} q 6,-4 12,0 q 6,4 12,0" stroke="#ffffff" stroke-width="1.6" fill="none" opacity="{rnd.uniform(.3, .7):.2f}"/>'
    return g

VK = 1.0       # 자판기 원래 크기 · 위쪽 벽(방 앞쪽)에 붙여 세움 — 방 앞부분을 조금 가려도 됨 (본부장 10-31)
VEND = [(CX[0] + 26, R1 + RH + 22, "#d8352e", "DRINK"), (CX[2] + 10, R2 + RH + 22, "#2f6fd0", "COFFEE")]
body, report = corridors(), None
LAYOUT["vend"] = [[vx_ + 46 * VK + 14, vy_ - 22 + CORR / 2 + 8, vl_] for vx_, vy_, vc_, vl_ in VEND]
for key, x, y in ROOMS:
    g, rep = team_room(key, x, y); body += g; report = report or rep
body += boss_room(CX[3], R2, report)
body += board_room(CX[0], R3, CX[3] + CWS[3] - CX[0], RH3)
for vx_, vy_, vc_, vl_ in VEND: body.append(f'<g transform="translate({vx_},{vy_}) scale({VK}) translate({-vx_},{-vy_})">{vending(vx_, vy_, vc_, vl_)}</g>')     # 방 위에 그림 (본부장 10-31 '방보다 위로')
if ASSETS:
    bg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs><filter id="blur" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="8"/></filter>{FILTERS}{"".join(DEFS)}</defs>'
          f'<rect width="{W}" height="{H}" fill="{OS["bg"]}"/>' + sea_bg() + "".join(body) + "</svg>")
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
