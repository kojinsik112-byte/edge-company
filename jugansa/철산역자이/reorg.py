# -*- coding: utf-8 -*-
"""철산역 자이 제안서 — 목차를 통합제안서 순서로 재배치(본부장 지시 2026-10-07).

01 회사소개 · 02 마케팅전략 · 03 업체선정 · 04 하자보증 · 05 주관 콜센터 · 06 입주박람회
· 07 철산역 자이 맞춤 제안 · 08 혜택안내 · 09 차별화 포인트 · 10 특화서비스 요약 → 약속 · 연락처

08 혜택안내 원칙(본부장 10-07)
- 박람회 기본 혜택(상품권·정회원·사은품·경품)은 방문 세대 모두에게 — 15만원과 별개
- 세대당 15만원 = ① 현금(조합 또는 입예협 공식 통장) 또는 ② 같은 금액 범위의 혜택 패키지 A·B·C 중 선택
  A 입주민 특화서비스 · B 협의회 단지발전지원 · C 단지지원 컨설팅 (통합제안서 혜택안내 구성)
- '8가지 무상 단지지원' 장 삭제(15만원 + 무상지원을 다 주는 것처럼 보이던 문제)
- 상품권은 2만원 쿠폰을 업체마다 1매씩 쓰는 구조 → 정회원 '60만원 상당'은 내세우지 않는다

build_cheolsan.py 끝(특수 페이지 함수 교체 뒤)에서 apply(globals()) 로 부른다 — NO_NATIVE 미리보기에서는 안 돎.
"""
import html as _h


def apply(G):
    B, D, sub, won = G["B"], G["D"], G["sub"], G["won"]
    P = B.PAGES
    t = B.t
    hh, fund = D.SITE["households"], D.FUND
    total = won(hh * fund)

    def take(title=None, kind=None):
        """제목(정확 일치 우선, 없으면 부분 일치 1건) 또는 kind 로 장 하나를 꺼낸다."""
        if kind and not title:
            hits = [p for p in P if p[0] == kind]
        else:
            hits = [p for p in P if p[1].get("title") == title] or [p for p in P if title in p[1].get("title", "")]
        assert len(hits) == 1, (title, kind, len(hits))
        return hits[0]

    def dv(n, title, bl):
        return ("divider", dict(n=n, title=title, bl=bl))

    # ------------------------------------------------ 문구 손질(장 이동 전)
    # 상품권 = 2만원 쿠폰, 업체마다 1매 (본부장 10-07)
    k = take("방문 세대 [[상품권 · 현장 혜택]]")[1]
    k["title"] = "방문 세대 [[박람회 상품권 · 현장 혜택]]"
    k["body"] = B.cards([
        dict(lb="GIFT 01", big="2", unit="만원권", nm="박람회 상품권(쿠폰)",
             ds="계약하는 업체마다 1매씩 2만원 할인. 일반회원 20만원분, 정회원은 10만원분 추가."),
        dict(lb="GIFT 02", big="+5", unit="만원", nm="특정 입주민 추가 쿠폰",
             ds="소년·소녀가장, 80세 이상 노부모 부양, 장애인, 다자녀(3자녀↑), 다문화, 임산부."),
        dict(lb="GIFT 03", big="백화점", nm="백화점 상품권", ds="박람회 방문·신청 시 1세대 1회 교부. 행사장 안에서 현금처럼 사용."),
        dict(lb="GIFT 04", big="10", unit="%", nm="현장 특별할인", ds="박람회 기간 품목별 현장 할인 특가 최대 10% 추가할인."),
    ])
    k["kp"] = "상품권은 계약하는 업체마다 [[2만원씩]] 깎아 드리는 쿠폰입니다. 필요한 품목만 계약하셔도 됩니다."
    k = take("정회원 전용 [[세대당 60만원 상당]]")[1]
    k["title"] = "정회원 전용 [[추가 혜택]]"
    k["lead"] = "정회원으로 박람회에 방문하시면 아래 혜택을 더 받으실 수 있습니다."
    k["kp"] = ("정회원은 [[상품권 10만원분 추가]]와 품목별 특가를 더 받습니다.",
               "품목은 입예협 협의 후 확정 · 조합원 옵션과 겹치는 품목은 제외")
    # 특화 제안 03: 조명 점검은 C 패키지(단지지원 컨설팅) 항목 → '무상' 표기 삭제
    k = take("철산역 자이 [[특화 제안]]")[1]
    k["body"] = sub(k["body"], "경관·커뮤니티 조명 무상 점검", "경관·커뮤니티 조명 점검")
    k = take("전기차 충전 [[인프라 검토]]")[1]
    k["lead"] = sub(k["lead"], "충전기 설치 컨설팅을 무상으로 지원합니다.", "충전기 설치 컨설팅을 지원합니다.")
    k["body"] = sub(k["body"], "컨설팅은 무상이며, 충전기", "충전기")

    # 15만원 장: 현금 또는 패키지
    def p_hi_fund(no, sec):
        s = B_hi_fund(no, sec)
        s = sub(s, f"<em>공고 대상 조합 {hh:,}세대</em>를 기준으로 지급하고, <em>조합 또는 입예협 공식 통장</em>으로 입금합니다.",
                f"<em>공고 대상 조합 {hh:,}세대</em> 기준 — <em>현금</em> 또는 같은 금액 범위의 <em>혜택 패키지</em> 중 입예협이 고릅니다.")
        s = sub(s, "<span>현금성 지원 · 조합 또는 입예협 공식 통장 입금 가능</span><span>단지 시설 투자</span><span>협의회 활동 지원</span>",
                "<span>① 현금 — 조합 또는 입예협 공식 통장 입금</span><span>② 혜택 패키지 A · B · C</span>")
        return s
    B_hi_fund = B.p_hi_fund
    B.p_hi_fund = p_hi_fund

    # ------------------------------------------------ 08장 신설 장
    B.CSS += r"""
.optx{display:grid;grid-template-columns:1fr 70px 1fr;align-items:stretch;flex:1;min-height:0}
.optx .op{border:1px solid var(--line);border-radius:16px;padding:26px 32px;display:flex;flex-direction:column;justify-content:center;
  background:linear-gradient(180deg,rgba(255,255,255,.075),rgba(255,255,255,.015))}
.optx .op.hl{border-color:rgba(235,203,143,.75);background:linear-gradient(180deg,rgba(235,203,143,.15),rgba(235,203,143,.03))}
.optx .op i{font-style:normal;font-size:13px;font-weight:700;letter-spacing:.26em;color:var(--gold2)}
.optx .op h3{font-size:30px;font-weight:800;margin:8px 0 10px}
.optx .op .v{font-size:46px;font-weight:800;color:var(--gold);line-height:1.1;font-variant-numeric:tabular-nums}
.optx .op .v small{font-size:20px;margin-left:4px}
.optx .op ul{margin:14px 0 0;padding:0;list-style:none}
.optx .op li{font-size:17px;color:var(--sub);line-height:1.6;padding-left:16px;position:relative}
.optx .op li:before{content:'·';position:absolute;left:2px;color:var(--gold2)}
.optx .or{display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:800;color:var(--gold)}
.basex{border:1px dashed rgba(200,168,106,.55);border-radius:12px;padding:12px 20px;font-size:16px;color:var(--sub);line-height:1.5}
.basex b{color:var(--ink)}
.pkx{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;flex:1;min-height:0}
.pkx .pk{border:1px solid var(--line);border-radius:14px;padding:16px 20px;display:flex;flex-direction:column;min-height:0;
  background:linear-gradient(180deg,rgba(255,255,255,.07),rgba(255,255,255,.015))}
.pkx .pk .hd2{display:flex;align-items:center;gap:12px;padding-bottom:10px;border-bottom:1.5px solid rgba(200,168,106,.5);margin-bottom:6px}
.pkx .pk .L{width:40px;height:40px;border-radius:50%;background:var(--gold);color:#0d1e33;font-weight:800;font-size:22px;
  display:flex;align-items:center;justify-content:center;flex:none}
.pkx .pk h3{font-size:20px;font-weight:800;line-height:1.2}
.pkx .pk h3 small{display:block;font-size:12.5px;color:var(--mute);font-weight:500;margin-top:3px}
.pkx .pk ul{list-style:none;margin:0;padding:0}
.pkx .pk li{font-size:14.5px;color:var(--sub);line-height:1.32;padding:4px 0;border-bottom:1px dashed rgba(255,255,255,.12)}
.pkx .pk li:last-child{border-bottom:0}
.pkx .pk li b{color:var(--ink);font-weight:700}
.exx{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;flex:1;min-height:0}
.exx .ex{border:1px solid var(--line);border-radius:14px;padding:16px 18px;display:flex;flex-direction:column;
  background:linear-gradient(180deg,rgba(255,255,255,.07),rgba(255,255,255,.015))}
.exx .ex.cash{border-style:dashed}
.exx .ex i{font-style:normal;font-size:12px;font-weight:700;letter-spacing:.22em;color:var(--gold2)}
.exx .ex h3{font-size:21px;font-weight:800;margin:6px 0 4px}
.exx .ex p.w{font-size:14px;color:var(--mute);line-height:1.45;margin-bottom:10px}
.exx .ex ul{list-style:none;margin:0;padding:0;border-top:1px solid rgba(200,168,106,.4);padding-top:6px}
.exx .ex li{font-size:14.5px;color:var(--sub);line-height:1.4;padding:5px 0 5px 34px;position:relative}
.exx .ex.cash li{padding-left:48px}
.exx .ex li span{position:absolute;left:0;top:6px;font-size:11px;font-weight:800;color:#0d1e33;background:var(--gold2);border-radius:5px;padding:1px 6px}
.sumx{display:grid;grid-template-columns:1fr 1fr;gap:16px 22px;flex:1;min-height:0;align-content:start}
.sumx .sb{min-width:0}
.sumx .stk{display:flex;flex-direction:column;gap:16px;min-width:0}
.sumx h3{font-size:17px;font-weight:800;color:var(--gold);margin-bottom:6px;display:flex;gap:10px;align-items:baseline}
.sumx h3 i{font-style:normal;font-family:var(--serif);font-size:20px;color:var(--gold2)}
.sumx h3 small{font-size:12.5px;color:var(--mute);font-weight:500}
.tbl.xs th{font-size:11px;padding:0 10px 6px;letter-spacing:.18em}
.tbl.xs td{font-size:13.5px;padding:4.5px 10px;line-height:1.35}
.tbl.xs td.k{font-size:14px;white-space:nowrap}
.tbl.xs td.n{font-size:12.5px;width:30px}
.sumx.roomy .tbl.xs td{font-size:15px;padding:7.5px 10px}
.sumx.roomy .tbl.xs td.k{font-size:15.5px}
.sumx.roomy{gap:26px 26px}
.sumx.roomy h3{font-size:19px;margin-bottom:8px}
.toc5{grid-template-columns:repeat(5,1fr)!important}
.toc5 .col{padding:0 16px;gap:22px}
.toc5 .s h3{font-size:20px;margin:4px 0 6px}
.toc5 .s li{font-size:14.5px;line-height:1.7}
.toc5 .s li i{font-size:12px;margin-right:8px}
.toc5 .s .sn{font-size:26px}
"""

    A = [("사전점검 대행 할인", "전문 점검원 대행 최대 50% 할인 · 이벤트 당첨 세대 동행"),
         ("셀프 점검 지원", "사전점검 체크리스트 · 점검요령 영상"),
         ("타입별 실측 사이즈", "가구·커튼 사이즈를 입주 전에 확인"),
         ("샘플하우스", "실제 제품을 보고 결정"),
         ("항공 VR 촬영", "단지 주변 입지를 입주 전에 확인"),
         ("3D 홈스타일링", "대표 타입 맞춤 공간 제안")]
    Bk = [("공용부 품질 점검", "철근 탐지 · 콘크리트 강도 · 기울기"),
          ("열화상 드론 · 라돈 측정", "누수·단열 징후 · 동별 대표세대 라돈"),
          ("일조 시뮬레이션", "3D 모델로 시간대별 그림자 분석"),
          ("도면 분석보고서", "착공·조경 도면 검토 · 개선안 비교"),
          ("공용·조경 하자진단", "사전점검 당일 보고서"),
          ("협상 미팅 동석", "전문 엔지니어가 조합·시공사 협의에"),
          ("온라인 위임장 · 민원", "전자서명 위임장 · 민원 양식·접수"),
          ("사전점검 당일 지원", "물품·도우미 · 라돈측정기 10대 · 커피차"),
          ("세미나 영상", "사전점검 요령·홈스타일 강좌")]
    C = [("커뮤니티·공용부 조명", "조도 재설계 · 관리비 절감안"),
         ("문주·경관조명 컨설팅", "진입부·외벽 야간 경관 개선안"),
         ("피트니스·키즈 공간", "운동·키즈 시설 구성·활용안"),
         ("전기차 충전 인프라", "위치·대수·전기 용량 검토"),
         ("입주 기념 점등식", "점등식 행사 기획·운영")]

    def pk(L, name, en, items):
        li = "".join(f"<li><b>{_h.escape(a)}</b> — {_h.escape(b)}</li>" for a, b in items)
        return f'<div class="pk"><div class="hd2"><div class="L">{L}</div><h3>{name}<small>{en}</small></h3></div><ul>{li}</ul></div>'

    S8 = "08. 혜택안내"
    p_choice = ("std", dict(sec=S8 + " · 발전지원 15만원", title=f"세대당 {fund}만원, [[현금 또는 혜택 패키지]] 중 선택",
        lead="두 가지를 다 드리는 것이 아니라, 받는 방식을 입예협이 고르십니다.",
        body=('<div class="nb"><div class="optx">'
              f'<div class="op"><i>OPTION ①</i><h3>현금으로 받기</h3><div class="v">{total.replace("만원", "")}<small>만원</small></div>'
              f'<ul><li>조합 {hh:,}세대 × {fund}만원 (부가세 포함)</li><li>조합 또는 입예협 공식 통장으로 입금</li><li>쓰임새는 입예협이 결정</li></ul></div>'
              '<div class="or">또는</div>'
              '<div class="op hl"><i>OPTION ②</i><h3>혜택 패키지로 받기</h3><div class="v">A · B · C</div>'
              f'<ul><li>같은 금액({total}) 범위 안에서 항목 선택</li><li>A 입주민 특화서비스 · B 협의회 단지발전지원 · C 단지지원 컨설팅</li>'
              '<li>항목·범위는 협의 후 협약서로 확정</li></ul></div></div>'
              '<div class="basex"><b>박람회 기본 혜택은 선택과 관계없이</b> 방문 세대 모두에게 드립니다 — '
              '박람회 상품권(2만원 쿠폰, 일반 20만원분 · 정회원 10만원분 추가) · 특정 입주민 5만원 추가 · 정회원 특가 · 사은품·경품 · 현장할인 최대 10%</div></div>'),
        kp=f"세대당 {fund}만원 = [[현금 또는 패키지]], 둘 중 하나로 드립니다."))
    p_pack = ("std", dict(sec=S8 + " · 혜택 패키지", title="혜택 패키지 [[A · B · C]] 구성 항목",
        lead=f"입예협이 필요한 항목을 골라 세대당 {fund}만원 범위를 채웁니다.",
        body='<div class="nb"><div class="pkx">' + pk("A", "입주민 특화서비스", "세대가 직접 받는 서비스", A)
             + pk("B", "협의회 단지발전지원", "입예협 업무·하자 대응", Bk) + pk("C", "단지지원 컨설팅", "공용부·커뮤니티 가치", C) + "</div></div>",
        kp=("각 항목의 자세한 내용은 [[다음 장부터 A → B → C 순서]]로 보여 드립니다.",
            "공용부 항목은 조합·관리주체 협의 전제")))

    def ex(tag, name, who, items, cls=""):
        li = "".join(f"<li><span>{a}</span>{_h.escape(b)}</li>" for a, b in items)
        return f'<div class="ex {cls}"><i>{tag}</i><h3>{name}</h3><p class="w">{who}</p><ul>{li}</ul></div>'
    p_examples = ("std", dict(sec=S8 + " · 혜택 패키지", title="이렇게 [[패키지로]] 받으실 수 있습니다 (예시)",
        lead="입예협이 무엇을 먼저 챙기고 싶은지에 따라 구성이 달라집니다.",
        body='<div class="nb"><div class="exx">'
             + ex("CASH", "현금형", "쓰임새를 입예협이 직접 정하고 싶을 때",
                  [("현금", f"전액 {total}"), ("통장", "조합 또는 입예협 공식 통장 입금")], "cash")
             + ex("EXAMPLE 1", "하자 대응형", "공사 품질과 하자를 먼저 챙기고 싶을 때",
                  [("B", "공용부 품질 점검"), ("B", "열화상 드론 · 라돈 측정"), ("B", "도면 분석보고서"),
                   ("B", "공용·조경 하자진단"), ("B", "협상 미팅 동석"), ("A", "사전점검 대행 할인")])
             + ex("EXAMPLE 2", "입주민 체감형", "세대가 직접 느끼는 혜택이 먼저일 때",
                  [("A", "타입별 실측 사이즈"), ("A", "3D 홈스타일링"), ("A", "항공 VR 촬영"), ("A", "사전점검 대행 할인"),
                   ("B", "사전점검 당일 지원"), ("B", "온라인 위임장")])
             + ex("EXAMPLE 3", "단지 가치형", "입주 후 단지 가치를 높이고 싶을 때",
                  [("C", "문주·경관조명 컨설팅"), ("C", "커뮤니티·공용부 조명"), ("C", "피트니스·키즈 공간"),
                   ("C", "전기차 충전 인프라"), ("B", "일조 시뮬레이션")])
             + "</div></div>",
        kp=(f"예시일 뿐입니다 — 항목을 섞어 [[세대당 {fund}만원 범위 안에서]] 자유롭게 구성합니다.",
            "항목별 금액 환산·수량은 입예협 협의 후 협약서로 확정")))

    # ------------------------------------------------ 10장 특화서비스 요약(통합 147~150 표 형식)
    def stbl(rows, head=("NO", "지원 항목", "지원 내용")):
        body = "".join(f'<tr><td class="n">{i:02d}</td><td class="k">{t(a)}</td><td>{t(b)}</td></tr>' for i, (a, b) in enumerate(rows, 1))
        return G["table"](list(head), body, "xs")

    def sb(n, name, rows, note="", cls=""):
        return f'<div class="sb {cls}"><h3><i>{n}</i>{name}<small>{note}</small></h3>{stbl(rows)}</div>'

    S10 = "10. 특화서비스 요약"
    base = [("박람회 상품권(쿠폰)", "2만원권 · 계약 업체마다 1매 · 일반회원 20만원분"),
            ("정회원 추가 쿠폰", "10만원분 추가"),
            ("특정 입주민 추가 쿠폰", "5만원 추가 · 소년·소녀가장·장애인·다자녀 등"),
            ("백화점 상품권", "방문·신청 시 1세대 1회"),
            ("현장 특별할인", "품목별 최대 10% 추가할인"),
            ("방문 선물 · 계약 사은품", "원터치 말발굽 · 업체별 사은품"),
            ("경품 추첨", "대형·소형 가전 · 참여 업체 경품"),
            ("온라인 박람회", "폐쇄몰 · 라이브커머스 · 같은 공동구매가")]
    member = [("정회원 특가", "실링팬 50% · 인테리어 30% · 프리미엄 중문 등"),
              ("조명 혜택", "우물 간접조명 · 갤러리조명 2구"),
              ("시공 혜택", "현관 줄눈 · 미세촘촘망 거실창 · 도어락 나노코팅"),
              ("케어 서비스", "피톤치드 항균 · 진드기 박멸 · 욕실케어 1회"),
              ("생활 혜택", "욕실 휴젠뜨 · 화재보험 2년 · 사전점검 할인"),
              ("품목 확정", "입예협 협의 · 조합원 옵션 중복 품목 제외")]
    p_s1 = ("std", dict(sec=S10, title="특화서비스 요약 ① [[박람회 기본 혜택]]",
        lead="15만원 선택과 관계없이, 박람회를 찾는 세대 모두에게 드립니다.",
        body='<div class="nb"><div class="sumx roomy">' + sb("01", "입주민 혜택", base, "방문 세대 모두") + sb("02", "정회원 혜택", member, "정회원 방문 세대") + "</div></div>",
        kp="상품권은 [[계약 업체마다 2만원씩]] — 필요한 품목만 계약하셔도 혜택이 적용됩니다."))
    p_s2 = ("std", dict(sec=S10, title=f"특화서비스 요약 ② [[발전지원 {fund}만원 · 패키지 A·B·C]]",
        lead=f"세대당 {fund}만원(총 {total}) — ① 현금 또는 ② 아래 항목으로 구성한 패키지 중 선택.",
        body='<div class="nb"><div class="sumx">' + sb("B", "협의회 단지발전지원", Bk)
             + '<div class="stk">' + sb("A", "입주민 특화서비스", A) + sb("C", "단지지원 컨설팅", C) + "</div></div></div>",
        kp="[[현금 또는 패키지]] 중 하나 · 항목·범위는 협약서로 확정 · 공용부 항목은 조합·관리주체 협의 전제"))
    safety = [("하자 예치금", "현금 1억 · 엣지컴퍼니 자산으로 공동통장 예치"),
              ("이행보증보험", "2년 · 10억 · 증권 실물 제출"),
              ("업체 하자보증", "특약이행각서 9개 항 · 패널티 3단계"),
              ("A/S", "48시간 하자보수 · 무상 A/S 2년 · 장기관리 최대 10년"),
              ("주관 콜센터", "클레임 접수·선보상 · CRM 관리")]
    vendor = [("4단계 공개 심사", "입예협 최종 컨펌 · 업체 서비스 교육"),
              ("인근 지역업체 90%", "시공 품목 · 48시간 A/S 거리"),
              ("최저가 차액 10배", "단가표 사전 공개 · 현장 가격 변경 없음"),
              ("계약 보호", "계약금 10% 상한 · 품목별 취소 기한·환불")]
    promo = [("카페 홍보 콘텐츠", "카페 대문·카드뉴스·이벤트 게시물"),
             ("사전점검 언박싱", "세대 동의 후 촬영 · 유튜브 공개"),
             ("드론 영상 · 검색·언론", "주·야간 드론 · 키워드 광고 · 기획 보도"),
             ("현장 매체", "현수막·전단·버스 광고")]
    cheolsan = [("옵션 중복 확인표", "조합원 유상옵션·기본 품목과 대조"),
                ("가격 공개표", "모델코드·시공비·추가금 공개"),
                ("3개 단지 분리 운영", "단지별 설치 예약·하역·엘리베이터"),
                ("31개월 관리", "선정~입주 후 1년 · 분기별 보고")]
    p_s3 = ("std", dict(sec=S10, title="특화서비스 요약 ③ [[안전망 · 업체선정 · 홍보 · 철산 맞춤]]",
        lead="입주민 돈을 지키는 장치와 박람회 운영 약속입니다.",
        body='<div class="nb"><div class="sumx">' + sb("03", "하자보증 · 안전망", safety) + sb("04", "업체선정 · 가격 보호", vendor)
             + sb("05", "홍보 방안", promo) + sb("06", "철산역 자이 맞춤", cheolsan) + "</div></div>",
        kp="제안서의 모든 항목은 [[협약서에 그대로 옮겨]] 이행합니다."))

    # ------------------------------------------------ 핵심 혜택 6가지 · 약속 장 정리
    k = take("철산역 자이에 드리는 [[핵심 혜택 6가지]]")[1]
    k["sec"] = S10
    k["body"] = B.tiles([
        dict(lb="발전지원금", big=f"{fund}", unit="만원", nm="현금 또는 패키지", ds=f"조합 {hh:,}세대 기준 총 {total} (부가세 포함) · 입예협 선택"),
        dict(lb="하자 예치금", big="1", unit="억원", nm="현금 예치", ds="엣지컴퍼니 자산으로 입예협 공동통장에 직접 예치"),
        dict(lb="이행보증보험", big="10", unit="억원", nm="2년 보증", ds="증권 실물을 입예협에 전달"),
        dict(lb="최저가 보장", big="10", unit="배", nm="차액 보상", ds="동일 제품이 더 싸면 차액의 10배 보상"),
        dict(lb="계약금 상한", big=f"{D.DEPOSIT_MAX}", unit="%", nm="계약 보호", ds="시공 전 취소·환불 절차를 품목별로 공개"),
        dict(lb="인근 지역업체", big="90", unit="%", nm="시공 품목", ds="48시간 하자보수가 가능한 거리의 업체 선정"),
    ], cols=3, rows_n=2).replace('class="tiles"', 'class="tiles lg"')

    def p_closing(no, sec):
        s = B_closing(no, sec)
        s = sub(s, f"<p>공고 대상 조합 {hh:,}세대 기준 · 총 {total}(부가세 포함)</p>", f"<p>조합 {hh:,}세대 · 총 {total} · 현금 또는 혜택 패키지 선택</p>")
        s = sub(s, "<b>입예협 전용 8가지 무상 지원</b><p>별도 비용 없음 · 자체 인력</p>",
                "<b>박람회 기본 혜택은 방문 세대 모두에게</b><p>상품권 쿠폰 · 사은품·경품 · 현장할인</p>")
        return s
    B_closing = B.p_closing
    B.p_closing = p_closing

    # ------------------------------------------------ 재배치
    T = take
    d01 = T("엣지컴퍼니는 [[이런 회사]]입니다.")
    d01[1]["n"] = "01"
    d03 = T("업체 선정이 [[주관사의 본질]]입니다.")
    d03[1]["n"] = "03"
    d04 = T("사고가 나도 [[입주민이 먼저]] 보상받습니다")
    d04[1]["n"] = "04"
    d04[1]["bl"] = [x for x in d04[1]["bl"] if "콜센터" not in x]
    d07 = T("철산역 자이를 위한 [[맞춤 제안]]")
    d07[1]["n"] = "07"
    d07[1]["bl"] = ["조합 단지 이해 · 특화 제안", "참가 자격 10개 항목 대응", "추진 일정 · 31개월 관리", "품목별 예상 참가 업체"]

    ch = [
        ("01. 회사소개", [d01] + [T(x) for x in [
            "숫자로 보는 [[엣지컴퍼니]]", "해마다 쌓이는 [[누적 주관 단지]]", "[[본사 사옥]] 운영 · 자본금 2억", "회사 개요와 [[법인 서류]]",
            "재무·납세·고용 [[증빙 원본]]", "공인된 [[자격과 신뢰]]", "제휴 · 면허 · 인증 [[원본 서류]]", "전국 지사망 · [[직영 4곳 + 협력 8곳]]",
            "[[직영 4곳]]이 지키는 12개 지사망", "왜 [[직영]]이어야 합니까",
            "주관 [[성공사례]] · 수임실적", "[[2,000세대 이상]] 초대형 단지를 맡아 왔습니다", "[[대단지]] 운영 경험", "2023년 이후 수임 단지",
            "사진으로 보는 주관 단지 [[2018–2022]]", "사진으로 보는 주관 단지 [[2023–2026]]", "한 단지가 아니라 [[한 신도시]]를 맡습니다",
            "[[사송 · 에코델타]] 단지별 주관 현황", "타 단지 협의회의 [[추천과 감사]]", "행사 밖에서도 [[현장 지원]]", "지역과 함께하는 [[나눔 활동]]"]]),
        ("02. 마케팅전략", [dv("02", "입주민이 [[먼저 알고]] 찾아옵니다", ["입예협 카페 홍보 콘텐츠", "사전점검 언박싱 영상", "드론 영상 · 검색·언론", "현수막·전단·버스 광고"])]
         + [T("입예협 카페 [[홍보 콘텐츠]] 제작"), T("사전점검 [[언박싱 영상]]과 현장 홍보")]),
        ("03. 업체선정", [d03, T("공동구매 [[품목]]을 한눈에")] + [T(x) for x in [
            "[[4단계]] 공개 심사 프로세스", "업체 [[심사 기준]]과 계약 원칙", "참여업체 [[서비스 교육]]", "[[지역업체 90%]] 선정 원칙",
            "공동구매 단가를 지키는 [[4가지 장치]]", "[[최저가 차액 10배]] 보상", "실적 비례 [[추가할인]] 구조", "입주민 [[자금]]을 먼저 지킵니다",
            "품목별 [[취소 기한]]과 환불 절차"]]),
        ("04. 하자보증", [d04] + [T(x) for x in ["입주민을 지키는 [[4중 안전망]]"]] + [T(kind="hi_money")] + [T(x) for x in [
            "이행보증보험 [[2년 · 10억]]", "보증보험증권 [[제출과 확인]]", "참여업체 [[하자보증]] 체계", "하자보수 [[특약이행각서]] 9개 항",
            "주요 클레임 품목과 [[보상 기준]]", "참여업체 [[패널티 3단계]]"]]),
        ("05. 주관 콜센터", [dv("05", "클레임은 [[주관사가 먼저]] 받습니다", ["주관 콜센터 · 선보상", "클레임 처리 흐름 · CRM", "입주민 후기 · 실시간 응대"])]
         + [T(x) for x in ["주관 [[콜센터]]와 선보상", "클레임 [[처리 흐름]]과 CRM 관리", "입주민 후기 · [[실시간 응대]] 화면"]]),
        ("06. 입주박람회", [dv("06", "확인하고 비교하는 [[입주박람회]]", ["운영 계획 · 행사장 대관", "즐거운 박람회 · 편의시설", "온라인 박람회 · 라이브커머스", "실제 박람회 현장"])]
         + [T(x) for x in ["입주박람회 [[운영 계획]]", "행사장 대관과 [[운영 준비]]", "하루가 [[즐거운]] 박람회", "가족이 머무는 [[편의시설]]",
                           "못 오셔도 [[괜찮습니다]]", "실제 박람회 [[현장]]"]]),
        ("07. 철산역 자이 맞춤 제안", [d07] + [T(x) for x in [
            "철산역 자이, [[이런 단지]]입니다", "조합 단지라서 [[챙겨야 하는 것]]", "입주까지 31개월, [[긴 시간]]을 관리합니다", "철산역 자이 [[특화 제안]]",
            "입찰 참가 자격 [[10개 항목]] 대응", "선정부터 입주까지 [[추진 일정]] (안)", "품목별 [[예상 참가 업체]]"]]),
        ("08. 혜택안내 · 박람회 기본 혜택", [dv("08", "혜택은 [[두 갈래]]로 드립니다",
            ["박람회 기본 혜택 — 방문 세대 모두", f"세대당 {fund}만원 — 현금 또는 패키지 선택", "A 입주민 특화서비스", "B 협의회 단지발전지원", "C 단지지원 컨설팅"])]
         + [T(x) for x in ["방문 세대 [[박람회 상품권 · 현장 혜택]]", "정회원 전용 [[추가 혜택]]", "사진으로 보는 [[정회원 혜택]]", "박람회 [[사은품 · 경품]]"]]),
        ("08. 혜택안내 · 발전지원 15만원", [T(kind="hi_fund"), p_choice, p_pack, p_examples]),
        ("08. 혜택안내 · A 입주민 특화서비스", [T(x) for x in ["입주 전에 [[미리 보는]] 우리 집", "사전점검 대행, [[이렇게 봅니다]]"]] + [T(kind="pricing")]),
        ("08. 혜택안내 · B 협의회 단지발전지원", [T(x) for x in [
            "공용부 [[구조·시공 품질]] 점검", "보이지 않는 [[하자]]까지 확인합니다", "입주 전에 보는 [[일조 시뮬레이션]]", "[[조경·착공]] 분석보고서",
            "도면·하자 분석 [[보고서 샘플]]", "입주 전부터 [[끝까지]] 붙어 있습니다", "사전점검 당일 [[현장 지원]]", "위임장, 이제 [[휴대폰으로]] 받습니다",
            "사전점검 세미나, [[영상으로]] 다시 봅니다"]]),
        ("08. 혜택안내 · C 단지지원 컨설팅", [T(x) for x in [
            "커뮤니티·공용부 [[조명 개선]]", "문주·경관조명 [[컨설팅]]", "피트니스·키즈 공간 [[개선 제안]]", "전기차 충전 [[인프라 검토]]"]]),
        ("09. 차별화 포인트", [T(kind="divider_lx"), T(kind="landscape"), T("[[조명 수직계열화]] · 유통 단계 없는 공급")]),
        ("10. 특화서비스 요약", [dv("10", "한눈에 보는 [[특화서비스]]", ["박람회 기본 혜택 · 정회원 혜택", f"발전지원 {fund}만원 · 패키지 A·B·C", "안전망 · 업체선정 · 홍보", "철산역 자이 맞춤"]),
                                p_s1, p_s2, p_s3, T("철산역 자이에 드리는 [[핵심 혜택 6가지]]")]),
    ]
    drop = [T("발전지원금은 [[이렇게 쓰입니다]]"), T("협의회 전용 [[8가지 무상 단지지원]]"), T("입예협·입주민 [[지원 한눈에]]"),
            T("협의회 전용 [[단지 지원]]"), T("입주민에게 [[직접]] 돌아가는 혜택"), T("기록이 [[증명]]합니다.")]
    head = [T(kind="cover"), T(kind="toc")]
    tail = [T(kind="closing"), T(kind="contact")]
    used = {id(p) for p in head + tail + drop}
    out = list(head)
    for sec, pages in ch:
        for p in pages:
            if p[0] not in ("divider", "divider_lx"):
                p[1]["sec"] = sec
            used.add(id(p))
            out.append(p)
    out += tail
    left = [p[1].get("title", p[0]) for p in P if id(p) not in used]
    assert not left, f"재배치에서 빠진 장: {left}"
    P[:] = out

    B.p_divider_lx = lambda: sub(G["B_p_divider_lx"](), '<div class="n">02</div>', '<div class="n">09</div>')

    # ------------------------------------------------ 목차 10장(5열 × 2)
    G["TOC4"][:] = [
        [("01", "회사소개", ["숫자·누적 실적", "법인·재무 서류 · 인증", "지사망 · 직영", "수임실적 · 대단지", "추천·감사 · 나눔"]),
         ("06", "입주박람회", ["운영 계획 · 대관", "즐거운 박람회 · 편의시설", "온라인 박람회", "박람회 현장"])],
        [("02", "마케팅전략", ["카페 홍보 콘텐츠", "사전점검 언박싱", "드론 · 검색 · 언론", "현수막 · 버스 광고"]),
         ("07", "철산역 자이 맞춤", ["단지 이해 · 조합 특화", "참가 자격 10개 항목", "일정 · 31개월 관리", "예상 참가 업체"])],
        [("03", "업체선정", ["공동구매 품목", "4단계 공개 심사", "지역업체 90%", "최저가 차액 10배", "계약·환불 보호"]),
         ("08", "혜택안내", ["박람회 기본 혜택", f"{fund}만원 · 현금 또는 패키지", "A 입주민 특화서비스", "B 협의회 단지발전지원", "C 단지지원 컨설팅"])],
        [("04", "하자보증", ["예치금 1억 · 보증 10억", "업체 하자보증 · 특약", "클레임 보상 기준", "패널티 3단계"]),
         ("09", "차별화 포인트", ["경관조명 설계·생산·시공", "조명 수직계열화"])],
        [("05", "주관 콜센터", ["콜센터 · 선보상", "클레임 처리 · CRM", "후기 · 실시간 응대"]),
         ("10", "특화서비스 요약", ["박람회 기본 · 정회원", "발전지원 · 패키지", "안전망 · 업체 · 홍보", "핵심 혜택 6가지"])],
    ]
    G["TOC_CLS"] = "toc5"
