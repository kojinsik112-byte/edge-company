# -*- coding: utf-8 -*-
"""신분평 더웨이시티 제일풍경채 입주박람회 및 공동구매 주관사 선정 — 공고 '마. 제출서류' 1) ~ 10) 생성 · 번호별 PDF + ZIP 1개 + 예비 통합본(A4).

공고: 이메일 접수(thewaycity-official@naver.com) · 11.06(금) 18:00 도착분 · 통합 · 파일 1개 · 압축 금지 · 형식 · 제목 규칙 없음 → 번호별 PDF + ZIP 1개(규칙 21)
      · '제출서류는 자유양식으로 작성하되 공고에서 요구한 사항을 빠짐없이 포함'(마 ※) · 날인 요구 0건 → 작성 서류는 대표이사 직인만.
  00 제출서류 목록(번호 · 파일 · 쪽 · 발급일 · 내용)
  1  참가신청서(업체명 · 대표자 · 소재지 · 담당자 · 연락처) · 직인
  2  사업자등록증 사본(2026.10.23)                     3  법인등기사항증명서(2026.10.23 · 대표 주소 가림)
  4  국세 · 지방세 납세증명서(2026.10.23 · 휴대번호 가림)
  5  회사소개서 및 정규직 · 전담인력 구성표 = 회사 개요 · 구성표(직인) + 고용 · 산재 가입증명원(10.31) + 4대보험 사업장가입자 명부 · 완납증명(10.23 · 가림) + 제안서 회사 쪽
  6  최근 5년 관련 행사 실적표 및 증빙 = 실적표(직인) + A NICE 연혁 + B 공식 행사일정 · 카페 공지 + C 주관사 협약서 3건
  7  사업제안서 = build_sb.py 밝은 시안
  8  계약 취소 · 환불 · 하자 · A/S 운영 규정 + 환불 규정 전문(제안서 쪽) + 이행각서(A/S 완료 시까지 책임 · 청주 지역 업체 50% 이상) · 직인
  9  계약이행보증보험 등 보증수단 제출 가능 확인서(10억 원 이상 또는 준하는 수단) · 직인 + SGI 계약보증 발급 이력(가림 · 광고대행 용역 · 입주박람회 이행보증 아님)
  10 공정참여 및 이해관계 공개 확약서 · 직인

날인: 대표이사 직인(투명 PNG)만 · 법인인감 · 사용인감계 없음(규칙 4 · 법인인감 11.03까지 없음).
빈칸: 10 이해관계 '없음'(data.CONFLICT_OK) — 비어 있으면 노란 칸 · '작업/확인본_빈칸있음/'에만 낸다(제출본 · ZIP 안 만듦). --final은 빈칸 0이어야 함.
출력: 작업/(중간) · 제출본/번호별/00 ~ 10 PDF + 제출본/<FILE_TITLE>.zip + 제출본/예비_통합본_보내지않음.pdf → 공고 폴더 사본
사용: python docs_sb.py <투명 직인.png> [--final]
"""
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
PROPOSAL = os.path.join(HERE, "엣지컴퍼니_신분평제일풍경채_입주박람회_주관사_제안서_밝은시안.pdf")
WORK = os.path.join(HERE, "작업")
SGI_PNG = os.path.join(HERE, "assets_ins", "os_sgi_bond_masked.png")
GOYONG = os.path.join(WORK, "05_고용산재보험_가입증명원_20261031.pdf")   # 근로복지공단 고용 · 산재보험 가입증명원(2026.10.31 · 제출용)
REG_MASK = [(203, 163, 556, 177), (30, 176, 50, 187)]   # 등기부 2/2쪽 대표이사 주소(10.23 발급본)
TAX_PHONE = (119, 228.5, 196, 239)                      # 지방세 납세증명서 2쪽 대표 휴대번호(그림)
PAID_DATES = "2026.10.23 · 10.24"                      # 완납증명 발급일(건강 · 연금 10.23 · 고용 · 산재 10.24 · 검증 11-01 D9)
ROSTER_MASK = (87, 311, 193, 571)                       # 명부 1쪽 주민번호 칸 전체(챗 검증 10-31 청주와 같게)
SUBMIT = os.path.join(HERE, "제출본")
BLANK_DIR = os.path.join(WORK, "확인본_빈칸있음")
NOTICE_DIR = r"C:\본부장\05주관사 입찰공고\20261105_신분평 더웨이시티 제일풍경채\제안자료_주식회사 엣지컴퍼니"
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
    return f'<section class="pg"><div class="lb"><span>{e(label)}</span><span>주식회사 엣지컴퍼니 · 입주박람회 및 공동구매 주관사</span></div>{body}{nt}</section>'


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
       "남울산 노르웨이숲": "B-8", "영주자이 시그니처": "B-9", "부산 드파인 센텀": "C-2", "디에트르 더 퍼스트": "C-3"}


B_CROP = {1: (0, 0, 1, 0.9)}   # B-1 = 아래 검색창 · 빈 칸만 자름(카페 제목 [인증] 살림 · 비율 x0, y0, x1, y1)


def _img(src, pno, k, name, top=0, box=None):
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
    if box:
        from PIL import Image
        im = Image.open(fn)
        w_, h_ = im.size
        im.crop((int(w_ * box[0]), int(h_ * box[1]), int(w_ * box[2]), int(h_ * box[3]))).save(fn)
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
    body = ('<h2>최근 5년간 관련 행사 실적표</h2>'
            f'<p style="font-size:10pt;margin-bottom:3mm">공고 라 2) · 마 6) · 기준 = 공고일(2026.10.27) 기준 최근 5년 · 입주 연월 순 · 아파트 입주박람회 주관 {len(rows)}개 단지 · '
            f'{sum(r[2] for r in rows):,}세대(500세대 이상)</p>'
            '<table class="l sm r6"><tr><th>No</th><th>입주</th><th>단지(모두 주관)</th><th>세대</th><th>박람회 일정</th><th>장소</th><th style="white-space:nowrap">증빙</th></tr>' + tr + '</table>'
            f'<div class="box" style="margin-top:4mm">증빙 = 이 서류의 붙임 A(NICE 연혁) · B(공식 행사일정 · 카페 공지) · C(주관사 협약서) · 증빙 첨부 {ev_n}개 단지 · 나머지는 협의회가 요청하시면 제출합니다(공고 마 ※). '
            '누적 수임 단지(전신 실적 · 입주 예정 포함)는 이 표에 넣지 않았습니다.</div>'
            + sign_line(seal_uri))
    return page("서류 6 · 최근 5년간 관련 행사 실적표", body)


def ev_pages():
    s03, s09 = nr("03_입주박람회_실적_및_공동구매_증빙.pdf"), nr("09_기업신용평가서.pdf")
    nfn = os.path.join(WORK, "_ev", "nice_p9.png")
    os.makedirs(os.path.dirname(nfn), exist_ok=True)
    s09[9].get_pixmap(dpi=150).save(nfn)   # NICE 원본 9쪽(기업개요 · 연혁) — 09 = 표지 1쪽 + 원본 24쪽
    info = [("보고서명", "CLIP 기업신용평가보고서"), ("발행 기관", "NICE디앤비(dun & bradstreet)"), ("평가 대상", f"{D.COMPANY}({D.BIZ_NO})"),
            ("평가완료일", f"{D.NICE_DATE} · 연 1회 정기 평가(재무제표 기준) · 유효기간 안 최근 평가본"), ("발췌 범위", "원본 9쪽 ‘04 영업 현황(기업개요)’ 중 ‘연혁’")]
    pa = ('<h2>붙임 A · NICE디앤비 기업신용평가보고서 ‘연혁’ 발췌</h2><table class="f" style="margin-bottom:4mm">'
          + "".join(f"<tr><th>{a}</th><td>{e(b)}</td></tr>" for a, b in info) + "</table>"
          f'<img src="{pathlib.Path(nfn).as_uri()}" style="display:block;width:106mm;margin:0 auto;border:1px solid #bbb">'
          '<p style="font-size:10pt;margin-top:3mm">연혁의 2023/03 ~ 2026/07 주관 행이 1,000세대 이상 입주박람회 주관 실적입니다. 연혁 일자는 주관 협약 뒤 확정된 일정 기준이라, 창원 센트럴 아이파크(2026/07)는 평가 당시 이미 일정이 확정된 단지이며 2026.07.03 ~ 05 CECO에서 개최했습니다(붙임 B-4). 위 발췌는 원본과 같습니다.</p>')
    pages = [page("서류 6 · 붙임 A", pa)]
    # 검증 11-01 D11: B-1(카페 공지 목록)은 세로로 길어 두 장 묶음에서 읽기 어려움 → 아래를 잘라 한 쪽에 크게(쪽수 그대로 5)
    groups = [[0]] + [list(range(i, min(i + 2, len(B_CAPS)))) for i in range(1, len(B_CAPS), 2)]
    for g in groups:
        body = ""
        for j in (x + 1 for x in g):
            pno, k, nm, src, when = B_CAPS[j - 1]
            uri = _img(s03, pno, k, f"b{j}.png", box=B_CROP.get(j))
            mh = "205mm" if len(g) == 1 else "92mm"
            body += (f'<div style="margin-bottom:7mm"><h2 style="font-size:12.5pt">B-{j} · {e(nm)}</h2>'
                     f'<p style="font-size:10pt;color:#444;margin-bottom:2mm">{e(src)} · {e(when)}</p>'
                     f'<img src="{uri}" style="display:block;max-width:100%;max-height:{mh};margin:0 auto;border:1px solid #bbb"></div>')
        pages.append(page("서류 6 · 붙임 B · 공식 행사일정 · 카페 공지", body,
                          "B-1 ~ B-4 = 1,000세대 이상 주관 단지 · B-5 ~ B-9 = 500 ~ 999세대 주관 단지 · 화면 그대로 · 입주민 닉네임만 가림"))
    for j, (pno, nm, dt) in enumerate(C_DOCS, 1):
        uri = _img(s03, pno, 0, f"c{j}.png", top=0.15)   # 고양 때 박힌 옛 머리글 · 제목 잘라냄
        body = (f'<h2>붙임 C-{j} · 주관사 협약서 사본 - {e(nm)}</h2><p style="font-size:10.5pt;margin-bottom:4mm">협약일 {dt} · 상대방 대표자 성명 · 연락처 · 계좌 가림</p>'
                f'<img src="{uri}" style="display:block;width:100%;border:1px solid #bbb">')
        pages.append(page("서류 6 · 붙임 C · 주관사 협약서(협약일 순)", body, "500 ~ 999세대 주관 단지의 협약서 - 입주박람회 운영 실적 증빙"))
    return pages


# ------------------------------------------------------------ 7 붙임 · 타 단지 공개 단가표(바 2) 나 · 라 · 법정 10-31)
PRICE_PAGES = (22, 23)   # 나리벡 제출본 14 ⑥ = 2026.10 타 단지 공개 단가표(품목별 범위 · 실링팬 현금 괄호 가림본)


def p7_price_note():
    body = ('<h2>붙임 · 타 단지 공개 단가표(참고)</h2>'
            '<table class="f"><tr><th>무엇인가</th><td>다른 단지 입주박람회(2026.10)에서 입주예정자에게 실제 공개한 품목별 시공 단가 범위(참여 업체 수 · 일반 / 프리미엄 · 시공 범위)</td></tr>'
            '<tr><th>왜 붙이는가</th><td>공고 바 2) 나 · 라 - 대표 품목의 제품 · 규격 · 가격 · 시공 범위와 비교 자료를 어떤 형식으로 공개하는지 보여 드리기 위해</td></tr>'
            f'<tr><th>이 단지 단가인가</th><td><b>아닙니다.</b> {e(SITE)} 단가로 약속하는 금액이 아니며, 확정 단가는 업체 공개 입찰 → 박람회 30일 전 협의회 검수 → 14일 전 비교자료 공개로 정합니다(사업제안서 가격 쪽).</td></tr>'
            f'<tr><th>‘현장 제시’ 표기</th><td>그 단지의 진행 방식입니다. {e(SITE)}는 박람회 30일 전 협의회 검수 → 14일 전 비교자료 공개(협의회 승인 후)로 가격을 먼저 정하고, 현장에서 가격을 바꾸지 않습니다(사업제안서 p.16 · 17).</td></tr>'
            '<tr><th>가림</th><td>다른 단지 이름(머리 ‘단지’ 칸 = 가림) · 업체 정보 · 결제 조건 1곳(회색 상자 = 가림)</td></tr></table>')
    return page("서류 7 · 붙임 안내", body)


# ------------------------------------------------------------ 1 참가신청서
def p1(seal_uri):
    rows = [("업 체 명", D.COMPANY), ("대 표 자", f"대표이사 {D.CEO}"), ("소 재 지", f"{D.ADDRESS}(본점)"),
            ("사업자등록번호", D.BIZ_NO), ("법인등록번호", D.CORP_NO), ("설립일 · 자본금", f"{D.FOUNDED} · 2억원(법인등기 기재)"),
            ("업태 · 종목", "전시, 박람회 및 행사 대행업 외(사업자등록증 기재)"), ("담 당 자", f"{D.MANAGER[0]} · {D.MANAGER[1]}"),
            ("연 락 처", f"{D.MANAGER[2]}(담당자) · {D.TEL}(대표번호)"), ("이 메 일", D.EMAIL)]
    body = ('<h1>참 가 신 청 서</h1>'
            '<table class="f">' + "".join(f"<tr><th>{a}</th><td>{e(b)}</td></tr>" for a, b in rows) + "</table>"
            f'<p class="sv">당사는 {e(TO)}의 「{e(NOTICE)}」에 따라 입주박람회 및 공동구매 운영 주관사 선정에 참가하고자, 공고에서 정한 제출서류 1) ~ 10)을 갖추어 신청합니다. '
            '제출한 서류와 제안 내용은 사실과 같으며, 협의회가 사실 확인을 위해 추가 증빙을 요청하시면 바로 제출하겠습니다.</p>'
            '<div class="box"><b>붙임</b> 2 사업자등록증 사본 · 3 법인등기사항증명서 · 4 국세 · 지방세 납세증명서 · 5 회사소개서 및 정규직 · 전담인력 구성표 · '
            '6 최근 5년간 관련 행사 실적표 및 증빙 · 7 사업제안서 · 8 운영 규정 및 이행각서 · 9 보증수단 제출 가능 확인서 · 10 공정참여 및 이해관계 공개 확약서</div>'
            + sign(seal_uri))
    return page("서류 1 · 참가신청서", body)


# ------------------------------------------------------------ 5 회사소개 · 구성표
def p5(seal_uri, have_goyong):
    ov = [("상호 · 대표", f"{D.COMPANY} · 대표이사 {D.CEO}"), ("설립", f"{D.FOUNDED}(법인 설립 · 개업)"), ("본점", D.ADDRESS),
          ("자본금", "2억원(법인등기 기재)"), ("사업", "입주박람회 · 공동구매 주관 · 전시 · 박람회 및 행사 대행 · 조명 · 전기공사"),
          ("등록 · 인증", f"{D.ELEC_LICENSE} · ISO 9001 · 14001 · 45001"), ("관리 거점", "울산 본사(계약 · 책임) · 청주 지사(직지대로 642 · 상담 · 시공 관리 · A/S 출동) · 보조 거점 경인 지사(평택 · 상설 쇼룸)"),
          ("연락", f"대표번호 {D.TEL} · {D.EMAIL}")]
    staff = [("대표이사", "1", "제안 조건 확약 · PT 참석 · 결정권자"), ("주관사업 총괄 본부장", "1", "이 단지 총괄 책임자 · 협의회 회의 · 업체 관리 감독")]
    staff += [(a, str(n), r) for a, n, r in D.STAFF]
    ded = [("총괄 책임자", "주관사업 총괄 본부장 1명", "계약 ~ A/S 완료"), ("전담 PM", "행사관리팀 정규직 1명(4대보험 명부 등재) · 실명은 계약 시 제출", "계약 ~ A/S 완료"),
           ("박람회 현장", "현장 책임자 1명 + 운영 인력(예시 약 21명 · 외부 인력 포함)", "박람회 기간"),
           ("사후관리 · 민원", "대외지원팀 3명 · 주관 콜센터(평일 09:00 ~ 18:00 · 온라인 365일 접수)", "계약 ~ A/S 완료")]
    body = ('<h2>회사소개서 · 정규직 · 전담인력 구성표</h2>'
            '<h3>1. 회사 개요</h3><table class="f sm" style="margin-bottom:3mm">' + "".join(f"<tr><th>{a}</th><td>{e(b)}</td></tr>" for a, b in ov) + "</table>"
            '<h3>2. 임직원 구성(2026.10 · 정규직 = 4대보험 사업장 가입자 13명 · 대표 포함 · 공고 기준 7명 이상 + 인턴 1명)</h3>'
            '<table class="l sm"><tr><th>구분</th><th>인원</th><th>역할</th></tr>'
            + "".join(f"<tr><td>{e(a)}</td><td class='r'>{b}명</td><td>{e(c)}</td></tr>" for a, b, c in staff)
            + f'<tr><td><b>합계</b></td><td class="r"><b>{sum(int(b) for _a, b, _c in staff)}명</b></td><td>정규직 13명 + 인턴 1명 · 실명은 계약 시 명단으로 제출(개인정보)</td></tr></table>'
            '<h3>3. 이 단지 전담인력 · 연락체계</h3>'
            '<table class="l sm"><tr><th>구분</th><th>인원 · 내용</th><th>기간</th></tr>'
            + "".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td><td>{e(c)}</td></tr>" for a, b, c in ded) + '</table>'
            f'<p style="font-size:9.6pt;color:#444;margin-top:2.5mm">연락체계 = 콜센터 {D.TEL} → 전담 PM → 총괄 본부장({D.MANAGER[2]}) · 긴급 건은 총괄 본부장 직통. 다음 쪽부터 '
            + ("고용 · 산재보험 가입증명원(2026.10.31) · " if have_goyong else "")
            + f'4대보험 사업장가입자 명부({D.ROSTER_DATE}) · 완납증명({PAID_DATES}) · 개인정보 가림 · 회사소개(사업제안서 해당 쪽)입니다.</p>'
            + sign_line(seal_uri))
    return page("서류 5 · 회사소개서 및 정규직 · 전담인력 구성표", body)


# ------------------------------------------------------------ 8 운영 규정 · 이행각서
RULES = [
    ("제1조(목적)", f"이 규정은 {D.COMPANY}(이하 ‘주관사’)가 주관하는 {SITE} 입주박람회 및 공동구매에서 입주예정자(이하 ‘계약자’)를 보호하기 위해 협력업체 선정, 계약 취소 · 환불, 하자 · A/S 처리 기준을 정한다."),
    ("제2조(협력업체 선정 기준)", "① 사업자등록 · 통신판매업 신고(해당 시), 품목에 법정 면허 · 등록이 있으면 그 등록증, KC 등 법정 인증, 영업배상책임보험, 국세 · 지방세 완납, 특약이행각서를 갖춘 업체만 참가한다. "
     "② 서류는 원본 대조와 발급 기관 공공 조회로 확인한다. ③ 4단계 공개 심사(공개 모집 → 서류 · 가격 심사 → 현장 · 세부 심사 → 협의회 승인)로 선정하고, 청주 지역 업체를 우선 모집한다."),
    ("제3조(계약금 · 대금 보호)", f"① 계약금은 계약 총액의 {D.DEPOSIT_MAX}% 이하로 한다(맞춤 제작 · 본사 규정 품목은 업체 선정 때 협의회 승인을 받아 미리 표시). "
     "② 계약금 · 구매대금은 금융기관 · PG사 등 제3자 기관의 결제대금예치(에스크로)로 보관하고, 시공 · 설치 · 인도 확인 뒤 업체에 지급한다. 구체적인 운영 범위와 조건은 계약 체결 시 정한다. ③ 카드 · 현금 결제의 단가는 같다."),
    ("제4조(취소 · 환불)", "① 품목별 취소 기한(시공일 7일 · 15일 전, 맞춤 제작은 출고 지시 전) 안에 취소하면 납부 금액 전액을 환불한다. ② 시공 지연 · 계약과 다른 제품 · 하자 미보수 등 업체 귀책이면 기한과 관계없이 전액 환불한다. "
     "③ 환불금은 취소 확정일부터 3영업일 안에 지급한다. ④ 세부 기준은 붙임 ‘계약 취소 · 환불 규정 전문’(제1 ~ 10조 · 별표)에 따른다."),
    ("제5조(하자 · A/S 접수 · 처리)", "① 접수 창구는 주관 콜센터 한 곳(대표번호 · 공식카페 · 카카오채널)이며 전담 PM이 담당한다. ② 24시간 안에 1차 회신(주말 · 공휴일 접수는 다음 영업일 12시까지)하고, 48시간 안에 방문 일정을 확정한다. "
     "③ 업체가 24시간 무응답이거나 처리를 미루면 주관사가 사실 확인 뒤 계약자에게 먼저 보상하고 업체와 정산한다."),
    ("제6조(무상 A/S · 사후관리 기간)", "① 무상 A/S는 시공 품목 최소 2년, 브랜드 제품은 제조사 보증 기간으로 한다. ② 사후관리 기간은 2028.08.31 또는 주관사 및 협력업체의 제반 A/S가 완료된 때 중 늦은 때까지로 한다. "
     "③ ‘A/S 완료’는 무상 A/S 기간 안에 접수된 공동구매 품목 건의 처리가 끝난 때를 말하며, 세부 기준은 계약서에서 협의회와 정한다."),
    ("제7조(폐업 · 연락 두절)", "협력업체가 폐업 · 연락 두절되면 협의회 승인과 계약자 동의를 받아 대체 업체로 이관하고, 무상 A/S 기간 안의 이관 비용은 주관사가 부담한다. 미이행 금액은 주관사가 먼저 보상한다."),
    ("제8조(책임 범위)", "주관사 = 업체 선정 · 계약 관리 · 접수 · 선보상 · 이관 · 이행 감독 / 협력업체 = 판매 · 시공 · 하자보수 · A/S / 세대 · 공용부 건설 하자 = 사업주체 · 시공사(주관사는 협의회 요청 시 정리 · 전달 · 추적 지원)."),
    ("제9조(부실업체 조치)", "민원 · 지연이 확인되면 서면 경고 → 판매 · 홍보 중단 → 협의회 승인으로 교체 · 이관 순서로 조치하고, 페널티(홍보정지 → 총액 10% 배상 → 자격박탈)를 부과한다."),
    ("제10조(보고 · 효력)", "주관사는 A/S 처리 현황을 입주 지정기간 주 1회 · 이후 월 1회 협의회에 보고한다. 이 규정은 계약 체결일부터 제6조 ②의 기간까지 체결된 계약에 적용하며, 계약서 또는 부속합의서에 반영한다."),
]


def p8_rules():
    half = 6
    b1 = ('<h2>계약 취소 · 환불 · 하자 · A/S 운영 규정</h2>'
          f'<p style="font-size:10pt;margin-bottom:3mm">공고 라 5) · 9) · 마 8) · 바 4) · {SITE} 입주박람회 및 공동구매에 적용 · 모든 공동구매 계약서에 붙임</p>'
          + "".join(f'<div class="art"><b>{e(a)}</b> {e(b)}</div>' for a, b in RULES[:half]))
    b2 = ("".join(f'<div class="art"><b>{e(a)}</b> {e(b)}</div>' for a, b in RULES[half:])
          + '<div class="box" style="margin-top:4mm"><b>붙임</b> 계약 취소 · 환불 규정 전문 ① 제1 ~ 5조 · ② 제6 ~ 10조 · 별표(사업제안서 해당 쪽 그대로) → 다음 2쪽 · 이행각서 → 그 다음 쪽</div>')
    return [page("서류 8 · 운영 규정 (1/2)", b1), page("서류 8 · 운영 규정 (2/2)", b2)]


def p8_gaksu(seal_uri):
    items = [
        "주관사는 협력업체가 판매 · 시공한 공동구매 품목에 대하여 A/S가 완료될 때까지(무상 A/S 기간 안에 접수된 건의 처리 완료 · 세부 기준은 계약서에서 협의회와 정함) 계약 이행 · 하자보수 · A/S 책임을 집니다.",
        "협력업체가 이행하지 않거나 폐업 · 연락 두절된 경우, 주관사가 사실 확인 뒤 계약자에게 먼저 보상하거나 협의회 승인 · 계약자 동의를 받아 대체 업체로 이관합니다.",
        "협력업체 중 청주 지역 업체(사업장 소재지 기준)를 50% 이상 구성하며, 70% 이상 구성을 목표로 합니다. 선정 후 청주권 업체를 우선 공개 모집하고, 협력업체 확정 시 명단과 사업자등록증 사본을 증빙으로 제출합니다. 이 비율을 이행하지 못한 경우 공고 라 11)에 따른 A/S 지연 가산금을 계약서에서 정하는 기준에 따라 부담합니다.",
        "운영 규정(서류 8)과 계약 취소 · 환불 규정 전문을 모든 공동구매 계약서에 붙이고, 위 사항을 계약서 또는 부속합의서에 반영하는 데 동의합니다.",
    ]
    body = ('<h1>이 행 각 서</h1>'
            f'<p class="sv">{e(D.COMPANY)}(이하 ‘주관사’)는 {e(TO)}가 시행하는 입주박람회 및 공동구매의 주관사로 선정되는 경우, 공고 라 9) · 11)에 따라 다음 사항을 이행할 것을 각서합니다.</p>'
            '<ol class="c">' + "".join(f"<li>{e(x)}</li>" for x in items) + '</ol>'
            + sign(seal_uri, "각서인"))
    return page("서류 8 · 이행각서", body)


# ------------------------------------------------------------ 9 보증수단 제출 가능 확인서
def p9(seal_uri):
    rows = [("보증 수단", "계약이행보증보험(보증금액 10억 원 이상) 또는 이에 준하는 보증 수단"), ("피보험자(채권자)", f"{TO} 또는 협의회가 지정하는 명의"),
            ("보증 대상", "계약서에서 정한 주관사의 계약상 의무 이행"), ("보증기간", "24개월 · 기산일은 계약 때 협의회와 확정(사업제안서 · 환불 규정 제7조와 같음)"), ("제출 시기", "계약 체결 시 협의회와 정한 날까지"),
            ("발급 이력", "서울보증보험 계약보증보험증권 발급 이력 사본 붙임(2026.09.07 발급 · 주계약 = 광고대행 용역 · 입주박람회 이행보증 아님)")]
    body = ('<h1 style="letter-spacing:.12em">보증수단 제출 가능 확인서</h1>'
            '<table class="f" style="margin-bottom:5mm">' + "".join(f"<tr><th>{a}</th><td>{e(b)}</td></tr>" for a, b in
                                                                   [("업 체 명", D.COMPANY), ("대 표 자", f"대표이사 {D.CEO}"), ("소 재 지", D.ADDRESS), ("사업자등록번호", D.BIZ_NO)]) + "</table>"
            f'<p class="sv">{e(D.COMPANY)}는 {e(SITE)} 입주박람회 및 공동구매 주관사로 선정되어 계약을 체결하는 경우, 공고 라 6)에 따라 계약상 의무 이행을 담보하는 다음 보증 수단을 제출할 수 있음을 확인합니다.</p>'
            '<table class="f">' + "".join(f"<tr><th>{a}</th><td>{e(b)}</td></tr>" for a, b in rows) + "</table>"
            + sign(seal_uri, "확인인"))
    sgi = ('<h2>붙임 · 서울보증보험 계약보증보험증권 발급 이력</h2>'
           f'<div style="text-align:center"><img src="{pathlib.Path(SGI_PNG).as_uri()}" style="height:212mm;border:.6pt solid #bbb"></div>')
    return [page("서류 9 · 보증수단 제출 가능 확인서", body),
            page("서류 9 · 붙임", sgi, "광고대행 용역 계약보증(입주박람회 이행보증 아님) · 금액 · 상대방 정보 · 증권번호 일부 가림 · 원본은 협의회 요청 시 열람")]


# ------------------------------------------------------------ 10 공정참여 · 이해관계 공개 확약서
def p10(seal_uri):
    if D.CONFLICT_OK:
        conf = "없음 - 당사와 대표자 · 임직원은 협의회 임원 또는 평가위원과 친족 · 고용 · 금전거래 등 평가의 공정성에 영향을 미칠 수 있는 이해관계가 없습니다."
    else:
        conf = None
        if "서류 10 이해관계 확인" not in BLANKS:
            BLANKS.append("서류 10 이해관계 확인")
    items = [
        "허위자료 제출, 금품 제공, 부당한 청탁 등 선정의 공정성을 해치는 행위를 하지 않습니다(공고 라 10).",
        "업체 및 그 관계자는 금품 · 향응 제공, 청탁, 담합 등 부당행위를 하지 않습니다(공고 자 3).",
        "선정 전후를 불문하고 협의회 및 그 임원에게 어떠한 명목으로도 금전 또는 물품을 제공하거나 제공을 약속하지 않습니다(공고 자 5). 세대 혜택은 입주예정자 각 세대에 현물 · 서비스로 직접 전달하고, 협의회 업무 지원은 용역으로만 합니다.",
        "입주예정자 개인정보는 필요한 법적 요건과 절차를 갖춘 경우에만 처리합니다(공고 차 4).",
        "당사는 영업 기간 중 계약 취소 · 환불 · 하자 · A/S 사유로 인한 법적 분쟁이 없었음을 확약합니다(공고 라 5)).",
        "위 사항을 위반한 경우 공고 차 6)에 따른 협의회의 조치를 따릅니다.",
    ]
    body = ('<h1 style="letter-spacing:.1em">공정참여 및 이해관계 공개 확약서</h1>'
            f'<p class="sv">{e(D.COMPANY)}는 {e(TO)}의 입주박람회 및 공동구매 주관사 선정에 참가하면서 다음과 같이 확약합니다.</p>'
            '<h3>1. 이해관계 공개(공고 자 1) · 2))</h3>'
            '<table class="f"><tr><th>협의회 임원 · 평가위원과의 이해관계</th><td>'
            + (e(conf) if conf else '<span class="yb">확인 후 기재</span>') + '</td></tr></table>'
            '<h3>2. 공정참여 확약</h3><ol class="c">' + "".join(f"<li>{e(x)}</li>" for x in items) + '</ol>'
            + sign(seal_uri, "확약인"))
    return page("서류 10 · 공정참여 및 이해관계 공개 확약서", body)


def p00(spans, blanks):
    rows = "".join(f'<tr><td class="n">{n}</td><td>{e(t)}</td><td>{e(fn)}</td><td class="r">{pc}쪽</td><td>{e(s)}</td></tr>' for n, t, fn, pc, s in spans)
    body = ('<h2>제출서류 목록</h2>'
            f'<p style="margin-bottom:4mm;font-size:11pt">건명 : {e(NOTICE)}<br>제출처 : {e(TO)} · {e(D.SUBMIT_TO)} · 공고 마. 제출서류 순서(1 ~ 10)</p>'
            '<table class="l"><tr><th>No</th><th>서류</th><th>파일</th><th>쪽</th><th>발급일 · 내용</th></tr>' + rows + "</table>"
            '<p style="font-size:9.6pt;color:#555;margin-top:4mm">모든 파일은 PDF이며, 파일 이름 앞 번호 = 공고 제출서류 번호입니다. 작성 서류(1 · 5 · 6 · 8 · 9 · 10)는 자유양식 · 대표이사 직인 · 개인정보는 가림본(원본은 협의회 요청 시 열람).</p>'
            + (f'<p style="color:#b00;font-weight:800;margin-top:4mm">※ 확인본 - 빈칸 {len(blanks)}곳({e(" · ".join(blanks))})을 채우기 전에는 제출하지 않습니다.</p>' if blanks else ""))
    return page("제출서류 목록", body)


FILES = [  # (번호, 공고 서류 이름, 파일 이름)
    ("1", "참가신청서", "01_참가신청서"),
    ("2", "사업자등록증 사본", "02_사업자등록증"),
    ("3", "법인등기사항증명서", "03_법인등기사항증명서"),
    ("4", "국세 및 지방세 납세증명서", "04_국세_지방세_납세증명서"),
    ("5", "회사소개서 및 정규직 · 전담인력 구성표", "05_회사소개서_정규직_전담인력_구성표"),
    ("6", "최근 5년간 관련 행사 실적표 및 증빙자료", "06_최근5년_행사실적표_증빙"),
    ("7", "사업제안서", "07_사업제안서"),
    ("8", "계약 취소 · 환불 · 하자 · A/S 운영 규정 및 이행각서", "08_운영규정_이행각서"),
    ("9", "계약이행보증보험 등 보증수단 제출 가능 확인서", "09_보증수단_제출가능_확인서"),
    ("10", "공정참여 및 이해관계 공개 확약서", "10_공정참여_이해관계공개_확약서"),
]


def main():
    seal = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None
    assert seal and os.path.exists(seal), "투명 직인 PNG 경로를 주세요(대표이사 직인)"
    seal_uri = pathlib.Path(seal).resolve().as_uri()
    final = "--final" in sys.argv
    assert os.path.exists(PROPOSAL), "제안서 밝은 시안 PDF가 없음 — build_sb.py → light_build.py 먼저"
    prop = fitz.open(PROPOSAL)
    BLANKS.clear()

    def take(src, pages):
        d = fitz.open()
        for p in pages:
            d.insert_pdf(src, from_page=p - 1, to_page=p - 1)
        return d

    def add_prop(d, idx):
        for i in idx:
            d.insert_pdf(prop, from_page=i, to_page=i)

    docs, desc = {}, {}
    docs["1"] = fitz.open(render("01_참가신청서", doc("참가신청서", [p1(seal_uri)])))
    desc["1"] = f"자유양식 · 담당자 · 연락처 · 대표이사 직인 · 작성 {ymd()}"
    docs["2"] = take(nr("05_사업자등록증.pdf"), [1])
    desc["2"] = f"{D.ISSUE['biz']} 발급"
    d3 = take(nr("06_법인등기부등본_법인인감증명서.pdf"), [1, 2])
    for r_ in REG_MASK:
        d3[1].add_redact_annot(fitz.Rect(*r_), fill=(0.6, 0.6, 0.6))
    d3[1].apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS)
    docs["3"] = d3
    desc["3"] = f"{D.ISSUE['reg']} 발급 · 자본금 2억원 · 대표 주소 가림"
    d4 = take(nr("07_국세_지방세_완납증명서.pdf"), [1, 2])
    d4[1].add_redact_annot(fitz.Rect(*TAX_PHONE), fill=(0.6, 0.6, 0.6))
    d4[1].apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS)
    docs["4"] = d4
    desc["4"] = f"국세 · 지방세 각 1부 · {D.ISSUE['tax']} 발급 · 유효기간 안 · 휴대번호 가림"

    have_goyong = os.path.exists(GOYONG)
    d5 = fitz.open(render("05_구성표", doc("회사소개서 · 구성표", [p5(seal_uri, have_goyong)])))
    if have_goyong:
        d5.insert_pdf(fitz.open(GOYONG))
    n0 = d5.page_count
    d5.insert_pdf(nr("08_4대보험_가입자명부_완납증명서.pdf"))
    d5[n0].add_redact_annot(fitz.Rect(*ROSTER_MASK), fill=(0.72, 0.72, 0.72))   # 명부 1쪽 주민번호 칸 전체
    d5[n0].apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS)
    add_prop(d5, prop_pages(prop, ["숫자로 보는 엣지컴퍼니", "엣지컴퍼니 연혁", "운영 · 자본금 2억", "대표자 · 핵심 운영인력 수행 경험", "조직 구성 - ", "전담 체계 - 정규직"]))
    docs["5"] = d5
    desc["5"] = ("구성표(직인) · 고용 · 산재 가입증명원 2026.10.31 · " if have_goyong else "구성표(직인) · ") + f"4대보험 명부 {D.ROSTER_DATE} · 완납증명 {PAID_DATES} · 회사소개 6쪽"

    d6 = fitz.open(render("06_실적표", doc("최근 5년 실적표", [p6_table(seal_uri)])))
    d6.insert_pdf(fitz.open(render("06_붙임", doc("서류 6 붙임", ev_pages()))))
    docs["6"] = d6
    desc["6"] = f"실적표 {len(rec5())}개 단지(직인) + A NICE 연혁 + B 공식 행사일정 · 카페 공지 9 + C 주관사 협약서 3"
    d7 = fitz.open()
    d7.insert_pdf(prop)
    d7.insert_pdf(fitz.open(render("07_붙임안내", doc("서류 7 붙임", [p7_price_note()]))))
    _n14 = nr("14_기타_제안_확인자료.pdf")
    for p_ in PRICE_PAGES:
        d7.insert_pdf(_n14, from_page=p_ - 1, to_page=p_ - 1)
        if p_ == PRICE_PAGES[0]:   # 검증 11-01 D10: 머리 '단지 ____' 빈 밑줄이 채우지 않은 칸으로 보임 → '(가림)' 표기
            d7[-1].insert_text((491, 64.5), "(다른 단지 · 가림)", fontsize=7.5, fontname="mg", fontfile=r"C:\Windows\Fonts\malgun.ttf", color=(0.35, 0.35, 0.35))
    docs["7"] = d7
    desc["7"] = f"제안서 {prop.page_count}쪽(평가표 8항목 순서 · 바 1) ~ 7) 모두) + 붙임 3쪽(안내 1 + 타 단지 공개 단가표 2 · 참고 · 이 단지 단가 아님)"

    d8 = fitz.open(render("08_운영규정", doc("운영 규정", p8_rules())))
    add_prop(d8, prop_pages(prop, ["계약 취소 · 환불 규정 전문 ① 제1 ~ 5조", "계약 취소 · 환불 규정 전문 ② 제6 ~ 10조"]))
    d8.insert_pdf(fitz.open(render("08_이행각서", doc("이행각서", [p8_gaksu(seal_uri)]))))
    docs["8"] = d8
    desc["8"] = "운영 규정 제1 ~ 10조 + 환불 규정 전문 2쪽 + 이행각서(A/S 완료까지 · 청주 지역 업체 50% 이상) · 직인"
    assert os.path.exists(SGI_PNG), ("SGI 가림본 없음", SGI_PNG)
    docs["9"] = fitz.open(render("09_보증확인서", doc("보증수단 제출 가능 확인서", p9(seal_uri))))
    desc["9"] = "10억 원 이상 또는 준하는 수단 · 직인 + SGI 계약보증 발급 이력(가림)"
    docs["10"] = fitz.open(render("10_확약서", doc("공정참여 및 이해관계 공개 확약서", [p10(seal_uri)])))
    desc["10"] = "이해관계 공개 · 공정참여 확약 · 직인"
    render("작성서류_날인출력용", doc("작성 서류 날인 출력용", [p1(None), p8_gaksu(None)] + p9(None)[:1] + [p10(None)]))   # 실물 직인으로 찍을 때

    blanks = list(BLANKS)
    if final:
        assert not blanks, f"--final: 빈칸이 남음 {blanks}"
    spans = [(n, t, fn + ".pdf", docs[n].page_count, desc[n]) for n, t, fn in FILES]
    d0 = fitz.open(render("00_제출서류_목록", doc("제출서류 목록", [p00(spans, blanks)])))
    assert d0.page_count == 1, "목록이 한 쪽을 넘음"

    out_dir = BLANK_DIR if blanks else os.path.join(SUBMIT, "번호별")
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)
    paths = [os.path.join(out_dir, "00_제출서류_목록.pdf")]
    d0.save(paths[0], garbage=GARBAGE, deflate=True)
    whole = fitz.open()
    whole.insert_pdf(d0)
    for n, _t, fn in FILES:
        p = os.path.join(out_dir, fn + ".pdf")
        docs[n].save(p, garbage=GARBAGE, deflate=True)
        paths.append(p)
        whole.insert_pdf(docs[n])
    zp = os.path.join(os.path.dirname(out_dir) if not blanks else out_dir, ZIP_NAME if not blanks else ZIP_NAME[:-4] + "_보내지않음.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p, os.path.basename(p))
    with zipfile.ZipFile(zp) as z:   # 풀어서 같은 파일인지 대조(이름 · 크기)
        got = {i.filename: i.file_size for i in z.infolist()}
    assert got == {os.path.basename(p): os.path.getsize(p) for p in paths}, "ZIP 대조 불일치"
    wp = os.path.join(os.path.dirname(zp), "예비_통합본_보내지않음.pdf")
    whole.save(wp, garbage=GARBAGE, deflate=True)

    tag = "확인본(빈칸 있음 · 제출 금지)" if blanks else "제출본"
    print(f"{tag} → {out_dir}")
    for (n, t, fn, pc, s), p in zip(spans, paths[1:]):
        print(f"  {n} {fn} · {pc}쪽 · {os.path.getsize(p) / 1e6:.1f}MB · {s}")
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
