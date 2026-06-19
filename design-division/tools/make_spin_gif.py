#!/usr/bin/env python3
"""이미지를 중심 회전시켜 무한 루프 스핀 GIF 생성 (무료).
사용: make_spin_gif.py <src.png> <out.gif> [총각도=120] [프레임=18] [duration=55] [size=460]
"""
import sys
from PIL import Image
from pathlib import Path

src = Path(sys.argv[1])
out = Path(sys.argv[2])
total = float(sys.argv[3]) if len(sys.argv) > 3 else 120.0
N = int(sys.argv[4]) if len(sys.argv) > 4 else 18
dur = int(sys.argv[5]) if len(sys.argv) > 5 else 55
SIZE = int(sys.argv[6]) if len(sys.argv) > 6 else 460

im = Image.open(src).convert("RGB")
w, h = im.size
s = min(w, h)
im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))
bg = im.getpixel((4, 4))
cx, cy = im.size[0] / 2, im.size[1] / 2

frames = []
for i in range(N):
    a = i * (total / N)
    fr = im.rotate(-a, resample=Image.BICUBIC, center=(cx, cy), fillcolor=bg)
    fr = fr.resize((SIZE, SIZE), Image.LANCZOS).convert("P", palette=Image.ADAPTIVE, colors=64)
    frames.append(fr)

mid = im.rotate(-total / 2, resample=Image.BICUBIC, center=(cx, cy), fillcolor=bg).resize((SIZE, SIZE), Image.LANCZOS)
mid.save(out.with_name(out.stem + "_preview.png"), "PNG")

frames[0].save(out, save_all=True, append_images=frames[1:], duration=dur, loop=0, optimize=True, disposal=2)
print(f"OK -> {out}  ({N}f, {out.stat().st_size//1024}KB)")
