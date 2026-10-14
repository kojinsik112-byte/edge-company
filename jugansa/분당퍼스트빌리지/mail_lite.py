# -*- coding: utf-8 -*-
"""메일 첨부용 경량본 — 빌드된 제안서 HTML이 쓰는 사진(assets_ins · 요약제안서/assets)을 줄여 임시 폴더에서 다시 인쇄한다.

공고 3항 'PDF 이메일 접수' — 원본 PDF(약 59MB)는 일반 메일 첨부 한도를 넘어 대용량 링크로 갈 수 있다(9항 2 접수방법 시비).
→ 같은 HTML · 같은 쪽수로 사진 해상도만 낮춘 '_메일용.pdf'를 만든다(목표 20MB 이하). 원본 PDF는 보관함에 둔다. 탕정 메일용 경량본과 같은 방식.

사용: python3 build_bd.py && python3 mail_lite.py [최대 픽셀(기본 1000)] [JPEG 품질(기본 72)]
- 기본 = 전체본 134쪽(build_bd.py 기본 출력 NAME.html) → NAME_메일용.pdf
- 압축본: python3 build_bd.py --compact && python3 mail_lite.py --compact → NAME_압축본_메일용.pdf
- 요약제안서: python3 mail_lite.py --summary → 엣지컴퍼니_분당퍼스트빌리지_14_요약제안서_메일용.pdf(원본이 작으면 생략 가능)
"""
import os
import re
import shutil
import sys
import tempfile

import pymupdf
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, "..", "요약제안서"))
sys.path[:0] = [BASE]
import build as B  # noqa: E402  (기본틀 — build_pdf()만 쓴다)

NAME = ("엣지컴퍼니_분당퍼스트빌리지_14_요약제안서" if "--summary" in sys.argv else
        "엣지컴퍼니_분당퍼스트빌리지_02_입주박람회_주관사_제안서" + ("_압축본" if "--compact" in sys.argv else ""))
TITLE = ("엣지컴퍼니 e편한세상 분당 퍼스트빌리지 요약제안서" if "--summary" in sys.argv else
         "엣지컴퍼니 e편한세상 분당 퍼스트빌리지 입주박람회 주관사 제안서")
SRC_HTML = os.path.join(HERE, NAME + ".html")
SRC_PDF = os.path.join(HERE, NAME + ".pdf")
OUT_PDF = os.path.join(HERE, NAME + "_메일용.pdf")
LIMIT_MB = 20


def shrink(src, dst, px, q):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im = Image.open(src)
    im.thumbnail((px, px))
    if src.lower().endswith((".jpg", ".jpeg")):
        im.convert("RGB").save(dst, quality=q, optimize=True, progressive=True)
    else:
        im.save(dst, optimize=True)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    px = int(args[0]) if len(args) > 0 else 1000
    q = int(args[1]) if len(args) > 1 else 72
    html = open(SRC_HTML, encoding="utf-8").read()
    tmp = tempfile.mkdtemp(prefix="bd_mail_")
    try:
        work = os.path.join(tmp, "bd")  # HTML 위치(…/bd) 기준 상대 경로를 그대로 살린다
        os.makedirs(work)
        for ref in sorted(set(re.findall(r"""(?:src=["']|url\(["']?)([^"')]+\.(?:jpe?g|png))""", html))):
            src = os.path.normpath(os.path.join(HERE, ref))
            dst = os.path.normpath(os.path.join(work, ref))
            assert os.path.exists(src), ref
            shrink(src, dst, px, q)
        # SVG 도식(09장 경관조명 설계 · 생산 · 시공 · 야경)은 원본 그대로 복사 — 빠지면 메일용에서 그림이 비었다(10-14 확인)
        for ref in sorted(set(re.findall(r"""(?:src=["']|url\(["']?)([^"')]+\.svg)""", html))):
            src = os.path.normpath(os.path.join(HERE, ref))
            dst = os.path.normpath(os.path.join(work, ref))
            assert os.path.exists(src), ref
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src, dst)
        fonts =os.path.join(BASE, "assets", "fonts")  # 글꼴은 원본 그대로
        if os.path.isdir(fonts):
            shutil.copytree(fonts, os.path.join(tmp, "요약제안서", "assets", "fonts"), dirs_exist_ok=True)
        h = os.path.join(work, NAME + ".html")
        open(h, "w", encoding="utf-8").write(html)
        B.OUT_HTML, B.OUT_PDF = h, h[:-5] + ".pdf"
        B.build_pdf()
        d = pymupdf.open(B.OUT_PDF)
        n0 = len(pymupdf.open(SRC_PDF)) if os.path.exists(SRC_PDF) else None
        assert n0 is None or len(d) == n0, ("쪽수가 원본과 다름", len(d), n0)
        d.set_metadata({"title": TITLE, "author": "주식회사 엣지컴퍼니"})
        d.save(OUT_PDF, garbage=4, deflate=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    mb = os.path.getsize(OUT_PDF) / 1e6
    print(f"{OUT_PDF} · {len(pymupdf.open(OUT_PDF))}쪽 · {mb:.1f}MB" + ("" if mb <= LIMIT_MB else f"  ※ {LIMIT_MB}MB 초과 — 픽셀·품질을 낮춰 다시 실행"))


if __name__ == "__main__":
    main()
