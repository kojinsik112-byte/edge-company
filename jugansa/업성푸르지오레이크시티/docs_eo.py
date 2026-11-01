# -*- coding: utf-8 -*-
"""업성 푸르지오 레이크시티 1BL 공동구매 주관사 선정 — 공고 7항 '제출 서류' 가 ~ 아 생성 · 번호별 PDF + 00 자료 목록 + ZIP 1개 + 예비 통합본(A4).

공고 6항 나: 서명 또는 날인한 제안서와 증빙을 PDF로 · 파일을 나누면 자료 목록 첨부 · 통합 · 파일 1개 조건 없음 → 번호별 PDF + 00 목록 + ZIP 1개(규칙 21) · 통합본은 예비 보관.
  00 자료 목록
  01 가 입찰참가 신청서(직인) · 사업자등록증 · 법인등기(대표 주소 가림)
  02 나 회사소개서 · 담당 인력 현황(직인) · 고용 · 산재 가입증명원 · 4대보험 명부(가림) · 제안서 회사 쪽 · 최근 5년 실적표 · A NICE 연혁 · B 공식 행사일정 · 카페 공지 · C 협약서
  03 다 국세 · 지방세 납세증명서(10.23 · 휴대번호 가림 — 신분평 G1 교훈: 제안서 안 사진도 같은 가림본)
  04 라 운영제안서(build_eo.py 밝은 시안 · 제안설명 자료 겸) + 가격표 · 수수료 명세서(직인) + 붙임 안내 + 타 단지 공개 단가표 2쪽(나리벡 14 ⑥ 가림본)
  05 마 취소 · 환불 · 사후관리 계획서 + 환불 규정 전문 + 보험 가입 현황 · 보증 제공계획(직인) + KB 영업배상 증권(종류 그대로) + SGI 발급 이력(가림)
  06 바 청렴 · 이해관계 · 개인정보 · 비밀유지 확약서(직인)   07 사 참여 업체 모집계획 · 확인 절차(직인)   08 아 해지 · 소송 이력 확인서(직인)
날인: 대표이사 직인(투명 PNG)만 · 법인인감 · 사용인감계 없음(규칙 4).
빈칸: 이해관계(data.CONFLICT_OK) · 해지 · 소송(data.HISTORY_OK) — 비어 있으면 노란 칸 · '작업/확인본_빈칸있음/'에만 · --final은 빈칸 0이어야 함.
출력: 작업/(중간) · 제출본/번호별/00 ~ 08 + 제출본/<FILE_TITLE>.zip + 예비 통합본 → 공고 폴더 사본
사용: python docs_eo.py assets_ins/jigin_t.png [--final]
"""
import hashlib
import html
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import zipfile

import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "요약제안서")]
import data as D  # noqa: E402
from build import find_chrome  # noqa: E402

e = html.escape
ST = D.SITE
SITE = ST["name"]
TO = f"{SITE} 입주예정자협의회"
NOTICE = D.NOTICE

NR = r"C:\본부장\05주관사 입찰공고\20261025_롯데캐슬 나리벡시티\제안자료_주식회사 엣지컴퍼니\제안자료_주식회사 엣지컴퍼니"   # 10.23 발급 증빙 원본(가림 끝난 나리벡 제출본)
PROPOSAL = os.path.join(HERE, "엣지컴퍼니_업성푸르지오레이크시티_공동구매_주관사_제안서_밝은시안.pdf")
KB = r"C:\본부장\05주관사 입찰공고\20261024_창릉신도시 S5\엣지컴퍼니_고양창릉S5_제출서류\12_영업배상책임보험_증서\엣지컴퍼니_고양창릉S5_12_영업배상책임보험_증서.pdf"   # KB 영업배상(시설소유관리자 · 2026.10.14) 증권 1쪽 원본
WORK = os.path.join(HERE, "작업")
SGI_PNG = os.path.join(HERE, "assets_ins", "os_sgi_bond_masked.png")
GOYONG = os.path.join(WORK, "05_고용산재보험_가입증명원_20261031.pdf")   # 근로복지공단 고용 · 산재보험 가입증명원(2026.10.31 · 제출용)
REG_MASK = [(203, 163, 556, 177), (30, 176, 50, 187)]   # 등기부 2/2쪽 대표이사 주소(10.23 발급본)
TAX_PHONE = (119, 228.5, 196, 239)                      # 지방세 납세증명서 2쪽 대표 휴대번호(그림)
ROSTER_MASK = (87, 311, 193, 571)                       # 명부 1쪽 주민번호 칸 전체(챗 검증 10-31 청주와 같게)
SUBMIT = os.path.join(HERE, "제출본")
BLANK_DIR = os.path.join(WORK, "확인본_빈칸있음")
NOTICE_DIR = r"C:\본부장\05주관사 입찰공고\20261104_업성 푸르지오 레이크시티\제안자료_주식회사 엣지컴퍼니"
ZIP_NAME = f"{D.FILE_TITLE}.zip"
GARBAGE = 1
BLANKS = []

CSS = r"""
@page{size:A4;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Malgun Gothic','맑은 고딕',sans-serif;color:#111;font-size:12pt;line-height:1.6}
.pg{width:210mm;height:297mm;padding:18mm 20mm 16mm;position:relative;page-break-after:always;overflow:hidden}
.pg:last-child{page-break-after:auto}
.lb{font-size:9.5pt;color:#9a7a40;font-weight:700;letter-spacing:.06em;border-bottom:1.2px solid #c8a86a;padding-bottom:4px;margin-bottom:8mm;display:flex;justify-content:space-between}
h1{font-size:21pt;text-align:center;letter-spacing:.3em;margin:2mm 0 7mm;font-weight:800}
h2{font-size:14pt;margin:2mm 0 3.5mm;font-weight:800}
h3{font-size:11.5pt;margin:4mm 0 2mm;font-weight:800;color:#5a4416}
table.f{width:100%;border-collapse:collapse;margin-bottom:7mm}
table.f th,table.f td{border:1px solid #333;padding:6px 9px;font-size:11pt;vertical-align:middle}
table.f th{background:#f3efe6;width:26%;text-align:center;font-weight:700}
table.l{width:100%;border-collapse:collapse;font-size:9.6pt;line-height:1.42}
table.l th,table.l td{border-bottom:1px solid #bbb;padding:3.6px 5px;text-align:left;vertical-align:top}
table.l th{border-bottom:1.5px solid #9a7a40;color:#7a5c25;font-size:9.2pt}
table.l td.n{width:8mm;font-weight:800;color:#9a7a40;text-align:center}
table.l td.r{text-align:right;white-space:nowrap}
p.b{text-indent:.6em;margin-bottom:4mm}
p.sv{text-indent:.6em;margin-bottom:3mm;line-height:1.8}
ol.c{margin:0 0 0 1.3em}ol.c li{margin:0 0 2.6mm;padding-left:2px;line-height:1.65}
.art{margin-bottom:2.6mm;font-size:10.4pt;line-height:1.62}.art b{color:#5a4416}
.dt{text-align:center;font-size:13pt;margin:7mm 0 5mm;letter-spacing:.1em}
.who{margin:4mm 0 0 auto;width:96mm;line-height:2.1;position:relative;font-size:12pt}
.who .in{position:relative;display:inline-block}
.who .seal{position:absolute;width:21mm;height:21mm;right:-23mm;top:-6mm;opacity:.92}
.to{text-align:center;font-size:14.5pt;font-weight:800;margin-top:7mm;letter-spacing:.05em}
.nt{position:absolute;left:20mm;right:20mm;bottom:12mm;font-size:8.8pt;color:#555;line-height:1.5}
.box{border:1.2px solid #c8a86a;border-radius:6px;padding:4mm 5mm;background:#fbf8f1;font-size:10.5pt;margin-bottom:5mm}
.yb{background:#FFE066;font-weight:800;padding:0 4px}
table.l.sm{font-size:8.6pt;line-height:1.3}table.l.sm td,table.l.sm th{padding:2.4px 4px}table.l.r6 td:last-child{white-space:nowrap}
table.f.sm th,table.f.sm td{padding:4px 8px;font-size:10pt}
"""


def page(label, body, note=""):
    nt = f'<div class="nt">{note}</div>' if note else ""
    return f'<section class="pg"><div class="lb"><span>{e(label)}</span><span>주식회사 엣지컴퍼니 · 공동구매 주관사</span></div>{body}{nt}</section>'


def doc(title, pages):
    return f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{e(title)}</title><style>{CSS}</style></head><body>{"".join(pages)}</body></html>'


def ymd():
    y, m, d = D.SIGN_DATE
    return f"{y}년 {m}월 {d}일"


def seal_img(seal_uri):
    return f'<img class="seal" src="{seal_uri}" alt="">' if seal_uri else ""


def sign(seal_uri, who="신청인"):
    return (f'<div class="dt">{ymd()}</div><div class="who">[{who}]<br>상 호 : {e(D.COMPANY)}<br>'
            f'대표자 : <span class="in">대표이사 {e(D.CEO)} (인){seal_img(seal_uri)}</span></div><div class="to">{e(TO)} 귀중</div>')


def sign_line(seal_uri):
    """목록 · 표 서류용 한 줄 서명(쪽이 꽉 찰 때) — 작성일 · 상호 · 대표이사 직인."""
    sl = f'<img src="{seal_uri}" style="position:absolute;width:15mm;height:15mm;right:-17mm;top:-4.5mm;opacity:.92" alt="">' if seal_uri else ""
    return (f'<div style="margin-top:4mm;text-align:right;font-size:10.5pt;padding-right:18mm">{ymd()} · {e(D.COMPANY)} 대표이사 {e(D.CEO)} '
            f'<span style="position:relative;display:inline-block">(인){sl}</span></div>')


def render(name, html_text):
    os.makedirs(WORK, exist_ok=True)
    hp = os.path.join(WORK, name + ".html")
    pp = os.path.join(WORK, name + ".pdf")
    open(hp, "w", encoding="utf-8").write(html_text)
    subprocess.run([find_chrome(), "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=8000",
                    f"--print-to-pdf={pp}", pathlib.Path(hp).as_uri()], check=True, capture_output=True, timeout=180)
    return pp


def nr(name):
    p = os.path.join(NR, name)
    assert os.path.exists(p), ("나리벡 제출본 증빙 없음", p)
    return fitz.open(p)


def prop_pages(prop, keys):
    """제안서 쪽을 제목(쪽 첫머리 글)으로 찾는다 → 0부터 쪽 번호 목록."""
    texts = [re.sub(r"[\s\u00a0\u2060]+", " ", p.get_text()) for p in prop]
    out = []
    for key in keys:
        hit = [i for i, t in enumerate(texts) if key in t[:420]]
        assert len(hit) == 1, ("제안서에서 쪽을 찾지 못함 · 여러 개", key, hit)
        out.append(hit[0])
    return out



# ------------------------------------------------------------ 6 실적 증빙 붙임(이미지는 나리벡 최종 제출본 03 · 09에서 꺼냄 — 가림 끝난 것)
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
# 실적표 증빙 칸(이 서류 안 붙임) — 없으면 '요청 시 제출'
EV6 = {"레이카운티": "A", "두산위브더제니스 센트럴사하": "A", "양정자이더샵SK VIEW 1·2단지": "A", "춘천 학곡지구 중해마루힐 포레스트": "A",
       "두산위브더제니스 오션시티": "A", "창원 센트럴 아이파크": "A · B-4", "힐스테이트 포항": "A", "에코델타 대성베르힐": "B-1 · B-3",
       "e편한세상 송도 더퍼스트비치": "B-2", "e편한세상 에코델타 센터포인트": "B-5 · C-1", "강서자이 에코델타": "B-6", "에코델타시티 푸르지오 린": "B-7",
       "남울산 노르웨이숲": "B-8", "영주자이 시그니처": "B-9", "부산 드파인 센텀": "C-2", "디에트르 더 퍼스트": "C-3",
       "부산사상 중흥S-클래스 그랜드센트럴": "B-0"}


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


def rec5():
    """최근 5년(공고일 2026.10.27 기준 · 입주 2023.04 이후) 입주박람회 주관 단지 = 최근 3년 500세대 이상 20 + 1,000세대 이상 2023.04 · 2023.07 2곳."""
    rows = [(m, nm, n) for m, nm, n, _j in D.RECENT3_500]
    rows += [(m, nm, n) for m, nm, _a, n in D.RECORDS if m < "2023.10"]
    return sorted(rows)


def p6_table(seal_uri):
    rows = rec5()
    tr = ""
    for i, (m, nm, n) in enumerate(rows, 1):
        when, where = D.EXPO_VENUE.get(nm, ("NICE 연혁 기재 주관" if EV6.get(nm) == "A" else "일정 자료 요청 시 제출", "-"))
        tr += (f'<tr><td class="n">{i}</td><td>{m}</td><td>{e(nm)}</td><td class="r">{n:,}</td><td>{e(when.replace(chr(10), " · "))}</td>'
               f'<td>{e(where)}</td><td>{e(EV6.get(nm, "요청 시"))}</td></tr>')
    ev_n = sum(1 for _m, nm, _n in rows if nm in EV6)
    body = ('<h2>최근 5년간 운영 실적표 · 담당 업무</h2>'
            f'<p style="font-size:10pt;margin-bottom:3mm">공고 5항 가 · 7항 나 · 기준 = 공고일(2026.10.31) 기준 최근 5년 · 입주 연월 순 · 아파트 입주박람회 주관 {len(rows)}개 단지 · '
            f'{sum(r[2] for r in rows):,}세대(500세대 이상)</p>'
            '<table class="l sm r6"><tr><th>No</th><th>입주</th><th>단지(모두 주관)</th><th>세대</th><th>박람회 일정</th><th>장소</th><th style="white-space:nowrap">증빙</th></tr>' + tr + '</table>'
            f'<div class="box" style="margin-top:4mm">증빙 = 이 파일의 실적 확인자료 A(NICE 연혁) · B(공식 행사일정 · 카페 공지) · C(주관사 협약서) · 증빙 첨부 {ev_n}개 단지 · 나머지는 협의회가 요청하시면 제출합니다(공고 6항 라 · 요청받은 보완자료). '
            '누적 수임 단지(전신 실적 · 입주 예정 포함)는 이 표에 넣지 않았습니다.</div>'
            + sign_line(seal_uri))
    return page("제출서류 나 · 최근 5년간 운영 실적표", body)


def ev_pages():
    s03, s09 = nr("03_입주박람회_실적_및_공동구매_증빙.pdf"), nr("09_기업신용평가서.pdf")
    nfn = os.path.join(WORK, "_ev", "nice_p9.png")
    os.makedirs(os.path.dirname(nfn), exist_ok=True)
    s09[9].get_pixmap(dpi=150).save(nfn)   # NICE 원본 9쪽(기업개요 · 연혁) — 09 = 표지 1쪽 + 원본 24쪽
    info = [("보고서명", "CLIP 기업신용평가보고서"), ("발행 기관", "NICE디앤비(dun & bradstreet)"), ("평가 대상", f"{D.COMPANY}({D.BIZ_NO})"),
            ("평가완료일", f"{D.NICE_DATE} · 연 1회 정기 평가(재무제표 기준) · 유효기간 안 최근 평가본"), ("발췌 범위", "원본 9쪽 ‘04 영업 현황(기업개요)’ 중 ‘연혁’")]
    pa = ('<h2>실적 확인자료 A · NICE디앤비 기업신용평가보고서 ‘연혁’ 발췌</h2><table class="f" style="margin-bottom:4mm">'
          + "".join(f"<tr><th>{a}</th><td>{e(b)}</td></tr>" for a, b in info) + "</table>"
          f'<img src="{pathlib.Path(nfn).as_uri()}" style="display:block;width:106mm;margin:0 auto;border:1px solid #bbb">'
          '<p style="font-size:10pt;margin-top:3mm">연혁의 2023/03 ~ 2026/07 주관 행이 1,000세대 이상 입주박람회 주관 실적입니다. 연혁 일자는 주관 협약 뒤 확정된 일정 기준이라, 창원 센트럴 아이파크(2026/07)는 평가 당시 이미 일정이 확정된 단지이며 2026.07.03 ~ 05 CECO에서 개최했습니다(붙임 B-4). 위 발췌는 원본과 같습니다.</p>')
    pages = [page("제출서류 나 · 실적 확인자료 A", pa)]
    # 검수 11-02 #2: 사상(1,572 · 입주 2023.07) = 입주민 소통 카페 주관사 게시판 캡처(나리벡 제출본 03 5쪽 · 입주민 닉네임 가림 끝난 것)
    uri0 = _img(s03, 5, 0, "b0.png")
    pages.append(page("제출서류 나 · 실적 확인자료 B-0 · 카페 주관사 게시판", (
        '<h2 style="font-size:12.5pt">B-0 · 부산사상 중흥S-클래스 그랜드센트럴(1,572세대 · 1,000세대 이상 주관)</h2>'
        '<p style="font-size:10pt;color:#444;margin-bottom:2mm">입주민 소통 카페 · 엣지컴퍼니 게시판(cafe.naver.com/f-e/cafes/30121620 · 게시판명 (주)엣지컴퍼니&amp;오케이시스템 · 오케이시스템은 당사 협력사) · '
        '작성자 ‘주관사엣지컴퍼니’ — 2022.12.14 박람회 수요조사 · 2022.12.31 주관사 인사 · 2023.01.16 입주 설명회 · 2023.02.20 박람회 날짜 · 장소 · 혜택 안내 · 2023.03.01 박람회 혜택 안내</p>'
        f'<img src="{uri0}" style="display:block;max-width:100%;max-height:205mm;margin:0 auto;border:1px solid #bbb">'),
        "화면 그대로 · 입주민 닉네임(동 · 호수)은 가림"))
    for grp in ([0], [1, 2], [3, 4], [5, 6], [7, 8]):   # 신분평 D11: 카페 공지 캡처(B-1)는 혼자 한 쪽에 크게
        body = ""
        for i in grp:
            j = i + 1
            pno, k, nm, src, when = B_CAPS[i]
            uri = _img(s03, pno, k, f"b{j}.png")
            mh = "205mm" if len(grp) == 1 else "92mm"
            body += (f'<div style="margin-bottom:7mm"><h2 style="font-size:12.5pt">B-{j} · {e(nm)}</h2>'
                     f'<p style="font-size:10pt;color:#444;margin-bottom:2mm">{e(src)} · {e(when)}</p>'
                     f'<img src="{uri}" style="display:block;max-width:100%;max-height:{mh};margin:0 auto;border:1px solid #bbb"></div>')
        pages.append(page("제출서류 나 · 실적 확인자료 B · 공식 행사일정 · 카페 공지", body,
                          "B-1 ~ B-4 = 1,000세대 이상 주관 단지 · B-5 ~ B-9 = 500 ~ 999세대 주관 단지 · 화면 그대로 · 입주민 닉네임만 가림"))
    for j, (pno, nm, dt) in enumerate(C_DOCS, 1):
        uri = _img(s03, pno, 0, f"c{j}.png", top=0.15)   # 고양 때 박힌 옛 머리글 · 제목 잘라냄
        body = (f'<h2>실적 확인자료 C-{j} · 주관사 협약서 사본 - {e(nm)}</h2><p style="font-size:10.5pt;margin-bottom:4mm">협약일 {dt} · 상대방 대표자 성명 · 연락처 · 계좌 가림</p>'
                f'<img src="{uri}" style="display:block;width:100%;border:1px solid #bbb">')
        pages.append(page("제출서류 나 · 실적 확인자료 C · 주관사 협약서(협약일 순)", body, "500 ~ 999세대 주관 단지의 협약서 - 입주박람회 운영 실적 증빙"))
    return pages


# ------------------------------------------------------------ 라 붙임 · 타 단지 공개 단가표(참고 · 신분평 G5 · D10 예방)
PRICE_PAGES = (22, 23)   # 나리벡 제출본 14 ⑥ = 2026.10 타 단지 공개 단가표(품목별 범위 · 실링팬 현금 괄호 가림본)


FONT_R, FONT_B = r"C:\Windows\Fonts\malgun.ttf", r"C:\Windows\Fonts\malgunbd.ttf"
PRICE_RETEXT = [("박람회 현장 계약가", "타 단지 공개 단가표(2026.10) · 참고"), ("그 외 전 품목은 박람회 현장 공개", "그 외 품목은 업체 견적"),
                ("'현장 제시' 항목은 박람회 현장에서 업체별로 안내합니다", "'업체 견적' 항목은 업체 견적서로 안내합니다"),
                ("현장 제시", "업체 견적"), ("부산 시내", "시내")]   # 검수 11-02 #8: 타 단지 표의 '현장' 표현 · 지역명 정리(가림 후 같은 자리에 다시 씀)


def retext(page, old, new):
    """page에서 old 글자를 배경색으로 가리고 같은 자리에 new를 맑은 고딕으로 다시 쓴다(폭에 맞춰 글자 크기 줄임). 바꾼 수를 돌려준다."""
    rects = page.search_for(old)
    if not rects:
        return 0
    pix = page.get_pixmap(dpi=144)
    sc = 144 / 72
    jobs = []
    for r in rects:
        bx = max(0, min(pix.width - 1, int((r.x0 - 1.5) * sc)))
        by = max(0, min(pix.height - 1, int((r.y0 + r.height / 2) * sc)))
        bg = tuple(c / 255 for c in pix.pixel(bx, by)[:3])
        _bg = pix.pixel(bx, by)[:3]
        dark = max(((pix.pixel(int(x * sc), int(y * sc))[:3]) for x in range(int(r.x0) + 1, int(r.x1) - 1) for y in range(int(r.y0) + 1, int(r.y1))),
                   key=lambda c: sum(abs(c[i] - _bg[i]) for i in range(3)))   # 글자색 = 배경과 가장 다른 화소(어두운 머리띠 위 흰 글자도)
        jobs.append((r, bg, tuple(c / 255 for c in dark)))
        page.add_redact_annot(r, fill=bg)
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
    for r, bg, fg in jobs:
        fs = min(r.height * 0.86, r.height * 0.86 * (r.width + 30) / max(1e-3, fitz.Font(fontfile=FONT_R).text_length(new, fontsize=r.height * 0.86)))
        page.insert_text((r.x0, r.y1 - r.height * 0.18), new, fontsize=fs, fontname="mg", fontfile=FONT_R, color=fg)
    return len(rects)


def stamp_cover(prop, seal):
    """검수 11-02 #1: 6항 나 '서명 또는 날인한 제안서' — 제안서 표지 오른쪽 아래에 작성일 · 상호 · 대표이사 직인."""
    pg = prop[0]
    W, H = pg.rect.width, pg.rect.height
    y = H * 0.845
    txt = f"{ymd()}   {D.COMPANY}  대표이사 {D.CEO}  (인)"
    fs = H * 0.022
    tl = fitz.Font(fontfile=FONT_B).text_length(txt, fontsize=fs)
    x = W * 0.94 - tl
    pg.insert_text((x, y), txt, fontsize=fs, fontname="mgb", fontfile=FONT_B, color=(0.93, 0.86, 0.70))
    sz = fs * 3.0
    xi = W * 0.94 - fitz.Font(fontfile=FONT_B).text_length("(인)", fontsize=fs) / 2
    pg.insert_image(fitz.Rect(xi - sz / 2, y - fs * 0.35 - sz / 2, xi + sz / 2, y - fs * 0.35 + sz / 2), filename=seal, overlay=True)


def p4_price_note():
    body = ('<h2>붙임 · 타 단지 공개 단가표(참고가격 근거)</h2>'
            '<table class="f"><tr><th>무엇인가</th><td>다른 단지 입주박람회(2026.10)에서 입주예정자에게 실제 공개한 품목별 시공 단가 범위(참여 업체 수 · 일반 / 프리미엄 · 시공 범위 · 84㎡ 기준)</td></tr>'
            '<tr><th>왜 붙이는가</th><td>공고 5항 다 · 라 - 제안서의 대표 품목 참고가격이 어디서 왔는지 보여 드리기 위해</td></tr>'
            f'<tr><th>이 단지 단가인가</th><td><b>아닙니다.</b> {e(SITE)} 단가로 약속하는 금액이 아니며, 확정 단가는 업체 공개 모집 → 박람회 30일 전 협의회 검수 → 14일 전 확정가 · 비교자료 공개로 정합니다(제안서 3 · 4장).</td></tr>'
            '<tr><th>‘업체 견적’ 표기</th><td>다른 단지 표에서 금액 없이 업체가 따로 안내한 칸은 <b>‘업체 견적’</b>으로 바꿔 적었습니다(같은 자리 · 가림 후 다시 씀 · 지역명도 가림). 이 단지는 <b>D-14에 전 품목 확정 단가를 미리 공개</b>하고, 현장에서 가격을 바꾸지 않습니다.</td></tr>'
            '<tr><th>가림 표시</th><td>머리의 ‘단지 ______’ 빈 밑줄과 회색 상자 = 다른 단지 이름 · 업체 정보 · 결제 조건 1곳을 가린 자리입니다(빈칸이 아님).</td></tr></table>')
    return page("제출서류 라 · 붙임 안내", body)


def p4_fee(seal_uri):
    """5항 다 · 마 · 7항 라: 대표 품목 가격표 · 추가비용 및 수수료 명세서 — 항목 · 부과 대상 · 방식 · 상한만(세부 금액은 업체 모집 뒤 확정)."""
    price = [("줄눈(현관 · 욕실 2곳 바닥)", "자재명 · 시공 면적", "34 ~ 35만원 / 상위 55 ~ 60만원"), ("탄성코트(베란다 · 다용도실 2곳)", "자재 계열 · 도막 횟수", "35 ~ 38만원 / 상위 45 ~ 48만원"),
             ("창호 필름(거실 + 안방 창)", "필름 제품명 · 등급", "42 ~ 50만원 / 상위 75 ~ 85만원"), ("입주청소(기본 범위)", "공정 · 범위표 · 면적", "3.3㎡당 1.3 ~ 1.4만원"),
             ("커튼 · 블라인드(거실 이중 · 안방 암막 · 작은방 2)", "원단 등급 · 창 크기", "88 ~ 100만원"), ("현관 중문(옵션 미선택 세대)", "형식 · 프레임 · 유리", "80 ~ 90만원"),
             ("시스템에어컨 4대(옵션 미선택 세대)", "제조사 · 모델 · 출시연도", "650만원(타 단지 1곳)")]
    fee = [("입점비(참가비)", "참여업체", "정액 · 품목군별 같은 기준 · 공구가와 연동 없음", "업체 모집 공고 전 협의회 승인 금액 이내 · 모집 공고에 공개"),
           ("판매수수료", "-", "받지 않음(계약 건 · 매출 비례 수수료 없음)", "-"),
           ("광고비", "-", "별도로 받지 않음(카페 · 홍보물 제작은 입점비 안)", "-"),
           ("발전기금(세대 혜택)", "업체에게 걷지 않음 · 주관사가 직접 사서 드림", f"{D.FUND_BASIS}에 주관사가 직접 사서 드리는 선택 항목", f"세대당 {D.FUND}만원 상당(안) · {D.FUND_DECIDE}"),
           ("구매자 추가비용", "구매자", "부가세 · 배송비 · 설치비 · 철거 · 추가 자재를 단가표에 칸으로 따로 적고 합계 = 총 부담액", "단가표에 없는 현장 추가 비용 받지 않음")]
    body = ('<h2>대표 품목 가격표 · 추가비용 및 수수료 명세서</h2>'
            f'<p style="font-size:10pt;margin-bottom:2.5mm">공고 5항 다 · 라 · 마 · 7항 라 · {e(SITE)} · 작성 {ymd()}</p>'
            '<h3>1. 대표 품목 참고가격(타 단지 공개 단가표 2026.10 · 참고 · 84㎡ 기준 · 이 단지 확정가 아님)</h3>'
            '<table class="l sm"><tr><th>품목 · 시공 범위</th><th>모델 · 규격 표기</th><th>참고가격</th></tr>'
            + "".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td><td class='r'>{e(c)}</td></tr>" for a, b, c in price) + '</table>'
            '<p style="font-size:9.4pt;color:#444;margin:1.5mm 0 1mm">부가세 = 참고가격은 타 단지 표기 그대로(부가세 포함 여부 미표기) · 확정 단가표에는 품목마다 부가세 포함 / 별도를 적습니다.</p>'
            '<p style="font-size:9.4pt;color:#444;margin:0 0 3mm">확정 시점 = 업체 선정 뒤 단가 제출 → 박람회 30일 전 협의회 검수 → 14일 전 확정가 · 같은 조건 일반 판매가 비교자료 공개(매장 2곳 + 온라인 1곳 · 출처 · 조사일) · '
            '적용기간 = 공개일 ~ 공동구매 운영기간 종료일 · 계약 후 7일 안 인근 매장이 더 싸면 차액 10배(1건당 최대 50만원 · 주관사 지급)</p>'
            '<h3>2. 추가비용 및 수수료 명세(항목 · 부과 대상 · 방식 · 상한)</h3>'
            '<table class="l sm"><tr><th>항목</th><th>부과 대상</th><th>방식</th><th>상한 · 공개</th></tr>'
            + "".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td><td>{e(c)}</td><td>{e(d)}</td></tr>" for a, b, c, d in fee) + '</table>'
            '<p style="font-size:9.4pt;color:#444;margin-top:1.5mm">업체별 세부 금액은 업체 모집 전에 협의회 승인으로 확정합니다. 협의회 · 임원 · 관계자에게 금전 · 물품 · 협찬금을 제공하지 않으며, 발전기금은 공증으로 진행합니다(공고 10항 아).</p>'
            + sign_line(seal_uri))
    return page("제출서류 라 · 가격표 · 수수료 명세서", body)


# ------------------------------------------------------------ 가 입찰참가 신청서
def p1(seal_uri):
    rows = [("업 체 명", D.COMPANY), ("대 표 자", f"대표이사 {D.CEO}"), ("소 재 지", f"{D.ADDRESS}(본점)"),
            ("사업자등록번호", D.BIZ_NO), ("법인등록번호", D.CORP_NO), ("설립일 · 자본금", f"{D.FOUNDED} · 2억원(법인등기 기재)"),
            ("업태 · 종목", "전시, 박람회 및 행사 대행업 외(사업자등록증 기재)"), ("운영책임자", f"{D.MANAGER[0]} · {D.MANAGER[1]}"),
            ("상담 담당자", D.CONSULT or "확인 후 기재"), ("연 락 처", f"{D.TEL}(대표번호) · {D.MANAGER[2]}(운영책임자)"), ("이 메 일", D.EMAIL)]
    body = ('<h1>입 찰 참 가 신 청 서</h1>'
            '<table class="f">' + "".join(f"<tr><th>{a}</th><td>{e(b)}</td></tr>" for a, b in rows) + "</table>"
            f'<p class="sv">당사는 {e(TO)}의 「{e(NOTICE)}」에 따라 {e(SITE)} 1BL 공동구매 주관사 선정 입찰에 참가하고자, 공고 7항에서 정한 제출서류 가 ~ 아를 갖추어 신청합니다. '
            '제출한 서류와 제안 내용은 사실과 같으며, 협의회가 요청하시는 보완자료는 지정 기한 안에 제출하겠습니다.</p>'
            '<div class="box"><b>붙임</b> 사업자등록증 사본 · 법인등기사항증명서(이 파일) · 나 회사소개서 · 담당 인력 · 실적 · 다 납세증명서 · 라 운영제안서 · 가격표 · 수수료 명세서 · '
            '마 취소 · 환불 · 사후관리 계획서 · 보험 · 보증 · 바 확약서 · 사 참여 업체 모집계획 · 아 해지 · 소송 이력 확인서 · 00 자료 목록</div>'
            + sign(seal_uri))
    return page("제출서류 가 · 입찰참가 신청서", body)


# ------------------------------------------------------------ 나 회사소개 · 담당 인력 현황
def p2_company(seal_uri, have_goyong):
    ov = [("상호 · 대표", f"{D.COMPANY} · 대표이사 {D.CEO}"), ("설립", f"{D.FOUNDED}(법인 설립 · 개업)"), ("본점", D.ADDRESS),
          ("자본금", "2억원(법인등기 기재)"), ("사업", "공동구매 · 입주박람회 주관 · 전시 · 박람회 및 행사 대행 · 조명 · 전기공사"),
          ("등록 · 인증", f"{D.ELEC_LICENSE} · ISO 9001 · 14001 · 45001"), ("관리 거점", "울산 본사(계약 · 책임) · 경인 지사(평택 · 상설 쇼룸 · 상담 · 시공 관리 · A/S 출동) · 지사 확장 중(2026.11 초 법인등기 예정 · 진행 중)"),
          ("연락", f"대표번호 {D.TEL} · {D.EMAIL}")]
    staff = [("대표이사", "1", "제안 조건 확약 · 제안설명 참석 · 결정권자"), ("주관사업 총괄 본부장", "1", "운영책임자 · 협의회 연락 · 업체 관리 감독")]
    staff += [(a, str(n), r) for a, n, r in D.STAFF]
    ded = [("운영책임자", f"주관사업 총괄 본부장 {D.MANAGER[0]}", "계약 ~ 사후관리 종료"), ("상담 담당자", D.CONSULT or "확인 후 기재", "계약 ~ 사후관리 종료"),
           ("전담 PM", "행사관리팀 정규직 1명(4대보험 명부 등재) · 실명은 계약 시 제출", "계약 ~ 사후관리 종료"),
           ("사후관리 · 민원", "대외지원팀 3명 · 주관 콜센터(평일 09:00 ~ 18:00 · 온라인 365일 접수)", "계약 ~ 사후관리 종료")]
    body = ('<h2>회사소개서 · 담당 인력 현황</h2>'
            '<h3>1. 회사 개요</h3><table class="f sm" style="margin-bottom:3mm">' + "".join(f"<tr><th>{a}</th><td>{e(b)}</td></tr>" for a, b in ov) + "</table>"
            '<h3>2. 임직원 구성(2026.10 · 4대보험 사업장 가입자 13명 · 대표 포함)</h3>'
            '<table class="l sm"><tr><th>구분</th><th>인원</th><th>역할</th></tr>'
            + "".join(f"<tr><td>{e(a)}</td><td class='r'>{b}명</td><td>{e(c)}</td></tr>" for a, b, c in staff)
            + f'<tr><td><b>합계</b></td><td class="r"><b>{sum(int(b) for _a, b, _c in staff)}명</b></td><td>정규직 13명 + 인턴 1명 · 실명은 계약 시 명단으로 제출(개인정보)</td></tr></table>'
            '<h3>3. 이 단지 담당 인력 · 역할 · 연락체계</h3>'
            '<table class="l sm"><tr><th>구분</th><th>인원 · 내용</th><th>기간</th></tr>'
            + "".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td><td>{e(c)}</td></tr>" for a, b, c in ded) + '</table>'
            f'<p style="font-size:9.6pt;color:#444;margin-top:2.5mm">연락체계 = 콜센터 {D.TEL} → 전담 PM → 운영책임자. 다음 쪽부터 '
            + ("고용 · 산재보험 가입증명원(2026.10.31) · " if have_goyong else "")
            + '4대보험 사업장가입자 명부 · 완납증명(2026.10.23 · 10.24 발급 · 개인정보 가림) · 회사소개(제안서 해당 쪽) · 최근 5년 운영 실적표 · 실적 확인자료입니다.</p>'
            + sign_line(seal_uri))
    return page("제출서류 나 · 회사소개서 · 담당 인력 현황", body)


# ------------------------------------------------------------ 마 취소 · 환불 · 사후관리 계획서
RULES = [
    ("제1조(목적)", f"이 계획은 {D.COMPANY}(이하 ‘주관사’)가 주관하는 {SITE} 1BL 공동구매(입주박람회 포함)에서 입주예정자(이하 ‘계약자’)를 보호하기 위해 계약 · 대금 · 취소 · 환불 · 사후관리 기준을 정한다."),
    ("제2조(계약 상대방 · 대금 수령자)", "① 공동구매 계약은 계약자와 참여업체(판매 · 시공업체) 사이에 업체 명의로 체결하고, 대금은 계약서에 적힌 업체 명의(사업자 계좌 · 카드 가맹점)로만 지급한다. "
     "② 주관사 직영 품목은 주관사가 계약 상대방 · 대금 수령자이다. ③ 주관사는 직영 품목 외 대금을 받지 않으며, 개인 계좌 송금은 금지한다."),
    ("제3조(계약금 · 잔금)", f"① 계약금은 계약 총액의 {D.DEPOSIT_MAX}% 이하로 한다(맞춤 제작 · 본사 규정 품목은 업체 선정 때 협의회 승인을 받아 단가표 · 계약서에 미리 표시). "
     "② 잔금은 시공 · 설치가 끝나고 계약자가 확인한 뒤 지급하며, 하자 · 미시공 부분이 있으면 보수가 끝난 뒤 지급할 수 있다. ③ 카드 · 현금 결제의 단가는 같다."),
    ("제4조(단계별 취소 · 환불)", "① 시공일 7일 전(청소 · 줄눈 · 탄성 등) · 15일 전(방충망 · 필름 · 시스템에어컨 등) 안에 취소하면 납부 금액 전액을 환불한다. ② 맞춤 제작 품목은 출고 지시 전까지 협의해 취소하고, 이후에는 실제 자재 · 제작비만 공제한다(공제 내역 서면 제시 · 주관사 검토). "
     "③ 업체 귀책(시공 지연 · 다른 제품 · 하자 미보수)이면 기한과 관계없이 전액 환불한다. ④ 환불금은 취소 확정일부터 3영업일 안에 지급한다. ⑤ 세부 기준은 붙임 ‘계약 취소 · 환불 규정 전문’(제1 ~ 10조 · 별표)에 따른다."),
    ("제5조(민원 접수 · 처리기한)", "① 접수 창구는 주관 콜센터 한 곳(대표번호 · 공식카페 · 카카오채널)이다. ② 24시간 안에 1차 회신(주말 · 공휴일 접수는 다음 영업일 12시까지)하고, 48시간 안에 방문 일정을 확정한다. "
     "③ 납품 지연 · 시공 불량은 업체에 시정 기한을 통보하고, 업체가 24시간 무응답이거나 처리를 미루면 주관사가 사실 확인 뒤 계약자에게 먼저 보상하고 업체와 정산한다."),
    ("제6조(기간)", f"① {D.CONTRACT_SPLIT[0]}. ② {D.CONTRACT_SPLIT[1]}. ③ 무상 A/S는 시공 품목 최소 2년, 브랜드 제품은 제조사 보증 기간으로 한다."),
    ("제7조(폐업 · 연락 두절 · 추가 책임)", "① 납품 · 시공 · 취소 · 환불 · 사후관리의 1차 책임은 참여업체가 진다. ② 업체가 이행하지 않거나 폐업 · 연락 두절로 처리가 어려우면 주관사가 사실 확인 뒤 추가 책임을 지고 처리한다(선보상 또는 협의회 승인 · 계약자 동의를 받아 대체 업체 이관 · 무상 A/S 기간 안 이관 비용 주관사). "
     "③ 추가 책임은 공동구매로 계약한 품목에 한하고, 계약서에 정한 보증 금액 안에서 이행한다. 최저가 차액 10배 보상은 1건당 최대 50만원(주관사 지급)이다. ④ 세대 · 공용부 건설 하자는 사업주체 · 시공사 책임이며, 주관사는 정리 · 공문 초안 · 전달 · 추적을 돕는다."),
    ("제8조(부실업체 조치)", "민원 · 지연이 확인되면 서면 경고 → 판매 · 홍보 중단 → 협의회 사전 승인으로 교체 · 이관 순서로 조치하고, 페널티(홍보정지 → 총액 10% 배상 → 자격박탈)를 부과한다. 업체가 바뀌어도 기존 구매계약과 사후관리는 이어진다."),
    ("제9조(보고 · 인계)", "① 처리 현황은 입주 지정기간 주 1회 · 이후 월 1회 협의회에 보고한다. ② 계약 종료 · 해지 시 미처리 주문 · 환불 · 사후관리 · 정산자료를 종료 후 30일 안에 합의한 방법으로 인계한다."),
    ("제10조(반영)", "이 계획과 붙임 규정은 계약서 또는 부속합의서에 반영하며, 모든 공동구매 계약서에 붙인다."),
]


def p5_rules(seal_uri=None):
    half = 5
    b1 = ('<h2>취소 · 환불 · 사후관리 계획서</h2>'
          f'<p style="font-size:10pt;margin-bottom:3mm">공고 5항 바 · 사 · 7항 마 · {SITE} 1BL 공동구매에 적용 · 모든 공동구매 계약서에 붙임</p>'
          + "".join(f'<div class="art"><b>{e(a)}</b> {e(b)}</div>' for a, b in RULES[:half]))
    b2 = ("".join(f'<div class="art"><b>{e(a)}</b> {e(b)}</div>' for a, b in RULES[half:])
          + '<div class="box" style="margin-top:4mm"><b>붙임</b> 계약 취소 · 환불 규정 전문 ① 제1 ~ 5조 · ② 제6 ~ 10조 · 별표(제안서 해당 쪽 그대로) → 다음 2쪽 · 계약 후 보증 제공계획 · 보험 가입증명 → 그 다음 쪽</div>'
          + sign_line(seal_uri))
    return [page("제출서류 마 · 취소 · 환불 · 사후관리 계획서 (1/2)", b1), page("제출서류 마 · 취소 · 환불 · 사후관리 계획서 (2/2)", b2)]


def p5_ins(seal_uri):
    rows = [("보험회사 · 상품", "KB손해보험 · 영업배상책임보험(일반보험 증권 · 2026.10.14 발급)"), ("증권번호", "2026-6774341(000)"),
            ("담보", "시설소유관리자배상책임 특별약관 · 구내치료비 특별약관"), ("계약자 · 피보험자", D.COMPANY),
            ("보험기간", "2026.10.14 24:00 ~ 2027.10.14 24:00(365일 · 매년 갱신)"), ("보장 대상 시설", "울산 울주군 청량읍 온산로 615-1, 2층 · 3층(본사 사업장)"),
            ("보상한도", "대인 1인당 1억원 · 1사고당 3억원 · 대물 1사고당 1억원 · 구내치료비 1인당 100만원 · 1사고당 300만원"), ("자기부담", "1사고당 10만원(대인 · 대물)"),
            ("청구 대상", "본사 사업장 시설 사고로 피해를 입은 제3자")]
    plan = [("행사(주최자)배상책임보험", "입주박람회 개최가 확정되면 행사 기간 · 장소 기준으로 가입 · 개장 전 증권 사본 제출 · 청구 대상 = 박람회장 관람객 등 제3자"),
            ("계약 후 보증(계약이행 · 하자보증보험)", "협약 체결 시 보증보험사 심사를 거쳐 협의회를 피보험자로 발급 · 금액은 협약 시 확정 · 보증기간 24개월 이상(공동구매 운영기간부터 무상 A/S 종료까지 공백이 없도록 협약 때 기산일을 정함) · 보장 대상은 계약서에 명시(공고 10항 라) · 증서 제출 = 계약 체결 시 협의회와 정한 날까지"),
            ("하자 예치금(주관사 자산)", "선보상 재원 · 최대 1억원 · 금액 · 예치 방식은 계약 때 확정"),
            ("참고 · 다른 용역 계약보증 1건", "서울보증보험 계약보증보험증권(2026.09.07 발급 · 주계약 = 광고대행 용역 · 공동구매 · 입주박람회 이행보증 아님) - 다음 쪽 가림본")]
    body = ('<h2>계약 후 보증 제공계획 · 보험 가입증명</h2>'
            '<h3>1. 계약 후 보증 · 박람회 행사배상</h3><table class="f sm" style="margin-bottom:3mm">' + "".join(f"<tr><th>{a}</th><td>{e(b)}</td></tr>" for a, b in plan) + "</table>"
            '<h3>2. 현재 가입 - 영업배상책임보험(시설소유관리자배상책임 · 증권 사본 다음 쪽)</h3><table class="f sm">' + "".join(f"<tr><th>{a}</th><td>{e(b)}</td></tr>" for a, b in rows) + "</table>"
            + sign_line(seal_uri))
    sgi = ('<h2>붙임 · 서울보증보험 계약보증보험증권 발급 이력</h2>'
           f'<div style="text-align:center"><img src="{pathlib.Path(SGI_PNG).as_uri()}" style="height:212mm;border:.6pt solid #bbb"></div>')
    return page("제출서류 마 · 보증 제공계획 · 보험 가입증명", body), page("제출서류 마 · 붙임 · 보증서 발급 이력", sgi,
                                                            "광고대행 용역 계약보증(공동구매 · 입주박람회 이행보증 아님) · 금액 · 상대방 정보 · 증권번호 일부 가림 · 원본은 협의회 요청 시 열람")


# ------------------------------------------------------------ 바 청렴 · 이해관계 · 개인정보 · 비밀유지 확약서
def p6_pledge(seal_uri):
    if D.CONFLICT_OK:
        conf = "없음 - 당사와 대표자 · 임직원은 협의회 운영진 · 사업관계자와 친족 · 고용 · 금전거래 등 이해관계가 없으며, 임직원 중 이 단지(1BL) 분양 계약자도 없습니다."
    else:
        conf = None
        if "바 이해관계 확인" not in BLANKS:
            BLANKS.append("바 이해관계 확인")
    items = [("청렴", "명의대여 · 실적차용 · 담합 및 운영진 · 심사 담당자 개인에 대한 금품 · 향응 제공을 하지 않고, 공식 절차 밖에서 발전기금 · 협찬금 · 수수료를 약속하지 않습니다(9항 다 · 라). 공고일 이후 사전 만남 · 개별 연락을 하지 않습니다(6항 바)."),
             ("이해관계 공개", None),
             ("개인정보 보호", "입주예정자 개인정보는 본인이 동의한 범위에서만 수집 · 보관 · 이용하고, 회원명부를 영업용으로 받거나 업체에 제공하지 않으며, 목적 달성 후 지체 없이 파기하고 결과를 협의회에 보고합니다(4항 라 · 10항 마). 선정 전 공식 주관사처럼 홍보하거나 개인정보를 수집하지 않습니다(9항 마)."),
             ("비밀유지", "입찰 · 협상 · 계약 과정에서 알게 된 협의회와 입주예정자의 정보를 계약 목적 외로 쓰거나 제3자에게 알리지 않으며, 이 의무는 계약 종료 뒤에도 유지됩니다.")]
    rows = "".join(f'<tr><th>{a}</th><td>{e(b) if b else (e(conf) if conf else "<span class=yb>확인 후 기재</span>")}</td></tr>' for a, b in items)
    body = ('<h1 style="letter-spacing:.06em;font-size:17pt">청렴 · 이해관계 공개 · 개인정보 보호 · 비밀유지 확약서</h1>'
            f'<p class="sv">{e(D.COMPANY)}는 {e(TO)}의 공동구매 주관사 선정 입찰에 참가하면서 다음과 같이 확약합니다.</p>'
            '<table class="f">' + rows + '</table>'
            '<p class="sv">위 사항을 위반하거나 이해관계를 숨긴 경우 입찰 무효 · 선정 취소(공고 9항) 등 협의회의 조치를 따릅니다.</p>'
            + sign(seal_uri, "확약인"))
    return page("제출서류 바 · 확약서", body)


# ------------------------------------------------------------ 사 참여 예정 업체 — 미정 → 모집계획 · 확인 절차
def p7_vendor(seal_uri):
    steps = [("1. 수요조사", "협약 뒤 입주예정자 수요조사로 품목을 정하고 협의회 승인을 받습니다(유상옵션과 겹치는 품목은 미선택 세대 기준)."),
             ("2. 공개 모집", "품목별 업체 모집 공고(협의회 승인 후) · 시공 품목은 천안 · 아산권 업체에 먼저 공지 · 브랜드 품목은 본사 · 공식 판매점"),
             ("3. 자격 확인", "사업자등록증 원본 대조 · 국세청 휴 · 폐업 조회 · 법정 면허 · 등록 · KC 인증 · 영업배상책임보험 · 국세 · 지방세 완납 · 공동구매 이력 또는 동종 시공 실적 · A/S 인력 · 특약이행각서"),
             ("4. 4단계 심사", "서류 → 단가 · 조건 → 품질 · 사후관리 → 협의회 승인. 지역 업체도 같은 기준"),
             ("5. 확정 · 제출", "확정 명단 · 사업자등록증 사본 · 자격자료 · 지역 비율을 협의회에 제출 · 업체가 바뀌면(사전 승인) 다시 제출")]
    body = ('<h2>참여 예정 업체 모집계획 및 확인 절차</h2>'
            '<p style="font-size:10.5pt;margin-bottom:3mm">공고 7항 사 · 참여 예정 업체는 아직 정하지 않았습니다. 주관사 선정 뒤 공개 모집으로 정하므로, 모집계획과 확인 절차를 제출합니다.</p>'
            '<table class="f">' + "".join(f"<tr><th>{a}</th><td>{e(b)}</td></tr>" for a, b in steps) + '</table>'
            '<div class="box"><b>지역 업체 구성</b> 시공 품목 참여업체 중 천안 · 아산권 업체(사업장 소재지 기준)를 50% 이상 구성하고, 70% 이상을 목표로 합니다. 비율은 업체 확정 때 사업자등록증으로 계산해 보고합니다.</div>'
            '<div class="box"><b>주관사 직영 품목</b> 조명 · 실링팬 · 커튼 · 욕실 환기(㈜엣지컴퍼니)도 다른 업체와 같은 공개 심사 · 같은 단가 사전 공개 · 같은 가격 보호 규정을 거칩니다.</div>'
            + sign_line(seal_uri))
    return page("제출서류 사 · 참여 예정 업체 모집계획 · 확인 절차", body)


# ------------------------------------------------------------ 아 해지 · 소송 이력 확인서
def p8_history(seal_uri):
    if D.HISTORY_OK:
        hist = ("없음", "없음", "없음")
    else:
        hist = None
        if "아 해지 · 소송 이력 확인" not in BLANKS:
            BLANKS.append("아 해지 · 소송 이력 확인")
    q = [("입주예정자협의회와의 계약상 문제로 해지된 이력", 0), ("입주예정자협의회 관련 소송 이력", 1), ("진행 중인 소송", 2)]
    rows = "".join(f'<tr><th>{a}</th><td style="text-align:center;font-weight:800">{hist[i] if hist else "<span class=yb>확인 후 기재</span>"}</td></tr>' for a, i in q)
    body = ('<h1 style="letter-spacing:.04em;font-size:17pt">입주예정자협의회 계약 해지 및 소송 이력 확인서</h1>'
            '<table class="f" style="margin-bottom:5mm">' + "".join(f"<tr><th>{a}</th><td>{e(b)}</td></tr>" for a, b in
                                                                   [("업 체 명", D.COMPANY), ("대 표 자", f"대표이사 {D.CEO}"), ("소 재 지", D.ADDRESS), ("사업자등록번호", D.BIZ_NO)]) + "</table>"
            '<table class="f">' + rows + '</table>'
            f'<p class="sv">당사는 공고 4항 사 · 9항 바에 따라 위 내용이 사실임을 확인하며, 사실과 다른 것이 확인되면 참가 제한 · 심사 제외 · 선정 취소 등 {e(TO)}의 조치를 따르겠습니다.</p>'
            + sign(seal_uri, "확인인"))
    return page("제출서류 아 · 해지 · 소송 이력 확인서", body)


def p00(spans, blanks):
    rows = "".join(f'<tr><td class="n">{n}</td><td>{e(t)}</td><td>{e(fn)}</td><td class="r">{pc}쪽</td><td>{e(s)}</td></tr>' for n, t, fn, pc, s in spans)
    body = ('<h2>자료 목록</h2>'
            f'<p style="margin-bottom:4mm;font-size:11pt">건명 : {e(NOTICE)} · {e(SITE)} 1BL<br>제출처 : {e(TO)} · {e(D.SUBMIT_TO)}(동시 제출) · 공고 7항 제출서류 가 ~ 아 순서</p>'
            '<table class="l sm"><tr><th>No</th><th>서류(7항)</th><th>파일</th><th>쪽</th><th>발급일 · 내용</th></tr>' + rows + "</table>"
            '<p style="font-size:9.6pt;color:#555;margin-top:4mm">공고 6항 나에 따라 파일을 나누어 이 목록을 함께 냅니다. 모든 파일은 PDF이며, 파일 이름 앞 번호 = 이 목록 번호입니다. 대표이사 직인(서명 또는 날인 · 6항 나) = 01 신청서 · 02 회사소개 · 실적표 · 04 제안서 표지 · 가격표 · 수수료 명세서 · 05 계획서 · 보증 제공계획 · 06 · 07 · 08(자체 양식). 개인정보는 가림본(원본은 협의회 요청 시 열람).</p>'
            + (f'<p style="color:#b00;font-weight:800;margin-top:4mm">※ 확인본 - 빈칸 {len(blanks)}곳({e(" · ".join(blanks))})을 채우기 전에는 제출하지 않습니다.</p>' if blanks else ""))
    return page("00 · 자료 목록", body)


FILES = [  # (번호, 7항 서류, 파일 이름)
    ("01", "가 입찰참가 신청서 · 사업자등록증 · 법인등기사항증명서", "01_가_입찰참가신청서_사업자등록증_법인등기"),
    ("02", "나 회사소개서 · 담당 인력 현황 · 최근 5년 운영 실적표 · 실적 확인자료", "02_나_회사소개서_담당인력_운영실적_확인자료"),
    ("03", "다 국세 · 지방세 납세증명서", "03_다_국세_지방세_납세증명서"),
    ("04", "라 운영제안서 · 제안설명 자료 · 대표 품목 가격표 · 추가비용 및 수수료 명세서", "04_라_운영제안서_가격표_수수료명세서"),
    ("05", "마 취소 · 환불 · 사후관리 계획서 · 보험 가입증명서 · 계약 후 보증 제공계획", "05_마_취소환불_사후관리계획서_보험_보증"),
    ("06", "바 청렴 · 이해관계 공개 · 개인정보 보호 · 비밀유지 확약서", "06_바_청렴_이해관계_개인정보_비밀유지_확약서"),
    ("07", "사 참여 예정 업체 현황 · 자격자료(미정 → 모집계획 · 확인 절차)", "07_사_참여업체_모집계획_확인절차"),
    ("08", "아 입주예정자협의회 계약 해지 및 소송 이력 확인서", "08_아_계약해지_소송이력_확인서"),
]


def main():
    seal = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None
    assert seal and os.path.exists(seal), "투명 직인 PNG 경로를 주세요(대표이사 직인)"
    seal_uri = pathlib.Path(seal).resolve().as_uri()
    final = "--final" in sys.argv
    assert os.path.exists(PROPOSAL), "제안서 밝은 시안 PDF가 없음 — build_eo.py → light_build.py 먼저"
    assert os.path.exists(KB), ("KB 영업배상책임보험 증권 없음", KB)
    prop = fitz.open(PROPOSAL)
    stamp_cover(prop, seal)
    BLANKS.clear()

    def take(src, pages):
        d = fitz.open()
        for p in pages:
            d.insert_pdf(src, from_page=p - 1, to_page=p - 1)
        return d

    def add_prop(d, idx):
        for i in idx:
            d.insert_pdf(prop, from_page=i, to_page=i)

    _kt = fitz.open(KB)[0].get_text()   # 증권 사본이 종류 그대로(영업배상 · 시설소유관리자)인지 글자로 확인
    for k in ("2026- 6774341", "영업배상책임보험", "시설소유관리자배상책임", "100,000,000", "300,000,000"):
        assert k in _kt, f"KB 증권 글자 확인 실패: {k}"

    docs, desc = {}, {}
    d1 = fitz.open(render("01_신청서", doc("입찰참가 신청서", [p1(seal_uri)])))
    d1.insert_pdf(nr("05_사업자등록증.pdf"))
    d3 = take(nr("06_법인등기부등본_법인인감증명서.pdf"), [1, 2])
    for r_ in REG_MASK:
        d3[1].add_redact_annot(fitz.Rect(*r_), fill=(0.6, 0.6, 0.6))
    d3[1].apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS)
    d1.insert_pdf(d3)
    docs["01"] = d1
    desc["01"] = f"신청서(직인 · 작성 {ymd()}) + 사업자등록증({D.ISSUE['biz']}) + 법인등기({D.ISSUE['reg']} · 자본금 2억원 · 대표 주소 가림)"
    have_goyong = os.path.exists(GOYONG)
    d2 = fitz.open(render("02_회사소개", doc("회사소개서 · 담당 인력", [p2_company(seal_uri, have_goyong)])))
    if have_goyong:
        d2.insert_pdf(fitz.open(GOYONG))
    n0 = d2.page_count
    d2.insert_pdf(nr("08_4대보험_가입자명부_완납증명서.pdf"))
    d2[n0].add_redact_annot(fitz.Rect(*ROSTER_MASK), fill=(0.72, 0.72, 0.72))   # 명부 1쪽 주민번호 칸 전체
    d2[n0].apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS)
    add_prop(d2, prop_pages(prop, ["숫자로 보는 엣지컴퍼니", "엣지컴퍼니 연혁", "경인 쇼룸 · 자본금 2억", "회사 수행 실적과 운영책임자 역할", "조직 구성 - ", "담당 인력 - 운영책임자"]))
    d2.insert_pdf(fitz.open(render("02_실적표", doc("최근 5년 실적표", [p6_table(seal_uri)]))))
    d2.insert_pdf(fitz.open(render("02_붙임", doc("실적 확인자료", ev_pages()))))
    docs["02"] = d2
    desc["02"] = ("회사 개요 · 인력 현황(직인) · 고용 · 산재 가입증명원 10.31 · " if have_goyong else "회사 개요 · 인력 현황(직인) · ") + \
        f"4대보험 명부 · 완납증명(10.23 · 10.24) · 회사소개 6쪽 · 실적표 {len(rec5())}개 단지 · NICE 연혁 · 공식 행사일정 · 카페 공지 10 · 협약서 3"
    d4 = take(nr("07_국세_지방세_완납증명서.pdf"), [1, 2])
    d4[1].add_redact_annot(fitz.Rect(*TAX_PHONE), fill=(0.6, 0.6, 0.6))
    d4[1].apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS)
    docs["03"] = d4
    desc["03"] = f"국세 · 지방세 각 1부 · {D.ISSUE['tax']} 발급 · 유효기간 안 · 휴대번호 가림"
    d7 = fitz.open()
    d7.insert_pdf(prop)
    d7.insert_pdf(fitz.open(render("04_가격표_수수료", doc("가격표 · 수수료 명세서", [p4_fee(seal_uri), p4_price_note()]))))
    _n14 = nr("14_기타_제안_확인자료.pdf")
    n_price = d7.page_count
    for p_ in PRICE_PAGES:
        d7.insert_pdf(_n14, from_page=p_ - 1, to_page=p_ - 1)
    _hit = {}
    for k_ in range(n_price, d7.page_count):
        for a_, b_ in PRICE_RETEXT:
            _hit[a_] = _hit.get(a_, 0) + retext(d7[k_], a_, b_)
    assert all(_hit.values()), ("공개 단가표 바꿀 글자를 못 찾음", _hit)
    _pt = "".join(d7[k_].get_text() for k_ in range(n_price, d7.page_count))
    assert "현장 제시" not in _pt and "현장 계약가" not in _pt and "부산" not in _pt, "공개 단가표 '현장' 표현 남음"
    d7.subset_fonts()   # 다시 쓴 글자 · 표지 날인 글꼴(맑은 고딕)을 쓴 글자만 남김 — 용량
    docs["04"] = d7
    desc["04"] = f"운영제안서 {prop.page_count}쪽(5항 가 ~ 자 순서 · 제안설명 자료 겸 · 표지 직인) + 가격표 · 수수료 명세서(직인) + 붙임 안내 + 타 단지 공개 단가표 2쪽(참고)"
    d5 = fitz.open(render("05_계획서", doc("취소 · 환불 · 사후관리 계획서", p5_rules(seal_uri))))
    add_prop(d5, prop_pages(prop, ["계약 취소 · 환불 규정 전문 ① 제1 ~ 5조", "계약 취소 · 환불 규정 전문 ② 제6 ~ 10조"]))
    ins, sgi = p5_ins(seal_uri)
    d5.insert_pdf(fitz.open(render("05_보험", doc("보험 · 보증", [ins]))))
    _kb = fitz.open(KB)
    for w_ in ("노경희", "010-2744-0360"):   # 검수 11-02 #11: 보험대리점 담당자 이름 · 휴대번호 가림
        for r_ in _kb[0].search_for(w_):
            _kb[0].add_redact_annot(r_ + (-1, -1, 1, 1), fill=(0.72, 0.72, 0.72))
    _kb[0].apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS)
    assert "노경희" not in _kb[0].get_text() and "2744" not in _kb[0].get_text()
    d5.insert_pdf(_kb)
    assert os.path.exists(SGI_PNG), ("SGI 가림본 없음", SGI_PNG)
    d5.insert_pdf(fitz.open(render("05_보증이력", doc("보증서 발급 이력", [sgi]))))
    docs["05"] = d5
    desc["05"] = "계획서 2쪽 + 환불 규정 전문 2쪽 + 보험 · 보증 제공계획(직인) + KB 영업배상책임보험 증권 사본(종류 그대로) + SGI 발급 이력(가림)"
    docs["06"] = fitz.open(render("06_확약서", doc("확약서", [p6_pledge(seal_uri)])))
    desc["06"] = "청렴 · 이해관계 공개 · 개인정보 보호 · 비밀유지 · 직인"
    docs["07"] = fitz.open(render("07_모집계획", doc("모집계획", [p7_vendor(seal_uri)])))
    desc["07"] = "업체 미정 → 모집계획 · 확인 절차 · 천안 · 아산권 우선 · 직인"
    docs["08"] = fitz.open(render("08_이력확인서", doc("이력 확인서", [p8_history(seal_uri)])))
    desc["08"] = "해지 · 소송(진행 중 포함) 이력 · 직인"
    render("작성서류_날인출력용", doc("작성 서류 날인 출력용", [p1(None), p6_pledge(None), p8_history(None)]))   # 실물 직인으로 찍을 때

    blanks = list(BLANKS)
    if final:
        assert not blanks, f"--final: 빈칸이 남음 {blanks}"
    spans = [(n, t, fn + ".pdf", docs[n].page_count, desc[n]) for n, t, fn in FILES]
    d0 = fitz.open(render("00_자료목록", doc("자료 목록", [p00(spans, blanks)])))
    assert d0.page_count == 1, "목록이 한 쪽을 넘음"

    out_dir = BLANK_DIR if blanks else os.path.join(SUBMIT, "번호별")
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)
    paths = [os.path.join(out_dir, "00_자료목록.pdf")]
    d0.save(paths[0], garbage=GARBAGE, deflate=True)
    whole = fitz.open()
    whole.insert_pdf(d0)
    for n, _t, fn in FILES:
        p = os.path.join(out_dir, fn + ".pdf")
        docs[n].save(p, garbage=GARBAGE, deflate=True)
        paths.append(p)
        whole.insert_pdf(docs[n])
    zp = os.path.join(out_dir if blanks else os.path.dirname(out_dir), ZIP_NAME[:-4] + "_보내지않음.zip" if blanks else ZIP_NAME)
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p, os.path.basename(p))
    with zipfile.ZipFile(zp) as z:   # 풀어서 같은 파일인지 대조(이름 · 해시)
        got = {i.filename: hashlib.sha256(z.read(i.filename)).hexdigest() for i in z.infolist()}
    assert got == {os.path.basename(p): hashlib.sha256(open(p, "rb").read()).hexdigest() for p in paths}, "ZIP 대조 불일치"
    wp = os.path.join(os.path.dirname(zp), "예비_통합본_보내지않음.pdf")
    whole.save(wp, garbage=GARBAGE, deflate=True)

    tag = "확인본(빈칸 있음 · 제출 금지)" if blanks else "제출본"
    print(f"{tag} → {out_dir}")
    for (n, t, fn, pc, s), p in zip(spans, paths[1:]):
        print(f"  {n} {fn} · {pc}쪽 · {os.path.getsize(p) / 1e6:.1f}MB")
    print(f"  ZIP {os.path.getsize(zp) / 1e6:.1f}MB → {zp}")
    print(f"  예비 통합본 {whole.page_count}쪽 · {os.path.getsize(wp) / 1e6:.1f}MB → {wp}")
    if blanks:
        print(f"[빈칸 {len(blanks)}곳] " + " / ".join(blanks))
    dst = NOTICE_DIR + ("_확인본_빈칸있음" if blanks else "")
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(out_dir, dst)
    if not blanks:
        shutil.copy2(zp, dst)
        shutil.copy2(wp, dst)   # 규칙 21: 통합본은 제출 폴더에 함께 보관(보내지 않음)
    print(f"  공고 폴더 사본 → {dst}")


if __name__ == "__main__":
    main()
