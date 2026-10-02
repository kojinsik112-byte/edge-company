# -*- coding: utf-8 -*-
"""직인 날인: PDF에서 '(인감날인)' 또는 '(인)' 글자를 찾아 그 자리에 직인 이미지를 찍는다.

직인 이미지는 저장소에 두지 않는다(공개 저장소 — 위조 방지). 결과 파일 이름은 '<원본>_직인.pdf'이고 .gitignore 대상.
사용: python stamp.py <직인.png|webp> <파일.pdf> [파일.pdf ...]
"""
import io
import os
import sys

import pymupdf as fitz
from PIL import Image

SIZE = 54  # pt ≈ 19mm (법인 인감 실제 크기와 비슷하게)
MARKS = ("(인감날인)", "(인)")


def seal_png(path):
    """배경 투명 + 인주처럼 살짝 비치게(알파 90%)."""
    im = Image.open(path).convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if r > 235 and g > 235 and b > 235:  # 흰 배경이 있으면 투명 처리
                a = 0
            px[x, y] = (r, g, b, int(a * 0.9))
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return buf.getvalue()


def stamp(seal, pdf_path):
    doc = fitz.open(pdf_path)
    n = 0
    for page in doc:
        for mark in MARKS:
            hits = page.search_for(mark)
            if not hits:
                continue
            for r in hits:
                c = fitz.Point((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2)
                page.insert_image(fitz.Rect(c.x - SIZE / 2, c.y - SIZE / 2, c.x + SIZE / 2, c.y + SIZE / 2),
                                  stream=seal, overlay=True)
                n += 1
            break  # '(인감날인)'을 찾았으면 그 안의 '(인'은 다시 찍지 않음
    out = pdf_path[:-4] + "_직인.pdf"
    doc.save(out, garbage=4, deflate=True)
    print(f"saved {out} (날인 {n}곳)")
    return out, n


if __name__ == "__main__":
    seal = seal_png(sys.argv[1])
    for p in sys.argv[2:]:
        stamp(seal, p)
