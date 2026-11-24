"""영주자이 4공종 카톡 전송용 JPG (페이지별).

회장 지시(2026-11-24): 문주·정원·요정의 숲·수직경관 4개 전부, 톡에 올리게 페이지별 JPG로.
출력: 바탕화면\\경관조명 관련\\영주자이 자료\\카톡용 JPG\\
  0_문주+정원 묶음 견적 (950만)\\  — 공무팀 묶음 견적서 전 쪽
  1~4_<공종>\\                      — 01_소개(사진 페이지) + 02~ 견적서 쪽별
105동은 기본안(ㄷ자·12V) 견적만 넣는다(1줄·24V 대안 제외 — 입예협이 깎을 빌미 차단 방침).
제안서(yeongju_proposal.py)를 먼저 빌드해 둬야 사진 수정본·품목 크롭이 있다.
실행: python 경관조명/tools/yeongju_kakao.py
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import yeongju_build as yb  # noqa: E402
import yeongju_package as pk  # noqa: E402

OUT = yb.OUT.parent / "카톡용 JPG"
DPI = 200  # A4 → 1654×2339px, 확대해도 견적서 글자가 읽히는 해상도
SETS = [  # (폴더 이름, 테마, 견적 키)
    ("1_하늘에 새긴 빛 (105동 수직경관)", "하늘에 새긴 빛", "1_하늘에새긴빛_ㄷ자_12V"),
    ("2_겨울빛의 문 (정문 문주)", "겨울빛의 문", "2_겨울빛의문_정문문주"),
    ("3_별빛이 머무는 정원 (잔디 정원)", "별빛이 머무는 정원", "3_별빛이머무는정원"),
    ("4_요정의 숲 (소나무 숲)", "요정의 숲", "4_요정의숲"),
]
BUNDLE_DIR = "0_문주+정원 묶음 견적 (950만)"
BUNDLE_LABELS = ["표지", "겨울빛의 문", "별빛이 머무는 정원", "묶음 견적"]


def save_pages(pdf: Path, folder: Path, labels: list[str], start: int = 1) -> int:
    with fitz.open(pdf) as d:
        for n, pg in enumerate(d):
            pix = pg.get_pixmap(dpi=DPI)
            im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            im.save(folder / f"{start + n:02d}_{labels[n]}.jpg", quality=90, optimize=True)
        return d.page_count


def main():
    pk.main()  # 묶음 견적서 최신화
    hdir = yb.OUT / "_html"
    img_dir = hdir / "pkg_img"
    quotes = {q["key"]: q for q in yb.QUOTES}
    OUT.mkdir(parents=True, exist_ok=True)

    # 0) 공무팀 묶음 견적
    bdir = OUT / BUNDLE_DIR
    shutil.rmtree(bdir, ignore_errors=True)
    bdir.mkdir()
    bundle = yb.OUT / f"{pk.NAME}.pdf"
    with fitz.open(bundle) as d:
        n = d.page_count
    labels = BUNDLE_LABELS + [f"별첨 세부견적_{i + 1}" for i in range(n - len(BUNDLE_LABELS))]
    print(f"{BUNDLE_DIR}: {save_pages(bundle, bdir, labels)}장")

    # 1~4) 공종별 — 사진 소개 1쪽 + 견적서
    for folder, theme, key in SETS:
        fdir = OUT / folder
        shutil.rmtree(fdir, ignore_errors=True)
        fdir.mkdir()
        tag = key.split("_")[0]
        hp = hdir / f"카톡_{tag}_소개.html"
        hp.write_text(pk.html_doc(pk.theme_section(theme, img_dir), f"{theme} 소개"), encoding="utf-8")
        intro = hdir / f"카톡_{tag}_소개.pdf"
        yb.to_pdf(hp, intro)
        qp = hdir / f"카톡_{tag}_견적서.html"
        qp.write_text(yb.quote_html(quotes[key]), encoding="utf-8")
        qpdf = hdir / f"카톡_{tag}_견적서.pdf"
        yb.to_pdf(qp, qpdf)
        a = save_pages(intro, fdir, ["소개"])
        with fitz.open(qpdf) as d:
            qn = d.page_count
        b = save_pages(qpdf, fdir, [f"견적서_{i + 1}" for i in range(qn)], start=a + 1)
        print(f"{folder}: 소개 {a} + 견적서 {b} = {a + b}장 (공급가 {yb.calc(quotes[key])['supply']:,})")
    print("OK ->", OUT)


if __name__ == "__main__":
    main()
