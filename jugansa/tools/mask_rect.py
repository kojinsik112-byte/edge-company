"""증빙 PDF 개인정보 가림 — 지정 영역을 회색으로 덮고 이미지로 굳힌다(글자 층이 남지 않음).

사용:
  python3 mask_rect.py <원본.pdf> <가림본.pdf> --preset ingam [--preview 미리보기.png]
  python3 mask_rect.py <원본.pdf> <가림본.pdf> --rect 1:0.47,0.45,0.58,0.50 [--rect …] [--dpi 200]
  python3 mask_rect.py <원본.pdf> <가림본.pdf> --rrn          (글자 층이 있는 PDF — 주민번호 뒷자리를 찾아 가림)

- 좌표 = 쪽 크기 대비 비율(왼쪽 위 0,0 ~ 오른쪽 아래 1,1) · 쪽 번호는 1부터.
- --preset ingam = 법인인감증명서 대표자 주민번호 뒷자리 줄(2026.10.15 등기소 발급 스캔 기준 위치).
  발급처 · 스캔마다 위치가 달라질 수 있으니 미리보기 PNG를 반드시 눈으로 확인한다.
  등기소에서 '주민등록번호 뒷자리 미표시'로 발급하면 가릴 것이 없다(10.15본이 그 방식) — 그때는 이 도구 없이 그대로 쓴다.
- 원본 · 가림본은 개인정보라 깃에 넣지 않는다($SP/evidence_nr/ 등 작업 폴더에만).
"""
import argparse
import io
import re
import sys

import pymupdf as fitz
from PIL import Image, ImageDraw

PRESETS = {"ingam": [(1, (0.474, 0.461, 0.585, 0.492))]}
RRN = re.compile(r"\d{6}\s*-\s*[1-4]\d{6}")


def rrn_rects(doc):
    """글자 층에서 주민번호를 찾아 뒷자리(하이픈 뒤) 영역을 비율 좌표로 돌려준다."""
    out = []
    for i, pg in enumerate(doc):
        W, H = pg.rect.width, pg.rect.height
        for m in RRN.finditer(pg.get_text()):
            back = m.group(0).split("-")[1].strip()
            for r in pg.search_for(back):
                out.append((i + 1, ((r.x0 - 2) / W, (r.y0 - 2) / H, (r.x1 + 2) / W, (r.y1 + 2) / H)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--rect", action="append", default=[], help="쪽:x0,y0,x1,y1 (비율)")
    ap.add_argument("--preset", choices=sorted(PRESETS))
    ap.add_argument("--rrn", action="store_true", help="글자 층에서 주민번호 뒷자리를 찾아 가림")
    ap.add_argument("--dpi", type=int, default=200)
    ap.add_argument("--preview")
    a = ap.parse_args()

    src = fitz.open(a.src)
    rects = list(PRESETS.get(a.preset, []))
    for s in a.rect:
        p, xy = s.split(":")
        rects.append((int(p), tuple(float(v) for v in xy.split(","))))
    if a.rrn:
        found = rrn_rects(src)
        if not found:
            sys.exit("--rrn: 글자 층에서 주민번호를 찾지 못함(스캔 이미지 PDF면 --preset · --rect로)")
        rects += found
    if not rects:
        sys.exit("가릴 영역이 없음 — --preset · --rect · --rrn 중 하나")

    out = fitz.open()
    first = None
    for i, pg in enumerate(src):
        pix = pg.get_pixmap(dpi=a.dpi)
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        dr = ImageDraw.Draw(im)
        for p, (x0, y0, x1, y1) in rects:
            if p == i + 1:
                dr.rectangle([x0 * im.width, y0 * im.height, x1 * im.width, y1 * im.height], fill=(150, 150, 150))
        if first is None:
            first = im
        page = out.new_page(width=pg.rect.width, height=pg.rect.height)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=90)
        page.insert_image(page.rect, stream=buf.getvalue())
    out.save(a.dst, garbage=4, deflate=True)
    if a.preview and first is not None:
        first.save(a.preview)
    print(f"가림 {len(rects)}곳 · {len(out)}쪽 → {a.dst}" + (f" · 미리보기 {a.preview}" if a.preview else ""))


if __name__ == "__main__":
    main()
