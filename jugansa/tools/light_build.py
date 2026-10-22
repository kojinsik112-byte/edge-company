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


# 10-22 본부장(2차): 경인 지사(평택 · 쇼룸 · 입예협 미팅 공간) 추가 → 현장 사무소 개설 약속 삭제 · 지역 거점 5곳 + 협력 네트워크 7곳(수도권 단지)
KYEONGIN = {"고양창릉S5", "북수원디에트르더리체2"}
FOLDER = ""
# 지원금 '전 세대 고정 총액' 대신 '계약 세대 · 최대 총액'으로 적는 단지(폴더 → 세대수 표기) — 10-22 북수원 착수 분석
CONTRACT_BASIS = {}   # 북수원은 본부장 10-22 저녁 '전 세대'로 되돌림(업체 110곳 · 최소 100 · 4,000㎡ 단일 홀 → 전 세대 약속도 +1.3 ~ 1.7억) — 다시 쓰려면 {"북수원디에트르더리체2": "1,744"}


def office3(doc):
    """10-22 본부장: '선정 후 30일 안 현장 사무소'는 무리 → 3단계안(선정 후 30일 전담 PM · 박람회 60일 전 사무소 · 입주 지정기간 상주 창구).
    수도권 단지(KYEONGIN)는 사무소 대신 경인 지사 거점."""
    ky = FOLDER in KYEONGIN
    doc = doc.replace("<b>선정 후 30일 안 현장 사무소 개설</b><p>전담 PM 배치 · 시공 품목은 인근 업체 우선 선정</p>",
                      "<b>경인 지사(평택) 거점</b><p>선정 후 30일 안 전담 PM 지정 · 쇼룸 상담 · 입예협 미팅 공간 · 시공 · A/S 출동 · 입주 지정기간 단지 안 상주 창구(협의)</p>" if ky else
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
    if ky:
        for a_, b_ in [(r"직영 거점 4곳", "지역 거점 5곳"), (r"직영 4곳", "지역 거점 5곳"), (r"협력 네트워크 8곳", "협력 네트워크 7곳"),
                       (r"협력 8곳", "협력 7곳"), (r"직영은 <em>책임 주체가 바뀌지 않습니다\.</em>", "거점이 있으면 <em>책임 주체가 바뀌지 않습니다.</em>")]:
            doc = re.sub(a_, b_, doc)
        _left = re.findall(r".{0,20}(?:현장 사무소|사무소 개설|60일 전|직영 4곳|직영 거점 4|협력 네트워크 8|협력 8곳|4 \+ 8|12개 지사).{0,20}",
                           re.sub(r"<[^>]+>", " ", re.sub(r"<style.*?</style>|<script.*?</script>", "", doc, flags=re.S)))
        assert not _left, f"경인 지사 반영 전 문구 남음 {_left[:5]}"
    return doc


def contract(doc):
    """10-22 착수 분석(북수원 청약 31% · 손익 본전 79곳): 세대당 금액은 그대로, 지원 대상 = 계약 세대 · 총액은 '최대'.
    tjlight.light(final=) — 디자인 레이어(15만원 증서)까지 끝난 뒤 실행."""
    S = "[\\s\u00a0\u2060]*·[\\s\u00a0\u2060]*"
    hh = CONTRACT_BASIS[FOLDER]
    for a_, b_ in [(r"<b>전 세대 " + hh + r"세대</b><small>전 세대 동일 기준</small>", "<b>분양 계약 세대 모두</b><small>입주 지정기간 전 계약 · 같은 기준</small>"),
                   (r"<i>총 규모</i><b>([^<]+?) 상당</b><small>(" + hh + r"세대) × (\d+)만원", r"<i>총 규모</i><b>최대 \1 상당</b><small>\2 모두 계약 시 × \3만원"),
                   (r"(?:<em>)?전 세대 " + hh + r"세대(?:</em>)? × 세대당 (\d+)만원 상당 = <em>총? ?([^<]+?) 상당</em>",
                    r"<em>분양 계약을 마친 모든 세대</em> × 세대당 \1만원 상당 · <em>최대 \2 상당</em>(" + hh + "세대 모두 계약 시)"),
                   (hh + rf"세대({S})세대당 (\d+)만원 상당({S})총 ", r"계약 세대 모두\1세대당 \2만원 상당\3최대 "),
                   (r"같은 금액\(([^)]+?) 상당\)", r"같은 금액(최대 \1 상당 · 계약 세대 기준)"),
                   (r"상당\(총 ([^)]+?)\)", r"상당(최대 \1 · 계약 세대 기준)"),
                   (r"전 세대 " + hh + rf"세대 기준({S})총 ", r"계약 세대 기준\1최대 "),
                   (hh + rf"세대({S})총 ", r"계약 세대 기준\1최대 "),
                   (hh + rf"세대 전 세대({S})총 ", r"계약 세대 모두\1최대 "),
                   (r"총 (\d억 [\d,]+만원)(?![^<]{0,12}계약 세대)", r"최대 \1(계약 세대 기준)"),
                   (r"모두 계약 시\)\(부가세 포함\)", "모두 계약 시 · 부가세 포함)")]:
        doc = re.sub(a_, b_, doc)
    _t = re.sub(r"<[^>]+>", " ", re.sub(r"<style.*?</style>|<script.*?</script>", "", doc, flags=re.S))
    _left = re.findall(r".{0,20}(?:전 세대 " + hh + r"세대|총 \d억 [\d,]+만원).{0,20}", _t)
    assert not _left, f"지원 대상 '계약 세대' 반영 전 문구 남음 {_left[:5]}"
    return doc


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    folder = args[0].rstrip("/").split("/")[-1]
    global FOLDER
    FOLDER = folder
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
        tjlight.light(src, src[:-5] + "_밝은시안.html", None, None, label, hh=D.SITE["households"], fund=D.FUND, site=site, post=office3,
                     final=contract if folder in CONTRACT_BASIS else None)


if __name__ == "__main__":
    main()
