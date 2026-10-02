# -*- coding: utf-8 -*-
"""공고문 별지 #1~#5를 원본 양식 그대로 두고 빈칸만 채운다(직인은 stamp.py).

- 별지#1 입찰참가신청서: 업체정보·담당자 표, 날짜, 업체명·대표자명
- 별지#2~#5: 날짜, 법인명·대표자명 / #5는 '[업체명 기입] (은)는' → '주식회사 엣지컴퍼니는'
값은 data.py. 칸 좌표는 공고 PDF의 표 선(drawings)과 글자 위치(rawdict)로 잰 값.

사용: python forms.py <입찰공고.pdf>
  → 엣지컴퍼니_동탄파라곤3차_01_입찰참가신청서_별지1.pdf … 13_위반사실확약서_별지5.pdf
"""
import os
import sys

import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data as D  # noqa: E402

FONT = fitz.Font(fontfile=os.path.join(HERE, "..", "통합제안서", "fonts", "Pretendard-Regular.ttf"))
INK = (0.08, 0.08, 0.1)
# (공고 PDF 쪽 index, 제출서류 번호, 파일 이름)
FORMS = [(5, "01", "입찰참가신청서_별지1"), (6, "10", "업무이행각서_별지2"), (7, "11", "AS이행각서_별지3"),
         (8, "12", "이의제기금지서약서_별지4"), (9, "13", "위반사실확약서_별지5")]


def put(page, x, y, s, size=10.0, align="c", maxw=None):
    if maxw:
        while FONT.text_length(s, fontsize=size) > maxw and size > 7:
            size -= 0.25
    w = FONT.text_length(s, fontsize=size)
    x = x - w / 2 if align == "c" else x
    tw = fitz.TextWriter(page.rect)
    tw.append((x, y), s, font=FONT, fontsize=size)
    tw.write_text(page, color=INK)


def spans(page):
    for b in page.get_text("rawdict")["blocks"]:
        for ln in b.get("lines", []):
            for s in ln["spans"]:
                yield s, "".join(c["c"] for c in s["chars"])


def find(page, needle):
    for s, t in spans(page):
        if needle in t:
            return s, t
    raise LookupError(needle)


def fill_date(page):
    s, t = find(page, "2026")
    cs = s["chars"]
    pos = {c["c"]: c["bbox"] for c in cs if c["c"] in "년월일"}
    base = s["origin"][1]
    _, mm, dd = D.SIGN_DATE
    put(page, (pos["년"][2] + pos["월"][0]) / 2, base, str(mm), 11)
    put(page, (pos["월"][2] + pos["일"][0]) / 2, base, str(dd), 11)


def fill_blank(page, label, value):
    s, t = find(page, label)
    us = [c for c in s["chars"] if c["c"] == "_"]
    x = (us[0]["bbox"][0] + us[-1]["bbox"][2]) / 2
    put(page, x, s["origin"][1] - 1.5, value, 11)


def fill_table(page):
    """별지#1 업체정보·담당자 표. 값 칸: 왼쪽 214.8~328.6, 오른쪽 414.0~528.4, 넓은 칸 214.8~528.4."""
    L, R, W = (214.8, 328.6), (414.0, 528.4), (214.8, 528.4)
    rows = [  # (행 위, 행 아래)
        (135.0, 163.4), (163.4, 191.7), (191.7, 220.1), (220.1, 248.4), (248.4, 276.8), (276.8, 305.1)]
    name, title, tel = D.MANAGER
    cells = [
        (0, L, D.COMPANY), (0, R, D.BIZ_NO),
        (1, L, D.CEO), (1, R, D.CEO_TEL),
        (2, W, D.ADDRESS),
        (3, W, D.EMAIL),
        (4, L, name), (4, R, title),
        (5, L, tel), (5, R, D.EMAIL),
    ]
    for r, (x0, x1), v in cells:
        y0, y1 = rows[r]
        put(page, (x0 + x1) / 2, (y0 + y1) / 2 + 3.6, v, 10, maxw=x1 - x0 - 8)


def fill_company_line(page):
    """별지#5 첫 줄의 '[업체명 기입] (은)는'을 업체명으로 바꾼다. 글자 크기를 유지하려고 첫 줄 전체를 같은 기준선에 다시 쓴다."""
    s, t = find(page, "[업체명 기입]")
    page.add_redact_annot(fitz.Rect(s["bbox"]))
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
    line = t.replace("[업체명 기입] (은)는", f"{D.COMPANY}는", 1).rstrip()
    put(page, s["origin"][0], s["origin"][1], line, s["size"], align="l", maxw=538 - s["origin"][0])


def build(notice_path):
    src = fitz.open(notice_path)
    outs = []
    for idx, no, name in FORMS:
        doc = fitz.open()
        doc.insert_pdf(src, from_page=idx, to_page=idx)
        page = doc[0]
        if idx == 5:
            fill_table(page)
            fill_blank(page, "업체명 :", D.COMPANY)
        else:
            fill_blank(page, "법인명 :", D.COMPANY)
        if idx == 9:
            fill_company_line(page)
        fill_blank(page, "대표자명 :", D.CEO)
        fill_date(page)
        out = os.path.join(HERE, f"엣지컴퍼니_동탄파라곤3차_{no}_{name}.pdf")
        doc.set_metadata({"title": name.replace("_", " "), "author": D.COMPANY})
        doc.save(out, garbage=4, deflate=True)
        outs.append(out)
        print("saved", out)
    return outs


if __name__ == "__main__":
    build(sys.argv[1])
