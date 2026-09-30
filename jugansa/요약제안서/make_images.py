# -*- coding: utf-8 -*-
"""요약제안서용 경관조명 일러스트(SVG) 생성기.

- 경관조명_야경.svg  : 아파트 단지 야간 경관조명(구분페이지 배경)
- 경관조명_1_설계.svg : 경관조명 설계도(평면·입면)
- 경관조명_2_생산.svg : 단지 맞춤 생산 조명 라인업
- 경관조명_3_시공.svg : 고소작업차 직접 시공 장면

실사 사진이 아닌 '일러스트'로 제작 → 가짜 시공사진 오해 없음.
실행: python make_images.py  (assets/ 에 저장)
"""
import os
import random

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
FONT = "Pretendard, 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif"

GOLD = "#F0CF8E"
GOLD_D = "#C8A86A"
WARM = "#FFE3AA"
AMBER = "#D9A74E"


def glow_defs(extra=""):
    return f"""
  <filter id="glow" filterUnits="userSpaceOnUse" x="-200" y="-200" width="2400" height="1400">
    <feGaussianBlur stdDeviation="3.2" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="soft" filterUnits="userSpaceOnUse" x="-200" y="-200" width="2400" height="1400">
    <feGaussianBlur stdDeviation="9"/>
  </filter>
  <radialGradient id="bulb" cx="50%" cy="50%" r="50%">
    <stop offset="0" stop-color="#FFF6DD" stop-opacity="1"/>
    <stop offset=".35" stop-color="{WARM}" stop-opacity=".85"/>
    <stop offset="1" stop-color="{GOLD}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="beamUp" x1="0" y1="1" x2="0" y2="0">
    <stop offset="0" stop-color="{WARM}" stop-opacity=".55"/>
    <stop offset="1" stop-color="{GOLD}" stop-opacity="0"/>
  </linearGradient>
  {extra}"""


# ---------------------------------------------------------------- 공통 요소
def tower(r, x, top, w, ground, side=0, lit_from=None, crown=True, win_p=.24,
          floor_h=15, facade="#0f2238", side_fill="#0b1a2b", corner_lit=True,
          wash=True, halo=True):
    """아파트 한 동. lit_from: 이 y값 아래만 경관조명 점등(시공 진행 표현)."""
    s = []
    h = ground - top
    if side:
        s.append(f'<polygon points="{x+w},{top} {x+w+side},{top+side*.28} '
                 f'{x+w+side},{ground} {x+w},{ground}" fill="{side_fill}"/>')
    s.append(f'<rect x="{x}" y="{top}" width="{w}" height="{h}" fill="{facade}"/>')
    # 창문
    cols = max(2, int((w - 16) // 13))
    cw = (w - 16) / cols
    y = top + 26
    while y < ground - 14:
        for c in range(cols):
            wx = x + 8 + c * cw + 2
            if r.random() < win_p:
                op = r.uniform(.35, .9)
                s.append(f'<rect x="{wx:.1f}" y="{y:.1f}" width="{cw-4:.1f}" height="7" '
                         f'fill="{WARM}" opacity="{op:.2f}"/>')
            else:
                s.append(f'<rect x="{wx:.1f}" y="{y:.1f}" width="{cw-4:.1f}" height="7" '
                         f'fill="#16304b" opacity=".85"/>')
        s.append(f'<line x1="{x}" y1="{y+10:.1f}" x2="{x+w}" y2="{y+10:.1f}" '
                 f'stroke="#1c3753" stroke-width=".8"/>')
        y += floor_h
    lo = top if lit_from is None else lit_from
    # 상부 워시 + 하부 워시
    if wash and lit_from is None:
        s.append(f'<rect x="{x}" y="{top}" width="{w}" height="{min(140, h*.35):.0f}" '
                 f'fill="url(#washDown)"/>')
    if halo:
        s.append(f'<rect x="{x}" y="{ground-90}" width="{w}" height="90" fill="url(#washUp)"/>')
    # 코너 라인바
    if corner_lit:
        for cx in (x + 2.5, x + w - 2.5):
            s.append(f'<line x1="{cx}" y1="{ground}" x2="{cx}" y2="{lo}" stroke="{GOLD}" '
                     f'stroke-width="2.6" filter="url(#glow)"/>')
            if lit_from is not None:
                s.append(f'<line x1="{cx}" y1="{lo}" x2="{cx}" y2="{top}" stroke="#4d6178" '
                         f'stroke-width="1.6" stroke-dasharray="4 4"/>')
    # 크라운(옥탑) 조명
    if crown:
        cx0, cw0 = x + w * .18, w * .64
        s.append(f'<rect x="{cx0:.1f}" y="{top-34}" width="{cw0:.1f}" height="34" fill="{side_fill}"/>')
        if lit_from is None:
            s.append(f'<rect x="{cx0:.1f}" y="{top-34}" width="{cw0:.1f}" height="34" '
                     f'fill="none" stroke="{GOLD}" stroke-width="2" filter="url(#glow)"/>')
            s.append(f'<line x1="{x}" y1="{top+1}" x2="{x+w}" y2="{top+1}" stroke="{GOLD}" '
                     f'stroke-width="3" filter="url(#glow)"/>')
            for k in range(1, 4):
                lx = cx0 + cw0 * k / 4
                s.append(f'<line x1="{lx:.1f}" y1="{top-34}" x2="{lx:.1f}" y2="{top}" '
                         f'stroke="{GOLD}" stroke-width="1.2" opacity=".75"/>')
        else:
            s.append(f'<rect x="{cx0:.1f}" y="{top-34}" width="{cw0:.1f}" height="34" '
                     f'fill="none" stroke="#4d6178" stroke-width="1.2" stroke-dasharray="4 4"/>')
    return "\n".join(s)


def tree(x, y, rr, lit=True, fill="#0c2033"):
    s = []
    if lit:
        s.append(f'<ellipse cx="{x}" cy="{y}" rx="{rr*1.6:.1f}" ry="{rr*1.4:.1f}" '
                 f'fill="{GOLD}" opacity=".20" filter="url(#soft)"/>')
    for dx, dy, k in ((0, 0, 1), (-rr*.55, rr*.25, .75), (rr*.55, rr*.2, .78), (0, -rr*.45, .7)):
        s.append(f'<circle cx="{x+dx:.1f}" cy="{y+dy:.1f}" r="{rr*k:.1f}" fill="{fill}"/>')
    if lit:
        s.append(f'<ellipse cx="{x}" cy="{y+rr*.35:.1f}" rx="{rr*.8:.1f}" ry="{rr*.6:.1f}" '
                 f'fill="{WARM}" opacity=".16"/>')
    s.append(f'<rect x="{x-1.5:.1f}" y="{y+rr*.7:.1f}" width="3" height="{rr*1.1:.1f}" fill="#081523"/>')
    return "\n".join(s)


def bollard(x, y, h=14):
    return (f'<rect x="{x-1.6}" y="{y-h}" width="3.2" height="{h}" fill="#20354c"/>'
            f'<circle cx="{x}" cy="{y-h}" r="7" fill="url(#bulb)"/>'
            f'<ellipse cx="{x}" cy="{y+1}" rx="10" ry="2.6" fill="{GOLD}" opacity=".22"/>')


def svg(w, h, body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" font-family="{FONT}">\n<defs>{glow_defs(defs)}</defs>\n'
            f'{body}\n</svg>\n')


WASH_DEFS = f"""
  <linearGradient id="washDown" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{GOLD}" stop-opacity=".26"/>
    <stop offset="1" stop-color="{GOLD}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="washUp" x1="0" y1="1" x2="0" y2="0">
    <stop offset="0" stop-color="{WARM}" stop-opacity=".30"/>
    <stop offset="1" stop-color="{WARM}" stop-opacity="0"/>
  </linearGradient>"""


# ---------------------------------------------------------------- 1) 야경
def skyline():
    r = random.Random(7)
    W, H, G = 1600, 900, 700
    defs = WASH_DEFS + f"""
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#071426"/>
    <stop offset=".75" stop-color="#11294a"/>
    <stop offset="1" stop-color="#1b3a5e"/>
  </linearGradient>
  <radialGradient id="cityGlow" cx="55%" cy="100%" r="60%">
    <stop offset="0" stop-color="{GOLD}" stop-opacity=".22"/>
    <stop offset="1" stop-color="{GOLD}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="ground" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#0b1b2e"/>
    <stop offset="1" stop-color="#040b15"/>
  </linearGradient>
  <linearGradient id="pool" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#0f2743"/>
    <stop offset="1" stop-color="#07111f"/>
  </linearGradient>"""
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>',
         f'<rect width="{W}" height="{H}" fill="url(#cityGlow)"/>']
    # 원경 실루엣
    x = -20
    while x < W:
        w = r.randint(60, 120)
        top = r.randint(430, 560)
        b.append(f'<rect x="{x}" y="{top}" width="{w}" height="{G-top}" fill="#0c1c30"/>')
        for _ in range(r.randint(3, 9)):
            b.append(f'<rect x="{x + r.randint(6, w-12)}" y="{r.randint(top+10, G-20)}" '
                     f'width="6" height="4" fill="{WARM}" opacity="{r.uniform(.15, .45):.2f}"/>')
        x += w + r.randint(8, 40)
    # 메인 동
    towers = [(470, 150, 250, 34), (690, 170, 150, 40), (930, 160, 210, 36),
              (1150, 150, 120, 42), (1380, 150, 260, 34), (280, 130, 330, 30)]
    for (tx, tw, top, sd) in sorted(towers, key=lambda t: -t[2]):
        b.append(tower(r, tx, top, tw, G, side=sd))
    # 조경: 지면·수경·나무·볼라드
    b.append(f'<rect x="0" y="{G}" width="{W}" height="{H-G}" fill="url(#ground)"/>')
    b.append(f'<line x1="0" y1="{G}" x2="{W}" y2="{G}" stroke="{GOLD}" stroke-width="1.6" '
             f'opacity=".55" filter="url(#glow)"/>')
    b.append(f'<rect x="220" y="{G+38}" width="1200" height="64" rx="6" fill="url(#pool)"/>')
    for (tx, tw, top, sd) in towers:
        for cx in (tx + 2.5, tx + tw - 2.5):
            b.append(f'<line x1="{cx}" y1="{G+40}" x2="{cx}" y2="{G+98}" stroke="{GOLD}" '
                     f'stroke-width="3" opacity=".28" filter="url(#soft)"/>')
    b.append(f'<line x1="220" y1="{G+38}" x2="1420" y2="{G+38}" stroke="{WARM}" '
             f'stroke-width="2" opacity=".6" filter="url(#glow)"/>')
    for tx in (120, 250, 450, 610, 880, 1080, 1300, 1480):
        b.append(tree(tx, G - 14, r.randint(20, 30)))
    for bx in range(60, W, 90):
        b.append(bollard(bx, G + 150))
    b.append(f'<path d="M0 {G+150} L{W} {G+150}" stroke="{GOLD}" stroke-width="1" opacity=".35"/>')
    return svg(W, H, "\n".join(b), defs)


# ---------------------------------------------------------------- 2) 설계도
def plan():
    r = random.Random(11)
    W, H = 640, 400
    defs = WASH_DEFS + """
  <pattern id="grid" width="16" height="16" patternUnits="userSpaceOnUse">
    <path d="M16 0 L0 0 0 16" fill="none" stroke="#15304c" stroke-width=".6"/>
  </pattern>
  <pattern id="gridL" width="80" height="80" patternUnits="userSpaceOnUse">
    <path d="M80 0 L0 0 0 80" fill="none" stroke="#1d3d5e" stroke-width=".9"/>
  </pattern>"""
    b = ['<rect width="640" height="400" fill="#0a1a2d"/>',
         '<rect width="640" height="400" fill="url(#grid)"/>',
         '<rect width="640" height="400" fill="url(#gridL)"/>']
    # 대지 경계
    b.append(f'<path d="M26 40 L392 30 L404 368 L20 372 Z" fill="#0c2034" fill-opacity=".6" '
             f'stroke="{GOLD_D}" stroke-width="1.2" stroke-dasharray="7 4"/>')
    # 동선(산책로)
    paths = ["M40 300 C120 250 150 330 230 280 S330 190 390 210",
             "M90 60 C110 140 170 150 205 205 S230 330 250 362",
             "M30 170 C120 180 250 120 395 120"]
    for d in paths:
        b.append(f'<path d="{d}" fill="none" stroke="#1d3a58" stroke-width="12" stroke-linecap="round"/>')
        b.append(f'<path d="{d}" fill="none" stroke="#35587a" stroke-width="1" stroke-dasharray="3 5"/>')
    # 광장
    b.append(f'<circle cx="208" cy="208" r="34" fill="#102a44" stroke="#3d5f82" stroke-width="1.2"/>')
    b.append(f'<circle cx="208" cy="208" r="14" fill="none" stroke="{GOLD}" stroke-width="1.4" '
             f'stroke-dasharray="2 3"/>')
    # 동 배치
    blds = [(60, 78, 92, 30, -8, "101"), (250, 58, 96, 30, 6, "102"),
            (292, 250, 88, 30, -14, "103"), (58, 318, 100, 28, 4, "104")]
    for (x, y, w, h, rot, name) in blds:
        cx, cy = x + w / 2, y + h / 2
        b.append(f'<g transform="rotate({rot} {cx} {cy})">'
                 f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#142c46" stroke="#557493" stroke-width="1.2"/>'
                 f'<line x1="{x}" y1="{y}" x2="{x+w}" y2="{y}" stroke="{GOLD}" stroke-width="2" filter="url(#glow)"/>'
                 f'<text x="{cx}" y="{cy+4}" font-size="11" font-weight="700" fill="#9fb3c8" '
                 f'text-anchor="middle">{name}동</text></g>')
    # 수목
    for (tx, ty) in ((170, 100), (340, 170), (150, 250), (330, 330), (110, 210), (260, 150), (360, 80)):
        b.append(f'<circle cx="{tx}" cy="{ty}" r="9" fill="#0f2a40" stroke="#3f6384" stroke-width="1"/>'
                 f'<circle cx="{tx}" cy="{ty}" r="2.2" fill="{GOLD}" filter="url(#glow)"/>')
    # 조명 기구 + 조도 등고선
    fx = [(70, 290), (140, 272), (230, 280), (300, 222), (372, 208), (118, 118), (180, 180),
          (226, 300), (60, 174), (170, 162), (290, 132), (370, 122)]
    for i, (x, y) in enumerate(fx):
        b.append(f'<circle cx="{x}" cy="{y}" r="22" fill="{GOLD}" fill-opacity=".05" '
                 f'stroke="{GOLD}" stroke-opacity=".35" stroke-width=".8" stroke-dasharray="3 3"/>')
        b.append(f'<circle cx="{x}" cy="{y}" r="12" fill="none" stroke="{GOLD}" stroke-opacity=".5" '
                 f'stroke-width=".8"/>')
        b.append(f'<circle cx="{x}" cy="{y}" r="3.4" fill="{WARM}" filter="url(#glow)"/>')
    b.append(f'<text x="96" y="262" font-size="10" fill="{GOLD}" font-weight="600">조도 분포</text>')
    # 방위표·축척
    b.append(f'<g transform="translate(360 56)"><circle r="13" fill="none" stroke="#6f89a3"/>'
             f'<path d="M0 -11 L5 5 L0 1 L-5 5 Z" fill="{GOLD}"/>'
             f'<text y="-17" font-size="9" fill="#9fb3c8" text-anchor="middle">N</text></g>')
    b.append('<g transform="translate(30 388)" font-size="8.5" fill="#8aa0b6">'
             '<rect width="20" height="4" fill="#9fb3c8"/><rect x="20" width="20" height="4" fill="none" stroke="#9fb3c8"/>'
             '<rect x="40" width="20" height="4" fill="#9fb3c8"/><text x="66" y="5">SCALE</text></g>')
    # ---- 입면 패널
    b.append('<rect x="422" y="18" width="200" height="364" rx="4" fill="#0b1d31" stroke="#2a4a6b"/>')
    b.append(f'<text x="436" y="40" font-size="10" letter-spacing="2" fill="{GOLD_D}" font-weight="700">ELEVATION</text>')
    b.append(tower(r, 468, 92, 84, 340, side=0, floor_h=12, win_p=.18, halo=True))
    # 투광 콘
    for cx in (476, 544):
        b.append(f'<polygon points="{cx-4},340 {cx+4},340 {cx+18},250 {cx-18},250" fill="url(#beamUp)" opacity=".7"/>')
    b.append('<line x1="436" y1="340" x2="610" y2="340" stroke="#6f89a3" stroke-width="1"/>')
    # 치수선
    b.append('<g stroke="#8aa0b6" stroke-width=".9"><line x1="580" y1="58" x2="580" y2="340"/>'
             '<line x1="574" y1="58" x2="586" y2="58"/><line x1="574" y1="340" x2="586" y2="340"/></g>')
    # 콜아웃
    callouts = [(552, 70, "크라운 투광"), (552, 180, "코너 라인바"), (548, 318, "지중 업라이트")]
    for (px, py, t) in callouts:
        b.append(f'<circle cx="{px}" cy="{py}" r="2.5" fill="{WARM}"/>'
                 f'<line x1="{px}" y1="{py}" x2="{px+18}" y2="{py-14}" stroke="{GOLD_D}" stroke-width=".9"/>')
        b.append(f'<rect x="{px+14}" y="{py-28}" width="{len(t)*10+12}" height="17" rx="3" '
                 f'fill="#0a1a2d" stroke="{GOLD_D}" stroke-width=".8"/>'
                 f'<text x="{px+20}" y="{py-16}" font-size="10" fill="{WARM}">{t}</text>')
    # 표제란
    b.append(f'<rect x="436" y="352" width="172" height="22" fill="#0a1a2d" stroke="{GOLD_D}" stroke-width=".9"/>'
             f'<text x="444" y="367" font-size="10.5" font-weight="700" fill="{GOLD}">경관조명 설계도</text>'
             f'<text x="600" y="367" font-size="8" fill="#8aa0b6" text-anchor="end">PLAN · ELEV.</text>')
    return svg(W, H, "\n".join(b), defs)


# ---------------------------------------------------------------- 3) 생산
def production():
    W, H = 640, 400
    defs = f"""
  <radialGradient id="studio" cx="50%" cy="38%" r="70%">
    <stop offset="0" stop-color="#1e3a5c"/>
    <stop offset="1" stop-color="#081424"/>
  </radialGradient>
  <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#0f223a"/>
    <stop offset="1" stop-color="#060f1c"/>
  </linearGradient>
  <linearGradient id="metal" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#1a2b3f"/>
    <stop offset=".45" stop-color="#4a6380"/>
    <stop offset="1" stop-color="#16263a"/>
  </linearGradient>
  <linearGradient id="metalV" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#4a6380"/>
    <stop offset="1" stop-color="#1a2b3f"/>
  </linearGradient>
  <linearGradient id="lens" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#FFF6DD"/>
    <stop offset="1" stop-color="{GOLD}"/>
  </linearGradient>
  <linearGradient id="beamR" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{WARM}" stop-opacity=".5"/>
    <stop offset="1" stop-color="{WARM}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="beamUp2" x1="0" y1="1" x2="0" y2="0">
    <stop offset="0" stop-color="{WARM}" stop-opacity=".6"/>
    <stop offset="1" stop-color="{WARM}" stop-opacity="0"/>
  </linearGradient>"""
    b = ['<rect width="640" height="400" fill="url(#studio)"/>',
         '<rect y="282" width="640" height="118" fill="url(#floor)"/>',
         f'<line x1="0" y1="282" x2="640" y2="282" stroke="{GOLD_D}" stroke-opacity=".35"/>']
    # 1) 투광등
    b.append('<g transform="translate(40 150)">'
             '<polygon points="70,40 190,-10 190,120 70,78" fill="url(#beamR)" opacity=".55"/>'
             '<ellipse cx="46" cy="134" rx="46" ry="7" fill="#000" opacity=".45"/>'
             '<path d="M22 68 L22 110 L70 110 L70 68" fill="none" stroke="#5a7390" stroke-width="5"/>'
             '<rect x="40" y="110" width="12" height="22" fill="#2a3e56"/>'
             '<rect x="18" y="126" width="56" height="7" rx="2" fill="#324862"/>'
             '<rect x="6" y="14" width="80" height="62" rx="6" fill="url(#metalV)" stroke="#6d87a4" stroke-width="1"/>'
             + "".join(f'<line x1="{12+k*7}" y1="18" x2="{12+k*7}" y2="72" stroke="#233750" stroke-width="2"/>' for k in range(10))
             + f'<rect x="64" y="20" width="14" height="50" rx="2" fill="url(#lens)" filter="url(#glow)"/>'
             '</g>')
    # 2) 볼라드
    b.append('<g transform="translate(222 120)">'
             f'<ellipse cx="22" cy="164" rx="60" ry="12" fill="{GOLD}" opacity=".22" filter="url(#soft)"/>'
             '<ellipse cx="22" cy="164" rx="26" ry="5" fill="#000" opacity=".5"/>'
             '<rect x="4" y="24" width="36" height="140" fill="url(#metal)"/>'
             '<ellipse cx="22" cy="24" rx="18" ry="5" fill="#5b7594"/>'
             '<rect x="2" y="16" width="40" height="8" rx="2" fill="#3b5270"/>'
             f'<rect x="4" y="34" width="36" height="16" fill="url(#lens)" filter="url(#glow)"/>'
             f'<ellipse cx="22" cy="42" rx="40" ry="18" fill="{WARM}" opacity=".25" filter="url(#soft)"/>'
             '<ellipse cx="22" cy="164" rx="18" ry="4" fill="#2a3d55"/>'
             '</g>')
    # 3) 라인바 (2단)
    for k, (y, rot) in enumerate(((168, -6), (214, -6))):
        b.append(f'<g transform="rotate({rot} 400 {y})">'
                 f'<rect x="318" y="{y}" width="168" height="16" rx="3" fill="url(#metalV)" stroke="#6d87a4" stroke-width=".8"/>'
                 f'<rect x="324" y="{y+10}" width="156" height="5" rx="2" fill="url(#lens)" filter="url(#glow)"/>'
                 f'<rect x="312" y="{y-1}" width="8" height="18" rx="2" fill="#2a3e56"/>'
                 f'<rect x="484" y="{y-1}" width="8" height="18" rx="2" fill="#2a3e56"/>'
                 f'<ellipse cx="402" cy="{y+22}" rx="90" ry="10" fill="{WARM}" opacity=".18" filter="url(#soft)"/>'
                 '</g>')
    b.append('<ellipse cx="402" cy="282" rx="80" ry="7" fill="#000" opacity=".35"/>')
    b.append('<path d="M360 270 L372 238 M440 270 L428 232" stroke="#4a6380" stroke-width="4"/>')
    # 4) 지중 업라이트
    b.append('<g transform="translate(560 262)">'
             '<polygon points="-16,10 16,10 44,-230 -44,-230" fill="url(#beamUp2)"/>'
             '<ellipse cx="0" cy="12" rx="40" ry="11" fill="#0a1626" stroke="#6d87a4" stroke-width="1.6"/>'
             '<ellipse cx="0" cy="11" rx="30" ry="8" fill="#23384f"/>'
             f'<ellipse cx="0" cy="10" rx="19" ry="5" fill="url(#lens)" filter="url(#glow)"/>'
             '</g>')
    # 라벨
    labels = [(86, "투광등", "FLOOD"), (244, "볼라드", "BOLLARD"), (402, "라인바", "LINEAR"), (560, "지중 업라이트", "IN-GROUND")]
    for (x, ko, en) in labels:
        b.append(f'<text x="{x}" y="326" font-size="15" font-weight="700" fill="#EAF0F6" text-anchor="middle">{ko}</text>'
                 f'<text x="{x}" y="344" font-size="9" letter-spacing="2.4" fill="{GOLD_D}" text-anchor="middle">{en}</text>')
    # 상단 태그
    b.append(f'<rect x="20" y="20" width="148" height="26" rx="13" fill="none" stroke="{GOLD_D}"/>'
             f'<text x="94" y="38" font-size="12" font-weight="700" fill="{GOLD}" text-anchor="middle">단지 사양 맞춤 제작</text>')
    b.append(f'<rect x="508" y="20" width="112" height="26" rx="13" fill="{GOLD}"/>'
             f'<text x="564" y="38" font-size="12" font-weight="800" fill="#0a1a2d" text-anchor="middle">KC 인증 제품</text>')
    b.append('<text x="320" y="380" font-size="9.5" letter-spacing="3" fill="#6f89a3" text-anchor="middle">'
             'IMPORT · PRODUCTION · QC</text>')
    return svg(W, H, "\n".join(b), defs)


# ---------------------------------------------------------------- 4) 시공
def install():
    r = random.Random(5)
    W, H, G = 640, 400, 322
    defs = WASH_DEFS + f"""
  <linearGradient id="sky2" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#081629"/>
    <stop offset="1" stop-color="#16345a"/>
  </linearGradient>
  <linearGradient id="gnd2" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#0c1c30"/>
    <stop offset="1" stop-color="#050c17"/>
  </linearGradient>
  <linearGradient id="boom" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#F2C46B"/>
    <stop offset="1" stop-color="#B9852F"/>
  </linearGradient>"""
    b = ['<rect width="640" height="400" fill="url(#sky2)"/>']
    # 원경
    for (x, w, t) in ((0, 70, 210), (78, 60, 236), (150, 80, 196), (250, 50, 250)):
        b.append(f'<rect x="{x}" y="{t}" width="{w}" height="{G-t}" fill="#0d1f35"/>')
        for _ in range(6):
            b.append(f'<rect x="{x+r.randint(6, w-10)}" y="{r.randint(t+8, G-12)}" width="5" height="3" '
                     f'fill="{WARM}" opacity="{r.uniform(.2, .5):.2f}"/>')
    # 시공 중인 동 (하부 점등 완료 / 상부 시공 중)
    b.append(tower(r, 372, 44, 190, G, side=44, lit_from=128, win_p=.22, floor_h=13))
    b.append(f'<line x1="372" y1="{G}" x2="562" y2="{G}" stroke="{GOLD}" stroke-width="2" filter="url(#glow)"/>')
    # 진행 표시
    b.append(f'<g font-size="10.5" font-weight="700">'
             f'<rect x="572" y="70" width="58" height="20" rx="10" fill="#0a1a2d" stroke="#6f89a3"/>'
             f'<text x="601" y="84" fill="#b8c6d4" text-anchor="middle">시공 중</text>'
             f'<rect x="572" y="210" width="58" height="20" rx="10" fill="{GOLD}"/>'
             f'<text x="601" y="224" fill="#0a1a2d" text-anchor="middle">점등 완료</text></g>')
    # 지면
    b.append(f'<rect y="{G}" width="640" height="{H-G}" fill="url(#gnd2)"/>')
    # 고소작업차
    b.append('<g>'
             f'<rect x="96" y="{G-40}" width="132" height="30" rx="4" fill="#2b4058" stroke="#5d7896"/>'
             f'<rect x="200" y="{G-58}" width="38" height="48" rx="5" fill="#34506e" stroke="#5d7896"/>'
             f'<rect x="208" y="{G-52}" width="22" height="16" rx="2" fill="#9ec3e6" opacity=".55"/>'
             f'<circle cx="126" cy="{G-8}" r="11" fill="#0b1522" stroke="#5d7896" stroke-width="3"/>'
             f'<circle cx="212" cy="{G-8}" r="11" fill="#0b1522" stroke="#5d7896" stroke-width="3"/>'
             f'<rect x="90" y="{G-14}" width="8" height="14" fill="#5d7896"/>'
             f'<rect x="84" y="{G-2}" width="20" height="4" fill="#5d7896"/>'
             f'<rect x="138" y="{G-56}" width="30" height="18" rx="3" fill="#3f5b7a"/>'
             '</g>')
    # 붐
    bx0, by0, bx1, by1 = 152, G - 50, 338, 136
    b.append(f'<line x1="{bx0}" y1="{by0}" x2="{bx1}" y2="{by1}" stroke="url(#boom)" stroke-width="13" stroke-linecap="round"/>'
             f'<line x1="{bx0}" y1="{by0}" x2="{(bx0+bx1)/2}" y2="{(by0+by1)/2}" stroke="#A8762A" stroke-width="17" stroke-linecap="round"/>'
             f'<line x1="{bx0+6}" y1="{by0-4}" x2="{bx1}" y2="{by1-4}" stroke="#FFE3AA" stroke-width="1.2" opacity=".6"/>')
    # 바스켓 + 작업자
    b.append(f'<g>'
             f'<rect x="316" y="124" width="46" height="24" rx="2" fill="#2b4058" stroke="{AMBER}" stroke-width="2"/>'
             f'<line x1="316" y1="110" x2="362" y2="110" stroke="{AMBER}" stroke-width="2.4"/>'
             f'<line x1="318" y1="110" x2="318" y2="124" stroke="{AMBER}" stroke-width="2"/>'
             f'<line x1="360" y1="110" x2="360" y2="124" stroke="{AMBER}" stroke-width="2"/>'
             # 몸
             f'<rect x="332" y="96" width="14" height="28" rx="5" fill="#1a2c42"/>'
             f'<rect x="332" y="100" width="14" height="4" fill="{GOLD}" opacity=".9"/>'
             f'<circle cx="339" cy="88" r="6.5" fill="#c9a37b"/>'
             f'<path d="M331.5 87 A7.5 7.5 0 0 1 346.5 87 Z" fill="{GOLD}"/>'
             f'<rect x="330" y="86" width="18" height="2.4" rx="1" fill="{AMBER}"/>'
             # 팔 → 파사드
             f'<path d="M344 102 L358 100 L368 104" fill="none" stroke="#1a2c42" stroke-width="4.5" stroke-linecap="round"/>'
             f'<rect x="366" y="97" width="8" height="18" rx="1.5" fill="#6d87a4"/>'
             f'<circle cx="372" cy="118" r="16" fill="url(#bulb)"/>'
             f'</g>')
    # 케이블
    b.append(f'<path d="M160 {G-40} C220 {G+18} 300 {G+22} 372 {G+6}" fill="none" stroke="{GOLD_D}" '
             f'stroke-width="1.6" stroke-dasharray="5 4"/>')
    # 라바콘
    for cx in (60, 262, 300):
        b.append(f'<polygon points="{cx-8},{G+10} {cx+8},{G+10} {cx},{G-12}" fill="{AMBER}"/>'
                 f'<rect x="{cx-5}" y="{G-2}" width="10" height="3" fill="#fff" opacity=".8"/>')
    # 볼라드·조경
    for bx in (30, 330, 420, 490, 560, 620):
        b.append(bollard(bx, G + 50))
    b.append(tree(40, G - 20, 18))
    b.append(f'<line x1="0" y1="{G+50}" x2="640" y2="{G+50}" stroke="{GOLD}" stroke-width=".8" opacity=".3"/>')
    return svg(W, H, "\n".join(b), defs)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("경관조명_야경.svg", skyline), ("경관조명_1_설계.svg", plan),
                     ("경관조명_2_생산.svg", production), ("경관조명_3_시공.svg", install)):
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(fn())
        print("saved", name)
