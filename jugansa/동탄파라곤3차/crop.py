# -*- coding: utf-8 -*-
"""2-1 네이티브 페이지용 사진·서류 자르기 → assets_ins/<이름>.jpg (깃 제외: 증빙·사진 원본 포함)

통합제안서 기본틀에서 '실제 사진'만 영역을 지정해 잘라낸다(글자·장식·AI 그림은 넣지 않는다).
  python crop.py base <이름> <쪽 index(0부터)> <x0> <y0> <x1> <y1> [--dpi 220]
      · 좌표는 PDF pt(페이지 850×604). 쪽 index는 통합제안서 152쪽 기준 0부터.
증빙 원본 PDF(사업자등록증 등)는 한 쪽 통째로 또는 영역 지정:
  python crop.py ev <이름> <증빙파일명.pdf> <쪽 index> [x0 y0 x1 y1] [--dpi 170] [--mask-roster]
      · --mask-roster: 4대보험 명부 성명 가운데 글자·주민번호 성별자리 '*' 처리 후 렌더
목록 보기:
  python crop.py info <쪽 index>   # 그 쪽의 이미지 배치(bbox)·글자 블록 좌표 출력

환경변수 BASE_PDF(기본: 세션 스크래치패드의 152p 제출본), EVIDENCE_DIR 로 경로 변경 가능.
"""
import io
import os
import sys

import pymupdf as fitz
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets_ins")
SP = "/tmp/claude-0/-home-user-edge-company/a96d9eb6-5244-5d3f-9f1b-6f379ac2a82c/scratchpad"
BASE_PDF = os.environ.get("BASE_PDF", os.path.join(SP, "out2", "엣지컴퍼니_통합제안서_전체_152p_제출용.pdf"))
EVIDENCE_DIR = os.environ.get("EVIDENCE_DIR", os.path.join(SP, "evidence"))
MAXW = 2000


def save(pix, name):
    im = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
    if im.width > MAXW:
        im = im.resize((MAXW, round(im.height * MAXW / im.width)), Image.LANCZOS)
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name + ".jpg")
    im.save(path, quality=88)
    print(f"saved {path} {im.width}x{im.height}")


def opt(flag, default):
    if flag in sys.argv:
        v = sys.argv[sys.argv.index(flag) + 1]
        return type(default)(v)
    return default


def main():
    cmd = sys.argv[1]
    if cmd == "info":
        p = fitz.open(BASE_PDF)[int(sys.argv[2])]
        print("page", p.rect)
        for b in p.get_image_info(xrefs=True):
            print("IMG", [round(v) for v in b["bbox"]], b["width"], "x", b["height"])
        for b in p.get_text("blocks"):
            if b[4].strip():
                print("TXT", [round(v) for v in b[:4]], b[4].strip().replace("\n", " / ")[:70])
        return
    if cmd == "base":
        name, idx = sys.argv[2], int(sys.argv[3])
        rect = fitz.Rect(*map(float, sys.argv[4:8]))
        p = fitz.open(BASE_PDF)[idx]
        save(p.get_pixmap(dpi=opt("--dpi", 220), clip=rect), name)
        return
    if cmd == "ev":
        name, fn, idx = sys.argv[2], sys.argv[3], int(sys.argv[4])
        doc = fitz.open(os.path.join(EVIDENCE_DIR, fn))
        if "--mask-roster" in sys.argv:
            sys.path.insert(0, HERE)
            from mask_roster import mask
            mask(doc, rrn=True)
        p = doc[idx]
        nums = [a for a in sys.argv[5:9] if not a.startswith("--")]
        clip = fitz.Rect(*map(float, nums)) if len(nums) == 4 else None
        save(p.get_pixmap(dpi=opt("--dpi", 170), clip=clip), name)
        return
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
