# -*- coding: utf-8 -*-
"""통합제안서 08.수임실적 장 단지명·세대수 정정(본부장 확정 2026-10-05) — 기본틀 위 덧패치, 새 버전 파일로 저장.

기준표: suim/SPEC.md · 쪽별 수정: suim/p<idx>.py 의 fix(page)
사용: python suim_fix.py <통합제안서_152p.pdf> <출력.pdf> [--pages-only <검토용.pdf>]
출력 PDF는 개인정보(4대보험 명부 등)가 들어 있으므로 깃에 올리지 않는다.
"""
import importlib
import os
import sys

import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE]
import fix_all as F  # noqa: E402

PAGES = [21, 22, 23, 24, 25, 26, 27, 28, 31]


def main():
    src, dst = sys.argv[1], sys.argv[2]
    d = fitz.open(src)
    done = []
    for idx in PAGES:
        if not os.path.exists(os.path.join(HERE, "suim", f"p{idx}.py")):
            continue
        importlib.import_module(f"suim.p{idx}").fix(d[idx])
        done.append(idx)
    d.save(dst, garbage=3, deflate=True)
    print("saved", dst, f"{os.path.getsize(dst) / 1e6:.1f}MB", "patched", done)
    if "--pages-only" in sys.argv:
        out = fitz.open()
        for idx in done:
            out.insert_pdf(d, from_page=idx, to_page=idx)
        po = sys.argv[sys.argv.index("--pages-only") + 1]
        out.save(po, garbage=4, deflate=True)
        print("saved", po)
    print("\n".join(F.LOG))


if __name__ == "__main__":
    main()
