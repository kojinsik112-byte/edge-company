# -*- coding: utf-8 -*-
"""제출서류 4) 법인인감증명서 — 대표이사 주민등록번호 뒷자리 7자리를 '*******'로 가린 제출본.

스캔본(이미지 1장) 위에 덮어쓴다: 뒷자리 7칸만 종이색(주변 중앙값)으로 메우고, 같은 글자 간격으로 '*'를 그린다.
'*' 색은 같은 줄 앞자리 숫자의 잉크색. 하이픈·괄호·앞자리·인감·발급확인번호·하단 바코드는 그대로.
좌표(pt)는 2026.09.11 발급본 스캔에서 글자 픽셀로 잰 값.

개인정보 문서이므로 결과물은 깃에 올리지 않는다(.gitignore).
사용: python mask_ingam.py <인감증명서.pdf>
"""
import io
import math
import os
import statistics
import sys

import pymupdf as fitz
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "엣지컴퍼니_동탄파라곤3차_04_인감증명서_가림.pdf")

# 뒷자리 7글자 칸(x0, x1) — '(870102-1903518)' 중 '1903518'
DIGITS = [(294.12, 298.5), (299.25, 303.88), (304.62, 309.62), (310.38, 315.0),
          (315.75, 320.38), (321.88, 326.25), (326.88, 331.62)]
Y0, Y1 = 383.3, 393.3          # 글자 높이(괄호 포함 잉크 범위)
FRONT = fitz.Rect(254.5, 384, 287.25, 393)  # 앞자리 숫자(잉크색 표본)


def pixels(page, rect, z=6):
    pix = page.get_pixmap(matrix=fitz.Matrix(z, z), clip=rect, alpha=False)
    im = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
    return list(im.getdata())


def paper_color(page, rect):
    ring = [fitz.Rect(rect.x0 - 3, rect.y0 - 4, rect.x1 + 3, rect.y0 - 1),
            fitz.Rect(rect.x0 - 3, rect.y1 + 1, rect.x1 + 3, rect.y1 + 4)]
    px = [c for r in ring for c in pixels(page, r)]
    return tuple(statistics.median(c[i] for c in px) / 255 for i in range(3))


def ink_color(page, rect):
    px = sorted(pixels(page, rect), key=sum)
    core = px[: max(1, len(px) // 12)]  # 가장 진한 픽셀들
    return tuple(statistics.median(c[i] for c in core) / 255 for i in range(3))


def star(page, cx, cy, r, color, width):
    """6갈래 '*' — 타자 글꼴 별표처럼 선 3개."""
    for k in range(3):
        a = math.pi / 2 + k * math.pi / 3
        dx, dy = r * math.cos(a), r * math.sin(a)
        page.draw_line(fitz.Point(cx - dx, cy - dy), fitz.Point(cx + dx, cy + dy), color=color, width=width,
                       lineCap=1, overlay=True)


def main():
    doc = fitz.open(sys.argv[1])
    page = doc[0]
    box = fitz.Rect(DIGITS[0][0] - 0.6, Y0 - 0.4, DIGITS[-1][1] + 0.6, Y1 + 0.4)
    paper, ink = paper_color(page, box), ink_color(page, FRONT)
    page.draw_rect(box, color=None, fill=paper, overlay=True)
    cy = (Y0 + Y1) / 2
    for x0, x1 in DIGITS:
        star(page, (x0 + x1) / 2, cy, 2.15, ink, 0.75)
    doc.set_metadata({"title": "법인인감증명서(주민등록번호 뒷자리 가림)", "author": "주식회사 엣지컴퍼니"})
    doc.save(OUT, garbage=4, deflate=True)
    print("saved", OUT)


if __name__ == "__main__":
    main()
