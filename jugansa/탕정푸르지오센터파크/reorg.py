# -*- coding: utf-8 -*-
"""탕정 푸르지오 센터파크 제안서 — 목차를 통합제안서 순서로 재배치(본부장 지시 2026-10-07).

01 회사소개 · 02 마케팅전략 · 03 업체선정 · 04 하자보증 · 05 주관 콜센터 · 06 입주박람회
· 07 탕정 푸르지오 센터파크 맞춤 제안 · 08 혜택안내 · 09 차별화 포인트 · 10 특화서비스 요약 → 약속 · 연락처

08 혜택안내 원칙(본부장 10-07)
- 박람회 기본 혜택(상품권·정회원·사은품·경품)은 방문 세대 모두에게 — 15만원과 별개
- 세대당 15만원 = ① 현금(입예협 공식 통장) 또는 ② 같은 금액 범위의 혜택 패키지 A·B·C 중 선택
  A 입주민 특화서비스 · B 협의회 단지발전지원 · C 단지지원 컨설팅 (통합제안서 혜택안내 구성)
- '8가지 무상 단지지원' 장 삭제(15만원 + 무상지원을 다 주는 것처럼 보이던 문제)
- 상품권은 2만원 쿠폰을 업체마다 1매씩 쓰는 구조 → 정회원 '60만원 상당'은 내세우지 않는다

build_tangjeong.py 끝(특수 페이지 함수 교체 뒤)에서 apply(globals()) 로 부른다 — NO_NATIVE 미리보기에서는 안 돎.
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
        dict(lb="GIFT 01", big="30", unit="만원", nm="정회원 박람회 상품권",
             ds="일반회원 20만원 + 정회원 추가 10만원. 박람회 계약 시 품목(업체)당 1매 사용."),
        dict(lb="GIFT 02", big="+5", unit="만원", nm="특정 입주민 추가 상품권",
             ds="소년·소녀가장, 80세 이상 노부모 부양, 장애인, 다자녀(3자녀↑), 다문화, 임산부."),
        dict(lb="GIFT 03 · 현물", big="10", unit="만원", nm="백화점 상품권", hl=True, ds="방문·신청 시 1세대 1회 현물 지급(금액은 단지별 상이). 행사장에서 현금처럼 사용."),
        dict(lb="GIFT 04", big="10", unit="%", nm="현장 특별할인", ds="박람회 기간 품목별 현장 할인 특가 최대 10% 추가할인."),
    ])
    k["kp"] = ("[[백화점 상품권 10만원]]은 현물로, 박람회 상품권 [[30만원]]은 계약금으로 씁니다.", "정회원 기준 · 백화점 상품권 금액은 단지별 상이")
    k = take("정회원 전용 [[세대당 60만원 상당]]")[1]
    k["title"] = "정회원 전용 [[추가 혜택]]"
    k["lead"] = "정회원으로 박람회에 방문하시면 아래 혜택을 더 받으실 수 있습니다."
    k["kp"] = ("품목은 입예협 협의 후 [[조정 가능]]합니다.", "유상옵션과 겹치는 품목은 제외")
    # 특화 제안 03: 조명 점검은 C 패키지(단지지원 컨설팅) 항목 → '무상' 표기 삭제
    k = take("전기차 충전 [[인프라 검토]]")[1]
    k["lead"] = sub(k["lead"], "충전기 설치 컨설팅을 무상으로 지원합니다.", "충전기 설치 컨설팅을 지원합니다.")
    k["body"] = sub(k["body"], "컨설팅은 무상이며, 충전기", "충전기")

    # 15만원 장: 현금 또는 패키지
    def p_hi_fund(no, sec):
        s = B_hi_fund(no, sec)
        s = sub(s, f"<em>공고 단지 전 세대 {hh:,}세대</em>를 기준으로 지급하고, <em>입예협 공식 통장</em>으로 입금합니다.",
                f"<em>전 세대 {hh:,}세대</em> 기준 — <em>현금</em> 또는 같은 금액 범위의 <em>혜택 패키지</em> 중 입예협이 고릅니다.")
        s = sub(s, "<span>현금성 지원 · 입예협 공식 통장 입금 가능</span><span>단지 시설 투자</span><span>협의회 활동 지원</span>",
                "<span>① 현금 — 입예협 공식 통장 입금</span><span>② 혜택 패키지 A · B · C</span>")
        return s
    B_hi_fund = B.p_hi_fund
    B.p_hi_fund = p_hi_fund

    # ------------------------------------------------ 08장 신설 장
    B.CSS += r"""
.optx{display:grid;grid-template-columns:1fr 70px 1fr;align-items:stretch;flex:1;min-height:0}
.optx .op{border:1px solid var(--line);border-radius:16px;padding:40px 32px 26px;display:flex;flex-direction:column;justify-content:flex-start;
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
.pkx .pk .pkn{margin-top:auto;border:1px dashed rgba(200,168,106,.55);border-radius:10px;padding:10px 12px;font-size:13px;color:var(--sub);line-height:1.5}
.pkx{grid-template-columns:1.2fr 1.05fr .9fr !important}
.ruls .rc .v small{font-size:12.5px;color:var(--sub);font-weight:500}
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
.big small.mx{font-size:19px;margin:0 6px 0 0;font-weight:700}
.sumx.tight .tbl.xs td{padding:3.4px 10px}
.pkx .pk ul[style] li{break-inside:avoid}
.toc5{grid-template-columns:repeat(5,1fr)!important}
.toc5{grid-template-rows:auto 1fr}
.toc5 .col{padding:0 16px;gap:22px;display:grid;grid-template-rows:subgrid;grid-row:1 / 3;align-content:start}
.toc5 .s h3{font-size:20px;margin:4px 0 6px}
.toc5 .s li{font-size:14.5px;line-height:1.7}
.toc5 .s li i{font-size:12px;margin-right:8px}
.toc5 .s .sn{font-size:26px}
"""

    A = [("박람회 혜택", "백화점 상품권 10만원(현물) · 박람회 상품권 30만원 · 현장할인 10%"),
         ("정회원 혜택", "정회원 전용 품목 특가·시공 지원"),
         ("사은품 · 경품", "원터치 말발굽 · 업체 사은품 · 경품 추첨"),
         ("사전점검 대행 할인", "전문 점검원 대행 최대 50% 할인 · 이벤트 당첨 세대 동행"),
         ("셀프 점검 지원", "사전점검 체크리스트 · 점검요령 영상"),
         ("타입별 실측 사이즈", "가구·커튼 사이즈를 입주 전에 확인"),
         ("샘플하우스", "실제 제품을 보고 결정"),
         ("항공 VR 촬영", "단지 주변 입지를 입주 전에 확인"),
         ("3D 홈스타일링", "대표 타입 맞춤 공간 제안")]
    Bk = [("공용부 품질 점검", "철근 탐지 · 콘크리트 강도 · 기울기"),
          ("건설현장 안전점검", "입주 전 현장 안전점검 · 결과 정리"),
          ("온라인 위임장 · 민원", "전자서명 위임장 · 민원 양식·접수"),
          ("의견 전달 지원", "공문·자료·현장 운영으로 입예협 의견 전달"),
          ("공정·하자 분석 & 솔루션", "공정별 하자 검토 · 원인·보수 방안"),
          ("도면 분석보고서", "착공·조경 도면 검토 · 개선안 비교"),
          ("협상 미팅 동석", "전문 엔지니어가 입예협·시공사 협의에 동석"),
          ("세미나 영상", "사전점검 요령·홈스타일 강좌"),
          ("사전점검 당일 지원", "물품·도우미 · 라돈측정기 10대 · 커피차"),
          ("공용·조경 하자진단", "사전점검 당일 보고서"),
          ("열화상 드론 · 라돈 측정", "누수·단열 징후 · 동별 대표세대 라돈"),
          ("일조 시뮬레이션", "3D 모델로 시간대별 그림자 분석"),
          ("공용부 항균나노코팅", "엘리베이터 버튼·핸드레일 등"),
          ("세스코 특수해충 점검", "2025.11 MOU · 동별 대표세대 진단"),
          ("공용부 새집증후군 지원", "공용부 항균·탈취 관리")]
    C = [("커뮤니티·공용부 조명", "조도 재설계 · 관리비 절감안"),
         ("문주·경관조명 컨설팅", "진입부·외벽 야간 경관 개선안"),
         ("피트니스·키즈 공간", "운동·키즈 시설 구성·활용안"),
         ("전기차 충전 인프라", "위치·대수·전기 용량 검토"),
         ("입주 기념 점등식", "점등식 행사 기획·운영")]

    def pk(L, name, en, items, short=False, note=""):
        li = "".join(f"<li><b>{_h.escape(a)}</b>" + ("" if short else f" — {_h.escape(b)}") + "</li>" for a, b in items)
        ul = '<ul style="column-count:2;column-gap:14px">' if short else "<ul>"
        nt = f'<div class="pkn">{note}</div>' if note else ""
        return f'<div class="pk"><div class="hd2"><div class="L">{L}</div><h3>{name}<small>{en}</small></h3></div>{ul}{li}</ul>{nt}</div>'

    S8 = "08. 혜택안내"
    p_choice = ("std", dict(sec=S8 + " · 발전지원 15만원", title=f"세대당 {fund}만원, [[현금 또는 혜택 패키지]] 중 선택",
        lead="두 가지를 다 드리는 것이 아니라, 받는 방식을 입예협이 고르십니다.",
        body=('<div class="nb"><div class="optx">'
              f'<div class="op"><i>OPTION ①</i><h3>현금으로 받기</h3><div class="v">{total.replace("만원", "")}<small>만원</small></div>'
              f'<ul><li>{hh:,}세대 × {fund}만원 (부가세 포함)</li><li>입예협 공식 통장으로 입금</li><li>쓰임새는 입예협이 결정</li></ul></div>'
              '<div class="or">또는</div>'
              '<div class="op"><i>OPTION ②</i><h3>혜택 패키지로 받기</h3><div class="v">A · B · C</div>'
              f'<ul><li>같은 금액({total}) 범위 안에서 항목 선택</li><li>A · B · C 세 가지 패키지에서 골라 구성</li>'
              '<li>항목·범위는 협의 후 협약서로 확정</li></ul></div></div>'
              '<div class="basex"><b>A 입주민 특화서비스</b>에는 <em>백화점 상품권 10만원(현물)</em> · 박람회 상품권(정회원 30만원 = 일반 20만원 + 정회원 추가 10만원) · 정회원 혜택 · '
              '사은품·경품 · 사전점검 할인 · 실측·VR·3D 서비스가 들어 있습니다.</div></div>'),
        kp=f"세대당 {fund}만원 = [[현금 또는 패키지]], 둘 중 하나로 드립니다."))
    p_pack = ("std", dict(sec=S8 + " · 혜택 패키지", title="혜택 패키지 [[A · B · C]] 구성 항목",
        lead=f"입예협이 필요한 항목을 골라 세대당 {fund}만원 범위를 채웁니다.",
        body='<div class="nb"><div class="pkx">' + pk("A", "입주민 특화서비스", "세대가 직접 받는 서비스", A)
             + pk("B", "협의회 단지발전지원", "입예협 업무·하자 대응", Bk, True) + pk("C", "단지지원 컨설팅", "공용부·커뮤니티 가치", C,
                                note="경관조명·공용부 조명은 전기공사업 면허를 갖춘 주관사가 시공 가능 여부까지 검토합니다. 시공은 입예협·관리주체 승인 후 선택.") + "</div></div>",
        kp=("각 항목의 자세한 내용은 [[다음 장부터 A → B → C 순서]]로 보여 드립니다.",
            "공용부 항목은 입예협·관리주체 협의 전제")))

    def ex(tag, name, who, items, cls=""):
        li = "".join(f"<li><span>{a}</span>{_h.escape(b)}</li>" for a, b in items)
        return f'<div class="ex {cls}"><i>{tag}</i><h3>{name}</h3><p class="w">{who}</p><ul>{li}</ul></div>'
    p_examples = ("std", dict(sec=S8 + " · 혜택 패키지", title="이렇게 [[패키지로]] 받으실 수 있습니다 (예시)",
        lead="입예협이 무엇을 먼저 챙기고 싶은지에 따라 구성이 달라집니다.",
        body='<div class="nb"><div class="exx">'
             + ex("CASH", "현금형", "쓰임새를 직접 정할 때",
                  [("현금", f"전액 {total}"), ("통장", "입예협 공식 통장 입금")], "cash")
             + ex("EXAMPLE 1", "하자 대응형", "품질·하자를 먼저 챙길 때",
                  [("B", "공용부 품질 점검"), ("B", "열화상 드론 · 라돈 측정"), ("B", "도면 분석보고서"),
                   ("B", "공용·조경 하자진단"), ("B", "협상 미팅 동석"), ("A", "사전점검 대행 할인")])
             + ex("EXAMPLE 2", "입주민 체감형", "세대 체감 혜택이 먼저일 때",
                  [("A", "백화점 상품권 10만원(현물)"), ("A", "박람회 혜택 · 정회원 혜택"), ("A", "사은품 · 경품"), ("A", "사전점검 대행 할인"),
                   ("A", "타입별 실측 사이즈"), ("A", "3D 홈스타일링"), ("B", "사전점검 당일 지원")])
             + ex("EXAMPLE 3", "단지 가치형", "단지 가치를 높이고 싶을 때",
                  [("C", "문주·경관조명 컨설팅"), ("C", "커뮤니티·공용부 조명"), ("C", "피트니스·키즈 공간"),
                   ("C", "전기차 충전 인프라"), ("B", "일조 시뮬레이션")])
             + "</div></div>",
        kp=(f"예시일 뿐입니다 — 항목을 섞어 [[세대당 {fund}만원 범위 안에서]] 자유롭게 구성합니다.",
            "금액 환산·수량은 협약서로 확정")))

    # ------------------------------------------------ 10장 특화서비스 요약(통합 147~150 표 형식)
    def stbl(rows, head=("NO", "지원 항목", "지원 내용")):
        body = "".join(f'<tr><td class="n">{i:02d}</td><td class="k">{t(a)}</td><td>{t(b)}</td></tr>' for i, (a, b) in enumerate(rows, 1))
        return G["table"](list(head), body, "xs")

    def sb(n, name, rows, note="", cls=""):
        return f'<div class="sb {cls}"><h3><i>{n}</i>{name}<small>{note}</small></h3>{stbl(rows)}</div>'

    S10 = "10. 특화서비스 요약"
    base = [("정회원 박람회 상품권", "30만원 (일반 20만원 + 정회원 추가 10만원)"),
            ("상품권 사용", "박람회 계약 시 품목(업체)당 1매"),
            ("특정 입주민 추가 상품권", "5만원 추가 · 소년·소녀가장·장애인·다자녀 등"),
            ("백화점 상품권 (현물)", "[[10만원]] (금액 상이) · 방문·신청 시 1세대 1회"),
            ("현장 특별할인", "품목별 최대 10% 추가할인"),
            ("방문 선물 · 계약 사은품", "원터치 말발굽 · 업체별 사은품"),
            ("경품 추첨", "대형·소형 가전 · 참여 업체 경품"),
            ("온라인 박람회", "폐쇄몰 · 라이브커머스 · 같은 공동구매가")]
    member = [("정회원 특가", "실링팬 50% · 인테리어 30% · 프리미엄 중문 등"),
              ("조명 혜택", "우물 간접조명 · 갤러리조명 2구"),
              ("시공 혜택", "현관 줄눈 · 미세촘촘망 거실창 · 도어락 나노코팅"),
              ("케어 서비스", "피톤치드 항균 · 진드기 박멸 · 욕실케어 1회"),
              ("생활 혜택", "욕실 휴젠뜨 · 화재보험 2년 · 사전점검 할인"),
              ("품목 조정", "입예협 협의 후 조정 가능 · 유상옵션 중복 품목 제외")]
    p_s1 = ("std", dict(sec=S10, title="특화서비스 요약 ① [[A 입주민 특화서비스]]",
        lead=f"세대당 {fund}만원 혜택 패키지 A — 입주민 한 세대 한 세대가 직접 받는 혜택입니다.",
        body='<div class="nb"><div class="sumx roomy">' + sb("01", "박람회 혜택", base) + sb("02", "정회원 혜택", member, "정회원 방문 세대") + "</div></div>",
        kp="정회원 박람회 상품권 [[30만원]] (일반회원 20만원 + 정회원 추가 10만원)"))
    p_s2 = ("std", dict(sec=S10, title="특화서비스 요약 ② [[B 협의회 단지발전지원 · C 단지지원 컨설팅]]",
        lead=f"세대당 {fund}만원(총 {total}) — ① 현금 또는 ② 패키지 A·B·C 항목으로 구성 중 선택.",
        body='<div class="nb"><div class="sumx tight">' + sb("B", "협의회 단지발전지원", Bk) + sb("C", "단지지원 컨설팅", C) + "</div></div>",
        kp="[[현금 또는 패키지]] 중 하나 · 항목·범위는 협약서로 확정 · 공용부 항목은 입예협·관리주체 협의 전제"))
    safety = [("이행보증보험", "2년 · 최대 10억 · 증권 실물 제출"),
              ("하자 예치금", "최대 1억 · 엣지컴퍼니 자산 · 선보상 재원"),
              ("업체 하자보증", "특약이행각서 9개 항 · 패널티 3단계"),
              ("A/S", "48시간 하자보수 · 무상 A/S 최소 2년(업체별 상이) · 장기관리 최대 10년"),
              ("주관 콜센터", "클레임 접수·선보상 · CRM 관리")]
    vendor = [("4단계 공개 심사", "입예협 최종 컨펌 · 업체 서비스 교육"),
              ("인근 지역업체 선정", "시공 품목 · 검증 업체 · 하청 금지"),
              ("최저가 차액 10배", "단가표 사전 공개 · 현장 가격 변경 없음"),
              ("계약 보호", "계약금 10% 상한 · 품목별 취소 기한·환불")]
    promo = [("카페 홍보 콘텐츠", "카페 대문·카드뉴스·이벤트 게시물"),
             ("사전점검 언박싱", "세대 동의 후 촬영 · 유튜브 공개"),
             ("드론 영상 · 검색·언론", "주·야간 드론 · 키워드 광고 · 기획 보도"),
             ("현장 매체", "현수막·전단·버스 광고")]
    cheolsan = [("유상옵션 중복 확인", "유상옵션·기본 품목과 대조"),
                ("84㎡ 타입별 견적", "84A·B·C 실측 · 가격 공개표"),
                ("건의 관리표 · 조경조명", "중앙광장·물의정원 진단"),
                ("17개월 관리", "선정~입주 후 1년 · 정례 보고")]
    p_s3 = ("std", dict(sec=S10, title="특화서비스 요약 ③ [[안전망 · 업체선정 · 홍보 · 단지 맞춤]]",
        lead="입주민 돈을 지키는 장치와 박람회 운영 약속입니다.",
        body='<div class="nb"><div class="sumx">' + sb("03", "하자보증 · 안전망", safety) + sb("04", "업체선정 · 가격 보호", vendor)
             + sb("05", "홍보 방안", promo) + sb("06", "탕정 푸르지오 센터파크 맞춤", cheolsan) + "</div></div>",
        kp="제안서의 모든 항목은 [[협약서에 그대로 옮겨]] 이행합니다."))

    # ------------------------------------------------ 핵심 혜택 6가지 · 약속 장 정리
    k = take("탕정 푸르지오 센터파크에 드리는 [[핵심 혜택 6가지]]")[1]
    k["sec"] = S10
    k["body"] = B.tiles([
        dict(lb="발전지원금", big=f"{fund}", unit="만원", nm="현금 또는 패키지", ds=f"{hh:,}세대 기준 총 {total} (부가세 포함) · 입예협 선택"),
        dict(lb="이행보증보험 2년", big="@@MX10", unit="억원", nm="주관사 이행 보증", ds="증권 실물을 입예협에 전달"),
        dict(lb="최저가 차액", big="10", unit="배", nm="차액 보상", ds="동일 모델 새 제품 · 인근 오프라인 정상가 · 계약 후 7일 이내"),
        dict(lb="계약금 상한", big=f"{D.DEPOSIT_MAX}", unit="%", nm="계약 보호", ds="시공 전 취소·환불 절차를 품목별로 공개"),
        dict(lb="하자보수", big="48", unit="시간", nm="하자보수 원칙", ds="하자지연 패널티 · 무상 A/S 최소 2년(업체별 상이)"),
        dict(lb="하자 예치금", big="@@MX1", unit="억원", nm="선보상 재원", ds="자산으로 예치 · 사용 내역 공개"),
    ], cols=3, rows_n=2).replace('class="tiles"', 'class="tiles lg"').replace("@@MX10", '<small class="mx">최대</small>10').replace("@@MX1", '<small class="mx">최대</small>1')

    def p_closing(no, sec):
        s = B_closing(no, sec)
        s = sub(s, f"<p>전 세대 {hh:,}세대 기준 · 총 {total}(부가세 포함)</p>", f"<p>{hh:,}세대 · 총 {total} · 현금 또는 혜택 패키지 선택</p>")
        s = sub(s, "<b>입예협 전용 8가지 무상 지원</b><p>별도 비용 없음 · 자체 인력</p>",
                "<b>A 입주민 특화서비스</b><p>정회원 박람회 상품권 30만원 · 정회원 혜택 · 사은품·경품 · 사전점검 할인</p>")
        s = sub(s, "<b>하자 예치금 1억 · 이행보증보험 10억</b><p>엣지컴퍼니 자산으로 공동통장 예치 · 증권 실물 제출</p>",
                "<b>이행보증보험 최대 10억 · 하자 예치금 최대 1억</b><p>증권 실물 제출 · 엣지컴퍼니 자산으로 예치</p>")
        s = sub(s, "<b>시공 품목 인근 지역업체 90% 선정</b>", "<b>시공 품목 인근 지역업체 우선 선정</b>")
        return s
    B_closing = B.p_closing
    B.p_closing = p_closing

    # ------------------------------------------------ 2차 수정(본부장 10-07 오후)
    B.CSS += r"""
.exbox{position:relative;border:1px dashed rgba(200,168,106,.6);border-radius:12px;padding:14px 16px 10px;background:rgba(255,255,255,.03)}
.exbox h4{font-size:14px;font-weight:700;color:var(--sub);margin:2px 0 8px 52px}
.extag{position:absolute;left:14px;top:12px;font-size:12px;font-weight:800;color:#0d1e33;background:var(--gold2);border-radius:6px;padding:2px 9px}
.paper{background:#fbfaf6;color:#1d2530;border-radius:3px;box-shadow:0 0 0 1px rgba(0,0,0,.4),0 18px 40px rgba(0,0,0,.55);position:relative;overflow:hidden}
.paper .stamp{position:absolute;right:14px;top:12px;border:2px solid #c0392b;color:#c0392b;font-weight:800;font-size:13px;padding:2px 10px;border-radius:4px;transform:rotate(-6deg);letter-spacing:.1em}
.a4{height:100%;aspect-ratio:210/297;padding:16px 18px 12px;display:flex;flex-direction:column;font-size:9px;line-height:1.38}
.a4 h2{font-size:16px;font-weight:800;text-align:center;letter-spacing:.06em;margin-top:4px}
.a4 .sub{text-align:center;font-size:8.5px;color:#5b6470;margin:3px 0 7px;padding-bottom:6px;border-bottom:1px dashed #9aa3ad}
.a4 table{width:100%;border-collapse:collapse}
.a4 th{background:#e7e9ec;font-size:8.6px;padding:3px;border:1px solid #aeb5bd}
.a4 td{border:1px solid #c4cad1;padding:2.6px 5px;vertical-align:top}
.a4 td.n{width:16px;text-align:center;color:#5b6470}
.a4 td.h{width:52px;font-weight:700;white-space:nowrap}
.a4 tr.red td{outline:1.5px solid #c0392b;outline-offset:-1.5px}
.a4 .ag{margin-top:7px;font-size:9px;font-weight:600}
.a4 .dt{margin-top:6px;text-align:right;font-size:9px;letter-spacing:.3em}
.a4 .sg{margin-top:5px;display:grid;grid-template-columns:auto 1fr;gap:3px 8px;font-size:9px;width:62%;margin-left:auto}
.a4 .sg i{font-style:normal}
.a4 .sg span{border-bottom:1px solid #9aa3ad;min-height:13px;text-align:right}
.bond{height:100%;aspect-ratio:210/250;padding:18px 20px 14px;display:flex;flex-direction:column;font-size:10.5px}
.bond .bt{text-align:center;font-size:19px;font-weight:800;letter-spacing:.04em;margin-top:8px}
.bond .bs{text-align:center;font-size:9.5px;color:#5b6470;margin:3px 0 10px}
.bond h5{font-size:10.5px;color:#fff;background:#2f4a6b;padding:2px 8px;margin:8px 0 0;display:inline-block;border-radius:2px}
.bond table{width:100%;border-collapse:collapse;border-top:2px solid #2f4a6b}
.bond th{width:22%;background:#eef1f4;font-size:10px;padding:5px 6px;border-bottom:1px solid #c4cad1;text-align:left}
.bond td{padding:5px 7px;border-bottom:1px solid #c4cad1;font-size:10.5px}
.bond .ft{margin-top:auto;font-size:9px;color:#5b6470;border-top:1px dashed #9aa3ad;padding-top:6px}
.bond .wm{position:absolute;left:50%;top:56%;transform:translate(-50%,-50%) rotate(-18deg);font-size:76px;font-weight:900;color:rgba(192,57,43,.13);letter-spacing:.3em;white-space:nowrap}
.docx{display:grid;gap:30px;flex:1;min-height:0;align-items:stretch}
.docx .pp{display:flex;justify-content:center;min-height:0;height:100%}
.msx{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;flex:1;min-height:0}
.msx .mc{border:1px solid var(--line);border-radius:14px;overflow:hidden;display:grid;grid-template-rows:minmax(0,1fr) 150px;text-align:center;
  background:linear-gradient(180deg,rgba(255,255,255,.07),rgba(255,255,255,.015))}
.msx .ic{background:#fbfaf6;flex:1;min-height:0;display:flex;align-items:center;justify-content:center;padding:10px}
.msx .ic img{max-height:100%;max-width:70%;object-fit:contain}
.msx .tx{padding:12px 16px 16px;border-top:2px solid var(--gold2)}
.msx i{font-style:normal;font-family:var(--serif);font-size:26px;color:var(--gold2)}
.msx h3{font-size:22px;font-weight:800;margin:2px 0 6px}
.msx b{display:block;font-size:17px;color:var(--gold)}
.msx p{font-size:14.5px;color:var(--sub);margin-top:6px;line-height:1.5}
.msband{display:flex;align-items:center;gap:24px;border:1px solid rgba(200,168,106,.5);border-radius:12px;padding:12px 24px;background:linear-gradient(90deg,rgba(235,203,143,.14),rgba(235,203,143,.02))}
.msband b{font-size:22px;color:var(--gold);white-space:nowrap}
.msband span{font-size:16px;color:var(--sub)}
.pkp{display:grid;grid-template-columns:300px 1fr;gap:26px;flex:1;min-height:0}
.pkp .lf{border:1px solid rgba(235,203,143,.6);border-radius:16px;padding:26px 26px;display:flex;flex-direction:column;justify-content:center;
  background:linear-gradient(180deg,rgba(235,203,143,.14),rgba(235,203,143,.02))}
.pkp .L{width:88px;height:88px;border-radius:50%;background:var(--gold);color:#0d1e33;font-weight:800;font-size:52px;display:flex;align-items:center;justify-content:center}
.pkp .lf h3{font-size:27px;font-weight:800;margin:16px 0 4px}
.pkp .lf i{font-style:normal;font-size:12px;letter-spacing:.24em;color:var(--gold2);font-weight:700}
.pkp .lf p{font-size:15.5px;color:var(--sub);line-height:1.55;margin-top:12px}
.pkp .rt{display:flex;flex-direction:column;gap:12px;min-height:0}
.pkp .gh{font-size:13px;font-weight:700;letter-spacing:.06em;color:var(--gold);display:flex;align-items:center;gap:10px}
.pkp .gh:after{content:'';flex:1;height:1px;background:rgba(200,168,106,.4)}
.pkp ul{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:10px}
.pkp li{border:1px solid var(--line);border-radius:10px;padding:10px 14px;display:flex;gap:12px;align-items:flex-start;background:rgba(255,255,255,.035)}
.pkp li .no{font-family:var(--serif);font-size:20px;color:var(--gold2);line-height:1.1;flex:none;width:26px}
.pkp li b{display:block;font-size:16.5px}
.pkp li span{display:block;font-size:13.5px;color:var(--sub);margin-top:2px;line-height:1.4}
.ruls{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;flex:1;min-height:0}
.ruls .rc{border:1px solid var(--line);border-radius:14px;padding:18px 20px;background:linear-gradient(180deg,rgba(255,255,255,.07),rgba(255,255,255,.015))}
.ruls .rc.hl{border-color:rgba(235,203,143,.7)}
.ruls .rc i{font-style:normal;font-size:12px;letter-spacing:.24em;color:var(--gold2);font-weight:700}
.ruls .rc h3{font-size:21px;font-weight:800;margin:6px 0 2px}
.ruls .rc .v{font-size:15px;color:var(--gold);font-weight:700;margin-bottom:10px}
.ruls .rc ul{list-style:none;margin:0;padding:10px 0 0;border-top:1px solid rgba(200,168,106,.35)}
.ruls .rc li{font-size:14.5px;color:var(--sub);line-height:1.5;padding:4px 0 4px 14px;position:relative}
.ruls .rc li:before{content:'·';position:absolute;left:2px;color:var(--gold2)}
"""

    # 회사소개 — 통합제안서 27쪽(행사리스트 머리말) 정리
    def mc(n, nm, hd, ds, img):
        return (f'<div class="mc"><div class="ic"><img src="assets_ins/{img}.jpg" alt=""></div>'
                f'<div class="tx"><i>{n}</i><h3>{nm}</h3><b>{hd}</b><p>{ds}</p></div></div>')
    p_mission = ("std", dict(sec="01. 회사소개", title="체계적 행사 운영으로 [[고객 만족]]을 최우선합니다",
        lead="보여주는 행사가 아니라, 입주 후까지 지키는 행사를 만듭니다.",
        body='<div class="nb"><div class="msx">'
             + mc("01", "행사관리", "‘보여주기’보다는 ‘지켜주기’", "전문가 집단이 만든 체계적 행사 시스템으로 운영합니다.", "n31_gift")
             + mc("02", "현장지원", "행사에서 입주 후까지의 책임", "입주민과의 약속은 보이지 않는 곳에서도 이행됩니다.", "n31_headset")
             + mc("03", "사회공헌활동", "마음을 담은 봉사", "꾸준한 사회공헌활동으로 지역과 나눔을 실천합니다.", "n31_heart")
             + '</div><div class="msband"><b>전문성 · 책임감 · 진정성</b><span>엣지컴퍼니는 약속을 지키고, 가치를 만들어 갑니다.</span></div></div>',
        kp="박람회 하루가 아니라 [[입주 후까지]] 책임지는 주관사입니다."))

    # 업체선정 — 90% 비중 삭제
    k = take("[[지역업체 90%]] 선정 원칙")[1]
    k["title"] = "검증된 [[인근 지역업체]] 선정 원칙"
    k["body"] = sub(k["body"], '<div class="big">90<small>%</small></div><div class="nm">시공 품목 지역업체 비중</div>',
                    '<div class="big">인근</div><div class="nm">시공 품목 인근 업체 우선</div>')
    d03b = take("업체 선정이 [[주관사의 본질]]입니다.")[1]
    d03b["bl"] = [{"시공 품목 지역업체 90%": "시공 품목 인근 업체 우선"}.get(x, x) for x in d03b["bl"]]

    # 실적 비례 추가할인 — 표는 '예시'로 작게
    k = take("실적 비례 [[추가할인]] 구조")[1]
    rows = [("50세대", "1%", "1만원", "99만원"), ("100세대", "2%", "2만원", "98만원"), ("150세대", "3%", "3만원", "97만원")]
    tb = G["table"](["계약 세대 수", "추가할인율", "할인액", "최종 결제"],
                    "".join(f'<tr><td class="k">{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>' for a, b, c, d in rows), "xs")
    k["body"] = ('<div class="nb"><div class="splitx" style="grid-template-columns:1.15fr 1fr">'
                 '<div><div class="bulx">'
                 '<div><b>기대매출을 넘기면 추가할인</b><p>업체가 입찰 때 약속한 기대매출을 넘기면, 넘긴 만큼 계약 세대에 추가할인을 드립니다.</p></div>'
                 '<div><b>잔금에서 차감</b><p>시공·설치를 확인한 뒤 내는 잔금에서 빼 드립니다.</p></div>'
                 '<div><b>계약 세대마다 적용</b><p>해당 업체와 계약한 모든 세대에 같은 비율로 적용합니다.</p></div>'
                 '<div><b>조건은 입예협과 확정</b><p>업체가 입찰 때 낸 단계별 할인율을 입예협과 검토해 품목별로 정합니다.</p></div>'
                 '</div></div>'
                 '<div style="justify-content:center"><div class="exbox"><span class="extag">예시</span>'
                 '<h4>계약가 100만원 품목 · 계약 세대 수별</h4>' + tb +
                 '<p class="notex" style="margin-top:8px">세대 수·할인율은 이해를 돕기 위한 예시입니다. 잔금 차감은 계약 취소·환불 규정 제4조와 같습니다.</p>'
                 '</div></div></div></div>')
    k["kp"] = "많이 계약될수록 [[계약 세대의 잔금]]이 함께 줄어듭니다."

    # 하자보증 — 예치금은 '최대 1억'으로 낮추고 콜센터(선보상) 장으로, 보증보험 '2년 최대 10억'
    # 예치금 카드는 주관 콜센터 장으로 옮겼으므로 삭제 → 3중 안전망 (본부장 10-07)
    k = take("입주민을 지키는 [[4중 안전망]]")[1]
    k["title"] = "입주민을 지키는 [[3중 안전망]]"
    k["lead"] = sub(k["lead"], "네 겹으로", "세 겹으로")
    k["body"] = sub(k["body"], '<div class="card"><div class="lb">01</div><div class="big">1<small>억</small></div><div class="nm">하자 예치금 현금</div><div class="ds">엣지컴퍼니 자산으로 직접 예치합니다.</div></div>', "")
    k["body"] = sub(k["body"], 'repeat(4,1fr)', 'repeat(3,1fr)')
    k["body"] = sub(k["body"], '<div class="lb">02</div><div class="big">10<small>억</small></div><div class="nm">이행보증보험 2년</div>',
                    '<div class="lb">01</div><div class="big"><small class="mx">최대</small>10<small>억</small></div><div class="nm">이행보증보험 2년</div>')
    k["body"] = sub(k["body"], '<div class="lb">03</div>', '<div class="lb">02</div>')
    k["body"] = sub(k["body"], '<div class="lb">04</div>', '<div class="lb">03</div>')
    d04b = take("사고가 나도 [[입주민이 먼저]] 보상받습니다")[1]
    d04b["bl"] = [{"이행보증보험 2년 10억": "이행보증보험 2년 · 최대 10억"}.get(x, x) for x in d04b["bl"] if "예치금" not in x]

    p_deposit = ("std", dict(sec="05. 주관 콜센터", title="선보상 재원 · 하자 예치금 [[최대 1억원]]",
        lead="콜센터가 먼저 보상할 수 있도록, 주관사가 예치금을 따로 둡니다.",
        body=B.cards([
            dict(lb="AMOUNT", big="@@MX1", unit="억원", nm="예치 규모", ds="단지 규모와 입예협 협의에 따라 예치 금액을 정합니다."),
            dict(lb="SOURCE", big="자산", nm="엣지컴퍼니 자산으로 예치", ds="참여 업체에게 걷은 돈이 아닙니다. 업체가 빠져도 예치금은 줄지 않습니다."),
            dict(lb="USE", big="선보상", nm="하자 시 입주민 먼저", ds="업체 사고·도산 시 입주민 선보상에 쓰고, 사용 내역을 공개합니다."),
        ], cols=3).replace("@@MX1", '<small class="mx">최대</small>1'),
        kp="예치금은 콜센터 [[선보상]]이 실제로 돌아가게 하는 재원입니다."))

    k = take("이행보증보험 [[2년 · 10억]]")[1]
    k["title"] = "이행보증보험 [[2년 · 최대 10억]]"
    k["lead"] = "공고 입찰자격 8) — 계약이행 보증과 하자보수 이행 보증을 협약 시 증권으로 제출합니다."
    bond = ('<div class="paper bond"><div class="stamp">견본</div><div class="wm">견 본</div>'
            '<div class="bt">이행(하자)보증보험증권</div><div class="bs">증권 항목 설명용 견본 · 실제 증권은 보증보험사가 발급합니다</div>'
            '<h5>기본사항</h5><table>'
            '<tr><th>증권번호</th><td>제 ○○○-○○○-○○○○ 호</td></tr>'
            '<tr><th>보험계약자</th><td>주식회사 엣지컴퍼니</td></tr>'
            f'<tr><th>피보험자</th><td>{D.CLIENT}</td></tr>'
            '<tr><th>보험가입금액</th><td>최대 금 10억원 (협약 확정액)</td></tr>'
            '<tr><th>보험기간</th><td>2년 (개시일은 박람회·입주 일정에 맞춰 협약으로 확정)</td></tr></table>'
            '<h5>보증하는 사항</h5><table>'
            '<tr><th>보증내용</th><td>입주박람회 주관 협약에 따른 이행(하자)보증</td></tr>'
            f'<tr><th>주계약내용</th><td>{D.SITE["official"]} 입주박람회 주관 협약서 — 제안 내용 이행 · 참여업체 하자보수 이관</td></tr></table>'
            '<div class="ft">증권을 받으시면 보험가입금액 · 보험기간 · 피보험자 · 주계약내용이 협약서와 같은지 확인해 주십시오.</div></div>')
    k["body"] = ('<div class="nb"><div class="docx" style="grid-template-columns:1fr 1fr">'
                 '<div class="bulx">'
                 '<div><b>보증 금액 · 최대 10억원</b><p>제안 내용 미이행·업체 도산·검증 미비에 대한 주관사 책임 범위. 금액은 협약으로 확정합니다.</p></div>'
                 '<div><b>보증 기간 · 2년</b><p>박람회·입주 기간을 보증하도록 개시일을 협약으로 정합니다.</p></div>'
                 '<div><b>업체 도산 시 · 전액</b><p>엣지컴퍼니가 비용 전액을 부담하고 동종업체로 하자보수를 이관합니다.</p></div>'
                 '<div><b>증권 실물 제출</b><p>협약식 때 증권 실물을 입예협에 전달합니다.</p></div>'
                 '</div><div class="pp">' + bond + '</div></div></div>')
    k["kp"] = ("주관사가 약속을 지키지 않으면 [[보험이 대신 지급]]합니다.", "오른쪽은 증권 견본(예시)")

    k = take("보증보험증권 [[제출과 확인]]")[1]
    k["body"] = sub(k["body"], "<p>이행(지급)보증보험증권 발급</p>", "<p>이행(하자)보증보험증권 발급</p>")
    k["body"] = sub(k["body"], '<div class="nm">보증금액 10억원</div><div class="ds">증권 금액이 제안서와 같은지</div>',
                    '<div class="nm">보증금액 최대 10억원</div><div class="ds">증권 금액이 협약 확정액과 같은지</div>')

    # 특약이행각서 — A4 문서 예시
    k = take("하자보수 [[특약이행각서]] 9개 항")[1]
    k["title"] = "입주박람회 [[특약이행각서]] (예시)"
    k["lead"] = "박람회에 참여하는 모든 업체는 아래 각서에 서명해야 참여할 수 있습니다."
    arts = [("이관 의무", "관련 법령에 따른 하자보수 이관 의무를 이행한다."),
            ("이관 대상", "설비·마감공사 등 입주민 하자 발생 시 보수 범위를 명시한다."),
            ("하자 통보", "하자 통보는 서면(내용증명·전자문서)으로 하며 근거를 남긴다."),
            ("계약 해지", "계약 해지 시 중도 정산 및 포기 각서를 작성한다."),
            ("보증 기간", "하자 접수 기간(최소 2년)과 보증 책임·조치 의무를 명문화한다."),
            ("연대책임", "폐업·도산 시 별도 계약 없이도 하자보수를 즉시 승인한다."),
            ("지연 배상", "비용 지급 기한과 불이행 시 지연배상금·손해배상을 따른다."),
            ("민원 처리", "민원 발생 시 즉시 처리하고 결과를 보고한다."),
            ("주관사 이관", "도산 시 ㈜엣지컴퍼니의 사후관리·하자보수 이관에 동의한다.")]
    trs = "".join(f'<tr{" class=red" if i == 9 else ""}><td class="n">{i}</td><td class="h">{a}</td><td>{b}</td></tr>'
                  for i, (a, b) in enumerate(arts, 1))
    a4 = ('<div class="paper a4"><div class="stamp">예시</div><h2>입주박람회 특약이행각서</h2>'
          '<div class="sub">탕정 푸르지오 센터파크 입주박람회 참여업체 · 하자보수 이관 의무 이행</div>'
          f'<table><thead><tr><th>항목</th><th colspan="2">내용</th></tr></thead><tbody>{trs}</tbody></table>'
          '<div class="ag">위 업체는 상기 조건에 동의하며, 탕정 푸르지오 센터파크 입주박람회에 제안한 내용과 공고 게시사항 및 계약 내용을 성실히 이행할 것을 확약합니다.</div>'
          '<div class="dt">20&nbsp;&nbsp;&nbsp;년&nbsp;&nbsp;&nbsp;&nbsp;월&nbsp;&nbsp;&nbsp;&nbsp;일</div>'
          '<div class="sg"><i>업 체 명</i><span></span><i>사업자번호</i><span></span><i>대 표 자</i><span>(인)</span></div></div>')
    k["body"] = ('<div class="nb"><div class="docx" style="grid-template-columns:1fr 1.05fr">'
                 '<div class="bulx">'
                 '<div><b>9개 항을 서면으로</b><p>하자보수 이관 의무부터 지연 배상·민원 처리까지 문서로 약속받습니다.</p></div>'
                 '<div><b>서명한 업체만 참여</b><p>각서를 내지 않은 업체는 박람회에 들어올 수 없습니다.</p></div>'
                 '<div><b>업체가 도산해도</b><p>주관사가 동종업체로 하자보수를 이관하고, A/S 비용을 지급·처리합니다.</p></div>'
                 '</div><div class="pp">' + a4 + '</div></div></div>')
    k["kp"] = ("업체가 사라져도 [[하자보수 책임]]은 남도록 계약으로 묶어 둡니다.", "오른쪽은 각서 양식 예시 · 문구는 입예협 협의 후 확정")

    k = take("주요 클레임 품목과 [[보상 기준]]")[1]
    k["title"] = "주요 클레임 품목과 [[보상 기준]] (예시)"
    k["body"] = sub(k["body"], "건수: 과거 입주 시점 주요 클레임 접수 집계. 품목 구성은 단지 여건에 맞춰 조정합니다.",
                    "예시 — 건수는 과거 단지 입주 시점 주요 클레임 접수 집계입니다. 품목·보상 기준은 단지 여건과 입예협 협의로 정합니다.")

    # A 입주민 특화서비스 — 상품권 사용 안내 · 정회원 혜택 상세
    def rc(tag, nm, v, items, hl=False):
        li = "".join(f"<li>{_h.escape(x)}</li>" for x in items)
        return f'<div class="rc{" hl" if hl else ""}"><i>{tag}</i><h3>{nm}</h3><div class="v">{v}</div><ul>{li}</ul></div>'  # v는 코드에서만 넣는 문구(HTML 허용)
    SA = S8 + " · A 입주민 특화서비스"
    p_gift_rule = ("std", dict(sec=SA, title="박람회 상품권 [[사용 안내]]",
        lead="상품권은 박람회장에서 업체와 계약할 때 계약금으로 씁니다.",
        body='<div class="nb"><div class="ruls">'
             + rc("GIFT 01", "박람회 상품권", "정회원 30만원<br><small>(일반회원 20만원 + 정회원 추가 10만원)</small>",
                  ["박람회장에서 업체 계약 시 품목(업체)당 1매 사용", "같은 품목에 중복 사용 불가 (특정 입주민 5만원권과는 함께 사용 가능)",
                   "제외 품목: 가전, 브랜드 가구, 선반·잡물, 청소 단독 계약", "벽걸이TV는 20만원 이상 계약 시 사용"], True)
             + rc("GIFT 02", "특정 입주민 추가 상품권", "5만원 추가",
                  ["대상: 소년·소녀가장, 80세 이상 노부모 부양가정, 장애인, 다자녀(3자녀 이상), 다문화가정, 임산부",
                   "품목(업체) 제한 없이 사용", "박람회 상품권 1매와 함께 사용 가능"])
             + rc("GIFT 03", "백화점 상품권 · 현물", "10만원 현물 지급<br><small>(금액은 단지별 상이 · 입예협 협의)</small>",
                  ["안내부스에서 명부 작성 후 배부", "1세대 1회 교부 · 중복 발행 불가", "행사장 안에서 현금처럼 사용 · 박람회 상품권과 함께 사용 가능",
                   "상품권 종류는 상황에 따라 바뀔 수 있습니다"], True)
             + "</div></div>",
        kp=("사용 조건은 박람회 전 [[카페 공지와 현장 안내]]로 미리 알려 드립니다.", "세부 조건은 입예협 협의 후 확정")))
    mem = [("백화점 상품권", "10만원 현물 증정 (금액 상이)"), ("도어락 나노코팅", "생활방수 코팅 · 오염·물때 방지"),
           ("실링팬 50% 특가", "아크로(ACRO) BLDC 실링팬 정회원 특가"), ("우물 간접조명", "거실 우물천장 간접조명 지원"),
           ("갤러리조명 2구", "복도 매입등 2구 시공 지원"), ("피톤치드 항균", "편백 추출물 항균·탈취 시공"),
           ("인테리어 30% 할인", "인테리어 전문 업체 프로모션"), ("미세촘촘망 거실창", "거실창 안전 방충망 시공 지원"),
           ("홈케어 진드기 박멸", "열 살균 방식 · 약품 미사용"), ("욕실케어 1회", "곰팡이·물때 전문 장비 세정"),
           ("현관 줄눈", "현관 줄눈 시공 지원"), ("프리미엄 중문", "박람회 특가"),
           ("욕실 휴젠뜨", "제습·온풍·환기 욕실 가전 박람회 최저 특가"), ("화재보험 2년", "신청 세대 가입 지원 (보험사 협력)"),
           ("사전점검 할인", "사전점검 대행 최대 50% 할인"), ("경품 응모", "박람회 경품 추첨 응모")]
    half = len(mem) // 2

    def mtb(rows, s0):
        return G["table"](["NO", "혜택", "내용"], "".join(
            f'<tr><td class="n">{i:02d}</td><td class="k">{a}</td><td>{b}</td></tr>' for i, (a, b) in enumerate(rows, s0)), "xs")
    p_member = ("std", dict(sec=SA, title="정회원 혜택 [[상세]]",
        lead="정회원으로 박람회장을 방문한 세대가 받는 혜택입니다.",
        body='<div class="nb"><div class="sumx roomy">' + f'<div class="sb">{mtb(mem[:half], 1)}</div><div class="sb">{mtb(mem[half:], half + 1)}</div>' + "</div></div>",
        kp=("품목은 입예협 협의 후 [[조정 가능]]합니다.", "유상옵션과 겹치는 품목은 제외")))

    # 회사 조직도(본부장 10-07, 통합제안서 '06 회사 조직도') — 실명은 org_private.json(깃 제외)에서 읽는다
    import json, os
    op = os.path.join(os.path.dirname(os.path.abspath(__file__)), "org_private.json")
    org = json.load(open(op, encoding="utf-8")) if os.path.exists(op) else {
        "ceo": "○○○", "gm": ["주관사업 총괄 본부장", "○○○"],
        "teams": [[n, [["담당", "○○○"]]] for n in ("영업팀", "행사관리팀", "이벤트팀", "대외지원팀")]}
    ICON = {"영업팀": "SALES", "행사관리팀": "OPERATION", "이벤트팀": "EVENT", "대외지원팀": "SUPPORT"}
    SVG = {  # 금색 선 아이콘(장식)
        "영업팀": '<path d="M4 9h16v10H4z"/><path d="M9 9V6h6v3"/><path d="M4 13h16"/>',
        "행사관리팀": '<rect x="4" y="6" width="16" height="14" rx="2"/><path d="M4 10h16M9 4v4M15 4v4"/><path d="M9 15l2 2 4-4"/>',
        "이벤트팀": '<path d="M12 4l2.4 4.9 5.4.8-3.9 3.8.9 5.4L12 16.4 7.2 18.9l.9-5.4-3.9-3.8 5.4-.8z"/>',
        "대외지원팀": '<path d="M5 13v-1a7 7 0 0 1 14 0v1"/><rect x="3.5" y="13" width="4" height="6" rx="1.5"/><rect x="16.5" y="13" width="4" height="6" rx="1.5"/><path d="M18.5 19c0 1.5-2 2.5-5 2.5"/>'}
    tms = "".join(
        f'<div class="tm"><svg viewBox="0 0 24 24">{SVG.get(n, "")}</svg><i>{ICON.get(n, "")}</i><h3>{_h.escape(n)}</h3><ul>'
        + "".join(f"<li><span>{_h.escape(r)}</span><b>{_h.escape(nm)}</b></li>" for r, nm in mem_) + "</ul></div>"
        for n, mem_ in org["teams"])
    p_org = ("std", dict(sec="01. 회사소개", title="회사 [[조직도]]", lead="전문가로 구성된 조직, 효율적인 운영의 핵심입니다.",
        body=('<div class="nb"><div class="org">'
              f'<div class="ceo"><i>㈜엣지컴퍼니</i><b>CEO</b><span>{_h.escape(org["ceo"])}</span></div>'
              f'<div class="gmr"><div class="gm"><i>{_h.escape(org["gm"][0])}</i><b>{_h.escape(org["gm"][1])}</b></div></div>'
              f'<div class="tms">{tms}</div></div></div>'),
        kp="팀별로 역할을 나눠 [[수임부터 박람회·사후관리까지]] 함께합니다."))
    # 제출서류 07용 — 실명 없이 팀 구성 + 인원(본부장 10-08: 조직도는 제안서에서 빼고, 07은 공고상 '조직도 포함'이라 이름 없는 구성도)
    tms0 = "".join(f'<div class="tm"><svg viewBox="0 0 24 24">{SVG.get(n, "")}</svg><i>{ICON.get(n, "")}</i><h3>{_h.escape(n)}</h3></div>'
                   for n, _ in org["teams"])
    B.ORG_ANON = ("std", dict(sec="01. 회사소개", title="회사 [[조직 구성]]", lead="대표이사 아래 주관사업 총괄 본부장이 4개 팀을 이끕니다.",
        body=('<div class="nb"><div class="org">'
              '<div class="ceo"><i>㈜엣지컴퍼니</i><b>CEO</b><span>대표이사</span></div>'
              '<div class="gmr"><div class="gm"><i>주관사업</i><b>총괄 본부장</b></div></div>'
              f'<div class="tms">{tms0}</div></div></div>'),
        kp=("임직원 [[14명]] = 정규직(4대보험) 10명 + 인턴(프리랜서) 4명", "팀별 담당·인원은 협약 시 입예협에 명단으로 제출")))
    B.CSS += r"""
.org{flex:1;min-height:0;display:flex;flex-direction:column;align-items:center;justify-content:center}
.org .ceo{width:176px;height:176px;border-radius:50%;border:2px solid var(--gold2);box-shadow:0 0 0 6px rgba(200,168,106,.12),0 0 34px rgba(235,203,143,.22);
  display:flex;flex-direction:column;align-items:center;justify-content:center;background:radial-gradient(circle,#16304f,#0b1a2d)}
.org .ceo i{font-style:normal;font-size:14px;color:var(--sub)}
.org .ceo b{font-family:var(--serif);font-size:42px;color:var(--gold);line-height:1.1;margin:2px 0}
.org .ceo span{font-size:23px;font-weight:700;letter-spacing:.3em;padding-left:.3em}
.org .gmr{position:relative;width:100%;height:46px}
.org .gmr:before{content:'';position:absolute;left:50%;top:0;bottom:0;width:2px;background:var(--gold2)}
.org .gm{position:absolute;left:calc(50% + 40px);top:6px;display:flex;align-items:center;gap:14px;border:1.5px solid var(--gold2);border-radius:10px;padding:6px 16px;background:#0b1a2d}
.org .gm:before{content:'';position:absolute;right:100%;top:50%;width:40px;height:2px;background:var(--gold2)}
.org .gm i{font-style:normal;font-size:13px;color:var(--gold2);font-weight:700;padding-right:14px;border-right:1px solid rgba(255,255,255,.25)}
.org .gm b{font-size:18px;letter-spacing:.2em}
.org .tms{position:relative;width:100%;display:grid;grid-template-columns:repeat(4,1fr);gap:18px;padding-top:24px;flex:0 0 auto}
.org .tms:before{content:'';position:absolute;left:calc((100% - 66px) / 8);right:calc((100% - 66px) / 8);top:0;height:2px;background:var(--gold2)}
.org .tm{position:relative;border:1px solid rgba(200,168,106,.35);border-top:2px solid var(--gold2);border-radius:14px;padding:9px 16px 11px;background:linear-gradient(180deg,rgba(235,203,143,.09),rgba(255,255,255,.015) 45%)}
.org .tm:after{content:'';position:absolute;left:50%;top:-29px;width:10px;height:10px;margin-left:-4px;border-radius:50%;background:var(--gold);box-shadow:0 0 8px rgba(235,203,143,.7)}
.org .tm svg{display:block;width:26px;height:26px;margin:0 auto 2px;fill:none;stroke:var(--gold);stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}
.org .gm{box-shadow:0 0 18px rgba(235,203,143,.15)}
.org .tm:before{content:'';position:absolute;left:50%;top:-26px;width:2px;height:26px;background:var(--gold2)}
.org .tm>i{display:block;font-style:normal;font-size:11.5px;letter-spacing:.26em;color:var(--gold2);font-weight:700;text-align:center}
.org .tm h3{font-size:19px;font-weight:800;color:var(--gold);text-align:center;margin:1px 0 6px}
.org .tm ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:5px}
.org .tm li{display:grid;grid-template-columns:64px 1fr;border:1px solid rgba(200,168,106,.35);border-radius:8px;overflow:hidden}
.org .tm li span{background:rgba(200,168,106,.16);color:var(--gold);font-size:13.5px;font-weight:700;text-align:center;padding:3px 0}
.org .tm li b{font-size:15px;text-align:center;padding:3px 0;letter-spacing:.06em}
"""

    # 실적 기간은 전신 실적 포함(본부장 10-08)
    k = take("숫자로 보는 [[엣지컴퍼니]]")[1]
    k["lead"] = sub(k["lead"], "8년간 쌓인 운영 데이터", "전신 실적을 포함해 8년간 쌓인 운영 데이터")
    k = take("주관 [[성공사례]] · 수임실적")[1]
    k["lead"] = sub(k["lead"], "2018년 첫 단지부터", "2018년 첫 단지(전신 실적 포함)부터")

    # 박람회장 배치와 인원 운영(본부장 10-08: 입예협이 인원 배치를 중요하게 봄) — 인원 수는 56쪽 운영 준비 표와 같음
    def zn(area, name, desc, staff="", cls=""):
        st = f'<b class="st">{staff}</b>' if staff else ""
        return f'<div class="z {cls}" style="grid-area:{area}"><h4>{name}{st}</h4><p>{desc}</p></div>'
    staff = [("주차 안내요원", 5), ("입구 체크인·입예협 부스 도우미", 3), ("보안요원", 2), ("구급요원", 1),
             ("카페테리아", 3), ("어린이 편의시설", 4), ("이벤트(네일·타로·캐리커처)", 3)]
    tot = sum(n for _, n in staff)
    p_floor = ("std", dict(sec="06. 입주박람회", title="박람회장 배치와 [[인원 운영]] (안)",
        lead="방문 동선을 따라 구역마다 담당 인원을 둡니다. 배치는 행사장 확정 후 입예협과 확정합니다.",
        body=('<div class="nb"><div class="fpx"><div class="fp">'
              + zn("kids", "키즈존", "어린이 편의시설", "4명")
              + zn("brand", "브랜드 존", "가전 · 가구 · 렌탈")
              + zn("cafe", "카페테리아", "휴게 · 음료", "3명")
              + zn("own", "직영 품목 존", "조명 · 커튼 · 실링팬")
              + zn("coun", "시공 · 판매 품목 존", "청소·줄눈·탄성·방충망 · 인테리어 · 가전·가구 · 공개 단가표 그대로", "", "hl")
              + zn("sign", "상담·계약 데스크", "공개 단가표 그대로 계약")
              + zn("build", "휴게 · 수유실", "가족 휴게 · 유모차 대여")
              + zn("event", "이벤트 · 경품존", "네일 · 타로 · 캐리커처", "3명")
              + zn("entry", "입구 · 체크인 · 입예협 부스", "정회원 등록 · 가입 안내 · 방문 선물 · 주관사 운영팀", "도우미 3명", "ent")
              + zn("safe", "안전 · 구급", "보안 2 · 구급 1 · 119 연계", "3명", "sf")
              + zn("park", "주차장 · 외부 동선", "차량 유도 · 하역 구역 분리", "5명", "pk")
              + '</div><div class="fps">'
              + '<div class="tot"><i>현장 배치 인원 (안)</i><b>' + str(tot) + '<small>명</small></b><span>+ 주관사 운영팀 상주 · 행사 규모에 따라 변동</span></div>'
              + '<ul>' + "".join(f'<li><span>{_h.escape(a)}</span><b>{n}명</b></li>' for a, n in staff) + '</ul>'
              + '<div class="bdg"><span>영업배상 책임보험 가입</span><span>119 연계 · 구급차 대비</span><span>전 인원 금색 명찰(직책·이름)</span><span>금·토·일 3일 운영</span></div>'
              + '</div></div></div>'),
        kp=("입예협이 가장 먼저 묻는 [[인원 배치]] - 구역마다 담당을 정해 둡니다.", "인원은 행사 규모에 따라 변동 · 타 단지 운영 기준(안)")))
    B.CSS += r"""
.fpx{display:grid;grid-template-columns:1.6fr 1fr;gap:22px;flex:1;min-height:0}
.fp{display:grid;gap:8px;grid-template-columns:1fr 1.15fr 1.15fr 1fr;grid-template-rows:repeat(3,1fr) .82fr .62fr;
  grid-template-areas:"kids brand brand cafe" "own coun coun sign" "build coun coun event" "safe entry entry event" "park park park park";
  border:1.5px dashed rgba(200,168,106,.55);border-radius:14px;padding:12px;min-height:0;
  background:repeating-linear-gradient(0deg,rgba(255,255,255,.025) 0 1px,transparent 1px 22px),repeating-linear-gradient(90deg,rgba(255,255,255,.025) 0 1px,transparent 1px 22px)}
.fp .z{border:1px solid var(--line);border-radius:9px;padding:8px 10px;background:rgba(13,30,51,.85);display:flex;flex-direction:column;justify-content:center;min-height:0}
.fp .z h4{font-size:14px;font-weight:800;display:flex;justify-content:space-between;align-items:center;gap:6px}
.fp .z p{font-size:11.5px;color:var(--sub);margin-top:3px;line-height:1.35}
.fp .z .st{font-size:11.5px;font-weight:800;color:#0d1e33;background:var(--gold);border-radius:99px;padding:2px 8px;white-space:nowrap}
.fp .z.hl{border:1.5px solid var(--gold2);background:linear-gradient(180deg,rgba(235,203,143,.18),rgba(13,30,51,.9));align-items:center;text-align:center}
.fp .z.hl h4{font-size:22px;color:var(--gold);flex-direction:column}
.fp .z.hl p{font-size:14px;line-height:1.5;margin-top:8px;max-width:88%}
.fp .z.ent{border-color:rgba(235,203,143,.6)}
.fp .z.sf{border-color:rgba(255,120,110,.55)}
.fp .z.pk{background:rgba(255,255,255,.04);border-style:dashed}
.fps{display:flex;flex-direction:column;gap:10px;min-height:0}
.fps .tot{border:1px solid rgba(235,203,143,.6);border-radius:12px;padding:12px 16px;background:linear-gradient(180deg,rgba(235,203,143,.14),rgba(235,203,143,.02))}
.fps .tot i{display:block;font-style:normal;font-size:12px;letter-spacing:.16em;color:var(--gold2);font-weight:700}
.fps .tot b{font-size:44px;font-weight:800;color:var(--gold);line-height:1.05}
.fps .tot b small{font-size:20px;margin-left:3px}
.fps .tot span{font-size:13.5px;color:var(--sub);margin-left:8px}
.fps ul{list-style:none;margin:0;padding:0;border-top:1px solid rgba(200,168,106,.35)}
.fps li{display:flex;justify-content:space-between;font-size:14px;color:var(--sub);padding:5px 2px;border-bottom:1px dashed rgba(255,255,255,.12)}
.fps li b{color:var(--ink);font-variant-numeric:tabular-nums}
.fps .bdg{display:flex;flex-wrap:wrap;gap:6px;margin-top:auto}
.fps .bdg span{font-size:12.5px;border:1px solid rgba(200,168,106,.55);border-radius:99px;padding:4px 10px;color:var(--gold)}
"""

    # 교차 검수 반영(10-07): 법령명 · 줄바꿈 · 증권 확인 기준
    k = take("[[조명 수직계열화]] · 유통 단계 없는 공급")[1]
    k["body"] = sub(k["body"], "전기용품 안전관리법 기준", "전기용품 및 생활용품 안전관리법 기준")
    k["body"] = sub(k["body"], "결선·설치까지 직접", "결선과 설치까지 직접")
    k = take("[[4단계]] 공개 심사 프로세스")[1]
    k["body"] = sub(k["body"], "</em>로 동시 접수.", "</em> 동시 접수.")
    k["body"] = sub(k["body"], "사후관리 시스템 완비.", "사후관리 체계 완비.")

    # '조명 회사' 이미지 대신 '전기공사업 면허를 갖춘 주관사'로(본부장 10-07)
    k = take("커뮤니티·공용부 [[조명 개선]]")[1]
    k["kp"] = "전기공사업 면허를 갖춘 주관사 — [[제안만 하고 끝내지 않습니다.]]"

    # 문주·경관조명 장 — 본부장 제공 이미지로 교체, 사진을 크게(10-07)
    k = take("문주·경관조명 [[컨설팅]]")[1]
    def ph(img, cap, sub_):
        return (f'<figure><img src="assets_ins/{img}.jpg" alt=""><figcaption>{cap}<small>{sub_}</small></figcaption></figure>')
    k["body"] = ('<div class="nb"><div class="gal lxg">'
                 + ph("tj_gate_night", "문주 · 진입부 조명", "간접조명 · 사인 조명 · 보행 동선 연출")
                 + ph("tj_facade_night", "단지 경관조명", "동 외벽 라인조명 · 단지 야간 경관")
                 + '</div><div class="lxs">'
                 '<div><b>문주 조명</b><p>진입부 문주의 간접조명·사인 조명 연출안을 제안합니다.</p></div>'
                 '<div><b>경관조명</b><p>동 외벽 라인조명 등 야간 경관 개선안을 검토합니다.</p></div>'
                 '<div><b>협의 후 적용</b><p>공용부는 입예협·관리주체 협의를 거쳐 범위를 정합니다.</p></div>'
                 '</div></div>')
    k["kp"] = ("제안에 그치지 않고 [[시공 가능 여부]]까지 함께 검토합니다.", "전기공사업 제 울산-00821호 · 사진은 연출 예시 이미지")
    B.CSS += r"""
.gal.lxg{grid-template-columns:1fr 1fr;gap:16px;flex:1 1 0}
.gal.lxg figcaption{font-size:17px;padding:30px 18px 12px}
.gal.lxg figcaption small{font-size:13.5px}
.lxs{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.lxs>div{border-left:2px solid var(--gold2);padding:2px 0 2px 14px}
.lxs b{font-size:17px}
.lxs p{font-size:14.5px;color:var(--sub);margin-top:4px;line-height:1.45}
"""

    # A·B·C 패키지 표지 장
    def pkg(L, name, en, desc, groups, cols=2):
        rt = ""
        n = 0
        for gh, items in groups:
            li = ""
            for a, b in items:
                n += 1
                li += f'<li><div class="no">{n:02d}</div><div><b>{_h.escape(a)}</b><span>{_h.escape(b)}</span></div></li>'
            rt += (f'<div class="gh">{gh}</div>' if gh else "") + f'<ul style="grid-template-columns:repeat({cols},1fr)">{li}</ul>'
        return (f'<div class="nb"><div class="pkp"><div class="lf"><div class="L">{L}</div><h3>{name}</h3><i>{en}</i>'
                f'<p>{desc}</p></div><div class="rt">{rt}</div></div></div>')
    pkA = ("std", dict(sec=SA, title="A 패키지 · [[입주민 특화서비스]]", lead="입주민 한 세대 한 세대가 직접 받는 혜택과 서비스입니다.",
        body=pkg("A", "입주민 특화서비스", "FOR RESIDENTS", f"세대당 {fund}만원 혜택 패키지 A — 박람회 혜택부터 사전점검·실측·VR·3D까지 입주민이 직접 받는 혜택으로 구성합니다.",
                 [("박람회 혜택", [("박람회 혜택", "백화점 상품권 10만원(현물) · 박람회 상품권 30만원 · 현장할인 10%"), ("정회원 혜택", "정회원 전용 품목 특가·시공 지원"),
                                                ("사은품", "원터치 말발굽 · 업체 계약 사은품"), ("경품 이벤트", "대형·소형 가전 · 업체 경품 추첨")]),
                  ("입주 준비 서비스", [("사전점검 혜택", "대행 최대 50% 할인 · 당첨 세대 동행"), ("실측 & 샘플하우스", "타입별 실측 사이즈 · 샘플하우스"),
                                       ("항공 VR 촬영", "단지 주변 입지 확인"), ("3D 홈스타일링", "대표 타입 맞춤 공간 제안")])]),
        kp=("다음 장부터 [[A 항목]]을 하나씩 보여 드립니다.", "15만원 패키지 선택 항목")))
    pkB = ("std", dict(sec=S8 + " · B 협의회 단지발전지원", title="B 패키지 · [[협의회 단지발전지원]]", lead="입예협 업무와 하자 대응을 주관사 인력이 함께합니다.",
        body=pkg("B", "협의회 단지발전지원", "FOR THE COUNCIL", "공사 품질 점검부터 위임장·민원·사전점검 당일 지원까지, 입예협이 직접 하실 일을 줄입니다.", [("", Bk)], 3),
        kp=("다음 장부터 [[B 항목]]을 하나씩 보여 드립니다.", "15만원 패키지 선택 항목")))
    p_badd = ("std", dict(sec=S8 + " · B 협의회 단지발전지원", title="현장 안전 · 공용부 위생까지 [[함께 챙깁니다]]",
        lead="품질 점검·보고서 외에 입예협 실무와 공용부 위생 관리도 지원합니다.",
        body=B.tiles([
            dict(lb="02 · SAFETY", nm="건설현장 안전점검", ds="입주 전 건설현장 안전점검을 실시하고 결과를 협의 자료로 정리합니다."),
            dict(lb="04 · VOICE", nm="의견 전달 지원", ds="입예협 의견이 입예협·시공사에 정확히 전달되도록 공문·자료·피켓·현수막을 지원합니다."),
            dict(lb="05 · ANALYSIS", nm="공정·하자 분석 & 솔루션", ds="공정별 하자(주차장 균열·누수, 창틀 파손, 보양 누락, 타일 파손 등)를 전문 엔지니어가 검토하고 보수 방안을 제시합니다."),
            dict(lb="13 · COATING", nm="공용부 항균나노코팅", ds="협의회와 논의 후 엘리베이터 버튼·핸드레일 등 손이 닿는 공용부에 항균 나노코팅을 지원합니다."),
            dict(lb="14 · CESCO", nm="세스코 특수해충 점검", ds="2025.11 MOU. 협의회 지정 동별 대표세대를 전문가가 방문 진단하고, 해충 발견 시 건설사 협의용 자료를 만듭니다."),
            dict(lb="15 · AIR", nm="공용부 새집증후군 지원", ds="공용부 항균·탈취 관리를 지원합니다. 범위는 입예협·관리주체와 협의합니다."),
        ], cols=3, rows_n=2),
        kp=("입예협이 필요한 항목을 골라 [[15만원 범위 안에서]] 구성합니다.", "번호 = B 패키지 목록 번호 · 공용부 작업은 입예협·관리주체 협의")))
    pkC = ("std", dict(sec=S8 + " · C 단지지원 컨설팅", title="C 패키지 · [[단지지원 컨설팅]]", lead="입주 후 매일 쓰는 공용부·커뮤니티의 가치를 높입니다.",
        body=pkg("C", "단지지원 컨설팅", "FOR THE COMPLEX", "전기공사업 면허를 갖춘 주관사라, 제안에서 끝내지 않고 시공 가능 여부까지 검토합니다. 공용부는 입예협·관리주체 협의 전제.", [("", C)]),
        kp=("다음 장부터 [[C 항목]]을 하나씩 보여 드립니다.", "15만원 패키지 선택 항목")))

    # ------------------------------------------------ 재배치
    T = take
    d01 = T("엣지컴퍼니는 [[이런 회사]]입니다.")
    d01[1]["n"] = "01"
    d03 = T("업체 선정이 [[주관사의 본질]]입니다.")
    d03[1]["n"] = "03"
    d03[1]["bl"] = ["품목 수요조사"] + [x for x in d03[1]["bl"] if "수요조사" not in x]  # 본부장 10-08
    d04 = T("사고가 나도 [[입주민이 먼저]] 보상받습니다")
    d04[1]["n"] = "04"
    d04[1]["bl"] = [x for x in d04[1]["bl"] if "콜센터" not in x]
    d07 = T("탕정 푸르지오 센터파크를 위한 [[맞춤 제안]]")
    d07[1]["n"] = "07"
    d07[1]["bl"] = ["단지 이해 · 입주민 건의", "공고 업무 8개 · 자격 22개 대응", "추진 일정 · 17개월 관리", "조경·경관조명 특화"]

    ch = [
        ("01. 회사소개", [d01] + [T(x) for x in [
            "숫자로 보는 [[엣지컴퍼니]]", "해마다 쌓이는 [[누적 주관 단지]]", "[[본사 사옥]] 운영 · 자본금 2억", "회사 개요와 [[법인 서류]]",
            "재무·납세·고용 [[증빙 원본]]", "공인된 [[자격과 신뢰]]", "제휴 · 면허 · 인증 [[원본 서류]]"]] + [B.ORG_ANON] + [T(x) for x in ["전국 지사망 · [[직영 4곳 + 협력 8곳]]",
            "[[직영 4곳]]이 지키는 12개 지사망", "왜 [[직영]]이어야 합니까"]] + [p_mission] + [T(x) for x in [
            "주관 [[성공사례]] · 수임실적", "[[2,000세대 이상]] 초대형 단지를 맡아 왔습니다", "[[대단지]] 운영 경험", "2023년 이후 수임 단지",
            "사진으로 보는 주관 단지 [[2018–2022]]", "사진으로 보는 주관 단지 [[2023–2026]]", "한 단지가 아니라 [[한 신도시]]를 맡습니다",
            "[[사송 · 에코델타]] 단지별 주관 현황", "타 단지 협의회의 [[추천과 감사]]", "행사 밖에서도 [[현장 지원]]", "지역과 함께하는 [[나눔 활동]]"]]),
        ("02. 마케팅전략", [dv("02", "입주민이 [[먼저 알고]] 찾아옵니다", ["입예협 카페 홍보 콘텐츠", "사전점검 언박싱 영상", "드론 영상 · 검색·언론", "현수막·전단·버스 광고"])]
         + [T("입예협 카페 [[홍보 콘텐츠]] 제작"), T("사전점검 [[언박싱 영상]]과 현장 홍보")]),
        ("03. 업체선정", [d03, T("공동구매 [[품목]]을 한눈에")] + [T(x) for x in [
            "[[4단계]] 공개 심사 프로세스", "업체 [[심사 기준]]과 계약 원칙", "참여업체 [[서비스 교육]]", "검증된 [[인근 지역업체]] 선정 원칙",
            "공동구매 단가를 지키는 [[4가지 장치]]", "[[최저가 차액 10배]] 보상", "실적 비례 [[추가할인]] 구조", "입주민 [[자금]]을 먼저 지킵니다",
            "품목별 [[취소 기한]]과 환불 절차"]]),
        ("04. 하자보증", [d04] + [T(x) for x in [
            "입주민을 지키는 [[3중 안전망]]", "이행보증보험 [[2년 · 최대 10억]]", "보증보험증권 [[제출과 확인]]", "참여업체 [[하자보증]] 체계",
            "입주박람회 [[특약이행각서]] (예시)", "주요 클레임 품목과 [[보상 기준]] (예시)", "참여업체 [[패널티 3단계]]"]]),
        ("05. 주관 콜센터", [dv("05", "클레임은 [[주관사가 먼저]] 받습니다", ["주관 콜센터 · 선보상", "하자 예치금 최대 1억", "클레임 처리 흐름 · CRM", "입주민 후기 · 실시간 응대"])]
         + [T("주관 [[콜센터]]와 선보상"), p_deposit] + [T(x) for x in ["클레임 [[처리 흐름]]과 CRM 관리", "입주민 후기 · [[실시간 응대]] 화면"]]),
        ("06. 입주박람회", [dv("06", "확인하고 비교하는 [[입주박람회]]", ["운영 계획 · 행사장 대관", "배치·인원 운영 · 편의시설", "온라인 박람회 · 라이브커머스", "실제 박람회 현장"])]
         + [T(x) for x in ["입주박람회 [[운영 계획]]", "행사장 대관과 [[운영 준비]]"]] + [p_floor] + [T(x) for x in ["가족이 머무는 [[편의시설]]",
                           "못 오셔도 [[괜찮습니다]]", "실제 박람회 [[현장]]"]]),
        ("07. 탕정 푸르지오 센터파크 맞춤 제안", [d07] + [T(x) for x in [
            "탕정 푸르지오 센터파크, [[이런 단지]]입니다", "이 단지라서 [[먼저 챙길 것]]", "입주민 건의, [[관리표로]] 끝까지 챙깁니다",
            "중앙광장 · 물의정원, [[밤까지]] 살피겠습니다", "입주까지 17개월, [[빈틈없이]] 관리합니다", "탕정 푸르지오 센터파크 [[특화 제안]]",
            "공고 업무 범위 [[8개 항목]] 대응", "입찰 참가 자격 [[22개 항목]] 대응 ①", "입찰 참가 자격 [[22개 항목]] 대응 ②",
            "입주민 개인정보는 [[행사 운영에만]] 씁니다", "하자 접수, [[책임부터]] 나눕니다", "보고는 [[항목과 시점]]을 정해 둡니다",
            "선정부터 입주까지 [[추진 일정]] (안)", "품목별 [[예상 참가 업체]]"]]),
        ("08. 혜택안내 · 발전지원 15만원", [dv("08", "입주민과 협의회를 [[함께]] 챙깁니다",
            [f"세대당 {fund}만원 — 현금 또는 패키지 선택", "A 입주민 특화서비스", "B 협의회 단지발전지원", "C 단지지원 컨설팅"]),
            T(kind="hi_fund"), p_choice, p_pack, p_examples]),
        ("08. 혜택안내 · A 입주민 특화서비스", [pkA] + [T(x) for x in ["방문 세대 [[박람회 상품권 · 현장 혜택]]"]] + [p_gift_rule]
         + [T("정회원 전용 [[추가 혜택]]"), p_member, T("사진으로 보는 [[정회원 혜택]]"), T("박람회 [[사은품 · 경품]]")]
         + [T(x) for x in ["입주 전에 [[미리 보는]] 우리 집", "사전점검 대행, [[이렇게 봅니다]]"]] + [T(kind="pricing")]),
        ("08. 혜택안내 · B 협의회 단지발전지원", [pkB] + [T(x) for x in [
            "공용부 [[구조·시공 품질]] 점검", "보이지 않는 [[하자]]까지 확인합니다", "입주 전에 보는 [[일조 시뮬레이션]]", "[[조경·착공]] 분석보고서",
            "도면·하자 분석 [[보고서 샘플]]", "입주 전부터 [[끝까지]] 붙어 있습니다", "사전점검 당일 [[현장 지원]]", "위임장, 이제 [[휴대폰으로]] 받습니다",
            "사전점검 세미나, [[영상으로]] 다시 봅니다"]] + [p_badd]),
        ("08. 혜택안내 · C 단지지원 컨설팅", [pkC] + [T(x) for x in [
            "커뮤니티·공용부 [[조명 개선]]", "문주·경관조명 [[컨설팅]]", "피트니스·키즈 공간 [[개선 제안]]", "전기차 충전 [[인프라 검토]]"]]),
        ("09. 차별화 포인트", [T(kind="divider_lx"), T(kind="landscape"), T("[[조명 수직계열화]] · 유통 단계 없는 공급")]),
        ("10. 특화서비스 요약", [dv("10", "한눈에 보는 [[특화서비스]]", ["A 입주민 특화서비스", "B 협의회 단지발전지원 · C 단지지원 컨설팅", "안전망 · 업체선정 · 홍보", "탕정 푸르지오 센터파크 맞춤"]),
                                p_s1, p_s2, p_s3, T("탕정 푸르지오 센터파크에 드리는 [[핵심 혜택 6가지]]")]),
    ]
    drop = [T(kind="hi_money"), T("발전지원금은 [[이렇게 쓰입니다]]"), T("협의회 전용 [[8가지 무상 단지지원]]"), T("입예협·입주민 [[지원 한눈에]]"),
            T("협의회 전용 [[단지 지원]]"), T("입주민에게 [[직접]] 돌아가는 혜택"), T("기록이 [[증명]]합니다."), T("하루가 [[즐거운]] 박람회")]
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

    # ------------------------------------------------ 쪽별 시각화(아이콘·도식·사진, 본부장 10-08)
    import vis
    vis.apply(B, D, take, sub)

    B.p_divider_lx = lambda: sub(G["B_p_divider_lx"](), '<div class="n">02</div>', '<div class="n">09</div>')

    # ------------------------------------------------ 목차 10장(5열 × 2)
    G["TOC4"][:] = [
        [("01", "회사소개", ["숫자·누적 실적", "법인·재무 서류 · 인증", "지사망 · 직영 운영", "수임실적 · 대단지", "추천·감사 · 나눔"]),
         ("06", "입주박람회", ["금·토·일 3일 · 대관", "배치·인원 운영", "편의시설 · 온라인", "박람회 현장"])],
        [("02", "마케팅전략", ["카페 홍보 콘텐츠", "사전점검 언박싱", "드론 · 검색 · 언론", "현수막 · 버스 광고"]),
         ("07", "탕정 푸르지오 센터파크 맞춤", ["단지 이해 · 입주민 건의", "업무 8개 · 자격 22개", "일정 · 17개월 관리", "예상 참가 업체"])],
        [("03", "업체선정", ["공동구매 품목 · 수요조사", "4단계 공개 심사", "인근 지역업체 선정", "최저가 차액 10배", "계약·환불 보호"]),
         ("08", "혜택안내", [f"{fund}만원 · 현금 또는 패키지", "A 입주민 특화서비스", "B 협의회 단지발전지원", "C 단지지원 컨설팅"])],
        [("04", "하자보증", ["이행보증보험 최대 10억", "업체 하자보증 · 특약이행각서", "클레임 보상 기준", "패널티 3단계"]),
         ("09", "차별화 포인트", ["경관조명 설계·생산·시공", "조명 수직계열화"])],
        [("05", "주관 콜센터", ["콜센터 · 선보상", "하자 예치금 최대 1억", "클레임 처리 · CRM", "후기 · 실시간 응대"]),
         ("10", "특화서비스 요약", ["A 입주민 특화서비스", "B 단지발전 · C 컨설팅", "안전망 · 업체 · 홍보", "핵심 혜택 6가지"])],
    ]
    G["TOC_CLS"] = "toc5"
