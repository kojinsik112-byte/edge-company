# -*- coding: utf-8 -*-
"""통합제안서 1-36p 텍스트 수정 (11p 재무 페이지): 자본금 5억→2억, 신용 B+→BB-.
사용: python fix_p11.py 원본.pdf 출력.pdf
스캔 서류(기업신용평가서 등 이미지)는 절대 수정하지 않음 — 새 증빙 스캔으로 교체할 것."""
import sys, glob, os
import pymupdf as fitz

src, dst = sys.argv[1], sys.argv[2]
cands = glob.glob(os.path.expanduser("~/.local/share/fonts/Pretendard-Bold.otf")) + \
        [r"C:\Windows\Fonts\malgunbd.ttf"]
BOLD = next(c for c in cands if os.path.exists(c))

def rgb(c): return ((c >> 16) & 255) / 255, ((c >> 8) & 255) / 255, (c & 255) / 255

# 원문 → (새 문구 조각들) : 각 조각 = (텍스트, 크기, 색)
EDITS = {
    "5억": [("2억", None, None)],
    "5": [("2", None, None)],
    "B+": [("BB-", None, None), (" / 현금흐름 A", 12.0, 0xc2ab85)],
    "/ 현금흐름 A": [],  # B+ 쪽에서 함께 다시 씀
    "자본금 5억 · 자가 사옥 · 신용등급 B+ — 박람회 한 번으로 사라지지 않는 주관사의 조건입니다.":
        [("자가 사옥 · ISO 3종 · 삼성전자 MOU — 박람회 한 번으로 사라지지 않는 주관사의 조건입니다.", None, None)],
}

doc = fitz.open(src)
page = doc[10]  # 11페이지
todo = []
for b in page.get_text("dict")["blocks"]:
    for l in b.get("lines", []):
        for s in l["spans"]:
            if s["text"] in EDITS and not (s["text"] == "5" and s["size"] < 20):
                todo.append(s)
assert len(todo) == 5, [s["text"] for s in todo]
for s in todo:
    page.add_redact_annot(fitz.Rect(s["bbox"]))
page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
font = fitz.Font(fontfile=BOLD)
ALT_F = next(c for c in ["/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", r"C:\Windows\Fonts\arialbd.ttf"] if os.path.exists(c))
ALT = fitz.Font(fontfile=ALT_F)
for s in todo:
    x, y = s["origin"]
    for txt, size, color in EDITS[s["text"]]:
        size = size or s["size"]; color = color if color is not None else s["color"]
        tw = fitz.TextWriter(page.rect)
        for ch in txt:  # 대시류는 Pretendard 렌더 누락 → 보조 폰트
            f = ALT if ch in "-—" else font
            tw.append((x, y), ch, font=f, fontsize=size)
            x += f.text_length(ch, fontsize=size)
        tw.write_text(page, color=rgb(color))
        x += 6 if txt == "BB-" else 0
doc.save(dst, garbage=3, deflate=True)
print("saved", dst)
