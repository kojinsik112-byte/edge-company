# -*- coding: utf-8 -*-
"""신분평 더웨이시티 제일풍경채 — 평가표 8항목 순서로 장 재배치(build_sb.py build()에서 emit 직전 apply(globals())).

장 순서 = 공고 '사. 평가 기준' 순서(평가위원이 채점표를 위에서부터 넘기며 같은 순서로 찾도록 · 경산 gs.py 방식)
  앞  : 표지 · 한 장 요약 · 목차 · 약속 10 · 바 1) ~ 7) 대응표 2쪽 · 다 1) ~ 8) 수행 업무 · 단지 · 먼저 묻는 다섯 가지
  01장: 입주예정자 구매 혜택      02장: 소비자 보호 및 사후관리   03장: 각종 서류 및 가격요건   04장: 행사 운영 능력
  05장: 협력업체 구성 및 관리     06장: 최근 지역 내 사업 실적    07장: 운영 및 정산 투명성     08장: 협의회 업무지원 계획
  09장: 차별화 · 요약(경관조명 · 단지지원 컨설팅 · 특화서비스 요약)
배점은 머리띠 · 간지 · 목차 · 한 장 요약에 쓰지 않는다(경산 본부장 10-30 '빼자'와 같게 — 항목 이름 · 순서만).
빠진 장이 있으면 멈춘다(재배치에서 빠진 장 = 목록에 이름을 넣거나 drop에 넣는다).
"""

S_FRONT = "제안 개요"


def apply(G):
    B, D = G["B"], G["D"]
    OLD = list(B.PAGES)
    used = set()

    def take(title=None, kind=None, part=None):
        if kind is not None:
            hits = [i for i, (k, kw) in enumerate(OLD) if k == kind]
        elif part is not None:
            hits = [i for i, (k, kw) in enumerate(OLD) if part in (kw.get("title") or "")]
        else:
            hits = [i for i, (k, kw) in enumerate(OLD) if kw.get("title") == title]
        assert len(hits) == 1, ("신분평 재배치: 장을 찾지 못함 · 여러 개", title, kind, part, len(hits))
        assert hits[0] not in used, ("신분평 재배치: 같은 장 두 번", title, kind, part)
        used.add(hits[0])
        k, kw = OLD[hits[0]]
        return k, dict(kw)

    def T(x):
        return take(kind=x[5:]) if x.startswith("kind:") else take(part=x[5:]) if x.startswith("part:") else take(title=x)

    EVAL = G["EVAL"]
    pages = [T("kind:cover"), T(G["T_ONE"]), T("kind:toc")] + [T(G[x]) for x in ["T_PROM", "T_GL1", "T_GL2", "T_MAPA", "T_MAPB", "T_WORK", "T_SITE", "T_VOICE"]]
    for _k, kw in pages:
        if "sec" in kw:
            kw["sec"] = S_FRONT

    CH = {
        "ch1": ["kind:hi_fund", G["T_FUNDCH"], G["T_SEP"], "part:[[A · B · C]] 구성 항목", G["T_MENU"], G["T_PRICE"], G["T_CHECK"],
                "공동구매 단가를 지키는 [[4가지 장치]]", "[[최저가 차액 10배]] 보상",
                "part:[[입주민 특화서비스]]", "박람회 상품권 [[사용 안내]]", "part:정회원 혜택 [[상세]]", "박람회 [[사은품 · 경품]]",
                "사전점검 대행, [[이렇게 봅니다]]", "kind:pricing"],
        "ch2": [G["T_CARE"], "입주민 [[자금]]을 먼저 지킵니다", G["T_ESCROW"], G["T_RULE1"], G["T_RULE2"], G["T_AS"],
                "주관 [[콜센터]]와 선보상", "선보상 재원 · 하자 예치금 [[최대 1억원]]", "클레임 [[처리 흐름]]과 CRM 관리",
                "입주민 [[컴플레인]], 이렇게 해결합니다", "입주민 후기 · [[실시간 응대]] 화면", G["T_DESK"],
                "입주민을 지키는 [[3중 안전망]]", "part:[[특약이행각서]] (예시)", "part:[[보상 기준]] (예시)", G["T_BOND"]],
        "ch3": [G["T_QUAL"], G["T_DOCS"], "숫자로 보는 [[엣지컴퍼니]]", G["T_HIST"], "part:운영 · 자본금 2억", "회사 개요와 [[법인 서류]]",
                "part:[[증빙 원본]]", "공인된 [[자격과 신뢰]]", "제휴 · 면허 · 인증 [[원본 서류]]", G["T_PEOPLE"], "part:[[조직 구성]]", G["T_STAFF7"],
                "계약이행 · 하자보증 [[24개월]]", "보증보험증권 [[제출과 확인]]"],
        "ch4": [G["T_EXPOPLAN"], "입주박람회 [[운영 계획]]", "행사장 대관과 [[운영 준비]]", "part:박람회장 배치와 [[인원 운영]]", G["T_SAFE"], G["T_CANCEL"],
                "가족이 머무는 [[편의시설]]", "못 오셔도 [[괜찮습니다]]", G["T_MON1"], G["T_MON2"], G["T_RECS"], "1,000세대 이상 [[주관 단지]]", G["T_R500"],
                "part:주관 [[성공사례]]", "part:2023년 이후 수임 단지", "part:앞으로 주관할 단지", "실제 박람회 [[현장]]", "part:타 단지가 남긴", "part:행사 밖에서도"],
        "ch5": ["공동구매 [[품목]]을 한눈에", G["T_ITEMS"], G["T_OPT"], G["T_VENDORS"], "[[4단계]] 공개 심사 프로세스", "업체 [[심사 기준]]과 계약 원칙",
                G["T_LICENSE"], "참여업체 [[하자보증]] 체계"],
        "ch6": [G["T_LOCAL"], "part:[[인근 지역업체]] 선정 원칙", G["T_PM"], "part:여러 단지를 [[연속으로]]"],
        "ch7": [G["T_INCOME"], G["T_REPORT"], G["T_FAIR"]],
        "ch8": [G["T_SUP1"], G["T_SUP2"], G["T_ROLE"], G["T_REQ"], "part:[[협의회 업무지원]]", "part:[[구조·시공 품질]] 점검", "보이지 않는 [[하자]]까지 확인합니다",
                "part:[[보고서 샘플]]", "사전점검 당일 [[현장 지원]]", "위임장, 이제 [[휴대폰으로]] 받습니다", G["T_RATE"],
                "입예협 카페 [[홍보 콘텐츠]] 제작", "사전점검 [[언박싱 영상]]과 현장 홍보", G["T_PRIV"], G["T_TERMS"]],
    }
    for key, n, name, dtitle, bl in EVAL:
        sec = f"{n}. {name}"
        pages.append(("divider", dict(n=n, title=dtitle, bl=bl)))
        for x in CH[key]:
            k, kw = T(x)
            if k not in ("divider", "divider_lx"):
                kw["sec"] = sec
            pages.append((k, kw))

    # 09장 차별화 · 요약
    S9 = "09. 차별화 · 요약"
    pages.append(("divider", dict(n="09", title=G["T_CH9"], bl=["단지지원 컨설팅(협의회 요청 시)", "외부 경관조명 진단", "조명 설계 · 생산 · 시공", "핵심 제안 6가지"])))
    for x in ["part:[[단지지원 컨설팅]]", "part:[[조명 개선]]", G["T_LX"], "kind:landscape", "part:경관조명 [[진단 · 제안]]", "part:[[조명 수직계열화]]", G["T_CORE6"]]:
        k, kw = T(x)
        kw["sec"] = S9
        pages.append((k, kw))
    pages += [T("kind:contact")]
    # 본부장 11-04 '중복 줄이자': 앞쪽 요약을 되풀이하는 6쪽은 뺌(지사 설명 2 · 특화서비스 요약 3 · 마무리 1) — 쪽 번호 참조 없음
    for x in ["part:12개 지사망", "part:이어야 합니까", "part:특화서비스 요약 ①", "part:특화서비스 요약 ②", "part:특화서비스 요약 ③", "kind:closing"]:
        T(x)

    # 버리는 장 — 옛 장 간지(평가표 장 간지로 바뀜) · 경관조명 간지(09장 간지로 합침)
    drop = [i for i, (k, kw) in enumerate(OLD) if i not in used and k in ("divider", "divider_lx")]
    used.update(drop)
    left = [(OLD[i][0], OLD[i][1].get("title")) for i in range(len(OLD)) if i not in used]
    assert not left, f"신분평 재배치에서 빠진 장: {left}"
    B.PAGES[:] = pages

    # 목차 = 한 줄에 장 하나(tocr) · 10줄(제안 개요 + 01 ~ 09) — tocr CSS 순서: 열 k의 첫 칸 = k번째 · 둘째 칸 = k + 5번째
    toc = [("00", "제안 개요", ["한 장 요약 · 약속 10 · 혜택표", "필수 포함 사항 바 1) ~ 7)", "수행 업무 다 1) ~ 8)", "단지 · 먼저 묻는 다섯 가지"])]
    toc += [(n, name, bl) for _k, n, name, _t, bl in EVAL]
    toc += [("09", "차별화 · 요약", ["단지지원 컨설팅", "외부 경관조명 진단", "조명 설계 · 생산 · 시공", "핵심 제안 6가지"])]
    assert len(toc) == 10
    G["TOC4"][:] = [[toc[i], toc[i + 5]] for i in range(5)]
    G["TOC_CLS"] = "tocr"
    B.CSS += ".tocr .s{grid-template-columns:54px 212px 1fr!important}.tocr .s h3{white-space:nowrap}"  # 평가 항목 이름이 길어 둘째 칸을 넓힘
    print(f"[신분평 재배치] 평가표 8항목 순서 · {len(pages)}쪽 · 버린 간지 {len(drop)}")
