# -*- coding: utf-8 -*-
"""제출서류 8) 별첨 1 — NICE디앤비 CLIP 기업신용평가보고서 '연혁' 발췌 (A4 1장).

원본 면은 손대지 않고 잘라 붙인다: 표지(축소) + 9쪽 제목띠 · 연혁 · 쪽 번호. 빠진 부분은 '중략'으로 표시.
주관 실적 7행에는 금색 테두리만 둔다.

NICE 원본이 들어가므로 결과물은 깃에 올리지 않는다(.gitignore).
사용: python annex.py <NICE_기업신용평가.pdf>
  → 엣지컴퍼니_동탄파라곤3차_08_별첨1_NICE연혁발췌.pdf
  → 엣지컴퍼니_동탄파라곤3차_08_행사실적_별첨1포함.pdf (8) 본문 + 별첨 1)
"""
import os
import sys

import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data as D  # noqa: E402

FONTS = os.path.join(HERE, "..", "통합제안서", "fonts")
REG, BOLD = os.path.join(FONTS, "Pretendard-Regular.ttf"), os.path.join(FONTS, "Pretendard-Bold.ttf")
NAVY, GOLD, GRAY, LINE = (0.051, 0.118, 0.2), (0.78, 0.66, 0.42), (0.36, 0.4, 0.46), (0.79, 0.81, 0.84)
ANNEX = os.path.join(HERE, "엣지컴퍼니_동탄파라곤3차_08_별첨1_NICE연혁발췌.pdf")
DOC8 = os.path.join(HERE, "엣지컴퍼니_동탄파라곤3차_08_최근5년_1000세대이상_행사실적.pdf")
BOTH = os.path.join(HERE, "엣지컴퍼니_동탄파라곤3차_08_행사실적_별첨1포함.pdf")

# NICE 9쪽(index 8)에서 가져올 영역(pt) — 원본 픽셀로 확인한 값
CLIP_TITLE = fitz.Rect(0, 0, 595, 76)        # '04 영업 현황(기업개요)' 제목띠
CLIP_HIST = fitz.Rect(36, 321, 560, 511)     # '■ 연혁' 표 전체
ROWS_RECORD = (380, 506)                     # 연혁 표 중 주관 실적 7행(2023/03 ~ 2026/07)
CLIP_FOOT = fitz.Rect(36, 800, 560, 828)     # NICE디앤비 로고 · '- 9 -'


class Pen:
    def __init__(self, page):
        self.page = page
        self.f = {"r": fitz.Font(fontfile=REG), "b": fitz.Font(fontfile=BOLD)}

    def text(self, x, y, s, size=9.5, w="r", color=NAVY, align="l"):
        f = self.f[w]
        if align != "l":
            tl = f.text_length(s, fontsize=size)
            x = x - tl / 2 if align == "c" else x - tl
        tw = fitz.TextWriter(self.page.rect)
        tw.append((x, y), s, font=f, fontsize=size)
        tw.write_text(self.page, color=color)


def build(nice_path):
    nice = fitz.open(nice_path)
    out = fitz.open()
    pg = out.new_page(width=595.28, height=841.89)
    pen = Pen(pg)
    L, R = 48, 547

    # 머리
    pg.draw_rect(fitz.Rect(L, 40, L + 46, 56), color=GOLD, width=1)
    pen.text(L + 23, 51.5, "별첨 1", 8.5, "b", GOLD, "c")
    pen.text(R, 51.5, "제출서류 8) 최근 5년간 1,000세대 이상 행사 실적", 8.5, "r", GRAY, "r")
    pg.draw_line((L, 64), (R, 64), color=NAVY, width=2)
    pen.text(L, 92, "NICE디앤비 기업신용평가보고서 ‘연혁’ 발췌", 17, "b")
    pen.text(L, 110, f"건명 : {D.TITLE}", 8.8, "r", GRAY)

    # 표지(축소) + 보고서 정보
    top = 126
    cover = fitz.Rect(L, top, L + 168, top + 168 * 842 / 595)
    pg.show_pdf_page(cover, nice, 0)
    pg.draw_rect(cover, color=LINE, width=0.6)
    info = [("보고서명", "CLIP 기업신용평가보고서"), ("발행 기관", "NICE디앤비 (dun & bradstreet)"),
            ("평가 대상", f"{D.COMPANY} (508-81-42798)"), ("관리번호", "11125949-202605-001"),
            ("평가완료일", "2026.06.19"), ("발췌 범위", "9쪽 ‘04 영업 현황(기업개요)’ 중 ‘연혁’"),
            ("원본 분량", f"전 {len(nice)}쪽")]
    x0, x1, xk, rh = L + 186, R, L + 186 + 70, 24
    for i, (k, v) in enumerate(info):
        y = top + i * rh
        pg.draw_rect(fitz.Rect(x0, y, xk, y + rh), color=LINE, fill=(0.945, 0.929, 0.894), width=0.6)
        pg.draw_rect(fitz.Rect(xk, y, x1, y + rh), color=LINE, width=0.6)
        pen.text(x0 + 8, y + 15.5, k, 8.8, "b")
        pen.text(xk + 8, y + 15.5, v, 8.8, "r", (0.1, 0.14, 0.2))
    y = top + len(info) * rh + 18
    pen.text(x0, y, "아래 연혁 중 금색 테두리 7행이 공고일 기준", 8.8, "r", GRAY)
    pen.text(x0, y + 13, "최근 5년 1,000세대 이상 입주박람회 주관 실적입니다.", 8.8, "r", GRAY)

    # 9쪽 발췌: 원본 좌표를 한 배율로 옮겨 쌓는다
    s = (R - L) / 595
    y = cover.y1 + 22
    pen.text(L, y, "■ 원본 9쪽 발췌", 9, "b")
    box_top = y + 8
    y = box_top + 4

    def put(clip, y):
        r = fitz.Rect(L + clip.x0 * s, y, L + clip.x1 * s, y + clip.height * s)
        pg.show_pdf_page(r, nice, 8, clip=clip)
        return r

    put(CLIP_TITLE, y)
    y += CLIP_TITLE.height * s + 2
    pen.text((L + R) / 2, y + 9, "··· (중략: 기업개요) ···", 8, "r", GRAY, "c")
    y += 16
    hist = put(CLIP_HIST, y)
    hy0 = hist.y0 + (ROWS_RECORD[0] - CLIP_HIST.y0) * s
    hy1 = hist.y0 + (ROWS_RECORD[1] - CLIP_HIST.y0) * s
    pg.draw_rect(fitz.Rect(hist.x0 - 3, hy0 - 1, hist.x1 + 3, hy1 + 1), color=GOLD, width=1.6)
    y = hist.y1 + 4
    pen.text((L + R) / 2, y + 9, "··· (이하 생략: 관계회사) ···", 8, "r", GRAY, "c")
    y += 16
    foot = put(CLIP_FOOT, y)
    pg.draw_rect(fitz.Rect(L, box_top, R, foot.y1 + 6), color=LINE, width=0.6)

    # 원본대조
    y = foot.y1 + 40
    pen.text((L + R) / 2, y, "위 발췌 내용은 원본과 같음을 확인합니다.", 10, "r", (0.1, 0.14, 0.2), "c")
    yy, mm, dd = D.SIGN_DATE
    pen.text((L + R) / 2, y + 26, f"{yy}년 {mm}월 {dd}일", 10, "r", (0.1, 0.14, 0.2), "c")
    who = f"{D.COMPANY}   대표이사   {D.CEO}"
    pen.text((L + R) / 2 - 14, y + 52, who, 11, "b", NAVY, "c")
    sx = (L + R) / 2 - 14 + pen.f["b"].text_length(who, fontsize=11) / 2 + 8
    pen.text(sx, y + 52, "(인)", 10, "r", GRAY)  # 직인은 stamp.py가 이 자리에 찍음

    out.set_metadata({"title": "별첨 1 NICE 기업신용평가보고서 연혁 발췌", "author": D.COMPANY})
    out.save(ANNEX, garbage=4, deflate=True)
    print("saved", ANNEX)
    if os.path.exists(DOC8):
        both = fitz.open(DOC8)
        both.insert_pdf(out)
        both.set_metadata({"title": "8) 최근 5년간 1,000세대 이상 행사 실적 (별첨 1 포함)", "author": D.COMPANY})
        both.save(BOTH, garbage=4, deflate=True)
        print("saved", BOTH, len(both), "pages")


if __name__ == "__main__":
    build(sys.argv[1])
