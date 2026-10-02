# -*- coding: utf-8 -*-
"""동탄 파라곤3차 표지 일러스트(SVG) — 신리천 변 20층 판상형 단지의 경관조명 야경.

공고·분양 자료 기준 특징만 반영한 '연출 일러스트'(실사·조감도 아님):
- 18개동 · 지상 최고 20층 판상형 → 높이가 고른 중층 스카이라인, 2열 배치
- 단지 앞 신리천 수변 → 물 반사, 산책로 볼라드·가로수
- 원경: 동탄2 신도시 고층 스카이라인(실루엣)
요약제안서 make_images.py 의 동(tower)·나무·볼라드 그리기 함수를 그대로 쓴다.

실행: python make_cover.py   → assets_dt/동탄_파라곤3차_야경.svg
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "요약제안서"))
from make_images import GOLD, WARM, WASH_DEFS, bollard, svg, tower, tree  # noqa: E402

OUT = os.path.join(HERE, "assets_dt", "동탄_파라곤3차_야경.svg")


def cover():
    r = random.Random(58)  # A58BL
    W, H, G = 1100, 1240, 900          # G: 동이 서는 지면
    WT, WB = G + 34, H                 # 신리천 수면
    defs = WASH_DEFS + f"""
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#050f1f"/>
    <stop offset=".62" stop-color="#0d2443"/>
    <stop offset="1" stop-color="#1d3d63"/>
  </linearGradient>
  <radialGradient id="cityGlow" cx="62%" cy="74%" r="55%">
    <stop offset="0" stop-color="{GOLD}" stop-opacity=".26"/>
    <stop offset="1" stop-color="{GOLD}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="moonGlow" cx="50%" cy="50%" r="50%">
    <stop offset="0" stop-color="#FFF4D6" stop-opacity=".55"/>
    <stop offset="1" stop-color="#FFF4D6" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="water" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#10294a"/>
    <stop offset="1" stop-color="#040a14"/>
  </linearGradient>
  <linearGradient id="reflFade" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity=".55"/>
    <stop offset=".7" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <mask id="reflMask"><rect x="0" y="{WT}" width="{W}" height="{WB - WT}" fill="url(#reflFade)"/></mask>
  <filter id="ripple" x="-5%" y="-5%" width="110%" height="110%">
    <feTurbulence type="fractalNoise" baseFrequency="0.004 0.09" numOctaves="2" seed="7" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="16" xChannelSelector="R" yChannelSelector="G" result="d"/>
    <feGaussianBlur in="d" stdDeviation="1.6"/>
  </filter>"""
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>',
         f'<rect width="{W}" height="{H}" fill="url(#cityGlow)"/>']
    # 별·초승달(마스크로 오려 냄)
    for _ in range(70):
        b.append(f'<circle cx="{r.uniform(0, W):.0f}" cy="{r.uniform(10, 380):.0f}" r="{r.uniform(.6, 1.6):.1f}" '
                 f'fill="#DDE6F2" opacity="{r.uniform(.15, .6):.2f}"/>')
    b.append('<mask id="cres"><circle cx="640" cy="250" r="30" fill="#fff"/><circle cx="656" cy="240" r="27" fill="#000"/></mask>')
    b.append('<circle cx="640" cy="250" r="80" fill="url(#moonGlow)" opacity=".7"/>')
    b.append('<circle cx="640" cy="250" r="30" fill="#F6E7C4" mask="url(#cres)"/>')
    # 원경: 동탄2 고층 스카이라인(실루엣)
    x = -10
    while x < W:
        w = r.randint(34, 70)
        top = r.randint(200, 430)
        b.append(f'<rect x="{x}" y="{top}" width="{w}" height="{G - top}" fill="#132b49" opacity=".85"/>')
        for _ in range(r.randint(4, 12)):
            b.append(f'<rect x="{x + r.randint(4, w - 8)}" y="{r.randint(top + 8, G - 120)}" width="4" height="3" '
                     f'fill="{WARM}" opacity="{r.uniform(.12, .38):.2f}"/>')
        b.append(f'<circle cx="{x + w / 2:.0f}" cy="{top - 4}" r="1.8" fill="#ff6b5b" opacity=".7"/>')
        x += w + r.randint(10, 46)
    # 단지(20층 판상형 2열). 살짝 높은 시점 → 뒷열은 지면이 더 위에 보이고, 앞열 사이·위로 드러난다.
    GB = G - 112
    back = [(-70, 170, 18), (185, 170, 20), (455, 170, 17), (725, 170, 20), (990, 170, 19)]  # (x, 폭, 층수)
    front = [(28, 205, 16), (298, 205, 20), (568, 205, 18), (838, 205, 15)]
    blocks = []
    for (tx, tw, fl) in back:
        blocks.append(tower(r, tx, GB - 26 - fl * 14, tw, GB, side=18, win_p=.22, floor_h=14,
                            facade="#0d2036", side_fill="#091729", halo=False))
    blocks.append(f'<rect x="0" y="200" width="{W}" height="{GB - 200}" fill="#0b1d35" opacity=".22"/>')  # 원근 헤이즈
    blocks.append(f'<rect x="0" y="{GB}" width="{W}" height="{G - GB}" fill="#0a1a2d"/>')
    for tx in range(-10, W, 64):
        blocks.append(tree(tx + r.randint(-8, 8), GB + 10, r.randint(12, 17)))
    for (tx, tw, fl) in front:
        blocks.append(tower(r, tx, G - 26 - fl * 19, tw, G, side=30, win_p=.32, floor_h=19))
    b.append(f'<g id="complex">{"".join(blocks)}</g>')
    # 지면·조경
    b.append(f'<rect x="0" y="{G}" width="{W}" height="{WT - G}" fill="#081627"/>')
    b.append(f'<line x1="0" y1="{G}" x2="{W}" y2="{G}" stroke="{GOLD}" stroke-width="1.6" opacity=".6" filter="url(#glow)"/>')
    for tx in (14, 120, 255, 392, 525, 660, 795, 930, 1075):
        b.append(tree(tx, G - 12, r.randint(18, 26)))
    # 신리천: 수면 + 단지 반사 + 물결
    b.append(f'<rect x="0" y="{WT}" width="{W}" height="{WB - WT}" fill="url(#water)"/>')
    b.append(f'<g mask="url(#reflMask)"><use href="#complex" transform="translate(0 {2 * WT}) scale(1 -1)" '
             f'filter="url(#ripple)" opacity=".85"/></g>')
    for _ in range(140):
        y = r.uniform(WT + 6, WB - 20)
        x0 = r.uniform(0, W)
        b.append(f'<line x1="{x0:.0f}" y1="{y:.0f}" x2="{x0 + r.uniform(14, 70):.0f}" y2="{y:.0f}" stroke="{WARM}" '
                 f'stroke-width="1.2" opacity="{r.uniform(.05, .22):.2f}"/>')
    # 수변 산책로 볼라드
    b.append(f'<line x1="0" y1="{WT}" x2="{W}" y2="{WT}" stroke="{WARM}" stroke-width="2" opacity=".55" filter="url(#glow)"/>')
    for bx in range(30, W, 78):
        b.append(bollard(bx, WT - 2, h=12))
    return svg(W, H, "\n".join(b), defs)


if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(cover())
    print("saved", OUT, os.path.getsize(OUT) // 1024, "KB")
