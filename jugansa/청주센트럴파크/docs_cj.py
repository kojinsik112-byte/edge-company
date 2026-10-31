# -*- coding: utf-8 -*-
"""두산위브더제니스 청주 센트럴파크 입주박람회 주관사 입찰 — 공고 3. 제출 서류 ① ~ ⑪ 생성 · 번호별 PDF + ZIP 1개 + 예비 통합본(A4 세로).

공고: E-mail 접수(kmg07m@naver.com / ※ PDF) · '아래 안내된 순서로 PDF 형식' · '제출 형식 및 순서 기준이 상이할 경우 검토 과정에서 제외될 수 있음'
      · 제목 "[주관사 제안서]_주식회사 엣지컴퍼니" · 11.01(일)까지(시각 미기재 → 11.01 12:00 전 발송 · 질의 메일 없음).
  00 제출 서류 목록(번호 · 파일 · 쪽 · 발급일)
  ①  입주박람회 제안서 = build_cj.py 밝은 시안(PT 자료)       ②  사업자등록증 사본(2026.10.23)
  ③  기업신용등급 평가서 = NICE디앤비 CLIP(2026.06.19 · 2025 결산 포함 · 가림 · 청주 표지)
  ④  법인 등기부등본(2026.10.23 · 대표 주소 가림)            ⑤  인감증명서(2026.10.26 · 가림)
  ⑥  국세 · 지방세 완납 증명서(2026.10.23 · 휴대번호 가림)
  ⑦  4대 보험 사업장 가입증명서 및 조직도 = 안내 + [사업장 가입증명서(본부장 발급본 · 없으면 빈칸 쪽)] + 사업장가입자 명부(10.23) + 4대보험 완납증명(10.23 · 10.24) + 조직도(제안서 쪽)
  ⑧  입주박람회 행사 수행 경험 이력 및 증빙 = 안내 + A NICE 연혁 + B 공식 행사일정 · 카페 공지 + C 주관사 협약서 3건
  ⑨  하자보수 이행각서 [서식1] — 별지서식 문구 그대로(‘상단 금액’ 포함 · 고치지 않음) · 대표이사 직인 · 생년월일 = D.CEO_BIRTH(없으면 빈칸)
  ⑩  개별 입주박람회 및 단지 영업행위 금지 서약서 [서식2](서식 제목 ‘이의 제기 금지 서약서’ 그대로) · 대표이사 직인
  ⑪  기타 자료 = 안내 + A/S 프로세스(표지 + 제안서 쪽) + SGI 계약보증증권 발급 이력(가림) + KB 영업배상책임보험 증권 + 디엔비 업무협약서 + 전기공사업 등록증 + ISO 인증서

날인: 법인인감 요구 0건 · 사용인감계 없음 · 서식 1 · 2 '(인)' = 대표이사 직인(투명 PNG) · 법인인감은 디지털로 만들지 않는다(규칙 4 · 11.03까지 없음).
빈칸: 서식1 생년월일 · ⑦ 사업장 가입증명서 — 비어 있으면 노란 칸 · 빈칸 쪽으로 만들고 '작업/확인본_빈칸있음/'에만 낸다(제출본 · ZIP 안 만듦). --final은 빈칸 0이어야 함.
출력: 작업/(중간 · 출력용) · 제출본/번호별/00 ~ 11 PDF + 제출본/[주관사 제안서]_주식회사 엣지컴퍼니.zip(본부장 10-30 ZIP 1개) + 제출본/예비_통합본.pdf(보내지 않음)
사용: python docs_cj.py <투명 직인.png> [--final]
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
CASE = f"{SITE} 입주박람회 주관사 선정 입찰"
NOTICE = D.NOTICE

NR = r"C:\본부장\05주관사 입찰공고\20261025_롯데캐슬 나리벡시티\제안자료_주식회사 엣지컴퍼니\제안자료_주식회사 엣지컴퍼니"
EVD = r"C:\본부장\02입찰공고필요양식(대외비)"
ELEC = os.path.join(EVD, "11.기타", "전기공사업 등록증.pdf")
ISO = os.path.join(EVD, "11.기타", "[글로벌시스템인증원]주식회사 엣지컴퍼니ISO인증.pdf")
DNB = r"C:\본부장\협력사_협약서\20261028_디엔비파트너스건축사사무소\업무협약서_엣지컴퍼니_디엔비파트너스건축사사무소_20261028_양측날인_2쪽을정보모자이크_v2.pdf"
PROPOSAL = os.path.join(HERE, "엣지컴퍼니_청주센트럴파크_입주박람회_주관사_제안서_밝은시안.pdf")
WORK = os.path.join(HERE, "작업")
SGI_PNG = os.path.join(HERE, "assets_ins", "os_sgi_bond_masked.png")
KB = r"C:\본부장\05주관사 입찰공고\20261024_창릉신도시 S5\엣지컴퍼니_고양창릉S5_제출서류\12_영업배상책임보험_증서\엣지컴퍼니_고양창릉S5_12_영업배상책임보험_증서.pdf"
REG_MASK = [(203, 163, 556, 177), (30, 176, 50, 187)]   # 등기부 2/2쪽 대표이사 주소(군포 · 엘리프와 같은 10.23 발급본)
KB_MASK = [(365, 790, 445, 801)]                        # KB 증권 아래 영업담당자 휴대번호
TAX_PHONE = (119, 228.5, 196, 239)                      # 지방세 납세증명서 2쪽 대표 휴대번호(그림)
DNB_DATE = "2026년 10월 26일"
SAEOP = os.path.join(WORK, "07_사업장가입증명서.pdf")   # ⑦ 공단 '사업장 가입(적용 · 성립) 증명' — 본부장 발급본을 이 이름으로 두면 넣는다
SUBMIT = os.path.join(HERE, "제출본")
BLANK_DIR = os.path.join(WORK, "확인본_빈칸있음")
NOTICE_DIR = r"C:\본부장\05주관사 입찰공고\20261101_청주 두산위브더제니스 센트럴파크\제안자료_주식회사 엣지컴퍼니"   # 본부장이 여는 공고 폴더 사본
ZIP_NAME = f"{D.FILE_TITLE}.zip"
GARBAGE = 1


def ceo_birth():
    if D.CEO_BIRTH:
        return D.CEO_BIRTH
    for f in ("ceo_private.json", "org_private.json"):   # 둘 다 깃 제외(org_private = 조직도 실명 · 있으면 reorg가 읽음)
        p = os.path.join(HERE, f)
        if os.path.exists(p):
            b = json.load(open(p, encoding="utf-8-sig")).get("ceo_birth")
            if b:
                return b
    return None


BLANKS = []   # 빌드 끝에 알릴 빈칸


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
            ("사전점검 · 하자 책임 구분", "사전점검 · 하자, 책임부터"), ("하자보수 이행 - 서식 1호를 지키는 장치", "서식 1호를 지키는 장치")]
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
            ("평가완료일", f"{D.NICE_DATE} · 연 1회 정기 평가(재무제표 기준) · 유효기간 안 최근 평가본"), ("발췌 범위", "원본 9쪽 ‘04 영업 현황(기업개요)’ 중 ‘연혁’ · 전문 = 제출 ③(같은 보고서)")]
    pa = ('<h2>붙임 A · NICE디앤비 기업신용평가보고서 ‘연혁’ 발췌</h2><table class="f" style="margin-bottom:4mm">'
          + "".join(f"<tr><th>{a}</th><td>{e(b)}</td></tr>" for a, b in info) + "</table>"
          f'<img src="{pathlib.Path(nfn).as_uri()}" style="display:block;width:106mm;margin:0 auto;border:1px solid #bbb">'
          '<p style="font-size:10pt;margin-top:3mm">연혁의 2023/11 ~ 2026/07 주관 6행이 최근 3년 1,000세대 이상 주관 실적입니다. 연혁 일자는 주관 협약(보통 박람회 1 ~ 2년 전) 뒤 확정된 일정 기준이라, 창원 센트럴 아이파크(2026/07)는 평가 당시 이미 일정이 확정된 단지이며 2026.07.03 ~ 05 CECO에서 개최했습니다(붙임 B-4). 위 발췌는 원본과 같습니다.</p>')
    pages = [page("제출 ⑧ · 붙임 A", pa)]
    for i in range(0, len(B_CAPS), 2):
        body = ""
        for j, (pno, k, nm, src, when) in enumerate(B_CAPS[i:i + 2], i + 1):
            uri = _img(s03, pno, k, f"b{j}.png")
            body += (f'<div style="margin-bottom:7mm"><h2 style="font-size:12.5pt">B-{j} · {e(nm)}</h2>'
                     f'<p style="font-size:10pt;color:#444;margin-bottom:2mm">{e(src)} · {e(when)}</p>'
                     f'<img src="{uri}" style="display:block;max-width:100%;max-height:92mm;margin:0 auto;border:1px solid #bbb"></div>')
        pages.append(page("제출 ⑧ · 붙임 B · 공식 행사일정 · 카페 공지", body,
                          "B-1 ~ B-4 = 1,000세대 이상 주관 단지 · B-5 ~ B-9 = 500 ~ 999세대 주관 단지 · 화면 그대로 · 입주민 닉네임만 가림"))
    for j, (pno, nm, dt) in enumerate(C_DOCS, 1):
        uri = _img(s03, pno, 0, f"c{j}.png", top=0.15)   # 고양 때 박힌 '제출서류 12 · 별첨 3-n' 머리글 · 제목 잘라냄
        body = (f'<h2>붙임 C-{j} · 주관사 협약서 사본 - {e(nm)}</h2><p style="font-size:10.5pt;margin-bottom:4mm">협약일 {dt} · 상대방 대표자 성명 · 연락처 · 계좌 가림</p>'
                f'<img src="{uri}" style="display:block;width:100%;border:1px solid #bbb">')
        pages.append(page("제출 ⑧ · 붙임 C · 주관사 협약서(협약일 순)", body, "500 ~ 999세대 주관 단지의 협약서 - 입주박람회 행사 수행 경험 참고"))
    return pages


EV8 = {"레이카운티": "A NICE 연혁", "e편한세상 송도 더퍼스트비치": "B BEXCO 공식 행사일정", "두산위브더제니스 센트럴사하": "A NICE 연혁",
       "양정자이더샵SK VIEW 1·2단지": "A NICE 연혁", "춘천 학곡지구 중해마루힐 포레스트": "A NICE 연혁", "에코델타 대성베르힐": "B 카페 공지 · BEXCO 공식 행사일정",
       "두산위브더제니스 오션시티": "A NICE 연혁", "창원 센트럴 아이파크": "A NICE 연혁 · B CECO 공식 행사일정"}




CSS += r"""
.yb{background:#FFE066;font-weight:800;padding:0 4px}
.fm{font-size:10pt;color:#333;margin-bottom:3mm}
h1.s{letter-spacing:.25em;margin:4mm 0 8mm}
table.s1 th{width:24%}
p.sv{text-indent:.6em;margin-bottom:4mm;line-height:1.85}
.who{margin:10mm 0 0 auto;width:92mm;line-height:2.2;position:relative}
.who .in{position:relative;display:inline-block}
.who .seal{position:absolute;width:21mm;height:21mm;right:-23mm;top:-6mm;opacity:.92}
.blk{border:2.5px dashed #c9a400;background:#fff8d6;border-radius:8px;padding:12mm 10mm;text-align:center;margin-top:30mm}
.blk b{display:block;font-size:17pt;margin-bottom:5mm}
"""


def _seal_img(seal_uri, cls="seal"):
    return f'<img class="{cls}" src="{seal_uri}" alt="">' if seal_uri else ""


# ------------------------------------------------------------ ⑨ 서식1 · ⑩ 서식2 — 별지서식 문구 그대로(띄어쓰기 · '상단' 포함 원문 유지)
S1_TEXT = (" 두산위브더제니스 청주 센트럴파크 입주예정자 협의회에서 시행하는 공동구매 행사로 인해 발생하는 사후 하자 보수를 이행함에 있어 "
           "계약(또는 협약) 일반조건에 따라 하자 보증기간 내에 주관한 행사에 참여한 업체가 납품한 공사 및 물품에 대해 하자가 발생할 시에는 "
           "즉시 실제 발생한 하자 보수 또는 원상 복귀에 대한 상단 금액을 변상할 것을 서약합니다.")
S2_HEAD = ("(은) 두산위브더제니스 청주 센트럴파크 입주예정자 협의회에서 진행하는 주관사 선정 행사 주관, 사후관리 위탁을 제안함에 있어 "
           "아래의 내용을 준수하고 이행할 것을 확약하고 이에 서약서를 제출합니다.")
S2_ITEMS = [
    "입찰 참가신청과 관련하여 작성된 모든 증빙자료는 신의성실의 원칙에 입각하여 작성하였으며, 귀사의 제안서 평가 및 협상 결과 등에 대하여 어떠한 이의도 제기하지 않겠습니다.",
    "협의회의 평가 결과에 대하여 부당하게 이의를 제기하거나 계약자 선정 통보에 불응한 경우 관계법령에 따라 부정 사업자로 제재 등 어떠한 처분도 감수하겠습니다.",
    "주관사로 선정될 경우, 사업 전체를 타인(타사)에게 일괄 도급하지 않으며, 계약 이후라도 일괄 도급한 사실이 적발될 경우, 계약이 해지되어도 민사 소송 등 이의를 일절 제기하지 않겠습니다.",
    "주관사 미 선정 시 [두산위브더제니스 청주 센트럴파크]에 대한 별도의 입주 박람회 주관 및 공동구매 등 행사 개최를 일절 하지 않을 것을 서약합니다.",
]
assert SITE == "두산위브더제니스 청주 센트럴파크"   # 서식 문구에 단지명이 그대로 박혀 있음


def f_s1(seal_uri):
    b = ceo_birth()
    if not b and "⑨ 서식1 생년월일" not in BLANKS:
        BLANKS.append("⑨ 서식1 생년월일")
    rows = [("업 체 명", e(D.COMPANY)), ("직 위", "대표이사"), ("성 명", e(D.CEO)),
            ("생년월일", e(b) if b else '<span class="yb">본부장 기재 - 대표자 생년월일</span>'), ("본사주소", e(D.ADDRESS))]
    y, m, d = D.SIGN_DATE
    body = ('<div class="fm">[별지서식 제 1호]</div><h1 class="s">하자 보수 이행 각서</h1>'
            '<table class="f s1">' + "".join(f"<tr><th>{a}</th><td>{v}</td></tr>" for a, v in rows) + "</table>"
            f'<p class="sv">{e(S1_TEXT)}</p>'
            f'<div class="dt">{y}년 {m}월 {d}일</div>'
            f'<div class="who">주관사 : {e(D.COMPANY)}<br>대표자 : <span class="in">대표이사 {e(D.CEO)} (인){_seal_img(seal_uri)}</span></div>'
            f'<div class="to">{e(SITE)} 입주예정자협의회 귀하</div>')
    return page("제출 ⑨ · 하자보수 이행각서 [서식1]", body)


def f_s2(seal_uri):
    y, m, d = D.SIGN_DATE
    body = ('<div class="fm">[별지서식 제 2호]</div><h1 class="s">이의 제기 금지 서약서</h1>'
            f'<p class="sv"><u>&nbsp;{e(D.COMPANY)}&nbsp;</u>{e(S2_HEAD)}</p>'
            + "".join(f'<p class="sv">{e(x)}</p>' for x in S2_ITEMS)
            + f'<div class="dt">{y}년 {m}월 {d}일</div>'
            f'<div class="who">[서 약 자]<br>상 호 : {e(D.COMPANY)}<br>대 표 : <span class="in">대표이사 {e(D.CEO)} (인){_seal_img(seal_uri)}</span></div>'
            f'<div class="to">{e(SITE)} 입주예정자협의회 귀하</div>')
    return page("제출 ⑩ · 영업행위 금지 서약서 [서식2]", body)   # 챗 검증 10-31: 머리말 한 줄로


# ------------------------------------------------------------ 안내 · 표지
def p03_cover():
    info = [("보고서", "NICE디앤비 CLIP 기업신용평가보고서"), ("평가 대상", f"{D.COMPANY}({D.BIZ_NO})"),
            ("평가완료일", f"{D.NICE_DATE} · 연 1회 정기 평가 · 유효기간 안 최근 평가본"),
            ("재무 기준", "2025년 결산 재무제표 포함(공고 ‘2025년도 포함’)"), ("가림", "개인정보(주민번호 · 주소 · 연락처)")]
    body = ('<div class="cv"><div class="no">제출 ③</div><div class="tt">기업신용등급 평가서</div>'
            '<table class="f">' + "".join(f"<tr><th>{a}</th><td>{e(b)}</td></tr>" for a, b in info) + "</table>"
            '<div class="ds">다음 쪽부터 평가보고서 원본 전문입니다.</div></div>')
    return page("제출 ③ · 기업신용등급 평가서", body)


def p07_guide(parts):
    rows = "".join(f'<tr><td class="n">{i}</td><td>{e(a)}</td><td>{e(b)}</td></tr>' for i, (a, b) in enumerate(parts, 1))
    body = ('<h2>4대 보험 사업장 가입증명서 및 조직도 - 안내</h2>'
            '<p class="b">공고 제출 서류 ⑦ ‘4대 보험 사업장 가입증명서 및 조직도(최근 1개월 이내)’입니다. 개인정보(성명 가운데 글자 · 주민등록번호 칸 전체)는 가렸습니다.</p>'
            '<table class="l"><tr><th>No</th><th>서류</th><th>발급 · 내용</th></tr>' + rows + '</table>'
            '<p style="font-size:10pt;color:#555;margin-top:5mm">가림 없는 원본은 협의회가 요청하시면 열람할 수 있습니다.</p>')
    return page("제출 ⑦ · 4대 보험 사업장 가입증명서 및 조직도", body)


def p07_blank():
    body = ('<div class="blk"><b>⑦ 4대 보험 사업장 가입증명서 - 빈칸</b>'
            '공단 ‘사업장 가입(적용 · 성립) 사실 증명’ 발급본을 받아<br>'
            f'<code>{e(os.path.relpath(SAEOP, HERE))}</code> 로 두고 다시 실행하면 이 쪽이 발급본으로 바뀝니다.<br><br>'
            '발급이 어려우면 본부장 결정으로 이 쪽 없이(명부 + 완납증명 + 조직도) 냅니다.</div>')
    return page("제출 ⑦ · 빈칸(제출 전 교체)", body)


def p08_guide():
    rows = "".join(f'<tr><td class="n">{i}</td><td>{m}</td><td>{e(nm)}</td><td class="r">{n:,}</td><td>{e(ev)}</td></tr>'
                   for i, (m, nm, _a, n, ev) in enumerate([(*r, EV8[r[1]]) for r in D.GP_REC], 1))
    body = ('<h2>입주박람회 행사 수행 경험 이력 및 증빙 - 안내</h2>'
            f'<p class="b">공고 제출 서류 ⑧ · 입찰 자격 ④(대표자 · 핵심 운영인력 실무 수행경험)의 증빙입니다. '
            f'입주 2023.10 이후 1,000세대 이상 주관 단지 {len(D.GP_REC)}곳 · {sum(r[3] for r in D.GP_REC):,}세대이며, 두산위브더제니스 2개 단지(센트럴사하 · 오션시티)를 포함합니다.</p>'
            '<table class="l"><tr><th>No</th><th>입주</th><th>단지</th><th>세대</th><th>증빙(이 서류 안)</th></tr>' + rows + '</table>'
            '<div class="box" style="margin-top:6mm"><b>붙임 구성</b><br>A · NICE디앤비 기업신용평가보고서 ‘연혁’ 발췌(1,000세대 이상 주관 단지 · 시기)<br>'
            'B · 박람회장 공식 행사일정 · 단지 카페 공지 캡처(주최 / 주관 엣지컴퍼니)<br>'
            'C · 주관사 협약서 3건(500 ~ 999세대 단지 · 협약일 순 · 상대방 개인정보 가림)</div>'
            f'<p style="font-size:10pt;color:#555">500세대 이상 주관 단지 전체 목록은 제출 ① 제안서 p.17, 1,000세대 이상 단지별 일정 · 장소는 p.66에 있습니다. 누적 수임 단지(전신 실적 포함)는 ‘수임’으로 적습니다.</p>')
    return page("제출 ⑧ · 입주박람회 행사 수행 경험 이력 및 증빙", body)


def p11_guide(ranges):
    li = "".join(f"<li>{e(t)} - 제안서 p.{a:02d}</li>" for t, a, _b in ranges)
    rows = [("A", "컴플레인 · A/S 관리 프로세스(취소 · 환불 규정 포함)", "제안서 해당 쪽 그대로 · 입찰 자격 ⑥ 사후관리 체계"),
            ("B", "서울보증보험 계약보증보험증권 발급 이력", "발급 2026.09.07 · 주계약 = 광고대행 용역(입주박람회 이행보증 아님) · 금액 · 상대방 정보 가림"),
            ("C", "KB 영업배상책임보험 증권", "시설소유관리자 · 2026.10.14 ~ 2027.10.14 · 행사주최자배상책임보험은 박람회 확정 시 행사장 기준으로 별도 가입"),
            ("D", "건축 기술 자문 업무협약서", f"{D.ADVISOR} · 2026.10.26 · 양측 날인 · 2쪽 을 정보 가림 · 하자 판정 아님"),
            ("E", "전기공사업 등록증", f"{D.ELEC_LICENSE} · 조명 · 경관조명 직접 시공"),
            ("F", "ISO 인증서", "ISO 9001 · 14001 · 45001(박람회 기획 · 대행, 전기 · 조명공사) · 인증서 주소는 2026.07 본점 이전 전 주소")]
    body = ('<h2>기타 자료(자유 제출) - 안내</h2>'
            '<p class="b">공고 제출 서류 ⑪ ‘기타 입예협이 필요하다고 인정하는 자료’입니다. 하자 · A/S 사후관리 체계와 이행 능력을 확인하실 수 있는 자료를 모았습니다.</p>'
            '<table class="l"><tr><th>No</th><th>자료</th><th>내용</th></tr>'
            + "".join(f'<tr><td class="n">{a}</td><td>{e(b)}</td><td>{e(c)}</td></tr>' for a, b, c in rows) + '</table>'
            '<div class="box" style="margin-top:6mm"><b>A · 컴플레인 · A/S 관리 프로세스 구성</b><ol class="c" style="margin-top:3mm">' + li + '</ol>'
            '한 창구 접수 → 24시간 안 1차 회신(주말 · 공휴일 = 다음 영업일 12시) → 48시간 안 방문 일정 확정 → 업체 무응답 시 주관사 개입 · 선보상 → 도산 · 연락 두절 시 이관 → 완료 확인 · 정기 보고</div>'
            '<p style="font-size:10pt;color:#555">입주박람회 계약이행 · 하자보증보험은 선정 · 협약 후 협의회를 피보험자로 발급합니다. 가림 없는 원본은 협의회가 요청하시면 열람할 수 있습니다.</p>')
    sgi = ('<h2>B · 서울보증보험 계약보증보험증권 발급 이력</h2>'
           f'<div style="text-align:center"><img src="{pathlib.Path(SGI_PNG).as_uri()}" style="height:205mm;border:.6pt solid #bbb"></div>')
    return [page("제출 ⑪ · 기타 자료 · 안내", body),
            page("제출 ⑪ · 기타 자료 · B", sgi, "광고대행 용역 계약보증(입주박람회 이행보증 아님) · 금액 · 상대방 정보 · 증권번호 일부 가림")]


def p00(spans, blanks):
    rows = "".join(f'<tr><td class="n">{n}</td><td>{e(t)}</td><td>{e(fn)}</td><td class="r">{pc}쪽</td><td>{e(s)}</td></tr>' for n, t, fn, pc, s in spans)
    body = ('<h2>제출 서류 목록</h2>'
            f'<p style="margin-bottom:4mm">건명 : {e(NOTICE)}<br>제출 : {e(D.SUBMIT_TO)} · 제목 {e(D.MAIL_TITLE)} · 공고 3. 제출 서류 순서(① ~ ⑪)</p>'
            '<table class="l"><tr><th>No</th><th>서류</th><th>파일</th><th>쪽</th><th>발급일 · 내용</th></tr>' + rows + "</table>"
            '<p style="font-size:10pt;color:#555;margin-top:4mm">모든 파일은 PDF이며, 파일 이름 앞 번호 = 공고 제출 서류 번호입니다. 서식 1 · 2호 = 별지서식 문구 그대로 · 대표이사 직인.</p>'
            + (f'<p style="color:#b00;font-weight:800;margin-top:4mm">※ 확인본 - 빈칸 {len(blanks)}곳({e(" · ".join(blanks))})을 채우기 전에는 제출하지 않습니다.</p>' if blanks else ""))
    return page("제출 서류 목록", body)


# ------------------------------------------------------------ 조립
FILES = [  # (번호, 공고 서류 이름, 파일 이름)
    ("①", "입주박람회 제안서", "01_입주박람회_제안서"),
    ("②", "사업자등록증 사본", "02_사업자등록증"),
    ("③", "기업신용등급 평가서", "03_기업신용등급_평가서"),
    ("④", "법인 등기부등본", "04_법인등기부등본"),
    ("⑤", "인감증명서", "05_인감증명서"),
    ("⑥", "국세 및 지방세 완납 증명서", "06_국세_지방세_완납증명서"),
    ("⑦", "4대 보험 사업장 가입증명서 및 조직도", "07_4대보험_사업장가입증명서_조직도"),
    ("⑧", "입주박람회 행사 수행 경험 이력 및 증빙자료", "08_입주박람회_행사수행경험_증빙"),
    ("⑨", "하자보수 이행각서 [서식1]", "09_하자보수_이행각서_서식1"),
    ("⑩", "개별 입주박람회 및 단지 영업행위 금지 서약서 [서식2]", "10_개별박람회_영업행위금지_서약서_서식2"),
    ("⑪", "기타 자료(자유 제출)", "11_기타자료"),
]


def org_page(prop):
    texts = [re.sub(r"[\s\u00a0\u2060]+", " ", p.get_text()) for p in prop]
    hit = [i for i, t in enumerate(texts) if "조직 구성" in t[:300] and "담당 체계" in t[:300]]
    assert len(hit) == 1, ("제안서에서 조직도 쪽을 찾지 못함", hit)
    return hit[0]


def main():
    seal = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None
    assert seal and os.path.exists(seal), "투명 직인 PNG 경로를 주세요(서식 1 · 2 대표이사 직인)"
    seal_uri = pathlib.Path(seal).resolve().as_uri()
    final = "--final" in sys.argv
    assert os.path.exists(PROPOSAL), "제안서 밝은 시안 PDF가 없음 — build_cj.py → light_build.py 먼저"
    prop = fitz.open(PROPOSAL)
    BLANKS.clear()

    def take(src, pages):
        d = fitz.open()
        for p in pages:
            d.insert_pdf(src, from_page=p - 1, to_page=p - 1)
        return d

    docs, desc = {}, {}
    docs["①"] = prop
    desc["①"] = f"{prop.page_count}쪽 · PT 자료로 그대로 사용"
    docs["②"] = take(nr("05_사업자등록증.pdf"), [1])
    desc["②"] = f"{D.ISSUE['biz']} 발급"
    d3 = fitz.open(render("03_표지", doc("기업신용등급 평가서", [p03_cover()])))
    d3.insert_pdf(nr("09_기업신용평가서.pdf"), from_page=1)   # 09 = 나리벡 표지 1쪽 + NICE 원본 24쪽(가림) → 원본만
    docs["③"] = d3
    desc["③"] = f"NICE디앤비 {D.NICE_DATE} · 2025 결산 포함 · 가림"
    d4 = take(nr("06_법인등기부등본_법인인감증명서.pdf"), [1, 2])
    for r_ in REG_MASK:
        d4[1].add_redact_annot(fitz.Rect(*r_), fill=(0.6, 0.6, 0.6))
    d4[1].apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS)
    docs["④"] = d4
    desc["④"] = f"{D.ISSUE['reg']} 발급 · 자본금 2억원 · 대표 주소 가림"
    docs["⑤"] = take(nr("06_법인등기부등본_법인인감증명서.pdf"), [3])
    desc["⑤"] = f"{D.INGAM_DATE} 발급 · 가림"
    d6 = take(nr("07_국세_지방세_완납증명서.pdf"), [1, 2])
    d6[1].add_redact_annot(fitz.Rect(*TAX_PHONE), fill=(0.6, 0.6, 0.6))
    d6[1].apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS)
    docs["⑥"] = d6
    desc["⑥"] = f"{D.ISSUE['tax']} 발급 · 유효기한 안 · 휴대번호 가림"

    # ⑦ = 안내 + 사업장 가입증명서(발급본 또는 빈칸) + 명부 2쪽 + 완납증명 2쪽 + 조직도(제안서 쪽)
    if not D.HISTORY_OK:
        BLANKS.append("① 자격 ⑨ · 유의 ⑤ 이력 없음 확인(data.HISTORY_OK)")
    have_saeop = os.path.exists(SAEOP)
    if not have_saeop:
        BLANKS.append("⑦ 사업장 가입증명서")
    # 법정 2차(10-31): 1행 = 실제 서류 이름 · 4대 보험 4종 가입은 명부에서 확인된다는 것을 2행에 보이게
    g7 = [("고용 · 산재보험 가입증명원(제출용)" if have_saeop else "4대 보험 사업장 가입증명서", "근로복지공단 · 2026.10.31 발급 · 고용 · 산재 성립 2022.03.04" if have_saeop else "발급본 넣을 자리(빈칸)"),
          ("사업장가입자 명부 = 4대 보험 가입 확인", f"{D.ROSTER_DATE} 발급 · 국민연금 · 건강 · 산재 · 고용 4종 · 13명"),
          ("4대 사회보험료 완납증명서 · 고용 · 산재보험료 완납증명서", "2026.10.23 · 10.24 발급"),
          ("조직도", "대표이사 · 주관사업 총괄 본부장 · 4개 팀(제안서 조직 구성 쪽)")]
    d7 = fitz.open(render("07_안내", doc("⑦ 안내", [p07_guide(g7)])))
    d7.insert_pdf(fitz.open(SAEOP) if have_saeop else fitz.open(render("07_빈칸", doc("⑦ 빈칸", [p07_blank()]))))
    d7.insert_pdf(nr("08_4대보험_가입자명부_완납증명서.pdf"))
    # 챗 검증 10-31: 명부 주민번호 칸 전체(생년월일 · 뒷자리 첫 숫자) 가림 — 13명 칸만(성명 · 취득일은 그대로)
    _ms = d7[2]   # 0 안내 · 1 가입증명원(또는 빈칸) · 2 명부 1쪽
    _ms.add_redact_annot(fitz.Rect(87, 311, 193, 571), fill=(0.72, 0.72, 0.72))
    _ms.apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS)
    _o = org_page(prop)
    d7.insert_pdf(prop, from_page=_o, to_page=_o)
    docs["⑦"] = d7
    desc["⑦"] = ("가입증명원 2026.10.31 · " if have_saeop else "") + f"명부 {D.ROSTER_DATE} · 완납증명 · 조직도" + ("" if have_saeop else " · 가입증명서 빈칸")

    d8 = fitz.open(render("08_안내", doc("⑧ 안내", [p08_guide()])))
    d8.insert_pdf(fitz.open(render("08_붙임", doc("⑧ 붙임", ev8_pages(seal_uri)))))
    docs["⑧"] = d8
    desc["⑧"] = "안내 + A NICE 연혁 + B 공식 행사일정 · 카페 공지 + C 주관사 협약서 3건"
    docs["⑨"] = fitz.open(render("09_서식1", doc("하자 보수 이행 각서", [f_s1(seal_uri)])))
    desc["⑨"] = "별지서식 제1호 그대로 · 대표이사 직인"
    docs["⑩"] = fitz.open(render("10_서식2", doc("이의 제기 금지 서약서", [f_s2(seal_uri)])))
    desc["⑩"] = "별지서식 제2호(이의 제기 금지 서약서) 그대로 · 대표이사 직인"
    render("09_10_서식_날인출력용", doc("서식 1 · 2 날인 출력용", [f_s1(None), f_s2(None)]))   # 실물 직인으로 찍을 때(빈 칸)

    ranges = proposal_ranges(prop)
    for p in (SGI_PNG, KB, DNB, ELEC, ISO):
        assert os.path.exists(p), ("⑪ 원본 없음", p)
    d11 = fitz.open(render("11_안내", doc("⑪ 안내", p11_guide(ranges)[:1])))
    for _l, a, _b in ranges:
        d11.insert_pdf(prop, from_page=a - 1, to_page=a - 1)
    d11.insert_pdf(fitz.open(render("11_SGI", doc("⑪ B", p11_guide(ranges)[1:]))))
    kb = fitz.open(KB)
    for r_ in KB_MASK:
        kb[0].add_redact_annot(fitz.Rect(*r_), fill=(0.6, 0.6, 0.6))
    kb[0].apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS)
    d11.insert_pdf(kb)
    dnb = fitz.open(DNB)
    _w = dnb[0].rect.width
    dnb[0].insert_textbox(fitz.Rect(_w - 300, 14, _w - 30, 30), f"업무협약 체결일 : {DNB_DATE}", fontsize=9.5,
                          fontname="malgun", fontfile=r"C:\Windows\Fonts\malgun.ttf", color=(0.25, 0.25, 0.25), align=fitz.TEXT_ALIGN_RIGHT)
    dnb.subset_fonts()
    d11.insert_pdf(dnb)
    d11.insert_pdf(fitz.open(ELEC))
    # 본부장 10-31 'ISO도 2개씩 · 너무 페이지 차지': 국문 · 영문 한 쌍을 가로 A4 한 쪽에 나란히(원본 그림 축소만 · 6쪽 → 3쪽)
    iso = fitz.open(ISO)
    for k in range(0, iso.page_count, 2):
        pg = d11.new_page(width=842, height=595)
        for j, x0 in enumerate((20, 426)):
            if k + j < iso.page_count:
                pg.show_pdf_page(fitz.Rect(x0, 18, x0 + 396, 577), iso, k + j)
    docs["⑪"] = d11
    desc["⑪"] = "A/S 프로세스 · SGI 발급 이력 · KB 증권 · 자문 협약 · 전기공사업 · ISO"

    blanks = list(BLANKS)
    if final:
        assert not blanks, f"--final: 빈칸이 남음 {blanks}"
    spans = [(n, t, fn + ".pdf", docs[n].page_count, desc[n]) for n, t, fn in FILES]
    d0 = fitz.open(render("00_제출서류_목록", doc("제출 서류 목록", [p00(spans, blanks)])))
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
    zp = os.path.join(os.path.dirname(out_dir) if not blanks else out_dir, ZIP_NAME)
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
    # 본부장이 여는 공고 폴더에 사본(빈칸 있으면 '확인본' 폴더명)
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
