# -*- coding: utf-8 -*-
"""다른 단지 밝은 버전(10-21 본부장 '고양부터 북수원 상주까지 밝은버전으로').

순서: 단지 빌더(build_xx.py --no-pdf)로 HTML을 만든 뒤
  python3 jugansa/tools/light_build.py <단지 폴더> [--no-pdf]
  ① 공통 문구 수정(common_fix · 탕정 법정 판결 기준) — 원래 HTML에도 써 둠 · 남은 위험 문구가 있으면 중단
  ② 탕정 밝은 시안과 같은 색 · 디자인 레이어(탕정푸르지오센터파크/tjlight.py · tjdesign.py)로 <이름>_밝은시안.html/pdf
제출서류 조립기(docs_xx.py)는 _밝은시안.pdf를 쓴다.
"""
import os
import re
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


def office3(doc):
    """10-22 본부장: '선정 후 30일 안 현장 사무소'는 무리 → 3단계안(선정 후 30일 전담 PM · 박람회 60일 전 사무소 · 입주 지정기간 상주 창구)."""
    doc = doc.replace("<b>선정 후 30일 안 현장 사무소 개설</b><p>전담 PM 배치 · 시공 품목은 인근 업체 우선 선정</p>",
                      "<b>박람회 60일 전 현장 사무소 개설</b><p>선정 후 30일 안 전담 PM 지정 · 입주 지정기간 단지 안 상주 창구(협의)</p>")
    assert "선정 후 30일 안 현장 사무소" not in doc, "옛 30일 사무소 문구 남음"
    # 10-22 탕정 법정 판결 공통분(고양 · 북수원부터): 지사망 → 협력 네트워크 · 이행보증 2년 이상 · 무상 A/S 정의 · 주말 회신
    S = "[\\s\u00a0\u2060]*·[\\s\u00a0\u2060]*"
    for a_, b_ in [(r"직영 4곳 \+ 협력 8곳 = <em>전국 12개 지사망</em>", "직영 4곳 + <em>협력 네트워크 8곳</em>"),
                   (r"전국 12개 지사망", "직영 4곳 + 협력 네트워크 8곳"), (rf"12개 지사망{S}직영 4곳", "직영 4곳 + 협력 네트워크 8곳"),
                   (r"이 지키는 12개 지사망", "이 책임지는 전국 네트워크"), (rf"지사망({S})직영 운영", r"직영 거점\1협력 네트워크"),
                   (r"전국 지사망", "직영 거점 + 협력 네트워크"), (r"권역별 협력 지사", "권역별 협력 네트워크"),
                   (r"이행보증보험\((2년) · ", r"이행보증보험(\1 이상 · "), (r"이행보증보험 2년(?! 이상)", "이행보증보험 2년 이상"),
                   (rf"무상 A/S 최소 2년\(업체{S}품목별 상이\)", "무상 A/S 시공 품목 최소 2년 · 브랜드는 제조사 보증"),
                   (r"24시간 이내 회신(?!\()", "24시간 이내 회신(주말 · 공휴일 접수는 다음 영업일 12시까지)")]:
        doc = re.sub(a_, b_, doc)
    assert "지사망" not in re.sub(r"<[^>]+>", "", doc), "지사망 표현 남음"
    return doc


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
        tjlight.light(src, src[:-5] + "_밝은시안.html", None, None, label, hh=D.SITE["households"], fund=D.FUND, site=site, post=office3)


if __name__ == "__main__":
    main()
