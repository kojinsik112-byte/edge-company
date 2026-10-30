# 스킨: 원피스직원 v1 (2026-10-30) — 원피스 주요 캐릭터 오마주 치비 36명 · 본부장 = 루피(기어5 니카)
# 사내 오피스 화면 전용 (팬아트 · 외부 게시 · 홍보물 사용 금지 — 캐릭터 저작권은 원작자)
# office_mock.py · roster.py 가 exec 로 불러 쓴다 (rr · el · poly … 그리기 함수는 부르는 쪽 것)
INK = "#3b2a22"
SK, SK2, SK3 = "#ffdcc2", "#f2c29b", "#e6b08a"

def C(name, hs, hair, out, c1, c2="#ffffff", c3="#1b2433", skin=SK, hat=None, eyes="normal", mouth="smile", ex=(), hair2=None, eyec="#2b1d16", legs="#3b3f52"):
    return dict(name=name, hs=hs, hair=hair, hair2=hair2 or hair, out=out, c1=c1, c2=c2, c3=c3, skin=skin, hat=hat, eyes=eyes, mouth=mouth, ex=list(ex), eyec=eyec, legs=legs)

BOSS_LOOK = C("루피 (기어5 니카)", "cloud", "#ffffff", "vest_open", "#ffffff", hair2="#e4e7ee", eyes="big", mouth="grin",
              ex=["scar_luffy", "x_scar", "steam_ring", "straw_back"], eyec="#4a3020", legs="#f4f4f4")
ROSTER = {   # 방(팀) 자리 순서대로 — 위 줄 → 아래 줄
    "scout": [
        C("나미", "long_wavy", "#f08a3a", "stripe", "#5a8fd8", "#ffffff", eyes="big", eyec="#8a5a34", ex=["log_pose"]),
        C("우솝", "curly", "#2b2220", "overalls", "#b0773e", "#ffffff", skin=SK3, ex=["long_nose", "goggles_head"], hat=None),
        C("캐럿", "bunny", "#f6f1e8", "dress", "#7fc3e8", "#ffffff", eyes="big", eyec="#d9493b", ex=["bunny_ears"]),
        C("비비", "pony", "#5aa9e6", "tshirt", "#ffffff", eyes="big", eyec="#2b3a5a", ex=["earrings_gold"]),
    ],
    "analysis": [
        C("로빈", "hime", "#2b2a33", "coat", "#7b5aa6", "#f4efe6", eyes="big", eyec="#3a5f9a", ex=["sunglasses_head"]),
        C("로우", "short", "#2b2a33", "hoodie", "#f2c94c", "#1f1d24", hat="law", eyes="sharp", mouth="smirk", ex=["goatee", "earrings_gold"]),
        C("징베", "topknot", "#2b2a33", "kimono", "#e9873a", "#ffffff", "#2a5ea8", skin="#7fa6c9", eyes="sharp", mouth="smile"),
        C("마르코", "pineapple", "#f2cf5a", "vest_open", "#7b5aa6", eyes="sleepy", mouth="smile", ex=["beads_blue"]),
        C("베가펑크", "big_round", "#b98ad8", "labcoat", "#ffffff", "#5fa3d9", eyes="normal", ex=["goggles_head"]),
    ],
    "build": [
        C("프랑키", "pompadour", "#3aa0e8", "hawaii", "#e04848", "#ffd34d", skin=SK2, eyes="sunglasses", mouth="grin", ex=[]),
        C("상디", "sanji", "#f2cf5a", "suit", "#1f2230", "#4a7fd0", "#1f2230", eyes="normal", mouth="smirk", ex=["curly_brow", "goatee_blond"]),
        C("쵸파", "short", "#8a5a34", "fur", "#8a5a34", "#e8c49a", skin="#e8c49a", hat="chopper", eyes="big", mouth="smile", ex=["blue_nose", "antlers"], legs="#5f8fd0"),
        C("브룩", "afro", "#1f1d24", "suit", "#1f1d24", "#ffffff", "#c9483b", skin="#f6f1e6", hat="tophat", eyes="skull", mouth="teeth"),
        C("에이스", "messy", "#1f1d24", "shirtless", SK2, skin=SK2, hat="ace", eyes="normal", mouth="grin", ex=["freckles", "beads_red"], legs="#2b3a5a"),
        C("사보", "wavy", "#f2cf5a", "coat", "#2f4f8a", "#ffffff", hat="sabo", eyes="normal", ex=["scar_sabo", "cravat"]),
        C("키드", "flame", "#d9382c", "fur_coat", "#c0392b", "#e9a19a", eyes="sharp", mouth="grin", ex=["goggles_head", "no_brow"]),
        C("야마토", "pony", "#f4f4f4", "kimono", "#ffffff", "#d94a4a", "#8c4bd0", hair2="#5fd0c6", eyes="big", eyec="#c9483b", ex=["horns"]),
    ],
    "audit": [
        C("조로", "short", "#3f8f4a", "kimono", "#3d7a4a", "#2b5a37", "#c9483b", skin=SK2, eyes="zoro", mouth="smirk", ex=["earrings3"]),
        C("미호크", "short", "#1f1d24", "coat", "#7a2a2a", "#1f1d24", hat="mihawk", eyes="hawk", mouth="flat", ex=["mustache_thin"]),
        C("스모커", "slick", "#eeeeee", "coat", "#ffffff", "#3a5f9a", eyes="sharp", mouth="flat", ex=["fur_collar"]),
        C("타시기", "bob", "#2b2a5a", "tshirt", "#f2a6b8", eyes="big", eyec="#3a3a5a", ex=["glasses_square"]),
        C("가프", "short", "#bdbdbd", "marine", "#ffffff", "#3a5f9a", hat="marine", eyes="normal", mouth="grin", ex=["beard_white", "scar_garp"]),
        C("코비", "short", "#f2a0c0", "marine", "#ffffff", "#3a5f9a", hat="marine", eyes="big", eyec="#5a3a6a"),
    ],
    "mail": [
        C("봉쿠레", "bun", "#1f1d24", "swan", "#ffffff", "#f29ac0", eyes="makeup", mouth="lips"),
        C("버기", "messy", "#3a7fd8", "coat", "#c0392b", "#f2cf5a", hat="captain", eyes="normal", mouth="grin", ex=["red_nose", "clown_paint"]),
        C("페로나", "drills", "#f29ac0", "dress", "#2b2a33", "#d9493b", hat="crown", eyes="big", eyec="#3a2a3a", ex=["star_cheek"]),
        C("바르톨로메오", "mohawk", "#3aa86a", "coat", "#2b2a33", "#ffffff", eyes="sharp", mouth="teeth", ex=["nose_ring"]),
    ],
    "pt": [
        C("우타", "uta", "#d9493b", "dress", "#ffffff", "#5a5a6a", hair2="#f4f4f4", eyes="big", eyec="#8c4bd0", ex=["headphones"]),
        C("핸콕", "hime", "#1f1d24", "dress", "#c0392b", "#ffffff", eyes="big", eyec="#2b2a5a", mouth="lips", ex=["snake_earrings"]),
        C("레베카", "long", "#f29ac0", "dress", "#e85d8a", "#f6d36b", eyes="big", eyec="#3a5f9a", ex=["headband_flower"]),
        C("히요리", "hime", "#1f1d24", "kimono", "#e8607a", "#ffffff", "#f2cf5a", eyes="big", eyec="#3a2a3a", ex=["kanzashi"]),
    ],
    "retro": [
        C("샹크스", "messy", "#c0392b", "cloak", "#1f1d24", "#ffffff", eyes="normal", mouth="smile", ex=["scar_shanks", "stubble"]),
        C("흰수염", "short", "#f4f4f4", "coat", "#f4f1e6", "#7b5aa6", skin=SK2, hat="bandana", eyes="sharp", mouth="flat", ex=["mustache_crescent"]),
        C("레일리", "slick", "#f4f4f4", "tshirt", "#f4f1e6", eyes="normal", ex=["glasses_round", "beard_white"]),
        C("크로커다일", "slick", "#1f1d24", "fur_coat", "#3a2f2a", "#5a4a3a", eyes="sharp", mouth="smirk", ex=["scar_croc"]),
    ],
}
def new_look(team, i=0):
    return ROSTER[team][i % len(ROSTER[team])]

# ───────────── 그리기 ─────────────
R_ = 23
def _cap(cx, cy, hc, f):      # 정수리 덮는 머리 (f = 이마선 높이)
    D.pieslice(P(cx - R_ - 1, cy - R_ - 2, cx + R_ + 1, cy + R_ * f), 180, 360, fill=hc)

def _hair_back(cx, cy, lk, back):
    hs, hc, h2 = lk["hs"], lk["hair"], lk["hair2"]; ol = mix(hc, INK, 0.45)
    if "bunny_ears" in lk["ex"]:
        for s in (-1, 1):
            el([cx + s * 11 - 7, cy - 58, cx + s * 11 + 7, cy - 14], "#f6f1e8", "#d6cfc2", 1.5); el([cx + s * 11 - 3, cy - 52, cx + s * 11 + 3, cy - 22], "#f6b3c2")
    if hs in ("hime", "long", "long_wavy"):
        rr([cx - 28, cy - 10, cx + 28, cy + 44], 13, hc, ol, 1.5)
        if hs == "long_wavy":
            for k in range(5): el([cx - 28 + k * 12, cy + 36, cx - 16 + k * 12, cy + 48], hc)
    elif hs == "pony":
        el([cx + 12, cy - 28, cx + 34, cy + 18], hc, ol, 1.5)
        if h2 != hc: el([cx + 16, cy + 2, cx + 32, cy + 18], h2)
    elif hs == "drills":
        for s in (-1, 1):
            for k in range(4):
                yy = cy - 4 + k * 10; el([cx + s * 31 - 10 + k, yy, cx + s * 31 + 10 - k, yy + 12], hc, ol, 1.2)
    elif hs == "afro":
        el([cx - 40, cy - 52, cx + 40, cy + 16], hc, ol, 1.5)
        for k in range(10):
            a = math.pi * (1 + k / 9); el([cx + math.cos(a) * 38 - 8, cy - 18 + math.sin(a) * 34 - 8, cx + math.cos(a) * 38 + 8, cy - 18 + math.sin(a) * 34 + 8], hc)
    elif hs == "big_round":
        el([cx - 34, cy - 56, cx + 34, cy + 6], hc, ol, 1.5)
    elif hs == "cloud":            # 니카: 흰 구름 머리
        for k in range(11):
            a = math.pi * (0.85 + k * 0.13); r = 13 + (k % 2) * 3
            px, py = cx + math.cos(a) * 25, cy - 4 + math.sin(a) * 25
            el([px - r, py - r, px + r, py + r], hc, h2, 1.5)
    elif hs == "uta":
        for s, c in ((-1, h2), (1, hc)):
            rr([cx + s * 24 - 6, cy - 6, cx + s * 24 + 6, cy + 30], 6, c)
            arc([cx + s * 22 - 10, cy - 36, cx + s * 22 + 10, cy - 16], 0, 360, c, 5)
    elif hs == "bun":
        el([cx - 11, cy - R_ - 14, cx + 11, cy - R_ + 6], hc, ol, 1.5)
    elif hs == "topknot":
        el([cx - 8, cy - R_ - 10, cx + 8, cy - R_ + 4], hc, ol, 1.5)
    if back and hs in ("short", "messy", "slick", "wavy", "flame", "pineapple", "curly", "sanji", "bob", "bunny", "pompadour"):
        pass

def _hair_front(cx, cy, lk):
    hs, hc, h2 = lk["hs"], lk["hair"], lk["hair2"]; hl = mix(hc, "#ffffff", 0.4)
    if hs in ("messy", "spiky"):
        _cap(cx, cy, hc, 0.25)
        for k, dx in enumerate((-15, -5, 5, 15)):
            poly([(cx + dx - 6, cy - 16), (cx + dx + 6, cy - 16), (cx + dx + (2 if k % 2 else -2), cy - 4)], hc)
        for a in (200, 235, 270, 305, 340):
            r = math.radians(a); px, py = cx + math.cos(r) * 22, cy + math.sin(r) * 22
            poly([(px - 6, py + 2), (px + 6, py + 2), (px + math.cos(r) * 9, py + math.sin(r) * 9)], hc)
    elif hs == "short":  _cap(cx, cy, hc, 0.05); poly([(cx - 10, cy - 20), (cx + 2, cy - 22), (cx - 4, cy - 12)], hc)
    elif hs == "slick":  _cap(cx, cy, hc, -0.25); arc([cx - 16, cy - 22, cx + 16, cy - 6], 200, 340, hl, 1.5)
    elif hs in ("hime",):
        _cap(cx, cy, hc, 0.35); rect([cx - R_ + 3, cy - R_ + 4, cx + R_ - 3, cy - 6], hc)
        rr([cx - R_ - 1, cy - 10, cx - R_ + 7, cy + 18], 4, hc); rr([cx + R_ - 7, cy - 10, cx + R_ + 1, cy + 18], 4, hc)
    elif hs in ("long", "long_wavy", "pony"):
        _cap(cx, cy, hc, 0.35); poly([(cx + 2, cy - R_ + 2), (cx + 12, cy - R_ + 4), (cx + 4, cy - 6)], lk["skin"])
        rr([cx - R_ - 1, cy - 8, cx - R_ + 7, cy + 14], 4, hc); rr([cx + R_ - 7, cy - 8, cx + R_ + 1, cy + 14], 4, hc)
    elif hs == "bob" or hs == "bunny":
        _cap(cx, cy, hc, 0.35); rr([cx - R_ - 2, cy - 8, cx - R_ + 8, cy + 16], 5, hc); rr([cx + R_ - 8, cy - 8, cx + R_ + 2, cy + 16], 5, hc)
        rect([cx - 14, cy - 18, cx + 14, cy - 8], hc)
    elif hs == "curly":
        _cap(cx, cy, hc, 0.2)
        for k in range(8):
            a = math.pi * (1 + k / 7); el([cx + math.cos(a) * 21 - 8, cy - 4 + math.sin(a) * 21 - 8, cx + math.cos(a) * 21 + 8, cy - 4 + math.sin(a) * 21 + 8], hc)
    elif hs == "afro": _cap(cx, cy, hc, 0.1)
    elif hs == "big_round": _cap(cx, cy, hc, 0.15)
    elif hs == "cloud":
        _cap(cx, cy, hc, 0.2)
        for dx in (-14, 0, 14): el([cx + dx - 9, cy - 22, cx + dx + 9, cy - 6], hc, h2, 1.2)
    elif hs == "pompadour":
        _cap(cx, cy, hc, 0.0); rr([cx - 18, cy - 44, cx + 30, cy - 16], 13, hc, mix(hc, INK, 0.4), 1.5); arc([cx - 10, cy - 40, cx + 24, cy - 22], 200, 330, hl, 2)
    elif hs == "sanji":
        _cap(cx, cy, hc, 0.25); poly([(cx - R_, cy - 12), (cx + 4, cy - R_), (cx + 2, cy + 12), (cx - 16, cy + 14), (cx - R_ - 1, cy + 4)], hc)
    elif hs == "pineapple":
        _cap(cx, cy, hc, -0.15)
        for dx in (-6, 0, 6): poly([(cx + dx - 5, cy - 20), (cx + dx + 5, cy - 20), (cx + dx * 1.6, cy - 38)], hc)
    elif hs == "mohawk":
        rr([cx - 6, cy - 40, cx + 6, cy - 6], 5, hc, mix(hc, INK, 0.4), 1.2)
    elif hs == "drills": _cap(cx, cy, hc, 0.3); rect([cx - 15, cy - 18, cx + 15, cy - 8], hc)
    elif hs == "uta":
        D.pieslice(P(cx - R_ - 1, cy - R_ - 2, cx + R_ + 1, cy + R_ * 0.3), 180, 270, fill=h2); D.pieslice(P(cx - R_ - 1, cy - R_ - 2, cx + R_ + 1, cy + R_ * 0.3), 270, 360, fill=hc)
        rect([cx - 15, cy - 18, cx, cy - 8], h2); rect([cx, cy - 18, cx + 15, cy - 8], hc)
    elif hs == "bun": _cap(cx, cy, hc, 0.05)
    elif hs == "topknot": _cap(cx, cy, hc, -0.2)
    elif hs == "wavy":
        _cap(cx, cy, hc, 0.25)
        for s in (-1, 1):
            for k in range(3): el([cx + s * 22 - 7, cy - 10 + k * 9, cx + s * 22 + 7, cy + 2 + k * 9], hc)
    elif hs == "flame":
        _cap(cx, cy, hc, 0.05)
        for dx, hh in ((-16, 22), (-8, 34), (0, 40), (8, 34), (16, 22)):
            poly([(cx + dx - 7, cy - 16), (cx + dx + 7, cy - 16), (cx + dx, cy - 16 - hh)], hc)
    if hs not in ("mohawk", "afro", "pompadour"):
        arc([cx - 14, cy - 18, cx + 2, cy - 4], 200, 300, hl, 2)

def _eyes(cx, cy, lk, working):
    e, ey = lk["eyes"], cy + 4; dark = "#2b1d16"
    if e == "sunglasses":
        rr([cx - 19, ey - 6, cx + 19, ey + 5], 4, "#1f2a3a", "#0f1520", 1.5); line([(cx - 14, ey - 3), (cx - 8, ey - 3)], "#7fb3e8", 1.5); return
    if e == "skull":
        for ex in (cx - 9, cx + 9): el([ex - 6, ey - 6, ex + 6, ey + 5], "#1f1d24")
        poly([(cx - 3, ey + 9), (cx + 3, ey + 9), (cx, ey + 4)], "#1f1d24"); return
    for side, ex in ((-1, cx - 9), (1, cx + 9)):
        if e == "zoro" and side == 1:
            line([(ex - 5, ey), (ex + 5, ey)], dark, 2); line([(ex, ey - 10), (ex - 1, ey + 10)], "#9a4d3d", 2); continue
        if not working:
            arc([ex - 5, ey - 4, ex + 5, ey + 4], 200, 340, dark, 2.2)
        elif e == "big":
            el([ex - 5, ey - 7, ex + 5, ey + 7], dark); el([ex - 4, ey - 3, ex + 4, ey + 6], lk["eyec"]); el([ex - 2, ey - 5, ex + 2, ey - 1], "#ffffff")
        elif e == "hawk":
            el([ex - 5, ey - 5, ex + 5, ey + 5], "#f2c94c", dark, 1.5); el([ex - 1.2, ey - 4, ex + 1.2, ey + 4], dark)
        elif e == "sleepy":
            el([ex - 4, ey - 2, ex + 4, ey + 5], dark); line([(ex - 6, ey - 2), (ex + 6, ey - 2)], dark, 2.2)
        else:
            el([ex - 4, ey - 5.5, ex + 4, ey + 5.5], dark); el([ex - 1, ey - 4, ex + 2.5, ey - 0.5], "#ffffff")
        if e in ("sharp", "zoro", "hawk"):
            line([(ex - 6, ey - 7 + (2 if side == -1 else 0)), (ex + 6, ey - 7 + (0 if side == -1 else 2))], dark, 2.4)
        if e == "makeup":
            for k in (-4, 0, 4): line([(ex + k, ey - 6), (ex + k * 1.4, ey - 10)], dark, 1.5)
    if lk["skin"] not in ("#f6f1e6",) and e != "zoro":
        for ex in (cx - 9, cx + 9): el([ex - 6 + (2 if ex > cx else -2), ey + 6, ex + 6 + (2 if ex > cx else -2), ey + 11], mix(lk["skin"], "#f08f8a", 0.45))

def _mouth(cx, cy, lk):
    m = lk["mouth"]
    if m == "grin":
        D.chord(P(cx - 10, cy + 3, cx + 10, cy + 21), 0, 180, fill="#ffffff", outline=INK, width=max(1, int(1.6 * K * SCL()))); line([(cx - 9, cy + 12), (cx + 9, cy + 12)], INK, 1.2)
    elif m == "teeth":
        rr([cx - 8, cy + 10, cx + 8, cy + 17], 2, "#ffffff", INK, 1.2)
        for k in (-4, 0, 4): line([(cx + k, cy + 10), (cx + k, cy + 17)], INK, 1)
    elif m == "smirk": line([(cx - 4, cy + 13), (cx + 5, cy + 11)], "#9a4d3d", 2)
    elif m == "flat": line([(cx - 4, cy + 13), (cx + 4, cy + 13)], "#9a4d3d", 2)
    elif m == "lips": el([cx - 4, cy + 10, cx + 4, cy + 15], "#d9384f")
    else: arc([cx - 4, cy + 8, cx + 4, cy + 15], 20, 160, "#9a4d3d", 2)

def _face_extras(cx, cy, lk):
    ex, ey = lk["ex"], cy + 4
    if "scar_luffy" in ex:
        line([(cx - 15, ey + 9), (cx - 6, ey + 9)], "#9a4d3d", 1.5); line([(cx - 13, ey + 7), (cx - 13, ey + 11)], "#9a4d3d", 1.2); line([(cx - 8, ey + 7), (cx - 8, ey + 11)], "#9a4d3d", 1.2)
    if "earrings3" in ex:
        for k in range(3): el([cx + R_ - 3, cy + 2 + k * 6, cx + R_ + 3, cy + 7 + k * 6], GOLD)
    if "earrings_gold" in ex:
        for s in (-1, 1): el([cx + s * R_ - 3, cy + 10, cx + s * R_ + 3, cy + 17], GOLD)
    if "snake_earrings" in ex:
        for s in (-1, 1): rr([cx + s * R_ - 2, cy + 8, cx + s * R_ + 3, cy + 22], 2, "#8c4bd0")
    if "long_nose" in ex: rr([cx - 2, cy + 4, cx + 20, cy + 10], 3, lk["skin"], INK, 1.5)
    if "curly_brow" in ex: arc([cx + 4, ey - 12, cx + 14, ey - 4], 180, 450, "#c9a23a", 1.8)
    if "goatee_blond" in ex: rr([cx - 3, cy + 17, cx + 3, cy + 22], 2, "#e0b84a")
    if "goatee" in ex: rr([cx - 4, cy + 16, cx + 4, cy + 22], 2, "#2b2a33")
    if "freckles" in ex:
        for s in (-1, 1):
            for dx, dy in ((0, 0), (4, 2), (-3, 3)): el([cx + s * 12 + dx - 1, ey + 8 + dy - 1, cx + s * 12 + dx + 1, ey + 8 + dy + 1], "#b5764f")
    if "red_nose" in ex: el([cx - 5, cy + 4, cx + 5, cy + 13], "#e0302a", INK, 1.2)
    if "clown_paint" in ex:
        for s in (-1, 1): rr([cx + s * 9 - 5, ey - 10, cx + s * 9 + 5, ey - 7], 1, "#3a7fd8")
    if "blue_nose" in ex: el([cx - 4, cy + 5, cx + 4, cy + 11], "#3a7fd8", INK, 1)
    if "star_cheek" in ex: el([cx + 13, ey + 7, cx + 19, ey + 13], "#f2cf5a")
    if "scar_sabo" in ex: el([cx - 16, ey - 7, cx - 3, ey + 6], mix(lk["skin"], "#d9706a", 0.35))
    if "scar_shanks" in ex:
        for k in (-3, 0, 3): line([(cx - 9 + k - 2, ey - 9), (cx - 9 + k + 2, ey + 5)], "#9a4d3d", 1.1)
    if "scar_croc" in ex:
        line([(cx - 18, ey + 4), (cx + 18, ey + 3)], "#9a4d3d", 1.6)
        for k in (-10, 0, 10): line([(cx + k, ey + 1), (cx + k, ey + 6)], "#9a4d3d", 1.2)
    if "scar_garp" in ex: line([(cx - 14, ey - 9), (cx - 4, ey + 1)], "#9a4d3d", 1.6)
    if "nose_ring" in ex: arc([cx - 3, cy + 7, cx + 3, cy + 13], 0, 180, GOLD, 1.5)
    if "stubble" in ex:
        for dx in range(-8, 9, 4): el([cx + dx - 0.8, cy + 18, cx + dx + 0.8, cy + 19.6], "#8a6a5a")
    if "beard_white" in ex: D.chord(P(cx - 18, cy + 2, cx + 18, cy + 30), 0, 180, fill="#f4f4f4", outline="#cfcfcf", width=K)
    if "mustache_crescent" in ex:
        arc([cx - 34, cy - 10, cx + 34, cy + 18], 20, 160, "#f4f4f4", 5); arc([cx - 34, cy - 10, cx + 34, cy + 18], 20, 160, "#d9d9d9", 1)
    if "mustache_thin" in ex:
        arc([cx - 12, cy + 6, cx, cy + 14], 200, 340, "#1f1d24", 1.6); arc([cx, cy + 6, cx + 12, cy + 14], 200, 340, "#1f1d24", 1.6); rr([cx - 2, cy + 17, cx + 2, cy + 23], 1, "#1f1d24")
    if "glasses_round" in ex:
        for s in (-1, 1): el([cx + s * 9 - 7, ey - 7, cx + s * 9 + 7, ey + 7], None, GOLD, 1.8)
    if "glasses_square" in ex:
        for s in (-1, 1): rr([cx + s * 9 - 7, ey - 6, cx + s * 9 + 7, ey + 6], 2, None, "#c0392b", 1.8)
    if "no_brow" in ex: pass

def _top_extras(cx, cy, lk):
    ex = lk["ex"]
    if "goggles_head" in ex:
        rect([cx - R_, cy - 16, cx + R_, cy - 11], "#4a3a2a")
        for s in (-1, 1): el([cx + s * 9 - 7, cy - 21, cx + s * 9 + 7, cy - 7], "#9fd3f2", "#4a3a2a", 2)
    if "sunglasses_head" in ex: rr([cx - 16, cy - 26, cx + 16, cy - 18], 3, "#3a2f2a")
    if "horns" in ex:
        for s in (-1, 1): poly([(cx + s * 10 - 5, cy - 18), (cx + s * 10 + 5, cy - 18), (cx + s * 14, cy - 40)], "#d9493b")
    if "headphones" in ex:
        arc([cx - R_ - 4, cy - R_ - 6, cx + R_ + 4, cy + R_], 190, 350, "#f4f4f4", 4)
        for s in (-1, 1): rr([cx + s * (R_ + 2) - 5, cy - 6, cx + s * (R_ + 2) + 5, cy + 8], 4, "#5a5a6a")
    if "headband_flower" in ex: arc([cx - R_ + 1, cy - R_ + 1, cx + R_ - 1, cy + R_ - 1], 200, 340, "#f6d36b", 4); el([cx + 10, cy - 24, cx + 20, cy - 14], "#ffffff")
    if "kanzashi" in ex:
        line([(cx + 8, cy - 22), (cx + 22, cy - 34)], GOLD, 2); el([cx + 16, cy - 30, cx + 26, cy - 20], "#e8607a")
    if "log_pose" in ex: pass

def _hat(cx, cy, lk):
    h = lk["hat"]
    if not h: return
    if h == "straw":
        el([cx - 36, cy - 26, cx + 36, cy - 10], "#f2cf6b", "#c99a3a", 1.5); rr([cx - 20, cy - 46, cx + 20, cy - 16], 14, "#f2cf6b", "#c99a3a", 1.5); rect([cx - 20, cy - 26, cx + 20, cy - 20], "#d9382c")
    elif h == "ace":
        el([cx - 36, cy - 28, cx + 36, cy - 12], "#ec8a2c", "#b5621a", 1.5); rr([cx - 19, cy - 48, cx + 19, cy - 18], 12, "#ec8a2c", "#b5621a", 1.5)
        rect([cx - 19, cy - 26, cx + 19, cy - 22], "#3a2a22"); el([cx - 12, cy - 32, cx - 4, cy - 24], "#5aa9e6"); el([cx + 4, cy - 32, cx + 12, cy - 24], "#e04848")
    elif h in ("tophat", "sabo"):
        col = "#1f1d24" if h == "tophat" else "#2f4f8a"
        rr([cx - 17, cy - 60, cx + 17, cy - 20], 4, col); rr([cx - 30, cy - 25, cx + 30, cy - 17], 4, col)
        rect([cx - 17, cy - 30, cx + 17, cy - 25], "#c9483b" if h == "tophat" else "#3a2a22")
        if h == "sabo":
            for s in (-1, 1): el([cx + s * 7 - 6, cy - 42, cx + s * 7 + 6, cy - 30], "#9fd3f2", "#3a2a22", 2)
    elif h == "chopper":
        rr([cx - 18, cy - 54, cx + 18, cy - 18], 6, "#f29ac0", "#c9708f", 1.5); rr([cx - 28, cy - 24, cx + 28, cy - 16], 4, "#f29ac0", "#c9708f", 1.2)
        line([(cx - 11, cy - 48), (cx + 11, cy - 28)], "#ffffff", 3); line([(cx + 11, cy - 48), (cx - 11, cy - 28)], "#ffffff", 3)
        for s in (-1, 1):
            line([(cx + s * 16, cy - 22), (cx + s * 32, cy - 46)], "#8a5a34", 4); line([(cx + s * 26, cy - 37), (cx + s * 36, cy - 34)], "#8a5a34", 3)
    elif h == "law":
        rr([cx - 26, cy - 42, cx + 26, cy - 8], 15, "#f6f3ee", "#d6d0c4", 1.5)
        for dx, dy in ((-14, -30), (0, -36), (12, -26), (-4, -20), (18, -16)): el([cx + dx - 3, cy + dy - 3, cx + dx + 3, cy + dy + 3], "#5a4a3a")
    elif h == "mihawk":
        el([cx - 44, cy - 28, cx + 44, cy - 12], "#1f1d24"); rr([cx - 18, cy - 46, cx + 18, cy - 18], 10, "#1f1d24")
        el([cx + 8, cy - 58, cx + 42, cy - 38], "#f4f1e6", "#cfcfcf", 1)
    elif h == "marine":
        rr([cx - 22, cy - 40, cx + 22, cy - 16], 8, "#ffffff", "#c9ced6", 1.5); rect([cx - 22, cy - 22, cx + 22, cy - 17], "#3a5f9a"); el([cx - 26, cy - 20, cx + 10, cy - 12], "#2b3a5a")
    elif h == "captain":
        poly([(cx - 36, cy - 18), (cx, cy - 50), (cx + 36, cy - 18), (cx, cy - 24)], "#1f1d24"); line([(cx - 34, cy - 19), (cx, cy - 25), (cx + 34, cy - 19)], GOLD, 2)
    elif h == "bandana":
        D.pieslice(P(cx - R_ - 2, cy - R_ - 3, cx + R_ + 2, cy + R_ * 0.1), 180, 360, fill="#2b2a33"); line([(cx - R_, cy - 2), (cx + R_, cy - 2)], "#2b2a33", 3)
    elif h == "crown":
        poly([(cx - 10, cy - 22), (cx - 10, cy - 34), (cx - 5, cy - 28), (cx, cy - 36), (cx + 5, cy - 28), (cx + 10, cy - 34), (cx + 10, cy - 22)], GOLD)

def _body(cx, cy, lk, team, back):
    o, c1, c2, c3, skin = lk["out"], lk["c1"], lk["c2"], lk["c3"], lk["skin"]; ol = mix(c1, INK, 0.45)
    base_c = skin if o == "shirtless" else c1
    if o == "hoodie": D.chord(P(cx - 20, cy + 8, cx + 20, cy + 30), 180, 360, fill=mix(c1, INK, 0.15))
    rr([cx - 23, cy + 15, cx + 23, cy + 52], 15, base_c, mix(base_c, INK, 0.45), 2)
    if back:
        if o in ("cloak", "coat", "fur_coat", "marine", "labcoat", "swan"): rr([cx - 25, cy + 15, cx + 25, cy + 52], 15, c1, ol, 2)
        if o == "kimono": rect([cx - 22, cy + 38, cx + 22, cy + 43], c3)
        if team: rr([cx - 23, cy + 26, cx - 16, cy + 34], 2, team)
        return
    if o == "vest_open":
        rr([cx - 8, cy + 15, cx + 8, cy + 50], 4, skin)
        if "x_scar" in lk["ex"]: line([(cx - 6, cy + 26), (cx + 6, cy + 36)], "#c97a6a", 1.6); line([(cx + 6, cy + 26), (cx - 6, cy + 36)], "#c97a6a", 1.6)
    elif o == "tshirt": D.chord(P(cx - 8, cy + 9, cx + 8, cy + 23), 0, 180, fill=skin)
    elif o == "stripe":
        for k in range(3): rect([cx - 21, cy + 25 + k * 8, cx + 21, cy + 28 + k * 8], c2)
        D.chord(P(cx - 8, cy + 9, cx + 8, cy + 23), 0, 180, fill=skin)
    elif o == "suit":
        poly([(cx - 10, cy + 16), (cx + 10, cy + 16), (cx, cy + 34)], c2); poly([(cx - 3, cy + 20), (cx + 3, cy + 20), (cx + 2, cy + 36), (cx - 2, cy + 36)], c3)
    elif o in ("coat", "marine", "labcoat"):
        rect([cx - 7, cy + 16, cx + 7, cy + 50], c2); line([(cx - 7, cy + 16), (cx - 7, cy + 50)], ol, 1.2); line([(cx + 7, cy + 16), (cx + 7, cy + 50)], ol, 1.2)
        if o == "marine":
            for s in (-1, 1): rr([cx + s * 18 - 6, cy + 14, cx + s * 18 + 6, cy + 19], 2, GOLD)
    elif o == "kimono":
        poly([(cx - 12, cy + 16), (cx, cy + 34), (cx + 12, cy + 16)], c2); poly([(cx - 7, cy + 16), (cx, cy + 27), (cx + 7, cy + 16)], skin)
        rect([cx - 22, cy + 37, cx + 22, cy + 43], c3)
    elif o == "hawaii":
        poly([(cx - 9, cy + 16), (cx + 9, cy + 16), (cx, cy + 34)], skin)
        for dx, dy in ((-16, 26), (14, 30), (-12, 42), (16, 44), (-2, 46)): el([cx + dx - 3, cy + dy - 3, cx + dx + 3, cy + dy + 3], c2)
    elif o == "shirtless": rect([cx - 22, cy + 44, cx + 22, cy + 52], lk["legs"])
    elif o == "hoodie":
        rect([cx - 22, cy + 30, cx + 22, cy + 36], c2); line([(cx - 4, cy + 18), (cx - 4, cy + 28)], c2, 1.5); line([(cx + 4, cy + 18), (cx + 4, cy + 28)], c2, 1.5)
    elif o == "fur": el([cx - 13, cy + 22, cx + 13, cy + 48], c2)
    elif o == "dress":
        poly([(cx - 10, cy + 16), (cx + 10, cy + 16), (cx, cy + 24)], c2); rect([cx - 22, cy + 36, cx + 22, cy + 39], c2)
    elif o == "overalls":
        rr([cx - 23, cy + 15, cx + 23, cy + 52], 15, c2, mix(c2, INK, 0.4), 2); rr([cx - 13, cy + 28, cx + 13, cy + 52], 4, c1)
        for s in (-1, 1): line([(cx + s * 11, cy + 16), (cx + s * 11, cy + 30)], c1, 3)
    elif o == "cloak":
        poly([(cx - 8, cy + 16), (cx + 8, cy + 16), (cx, cy + 28)], skin)
        for s in (-1, 1): rr([cx + s * 18 - 8, cy + 14, cx + s * 18 + 8, cy + 54], 6, c1)
    elif o == "fur_coat":
        rect([cx - 7, cy + 18, cx + 7, cy + 50], "#2b2a33")
        for k in range(5): el([cx - 26 + k * 13 - 7, cy + 11, cx - 26 + k * 13 + 7, cy + 24], c2)
    elif o == "swan":
        for s in (-1, 1): el([cx + s * 20 - 7, cy + 8, cx + s * 20 + 7, cy + 22], "#ffffff", "#cfcfcf", 1); poly([(cx + s * 26, cy + 14), (cx + s * 33, cy + 16), (cx + s * 26, cy + 18)], "#f29a3a")
        rect([cx - 22, cy + 34, cx + 22, cy + 38], c2)
    if "steam_ring" in lk["ex"]:
        for k in range(7): el([cx - 27 + k * 9 - 7, cy + 12, cx - 27 + k * 9 + 7, cy + 24], "#ffffff", "#dfe3ea", 1)
    if "beads_red" in lk["ex"]:
        for k in range(7): a = math.pi * (0.15 + k * 0.12); el([cx + math.cos(a) * 13 - 2.5, cy + 16 + math.sin(a) * 8 - 2.5, cx + math.cos(a) * 13 + 2.5, cy + 16 + math.sin(a) * 8 + 2.5], "#d9382c")
    if "beads_blue" in lk["ex"]:
        for k in range(7): a = math.pi * (0.15 + k * 0.12); el([cx + math.cos(a) * 12 - 2.5, cy + 17 + math.sin(a) * 8 - 2.5, cx + math.cos(a) * 12 + 2.5, cy + 17 + math.sin(a) * 8 + 2.5], "#3a7fd8")
    if "cravat" in lk["ex"]: el([cx - 6, cy + 15, cx + 6, cy + 25], "#ffffff", "#cfcfcf", 1)
    if "fur_collar" in lk["ex"]:
        for k in range(5): el([cx - 24 + k * 12 - 7, cy + 11, cx - 24 + k * 12 + 7, cy + 22], "#e9e2d2")
    if team: rr([cx - 23, cy + 26, cx - 16, cy + 34], 2, team)        # 팀 완장 (오피스에서만)

def chibi(cx, cy, shirt, lk, working, back=False, suit=False, stand=False, paper=False, team=None):
    skin = lk["skin"]
    if stand:
        rr([cx - 14, cy + 46, cx - 3, cy + 66], 4, lk["legs"]); rr([cx + 3, cy + 46, cx + 14, cy + 66], 4, lk["legs"])
        sh = "#d9b25f" if lk["name"].startswith("루피") else "#2a2026"
        rr([cx - 17, cy + 62, cx - 2, cy + 70], 4, sh); rr([cx + 2, cy + 62, cx + 17, cy + 70], 4, sh)
    if "straw_back" in lk["ex"]:
        el([cx - 34, cy + 4, cx + 34, cy + 22], "#f2cf6b", "#c99a3a", 1.5); rect([cx - 18, cy + 8, cx + 18, cy + 12], "#d9382c")
    if not back: _hair_back(cx, cy, lk, back)
    _body(cx, cy, lk, team, back)
    if paper:
        rr([cx + 8, cy + 24, cx + 30, cy + 50], 2, "#ffffff", "#c9bfae", 1.5)
        for k in range(3): line([(cx + 12, cy + 31 + k * 5), (cx + 26, cy + 31 + k * 5)], "#c9ced6", 1.2)
        el([cx + 14, cy + 34, cx + 24, cy + 44], skin, INK, 1.5)
    if back:
        _hair_back(cx, cy, lk, back)
        hc = lk["hair"] if lk["hs"] not in ("mohawk",) else skin
        el([cx - R_, cy - R_, cx + R_, cy + R_], hc, INK, 2)
        if lk["hs"] == "mohawk": rr([cx - 6, cy - 40, cx + 6, cy + 16], 5, lk["hair"])
        if lk["hs"] in ("hime", "long", "long_wavy"): rr([cx - 22, cy, cx + 22, cy + 40], 11, lk["hair"])
        if lk["hs"] == "uta": D.pieslice(P(cx - R_, cy - R_, cx + R_, cy + R_), 90, 270, fill=lk["hair2"])
        _top_extras(cx, cy, lk); _hat(cx, cy, lk)
        return
    el([cx - R_, cy - R_, cx + R_, cy + R_], skin, INK, 2)
    if lk["hs"] == "skull" or skin == "#f6f1e6": pass
    _hair_front(cx, cy, lk)
    if lk["hs"] not in ("mohawk",): arc([cx - R_ - 1, cy - R_ - 1, cx + R_ + 1, cy + R_ + 1], 180, 360, INK, 2)
    _eyes(cx, cy, lk, working); _mouth(cx, cy, lk); _face_extras(cx, cy, lk)
    if lk["hs"] == "sanji": pass
    _top_extras(cx, cy, lk); _hat(cx, cy, lk)
