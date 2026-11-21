"""영주자이 시그니처 정문 문주 — 도면 치수 기반 야간 입면 시뮬레이션(엣지컴퍼니 안).

※ 이 스크립트는 1차 「눈 내리는 문주」(은하수안) 그림이다. 2026-11-21 회장이 「겨울 게이트」안으로 확정해
  은하수안 그림은 시뮬레이션\\_이전버전\\으로 옮겼다. 겨울 게이트 연출 이미지는 회장 ChatGPT 완성본을 쓴다.

근거 도면: 주문주 및 경비실#1 A-861·A-862 (세림건축, 2023.11, 1/150)
  전체 길이 약 28.6m(450+28,175) · 높이 6.85m · 상부 띠 0.97m
  좌측 석재벽(X1~X2, 약 5.0m) · 차량 통과부(17.55m) · 우측 경비실(유리·SUS 스크린·석재)
1 SVG 단위 = 10mm.  실행: python 경관조명/tools/yeongju_sim.py
"""
from __future__ import annotations

import math
import random
import subprocess
from pathlib import Path

OUT = Path.home() / "Desktop" / "경관조명 관련" / "영주자이 자료" / "시뮬레이션"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
W, H = 3300, 1250
X0, GY = 220, 1010            # 문주 왼쪽 끝 x, 지면 y
L = 2862.5                    # 28.625m
TOP, BAND = 685, 97           # 높이 6.85m, 상부 띠 0.97m
YT, YB = GY - TOP, GY - TOP + BAND   # 띠 위·아래 y
WALL_R = X0 + 500             # 좌측 석재벽 끝 (5.0m)
GUARD_L = X0 + 2255           # 경비실 시작
random.seed(7)


def snowflake(cx, cy, r, color, sw):
    g = [f'<g stroke="{color}" stroke-width="{sw}" stroke-linecap="round" fill="none" filter="url(#glow)">']
    for k in range(6):
        a = math.radians(60 * k - 90)
        x2, y2 = cx + r * math.cos(a), cy + r * math.sin(a)
        g.append(f'<line x1="{cx}" y1="{cy}" x2="{x2:.1f}" y2="{y2:.1f}"/>')
        for t in (0.45, 0.72):
            bx, by = cx + r * t * math.cos(a), cy + r * t * math.sin(a)
            for s in (-1, 1):
                b = a + s * math.radians(42)
                g.append(f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{bx + r * 0.25 * math.cos(b):.1f}" y2="{by + r * 0.25 * math.sin(b):.1f}"/>')
    g.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.1:.1f}"/></g>')
    return "".join(g)


def star(cx, cy, r, color):
    pts = []
    for k in range(10):
        rr = r if k % 2 == 0 else r * 0.42
        a = math.radians(-90 + 36 * k)
        pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="5" stroke-linejoin="round" filter="url(#glow)"/>'


def build_svg() -> str:
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
         """<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a1430"/><stop offset="1" stop-color="#1f2d4d"/></linearGradient>
  <linearGradient id="glass" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3d6b7a"/><stop offset="1" stop-color="#9fd3d6"/></linearGradient>
  <linearGradient id="fall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity="0.05"/><stop offset="0.8" stop-color="#ffffff"/><stop offset="1" stop-color="#ffffff" stop-opacity="0.2"/></linearGradient>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="haze" x="-20%" y="-200%" width="140%" height="500%"><feGaussianBlur stdDeviation="22"/></filter>
</defs>""",
         f'<rect width="{W}" height="{H}" fill="url(#sky)"/>']
    # 배경 아파트 실루엣(일반화된 표현)
    for bx, bw, bh in [(120, 420, 900), (700, 360, 980), (1250, 400, 860), (1850, 380, 1000), (2450, 420, 920), (2980, 300, 880)]:
        s.append(f'<rect x="{bx}" y="{GY - bh}" width="{bw}" height="{bh}" fill="#18233b"/>')
        for wy in range(max(GY - bh + 40, 190), GY - 260, 58):
            for wx in range(bx + 30, bx + bw - 40, 62):
                if random.random() < 0.38:
                    s.append(f'<rect x="{wx}" y="{wy}" width="30" height="24" fill="#f7d28c" opacity="{random.uniform(0.35, 0.8):.2f}"/>')
    # 지면
    s.append(f'<rect x="0" y="{GY}" width="{W}" height="{H - GY}" fill="#2a2d33"/>')
    s.append(f'<rect x="0" y="{GY}" width="{W}" height="6" fill="#4a4e57"/>')
    # 좌측 석재벽 (X1~X2)
    s.append(f'<rect x="{X0}" y="{YB}" width="{WALL_R - X0}" height="{GY - YB}" fill="#5f5c58"/>')
    for gx in range(X0, WALL_R, 125):
        s.append(f'<line x1="{gx}" y1="{YB}" x2="{gx}" y2="{GY}" stroke="#4d4a47" stroke-width="2"/>')
    for gy in range(YB, GY, 97):
        s.append(f'<line x1="{X0}" y1="{gy}" x2="{WALL_R}" y2="{gy}" stroke="#4d4a47" stroke-width="2"/>')
    # 로고 사인 자리(기존 유지) — 실제 로고는 그리지 않음
    s.append(f'<rect x="{X0 + 160}" y="{GY - 330}" width="190" height="70" fill="none" stroke="#c9b58a" stroke-width="2" stroke-dasharray="8 6"/>')
    s.append(f'<text x="{X0 + 255}" y="{GY - 287}" fill="#c9b58a" font-size="22" text-anchor="middle" font-family="Malgun Gothic">로고 사인(기존)</text>')
    # 차량 통과부 안쪽(어둡게) + 바닥 조명 반사
    s.append(f'<rect x="{WALL_R}" y="{YB}" width="{GUARD_L - WALL_R}" height="{GY - YB}" fill="#101a2e" opacity="0.55"/>')
    # 우측 경비실: 유리 · SUS 스크린 · 석재
    s.append(f'<rect x="{GUARD_L}" y="{YB}" width="275" height="{GY - YB}" fill="url(#glass)"/>')
    for gx in range(GUARD_L, GUARD_L + 275, 55):
        s.append(f'<line x1="{gx}" y1="{YB}" x2="{gx}" y2="{GY}" stroke="#2c4b55" stroke-width="3"/>')
    sx = GUARD_L + 275
    s.append(f'<rect x="{sx}" y="{YB}" width="230" height="{GY - YB}" fill="#3a2f24"/>')
    for gx in range(sx + 8, sx + 230, 33):
        s.append(f'<rect x="{gx}" y="{YB}" width="15" height="{GY - YB}" fill="#8a6a45"/>')
    s.append(f'<rect x="{sx + 230}" y="{YB}" width="{X0 + L - sx - 230}" height="{GY - YB}" fill="#5f5c58"/>')
    # 상부 띠(구조) + 은하수 망: 전구색 촘촘 + 백색 트윙클
    s.append(f'<rect x="{X0}" y="{YT}" width="{L}" height="{BAND}" fill="#3b3833"/>')
    s.append(f'<rect x="{X0}" y="{YT - 10}" width="{L}" height="{BAND + 20}" fill="#ffcf7a" opacity="0.35" filter="url(#haze)"/>')
    dots = []
    for yy in range(YT + 5, YB - 2, 10):
        off = 5 if (yy // 10) % 2 else 0
        for xx in range(X0 + 4 + off, int(X0 + L) - 2, 10):
            dots.append(f'<circle cx="{xx}" cy="{yy}" r="2.3"/>')
    s.append(f'<g fill="#ffd690" filter="url(#glow)">{"".join(dots)}</g>')
    tw = [f'<circle cx="{random.uniform(X0, X0 + L):.0f}" cy="{random.uniform(YT + 3, YB - 3):.0f}" r="{random.uniform(2.6, 4.2):.1f}"/>' for _ in range(420)]
    s.append(f'<g fill="#ffffff" filter="url(#glow)">{"".join(tw)}</g>')
    # 고드름 라이트: 띠 하단 전체, 0.3~0.6m 드롭
    ic = []
    for xx in range(int(X0) + 6, int(X0 + L), 14):
        drop = random.choice([30, 38, 45, 52, 60])
        for yy in range(YB + 6, YB + drop, 7):
            ic.append(f'<circle cx="{xx}" cy="{yy}" r="1.8"/>')
    s.append(f'<g fill="#eaf6ff" filter="url(#glow)">{"".join(ic)}</g>')
    # 스노우폴 1000mm × 24본: 차량 통과부 상부에 매달림
    for k in range(24):
        xx = WALL_R + 80 + k * ((GUARD_L - WALL_R - 160) / 23)
        top = YB + 70
        s.append(f'<line x1="{xx:.0f}" y1="{YB}" x2="{xx:.0f}" y2="{top}" stroke="#6b7280" stroke-width="1.5"/>')
        s.append(f'<rect x="{xx - 3:.0f}" y="{top}" width="6" height="100" rx="3" fill="url(#fall)" filter="url(#glow)"/>')
    # 좌측 석재벽 모티브: 눈꽃 대(900) 전구색 · 눈꽃 중(600) 백색 2 · 별(450) 전구색 2 — 로고 자리는 비움
    s.append(snowflake(X0 + 150, YB + 150, 45, "#ffd690", 6))
    s.append(snowflake(X0 + 395, YB + 115, 30, "#f4fbff", 5))
    s.append(snowflake(X0 + 90, GY - 170, 30, "#f4fbff", 5))
    s.append(star(X0 + 330, YB + 250, 22, "#ffd690"))
    s.append(star(X0 + 430, GY - 150, 22, "#ffd690"))
    # 치수선
    s.append(f'<line x1="{X0}" y1="{GY + 70}" x2="{X0 + L}" y2="{GY + 70}" stroke="#9aa3b2" stroke-width="2"/>')
    for xx in (X0, X0 + L):
        s.append(f'<line x1="{xx}" y1="{GY + 55}" x2="{xx}" y2="{GY + 85}" stroke="#9aa3b2" stroke-width="2"/>')
    s.append(f'<text x="{X0 + L / 2}" y="{GY + 110}" fill="#c7cdd6" font-size="30" text-anchor="middle" font-family="Malgun Gothic">약 28.6m (도면 A-861 기준)</text>')
    s.append(f'<line x1="{X0 + L + 50}" y1="{YT}" x2="{X0 + L + 50}" y2="{GY}" stroke="#9aa3b2" stroke-width="2"/>')
    s.append(f'<text x="{X0 + L + 70}" y="{(YT + GY) / 2}" fill="#c7cdd6" font-size="30" font-family="Malgun Gothic">6.85m</text>')
    # 제목·범례
    s.append('<text x="60" y="80" fill="#ffffff" font-size="46" font-weight="700" font-family="Malgun Gothic">영주자이 시그니처 정문 문주 — 윈터라이팅 야간 입면 (엣지컴퍼니 안)</text>')
    s.append('<text x="60" y="128" fill="#c7cdd6" font-size="27" font-family="Malgun Gothic">컨셉 「눈 내리는 문주」 · 상부 띠 전구색 은하수 + 백색 트윙클 · 하단 고드름 · 통과부 스노우폴 · 석재벽 눈꽃·별 (로고 사인 유지)</text>')
    legend = [("#ffd690", "은하수 전구색 · 상부 띠 전면·양측면 420m"), ("#ffffff", "백색 트윙클 혼합"),
              ("#eaf6ff", "고드름 라이트 40m (드롭 0.3~0.6m)"), ("#ffffff", "스노우폴 1000mm 3세트(24본)"),
              ("#ffd690", "눈꽃 900 ×1 · 별 450 ×2 (전구색)"), ("#f4fbff", "눈꽃 600 ×2 (백색)")]
    for i, (c, t) in enumerate(legend):
        lx, ly = 60 + (i % 3) * 1000, H - 70 + (i // 3) * 40 - 20
        s.append(f'<circle cx="{lx}" cy="{ly - 9}" r="9" fill="{c}" filter="url(#glow)"/>')
        s.append(f'<text x="{lx + 22}" y="{ly}" fill="#dfe4ea" font-size="25" font-family="Malgun Gothic">{t}</text>')
    s.append(f'<text x="{W - 60}" y="{GY + 110}" fill="#8b94a3" font-size="22" text-anchor="end" font-family="Malgun Gothic">※ 도면 치수 기반 연출도이며 현장 설치 시 차이가 있을 수 있습니다</text>')
    s.append("</svg>")
    return "\n".join(s)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    svg = build_svg()
    hp = OUT / "문주_야간입면_엣지안.html"
    hp.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;background:#0a1430}}</style></head><body>{svg}</body></html>', encoding="utf-8")
    png = OUT / "문주_야간입면_엣지안.png"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={W},{H}",
                    f"--screenshot={png}", hp.as_uri()], check=True, capture_output=True, timeout=120)
    print("OK ->", png)


if __name__ == "__main__":
    main()
