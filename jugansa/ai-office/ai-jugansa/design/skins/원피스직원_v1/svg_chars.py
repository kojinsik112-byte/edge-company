# 원피스직원 v1 — 애니메이션풍 3등신 캐릭터 SVG 생성기 (셀 채색 · 액션 포즈 · 무기 · 소품)
# 본부장 PC 전용 로컬 오피스 화면 (팬아트 · 외부 게시 · 홍보물 사용 금지 — 캐릭터 저작권은 원작자)
# 좌표: 머리 가운데 (0, 0) · 얼굴 -55 ~ 44 · 몸 42 ~ 124 · 다리 118 ~ 202 · 발 205 (≈ 3등신)
import math

INK = "#3d2820"
STYLE_NAME = {"B": "3등신 애니 셀 채색"}
def set_style(k): pass

def mix(a, b, t):
    a = [int(a[i:i+2], 16) for i in (1, 3, 5)]; b = [int(b[i:i+2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))
def _lum(c): return sum(int(c[i:i+2], 16) for i in (1, 3, 5)) / 765
def dark(c, t=0.22): return mix(c, "#b4aed6", t * 1.2) if _lum(c) > 0.85 else mix(c, "#1a1020", t)
SK, SK2, SK3 = "#ffe0c8", "#f6cba6", "#e3a77c"

def C(name, hs, hair, out, c1, c2="#ffffff", c3="#24304a", skin=SK, hat=None, eyes=None, mouth=None, ex=(), hair2=None,
      eyec="#5a3a2a", legs="#3b4258", girl=False, shoes="#3a2a24", pose=None, props=(), vibe="cute", shorts=False):
    return dict(name=name, hs=hs, hair=hair, hair2=hair2 or hair, out=out, c1=c1, c2=c2, c3=c3, skin=skin, hat=hat, eyes=eyes, mouth=mouth,
                ex=list(ex), eyec=eyec, legs=legs, girl=girl, shoes=shoes, pose=pose, props=list(props), vibe=vibe, shorts=shorts)

BOSS_LOOK = C("루피", "messy", "#1f1d26", "vest_open", "#d8352e", "#f2c94c", hat="straw", eyes="round", mouth="laugh", vibe="fun",
              ex=["fur_cuffs", "scar_luffy", "x_scar", "sash_yellow"], eyec="#3a2a22", legs="#3f6fb5", shorts=True, shoes="sandal", pose="fist")
ROSTER = {
    "scout": [
        C("나미", "long_wavy", "#f68a3c", "stripe", "#ffffff", "#4f8fe0", eyec="#b5652e", girl=True, vibe="glam", legs="#4f6fb0", pose="hold", props=["climatact"], ex=["nami_tattoo", "log_pose", "earrings_gold"]),
        C("우솝", "curly", "#2b2220", "overalls", "#c58a4a", "#fff8ee", skin=SK3, vibe="fun", legs="#c58a4a", pose="fist", props=["slingshot"], ex=["long_nose", "goggles_head"]),
        C("캐럿", "bunny", "#f6dd8a", "dress", "#8fd0f2", "#ffffff", eyec="#e0484a", girl=True, vibe="cute", pose="wave", ex=["bunny_ears"], legs="#fbf6ee"),
        C("비비", "pony", "#5aaef0", "dress", "#ffffff", "#5aaef0", eyec="#3a5a8a", girl=True, vibe="cute", pose="wave", ex=["earrings_gold"], legs="#f0e6d8"),
    ],
    "analysis": [
        C("로빈", "blunt", "#2b2a38", "coat", "#7b5aa6", "#f4efe6", eyec="#3a6aa8", girl=True, vibe="glam", pose="cross", ex=["hana_arms", "sunglasses_head"], legs="#3a3448"),
        C("로우", "short", "#23222c", "hoodie", "#f2c94c", "#23222c", hat="law", vibe="cool", pose="shoulder", props=["nodachi"], ex=["heart_jolly", "sideburns", "goatee", "earrings_gold", "eyebags"], eyec="#6a5a3a", legs="#3a3a40"),
        C("징베", "topknot", "#23222c", "kimono", "#ec8b3c", "#ffffff", "#2a5ea8", skin="#86b6dc", vibe="cool", mouth="flat", pose="cross", eyec="#3a3a4a", legs="#2a5ea8", ex=["tusks"]),
        C("마르코", "pineapple", "#f4d35a", "vest_open", "#8a6ac0", "#8a6ac0", vibe="cool", eyes="sleepy", pose="cross", props=["blue_flame"], ex=["wb_tattoo", "beads_blue"], eyec="#4a5a7a"),
        C("베가펑크", "big_round", "#c89ae6", "labcoat", "#ffffff", "#6ab0e6", vibe="fun", pose="hold", props=["tablet"], eyec="#5a4a8a", ex=["goggles_head"]),
    ],
    "build": [
        C("프랑키", "pompadour", "#3aa6ec", "hawaii", "#e64a4a", "#ffd34d", skin=SK2, eyes="shades", mouth="grin", vibe="fun", pose="cheer", ex=["star_tattoo", "metal_nose"]),
        C("상디", "sanji", "#f6d260", "suit", "#232633", "#5a8fe0", "#232633", eyec="#3a5a8a", vibe="cool", pose="pockets", ex=["cigarette", "curly_brow", "goatee_blond"]),
        C("쵸파", "chopper_fur", "#a8693a", "fur", "#a8693a", "#f2d6b0", skin="#f7e2c4", hat="chopper", eyec="#3a2a22", vibe="cute", pose="wave", ex=["blue_nose"], legs="#e88aa8", shorts=True, shoes="hoof"),
        C("브룩", "afro", "#1f1d26", "suit", "#1f1d26", "#ffffff", "#c9483b", skin="#f6f2ea", hat="tophat", eyes="skull", mouth="skull", vibe="fun", pose="hold", props=["cane"]),
        C("에이스", "messy", "#1f1d26", "shirtless", SK2, skin=SK2, hat="ace", mouth="grin", vibe="cool", pose="fist", props=["flame"], ex=["asce", "ace_belt", "freckles", "beads_red"], eyec="#3a2a22", legs="#2b3a5a", shorts=True),
        C("사보", "wavy", "#f6d260", "coat", "#2f4f8a", "#ffffff", hat="sabo", eyec="#3a4a7a", vibe="cool", pose="shoulder", props=["pipe"], ex=["scar_sabo", "cravat"]),
        C("키드", "flame", "#e0402c", "fur_coat", "#c0392b", "#f2a6a0", mouth="kid", vibe="cool", pose="cross", ex=["metal_arm", "stitch_scar", "goggles_head"], eyec="#c9a23a", legs="#2b2a38"),
        C("야마토", "pony", "#f6f6f6", "kimono", "#ffffff", "#e05a5a", "#8c4bd0", hair2="#6ad8cc", eyec="#e0584a", girl=True, vibe="cool", pose="shoulder", props=["club"], ex=["wrist_cuffs", "horns"], legs="#ffffff"),
    ],
    "audit": [
        C("조로", "short", "#47a05a", "kimono", "#3f7d4f", "#2b5a3a", "#d9493b", skin=SK2, eyes="zoro", mouth="smirk", vibe="cool", pose="cross", props=["swords3"], ex=["arm_bandana", "earrings3"], eyec="#3a2a22", legs="#2b3a2e"),
        C("미호크", "short", "#1f1d26", "mihawk", "#24161c", "#8a1f2c", hat="mihawk", eyes="hawk", mouth="flat", vibe="cool", pose="cross", props=["yoru"],
          ex=["mustache_thin", "sideburns", "gold_sleeves", "cross_necklace"], legs="#efeae0", shoes="#1f1d26"),
        C("스모커", "slick", "#eeeef2", "coat", "#f4f4f6", "#3a5f9a", mouth="flat", vibe="cool", pose="cross", props=["jitte"], ex=["cigars3", "fur_collar"], eyec="#5a5a6a"),
        C("타시기", "bob", "#2c2c5a", "tshirt", "#f6a8bc", "#f6a8bc", eyec="#3a3a6a", girl=True, vibe="cute", pose="hold", props=["katana_up"], ex=["glasses_square"], legs="#4a5a8a"),
        C("가프", "short", "#c4c4c8", "marine", "#ffffff", "#3a5f9a", hat="marine", mouth="grin", vibe="fun", pose="fist", ex=["beard_white", "scar_garp"], eyec="#3a2a22"),
        C("코비", "side", "#f6a8c8", "marine", "#ffffff", "#3a5f9a", hat="marine", eyec="#7a4a8a", vibe="cute", pose="wave"),
    ],
    "mail": [
        C("바르톨로메오", "mohawk", "#3aaa6a", "coat", "#2b2a38", "#ffffff", mouth="wild", vibe="fun", pose="fist", ex=["nose_ring"]),   # 봉쿠레 대신 (본부장 10-31)
        C("버기", "messy", "#3a86e0", "coat", "#d03a32", "#f4d35a", hat="captain", mouth="laugh", vibe="fun", pose="fist", props=["knife"], ex=["red_nose", "clown_paint"], eyec="#3a2a22"),
        C("페로나", "drills", "#f6a0c6", "dress", "#2b2a38", "#e0484a", hat="crown", eyec="#6a3a5a", girl=True, vibe="cute", pose="wave", props=["ghost"], ex=["star_cheek"], legs="#2b2a38"),
        C("오키쿠", "pony", "#2b2230", "kimono", "#f4b6c4", "#ffffff", "#7a3a8a", eyec="#4a2a3a", girl=True, vibe="glam", mouth="lips", pose="hold", props=["sword_hip"], legs="#f4b6c4"),   # 바르톨로메오 대신 (본부장 10-31)
    ],
    "pt": [
        C("우타", "uta", "#e0483c", "dress", "#ffffff", "#6a6a7a", hair2="#f6f6f8", eyec="#8c4bd0", girl=True, vibe="cute", pose="sing", props=["mic"], ex=["headphones"], legs="#f6f6f8"),
        C("핸콕", "blunt", "#1f1d26", "dress", "#d03a32", "#ffffff", eyec="#3a3a7a", mouth="lips", girl=True, vibe="glam", pose="hip", ex=["snake_earrings"], legs="#f6e0d0"),
        C("시라호시", "long_wavy", "#f6a6c8", "dress", "#fbd3e2", "#ffffff", hat="crown", eyec="#4a90d8", girl=True, vibe="cute", pose="side", ex=["mermaid_tail", "earrings_gold"]),   # 레베카 대신 (본부장 10-31) · 인어 공주
        C("히요리", "blunt", "#1f1d26", "kimono", "#ec6a84", "#ffffff", "#f4d35a", eyec="#4a2a3a", girl=True, vibe="glam", pose="hold", props=["fan"], ex=["kanzashi"], legs="#ec6a84"),
    ],
    "retro": [
        C("샹크스", "messy", "#c8352c", "cloak", "#1f1d26", "#ffffff", vibe="cool", pose="onearm", props=["sword_hip"], ex=["open_shirt_white", "scar_shanks", "stubble", "no_left_arm"], eyec="#3a2a22", legs="#5a4a3a"),
        C("흰수염", "short", "#f4f4f4", "coat", "#f6f2e8", "#8a6ac0", skin=SK2, hat="bandana", mouth="flat", vibe="cool", pose="hold", props=["bisento"], ex=["mustache_crescent"], eyec="#4a4a5a"),
        C("레베카", "long", "#f6a0c6", "dress", "#ec6a94", "#f6d36b", eyec="#3a6aa8", girl=True, vibe="cute", pose="hold", props=["katana_up"], ex=["headband_flower"], legs="#f6e0d0"),   # 레일리 대신 (본부장 10-31)
        C("크로커다일", "slick", "#1f1d26", "fur_coat", "#3a2f2a", "#6a5a4a", mouth="smirk", vibe="cool", pose="hip", ex=["scar_croc", "hook"], eyec="#4a3a2a"),
    ],
}
def _defaults(lk):
    v = lk["vibe"]
    if not lk["eyes"]: lk["eyes"] = {"cute": "cute", "cool": "cool", "glam": "glam", "fun": "round"}[v]
    if not lk["mouth"]: lk["mouth"] = {"cute": "open", "cool": "smirk", "glam": "lips" if lk["girl"] else "smirk", "fun": "grin"}[v]
    if not lk["pose"]: lk["pose"] = {"cute": "wave", "cool": "cross", "glam": "hip", "fun": "fist"}[v]
for _l in ROSTER.values():
    for _lk in _l: _defaults(_lk)
_defaults(BOSS_LOOK)
# 한 손 든 포즈는 몇 명만 (본부장 10-30 '몇몇만 빼고 손 내려줘 · 루피도') — 에이스 불꽃 · 우솝 새총 · 쵸파 인사만 유지
RAISE_KEEP = {"에이스", "우솝", "쵸파"}
for _lk in [BOSS_LOOK] + [l for _l in ROSTER.values() for l in _l]:
    if _lk["pose"] in ("wave", "fist") and _lk["name"] not in RAISE_KEEP: _lk["pose"] = "side"
def new_look(team, i=0): return ROSTER[team][i % len(ROSTER[team])]

# ───────────── 머리 · 얼굴 ─────────────
FACE = "M -46,-4 C -47,-38 -25,-55 0,-55 C 25,-55 47,-38 46,-4 C 45,23 26,43 0,44 C -26,43 -45,23 -46,-4 Z"
CAP = "M -53,14 C -60,-46 -28,-72 0,-72 C 28,-72 60,-46 53,14 "

def strands(pts, k=0.22):
    """머리카락 덩어리: 점과 점 사이를 바깥으로 휘는 곡선으로 (지그재그 직선 대신)"""
    d = ""
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        cx, cy = (ax + bx) / 2 + (by - ay) * k, (ay + by) / 2 - (bx - ax) * k
        d += f"Q {cx:.1f},{cy:.1f} {bx},{by} "
    return d

def hair_front(lk):
    hs = lk["hs"]; extra = ""
    H = f'fill="url(#hair§)" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"'
    if hs == "messy":     # 루피 · 에이스 · 버기 · 샹크스
        p = CAP + "L 50,6 " + strands([(50, 6), (40, -20), (34, 4), (24, -22), (14, 8), (4, -24), (-6, 6), (-16, -22), (-26, 4), (-34, -20), (-44, 2), (-53, 14)]) + "Z"
        extra = f'<path d="M -51,-6 Q -66,-10 -64,-22 Q -56,-18 -50,-24 Z M 51,-6 Q 66,-10 64,-22 Q 56,-18 50,-24 Z" {H}/>'
    elif hs == "short":
        p = CAP + "L 48,-6 " + strands([(48, -6), (38, -26), (28, -12), (16, -28), (6, -14), (-6, -30), (-16, -14), (-28, -28), (-38, -12), (-48, -20), (-53, 14)], 0.18) + "Z"
    elif hs == "slick":
        p = "M -53,10 C -60,-46 -28,-72 0,-72 C 28,-72 60,-46 53,10 L 47,-6 C 40,-42 -40,-42 -47,-6 Z"
    elif hs == "blunt":
        p = CAP + "L 48,-6 Q 0,-12 -48,-6 Z"
        extra = f'<path d="M 40,-14 Q 54,22 46,60 L 57,58 Q 62,10 50,-14 Z M -40,-14 Q -54,22 -46,60 L -57,58 Q -62,10 -50,-14 Z" {H}/>'
    elif hs in ("side", "long", "long_wavy", "pony", "bob", "bunny", "drills", "wavy"):
        p = CAP + "L 48,-4 " + strands([(48, -4), (40, -20), (30, -6), (18, -28), (4, -12), (-10, -34), (-24, -18), (-36, -28), (-46, -6), (-53, 14)]) + "Z"
        if hs in ("long", "long_wavy", "bob", "bunny", "wavy"):
            ln = 34 if hs in ("bob", "bunny") else 58
            extra = f'<path d="M 42,-16 Q 55,14 48,{ln} L 58,{ln - 4} Q 62,8 52,-16 Z M -42,-16 Q -55,14 -48,{ln} L -58,{ln - 4} Q -62,8 -52,-16 Z" {H}/>'
    elif hs == "sanji":
        p = CAP + "L 48,-6 " + strands([(48, -6), (38, -26), (28, -12), (16, -28), (6, -10)]) + "Q 4,14 -14,32 Q -36,32 -48,14 L -53,14 Z"
    elif hs == "curly":
        p = CAP + "Q 0,-58 -53,14 Z"
        extra = "".join(f'<circle cx="{42 * math.cos(a):.1f}" cy="{-30 + 40 * math.sin(a):.1f}" r="14" {H}/>' for a in [math.pi * (1.02 + k * 0.12) for k in range(9)])
    elif hs == "afro": p = CAP + "Q 0,-58 -53,14 Z"
    elif hs == "big_round": p = CAP + "Q 0,-58 -53,14 Z"
    elif hs == "pompadour":
        p = "M -50,8 C -56,-36 -30,-60 0,-60 C 30,-60 56,-36 50,8 L 44,-14 Q 0,-30 -44,-14 Z"
        extra = f'<path d="M -40,-48 C -46,-92 52,-106 64,-62 C 68,-44 44,-36 20,-44 C 0,-50 -26,-40 -40,-48 Z" {H}/>'
    elif hs == "pineapple":
        p = "M -50,6 C -56,-40 -28,-62 0,-62 C 28,-62 56,-40 50,6 L 44,-18 Q 0,-34 -44,-18 Z"
        extra = f'<path d="M -18,-58 Q -30,-80 -28,-94 Q -14,-80 -6,-74 Q -2,-96 4,-106 Q 10,-90 10,-74 Q 20,-84 30,-94 Q 30,-76 20,-58 Z" {H}/>'
    elif hs == "mohawk":
        p = "M -10,-56 C -12,-80 12,-80 10,-56 Z"
        extra = f'<path d="M -12,-50 C -20,-104 20,-104 12,-50 Z" {H}/>'
    elif hs == "flame":
        p = CAP + "L 46,-12 " + strands([(46, -12), (30, -24), (14, -14), (0, -28), (-14, -14), (-30, -24), (-46, -12), (-53, 14)]) + "Z"
        extra = f'<path d="M -48,-40 Q -60,-80 -56,-98 Q -40,-74 -30,-62 Q -30,-100 -22,-120 Q -10,-90 -6,-70 Q 2,-108 6,-126 Q 16,-96 16,-70 Q 26,-100 34,-116 Q 38,-84 34,-62 Q 48,-82 62,-94 Q 60,-62 48,-40 Z" {H}/>'
    elif hs == "uta":
        p = CAP + "L 48,-4 " + strands([(48, -4), (36, -22), (24, -8), (12, -28), (0, -12), (-12, -28), (-24, -10), (-38, -24), (-46, -6), (-53, 14)]) + "Z"
    elif hs == "bun": p = CAP + "Q 0,-58 -53,14 Z"
    elif hs == "topknot": p = "M -50,6 C -56,-42 -28,-66 0,-66 C 28,-66 56,-42 50,6 L 46,-10 C 38,-42 -38,-42 -46,-10 Z"
    elif hs == "chopper_fur": p = "M -54,30 C -64,-40 -30,-70 0,-70 C 30,-70 64,-40 54,30 L 44,24 C 46,-28 -46,-28 -44,24 Z"
    else: p = CAP + "Q 0,-58 -53,14 Z"
    return p, extra

def hair_back(lk):
    hs, ex = lk["hs"], lk["ex"]; s = ""
    H = f'fill="url(#hair§)" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"'
    if "bunny_ears" in ex:
        for sx in (-1, 1):
            s += f'<g transform="translate({sx * 20},-60) rotate({sx * 8})"><ellipse cx="0" cy="-40" rx="13" ry="44" fill="#fbf6ee" stroke="{INK}" stroke-width="2"/><ellipse cx="0" cy="-38" rx="6" ry="34" fill="#f8b8c8"/></g>'
    if hs in ("long", "blunt"):
        s += f'<path d="M -56,-6 C -66,44 -62,96 -46,118 L 46,118 C 62,96 66,44 56,-6 Z" {H}/>'
    elif hs == "long_wavy":
        s += f'<path d="M -56,-6 C -68,40 -66,90 -52,114 Q -42,126 -30,114 Q -20,128 -8,116 Q 4,128 16,116 Q 28,128 38,114 Q 50,124 54,110 C 66,84 66,40 56,-6 Z" {H}/>'
    elif hs == "pony":
        s += f'<path d="M 30,-60 C 72,-76 100,-30 88,20 C 82,48 68,70 58,84 C 64,50 62,14 46,-14 Z" {H}/>'
        if lk["hair2"] != lk["hair"]: s += f'<path d="M 76,26 C 74,50 66,70 58,84 C 74,68 84,48 88,20 Z" fill="{lk["hair2"]}"/>'
    elif hs == "afro":
        s += "".join(f'<circle cx="{58 * math.cos(a):.1f}" cy="{-34 + 52 * math.sin(a):.1f}" r="24" {H}/>' for a in [math.pi * (0.9 + k * 0.1) for k in range(13)])
        s += '<circle cx="0" cy="-40" r="56" fill="url(#hair§)"/>'
    elif hs == "big_round": s += f'<ellipse cx="0" cy="-46" rx="66" ry="62" {H}/>'
    elif hs == "drills":
        for sx in (-1, 1):
            for k in range(4): s += f'<ellipse cx="{sx * (58 - k * 2)}" cy="{-6 + k * 20}" rx="{22 - k * 3}" ry="13" {H}/>'
    elif hs == "uta":
        for sx, c in ((-1, "hair2"), (1, "hair")):
            col = lk[c]
            s += f'<path d="M {sx * 46},-10 Q {sx * 62},30 {sx * 52},64 L {sx * 40},60 Q {sx * 48},26 {sx * 36},-10 Z" fill="{col}" stroke="{INK}" stroke-width="2"/>'
            s += f'<circle cx="{sx * 44}" cy="-70" r="17" fill="none" stroke="{INK}" stroke-width="13"/><circle cx="{sx * 44}" cy="-70" r="17" fill="none" stroke="{col}" stroke-width="9"/>'
    elif hs == "wavy":
        for sx in (-1, 1): s += "".join(f'<circle cx="{sx * (52 - k * 2)}" cy="{-14 + k * 16}" r="14" {H}/>' for k in range(4))
    elif hs == "bun": s += f'<circle cx="0" cy="-78" r="18" {H}/>'
    elif hs == "topknot": s += f'<ellipse cx="0" cy="-72" rx="12" ry="10" {H}/>'
    elif hs in ("bob", "bunny"): s += f'<path d="M -56,-10 C -62,20 -58,40 -46,48 L 46,48 C 58,40 62,20 56,-10 Z" {H}/>'
    return s

def eyes(lk, working):
    e, s = lk["eyes"], ""
    if e == "shades":
        return f'<path d="M -36,-2 L 36,-2 L 34,14 Q 20,22 4,12 L -4,12 Q -20,22 -34,14 Z" fill="#2a4a7a" stroke="{INK}" stroke-width="2"/><path d="M -28,3 L -16,3" stroke="#9fd3f2" stroke-width="3" stroke-linecap="round"/>'
    if e == "skull":
        for sx in (-1, 1): s += f'<ellipse cx="{sx * 17}" cy="6" rx="12" ry="13" fill="#24222c"/><circle cx="{sx * 17 + 4}" cy="1" r="3" fill="#ffffff" opacity=".9"/>'
        return s + '<path d="M -4,22 L 4,22 L 0,15 Z" fill="#24222c"/>'
    if e == "hawk": return hawk_eyes(working)
    for sx in (-1, 1):
        x = sx * 17
        if e == "zoro" and sx == 1:
            s += f'<path d="M {x - 9},8 Q {x},12 {x + 9},8" stroke="{INK}" stroke-width="2.6" fill="none" stroke-linecap="round"/><path d="M {x + 1},-12 L {x - 2},26" stroke="#b05a48" stroke-width="2.6" stroke-linecap="round"/>'
            s += f'<path d="M {x - 12},-6 L {x + 12},-10" stroke="#2b1d18" stroke-width="3.4" stroke-linecap="round"/>'
            continue
        if not working:
            s += f'<path d="M {x - 10},8 Q {x},-2 {x + 10},8" stroke="{INK}" stroke-width="3" fill="none" stroke-linecap="round"/>'
            continue
        ry = {"cute": 13.5, "round": 12.5, "cool": 9, "glam": 11.5, "hawk": 10, "sleepy": 10, "makeup": 11.5, "zoro": 9}.get(e, 12)
        if e == "glam": s += f'<ellipse cx="{x}" cy="-1" rx="13" ry="8" fill="#d88aa8" opacity=".35"/>'
        if e == "hawk":
            s += f'<ellipse cx="{x}" cy="8" rx="9" ry="{ry}" fill="#f6d260" stroke="#2b1d18" stroke-width="1.5"/><ellipse cx="{x}" cy="8" rx="2.2" ry="{ry - 2}" fill="#2b1d18"/>'
        else:
            s += (f'<ellipse cx="{x}" cy="8" rx="10" ry="{ry}" fill="#ffffff"/><ellipse cx="{x}" cy="9" rx="8.6" ry="{ry - 1}" fill="url(#iris§)"/>'
                  f'<ellipse cx="{x}" cy="{9 - ry * 0.55:.1f}" rx="8.6" ry="{ry * 0.42:.1f}" fill="#1e1612" opacity=".38"/>'
                  f'<ellipse cx="{x}" cy="9" rx="8.6" ry="{ry - 1}" fill="none" stroke="{mix(lk["eyec"], "#000000", 0.55)}" stroke-width="1.1"/>'
                  f'<ellipse cx="{x}" cy="10" rx="4" ry="{ry * 0.45}" fill="#1e1612"/>'
                  f'<ellipse cx="{x}" cy="{9 + ry * 0.55:.1f}" rx="5" ry="{ry * 0.22:.1f}" fill="#ffffff" opacity=".28"/>'
                  f'<circle cx="{x + 3.5}" cy="{8 - ry * 0.35}" r="{4 if e == "cute" else (2.4 if e == "cool" else 3.2)}" fill="#ffffff"/>'
                  f'<circle cx="{x - 3.2}" cy="{8 + ry * 0.45}" r="1.6" fill="#ffffff" opacity=".9"/>')
            if e == "cute": s += f'<path d="M {x - 4},2 l 1.2,-3 l 1.2,3 l 3,1.2 l -3,1.2 l -1.2,3 l -1.2,-3 l -3,-1.2 Z" fill="#ffffff"/>'
            if e == "sleepy": s += f'<rect x="{x - 11}" y="-6" width="22" height="10" fill="url(#skin§)"/><path d="M {x - 11},4 L {x + 11},4" stroke="#2b1d18" stroke-width="3.2" stroke-linecap="round"/>'
        lw = 4.6 if e in ("glam", "makeup") else (3.6 if lk["girl"] else 3)
        if e == "cool" or e == "hawk":
            s += f'<path d="M {x - 11},{3 - ry * 0.5} Q {x},{-3 - ry * 0.9} {x + 11},{1 - ry * 0.7}" stroke="#2b1d18" stroke-width="3.4" fill="none" stroke-linecap="round"/>'
            s += f'<path d="M {x - 12},{-10 + (4 if sx == -1 else 0)} L {x + 12},{-10 + (0 if sx == -1 else 4)}" stroke="#2b1d18" stroke-width="3.4" stroke-linecap="round"/>'
        elif e != "sleepy":
            s += f'<path d="M {x - 11},{2 - ry * 0.4} Q {x},{-2 - ry} {x + 11},{2 - ry * 0.4}" stroke="#2b1d18" stroke-width="{lw}" fill="none" stroke-linecap="round"/>'
            s += f'<path d="M {x - 8},{-6 - ry} Q {x},{-10 - ry} {x + 8},{-6 - ry}" stroke="{mix(lk["hair"], "#2b1d18", 0.45)}" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
            if lk["girl"] or e in ("glam", "makeup"):
                s += f'<path d="M {x + sx * 10},{2 - ry * 0.4} q {sx * 6},-2 {sx * 8},-7" stroke="#2b1d18" stroke-width="2.6" fill="none" stroke-linecap="round"/>'
    return s

def hawk_eyes(working):
    """미호크: 가늘고 끝이 올라간 매의 눈 · 금빛 홍채를 윗눈꺼풀이 덮음 · 작은 눈동자 · 미간으로 내려오는 굵은 눈썹"""
    s, D = "", "#1e1612"
    for sx in (-1, 1):
        x = sx * 17; ix, ox = x - sx * 11, x + sx * 12          # 눈 안쪽 · 바깥쪽 끝 (바깥이 더 높음)
        brow = f'<path d="M {ox + sx * 2},-11 Q {x},-11 {ix - sx * 1},0 L {ix},3.5 Q {x},-5 {ox + sx * 1},-6.5 Z" fill="{D}"/>'
        if not working:                                           # 눈 감음: 일자 눈꺼풀 + 같은 눈썹
            s += brow + f'<path d="M {ix},10 Q {x},12 {ox},6" stroke="{D}" stroke-width="3" fill="none" stroke-linecap="round"/>'
            continue
        eye = f"M {ix},10 Q {x - sx * 1},1 {ox},5 Q {x},15 {ix},10 Z"
        s += f'<defs><clipPath id="hk§{sx + 1}"><path d="{eye}"/></clipPath></defs>'
        s += f'<path d="{eye}" fill="#fbf7ee"/>'
        s += (f'<g clip-path="url(#hk§{sx + 1})"><circle cx="{x + sx * 0.5}" cy="9" r="6" fill="url(#hawkiris§)" stroke="#6a4210" stroke-width="1.2"/>'
              f'<circle cx="{x + sx * 0.5}" cy="9" r="2.3" fill="{D}"/><circle cx="{x + sx * 0.5 + 2}" cy="7" r="1.2" fill="#ffffff"/>'
              f'<path d="M {ix},3 Q {x},-2 {ox},0 L {ox},5 Q {x - sx * 1},1 {ix},10 Z" fill="#000000" opacity=".25"/></g>')    # 윗눈꺼풀 그늘
        s += f'<path d="M {ix - sx * 1},10.5 Q {x - sx * 1},0.5 {ox + sx * 3},4" stroke="{D}" stroke-width="3.6" fill="none" stroke-linecap="round"/>'   # 굵은 윗눈꺼풀 + 꼬리
        s += f'<path d="M {x - sx * 2},14 Q {x + sx * 5},13.5 {ox - sx * 1},8" stroke="{D}" stroke-width="1.3" fill="none" stroke-linecap="round" opacity=".7"/>'
        s += brow
    return s + f'<path d="M -3,-4 L -2,2 M 3,-4 L 2,2" stroke="{D}" stroke-width="1.2" opacity=".45" stroke-linecap="round"/>'   # 미간 주름

def mouth(lk):
    m = lk["mouth"]
    if m == "laugh":
        return (f'<path d="M -16,21 Q 0,48 16,21 Q 0,25 -16,21 Z" fill="#9a3a3a" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
                '<path d="M -8,34 Q 0,41 8,34 Q 0,30 -8,34 Z" fill="#f48a9a"/><path d="M -14,22 Q 0,26 14,22 L 13,26 Q 0,29 -13,26 Z" fill="#ffffff"/>')
    if m == "open":
        return f'<path d="M -8,23 Q 0,35 8,23 Q 0,25 -8,23 Z" fill="#a8404a" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/><path d="M -4,30 Q 0,33 4,30 Q 0,28 -4,30 Z" fill="#f48a9a"/>'
    if m == "grin":
        return (f'<path d="M -13,22 Q 0,40 13,22 Q 0,25 -13,22 Z" fill="#8a2f36" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
                '<path d="M -11.5,23 Q 0,26 11.5,23 L 10.5,26.5 Q 0,29.5 -10.5,26.5 Z" fill="#ffffff"/><path d="M -6,32.5 Q 0,37.5 6,32.5 Q 0,29.5 -6,32.5 Z" fill="#f48a9a"/>')
    if m == "wild":         # 바르톨로메오: 크게 벌린 입 + 들쭉날쭉한 이
        return (f'<path d="M -17,21 Q 0,44 17,21 Q 0,26 -17,21 Z" fill="#7a2430" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>'
                '<path d="M -15,22.5 L -11,28 L -8,23.6 L -4,29 L 0,24.2 L 4,29 L 8,23.6 L 11,28 L 15,22.5 Q 0,26 -15,22.5 Z" fill="#ffffff"/>'
                '<path d="M -8,36 Q 0,42 8,36 Q 0,32 -8,36 Z" fill="#f48a9a"/>')
    if m == "kid":
        return (f'<path d="M -15,21 Q 0,40 15,21 Z" fill="#ffffff" stroke="#4a1a3a" stroke-width="3.6" stroke-linejoin="round"/><path d="M -13,25 L 13,25" stroke="#d8c8c0" stroke-width="1.2"/>'
                '<path d="M -15,21 Q 0,17 15,21" stroke="#4a1a3a" stroke-width="3" fill="none" stroke-linecap="round"/>')
    if m == "skull":
        return f'<rect x="-13" y="25" width="26" height="10" rx="3" fill="#ffffff" stroke="#24222c" stroke-width="2"/>' + "".join(f'<path d="M {x},25 L {x},35" stroke="#24222c" stroke-width="1.5"/>' for x in (-6, 0, 6))
    if m == "teeth":
        return f'<rect x="-10" y="23" width="20" height="8" rx="3" fill="#ffffff" stroke="{INK}" stroke-width="2"/><path d="M -3,23 L -3,31 M 3,23 L 3,31" stroke="{INK}" stroke-width="1.2"/>'
    if m == "smirk": return f'<path d="M -6,27 Q 2,29 8,23" stroke="{INK}" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
    if m == "flat": return f'<path d="M -6,27 L 6,27" stroke="{INK}" stroke-width="2.4" stroke-linecap="round"/>'
    if m == "lips": return '<path d="M -6,26 Q 0,22 6,26 Q 0,32 -6,26 Z" fill="#e0405a"/>'
    return f'<path d="M -6,25 Q 0,31 6,25" stroke="{INK}" stroke-width="2.4" fill="none" stroke-linecap="round"/>'

def face_extras(lk):
    ex, s, sk = lk["ex"], "", lk["skin"]
    op = {"cute": .5, "glam": .4, "cool": .18, "fun": .32}.get(lk["vibe"], .38)
    if lk["eyes"] not in ("skull", "hawk"): s += f'<ellipse cx="-27" cy="22" rx="11" ry="6" fill="url(#blush§)" opacity="{min(1, op * 2.2):.2f}"/><ellipse cx="27" cy="22" rx="11" ry="6" fill="url(#blush§)" opacity="{min(1, op * 2.2):.2f}"/>'
    if not any(k in ex for k in ("long_nose", "red_nose", "blue_nose")) and lk["eyes"] != "skull":
        s += f'<path d="M -1,17 Q 1,19 2,17" stroke="{mix(sk, INK, 0.45)}" stroke-width="1.8" fill="none" stroke-linecap="round"/>'
    if "scar_luffy" in ex: s += '<path d="M -31,24 L -15,24 M -28,21 L -28,27 M -22,21 L -22,27 M -18,21 L -18,27" stroke="#b0604e" stroke-width="1.6" stroke-linecap="round"/>'
    if "long_nose" in ex: s += f'<path d="M -2,12 C 10,12 30,14 40,18 C 42,22 38,24 34,23 C 22,22 8,22 -2,22 Z" fill="url(#skin§)" stroke="{INK}" stroke-width="2"/>'
    if "red_nose" in ex: s += f'<circle cx="0" cy="13" r="7.5" fill="#e0302a" stroke="{INK}" stroke-width="2"/><circle cx="-2.6" cy="10" r="2.2" fill="#ffffff" opacity=".8"/>'
    if "blue_nose" in ex: s += f'<ellipse cx="0" cy="18" rx="7" ry="5" fill="#3a86e0" stroke="{INK}" stroke-width="1.8"/><circle cx="-2" cy="16.5" r="1.8" fill="#ffffff"/>'
    if "freckles" in ex: s += "".join(f'<circle cx="{sx * x}" cy="{y}" r="1.5" fill="#c07a50"/>' for sx in (-1, 1) for x, y in ((24, 18), (29, 21), (21, 22)))
    if "curly_brow" in ex: s += '<path d="M 9,-14 Q 17,-20 25,-14 Q 28,-8 22,-8 Q 18,-10 21,-13" stroke="#c9a23a" stroke-width="2.2" fill="none" stroke-linecap="round"/>'
    if "goatee" in ex: s += '<path d="M -4,34 L 4,34 L 2,42 L -2,42 Z" fill="#23222c"/>'
    if "goatee_blond" in ex: s += '<path d="M -3,35 L 3,35 L 1,41 L -1,41 Z" fill="#e0b84a"/>'
    if "eyebags" in ex: s += f'<path d="M -24,22 Q -17,25 -10,22 M 10,22 Q 17,25 24,22" stroke="{mix(sk, INK, 0.3)}" stroke-width="1.5" fill="none"/>'
    if "scar_sabo" in ex: s += '<path d="M -31,-4 Q -24,-10 -14,-6 Q -4,0 -6,12 Q -8,22 -18,24 Q -30,22 -32,10 Z" fill="#d88a7a" opacity=".16"/>'
    if "scar_shanks" in ex: s += "".join(f'<path d="M {-24 + k * 5},-8 L {-18 + k * 5},22" stroke="#b0604e" stroke-width="1.6" stroke-linecap="round"/>' for k in range(3))
    if "scar_croc" in ex: s += '<path d="M -34,16 L 34,14" stroke="#b0604e" stroke-width="2" stroke-linecap="round"/>' + "".join(f'<path d="M {x},11 L {x},19" stroke="#b0604e" stroke-width="1.4"/>' for x in (-20, -6, 8, 22))
    if "scar_garp" in ex: s += '<path d="M -30,-8 L -10,10" stroke="#b0604e" stroke-width="1.8" stroke-linecap="round"/>'
    if "stubble" in ex: s += "".join(f'<circle cx="{x}" cy="{y}" r="1" fill="#8a6a5a"/>' for x, y in ((-10, 36), (-4, 38), (2, 38), (8, 36), (-7, 34), (5, 34)))
    if "nose_ring" in ex: s += '<path d="M -3,21 A 3,3 0 1 0 3,21" stroke="#d9b25f" stroke-width="2" fill="none"/>'
    if "clown_paint" in ex: s += "".join(f'<path d="M {sx * 17 - 7},-6 L {sx * 17 + 7},-6" stroke="#3a86e0" stroke-width="3" stroke-linecap="round"/>' for sx in (-1, 1))
    if "star_cheek" in ex: s += '<path d="M 30,16 l 2,4 l 4,.5 l -3,3 l .8,4 l -3.8,-2 l -3.8,2 l .8,-4 l -3,-3 l 4,-.5 Z" fill="#f4d35a"/>'
    if "beard_white" in ex: s += '<path d="M -34,18 Q -30,52 0,58 Q 30,52 34,18 Q 20,34 0,34 Q -20,34 -34,18 Z" fill="#f6f6f6" stroke="#cfcfd4" stroke-width="2"/>'
    if "mustache_crescent" in ex: s += '<path d="M -70,-14 Q -40,30 0,20 Q 40,30 70,-14 Q 40,40 0,30 Q -40,40 -70,-14 Z" fill="#fbfbfb" stroke="#cfcfd4" stroke-width="2"/>'
    if "mustache_thin" in ex:
        s += '<path d="M -1,21 Q -8,19 -14,22 Q -19,24 -21,18 Q -17,23 -12,20 Q -6,17 -1,19 Z M 1,21 Q 8,19 14,22 Q 19,24 21,18 Q 17,23 12,20 Q 6,17 1,19 Z" fill="#23222c"/>'
        s += '<path d="M -1.6,33 L 1.6,33 L 1,47 L 0,50 L -1,47 Z" fill="#23222c"/>'
    smoke = lambda x, y: "".join(f'<circle cx="{x + dx_}" cy="{y + dy_}" r="{r_}" fill="#e4e7ec" stroke="#c3c8d0" stroke-width="1" opacity=".9"/>' for dx_, dy_, r_ in ((0, 0, 3), (4, -7, 4), (1, -15, 5)))
    if "cigarette" in ex: s += '<path d="M 5,28 L 33,21" stroke="#3d2820" stroke-width="6" stroke-linecap="round"/><path d="M 5,28 L 32,21.3" stroke="#ffffff" stroke-width="3.8" stroke-linecap="round"/><path d="M 10,26.8 L 14,25.8" stroke="#e8a23a" stroke-width="3.8"/><path d="M 30,21.8 L 33,21" stroke="#ff7a3a" stroke-width="3.8" stroke-linecap="round"/>' + smoke(37, 15)
    if "cigar" in ex: s += '<path d="M 6,29 L 30,27" stroke="#3d2820" stroke-width="7.4" stroke-linecap="round"/><path d="M 6,29 L 29,27.1" stroke="#7a4a2a" stroke-width="5" stroke-linecap="round"/><path d="M 12,28.5 L 15,28.2" stroke="#d9a63a" stroke-width="5"/><path d="M 28,27.2 L 31,27" stroke="#9a9aa2" stroke-width="5" stroke-linecap="round"/>' + smoke(36, 18)
    if "cigars3" in ex:     # 스모커: 입 오른쪽으로 시가 3개 (본부장 10-31)
        for ex_, ey_ in ((30, 19), (32, 27), (30, 35)):
            s += (f'<path d="M 4,28 L {ex_},{ey_}" stroke="#3d2820" stroke-width="7.4" stroke-linecap="round"/><path d="M 4,28 L {ex_ - 1},{ey_}" stroke="#7a4a2a" stroke-width="4.8" stroke-linecap="round"/>'
                  f'<path d="M {4 + (ex_ - 4) * 0.25:.1f},{28 + (ey_ - 28) * 0.25:.1f} L {4 + (ex_ - 4) * 0.36:.1f},{28 + (ey_ - 28) * 0.36:.1f}" stroke="#d9a63a" stroke-width="4.8"/>'
                  f'<path d="M {ex_ - 2},{ey_} L {ex_ + 1},{ey_}" stroke="#ff7a3a" stroke-width="4.8" stroke-linecap="round"/>')
        s += smoke(38, 16)
    if "tusks" in ex: s += "".join(f'<path d="M {sx * 12},31 L {sx * 9},18 L {sx * 6},31 Z" fill="#fbfaf4" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round"/>' for sx in (-1, 1))
    if "stitch_scar" in ex: s += '<path d="M -27,-12 L -12,26" stroke="#9a4a3e" stroke-width="2" stroke-linecap="round"/>' + "".join(f'<path d="M {-27 + k * 3.75 - 3},{-12 + k * 9.5 + 1} l 6,-2.4" stroke="#9a4a3e" stroke-width="1.6" stroke-linecap="round"/>' for k in range(1, 5))
    if "metal_nose" in ex: s += f'<rect x="-5" y="13" width="10" height="8" rx="3" fill="#c9ced6" stroke="{INK}" stroke-width="1.6"/><circle cx="-2" cy="15.5" r="1.3" fill="#ffffff"/>'
    if "sideburns" in ex: s += "".join(f'<path d="M {sx * 45},-6 Q {sx * 47},10 {sx * 41},26 L {sx * 37},24 Q {sx * 41},10 {sx * 40},-6 Z" fill="#1f1d26"/>' for sx in (-1, 1))
    if "glasses_round" in ex: s += "".join(f'<circle cx="{sx * 17}" cy="8" r="13" fill="none" stroke="#c9a45c" stroke-width="2.2"/>' for sx in (-1, 1)) + '<path d="M -4,6 L 4,6" stroke="#c9a45c" stroke-width="2"/>'
    if "glasses_square" in ex: s += "".join(f'<rect x="{sx * 17 - 13}" y="-3" width="26" height="22" rx="5" fill="none" stroke="#d03a32" stroke-width="2.4"/>' for sx in (-1, 1)) + '<path d="M -4,6 L 4,6" stroke="#d03a32" stroke-width="2"/>'
    if "earrings3" in ex: s += "".join(f'<circle cx="48" cy="{10 + k * 7}" r="3" fill="#e6c25a" stroke="{INK}" stroke-width="1"/>' for k in range(3))
    if "earrings_gold" in ex: s += "".join(f'<circle cx="{sx * 47}" cy="20" r="3.5" fill="#e6c25a" stroke="{INK}" stroke-width="1"/>' for sx in (-1, 1))
    if "snake_earrings" in ex: s += "".join(f'<path d="M {sx * 47},14 q {sx * 4},6 0,12 q {-sx * 4},6 0,12" stroke="#8c4bd0" stroke-width="3" fill="none" stroke-linecap="round"/>' for sx in (-1, 1))
    return s

def top_extras(lk):
    ex, s = lk["ex"], ""
    if "goggles_head" in ex:
        s += '<path d="M -52,-30 Q 0,-46 52,-30" stroke="#5a4232" stroke-width="7" fill="none"/>' + "".join(f'<circle cx="{sx * 18}" cy="-40" r="12" fill="#a8dcf6" stroke="#5a4232" stroke-width="4"/><circle cx="{sx * 18 - 3}" cy="-44" r="3" fill="#ffffff"/>' for sx in (-1, 1))
    if "sunglasses_head" in ex: s += f'<path d="M -30,-50 Q 0,-58 30,-50 L 28,-42 Q 14,-38 2,-44 L -2,-44 Q -14,-38 -28,-42 Z" fill="#3a2f2a" stroke="{INK}" stroke-width="1.5"/>'
    if "horns" in ex: s += "".join(f'<path d="M {sx * 14},-58 Q {sx * 18},-90 {sx * 30},-100 Q {sx * 28},-80 {sx * 26},-56 Z" fill="#e0584a" stroke="{INK}" stroke-width="2"/>' for sx in (-1, 1))
    if "headphones" in ex:
        s += '<path d="M -54,4 C -60,-60 60,-60 54,4" stroke="#f4f4f6" stroke-width="8" fill="none"/>'
        s += "".join(f'<rect x="{sx * 56 - 9}" y="-8" width="18" height="26" rx="8" fill="#6a6a7a" stroke="{INK}" stroke-width="2"/>' for sx in (-1, 1))
    if "headband_flower" in ex: s += '<path d="M -44,-34 Q 0,-60 44,-34" stroke="#f6d36b" stroke-width="6" fill="none"/>' + "".join(f'<circle cx="{30 + 7 * math.cos(a):.1f}" cy="{-44 + 7 * math.sin(a):.1f}" r="5" fill="#ffffff" stroke="#f2a6c0" stroke-width="1"/>' for a in [k * 1.2566 for k in range(5)]) + '<circle cx="30" cy="-44" r="3.5" fill="#f6d36b"/>'
    if "kanzashi" in ex: s += '<path d="M 22,-48 L 50,-76" stroke="#d9b25f" stroke-width="3"/><circle cx="46" cy="-70" r="8" fill="#ec6a84" stroke="#3d2820" stroke-width="1.5"/><circle cx="46" cy="-70" r="3" fill="#ffffff"/>'
    return s

def hat(lk):
    h = lk["hat"]; S = f'stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"'
    if not h: return ""
    if h == "straw":
        return (f'<ellipse cx="0" cy="-54" rx="74" ry="17" fill="url(#straw§)" {S}/><path d="M -42,-56 C -44,-100 44,-100 42,-56 Z" fill="url(#straw§)" {S}/>'
                '<path d="M -42,-60 C -42,-66 42,-66 42,-60 L 42,-52 C 30,-48 -30,-48 -42,-52 Z" fill="#d93a2e"/>')
    if h == "ace":
        return (f'<path d="M -78,-48 C -60,-64 -40,-58 0,-58 C 40,-58 60,-64 78,-48 C 60,-40 40,-44 0,-44 C -40,-44 -60,-40 -78,-48 Z" fill="#f08c2c" {S}/>'
                f'<path d="M -38,-54 C -40,-98 -10,-96 0,-86 C 10,-96 40,-98 38,-54 Z" fill="#f59a3a" {S}/><path d="M -38,-62 L 38,-62 L 38,-54 L -38,-54 Z" fill="#3a2a22"/>'
                f'<circle cx="-14" cy="-70" r="7" fill="#5aaef0" {S}/><circle cx="14" cy="-70" r="7" fill="#f0484a" {S}/>'
                '<path d="M -17,-72 L -16,-71 M -12,-72 L -11,-71 M -17,-66 Q -14,-69 -11,-66" stroke="#1f1d26" stroke-width="1.4" fill="none" stroke-linecap="round"/>'
                '<path d="M 11,-72 L 12,-71 M 16,-72 L 17,-71 M 11,-68 Q 14,-64 17,-68" stroke="#1f1d26" stroke-width="1.4" fill="none" stroke-linecap="round"/>')
    if h in ("tophat", "sabo"):
        c = "#1f1d26" if h == "tophat" else "#2f4f8a"
        g = "".join(f'<circle cx="{sx * 14}" cy="-86" r="10" fill="#a8dcf6" stroke="#5a4232" stroke-width="3.5"/>' for sx in (-1, 1)) if h == "sabo" else ""
        return (f'<ellipse cx="0" cy="-58" rx="54" ry="11" fill="{c}" {S}/><path d="M -34,-60 L -38,-128 Q 0,-136 38,-128 L 34,-60 Z" fill="{c}" {S}/>'
                f'<path d="M -35,-72 L 35,-72 L 34,-62 L -34,-62 Z" fill="{"#d93a2e" if h == "tophat" else "#5a4232"}"/>' + g)
    if h == "chopper":
        ant = "".join(f'<path d="M {sx * 30},-80 Q {sx * 52},-96 {sx * 58},-124 M {sx * 50},-100 Q {sx * 66},-100 {sx * 74},-112 M {sx * 44},-90 Q {sx * 34},-108 {sx * 38},-120" stroke="#8a5530" stroke-width="7" fill="none" stroke-linecap="round"/>' for sx in (-1, 1))
        return (ant + f'<ellipse cx="0" cy="-58" rx="58" ry="12" fill="#f6a0c0" {S}/><path d="M -36,-60 Q -42,-118 0,-120 Q 42,-118 36,-60 Z" fill="#f8acc8" {S}/>'
                '<path d="M -16,-108 L 16,-74 M 16,-108 L -16,-74" stroke="#ffffff" stroke-width="7" stroke-linecap="round"/><path d="M -36,-70 Q 0,-76 36,-70 L 36,-62 Q 0,-66 -36,-62 Z" fill="#3a86e0"/>')
    if h == "law":
        spots = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#6a5040"/>' for x, y, r in ((-28, -58, 6), (-6, -74, 7), (20, -64, 6), (36, -44, 5), (-40, -36, 5), (6, -50, 5)))
        return (f'<path d="M -57,6 C -66,-84 66,-84 57,6 Q 54,-8 47,-15 Q 0,-26 -47,-15 Q -54,-8 -57,6 Z" fill="#fbf8f2" {S}/>'
                '<path d="M -47,-15 Q 0,-26 47,-15" stroke="#e6dfd2" stroke-width="5" fill="none" stroke-linecap="round"/>' + spots)
    if h == "mihawk":
        return (f'<path d="M 18,-92 C 50,-134 104,-112 92,-78 C 74,-96 46,-96 18,-86 Z" fill="#fbf8f2" stroke="#cfcfd4" stroke-width="2"/>'
                f'<ellipse cx="0" cy="-58" rx="86" ry="16" fill="#1f1d26" {S}/><path d="M -36,-60 C -38,-104 38,-104 36,-60 Z" fill="#26242e" {S}/>')
    if h == "marine":
        return (f'<path d="M -46,-48 C -50,-96 50,-96 46,-48 Z" fill="#ffffff" {S}/><path d="M -46,-56 L 46,-56 L 46,-46 L -46,-46 Z" fill="#2f4f8a"/>'
                f'<path d="M -40,-46 Q -10,-26 30,-44 Q 0,-36 -40,-46 Z" fill="#24304a" {S}/><path d="M -8,-80 L 8,-80 L 0,-68 Z" fill="#c9a45c"/>')
    if h == "captain":
        return (f'<g transform="translate(0,-54) scale(.78) translate(0,54)">'      # 버기 선장모자 22% 줄임 (본부장 10-31)
                f'<path d="M -86,-46 Q -40,-120 0,-118 Q 40,-120 86,-46 Q 40,-64 0,-62 Q -40,-64 -86,-46 Z" fill="#24222c" {S}/><path d="M -80,-50 Q -40,-66 0,-64 Q 40,-66 80,-50" stroke="#e6c25a" stroke-width="3" fill="none"/></g>')
    if h == "bandana":
        return f'<path d="M -53,-2 C -60,-62 60,-62 53,-2 C 40,-14 -40,-14 -53,-2 Z" fill="#24304a" {S}/><path d="M 48,-16 L 70,-4 L 56,6 Z" fill="#24304a" {S}/>'
    if h == "crown":
        return f'<path d="M -20,-62 L -22,-90 L -10,-76 L 0,-96 L 10,-76 L 22,-90 L 20,-62 Z" fill="#f4d35a" {S}/><circle cx="0" cy="-74" r="3.5" fill="#e0484a"/>'
    return ""

# ───────────── 몸 · 팔 · 포즈 · 무기 ─────────────
TORSO = "M -30,50 C -34,68 -28,94 -26,124 L 26,124 C 28,94 34,68 30,50 C 18,40 -18,40 -30,50 Z"
POSES = {   # (화면 왼쪽 팔, 화면 오른쪽 팔) 어깨 → 팔꿈치 → 손
    "side":    ([(-28, 54), (-38, 88), (-37, 120)], [(28, 54), (38, 88), (37, 120)]),
    "wave":    ([(-28, 54), (-38, 88), (-37, 120)], [(28, 54), (52, 36), (64, 4)]),
    "fist":    ([(-28, 54), (-38, 88), (-37, 120)], [(28, 54), (50, 42), (54, 8)]),
    "cheer":   ([(-28, 54), (-52, 36), (-64, 4)], [(28, 54), (52, 36), (64, 4)]),
    "hip":     ([(-28, 54), (-38, 88), (-37, 120)], [(28, 54), (50, 84), (30, 110)]),
    "cross":   ([(-28, 54), (-36, 82), (12, 92)], [(28, 54), (36, 86), (-12, 98)]),
    "hold":    ([(-28, 54), (-38, 88), (-37, 120)], [(28, 54), (44, 86), (38, 112)]),
    "shoulder":([(-28, 54), (-38, 88), (-37, 120)], [(28, 54), (50, 70), (36, 44)]),
    "pockets": ([(-28, 54), (-36, 88), (-26, 116)], [(28, 54), (36, 88), (26, 116)]),
    "sing":    ([(-28, 54), (-38, 88), (-37, 120)], [(28, 54), (40, 80), (16, 58)]),
    "onearm":  (None, [(28, 54), (38, 88), (37, 120)]),
    "type":    ([(-28, 54), (-34, 86), (-16, 104)], [(28, 54), (34, 86), (16, 104)]),
}
IN_FRONT = {"cross", "type"}

def arm(pts, color, fist=False, hand=True, skin="url(#skin§)"):
    d = "M " + " L ".join(f"{x},{y}" for x, y in pts); hx, hy = pts[-1]
    a = (f'<path d="{d}" stroke="{INK}" stroke-width="17" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
         f'<path d="{d}" stroke="{color}" stroke-width="12.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
         f'<path d="{d}" transform="translate(-2.6,-1)" stroke="#ffffff" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity=".28"/>')
    h = f'<circle cx="{hx}" cy="{hy}" r="{10 if fist else 8.5}" fill="{skin}" stroke="{INK}" stroke-width="2.2"/>' if hand else ""
    return a, h

def blade(x1, y1, x2, y2, w=4.2, col="#dfe6ee"):
    return (f'<path d="M {x1},{y1} L {x2},{y2}" stroke="{INK}" stroke-width="{w + 3}" stroke-linecap="round"/>'
            f'<path d="M {x1},{y1} L {x2},{y2}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>')

def stick(x1, y1, x2, y2, w, col):
    return (f'<path d="M {x1},{y1} L {x2},{y2}" stroke="{INK}" stroke-width="{w + 3.4}" stroke-linecap="round"/>'
            f'<path d="M {x1},{y1} L {x2},{y2}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>')

def props_behind(lk, R):
    s = ""; hx, hy = R[-1] if R else (0, 0)
    for p in lk["props"]:
        if p == "yoru":       # 미호크: 등에 멘 큰 검
            s += blade(-26, 150, 44, -54, 10, "#1f1d26") + '<path d="M -20,138 L 40,-48" stroke="#d9a63a" stroke-width="1.4" opacity=".8"/>'
            s += f'<path d="M 22,-66 L 68,-42" stroke="{INK}" stroke-width="11" stroke-linecap="round"/><path d="M 22,-66 L 68,-42" stroke="#d9a63a" stroke-width="7" stroke-linecap="round"/>'
            s += "".join(f'<circle cx="{22 + k * 11.5}" cy="{-66 + k * 6}" r="2.4" fill="#3a6ae0" stroke="#1e2a5a" stroke-width=".8"/>' for k in (0, 1, 3, 4))
            s += stick(44, -54, 56, -90, 7, "#d9a63a") + '<circle cx="58" cy="-95" r="6.5" fill="#3a6ae0" stroke="#3d2820" stroke-width="2"/><circle cx="56" cy="-97" r="2" fill="#ffffff" opacity=".8"/>'
        elif p == "jitte":    # 스모커: 등에 멘 십수
            s += stick(-32, 140, 40, -40, 10, "#4a4f5a") + stick(30, -16, 48, -22, 6, "#4a4f5a")
        elif p == "nodachi":  # 로우: 어깨에 멘 긴 칼
            s += stick(58, 96, -66, -100, 8, "#24222c") + "".join(f'<path d="M {58 - k * 22},{96 - k * 35} l -5,4 m 0,-8 l 10,8" stroke="#ffffff" stroke-width="1.6"/>' for k in range(1, 5))
            s += f'<ellipse cx="46" cy="78" rx="9" ry="5" fill="#f4f1ea" stroke="{INK}" stroke-width="1.6"/>'
        elif p == "pipe": s += stick(hx + 4, hy + 6, -52, -66, 6, "#8a93a3")
        elif p == "club":
            s += stick(hx + 4, hy + 6, -50, -70, 14, "#3a3448") + "".join(f'<circle cx="{-50 + k * 14}" cy="{-70 + k * 19}" r="3" fill="#c9ced6"/>' for k in range(4))
        elif p == "bisento":
            s += stick(hx, hy - 140, hx, 206, 6, "#7a5236") + f'<path d="M {hx - 3},{hy - 138} Q {hx + 34},{hy - 170} {hx + 14},{hy - 208} Q {hx + 6},{hy - 170} {hx - 3},{hy - 160} Z" fill="#dfe6ee" stroke="{INK}" stroke-width="2"/>'
        elif p == "climatact": s += stick(hx, hy - 84, hx, hy + 60, 5, "#3a86e0") + "".join(f'<rect x="{hx - 4}" y="{hy - 70 + k * 40}" width="8" height="4" fill="#ffffff"/>' for k in range(4))
        elif p == "cane": s += stick(hx, hy, hx + 4, 204, 4, "#24222c") + f'<circle cx="{hx}" cy="{hy - 4}" r="5" fill="#dfe6ee" stroke="{INK}" stroke-width="1.6"/>'
    return s

def props_front(lk, R):
    s = ""; hx, hy = R[-1] if R else (0, 0)
    for p in lk["props"]:
        if p == "swords3":    # 조로: 허리에 찬 칼 세 자루 (하양 · 빨강 · 검정 손잡이)
            for k, col in enumerate(("#f4f1ea", "#c0392b", "#2b2a33")):
                y = 104 + k * 6; s += stick(22, y + 6, 62, y + 46, 6, "#1f1d26") + stick(22, y + 6, 4, y - 20, 6, col) + f'<ellipse cx="22" cy="{y + 6}" rx="6" ry="4" fill="#c9a45c" stroke="{INK}" stroke-width="1.4"/>'
        elif p == "sword_hip":
            s += stick(-22, 112, -64, 160, 6, "#1f1d26") + stick(-22, 112, -6, 86, 6, "#3a2a22") + '<ellipse cx="-22" cy="112" rx="6" ry="4" fill="#c9a45c" stroke="#3d2820" stroke-width="1.4"/>'
        elif p == "katana_up":
            s += blade(hx, hy - 6, hx + 26, hy - 104) + stick(hx - 4, hy + 16, hx, hy, 6, "#2b2a5a") + f'<ellipse cx="{hx + 1}" cy="{hy - 6}" rx="7" ry="4" fill="#c9a45c" stroke="{INK}" stroke-width="1.4"/>'
        elif p == "slingshot":
            s += stick(hx, hy - 6, hx, hy - 24, 5, "#8a5530") + stick(hx, hy - 24, hx - 13, hy - 44, 5, "#8a5530") + stick(hx, hy - 24, hx + 13, hy - 44, 5, "#8a5530")
            s += f'<path d="M {hx - 13},{hy - 44} Q {hx},{hy - 30} {hx + 13},{hy - 44}" stroke="#e0484a" stroke-width="2" fill="none"/>'
        elif p == "flame":
            s += (f'<path d="M {hx},{hy - 6} C {hx - 26},{hy - 30} {hx - 8},{hy - 52} {hx - 2},{hy - 74} C {hx + 6},{hy - 56} {hx + 22},{hy - 50} {hx + 14},{hy - 70} C {hx + 34},{hy - 44} {hx + 22},{hy - 14} {hx},{hy - 6} Z" fill="#ff8a2c" stroke="#d0461a" stroke-width="2"/>'
                  f'<path d="M {hx},{hy - 10} C {hx - 12},{hy - 26} {hx - 2},{hy - 40} {hx + 2},{hy - 50} C {hx + 8},{hy - 36} {hx + 14},{hy - 26} {hx},{hy - 10} Z" fill="#ffd34d"/>')
        elif p == "knife": s += blade(hx, hy - 8, hx + 4, hy - 38, 5)
        elif p == "tablet": s += f'<rect x="{hx - 14}" y="{hy - 30}" width="28" height="38" rx="4" fill="#24304a" stroke="{INK}" stroke-width="2"/><rect x="{hx - 10}" y="{hy - 26}" width="20" height="26" rx="2" fill="#7fd0f0"/>'
        elif p == "fan":
            s += f'<path d="M {hx},{hy} L {hx - 26},{hy - 36} A 44,44 0 0 1 {hx + 26},{hy - 36} Z" fill="#e0484a" stroke="{INK}" stroke-width="2"/><path d="M {hx},{hy} L {hx - 13},{hy - 40} M {hx},{hy} L {hx},{hy - 44} M {hx},{hy} L {hx + 13},{hy - 40}" stroke="#f4d35a" stroke-width="1.6"/>'
        elif p == "mic":
            s += stick(hx, hy, hx - 4, hy - 22, 5, "#5a5a6a") + f'<circle cx="{hx - 5}" cy="{hy - 28}" r="8" fill="#c9ced6" stroke="{INK}" stroke-width="2"/>'
        elif p == "ghost":
            s += (f'<path d="M 50,-40 C 50,-70 92,-70 92,-40 L 92,-20 Q 86,-14 80,-20 Q 74,-14 68,-20 Q 62,-14 56,-20 Q 50,-14 50,-20 Z" fill="#ffffff" stroke="#c9c2e0" stroke-width="2"/>'
                  '<circle cx="64" cy="-44" r="3.4" fill="#2b2a38"/><circle cx="78" cy="-44" r="3.4" fill="#2b2a38"/><path d="M 66,-34 Q 71,-28 76,-34" fill="#f48a9a"/>')
        elif p == "blue_flame":
            for sx in (-1, 1):
                s += f'<path d="M {sx * 30},50 C {sx * 46},38 {sx * 52},20 {sx * 62},10 C {sx * 56},28 {sx * 66},34 {sx * 72},28 C {sx * 66},50 {sx * 50},60 {sx * 32},62 Z" fill="#7fd6f6" stroke="#3a9ad0" stroke-width="2" opacity=".9"/>'
    return s

def outfit(lk, team):
    o, c1, c2, c3 = lk["out"], lk["c1"], lk["c2"], lk["c3"]; S = f'stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"'
    s = ""
    if o == "shirtless": s += f'<path d="{TORSO}" fill="url(#skin§)" {S}/><path d="M -8,72 Q -6,82 -8,92 M 8,72 Q 6,82 8,92" stroke="{mix(lk["skin"], INK, 0.3)}" stroke-width="1.6" fill="none"/>'
    elif o == "overalls": s += f'<path d="{TORSO}" fill="{c2}" {S}/><path d="M -22,78 L 22,78 L 26,124 L -26,124 Z" fill="url(#cloth§)" {S}/><path d="M -16,46 L -16,80 M 16,46 L 16,80" stroke="{c1}" stroke-width="7"/>'
    else: s += f'<path d="{TORSO}" fill="url(#cloth§)" {S}/>'
    if o == "vest_open":
        s += '<path d="M -13,44 L 13,44 L 9,118 L -9,118 Z" fill="url(#skin§)"/>' + "".join(f'<circle cx="{sx * 14}" cy="{62 + k * 18}" r="2.6" fill="{c2}" stroke="{INK}" stroke-width="1"/>' for sx in (-1, 1) for k in range(3))
        if "x_scar" in lk["ex"]: s += '<path d="M -8,62 L 8,82 M 8,62 L -8,82" stroke="#d07a6a" stroke-width="2.4" stroke-linecap="round"/>'
        if "sash_yellow" in lk["ex"]: s += f'<path d="M -27,108 L 27,108 L 27,122 L -27,122 Z" fill="#f2c94c" {S}/>'
    elif o == "stripe":
        s += "".join(f'<path d="M -31,{66 + k * 12} L 31,{66 + k * 12}" stroke="{c2}" stroke-width="5.5"/>' for k in range(4)) + '<path d="M -10,42 Q 0,54 10,42 Z" fill="url(#skin§)"/>'
    elif o == "tshirt": s += '<path d="M -10,42 Q 0,54 10,42 Z" fill="url(#skin§)"/>'
    elif o == "dress": s += f'<path d="M -12,42 L 0,56 L 12,42 Z" fill="{c2}"/>'
    elif o in ("coat", "marine", "labcoat", "cloak", "fur_coat"):
        s += f'<path d="M -11,42 L 11,42 L 11,124 L -11,124 Z" fill="{c2}"/><path d="M -11,42 L -20,74 L -11,124 M 11,42 L 20,74 L 11,124" stroke="{dark(c1, 0.35)}" stroke-width="2" fill="none"/>'
        if o == "marine": s += "".join(f'<rect x="{sx * 26 - 9}" y="44" width="18" height="7" rx="3.5" fill="#e6c25a" stroke="{INK}" stroke-width="1.2"/>' for sx in (-1, 1))
        if o == "fur_coat" or "fur_collar" in lk["ex"]: s += "".join(f'<circle cx="{x}" cy="46" r="9" fill="{c2 if o == "fur_coat" else "#efe8d8"}" stroke="{INK}" stroke-width="1.5"/>' for x in (-28, -15, 0, 15, 28))
    elif o == "mihawk":
        s += '<path d="M -15,43 L 15,43 L 7,100 L -7,100 Z" fill="url(#skin§)"/>'                                                     # 열린 가슴
        s += f'<path d="M -10,58 Q -4,62 0,60 Q 4,62 10,58 M 0,64 L 0,92 M -6,74 L 6,74 M -5,84 L 5,84" stroke="{mix(lk["skin"], INK, 0.32)}" stroke-width="1.3" fill="none"/>'
        s += f'<path d="M -15,43 L -7,100 L -12,100 L -22,46 Z M 15,43 L 7,100 L 12,100 L 22,46 Z" fill="{c2}" {S}/>'               # 진홍 안감(옷깃)
        s += f'<path d="M -27,104 L 27,104 L 27,114 L -27,114 Z" fill="#2a2420" {S}/><rect x="-7" y="102.5" width="14" height="13" rx="2" fill="#d9a63a" stroke="{INK}" stroke-width="1.4"/><rect x="-3.5" y="106" width="7" height="6" rx="1" fill="#8a5a14"/>'
    elif o == "suit": s += f'<path d="M -13,42 L 13,42 L 0,74 Z" fill="{c2}"/><path d="M -3.5,48 L 3.5,48 L 4.5,80 L 0,88 L -4.5,80 Z" fill="{c3}"/>'
    elif o == "kimono": s += f'<path d="M -17,42 L 0,82 L 17,42" stroke="{c2}" stroke-width="6" fill="none"/><path d="M -11,42 L 0,66 L 11,42 Z" fill="url(#skin§)"/><path d="M -31,96 L 31,96 L 30,110 L -30,110 Z" fill="{c3}" {S}/>'
    elif o == "hawaii": s += '<path d="M -13,42 L 13,42 L 0,80 Z" fill="url(#skin§)"/>' + "".join(f'<circle cx="{x}" cy="{y}" r="4.5" fill="{c2}"/>' for x, y in ((-18, 60), (17, 70), (-15, 96), (18, 104), (-2, 114)))
    elif o == "hoodie": s += f'<path d="M -31,86 L 31,86 L 31,95 L -31,95 Z" fill="{c2}"/><path d="M -5,46 L -5,64 M 5,46 L 5,64" stroke="{c2}" stroke-width="2.6" stroke-linecap="round"/>'
    elif o == "fur": s += f'<ellipse cx="0" cy="84" rx="20" ry="26" fill="{c2}"/>'
    elif o == "swan":
        s += "".join(f'<path d="M {sx * 26},48 q {sx * 4},-24 {sx * 16},-20 q {sx * 6},2 {sx * 2},9" stroke="#ffffff" stroke-width="7" fill="none" stroke-linecap="round"/><path d="M {sx * 42},-6 l {sx * 9},2 l {-sx * 9},3 Z" fill="#f29a3a"/>' for sx in (-1, 1))
        s += f'<path d="M -31,92 L 31,92 L 30,100 L -30,100 Z" fill="{c2}"/>'
    s += (f'<g clip-path="url(#torso§)"><path d="{TORSO}" transform="translate(4,3)" fill="none" stroke="#ffffff" stroke-width="5" opacity=".3"/>'
          f'<path d="{TORSO}" transform="translate(-6,-2)" fill="none" stroke="#000000" stroke-width="9" opacity=".13"/></g>')
    if "beads_red" in lk["ex"]: s += "".join(f'<circle cx="{19 * math.cos(a):.1f}" cy="{44 + 13 * math.sin(a):.1f}" r="3.8" fill="#e0302a" stroke="{INK}" stroke-width="1"/>' for a in [math.pi * (0.1 + k * 0.1) for k in range(9)])
    if "beads_blue" in lk["ex"]: s += "".join(f'<circle cx="{17 * math.cos(a):.1f}" cy="{46 + 11 * math.sin(a):.1f}" r="3.4" fill="#3a86e0" stroke="{INK}" stroke-width="1"/>' for a in [math.pi * (0.1 + k * 0.1) for k in range(9)])
    if "open_shirt_white" in lk["ex"]:
        s += f'<path d="{TORSO}" fill="#f6f4ee" {S}/><path d="M -13,43 L 13,43 L 0,86 Z" fill="url(#skin§)"/><path d="M -13,43 L 0,86 L 13,43" stroke="#cfcac0" stroke-width="2" fill="none"/>'
    if "wb_tattoo" in lk["ex"]:
        s += '<path d="M -8,64 L 8,80 M 8,64 L -8,80" stroke="#3a4a9a" stroke-width="3" stroke-linecap="round"/><path d="M -12,70 Q 0,82 12,70 Q 0,77 -12,70 Z" fill="#3a4a9a"/>'
    if "heart_jolly" in lk["ex"]:
        s += '<circle cx="0" cy="72" r="9" fill="#1f1d26"/><path d="M -5,72 Q 0,78 5,72" stroke="#f2c94c" stroke-width="2" fill="none" stroke-linecap="round"/><circle cx="-3.4" cy="68.5" r="1.4" fill="#f2c94c"/><circle cx="3.4" cy="68.5" r="1.4" fill="#f2c94c"/>'
        s += '<path d="M -14,62 L -9,67 M 14,62 L 9,67 M -14,82 L -9,77 M 14,82 L 9,77" stroke="#1f1d26" stroke-width="3" stroke-linecap="round"/>'
    if "ace_belt" in lk["ex"]:
        s += f'<path d="M -27,110 L 27,110 L 27,119 L -27,119 Z" fill="#5a3a22" {S}/><rect x="-7" y="108.5" width="14" height="12" rx="2" fill="#e8a23a" stroke="{INK}" stroke-width="1.4"/>'
        s += '<text x="0" y="118" font-family="Arial, sans-serif" font-size="9" font-weight="900" fill="#5a3a22" text-anchor="middle">A</text>'
    if "hana_arms" in lk["ex"]:
        for sx in (-1, 1):
            s += f'<path d="M {sx * 30},52 Q {sx * 40},40 {sx * 46},28" stroke="{INK}" stroke-width="9" fill="none" stroke-linecap="round"/><path d="M {sx * 30},52 Q {sx * 40},40 {sx * 46},28" stroke="url(#skin§)" stroke-width="5.6" fill="none" stroke-linecap="round"/>'
            s += f'<circle cx="{sx * 47}" cy="26" r="4.6" fill="url(#skin§)" stroke="{INK}" stroke-width="1.6"/>'
            s += "".join(f'<ellipse cx="{sx * 30 + 5 * math.cos(a):.1f}" cy="{53 + 5 * math.sin(a):.1f}" rx="3.6" ry="2.2" fill="#f6a6c8" stroke="#d0607e" stroke-width=".7" transform="rotate({math.degrees(a):.0f} {sx * 30 + 5 * math.cos(a):.1f} {53 + 5 * math.sin(a):.1f})"/>' for a in [k * 1.2566 for k in range(5)])
    if "cross_necklace" in lk["ex"]:
        s += '<path d="M -10,44 Q -4,58 0,62 Q 4,58 10,44" stroke="#d9a63a" stroke-width="1.3" fill="none"/>'
        s += f'<path d="M -1.8,61 L 1.8,61 L 1.8,65 L 6,65 L 6,68.5 L 1.8,68.5 L 1.8,78 L -1.8,78 L -1.8,68.5 L -6,68.5 L -6,65 L -1.8,65 Z" fill="#e6b84a" stroke="{INK}" stroke-width="1.1"/>'
    if "cravat" in lk["ex"]: s += f'<path d="M -9,42 Q 0,60 9,42 Q 0,48 -9,42 Z" fill="#ffffff" stroke="{INK}" stroke-width="1.5"/>'
    return s

def skirt_tails(lk):
    o, c1 = lk["out"], lk["c1"]; S = f'stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"'
    if o == "dress": return f'<path d="M -27,104 L 27,104 L 40,162 Q 0,170 -40,162 Z" fill="url(#cloth§)" {S}/><path d="M -38,156 Q 0,164 38,156" stroke="{lk["c2"]}" stroke-width="3" fill="none"/>'
    if o in ("coat", "marine", "labcoat", "fur_coat", "kimono", "swan", "mihawk"):
        ln = 176 if o in ("coat", "fur_coat", "kimono", "mihawk") else 166
        if o == "mihawk":                                          # 긴 코트 자락 + 진홍 안감이 살짝 보임
            return (f'<path d="M -27,112 L -40,{ln} L -12,{ln} L -9,116 Z M 27,112 L 40,{ln} L 12,{ln} L 9,116 Z" fill="url(#cloth§)" {S}/>'
                    f'<path d="M -12,{ln} L -9,116 L -14,116 L -18,{ln} Z M 12,{ln} L 9,116 L 14,116 L 18,{ln} Z" fill="{lk["c2"]}"/>')
        return f'<path d="M -27,112 L -36,{ln} L -10,{ln} L -9,118 Z M 27,112 L 36,{ln} L 10,{ln} L 9,118 Z" fill="url(#cloth§)" {S}/>'
    if o == "cloak": return f'<path d="M -30,48 Q -52,110 -48,186 L -14,186 Q -20,110 -14,50 Z M 30,48 Q 52,110 48,186 L 14,186 Q 20,110 14,50 Z" fill="{c1}" {S}/>'
    return ""

def legs(lk):
    S = f'stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"'; L = lk["legs"]; s = ""
    if "mermaid_tail" in lk["ex"]:      # 시라호시: 분홍 꼬리 + 비늘 + 꼬리지느러미
        tc = "#f48aa8"
        s += f'<path d="M -26,116 C -30,150 -16,180 -4,196 L 4,196 C 16,180 30,150 26,116 Z" fill="{tc}" {S}/>'
        s += "".join(f'<path d="M {-22 + k * 2 + j * 11},{130 + k * 14} q 5.5,6 11,0" stroke="#d0607e" stroke-width="1.4" fill="none"/>' for k in range(4) for j in range(4 - k) if -22 + k * 2 + j * 11 < 18 - k * 4)
        s += f'<path d="M -2,194 C -24,198 -40,206 -42,214 C -24,214 -10,208 0,202 C 10,208 24,214 42,214 C 40,206 24,198 2,194 Z" fill="#f6b4c8" {S}/>'
        s += '<path d="M -10,140 Q -8,166 -2,186" stroke="#ffffff" stroke-width="2.4" fill="none" opacity=".35" stroke-linecap="round"/>'
        return s
    for sx in (-1, 1):
        x0 = -23 if sx == -1 else 3
        cx_ = x0 + 10
        leg = lambda top, bot, w0, w1: f"M {cx_ - w0},{top} Q {cx_ - w0 - 1},{(top + bot) / 2} {cx_ - w1},{bot} L {cx_ + w1},{bot} Q {cx_ + w0 + 1},{(top + bot) / 2} {cx_ + w0},{top} Z"
        if lk["shorts"]:
            s += f'<path d="{leg(146, 202, 7.5, 6)}" fill="url(#skin§)" {S}/><path d="{leg(118, 158, 10.5, 10)}" fill="{L}" {S}/>'
            if "fur_cuffs" in lk["ex"]: s += "".join(f'<circle cx="{cx_ + d}" cy="157" r="3.6" fill="#fbf8f2" stroke="#cfcac0" stroke-width=".9"/>' for d in (-8, -3, 2, 7))
            s += f'<path d="M {cx_ + 3.5},124 L {cx_ + 3.5},154" stroke="#000000" stroke-width="4" opacity=".12" stroke-linecap="round"/>'
        else:
            s += f'<path d="{leg(118, 202, 10.5, 7.5)}" fill="{L}" {S}/>'
            s += f'<path d="M {cx_ + 4},124 Q {cx_ + 5},160 {cx_ + 3},196" stroke="#000000" stroke-width="4.5" fill="none" opacity=".14" stroke-linecap="round"/>'
            s += f'<path d="M {cx_ - 5},126 Q {cx_ - 6},150 {cx_ - 5},170" stroke="#ffffff" stroke-width="2" fill="none" opacity=".22" stroke-linecap="round"/>'
        fx = sx * 13
        if lk["shoes"] == "sandal": s += f'<ellipse cx="{fx}" cy="205" rx="13" ry="6.5" fill="url(#skin§)" {S}/><path d="M {fx - 8},202 Q {fx},198 {fx + 8},202" stroke="#c9a23a" stroke-width="3" fill="none"/>'
        elif lk["shoes"] == "hoof": s += f'<ellipse cx="{fx}" cy="205" rx="11" ry="6" fill="#6a4228" {S}/>'
        else: s += f'<ellipse cx="{fx}" cy="205" rx="14" ry="7" fill="{lk["shoes"]}" {S}/><ellipse cx="{fx - 4}" cy="202.5" rx="5" ry="2" fill="#ffffff" opacity=".35"/>'
    return s

def body(lk, team, pose=None):
    pose = pose or lk["pose"]; Lp, Rp = POSES[pose]
    bare = lk["out"] in ("vest_open", "shirtless", "stripe", "dress", "hawaii", "tshirt")
    col = "url(#skin§)" if bare else "url(#gold§)" if "gold_sleeves" in lk["ex"] else "url(#cloth§)"
    def deco(pts, side="R"):  # 팔에 붙는 캐릭터 표시 (금색 소매 무늬 · 두건 · 별 · ASCE · 어깨 문신 · 로그 포스 · 수갑)
        if not pts: return ""
        ex, out_ = lk["ex"], ""
        def at(seg, t):
            (ax, ay), (bx, by) = pts[seg], pts[seg + 1]; L_ = math.hypot(bx - ax, by - ay) or 1
            return ax + (bx - ax) * t, ay + (by - ay) * t, (bx - ax) / L_, (by - ay) / L_
        def band(seg, t, col, w=5, edge=INK):
            x, y, dx, dy = at(seg, t); px_, py_ = -dy * 7.6, dx * 7.6
            return (f'<path d="M {x - px_:.1f},{y - py_:.1f} L {x + px_:.1f},{y + py_:.1f}" stroke="{edge}" stroke-width="{w + 2.4}" stroke-linecap="round"/>'
                    f'<path d="M {x - px_:.1f},{y - py_:.1f} L {x + px_:.1f},{y + py_:.1f}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>')
        if "gold_sleeves" in ex:
            for seg in range(len(pts) - 1):
                for t in (0.3, 0.72):
                    x, y, _, _ = at(seg, t); out_ += f'<path d="M {x - 3:.1f},{y:.1f} a 3,3 0 1 1 3,3" stroke="#8a5a14" stroke-width="1.3" fill="none"/>'
        if "arm_bandana" in ex and side == "L":
            out_ += band(0, 0.45, "#1f1d26", 6); x, y, _, _ = at(0, 0.45); out_ += f'<path d="M {x - 6:.1f},{y:.1f} l -7,5 l 3,-8 Z" fill="#1f1d26"/>'
        if "star_tattoo" in ex:
            x, y, _, _ = at(1, 0.5); out_ += f'<path d="M {x:.1f},{y - 5:.1f} l 1.5,3.4 l 3.7,.4 l -2.8,2.5 l .8,3.6 l -3.2,-1.9 l -3.2,1.9 l .8,-3.6 l -2.8,-2.5 l 3.7,-.4 Z" fill="#3a86e0"/>'
        if "asce" in ex and side == "L":
            x, y, dx, dy = at(0, 0.55); ang = math.degrees(math.atan2(dy, dx))
            out_ += f'<text x="{x:.1f}" y="{y + 2.4:.1f}" font-family="Arial, sans-serif" font-size="6.4" font-weight="900" fill="#2a2a5a" text-anchor="middle" transform="rotate({ang - 90:.0f} {x:.1f} {y:.1f})">ASCE</text>'
        if "nami_tattoo" in ex and side == "R":
            x, y, _, _ = at(0, 0.35); out_ += f'<path d="M {x - 3:.1f},{y:.1f} a 3,3 0 1 1 3,3 a 5,5 0 1 1 -5,-5" stroke="#3a86e0" stroke-width="1.5" fill="none"/><circle cx="{x + 3:.1f}" cy="{y + 4:.1f}" r="1.8" fill="#f68a3c"/>'
        if "log_pose" in ex and side == "R":
            out_ += band(1, 0.82, "#8a5a30", 4); x, y, dx, dy = at(1, 0.82)
            out_ += f'<circle cx="{x - dy * 9:.1f}" cy="{y + dx * 9:.1f}" r="4.2" fill="#cfeefb" stroke="{INK}" stroke-width="1.2"/><path d="M {x - dy * 9 - 2:.1f},{y + dx * 9:.1f} L {x - dy * 9 + 2:.1f},{y + dx * 9:.1f}" stroke="#e0484a" stroke-width="1.2"/>'
        if "wrist_cuffs" in ex: out_ += band(len(pts) - 2, 0.84, "#8a93a3", 5)
        return out_
    out = {"behind": "", "front": "", "after_head": ""}
    out["behind"] += props_behind(lk, Rp) + legs(lk)
    arms_b, arms_f, hands = "", "", ""
    if Lp and "no_left_arm" not in lk["ex"]:
        metal = "metal_arm" in lk["ex"]
        a, h = arm(Lp, "url(#steel§)" if metal else col, hand="hook" not in lk["ex"], skin="url(#steel§)" if metal else "url(#skin§)"); a += deco(Lp, "L")
        if metal: a += "".join(f'<circle cx="{Lp[0][0] + (Lp[-1][0] - Lp[0][0]) * t:.1f}" cy="{Lp[0][1] + (Lp[-1][1] - Lp[0][1]) * t:.1f}" r="1.8" fill="#5a606a"/>' for t in (0.25, 0.5, 0.75))
        if pose in IN_FRONT: arms_f += a
        else: arms_b += a
        hands += h
        if "hook" in lk["ex"]:
            hx, hy = Lp[-1]; hands += f'<path d="M {hx},{hy - 4} L {hx},{hy + 6} Q {hx},{hy + 22} {hx - 14},{hy + 18}" stroke="{INK}" stroke-width="7" fill="none" stroke-linecap="round"/><path d="M {hx},{hy - 4} L {hx},{hy + 6} Q {hx},{hy + 22} {hx - 14},{hy + 18}" stroke="#e6c25a" stroke-width="4" fill="none" stroke-linecap="round"/>'
    if Rp:
        a, h = arm(Rp, col, fist=pose in ("fist", "shoulder", "hold", "sing"), hand=pose != "pockets"); a += deco(Rp, "R")
        if pose in IN_FRONT: arms_f += a
        elif pose == "sing": out["after_head"] += a
        else: arms_b += a
        if pose == "sing": out["after_head"] += h
        else: hands += h
    if pose == "pockets": hands = ""
    props = {**lk, "props": [p for p in lk["props"] if not (pose == "sing" and p == "mic")]}
    t = arms_b + outfit(lk, team) + skirt_tails(lk) + props_front(props, Rp) + arms_f + hands
    if team: t += (f'<path d="M -44,64 L -32,62 L -31,72 L -43,74 Z" fill="{team}" stroke="{INK}" stroke-width="1.4"/>' if pose in IN_FRONT
                   else f'<path d="M -45,68 L -32,66 L -31,76 L -44,78 Z" fill="{team}" stroke="{INK}" stroke-width="1.4"/>')
    out["front"] = t
    if pose == "sing" and "mic" in lk["props"]: out["after_head"] += props_front({"props": ["mic"]}, Rp)
    return out

def defs(lk, n):
    hc, h2 = lk["hair"], lk["hair2"]; sk = lk["skin"]; c1 = lk["c1"] if lk["out"] != "shirtless" else sk; ic = lk["eyec"]
    def cel(top, bot, at=".58"):
        hi = mix(top, "#ffffff", 0.16)
        return (f'<stop offset="0" stop-color="{hi}"/><stop offset=".16" stop-color="{hi}"/><stop offset=".16" stop-color="{top}"/>'
                f'<stop offset="{at}" stop-color="{top}"/><stop offset="{at}" stop-color="{bot}"/><stop offset="1" stop-color="{mix(bot, "#000000", 0.08)}"/>')
    return (f'<defs><linearGradient id="hair{n}" x1="0" y1="0" x2=".35" y2="1">{cel(hc, dark(h2, 0.2))}</linearGradient>'
            f'<radialGradient id="skin{n}" cx=".4" cy=".32" r=".85"><stop offset="0" stop-color="{sk}"/><stop offset=".84" stop-color="{sk}"/><stop offset=".84" stop-color="{mix(sk, "#c08060", 0.22)}"/><stop offset="1" stop-color="{mix(sk, "#c08060", 0.22)}"/></radialGradient>'
            f'<linearGradient id="cloth{n}" x1="0" y1="0" x2=".45" y2="1">{cel(c1, dark(c1, 0.18), ".6")}</linearGradient>'
            f'<linearGradient id="iris{n}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{mix(ic, "#000000", 0.55)}"/><stop offset=".5" stop-color="{ic}"/><stop offset="1" stop-color="{mix(ic, "#ffffff", 0.45)}"/></linearGradient>'
            f'<linearGradient id="gold{n}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f6d27a"/><stop offset=".55" stop-color="#d9a63a"/><stop offset="1" stop-color="#a8761e"/></linearGradient>'
            f'<linearGradient id="steel{n}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e4e8ee"/><stop offset=".5" stop-color="#9aa3ad"/><stop offset="1" stop-color="#5a606a"/></linearGradient>'
            f'<radialGradient id="hawkiris{n}" cx=".45" cy=".4" r=".7"><stop offset="0" stop-color="#ffe27a"/><stop offset=".6" stop-color="#e8a52a"/><stop offset="1" stop-color="#9a5a12"/></radialGradient>'
            f'<linearGradient id="straw{n}" x1="0" y1="0" x2=".3" y2="1">{cel("#ffe39a", "#e9b456")}</linearGradient>'
            f'<radialGradient id="blush{n}"><stop offset="0" stop-color="#ff7f86" stop-opacity=".9"/><stop offset="1" stop-color="#ff7f86" stop-opacity="0"/></radialGradient>'
            f'<clipPath id="face{n}"><path d="{FACE}"/></clipPath><clipPath id="torso{n}"><path d="{TORSO}"/></clipPath></defs>')

HEAD_SCALE, HEAD_PIVOT = 1.10, 44      # 머리 10% 키움 (본부장 10-31)
def svg(lk, n, team=None, working=True, pose=None, size=None, view=None):
    sk = lk["skin"]; front, extra = hair_front(lk)
    S = f'stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"'
    b = body(lk, team, pose)
    HG = f'<g transform="translate(0,{HEAD_PIVOT}) scale({HEAD_SCALE}) translate(0,{-HEAD_PIVOT})">'      # 머리 전체 키우기 (목 아래를 중심으로)
    g = '<ellipse cx="0" cy="208" rx="42" ry="7" fill="#000000" opacity=".16"/>' + HG + hair_back(lk) + "</g>" + b["behind"] + b["front"]
    g += f'<path d="M -10,34 L 10,34 L 9,46 Q 0,50 -9,46 Z" fill="{mix(sk, "#c08060", 0.22)}"/>'      # 목
    g += HG + "".join(f'<ellipse cx="{sx * 45}" cy="8" rx="7" ry="10" fill="url(#skin§)" {S}/>' for sx in (-1, 1))
    g += f'<path d="{FACE}" fill="url(#skin§)" {S}/>'
    g += f'<g clip-path="url(#face§)"><path d="{FACE}" transform="translate(3.5,2.5)" fill="none" stroke="#ffffff" stroke-width="3.4" opacity=".45"/></g>'
    g += f'<g clip-path="url(#face§)"><path d="{front}" transform="translate(0,6)" fill="{mix(sk, "#b06a50", 0.3)}" opacity=".5"/></g>'   # 앞머리 그림자
    g += eyes(lk, working) + mouth(lk) + face_extras(lk)
    g += f'<path d="{front}" fill="url(#hair§)" {S}/>' + extra
    if not lk["hat"] or lk["hat"] in ("crown", "bandana"):                        # 머리 광택 링 (앞머리 모양 안에서만)
        g += (f'<defs><clipPath id="hf§"><path d="{front}"/></clipPath></defs><g clip-path="url(#hf§)">'
              f'<path d="M -40,-36 Q -20,-52 0,-53 Q 20,-52 40,-36" stroke="#ffffff" stroke-width="6" fill="none" stroke-linecap="round" opacity=".32"/>'
              f'<path d="M -34,-41 Q -16,-53 0,-54" stroke="#ffffff" stroke-width="2.2" fill="none" stroke-linecap="round" opacity=".55"/></g>')
    g += top_extras(lk) + hat(lk) + "</g>" + b["after_head"]
    g = g.replace("§", str(n))
    vb = view or "-120 -180 240 400"
    wh = f' width="{size[0]}" height="{size[1]}"' if size else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"{wh}>{defs(lk, n)}{g}</svg>'
