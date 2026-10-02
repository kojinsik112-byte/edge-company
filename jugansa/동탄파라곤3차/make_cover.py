# -*- coding: utf-8 -*-
"""2-1 표지용 단지 이미지 — 임예협 입찰공고 1쪽 상단의 '동탄2 신동 Paragon 3차' 단지 조감도를 가공.

1) 공고 PDF에서 원본 이미지를 그대로 꺼냄
2) 하늘에 얹힌 제목 글자·금색 선을 위아래 하늘색으로 메워 지움(건물에는 손대지 않음)
3) 단지 부분만 자르고, 하늘을 투명하게 오려 네이비 표지 위로 건물이 솟아 보이게 함
4) 해질녘 톤(약간 어둡게·따뜻하게)으로 맞춤

원본은 임예협이 공고문에 넣은 이미지(사업주체 조감도)이므로 깃에는 올리지 않는다(.gitignore *.png).
실행: python make_cover.py <입찰공고.pdf>   → assets_dt/paragon3_cover.png
"""
import os
import sys

import numpy as np
import pymupdf as fitz
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets_dt", "paragon3_cover.png")

# 원본(1453×484)에서 지울 영역: (x0, y0, x1, y1) — 하늘 위 글자·선만, 건물과 겹치지 않는 범위
ERASE = [(230, 74, 1226, 93),     # 위 금색 선
         (355, 124, 1128, 206),   # '동탄2 신동 Paragon 3차'
         (278, 232, 1174, 253)]   # 아래 금색 선
CROP = (88, 182, 1352, 433)       # 단지(왼쪽 노을 번짐·오른쪽 구름 제외, 하늘 일부 ~ 잔디 끝)


def banner(pdf):
    doc = fitz.open(pdf)
    info = max(doc[0].get_image_info(xrefs=True), key=lambda b: b["width"] * b["height"])
    pix = fitz.Pixmap(doc, info["xref"])
    if pix.n - pix.alpha > 3:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    return np.asarray(Image.frombytes("RGB", (pix.width, pix.height), pix.samples)).astype(np.float32)


def erase(a):
    for x0, y0, x1, y1 in ERASE:
        top, bot = a[y0 - 2, x0:x1].copy(), a[y1 + 2, x0:x1].copy()
        n = y1 - y0
        for k in range(n):
            w = (k + 1) / (n + 1)
            a[y0 + k, x0:x1] = top * (1 - w) + bot * w
    return a


def sky_alpha(a):
    """열마다 위에서부터 '하늘이 아닌' 첫 픽셀을 찾아 그 위를 투명하게."""
    h, w, _ = a.shape
    lum = a.mean(axis=2)
    sat = a.max(axis=2) - a.min(axis=2)
    ref = a[2]  # 맨 윗줄 = 하늘
    diff = np.abs(a - ref[None, :, :]).sum(axis=2)
    nonsky = (diff > 34) | (lum < 205) | ((sat > 60) & (lum < 235))
    first = np.where(nonsky.any(axis=0), nonsky.argmax(axis=0), h)
    med = np.array([np.median(first[max(0, x - 1):x + 2]) for x in range(w)])  # 열 사이 잡음 제거
    # 건물 윤곽을 1px 안으로(좌우 이웃 중 낮은 쪽) → 하늘과 섞인 밝은 테두리 제거
    sm = np.array([med[max(0, x - 1):x + 2].max() for x in range(w)]) + 1
    yy = np.arange(h)[:, None]
    alpha = np.clip((yy - sm[None, :]) / 2.0, 0, 1)
    # 좌우 끝·아래쪽은 네이비로 자연스럽게 사라지게
    xx = np.arange(w)[None, :]
    side = np.clip(np.minimum(xx, w - 1 - xx) / (w * 0.06), 0, 1)
    bottom = np.clip((h - 1 - yy) / (h * 0.16), 0, 1)
    return alpha * side * bottom, sm


def grade(a, edge):
    """해질녘 톤: 대비 살짝 올리고 따뜻하게, 네이비 배경과 어울리게 전체를 낮춤.
    건물 윤곽 바로 아래 3px은 한 번 더 눌러 밝은 테두리를 지운다."""
    a = (a - 128) * 1.06 + 128
    a = a * 0.80
    a[..., 0] *= 1.06
    a[..., 1] *= 1.00
    a[..., 2] *= 0.88
    h, w, _ = a.shape
    yy = np.arange(h)[:, None]
    band = (yy >= edge[None, :]) & (yy < edge[None, :] + 3)
    a[band] *= 0.82
    return np.clip(a, 0, 255)


def main(pdf):
    a = erase(banner(pdf))
    x0, y0, x1, y1 = CROP
    a = a[y0:y1, x0:x1].copy()
    alpha, edge = sky_alpha(a)
    a = grade(a, edge)
    im = Image.fromarray(np.dstack([a, alpha * 255]).astype(np.uint8), "RGBA")
    # 인쇄용 2배 업스케일 + 약한 선명화
    im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2, 60, 2))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    im.save(OUT, optimize=True)
    print("saved", OUT, im.size)


if __name__ == "__main__":
    main(sys.argv[1])
