# -*- coding: utf-8 -*-
"""업성 푸르지오 레이크시티 1BL — 공고 5항 '제안서 기재사항' 가 ~ 자 순서로 장 재배치(build_eo.py build()에서 emit 직전 apply(globals())).

장 순서(인계 '제안서 장' 표 그대로)
  앞  : 표지 · 5항 가 ~ 자 한 장 요약(00 공고 대응) · 목차 · 약속 10 · 3항 · 4항 대응표 · 7항 제출서류 대응표 · 단지 · 먼저 묻는 다섯 가지
  01장 가 회사 · 실적 · 인력      02장 나 일정 · 품목 · 업체 선정 · 교체   03장 다 대표 품목 가격 · 총 부담액
  04장 라 가격 확정 시점 · 비교    05장 마 입점비 · 수수료 · 광고비 · 발전기금   06장 바 계약 · 대금 · 취소 · 환불
  07장 사 민원 · 지연 · 폐업 · 추가 책임   08장 아 보험 · 보증   09장 자 카페 · 개인정보 · 재위탁 · 인계
  10   부록 입주박람회 운영계획(안)(3항 마 · 개최 여부 · 횟수 · 장소 · 비용은 별도) · 경관조명 진단 · 핵심 제안
공고 범위 밖 장(협의회 업무지원 · 시공 단계 점검 · 위임장 · 단지지원 컨설팅 등)은 DROP에 이름을 적어 뺀다(이름이 없으면 멈춤).
"""

S_FRONT = "제안 개요"

# 공고(3항 업무 범위)에 없는 업무 · 다른 단지 틀에서 온 장 — 뺀다(새 약속 · 비용 노출 방지)
DROP = ["part:[[협의회 업무지원]]", "part:[[구조·시공 품질]] 점검", "보이지 않는 [[하자]]까지 확인합니다", "part:[[보고서 샘플]]",
        "위임장, 이제 [[휴대폰으로]] 받습니다", "사전점검 [[언박싱 영상]]과 현장 홍보", "part:[[단지지원 컨설팅]]", "part:[[조명 개선]]",
        "part:특화서비스 요약 ①", "part:특화서비스 요약 ②", "part:특화서비스 요약 ③", "part:행사 밖에서도", "part:[[입주민 특화서비스]]",
        "part:[[A · B · C]] 구성 항목", "part:12개 지사망", "사전점검 당일 [[현장 지원]]", "입주민 후기 · [[실시간 응대]] 화면",
        "part:정회원 혜택 [[상세]]", "박람회 상품권 [[사용 안내]]",
        "kind:landscape", "part:경관조명 [[진단 · 제안]]", "part:[[조명 수직계열화]]"]   # 검수 11-02: 경관조명 4쪽 → 1쪽


def apply(G):
    B = G["B"]
    OLD = list(B.PAGES)
    used = set()

    def find(title=None, kind=None, part=None):
        if kind is not None:
            hits = [i for i, (k, kw) in enumerate(OLD) if k == kind]
        elif part is not None:
            hits = [i for i, (k, kw) in enumerate(OLD) if part in (kw.get("title") or "")]
        else:
            hits = [i for i, (k, kw) in enumerate(OLD) if kw.get("title") == title]
        assert len(hits) == 1, ("업성 재배치: 장을 찾지 못함 · 여러 개", title, kind, part, len(hits))
        assert hits[0] not in used, ("업성 재배치: 같은 장 두 번", title, kind, part)
        return hits[0]

    def T(x):
        i = find(kind=x[5:]) if x.startswith("kind:") else find(part=x[5:]) if x.startswith("part:") else find(title=x)
        used.add(i)
        k, kw = OLD[i]
        return k, dict(kw)

    for x in DROP:
        used.add(find(kind=x[5:]) if x.startswith("kind:") else find(part=x[5:]) if x.startswith("part:") else find(title=x))

    pages = [T("kind:cover"), T(G["T_ONE"]), T("kind:toc")] + [T(G[x]) for x in ["T_PROM", "T_MAPA", "T_DOCS", "T_SITE", "T_VOICE"]]
    for _k, kw in pages:
        if "sec" in kw:
            kw["sec"] = S_FRONT

    CH = {
        "ch1": [G["T_QUAL"], "숫자로 보는 [[엣지컴퍼니]]", G["T_HIST"], "part:운영 · 자본금 2억", "회사 개요와 [[법인 서류]]", "part:[[증빙 원본]]",
                "공인된 [[자격과 신뢰]]", "제휴 · 면허 · 인증 [[원본 서류]]", G["T_RECS"], "1,000세대 이상 [[주관 단지]]", G["T_R500"],
                "part:주관 [[성공사례]]", "part:2023년 이후 수임 단지", "part:앞으로 주관할 단지", "실제 박람회 [[현장]]", "part:타 단지가 남긴",
                "part:여러 단지를 [[연속으로]]", G["T_PEOPLE"], "part:[[조직 구성]]", G["T_STAFF7"], G["T_PM"], "part:이어야 합니까"],
        "ch2": [G["T_MON1"], G["T_MON2"], "공동구매 [[품목]]을 한눈에", G["T_ITEMS"], G["T_OPT"], G["T_VENDORS"], "[[4단계]] 공개 심사 프로세스",
                "업체 [[심사 기준]]과 계약 원칙", G["T_LICENSE"], G["T_LOCAL"], "part:[[인근 지역업체]] 선정 원칙"],
        "ch3": [G["T_PRICE"], "kind:pricing"],
        "ch4": [G["T_CHECK"], "공동구매 단가를 지키는 [[4가지 장치]]", "[[최저가 차액 10배]] 보상"],
        "ch5": [G["T_INCOME"], "kind:hi_fund", G["T_FUNDCH"], G["T_SEP"], G["T_MENU"], "박람회 [[사은품 · 경품]]", "사전점검 대행, [[이렇게 봅니다]]"],
        "ch6": [G["T_CARE"], G["T_ESCROW"], "입주민 [[자금]]을 먼저 지킵니다", G["T_RULE1"], G["T_RULE2"]],
        "ch7": [G["T_AS"], "주관 [[콜센터]]와 선보상", "클레임 [[처리 흐름]]과 CRM 관리", "입주민 [[컴플레인]], 이렇게 해결합니다", G["T_DESK"],
                G["T_BOND"], "선보상 재원 · 하자 예치금 [[최대 1억원]]", "입주민을 지키는 [[3중 안전망]]", "part:[[특약이행각서]] (예시)",
                "part:[[보상 기준]] (예시)", "참여업체 [[하자보증]] 체계"],
        "ch8": [G["T_INS"], "계약이행 · 하자보증 [[24개월]]", "보증보험증권 [[제출과 확인]]"],
        "ch9": [G["T_CAFE"], "입예협 카페 [[홍보 콘텐츠]] 제작", G["T_PRIV"], G["T_TERMS"], G["T_REPORT"], G["T_ROLE"], G["T_FAIR"]],
        "app": [G["T_EXPOPLAN"], "입주박람회 [[운영 계획]]", "행사장 대관과 [[운영 준비]]", "part:박람회장 배치와 [[인원 운영]]", G["T_SAFE"], G["T_CANCEL"],
                "가족이 머무는 [[편의시설]]", "못 오셔도 [[괜찮습니다]]", G["T_LX"], G["T_CORE6"]],
    }
    for key, n, name, dtitle, bl in G["EVAL"] + [G["APPX"]]:
        sec = f"{n}. {name}"
        pages.append(("divider", dict(n=n, title=dtitle, bl=bl)))
        for x in CH[key]:
            k, kw = T(x)
            if k not in ("divider", "divider_lx"):
                kw["sec"] = sec
            pages.append((k, kw))
    pages += [T("kind:closing"), T("kind:contact")]

    # 버리는 장 — 옛 장 간지(5항 장 간지로 바뀜) · 경관조명 간지(부록 간지로 합침)
    drop = [i for i, (k, kw) in enumerate(OLD) if i not in used and k in ("divider", "divider_lx")]
    used.update(drop)
    left = [(OLD[i][0], OLD[i][1].get("title")) for i in range(len(OLD)) if i not in used]
    assert not left, f"업성 재배치에서 빠진 장: {left}"
    B.PAGES[:] = pages

    # 목차 = 한 줄에 장 하나(tocr) · 10줄(01 ~ 09 + 부록) — tocr CSS 순서: 열 k의 첫 칸 = k번째 · 둘째 칸 = k + 5번째
    toc = [(n, name, bl) for _k, n, name, _t, bl in G["EVAL"] + [G["APPX"]]]
    assert len(toc) == 10
    G["TOC4"][:] = [[toc[i], toc[i + 5]] for i in range(5)]
    G["TOC_CLS"] = "tocr"
    B.CSS += ".tocr .s{grid-template-columns:54px 330px 1fr!important}.tocr .s h3{white-space:nowrap;font-size:16.5px}"
    print(f"[업성 재배치] 5항 가 ~ 자 + 부록 · {len(pages)}쪽 · 버린 간지 {len(drop)} · 뺀 장 {len(DROP)}")
