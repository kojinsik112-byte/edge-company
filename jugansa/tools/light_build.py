# -*- coding: utf-8 -*-
"""다른 단지 밝은 버전(10-21 본부장 '고양부터 북수원 상주까지 밝은버전으로').

순서: 단지 빌더(build_xx.py --no-pdf)로 HTML을 만든 뒤
  python3 jugansa/tools/light_build.py <단지 폴더> [--no-pdf]
  ① 공통 문구 수정(common_fix · 탕정 법정 판결 기준) — 원래 HTML에도 써 둠 · 남은 위험 문구가 있으면 중단
  ② 탕정 밝은 시안과 같은 색 · 디자인 레이어(탕정푸르지오센터파크/tjlight.py · tjdesign.py)로 <이름>_밝은시안.html/pdf
제출서류 조립기(docs_xx.py)는 _밝은시안.pdf를 쓴다.
"""
import os
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
sys.path[:0] = [TOOLS, os.path.join(ROOT, "탕정푸르지오센터파크")]
import common_fix as CF  # noqa: E402

# 단지 폴더 → [(HTML 이름, 간지 띠 문서명)]
DOCS = {
    "고양창릉S5": [("입주박람회_주관사_제안서", "입주박람회 주관사 제안서"), ("요약제안서", "요약 제안서")],
    "북수원디에트르더리체2": [("입주박람회_주관사_제안서", "입주박람회 주관사 운영계획서"), ("요약제안서", "요약 제안서")],
    "상주자이르네": [("입주박람회_주관사_업무수행제안서", "입주박람회 주관사 업무 수행 제안서")],
}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    folder = args[0].rstrip("/").split("/")[-1]
    here = os.path.join(ROOT, folder)
    sys.path.insert(0, here)
    import data as D  # noqa: E402
    import tjlight  # noqa: E402
    site = D.SITE.get("name") or D.SITE["official"]
    for name, label in DOCS[folder]:
        src = os.path.join(here, f"엣지컴퍼니_{folder}_{name}.html")
        assert os.path.exists(src), ("HTML 없음 — 빌더 먼저", src)
        html = open(src, encoding="utf-8").read()
        html, rep = CF.fix(html)
        bad = CF.residue(html)
        print(f"[{name}] 문구 수정", sum(rep.values()), "곳", rep)
        assert not bad, ("남은 위험 문구", bad[:10])
        open(src, "w", encoding="utf-8").write(html)
        tjlight.light(src, src[:-5] + "_밝은시안.html", None, None, label, hh=D.SITE["households"], fund=D.FUND, site=site)


if __name__ == "__main__":
    main()
