#!/usr/bin/env python3
"""아크로 슬림 섹션 이미지들을 하나의 긴 상세페이지 PNG로 세로 조립."""
from PIL import Image
from pathlib import Path

SRC = Path(r"C:\Users\win11\Desktop\아크로 사진")
OUT = Path(r"C:\Users\win11\Downloads\에어전트 팀\edge-company-claude-friendly-thompson-NDkKH\design-division\output\슬림아크로\arco_slim_detail.png")

# 아크로 슬림 상세페이지 순서 (14.5cm 일관 · 프리미엄)
SECTIONS = [
    "ChatGPT Image 2026년 5월 26일 오전 10_57_54.png",   # 브랜드 히어로 (Acro Simple but Elegant)
    "ChatGPT Image 2026년 5월 25일 오전 11_35_50.png",   # NEW SLIM 히어로 (14.5cm, 159,000원)
    "ChatGPT Image 2026년 5월 25일 오전 11_44_13.png",   # SLIM BODY 14.5cm
    "ChatGPT Image 2026년 6월 5일 오후 05_00_37.png",     # 스마트한 바람 (앱/제어)
]

WIDTH = 1080
BG = (255, 255, 255)

imgs = []
for name in SECTIONS:
    p = SRC / name
    if not p.exists():
        print("MISSING:", name); continue
    im = Image.open(p).convert("RGB")
    w, h = im.size
    nh = round(h * WIDTH / w)
    imgs.append(im.resize((WIDTH, nh), Image.LANCZOS))
    print(f"  + {name}  ({w}x{h} -> {WIDTH}x{nh})")

total_h = sum(im.height for im in imgs)
canvas = Image.new("RGB", (WIDTH, total_h), BG)
y = 0
for im in imgs:
    canvas.paste(im, (0, y)); y += im.height

OUT.parent.mkdir(parents=True, exist_ok=True)
canvas.save(OUT, "PNG")
print(f"\nDONE -> {OUT}  ({WIDTH}x{total_h}, {OUT.stat().st_size//1024}KB)")
