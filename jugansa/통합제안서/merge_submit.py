# -*- coding: utf-8 -*-
"""제출용 통합본(152p, 원본 화질) 만들기.

1파트 = fix_all.py 결과(수정본), 2·3파트 = 원본 그대로.
단, 2파트 우측 상단 70번 장(2파트 32번째 장)의 '95% 이상' → '90% 이상' 한 곳만 수정
(요약제안서 '지역업체 90%'와 숫자 통일).

사용: python merge_submit.py <1파트_수정본.pdf> <2파트_원본.pdf> <3파트_원본.pdf> <출력.pdf>
"""
import os
import sys

import pymupdf as fitz

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fix_all import ink, rgb, sample_bg  # noqa: E402


def fix_local_ratio(doc):
    """2파트 index 31: 이미지에 박힌 '95'를 같은 글꼴(PDF에 내장된 맑은 고딕)로 '90'으로 교체.
    좌표·크기는 원본 글자 픽셀에 맞춰 보정한 값(15.4pt, x 246.0, 기준선 180.8)."""
    page = doc[31]
    buf = next(doc.extract_font(fi[0])[3] for fi in page.get_fonts(full=True) if fi[3].endswith("+MalgunGothic"))
    mg = fitz.Font(fontbuffer=buf)
    # 글자색·배경색: 원본 픽셀의 중앙값(배경은 패치 바깥 테두리, 글자는 배경과 먼 픽셀)
    rect = fitz.Rect(245.6, 168, 264.2, 182.5)
    bg = sample_bg(page, rect, ring=1.5)
    col = ink(page, rect)
    # 숨은 텍스트층도 같이 교체(검색·복사용)
    spans = [s for b in page.get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"]
             if s["text"].startswith("95% 이상")]
    assert len(spans) == 1, len(spans)
    s = spans[0]
    page.add_redact_annot(fitz.Rect(s["bbox"]))
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
    hidden = fitz.TextWriter(page.rect)
    hidden.append(s["origin"], s["text"].replace("95%", "90%", 1), font=mg, fontsize=s["size"])
    hidden.write_text(page, render_mode=3)
    # 화면에 보이는 숫자
    page.draw_rect(rect, color=None, fill=bg, overlay=True)
    tw = fitz.TextWriter(page.rect)
    tw.append((246.0, 180.8), "90", font=mg, fontsize=15.4)
    tw.write_text(page, color=rgb(col))


def main():
    p1, p2, p3, out = sys.argv[1:5]
    merged = fitz.open()
    merged.insert_pdf(fitz.open(p1))
    d2 = fitz.open(p2)
    fix_local_ratio(d2)
    merged.insert_pdf(d2)
    merged.insert_pdf(fitz.open(p3))
    merged.set_metadata({"title": "엣지컴퍼니 통합제안서", "author": "주식회사 엣지컴퍼니"})
    merged.save(out, garbage=4, deflate=True)
    print("saved", out, len(merged), "pages")


if __name__ == "__main__":
    main()
