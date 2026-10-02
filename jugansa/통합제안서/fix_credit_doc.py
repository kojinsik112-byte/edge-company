# -*- coding: utf-8 -*-
"""9·10p 기업신용평가 액자 속 서류를 NICE 공식 보고서(2026.06.19, BB-) 3쪽 원본으로 교체.
사용: python fix_credit_doc.py 입력.pdf NICE보고서.pdf 출력.pdf"""
import sys
import pymupdf as fitz
src, nice, dst = sys.argv[1:4]
rep = fitz.open(nice)
png = rep[2].get_pixmap(dpi=220).tobytes("png")  # '01 기업신용평가 요약' 페이지
doc = fitz.open(src)
FRAMES = {8: fitz.Rect(392, 199, 608, 523), 9: fitz.Rect(294, 154, 550, 513)}  # 0-index 페이지: 액자 내부
for pno, r in FRAMES.items():
    pg = doc[pno]
    pg.draw_rect(r, color=None, fill=(1, 1, 1), overlay=True)
    pg.insert_image(r + (3, 3, -3, -3), stream=png, keep_proportion=True, overlay=True)
doc.save(dst, garbage=3, deflate=True)
print("saved", dst)
