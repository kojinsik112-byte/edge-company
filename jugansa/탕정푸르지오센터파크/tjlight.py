# -*- coding: utf-8 -*-
"""탕정 v2 밝은 바탕 시안(10-21 본부장 요청) — v2 HTML의 색만 바꿔 _v2_밝은시안.html/pdf로 낸다(내용 · 순서는 v2 그대로).

본문 쪽 = 아이보리 종이 + 네이비 글자 + 짙은 골드 강조. 표지 · 간지 · 전면 사진 쪽 · 연락처 = 네이비 그대로(사진이 네이비로 스며들게 만든 쪽).
사용: python3 tjlight.py  (먼저 build_tangjeong.py --v2 로 v2 HTML을 만든다)
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "엣지컴퍼니_탕정푸르지오센터파크_05_입주박람회_입찰제안서_v2.html")
OUT = os.path.join(HERE, "엣지컴퍼니_탕정푸르지오센터파크_05_입주박람회_입찰제안서_v2_밝은시안.html")

DARK = "--bg:#0D1E33;--gold:#EBCB8F;--gold2:#C8A86A;--ink:#F4F6F9;--sub:#B4BECA;--mute:#8595A8;--line:rgba(255,255,255,.13)"
LIGHT = "--bg:#FAF7F0;--gold:#8A6420;--gold2:#A47A33;--ink:#14243A;--sub:#3B4A5D;--mute:#6A7686;--line:rgba(13,30,51,.14)"
DARK_PAGES = ".page.cv,.page.dv"

OVR = f"""
:root{{{LIGHT}}}
{DARK_PAGES}{{{DARK};color:var(--ink)}}
.page:not(.cv):not(.dv){{background:var(--bg)!important;color:var(--ink)}}
.page .hd{{border-bottom-color:rgba(13,30,51,.14)}}
.sheet{{border:1px solid #d9ccb2;box-shadow:0 6px 18px rgba(13,30,51,.12)!important}}
.kp{{{DARK};background:#0D1E33!important;color:var(--ink);border-color:transparent!important}}
.todo{{background:#FFE066;color:#0D1E33}}
"""


def light_css(css):
    # 반투명 흰 덧칠(카드 · 선 · 바탕) → 반투명 네이비. 투명도는 조금 낮춘다(밝은 바탕에서 네이비가 더 진하게 보임)
    # 단, 글자색(color:)은 사진 위 캡션이라 흰색 그대로 둔다
    def decl(m):
        if m.group(1).strip().lower() == "color":
            return m.group(0)
        return m.group(1) + ":" + re.sub(r"rgba\(255,\s*255,\s*255,\s*([.\d]+)\)", lambda n: f"rgba(13,30,51,{min(1, float(n.group(1)) * .8):.3f})", m.group(2))
    css = re.sub(r"([\w-]+)\s*:\s*([^;{}]*)", decl, css)
    # 어두운 판(콜센터 원 · 띠 · 표 머리)의 고정 남색 바탕 → 흰 판
    for a in ("#0f2237", "#0a1626", "#0b1a2d", "#2f4a6b"):
        css = re.sub(rf"background(-color)?:\s*{a}", r"background\1:#FFFFFF", css, flags=re.I)
    # 밝은 글자색 고정값 → 토큰
    for a, b in [("#D5DCE4", "var(--sub)"), ("#DCE3EB", "var(--sub)"), ("#9fd3c7", "#1f7a68")]:
        css = re.sub(rf"color:\s*{a}", f"color:{b}", css, flags=re.I)
    return css


def main():
    doc = open(SRC, encoding="utf-8").read()
    head, rest = doc.split("</head>", 1)
    head = re.sub(r"<style>(.*?)</style>", lambda m: "<style>" + light_css(m.group(1)) + "</style>", head, flags=re.S)
    head = head.replace("</style>", OVR + "</style>", 1) if head.count("</style>") == 1 else head + f"<style>{OVR}</style>"
    rest = re.sub(r"<style>(.*?)</style>", lambda m: "<style>" + light_css(m.group(1)) + "</style>", rest, flags=re.S)
    rest = re.sub(r'style="([^"]*)"', lambda m: 'style="' + light_css(m.group(1)) + '"', rest)
    open(OUT, "w", encoding="utf-8").write(head + "</head>" + rest)
    print("HTML:", OUT)
    if "--no-pdf" not in sys.argv:
        sys.path.insert(0, os.path.join(HERE, "..", "요약제안서"))
        import build as B
        B.OUT_HTML, B.OUT_PDF = OUT, OUT[:-5] + ".pdf"
        B.build_pdf()


if __name__ == "__main__":
    main()
