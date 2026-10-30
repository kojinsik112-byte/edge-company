# 스킨: 귀여운직원 v1 (2026-10-30 본부장 확정 시안 5) — 큰 머리 치비 · 볼 터치 · 전원 다른 머리 · 소품 · 옷
# office_mock.py · roster.py 가 exec 로 불러 쓴다 (rr · el · poly … 그리기 함수는 부르는 쪽 것)
SKINS = ["#ffdcc2", "#f7cfae", "#f2c29b", "#ffe3cf", "#eab991", "#fbd5b8"]
HAIRC = ["#3a2a22", "#5a3b2a", "#2b2a33", "#7a4e33", "#1f1d24", "#8b5e3c", "#b07a4f", "#4a3326", "#6b4a6e", "#a0522d"]
STYLES = ["bob", "long", "short", "bun", "pony", "curly", "twin", "side"]
ACCS = [None, "glasses", "ribbon", "headband", "beret", "earring", "headset", "pin", "round_glasses"]
CLOTH = ["plain", "cardigan", "stripe", "tie", "vest", "hoodie"]
ACC_C = ["#f28fa0", "#7fb3e8", "#f2c14e", "#9ad1a8", "#c39ae8", "#ff9f6e"]
_combos = [(st, hc, ac) for st in STYLES for hc in HAIRC for ac in ACCS]
random.Random(5).shuffle(_combos); _used = [0]
def new_look(team=None, i=0):                     # 전 직원이 서로 다른 머리 · 머리색 · 소품 · 옷 (부르는 순서대로 하나씩)
    st, hc, ac = _combos[_used[0]]; i = _used[0]; _used[0] += 1
    return {"style": st, "hair": hc, "acc": ac, "skin": SKINS[i % len(SKINS)], "cloth": CLOTH[(i * 5) % len(CLOTH)], "accc": ACC_C[(i * 7) % len(ACC_C)]}
INK = "#3b2a22"
BOSS_LOOK = {"name": "총괄 본부장", "style": "side", "hair": "#2b2a33", "acc": None, "skin": "#ffdcc2", "cloth": "tie", "accc": GOLD, "suit": True}

def body(cx, cy, shirt, lk, back=False, suit=False):
    rr([cx - 23, cy + 15, cx + 23, cy + 52], 15, shirt, mix(shirt, INK, 0.45), 2)
    if back:
        if lk["cloth"] == "hoodie": D.chord(P(cx - 18, cy + 10, cx + 18, cy + 30), 0, 180, fill=mix(shirt, INK, 0.2))
        return
    c = lk["cloth"]
    if suit:
        poly([(cx - 9, cy + 16), (cx + 9, cy + 16), (cx, cy + 30)], "#ffffff"); poly([(cx - 3, cy + 20), (cx + 3, cy + 20), (cx + 2, cy + 38), (cx - 2, cy + 38)], GOLD); return
    if c == "cardigan":
        poly([(cx - 12, cy + 16), (cx + 12, cy + 16), (cx, cy + 40)], "#fbf3e2")
        for k in range(3): el([cx - 2, cy + 26 + k * 7, cx + 2, cy + 30 + k * 7], mix(shirt, INK, 0.5))
    elif c == "stripe":
        for k in range(3): rect([cx - 21, cy + 24 + k * 8, cx + 21, cy + 27 + k * 8], mix(shirt, "#ffffff", 0.55))
        poly([(cx - 8, cy + 16), (cx + 8, cy + 16), (cx, cy + 23)], "#ffffff")
    elif c == "tie":
        poly([(cx - 11, cy + 16), (cx + 11, cy + 16), (cx, cy + 26)], "#ffffff"); poly([(cx - 3, cy + 22), (cx + 3, cy + 22), (cx + 2, cy + 40), (cx - 2, cy + 40)], NAVY)
    elif c == "vest":
        poly([(cx - 13, cy + 16), (cx + 13, cy + 16), (cx, cy + 42)], "#ffffff"); poly([(cx - 4, cy + 16), (cx + 4, cy + 16), (cx, cy + 22)], mix(shirt, INK, 0.3))
    elif c == "hoodie":
        D.chord(P(cx - 16, cy + 12, cx + 16, cy + 28), 0, 180, fill=mix(shirt, INK, 0.2))
        line([(cx - 5, cy + 22), (cx - 5, cy + 34)], "#ffffff", 1.5); line([(cx + 5, cy + 22), (cx + 5, cy + 34)], "#ffffff", 1.5)
    else:
        poly([(cx - 10, cy + 16), (cx + 10, cy + 16), (cx, cy + 26)], "#ffffff")

def chibi(cx, cy, shirt, lk, working, back=False, suit=False, stand=False, paper=False, team=None):
    hc, style, acc, skin, R_ = lk["hair"], lk["style"], lk["acc"], lk["skin"], 23
    hl = mix(hc, "#ffffff", 0.38)
    if stand:                                     # 서 있는 모습: 다리 · 구두
        rr([cx - 14, cy + 46, cx - 3, cy + 66], 4, "#3b3f52"); rr([cx + 3, cy + 46, cx + 14, cy + 66], 4, "#3b3f52")
        rr([cx - 17, cy + 62, cx - 2, cy + 70], 4, "#2a2026"); rr([cx + 2, cy + 62, cx + 17, cy + 70], 4, "#2a2026")
    if style == "long": rr([cx - 27, cy - 10, cx + 27, cy + 32], 13, hc, mix(hc, INK, 0.5), 1.5)
    if style == "twin":
        for sx in (-1, 1):
            el([cx + sx * 30 - 9, cy - 4, cx + sx * 30 + 9, cy + 30], hc, mix(hc, INK, 0.5), 1.5); el([cx + sx * 26 - 4, cy - 8, cx + sx * 26 + 4, cy], lk["accc"])
    if style == "pony": el([cx + 14, cy - 18, cx + 36, cy + 22], hc, mix(hc, INK, 0.5), 1.5)
    if style == "bun": el([cx - 10, cy - R_ - 13, cx + 10, cy - R_ + 5], hc, INK, 2)
    body(cx, cy, shirt, lk, back, suit)
    if paper:
        rr([cx + 8, cy + 24, cx + 30, cy + 50], 2, "#ffffff", "#c9bfae", 1.5)
        for k in range(3): line([(cx + 12, cy + 31 + k * 5), (cx + 26, cy + 31 + k * 5)], "#c9ced6", 1.2)
        el([cx + 14, cy + 34, cx + 24, cy + 44], skin, INK, 1.5)
    if back:
        el([cx - R_, cy - R_, cx + R_, cy + R_], hc, INK, 2)
        arc([cx - R_ + 6, cy - R_ + 5, cx + R_ - 6, cy + R_ - 10], 200, 290, hl, 3)
        if style == "curly":
            for k in range(7):
                a_ = math.pi * (k / 6); el([cx + math.cos(a_) * 20 - 7, cy + math.sin(a_) * 6 + 6, cx + math.cos(a_) * 20 + 7, cy + math.sin(a_) * 6 + 20], hc)
        if style == "long": rr([cx - 20, cy + 6, cx + 20, cy + 34], 10, hc)
        if style == "pony": el([cx - 7, cy + 4, cx + 7, cy + 34], hc, mix(hc, INK, 0.5), 1.5)
        if acc == "ribbon":
            poly([(cx - 14, cy - 18), (cx - 2, cy - 12), (cx - 14, cy - 6)], lk["accc"]); poly([(cx + 10, cy - 18), (cx - 2, cy - 12), (cx + 10, cy - 6)], lk["accc"])
        if acc == "headset": arc([cx - R_ - 3, cy - R_ - 3, cx + R_ + 3, cy + R_ + 3], 180, 360, "#3a3f4a", 4)
        if acc == "beret": el([cx - 20, cy - R_ - 6, cx + 16, cy - R_ + 10], lk["accc"])
        return
    el([cx - R_, cy - R_, cx + R_, cy + R_], skin, INK, 2)
    if style == "curly":
        D.pieslice(P(cx - R_ - 1, cy - R_ - 2, cx + R_ + 1, cy + R_ * 0.25), 180, 360, fill=hc)
        for k in range(7):
            a_ = math.pi + math.pi * (k / 6); el([cx + math.cos(a_) * 21 - 8, cy - 4 + math.sin(a_) * 20 - 8, cx + math.cos(a_) * 21 + 8, cy - 4 + math.sin(a_) * 20 + 8], hc)
    elif style == "side":
        D.pieslice(P(cx - R_ - 1, cy - R_ - 2, cx + R_ + 1, cy + R_ * 0.2), 180, 360, fill=hc)
        poly([(cx - R_, cy - 6), (cx + 6, cy - R_ + 2), (cx + R_, cy - 12), (cx + R_, cy - 2), (cx - 2, cy - 10)], hc)
    else:
        D.pieslice(P(cx - R_ - 1, cy - R_ - 2, cx + R_ + 1, cy + R_ * (0.15 if style == "short" else 0.35)), 180, 360, fill=hc)
    arc([cx - R_ - 1, cy - R_ - 1, cx + R_ + 1, cy + R_ + 1], 180, 360, INK, 2)
    if style in ("bob", "long", "twin"):
        rr([cx - R_ - 1, cy - 8, cx - R_ + 7, cy + 14], 4, hc); rr([cx + R_ - 7, cy - 8, cx + R_ + 1, cy + 14], 4, hc)
    if style in ("bob", "long", "bun", "pony"): poly([(cx + 2, cy - R_ + 2), (cx + 12, cy - R_ + 4), (cx + 4, cy - 6)], skin)
    arc([cx - 14, cy - 18, cx + 2, cy - 4], 200, 300, hl, 2)
    ey = cy + 4
    for ex in (cx - 9, cx + 9):
        if working:
            el([ex - 4, ey - 5.5, ex + 4, ey + 5.5], "#2b1d16"); el([ex - 1, ey - 4, ex + 2.5, ey - 0.5], "#ffffff")
        else:
            arc([ex - 5, ey - 4, ex + 5, ey + 4], 200, 340, "#2b1d16", 2.2)
        el([ex - 6 + (2 if ex > cx else -2), ey + 6, ex + 6 + (2 if ex > cx else -2), ey + 11], mix(skin, "#f08f8a", 0.45))
    arc([cx - 4, cy + 8, cx + 4, cy + 15], 20, 160, "#9a4d3d", 2)
    if acc in ("glasses", "round_glasses"):
        g = "#4a3a34" if acc == "glasses" else GOLD
        for ex in (cx - 9, cx + 9):
            if acc == "glasses": rr([ex - 7, ey - 6, ex + 7, ey + 6], 3, None, g, 1.8)
            else: el([ex - 7, ey - 7, ex + 7, ey + 7], None, g, 1.8)
        line([(cx - 2, ey - 1), (cx + 2, ey - 1)], g, 1.8)
    elif acc == "ribbon":
        bx_, by_ = cx + 14, cy - 18
        poly([(bx_ - 12, by_ - 7), (bx_, by_), (bx_ - 12, by_ + 7)], lk["accc"]); poly([(bx_ + 12, by_ - 7), (bx_, by_), (bx_ + 12, by_ + 7)], lk["accc"]); el([bx_ - 3, by_ - 3, bx_ + 3, by_ + 3], mix(lk["accc"], INK, 0.2))
    elif acc == "headband":
        arc([cx - R_ + 1, cy - R_ + 1, cx + R_ - 1, cy + R_ - 1], 200, 340, lk["accc"], 4)
    elif acc == "beret":
        el([cx - 24, cy - R_ - 8, cx + 18, cy - R_ + 10], lk["accc"], mix(lk["accc"], INK, 0.4), 1.5); rr([cx - 3, cy - R_ - 12, cx + 3, cy - R_ - 6], 2, mix(lk["accc"], INK, 0.3))
    elif acc == "earring":
        for sx in (-1, 1): el([cx + sx * 23 - 3, cy + 10, cx + sx * 23 + 3, cy + 16], GOLD)
    elif acc == "headset":
        arc([cx - R_ - 4, cy - R_ - 4, cx + R_ + 4, cy + R_ + 4], 185, 355, "#3a3f4a", 4)
        rr([cx - R_ - 7, cy - 6, cx - R_ + 1, cy + 10], 3, "#3a3f4a"); line([(cx - R_ - 3, cy + 8), (cx - 8, cy + 16)], "#3a3f4a", 2); el([cx - 10, cy + 13, cx - 5, cy + 18], "#3a3f4a")
    elif acc == "pin":
        el([cx - 18, cy - 16, cx - 8, cy - 6], lk["accc"]); el([cx - 15, cy - 13, cx - 11, cy - 9], "#ffffff")
