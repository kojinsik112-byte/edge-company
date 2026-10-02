# -*- coding: utf-8 -*-
"""제출서류 6) 4대보험 사업장 가입자 명부 — 성명 가운데 글자를 '*'로 가린 제출본.

원본 서식·직인·발급번호는 그대로 두고, 1쪽 성명 10명의 가운데 글자만 가린다(2쪽은 '이하 여백'·공단 직인).
'*'는 같은 문서 주민번호 칸에 찍힌 별표를 그대로 복사해 쓴다(글꼴·굵기 동일).
좌표는 통합제안서/fix_all.py 의 ROSTER_ROWS(같은 명부, 2026-10-02 발급본)와 같다.
옵션 --rrn : 주민번호 뒷자리 첫 숫자(성별)도 함께 가림(통합제안서 수록본과 동일 처리).

개인정보 문서이므로 결과물은 깃에 올리지 않는다(.gitignore).
사용: python mask_roster.py <4대보험_가입자명부.pdf> [--rrn]
"""
import os
import sys

import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "통합제안서"))
from fix_all import ROSTER_ROWS  # noqa: E402

OUT = os.path.join(HERE, "엣지컴퍼니_동탄파라곤3차_06_4대보험_가입자명부_가림.pdf")
WHITE = (1, 1, 1)


def mask(doc, rrn=False):
    page = doc[0]
    for (ny, gy, ay) in ROSTER_ROWS:
        star_clip = fitz.Rect(147.7, ay[0] - 0.3, 152.3, ay[1] + 0.3)
        star = page.get_pixmap(matrix=fitz.Matrix(10, 10), clip=star_clip, alpha=False).tobytes("png")
        sw, sh = star_clip.width, star_clip.height
        if rrn:
            page.draw_rect(fitz.Rect(141.0, gy[0] - 0.5, 146.4, gy[1] + 0.5), color=None, fill=WHITE, overlay=True)
            page.insert_image(fitz.Rect(141.4, star_clip.y0, 141.4 + sw, star_clip.y1), stream=star, overlay=True)
        # 성명 가운데 글자 → '*' (글자 높이 가운데, 1.5배)
        page.draw_rect(fitz.Rect(228.6, ny[0] - 0.6, 238.5, ny[1] + 0.6), color=None, fill=WHITE, overlay=True)
        k, cx, cy = 1.5, 233.55, (ny[0] + ny[1]) / 2
        page.insert_image(fitz.Rect(cx - sw * k / 2, cy - sh * k / 2, cx + sw * k / 2, cy + sh * k / 2),
                          stream=star, overlay=True)
    return len(ROSTER_ROWS)


def main():
    src = sys.argv[1]
    doc = fitz.open(src)
    n = mask(doc, rrn="--rrn" in sys.argv)
    doc.set_metadata({"title": "4대 사회보험 사업장 가입자 명부(개인정보 일부 가림)", "author": "주식회사 엣지컴퍼니"})
    doc.save(OUT, garbage=4, deflate=True)
    print(f"saved {OUT} ({n}명 성명 가운데 글자 가림{' + 주민번호 성별자리' if '--rrn' in sys.argv else ''})")


if __name__ == "__main__":
    main()
