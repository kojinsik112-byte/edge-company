# -*- coding: utf-8 -*-
"""개인정보 가림을 '그림 위 덮개'가 아니라 픽셀로 굳힌다(덮개만 씌우면 원본 이미지·벡터에서 번호를 다시 뽑을 수 있음).

04 법인인감증명서: 대표이사 주민등록번호 뒷자리 7칸을 종이색으로 지우고(redaction, 이미지 픽셀까지) '*' 7개를 그린 뒤
   페이지를 300dpi 한 장 이미지로 평탄화. 좌표는 2026.10.08 발급본 스캔에서 글자 픽셀로 잰 값(번호 자체는 기록하지 않음).
06 4대보험 명부(이미 가린 본): 각 쪽을 300dpi 이미지로 평탄화해 덮개 아래 원본 글자를 없앤다.
사용: python mask_cs.py ingam <인감증명서.pdf> <out.pdf> | python mask_cs.py flat <in.pdf> <out.pdf>
결과물은 개인정보 문서 — 깃에 올리지 않는다.
"""
import math
import os
import statistics
import sys

import pymupdf as fitz

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "동탄파라곤3차"))
from mask_ingam import ink_color, paper_color  # noqa: E402

DIGITS = [(290.25, 294.12), (294.88, 299.5), (300.62, 305.38), (306.0, 310.75),
          (311.38, 316.5), (317.88, 321.5), (322.62, 327.25)]
Y0, Y1 = 396.6, 405.9
FRONT = fitz.Rect(250.6, 397, 283.0, 405.5)


def flatten(doc, dpi=300, title=None):
    out = fitz.open()
    for p in doc:
        pix = p.get_pixmap(dpi=dpi, alpha=False)
        np_ = out.new_page(width=p.rect.width, height=p.rect.height)
        np_.insert_image(np_.rect, stream=pix.tobytes("jpeg", jpg_quality=92))
    out.set_metadata({"title": title or (doc.metadata or {}).get("title", ""), "author": "주식회사 엣지컴퍼니"})
    return out


def star(page, cx, cy, r, color, width):
    for k in range(3):
        a = math.pi / 2 + k * math.pi / 3
        dx, dy = r * math.cos(a), r * math.sin(a)
        page.draw_line(fitz.Point(cx - dx, cy - dy), fitz.Point(cx + dx, cy + dy), color=color, width=width, lineCap=1)


def ingam(src, dst):
    doc = fitz.open(src)
    page = doc[0]
    box = fitz.Rect(DIGITS[0][0] - 0.6, Y0 - 0.5, DIGITS[-1][1] + 0.6, Y1 + 0.5)
    paper, ink = paper_color(page, box), ink_color(page, FRONT)
    page.add_redact_annot(box, fill=paper)
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS)
    cy = (Y0 + Y1) / 2
    for x0, x1 in DIGITS:
        star(page, (x0 + x1) / 2, cy, 2.15, ink, 0.75)
    flatten(doc, title="법인인감증명서(주민등록번호 뒷자리 가림)").save(dst, garbage=4, deflate=True)


if __name__ == "__main__":
    mode, src, dst = sys.argv[1:4]
    if mode == "ingam":
        ingam(src, dst)
    else:
        flatten(fitz.open(src)).save(dst, garbage=4, deflate=True)
    print("saved", dst)
