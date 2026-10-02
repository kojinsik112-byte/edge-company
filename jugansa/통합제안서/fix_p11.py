# -*- coding: utf-8 -*-
"""통합제안서 1-36p 11페이지(재무) 텍스트 수정.
- 자본금 5억→2억(NICE: 납입자본금 200백만원), 신용 B+→BB-(NICE 2026.06.19)
- '자가 사옥' → '본사 사옥'(소유 미확인: NICE 보고서상 사업장 '임차')
- 신용 카드 → 현금흐름 A·부채비율 17.1% 우선 표기
사용: python fix_p11.py 원본.pdf 출력.pdf   (스캔 증빙 이미지는 수정하지 않음)"""
import sys, os
import pymupdf as fitz

src, dst = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
BOLD = next(c for c in [os.path.join(HERE, "fonts", "Pretendard-Bold.ttf"), r"C:\Windows\Fonts\malgunbd.ttf"] if os.path.exists(c))
REG = next(c for c in [os.path.join(HERE, "fonts", "Pretendard-Regular.ttf"), r"C:\Windows\Fonts\malgun.ttf"] if os.path.exists(c))
ALTF = next(c for c in ["/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", r"C:\Windows\Fonts\arialbd.ttf"] if os.path.exists(c))
FB, FR, ALT = fitz.Font(fontfile=BOLD), fitz.Font(fontfile=REG), fitz.Font(fontfile=ALTF)
W, G, SUB, LG, DESC = 0xffffff, 0xe3c48c, 0xa8b8ca, 0xc2ab85, 0x9dadbe

# (지울 span들 [(텍스트, y0)], 새로 쓸 조각들 [(텍스트, 크기, 색, 굵게)])
EDITS = [
    ([("자본금 ", 55.0), ("5억", 55.0), (" · ", 55.0), ("자가 사옥", 55.0), (" 보유", 55.0)],
     [("자본금 ", 28, W, 1), ("2억", 28, G, 1), (" · ", 28, W, 1), ("본사 사옥", 28, G, 1), (" 운영", 28, W, 1)]),
    ([("임대 사무실이 아닌 ", 95.8), ("자사 소유 사옥", 95.8), (", 그리고 공인 평가기관의 등급으로 증명합니다.", 95.8)],
     [("울산 본사·쇼룸을 ", 10.5, SUB, 0), ("직접 운영", 10.5, G, 1), ("하고, 재무 건전성은 공인 평가기관 보고서로 증명합니다.", 10.5, SUB, 0)]),
    ([("엣지컴퍼니 자가 사옥", 489.2)], [("엣지컴퍼니 본사 사옥", 11.5, 0xf0e2c4, 1)]),
    ([("5", 190.4)], [("2", 27, 0xedd6a4, 1)]),
    ([("자가", 197.1)], [("본사", 27, 0xedd6a4, 1)]),
    ([("자가 사옥 보유", 234.2)], [("본사 · 쇼룸 운영", 11.5, W, 1)]),
    ([("C R E D I T", 382.0)], [("F I N A N C E", 8, 0xc9a96a, 1)]),
    ([("B+", 392.9), (" ", 409.2), ("/ 현금흐름 A", 409.2)], [("A", 27, 0xedd6a4, 1), ("  현금흐름 등급", 12, LG, 1)]),
    ([("기업 신용등급", 430.0)], [("부채비율 17.1% · 신용 BB-", 11.5, W, 1)]),
    ([("공인 평가기관 기업신용평가 등급.", 449.2)], [("NICE 기업신용평가 보고서(2026.06.19) 기준.", 9, DESC, 0)]),
    ([("자본금 5억 · 자가 사옥 · 신용등급 B+ — 박람회 한 번으로 사라지지 않는 주관사의 조건입니다.", 536.8)],
     [("현금흐름 A · 부채비율 17.1% · ISO 3종 — 박람회 한 번으로 사라지지 않는 주관사의 조건입니다.", 10.5, 0xe8eef5, 1)]),
]

def rgb(c): return ((c >> 16) & 255) / 255, ((c >> 8) & 255) / 255, (c & 255) / 255

doc = fitz.open(src)
page = doc[10]
spans = [s for b in page.get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"]]
plan = []
for targets, pieces in EDITS:
    found = []
    for txt, y0 in targets:
        m = [s for s in spans if s["text"] == txt and abs(s["bbox"][1] - y0) < 1]
        assert len(m) == 1, (txt, y0, len(m))
        found.append(m[0])
    plan.append((found, pieces))
for found, _ in plan:
    for s in found:
        page.add_redact_annot(fitz.Rect(s["bbox"]))
page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
for found, pieces in plan:
    x, y = found[0]["origin"]
    for txt, size, color, bold in pieces:
        tw = fitz.TextWriter(page.rect)
        for ch in txt:  # 대시류는 보조 폰트(Pretendard 렌더 누락 대응)
            f = FB if bold else FR
            tw.append((x, y), ch, font=f, fontsize=size)
            x += f.text_length(ch, fontsize=size)
        tw.write_text(page, color=rgb(color))
doc.save(dst, garbage=3, deflate=True)
print("saved", dst)
