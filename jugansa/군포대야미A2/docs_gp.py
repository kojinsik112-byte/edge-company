# -*- coding: utf-8 -*-
"""군포 대야미 A-2블록 신혼희망타운 입주박람회 주관사 입찰 — 별첨 1 제출서류 1 ~ 13 생성 · PDF 1개 병합(A4 세로).

공고: 제출서류를 PDF로(제출 방법 4) · deyami_a2@naver.com · 마감 2026.11.02(월) 12:00 · 서식 없음(1 · 11 · 12 · 13 = 자유 양식).
  00 제출서류 목록(번호 · 쪽 · 발급일)
  1  입찰참가신청서(자유 · 직인)                 2  사업자등록증 사본(2026.10.23)
  3  법인 등기부등본(2026.10.23 · 대표 주소 가림)  4  인감증명서(2026.10.26 · 가림) + 사용인감계(법인인감 실물 날인 스캔)
  5  법인 사업자 통장 사본                          6  국세 · 지방세 완납(납세) 증명서(2026.10.23)
  7  4대 사회보험 가입자 명부(2026.10.23 · 13명 · 성명 가운데 글자 · 주민번호 가림)
  8  최근 3년 주관사 실적 증빙 = 안내 + A NICE 연혁 발췌 + B 공식 행사일정 · 카페 공지 캡처 + C 주관사 협약서 3건
  9  입주박람회 제안서 = build_gp.py 밝은 시안
  10 컴플레인 · A/S 관리 프로세스 제안서(취소 · 환불 규정 포함) = 표지 + 제안서 해당 쪽 발췌
  11 청렴 계약 이행각서 · 12 비밀 유지 서약서 · 13 서류 미반환 · 이의 미제기 서약서(자유 · 직인)
  자격 6 증빙 붙임: 안내 · SGI 계약보증증권 발급 이력(가림) · KB 영업배상책임보험 증권 · 건축 기술 자문 업무협약서(요지 + 원본 축소 · 을 정보 가림)(10-29 재확인 · 10-30 축소)
  선택 자료(필수 아님): NICE 기업신용평가 전문(가림) · 전기공사업 등록증 · ISO 인증서

증빙 원본: 나리벡 최종 제출본(2026.10.26 · 가림 · 검증 끝)의 쪽을 그대로 쓰고, 나리벡 건명이 박힌 표지 · 안내 쪽은 군포용으로 새로 만들거나 글자만 바꾼다.
날인: 법인인감은 디지털로 만들지 않는다(규칙 4) — 사용인감계는 사용인감 칸만 디지털 직인 · '작업/…_사용인감계_날인출력용.pdf'를 출력 → 법인인감 칸 · 대표자 (인) 실물 날인 → 스캔 →
      SEAL_SCAN 경로에 두고 다시 실행. 스캔이 없으면 출력용을 넣은 '_날인전' 통합본만 만든다(제출 금지).
출력: 작업/(중간 · 번호별 · 출력용) · 제출본/(통합 PDF 1개 · 메일용 저용량본 없음)
사용: python docs_gp.py <투명 직인.png> [--final]
"""
import html
import os
import pathlib
import re
import subprocess
import sys

import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "요약제안서")]
import data as D  # noqa: E402
from build import find_chrome  # noqa: E402

e = html.escape
ST = D.SITE
SITE = ST["name"]
TO = f"{SITE} 입주예정자협의회"
CASE = f"{SITE} 입주박람회 주관사 선정 입찰"
NOTICE = D.NOTICE

NR = r"C:\본부장\05주관사 입찰공고\20261025_롯데캐슬 나리벡시티\제안자료_주식회사 엣지컴퍼니\제안자료_주식회사 엣지컴퍼니"
EVD = r"C:\본부장\02입찰공고필요양식(대외비)"
BANK = os.path.join(EVD, "3.법인 사업자등록증&통장사본", "통장사본.pdf")
ELEC = os.path.join(EVD, "11.기타", "전기공사업 등록증.pdf")
ISO = os.path.join(EVD, "11.기타", "[글로벌시스템인증원]주식회사 엣지컴퍼니ISO인증.pdf")
DNB = r"C:\본부장\협력사_협약서\20261028_디엔비파트너스건축사사무소\업무협약서_엣지컴퍼니_디엔비파트너스건축사사무소_20261028_양측날인_2쪽을정보모자이크_v2.pdf"   # 본부장 10-29 원본 스캔 → 1쪽 업체명 공개 · 2쪽 을 칸만 모자이크
PROPOSAL = os.path.join(HERE, "엣지컴퍼니_군포대야미A2_입주박람회_주관사_제안서_밝은시안.pdf")
WORK = os.path.join(HERE, "작업")
SGI_PNG = os.path.join(HERE, "assets_ins", "os_sgi_bond_masked.png")   # 서울보증 계약보증증권 가림본(경산 · 엘리프와 같은 파일)
KB = r"C:\본부장\05주관사 입찰공고\20261024_창릉신도시 S5\엣지컴퍼니_고양창릉S5_제출서류\12_영업배상책임보험_증서\엣지컴퍼니_고양창릉S5_12_영업배상책임보험_증서.pdf"   # KB 2026.10.14 ~ 2027.10.14
REG_MASK = [(203, 163, 556, 177), (30, 176, 50, 187)]   # 등기부 2/2쪽 대표이사 주소(엘리프 docs_el 좌표 · 같은 10.23 발급본)
KB_MASK = [(365, 790, 445, 801)]                        # KB 증권 아래 영업담당자 휴대번호
TAX_PHONE = (119, 228.5, 196, 239)                      # 지방세 납세증명서(6번 2쪽) '전화번호(휴대전화)' 칸의 대표 휴대번호 — 그림이라 좌표로(법정 10-30 · 본부장 '응')
DNB_DATE = "2026년 10월 26일"                             # 디엔비 업무협약 체결일(본부장 10-30) — 협약서에 날짜 칸이 없어 본문 밖 위 여백에 표기
SUBMIT = os.path.join(HERE, "제출본")
SEAL_SCAN = getattr(D, "GP_SEAL_SCAN", None) or os.path.join(WORK, "사용인감계_날인스캔.pdf")   # 본부장 실물 날인 스캔 1쪽
OUT_NAME = f"{D.FILE_TITLE}.pdf"
GARBAGE = 1   # 크롬 PDF끼리 합칠 때 2 이상이면 글꼴이 섞여 글자가 깨진 일이 있음(엘리프 10-26)

CSS = r"""
@page{size:A4;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Malgun Gothic','맑은 고딕',sans-serif;color:#111;font-size:12.5pt;line-height:1.6}
.pg{width:210mm;height:297mm;padding:20mm 22mm 16mm;position:relative;page-break-after:always;overflow:hidden}
.pg:last-child{page-break-after:auto}
.lb{font-size:9.5pt;color:#9a7a40;font-weight:700;letter-spacing:.06em;border-bottom:1.2px solid #c8a86a;padding-bottom:4px;margin-bottom:9mm;display:flex;justify-content:space-between}
h1{font-size:22pt;text-align:center;letter-spacing:.5em;margin:2mm 0 8mm;font-weight:800}
h2{font-size:15pt;margin:2mm 0 4mm;font-weight:800}
table.f{width:100%;border-collapse:collapse;margin-bottom:9mm}
table.f th,table.f td{border:1px solid #333;padding:7px 10px;font-size:11.5pt;vertical-align:middle}
table.f th{background:#f3efe6;width:30%;text-align:center;font-weight:700}
ol.c{margin:0 0 0 1.4em}ol.c li{margin:0 0 3.2mm;padding-left:2px}
p.b{text-indent:.6em;margin-bottom:5mm}
.dt{text-align:center;font-size:13pt;margin:8mm 0 6mm;letter-spacing:.1em}
.sg{margin-left:auto;width:96mm;font-size:12.5pt;line-height:2.1;position:relative}
.sg .in{position:relative;display:inline-block}
.sg .seal{position:absolute;width:21mm;height:21mm;right:-17mm;top:-7.5mm;opacity:.92}
.to{text-align:center;font-size:15pt;font-weight:800;margin-top:8mm;letter-spacing:.06em}
.nt{position:absolute;left:22mm;right:22mm;bottom:14mm;font-size:9pt;color:#555;line-height:1.5}
table.l{width:100%;border-collapse:collapse;font-size:10pt;line-height:1.45}
table.l th,table.l td{border-bottom:1px solid #bbb;padding:4px 6px;text-align:left;vertical-align:top}
table.l th{border-bottom:1.5px solid #9a7a40;color:#7a5c25;font-size:9.5pt}
table.l td.n{width:9mm;font-weight:800;color:#9a7a40;text-align:center}
table.l td.r{text-align:right;white-space:nowrap}
.gam{display:grid;grid-template-columns:1fr 1fr;border:1px solid #333;margin:0 0 7mm}
.gam div{border-right:1px solid #333}.gam div:last-child{border-right:0}
.gam b{display:block;text-align:center;background:#f3efe6;border-bottom:1px solid #333;padding:6px;font-size:11.5pt}
.gam span{display:block;height:28mm}
.box{border:1.2px solid #c8a86a;border-radius:6px;padding:5mm 6mm;background:#fbf8f1;font-size:11pt;margin-bottom:6mm}
.cv{display:flex;flex-direction:column;justify-content:center;height:100%}
.cv .no{font-size:13pt;color:#9a7a40;font-weight:800;letter-spacing:.2em}
.cv .tt{font-size:25pt;font-weight:800;margin:4mm 0 6mm;line-height:1.35}
.cv .ds{font-size:11.5pt;color:#333}
"""


def page(label, body, note=""):
    nt = f'<div class="nt">{note}</div>' if note else ""
    return f'<section class="pg"><div class="lb"><span>{e(label)}</span><span>주식회사 엣지컴퍼니 · 입주박람회 주관사</span></div>{body}{nt}</section>'


def doc(title, pages):
    return f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{e(title)}</title><style>{CSS}</style></head><body>{"".join(pages)}</body></html>'


def ymd():
    y, m, d = D.SIGN_DATE
    return f"{y}년 {m}월 {d}일"


def sign(seal_uri, who="신청인"):
    seal = f'<img class="seal" src="{seal_uri}" alt="">' if seal_uri else ""
    return (f'<div class="dt">{ymd()}</div><div class="sg">{who}<br>상 호 : {e(D.COMPANY)}<br>'
            f'대표자 : <span class="in">대표이사 {e(D.CEO)} (인){seal}</span></div><div class="to">{e(TO)} 귀중</div>')


def render(name, html_text):
    os.makedirs(WORK, exist_ok=True)
    hp = os.path.join(WORK, name + ".html")
    pp = os.path.join(WORK, name + ".pdf")
    open(hp, "w", encoding="utf-8").write(html_text)
    subprocess.run([find_chrome(), "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=8000",
                    f"--print-to-pdf={pp}", pathlib.Path(hp).as_uri()], check=True, capture_output=True, timeout=180)
    return pp


# ------------------------------------------------------------ 자유 양식
def f01(seal):
    rows = [("건 명", CASE), ("상호(법인명)", D.COMPANY), ("대표자", f"대표이사 {D.CEO}"), ("사업자등록번호", D.BIZ_NO),
            ("법인등록번호", D.CORP_NO), ("본점 소재지", D.ADDRESS), ("대표 전화 · 이메일", f"{D.TEL} · {D.EMAIL}"),
            ("책임자(연락처)", f"{D.MANAGER[1]} {D.MANAGER[0]} · {D.MANAGER[2]}")]
    body = ('<h1>입찰참가신청서</h1><table class="f">' + "".join(f"<tr><th>{a}</th><td>{e(b)}</td></tr>" for a, b in rows) + "</table>"
            f'<p class="b">당사는 귀 협의회의 「{e(NOTICE)}」 내용을 모두 확인하고 이에 동의하며, 별첨 1 제출서류를 갖추어 위 입찰에 참가하고자 신청합니다.</p>'
            '<p class="b">제출한 서류와 제안 내용은 사실과 다름이 없으며, 허위 사실이 확인되면 계약 이후에도 무효 처리될 수 있음을 확인합니다(참고사항 1).</p>'
            + sign(seal))
    return page("제출서류 1 · 입찰참가신청서(자유 양식)", body)


def f11(seal):
    it = ["입찰 및 계약과 관련하여 협의회 임원 · 관계자에게 금품 · 향응 · 편의를 제공하거나 약속하지 않습니다(입찰제한 3).",
          "특정 업체의 낙찰을 위한 담합이나 다른 업체의 입찰 참가를 방해하는 행위를 하지 않습니다(입찰제한 2 · 4).",
          "발전기금 · 협찬금 · 참가비 · 판매수수료 등 입찰 및 행사 운영과 관련된 금전 · 현물 혜택과 수익 내역을 누락하거나 거짓으로 제출하지 않습니다(입찰제한 6).",
          "참여업체 사이의 부당한 가격 담합을 계약 조건으로 금지하고, 적발되면 협의회에 보고하고 필요한 조치를 합니다(참고사항 3).",
          "입찰 관련 질의는 공고에 따라 이메일로만 하며, 입찰 · 선정 기간 중에는 입주예정자 · 협의회 임원에게 개별 연락하거나 영업하지 않습니다(참고사항 2).",
          "당사는 타 단지에서 협약 내용을 이행하지 않은 이력과 타 단지 입주예정자협의회를 고소 · 고발한 이력이 없음을 확인합니다(입찰제한 8 · 9).",
          "위 사항을 위반하면 입찰 참가 제한, 선정 취소 또는 계약 해지 등 협의회의 조치를 이의 없이 따르겠습니다."]
    body = ('<h1>청렴 계약 이행각서</h1>'
            f'<p class="b">당사는 「{e(CASE)}」에 참가하면서 공정하고 투명한 입찰과 계약 이행을 위하여 다음 사항을 지킬 것을 서약합니다.</p>'
            '<ol class="c">' + "".join(f"<li>{e(x)}</li>" for x in it) + "</ol>" + sign(seal, "서약인"))
    return page("제출서류 11 · 청렴 계약 이행각서(자유 양식)", body)


def f12(seal):
    it = ["입찰 · 평가 · 협약 과정에서 알게 된 협의회의 운영 자료와 입주예정자 정보, 평가 내용을 입찰과 협약 이행 목적 밖으로 쓰거나 제3자에게 알리지 않습니다.",
          "입주예정자 개인정보는 박람회 · 입주 지원 업무에 필요한 범위에서만 수집 · 이용하고, 협의회 동의 없이 영업에 쓰거나 다른 업체에 제공하지 않습니다.",
          "참여업체가 계약 과정에서 받은 개인정보도 같은 기준으로 다루도록 업체 계약 조건에 넣고 관리합니다.",
          "협약이 끝나거나 선정되지 않으면 받은 자료를 돌려주거나 파기하고, 협의회가 요청하면 파기 결과를 알려 드립니다.",
          "위 사항을 위반하여 협의회 또는 입주예정자에게 손해가 생기면 관계 법령에 따라 책임을 지겠습니다."]
    body = ('<h1>비밀 유지 서약서</h1>'
            f'<p class="b">당사는 「{e(CASE)}」과 관련하여 다음과 같이 비밀을 유지할 것을 서약합니다.</p>'
            '<ol class="c">' + "".join(f"<li>{e(x)}</li>" for x in it) + "</ol>" + sign(seal, "서약인"))
    return page("제출서류 12 · 비밀 유지 서약서(자유 양식)", body)


def f13(seal):
    it = ["당사가 제출한 입찰 서류 일체는 반환을 요구하지 않습니다(참고사항 1).",
          "협의회의 서류 심사 · 프레젠테이션 평가와 최종 선정 결과에 대하여 일체의 이의를 제기하지 않습니다(참고사항 5).",
          "제출 서류에 허위 사실이 확인되면 계약 이후에도 무효 처리될 수 있음을 확인합니다(참고사항 1 · 입찰제한 7).",
          "공고문에 포함되지 않은 사항은 협의회의 결정을 따릅니다(참고사항 6)."]
    body = ('<h1>서 약 서</h1><h2 style="text-align:center;margin-top:-6mm;font-size:13pt">서류 미반환 · 이의 미제기</h2>'
            f'<p class="b">당사는 「{e(CASE)}」에 참가하면서 다음 사항을 서약합니다.</p>'
            '<ol class="c">' + "".join(f"<li>{e(x)}</li>" for x in it) + "</ol>" + sign(seal, "서약인"))
    return page("제출서류 13 · 서류 미반환 · 이의 미제기 서약서(자유 양식)", body)


def f_gam(seal_uri):
    """사용인감계 — 사용인감 칸 = 디지털 직인(철산 · 탕정 · 분당과 같음) · 법인인감 칸 · 대표자 (인)은 비워 두고 본부장이 실물 법인인감으로 찍는다(규칙 4)."""
    rows = [("상호(법인명)", D.COMPANY), ("사업자등록번호", D.BIZ_NO), ("법인등록번호", D.CORP_NO), ("본점(사업장) 소재지", D.ADDRESS), ("대표자 성명", D.CEO)]
    body = ('<h1 style="margin:0 0 7mm">사용인감계</h1><table class="f" style="margin-bottom:6mm">' + "".join(f"<tr><th>{a}</th><td>{e(b)}</td></tr>" for a, b in rows) + "</table>"
            '<div class="gam"><div><b>사 용 인 감</b><span style="display:flex;align-items:center;justify-content:center">'
            + (f'<img src="{seal_uri}" style="width:26mm;height:26mm;opacity:.92" alt="">' if seal_uri else '') + '</span></div><div><b>법 인 인 감</b><span></span></div></div>'
            f'<p class="b">위 사용인감은 당사가 {e(TO)}의 「입주박람회 주관사 선정 입찰」에 참가함에 있어 입찰참가신청서 · 이행각서 · 서약서 등 입찰 관련 서류와 협약 체결에 관한 서류에 사용하는 인감임을 신고합니다.</p>'
            '<p class="b">당사는 위 사용인감을 날인하여 행한 모든 행위에 대하여 법인인감을 날인하여 행한 것과 동일하게 일체의 책임을 지겠습니다.</p>'
            f'<div class="dt" style="margin:6mm 0 5mm">{ymd()}</div><div class="sg">신고인<br>상 호 : {e(D.COMPANY)}<br>대표자 : 대표이사 {e(D.CEO)} (인)</div>'
            f'<div class="to">{e(TO)} 귀중</div>'
            '<p style="font-size:9pt;color:#555;margin-top:5mm;line-height:1.45">' + NOTE_GAM + '</p>')
    return page("제출서류 4 · 사용인감계", body)


NOTE_GAM = ("※ 사용인감 칸 = 입찰참가신청서 · 이행각서 · 서약서에 찍은 인감(직인) · 법인인감 칸과 대표자 (인) = 인감증명서상 법인인감 · 인감증명서(최근 1개월 이내 발급분) 함께 제출")


# ------------------------------------------------------------ 안내 · 표지
def p_q6(sgi_uri, dnb_uris):
    """10-29 재확인: 입찰자격 6) 하자담보 이행 능력 증빙 붙임 = 안내 1쪽 + SGI 증권 1쪽 + 디엔비 협약 요약 1쪽(KB 증권 원본 쪽은 SGI 뒤에 끼움).
    10-30 본부장 '요약 1쪽 + 원본 축소' — 협약서 원본 2쪽을 A4로 크게 넣지 않고, 요지 표 + 원본 축소본 2장을 한 쪽에."""
    rows = [("①", "하자 처리 · 환불 규정", "제출서류 10(컴플레인 · A/S 관리 프로세스 · 계약 취소 · 환불 · 10배 보상 · 도산 이관)", "제출서류 10"),
            ("②", "서울보증보험 계약보증보험증권 발급 이력", "발급 2026.09.07 · 주계약 = 광고대행 용역(입주박람회 이행보증 아님) · 금액 · 상대방 정보 가림 · 보증 발급 이력의 근거", "다음 쪽"),
            ("③", "KB 영업배상책임보험 증권", "시설소유관리자 · 2026.10.14 ~ 2027.10.14 · 본사 기준 · 행사주최자배상책임보험은 박람회 기간 행사장 기준으로 별도 가입", "1쪽"),
            ("④", "건축 기술 자문 업무협약서", f"{D.ADVISOR} · 2026.10.26 · 양측 날인 · 협약 요지 + 원본 2쪽 축소(을 정보 가림) · 건설 하자 판정 · 보수는 시공사 책임", "1쪽")]
    body = ('<h2>입찰자격 6) 하자담보 이행 능력 - 증빙 붙임</h2>'
            '<p class="b">공고 입찰자격 6) ‘공동구매 제품 전체에 대한 계약 이행 등의 명확한 하자담보 이행 능력이 수립된 업체’의 증빙입니다.</p>'
            '<table class="l"><tr><th>No</th><th>증빙</th><th>내용</th><th>쪽</th></tr>'
            + "".join(f'<tr><td class="n">{a}</td><td>{e(b)}</td><td>{e(c)}</td><td>{e(d)}</td></tr>' for a, b, c, d in rows) + '</table>'
            '<div class="box" style="margin-top:6mm">입주박람회 계약이행 · 하자보증보험은 <b>가입 이력이 없으며</b>, 선정 · 협약 후 협의회를 피보험자로 발급합니다(보증기간 24개월 · 금액 · 기산일은 협약 때 확정).</div>'
            '<p style="font-size:10pt;color:#555">가림 없는 원본은 협의회가 요청하시면 열람할 수 있습니다.</p>')
    sgi = ('<h2>② 서울보증보험 계약보증보험증권 발급 이력</h2>'
           f'<div style="text-align:center"><img src="{sgi_uri}" style="height:205mm;border:.6pt solid #bbb"></div>')
    dnb_rows = [("당사자", f"갑 {D.COMPANY}(주관사) · 을 {D.ADVISOR}(건축 분야 기술 자문) · 을 사업자번호 · 주소 · 대표자 가림", "날인란"),
                ("체결 · 기간", f"{DNB_DATE} 양측 날인 · 1년(만료 1개월 전 종료 통지가 없으면 1년씩 연장) · 이미 시작된 단지 자문은 그 단지 협약이 끝날 때까지", "제10조"),
                ("적용 단지", "엣지컴퍼니가 주관사로 선정되어 협의회와 협약한 단지 · 단지마다 자문 범위를 서면 요청 → 을이 수락하면 시작", "제2조"),
                ("자문인", "을 소속 건축사 또는 건축 분야 건설기술인(설계 · 건설사업관리) · 단지별 성명 · 자격 · 소속 서면 통지 · 명의만 빌려주지 않음", "제3 · 9조"),
                ("자문 업무", "협의회 · 주관사 요청 시(횟수 제한 없음) - 공정별 기술 자문 · 협의회 질의 기술 검토 / 하자 취약 부위 · 마감 품질 확인(사업주체가 허용하는 범위) / "
                             "설계도서 · 설계변경 · 마감재 검토 의견 / 의견서 작성 · 협의회 회의 참석 · 설명", "제4조 ① ②"),
                ("하지 않는 일", "법정 감리 · 하자 판정 · 보수 · 소송 대리 · 별도 계약이 필요한 설계 · 감리 - 건설 하자 보수 책임은 사업주체 · 시공사", "제4조 ③"),
                ("회신 기한", "요청 받은 날부터 7영업일 안 서면 회신 · 어려우면 사유 · 회신 예정일 즉시 통지", "제5조"),
                ("비용", "주관사(갑) 부담 · 건별 정산 · 협의회 · 입주예정자에게 청구하지 않음", "제6조"),
                ("이해관계 · 정보", "단지 시행 · 시공 · 감리 · 협의회 임원과 이해관계 없음 서면 확인 · 비밀 유지 · 개인정보 파기 · 협의회 임원 등 개별 접촉 금지", "제7 · 8조")]
    thumbs = "".join(f'<figure style="margin:0;text-align:center"><img src="{u}" style="width:64mm;border:.6pt solid #999;display:block">'
                     f'<figcaption style="font-size:8.5pt;color:#555;margin-top:1.5mm">{c}</figcaption></figure>'
                     for u, c in zip(dnb_uris, ("원본 1쪽 · 제1 ~ 7조(위 여백 = 체결일 표기)", "원본 2쪽 · 제8 ~ 12조 · 양측 날인(을 정보 가림)")))
    dnb = ('<h2>④ 건축 기술 자문 업무협약서 - 요지</h2>'
           '<table class="l" style="font-size:9.5pt;margin-bottom:5mm"><tr><th style="width:28mm">항목</th><th>협약 내용</th><th style="width:23mm">조항</th></tr>'
           + "".join(f'<tr><td><b>{e(a)}</b></td><td>{e(b)}</td><td>{e(c)}</td></tr>' for a, b, c in dnb_rows) + '</table>'
           f'<div style="display:flex;justify-content:center;gap:10mm">{thumbs}</div>')
    return [page("입찰자격 6) 증빙 붙임 · 안내", body),
            page("입찰자격 6) 증빙 붙임 · ②", sgi, "광고대행 용역 계약보증(입주박람회 이행보증 아님) · 금액 · 상대방 정보 · 증권번호 일부 가림"),
            page("입찰자격 6) 증빙 붙임 · ④", dnb, "원본(2쪽)은 축소해 실었습니다 · 원본 전문은 협의회가 요청하시면 제출하고 PT 때 지참합니다")]


def p08_guide():
    rows = "".join(f'<tr><td class="n">{i}</td><td>{m}</td><td>{e(nm)}</td><td class="r">{n:,}</td><td>{e(ev)}</td></tr>'
                   for i, (m, nm, _a, n, ev) in enumerate([(*r, EV8[r[1]]) for r in D.GP_REC], 1))
    body = ('<h2>최근 3년 주관사 실적 증빙 - 안내</h2>'
            f'<p class="b">입찰자격 5) ‘최근 3년간 1,000세대 이상의 단지 5개 이상 수임 이력’ · 7) ‘신축 아파트 행사 및 단지 업무 관련 전문성과 실적’의 증빙입니다. '
            f'입주 2023.10 이후 1,000세대 이상 주관 단지 {len(D.GP_REC)}곳 · {sum(r[3] for r in D.GP_REC):,}세대이며, 레이카운티(박람회 2023.08 · 10)를 빼도 7곳입니다.</p>'
            '<table class="l"><tr><th>No</th><th>입주</th><th>단지</th><th>세대</th><th>증빙(이 서류 안)</th></tr>' + rows + '</table>'
            '<div class="box" style="margin-top:6mm"><b>붙임 구성</b><br>A · NICE디앤비 기업신용평가보고서 ‘연혁’ 발췌(1,000세대 이상 주관 단지 · 시기)<br>'
            'B · 박람회장 공식 행사일정 · 단지 카페 공지 캡처(주최 / 주관 엣지컴퍼니)<br>'
            'C · 주관사 협약서 3건(500 ~ 999세대 단지 · 협약일 순 · 상대방 개인정보 가림) - 입찰자격 7) 참고</div>'
            '<p style="font-size:10pt;color:#555">500 ~ 999세대 주관 단지 중 이 서류에 증빙이 없는 곳은 협의회가 요청하시면 제출합니다. 누적 수임 단지(전신 실적 포함)는 ‘수임’으로 적습니다.</p>')
    return page("제출서류 8 · 최근 3년 주관사 실적 증빙", body)


EV8 = {"레이카운티": "A NICE 연혁", "e편한세상 송도 더퍼스트비치": "B BEXCO 공식 행사일정", "두산위브더제니스 센트럴사하": "A NICE 연혁",
       "양정자이더샵SK VIEW 1·2단지": "A NICE 연혁", "춘천 학곡지구 중해마루힐 포레스트": "A NICE 연혁", "에코델타 대성베르힐": "B 카페 공지 · BEXCO 공식 행사일정",
       "두산위브더제니스 오션시티": "A NICE 연혁", "창원 센트럴 아이파크": "A NICE 연혁 · B CECO 공식 행사일정"}


def p10_cover(ranges):
    li = "".join(f"<li>{e(t)} - 제안서 p.{a:02d}{'' if a == b else f' ~ {b:02d}'}</li>" for t, a, b in ranges)
    body = ('<div class="cv"><div class="no">제출서류 10</div><div class="tt">입주민 컴플레인 및<br>A/S 관리 프로세스 제안서</div>'
            '<div class="ds">계약 취소 및 환불 규정 포함 · 입찰자격 6) 하자담보 이행 능력</div>'
            '<div class="box" style="margin-top:10mm"><b>이 서류의 구성(제출서류 9 제안서의 해당 쪽을 그대로 옮김)</b><ol class="c" style="margin-top:3mm">' + li + '</ol></div>'
            '<div class="ds">한 창구 접수 → 24시간 안 1차 회신(주말 · 공휴일 = 다음 영업일 12시) → 48시간 안 방문 일정 확정 → 업체 무응답 시 주관사 개입 · 선보상 → 도산 · 연락 두절 시 이관 → 완료 확인 · 정기 보고</div></div>')
    return page("제출서류 10 · 컴플레인 · A/S 관리 프로세스", body)


def p00(spans, final):
    rows = "".join(f'<tr><td class="n">{n}</td><td>{e(t)}</td><td>{e(s)}</td><td class="r">{a}{"" if a == b else f" ~ {b}"}</td></tr>' for n, t, s, a, b in spans)
    body = ('<h2>제출서류 목록</h2>'
            f'<p style="margin-bottom:4mm">건명 : {e(NOTICE)}<br>제출 : {e(D.SUBMIT_TO)} · 마감 {e(D.DEADLINE)} · 공고 별첨 1 순서</p>'
            '<table class="l"><tr><th>No</th><th>서류</th><th>발급일 · 내용</th><th>쪽</th></tr>' + rows + "</table>"
            + ("" if final else '<p style="color:#b00;font-weight:800;margin-top:5mm">※ 날인 전 확인본 - 사용인감계 실물 날인 스캔을 넣기 전에는 제출하지 않습니다.</p>'))
    return page("제출서류 목록", body)


# ------------------------------------------------------------ 기존 PDF 쪽 다루기
def nr(name):
    p = os.path.join(NR, name)
    assert os.path.exists(p), ("나리벡 제출본 증빙 없음", p)
    return fitz.open(p)


def proposal_ranges(prop):
    """제출서류 10에 옮길 제안서 쪽(제목으로 찾음)."""
    want = [("A/S 정책 - 한 창구 · 업체 부담 없는 제도", "A/S 정책 - 주관사"), ("주관 콜센터와 선보상", "콜센터와 선보상"),
            ("클레임 처리 흐름과 CRM 관리", "처리 흐름과 CRM"), ("입주민 컴플레인 처리 기준 · 해결 사례", "컴플레인, 이렇게 해결"),
            ("계약금 상한 · 취소 · 환불 요약", "자금을 먼저 지킵니다"), ("계약 취소 · 환불 규정 전문 ①", "환불 규정 전문 ①"), ("계약 취소 · 환불 규정 전문 ②", "환불 규정 전문 ②"),
            ("사전점검 · 하자 책임 구분", "사전점검 · 하자, 책임부터"), ("입찰자격 6) 하자담보 장치와 증빙", "장치와 증빙")]
    texts = [re.sub(r"[\s\u00a0\u2060]+", " ", p.get_text()) for p in prop]
    out = []
    for label, key in want:
        hit = [i for i, t in enumerate(texts) if key in t[:400]]
        assert hit, ("제안서에서 쪽을 찾지 못함", key)
        out.append((label, hit[0] + 1, hit[0] + 1))
    return out


# ------------------------------------------------------------ 8 실적 증빙 붙임(이미지는 나리벡 최종 제출본 03 · 09에서 꺼냄 — 가림 끝난 것)
B_CAPS = [  # (나리벡 03 쪽, 이미지 순번, 단지, 출처, 기간 · 장소)
    (6, 0, "에코델타 대성베르힐", "[인증]에코델타시티 대성베르힐 입주자 모임 · 주관사 공지사항(작성자 ‘주관사 엣지컴퍼니’ · 입주민 닉네임 가림)", "2024.11.08 주관사 인사 · 2025.11.26 입주박람회 개최 안내 · 2025.12.02 박람회 성료"),
    (7, 0, "e편한세상 송도 더퍼스트비치", "BEXCO 공식 행사일정(주최 / 주관 : 입주자협의회 / 주식회사 엣지컴퍼니)", "2024.06.14 ~ 06.16 · BEXCO 제2전시장 4(B,C)홀"),
    (12, 0, "에코델타 대성베르힐", "BEXCO 공식 행사일정", "2025.11.28 ~ 11.30 · BEXCO 제2전시장 4(D-F)홀"),
    (13, 1, "창원 센트럴 아이파크", "창원컨벤션센터(CECO) 공식 행사일정", "2026.07.03 ~ 07.05 · CECO 제2전시장"),
    (11, 0, "e편한세상 에코델타 센터포인트(953세대)", "BEXCO 공식 행사일정", "2025.02.14 ~ 02.16 · BEXCO 제2전시장 4E, F홀"),
    (11, 1, "강서자이 에코델타(856세대)", "BEXCO 공식 행사일정", "2025.02.21 ~ 02.23 · BEXCO 제2전시장 4(E-F)홀"),
    (11, 2, "에코델타시티 푸르지오 린(886세대)", "BEXCO 공식 행사일정", "2025.07.05 ~ 07.07 · BEXCO 제2전시장 4(E-F)홀"),
    (12, 1, "남울산 노르웨이숲(848세대)", "울산전시컨벤션센터(UECO) 공식 행사일정", "2026.03.28 ~ 03.29 · UECO 전시장 B"),
    (13, 0, "영주자이 시그니처(763세대)", "입주자 공식 카페 ‘엣지컴퍼니 공지사항’ 게시판(입주민 닉네임 가림)", "2026.08.29 ~ 08.30 · 영주 그랜드컨벤션"),
]
C_DOCS = [(8, "e편한세상 에코델타 센터포인트", "2023.04.03"), (9, "부산 드파인 센텀", "2023.12.20"), (10, "디에트르 더 퍼스트", "2025.08.02")]


def _img(src, pno, k, name, top=0):
    """나리벡 제출본 쪽의 k번째(큰) 이미지를 PNG로 꺼냄 → file URI. top = 위에서 잘라낼 비율(이미지에 박힌 옛 머리글)."""
    os.makedirs(os.path.join(WORK, "_ev"), exist_ok=True)
    pg = src[pno - 1]
    big = [i for i in pg.get_image_info(xrefs=True) if i["xref"] > 0 and (i["bbox"][2] - i["bbox"][0]) > 60]
    x = big[k]["xref"]
    pix = fitz.Pixmap(src, x)
    sm = src.extract_image(x).get("smask")
    if sm:
        pix = fitz.Pixmap(pix, fitz.Pixmap(src, sm))
    if pix.n - pix.alpha >= 4:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    fn = os.path.join(WORK, "_ev", name)
    pix.save(fn)
    if top:
        from PIL import Image
        im = Image.open(fn)
        im.crop((0, int(im.size[1] * top), im.size[0], im.size[1])).save(fn)
    return pathlib.Path(fn).as_uri()


def ev8_pages(seal_uri):
    s03, s09 = nr("03_입주박람회_실적_및_공동구매_증빙.pdf"), nr("09_기업신용평가서.pdf")
    nfn = os.path.join(WORK, "_ev", "nice_p9.png")
    os.makedirs(os.path.dirname(nfn), exist_ok=True)
    s09[9].get_pixmap(dpi=150).save(nfn)   # NICE 원본 9쪽(기업개요 · 연혁) — 09 = 표지 1쪽 + 원본 24쪽
    info = [("보고서명", "CLIP 기업신용평가보고서"), ("발행 기관", "NICE디앤비(dun & bradstreet)"), ("평가 대상", f"{D.COMPANY}({D.BIZ_NO})"),
            ("평가완료일", f"{D.NICE_DATE} · 연 1회 정기 평가(재무제표 기준) · 유효기간 안 최근 평가본"), ("발췌 범위", "원본 9쪽 ‘04 영업 현황(기업개요)’ 중 ‘연혁’ · 전문은 선택 자료")]
    pa = ('<h2>붙임 A · NICE디앤비 기업신용평가보고서 ‘연혁’ 발췌</h2><table class="f" style="margin-bottom:4mm">'
          + "".join(f"<tr><th>{a}</th><td>{e(b)}</td></tr>" for a, b in info) + "</table>"
          f'<img src="{pathlib.Path(nfn).as_uri()}" style="display:block;width:106mm;margin:0 auto;border:1px solid #bbb">'
          '<p style="font-size:10pt;margin-top:3mm">연혁의 2023/11 ~ 2026/07 주관 6행이 최근 3년 1,000세대 이상 주관 실적입니다. 위 발췌는 원본과 같습니다.</p>')
    pages = [page("제출서류 8 · 붙임 A", pa)]
    for i in range(0, len(B_CAPS), 2):
        body = ""
        for j, (pno, k, nm, src, when) in enumerate(B_CAPS[i:i + 2], i + 1):
            uri = _img(s03, pno, k, f"b{j}.png")
            body += (f'<div style="margin-bottom:7mm"><h2 style="font-size:12.5pt">B-{j} · {e(nm)}</h2>'
                     f'<p style="font-size:10pt;color:#444;margin-bottom:2mm">{e(src)} · {e(when)}</p>'
                     f'<img src="{uri}" style="display:block;max-width:100%;max-height:92mm;margin:0 auto;border:1px solid #bbb"></div>')
        pages.append(page("제출서류 8 · 붙임 B · 공식 행사일정 · 카페 공지", body,
                          "B-1 ~ B-4 = 입찰자격 5) 1,000세대 이상 단지 · B-5 ~ B-9 = 500 ~ 999세대 주관 단지(입찰자격 7) 참고) · 화면 그대로 · 입주민 닉네임만 가림"))
    for j, (pno, nm, dt) in enumerate(C_DOCS, 1):
        uri = _img(s03, pno, 0, f"c{j}.png", top=0.15)   # 고양 때 박힌 '제출서류 12 · 별첨 3-n' 머리글 · 제목 잘라냄
        body = (f'<h2>붙임 C-{j} · 주관사 협약서 사본 - {e(nm)}</h2><p style="font-size:10.5pt;margin-bottom:4mm">협약일 {dt} · 상대방 대표자 성명 · 연락처 · 계좌 가림</p>'
                f'<img src="{uri}" style="display:block;width:100%;border:1px solid #bbb">')
        pages.append(page("제출서류 8 · 붙임 C · 주관사 협약서(협약일 순)", body, "500 ~ 999세대 주관 단지의 협약서 - 입찰자격 7) 신축 아파트 행사 · 단지 업무 실적 참고"))
    return pages


def main():
    seal = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None
    assert seal and os.path.exists(seal), "투명 직인 PNG 경로를 주세요(사용인감 · 자유 양식 날인용)"
    seal_uri = pathlib.Path(seal).resolve().as_uri()
    final = "--final" in sys.argv
    os.makedirs(SUBMIT, exist_ok=True)
    assert os.path.exists(PROPOSAL), "제안서 밝은 시안 PDF가 없음 — build_gp.py → light_build.py → PDF 먼저"
    prop = fitz.open(PROPOSAL)

    # 자유 양식 · 출력용
    r01 = render("01_입찰참가신청서", doc("입찰참가신청서", [f01(seal_uri)]))
    r11 = render("11_청렴계약_이행각서", doc("청렴 계약 이행각서", [f11(seal_uri)]))
    r12 = render("12_비밀유지_서약서", doc("비밀 유지 서약서", [f12(seal_uri)]))
    r13 = render("13_서류미반환_이의미제기_서약서", doc("서약서", [f13(seal_uri)]))
    rgam = render(f"{D.FILE_TITLE.split(' 입주')[0]}_사용인감계_날인출력용", doc("사용인감계", [f_gam(seal_uri)]))
    # 본부장 10-28 '직인 찍을 거 먼저 올려줘' — 직인 · 법인인감을 모두 실물로 찍을 수 있게 빈 칸 5쪽(1 · 11 · 12 · 13 · 사용인감계)
    rprint = render(f"{D.FILE_TITLE.split(' 입주')[0]}_날인출력용_5쪽", doc("날인 출력용", [f01(None), f11(None), f12(None), f13(None), f_gam(None)]))
    have_scan = os.path.exists(SEAL_SCAN) or not D.GAM_SUBMIT   # 사용인감계를 내지 않으면(본부장 10-28) 날인 대기 없음
    if final:
        assert have_scan, f"사용인감계 실물 날인 스캔이 없음: {SEAL_SCAN}"

    ranges = proposal_ranges(prop)
    r08g = render("08_실적증빙_안내", doc("실적 증빙 안내", [p08_guide()]))
    r10c = render("10_AS프로세스_표지", doc("A/S 프로세스", [p10_cover(ranges)]))

    parts = []   # (번호, 서류, 내용, Document)

    def take(src, pages):
        d = fitz.open()
        for p in pages:
            d.insert_pdf(src, from_page=p - 1, to_page=p - 1)
        return d

    parts.append(("1", "입찰참가신청서(자유 양식)", f"작성 {ymd()} · " + ("사용인감" if D.GAM_SUBMIT else "대표이사 직인"), fitz.open(r01)))
    parts.append(("2", "사업자등록증 사본", f"{D.ISSUE['biz']} 발급", take(nr("05_사업자등록증.pdf"), [1])))
    d3 = take(nr("06_법인등기부등본_법인인감증명서.pdf"), [1, 2])
    for r_ in REG_MASK:   # 10-29 재확인: 목록엔 '가림'인데 실물에 대표 주소가 보였음 → 화소까지 지움
        d3[1].add_redact_annot(fitz.Rect(*r_), fill=(0.6, 0.6, 0.6))
    d3[1].apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS)
    parts.append(("3", "법인 등기부등본(최근 1개월)", f"{D.ISSUE['reg']} 발급 · 대표 주소 가림", d3))
    d4 = take(nr("06_법인등기부등본_법인인감증명서.pdf"), [3])
    if D.GAM_SUBMIT:
        d4.insert_pdf(fitz.open(SEAL_SCAN) if os.path.exists(SEAL_SCAN) else fitz.open(rgam))
    parts.append(("4", "인감증명서(최근 1개월)" if not D.GAM_SUBMIT else "인감증명서 / 사용인감계(최근 1개월)",
                  f"인감증명서 {D.INGAM_DATE} 발급 · 가림" + ("" if not D.GAM_SUBMIT else " + 사용인감계" + ("" if os.path.exists(SEAL_SCAN) else "(날인 전)")), d4))
    parts.append(("5", "법인 사업자 통장 사본", "법인 명의 계좌", fitz.open(BANK)))
    d6 = take(nr("07_국세_지방세_완납증명서.pdf"), [1, 2])
    d6[1].add_redact_annot(fitz.Rect(*TAX_PHONE), fill=(0.6, 0.6, 0.6))   # 법정 10-30 · 본부장 '응': 지방세 증명서 대표 휴대번호(그림) 화소 가림
    d6[1].apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS)
    parts.append(("6", "국세 · 지방세 완납 증명서(유효기한 내)", f"{D.ISSUE['tax']} 발급 · 휴대번호 가림", d6))
    parts.append(("7", "4대 사회보험 가입자 명부(최근 1개월)", f"{D.ROSTER_DATE} 발급 · 13명 · 개인정보 가림", take(nr("08_4대보험_가입자명부_완납증명서.pdf"), [1, 2])))

    # 8 실적 증빙 = 안내 + A NICE 연혁 발췌 + B 공식 행사일정 · 카페 공지 캡처 + C 주관사 협약서(나리벡 03 · 09의 이미지만 꺼내 군포 머리글로 새로 조판)
    d8 = fitz.open(r08g)
    d8.insert_pdf(fitz.open(render("08_실적증빙_붙임", doc("실적 증빙 붙임", ev8_pages(seal_uri)))))
    parts.append(("8", "최근 3년 주관사 실적 증빙", "안내 + A NICE 연혁 + B 공식 행사일정 · 카페 공지 + C 주관사 협약서 3건", d8))

    parts.append(("9", "입주박람회 제안서", f"{prop.page_count}쪽 · 운영계획 · 실적 · 업체 · LH 사례 · 참여율 · 위임장", prop))
    d10 = fitz.open(r10c)
    for _l, a, _b in ranges:
        d10.insert_pdf(prop, from_page=a - 1, to_page=a - 1)
    parts.append(("10", "컴플레인 · A/S 관리 프로세스(취소 · 환불 포함)", "표지 + 제안서 해당 쪽", d10))
    parts.append(("11", "청렴 계약 이행각서(자유 양식)", "사용인감" if D.GAM_SUBMIT else "대표이사 직인", fitz.open(r11)))
    parts.append(("12", "비밀 유지 서약서(자유 양식)", "사용인감" if D.GAM_SUBMIT else "대표이사 직인", fitz.open(r12)))
    parts.append(("13", "서류 미반환 · 이의 미제기 서약서(자유 양식)", "사용인감" if D.GAM_SUBMIT else "대표이사 직인", fitz.open(r13)))
    # 자격 6 증빙 붙임(10-29 재확인 · 착수 결정 3의 묶음)
    for p in (SGI_PNG, KB, DNB):
        assert os.path.exists(p), ("자격 6 증빙 원본 없음", p)
    dnb = fitz.open(DNB)
    _w = dnb[0].rect.width   # 서명된 본문은 건드리지 않고 1쪽 위 여백에만 체결일을 적음
    dnb[0].insert_textbox(fitz.Rect(_w - 300, 14, _w - 30, 30), f"업무협약 체결일 : {DNB_DATE}", fontsize=9.5,
                          fontname="malgun", fontfile=r"C:\Windows\Fonts\malgun.ttf", color=(0.25, 0.25, 0.25), align=fitz.TEXT_ALIGN_RIGHT)
    dnb_uris = []   # 10-30 본부장 '요약 1쪽 + 원본 축소' — 원본 쪽은 그림(확대하면 읽히는 200dpi)으로 요지 쪽에 작게
    for i, pg in enumerate(dnb):
        fp = os.path.join(WORK, f"14_디엔비협약서_원본{i + 1}.jpg")
        pg.get_pixmap(dpi=200).save(fp, jpg_quality=85)
        dnb_uris.append(pathlib.Path(fp).as_uri())
    dq6 = fitz.open(render("14_자격6_증빙붙임", doc("자격 6 증빙 붙임", p_q6(pathlib.Path(SGI_PNG).as_uri(), dnb_uris))))
    kb = fitz.open(KB)
    for r_ in KB_MASK:
        kb[0].add_redact_annot(fitz.Rect(*r_), fill=(0.6, 0.6, 0.6))
    kb[0].apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS)
    dq6.insert_pdf(kb, start_at=2)   # 안내 · ② SGI · ③ KB · ④ 디엔비 요지 순
    parts.append(("붙임", "입찰자격 6) 하자담보 이행 능력 증빙", "안내 · SGI 계약보증증권 발급 이력(가림) · KB 영업배상책임보험 증권 · 건축 기술 자문 업무협약서(요지 + 원본 축소 · 을 정보 가림)", dq6))
    # 선택 자료
    sel = fitz.open()
    sel.insert_pdf(nr("09_기업신용평가서.pdf"), from_page=1)
    for p in (ELEC, ISO):
        assert os.path.exists(p), ("선택 자료 원본 없음", p)
    sel.insert_pdf(fitz.open(ELEC))
    # 10-31 본부장 'ISO 인증도 2개씩 맞춰서 · 너무 페이지 차지 많이해' — 원본 6쪽(국문 · 영문 × 9001 · 14001 · 45001)을
    # A4 가로 한 쪽에 국문 · 영문 2장씩(원본 쪽을 그대로 축소해 얹음 · 다시 그리지 않음) → 3쪽
    iso = fitz.open(ISO)
    assert iso.page_count == 6, ("ISO 원본 쪽 수가 바뀜", iso.page_count)
    W_, H_, top, gap = 842, 595, 34, 18
    h_ = H_ - top - 16
    w_ = h_ * iso[0].rect.width / iso[0].rect.height
    x0 = (W_ - 2 * w_ - gap) / 2
    for k, nm in enumerate(("ISO 9001:2015 품질경영시스템", "ISO 14001:2015 환경경영시스템", "ISO 45001:2018 안전보건경영시스템")):
        pg = sel.new_page(width=W_, height=H_)
        pg.insert_textbox(fitz.Rect(x0, 12, W_ - x0, 28), f"선택 자료 · {nm} 인증서(국문 · 영문)", fontsize=9.5, fontname="malgun",
                          fontfile=r"C:\Windows\Fonts\malgun.ttf", color=(0.6, 0.48, 0.25))
        pg.insert_textbox(fitz.Rect(x0, 12, W_ - x0, 28), f"{D.COMPANY} · 입주박람회 주관사", fontsize=9.5, fontname="malgun",
                          fontfile=r"C:\Windows\Fonts\malgun.ttf", color=(0.6, 0.48, 0.25), align=fitz.TEXT_ALIGN_RIGHT)
        pg.draw_line(fitz.Point(x0, 29), fitz.Point(W_ - x0, 29), color=(0.78, 0.66, 0.42), width=0.8)
        for j in range(2):
            r = fitz.Rect(x0 + j * (w_ + gap), top, x0 + j * (w_ + gap) + w_, top + h_)
            pg.show_pdf_page(r, iso, 2 * k + j)
            pg.draw_rect(r, color=(0.75, 0.75, 0.75), width=0.5)
    sel.subset_fonts()
    parts.append(("선택", "선택 자료(필수 아님)", "NICE 기업신용평가 전문(연 1회 정기 평가 · 가림) · 전기공사업 등록증 · ISO 인증서", sel))

    # 목록(쪽 번호) → 병합
    spans, cur = [], 2
    for n, t, s, d in parts:
        spans.append((n, t, s, cur, cur + d.page_count - 1))
        cur += d.page_count
    out = fitz.open(render("00_제출서류_목록", doc("제출서류 목록", [p00(spans, have_scan)])))
    assert out.page_count == 1, "목록이 한 쪽을 넘음"
    for _n, _t, _s, d in parts:
        out.insert_pdf(d)
    name = OUT_NAME if have_scan else OUT_NAME.replace(".pdf", "_날인전.pdf")
    path = os.path.join(SUBMIT if have_scan else WORK, name)
    out.save(path, garbage=GARBAGE, deflate=True)
    print(f"{'제출본' if have_scan else '날인 전 확인본'} {out.page_count}쪽 · {os.path.getsize(path) / 1e6:.1f}MB → {path}")
    print(f"사용인감계 출력용 → {rgam}")
    print(f"날인 출력용 5쪽(빈 칸) → {rprint}")
    for n, t, s, a, b in spans:
        print(f"  {n:>3} {t} · p.{a}{'' if a == b else f'~{b}'} · {s}")


if __name__ == "__main__":
    main()
