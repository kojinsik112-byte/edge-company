# -*- coding: utf-8 -*-
"""엣지컴퍼니 통합제안서(1-152p, 3분할 PDF) 일괄 수정 — 동탄 파라곤3차 입찰용.

사용:
  python fix_all.py <증빙폴더> <원본_1-36.pdf> <원본_37-121.pdf> <원본_122-152.pdf> <출력폴더>
증빙폴더에 필요한 파일(파일명 고정):
  사업자등록증.pdf 법인등기부등본.pdf 국세_납세증명서.pdf 지방세_납세증명서.pdf
  4대보험_가입자명부.pdf ISO_인증서.pdf NICE_기업신용평가.pdf
※ 증빙 원본·출력 PDF에는 개인정보가 있으므로 깃에 올리지 않는다(스크립트만 커밋).

원칙: 공식 증빙은 원본 그대로(크롭·흰 바탕만), 문구 수정은 원본 텍스트층 교체 또는
이미지 위 덧패치(배경색 자동 추출) + Pretendard 재기입.
"""
import io
import os
import sys
import statistics

import pymupdf as fitz
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
F_BOLD = fitz.Font(fontfile=os.path.join(HERE, "fonts", "Pretendard-Bold.ttf"))
F_REG = fitz.Font(fontfile=os.path.join(HERE, "fonts", "Pretendard-Regular.ttf"))
F_SERIF = fitz.Font(fontfile=os.path.join(HERE, "fonts", "FreeSerifBold.ttf"))

NAVY = 0x0B1E3F
WHITE = 0xFFFFFF
LIGHT = 0xEDE8DF
GOLD = 0xC3A37D
DARK = 0x2B2F38
GRAY = 0x6B7280
LOG = []
OFF = [0]  # 분할 PDF의 시작 페이지 오프셋(로그용 전체 페이지 번호)


def pn(page):
    return page.number + 1 + OFF[0]


def rgb(c):
    return ((c >> 16) & 255) / 255, ((c >> 8) & 255) / 255, (c & 255) / 255


# ------------------------------------------------------------------ 기본 도구
def sample_bg(page, rect, ring=1.5):
    """rect 바깥 테두리 띠의 중앙값 색 → 패치 배경색."""
    z = 3
    clip = fitz.Rect(rect.x0 - ring, rect.y0 - ring, rect.x1 + ring, rect.y1 + ring) & page.rect
    pix = page.get_pixmap(matrix=fitz.Matrix(z, z), clip=clip, alpha=False)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    w, h, r = im.width, im.height, max(1, int(ring * z))
    px = [im.getpixel((x, y)) for x in range(w) for y in list(range(r)) + list(range(h - r, h))]
    px += [im.getpixel((x, y)) for y in range(h) for x in list(range(r)) + list(range(w - r, w))]
    return tuple(statistics.median(c[i] for c in px) / 255 for i in range(3))


def patch(page, rect, fill=None, opacity=1.0, radius=None):
    rect = fitz.Rect(rect)
    fill = fill if fill is not None else sample_bg(page, rect)
    if isinstance(fill, int):
        fill = rgb(fill)
    page.draw_rect(rect, color=None, fill=fill, fill_opacity=opacity, overlay=True,
                   radius=radius)


def write(page, x, y, text, size, color, font=None, align="left", max_w=None):
    """y = 글자 세로 중앙. align left/center/right 기준점 x. max_w 넘으면 자동 축소."""
    font = font or F_BOLD
    w = font.text_length(text, fontsize=size)
    if max_w and w > max_w:
        size = size * max_w / w
        w = font.text_length(text, fontsize=size)
    if align == "center":
        x -= w / 2
    elif align == "right":
        x -= w
    base = y + size * 0.36
    tw = fitz.TextWriter(page.rect)
    tw.append((x, base), text, font=font, fontsize=size)
    tw.write_text(page, color=rgb(color))
    return w


def write_runs(page, x, y, runs, align="left"):
    """runs = [(text, size, color, font)] 한 줄 연속 출력."""
    total = sum((f or F_BOLD).text_length(t, fontsize=s) for t, s, c, f in runs)
    if align == "center":
        x -= total / 2
    for t, s, c, f in runs:
        x += write(page, x, y, t, s, c, f)


def replace_text(page, old, new, y0=None, bold=None, size=None):
    """텍스트층 span 교체(같은 위치·크기·색). 화면에 실제로 보이는 글자인지도 검사."""
    hits = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                if s["text"] == old and (y0 is None or abs(s["bbox"][1] - y0) < 1.5):
                    hits.append(s)
    assert len(hits) == 1, f"p{pn(page)}: '{old}' 매칭 {len(hits)}건"
    s = hits[0]
    r = fitz.Rect(s["bbox"])
    h = r.height
    before = page.get_pixmap(clip=r, dpi=72).samples
    page.add_redact_annot(fitz.Rect(r.x0, r.y0 + h * 0.18, r.x1, r.y1 - h * 0.18))
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE,
                          text=fitz.PDF_REDACT_TEXT_REMOVE)
    after = page.get_pixmap(clip=r, dpi=72).samples
    visible = before != after
    is_bold = bold if bold is not None else ("Bold" in s["font"])
    if visible:
        x, yb = s["origin"]
        tw = fitz.TextWriter(page.rect)
        tw.append((x, yb), new, font=F_BOLD if is_bold else F_REG, fontsize=size or s["size"])
        tw.write_text(page, color=rgb(s["color"]))
    LOG.append(f"p{pn(page)}: '{old}' → '{new}'" + ("" if visible else "  [숨은 텍스트층: 화면 영향 없음]"))
    return visible


_CACHE = {}


def doc_image(src_doc, pno, trim=True, dpi=150, crop=None):
    """증빙 PDF 한 쪽 → (JPEG bytes, 가로/세로비). 여백 자동 트림, crop=(top,bottom) 비율 자르기."""
    pix = src_doc[pno].get_pixmap(dpi=dpi, alpha=False)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    if trim:
        g = im.convert("L").point(lambda v: 255 if v < 235 else 0)
        bb = g.getbbox()
        if bb:
            m = int(dpi * 0.08)
            im = im.crop((max(0, bb[0] - m), max(0, bb[1] - m), min(im.width, bb[2] + m), min(im.height, bb[3] + m)))
    if crop:
        t, b = crop
        im = im.crop((0, int(im.height * t), im.width, int(im.height * (1 - b))))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=82, optimize=True)
    return buf.getvalue(), im.width / im.height


def place_doc(page, inner, src_doc, pno, pad=3, crop=None, label=""):
    """액자 안쪽(inner)을 흰 바탕으로 덮고 증빙 원본을 비율 유지로 꽉 차게 배치."""
    inner = fitz.Rect(inner)
    key = (id(src_doc), pno, crop)
    if key not in _CACHE:
        _CACHE[key] = doc_image(src_doc, pno, crop=crop)
    data, ar = _CACHE[key]
    page.draw_rect(inner, color=None, fill=(1, 1, 1), overlay=True)
    box = inner + (pad, pad, -pad, -pad)
    if box.width / box.height > ar:
        w = box.height * ar
        tgt = fitz.Rect(box.x0 + (box.width - w) / 2, box.y0, box.x0 + (box.width + w) / 2, box.y1)
    else:
        h = box.width / ar
        tgt = fitz.Rect(box.x0, box.y0 + (box.height - h) / 2, box.x1, box.y0 + (box.height + h) / 2)
    page.insert_image(tgt, stream=data, overlay=True)
    LOG.append(f"p{pn(page)}: 증빙 교체 → {label}")



def ink(page, rect):
    """rect 안 글자색(배경과 먼 픽셀의 중앙값)."""
    rect = fitz.Rect(rect)
    bg = [v * 255 for v in sample_bg(page, rect)]
    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3), clip=rect, alpha=False)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    px = [c for c in im.getdata() if sum(abs(c[i] - bg[i]) for i in range(3)) > 110]
    if not px:
        return 0x333333
    m = [int(statistics.median(c[i] for c in px)) for i in range(3)]
    return (m[0] << 16) | (m[1] << 8) | m[2]


def retext(page, rect, lines, size, color=None, x=None, align="left", gap=None, font=None, note=None):
    """이미지에 박힌 문구 교체: 배경색 덧패치 + 같은 색 재기입."""
    rect = fitz.Rect(rect)
    color = color if color is not None else ink(page, rect)
    patch(page, rect)
    if isinstance(lines, str):
        lines = [lines]
    gap = gap or size * 1.45
    cy = (rect.y0 + rect.y1) / 2 - gap * (len(lines) - 1) / 2
    x = x if x is not None else (rect.x0 + 1 if align == "left" else (rect.x0 + rect.x1) / 2)
    for i, t in enumerate(lines):
        write(page, x, cy + gap * i, t, size, color, font, align=align, max_w=rect.x1 - x if align == "left" else rect.width)
    LOG.append(f"p{pn(page)}: 문구 → {' / '.join(lines)}" + (f"  ({note})" if note else ""))

# 카드 라벨 공통 패턴 ---------------------------------------------------
def panel_label(page, rect, lines, size, color=WHITE, align="left", x=None, gap=None, fill=None):
    """어두운 패널 위 2줄 라벨 교체."""
    rect = fitz.Rect(rect)
    patch(page, rect, fill=fill)
    gap = gap or size * 1.35
    n = len(lines)
    cy = (rect.y0 + rect.y1) / 2 - gap * (n - 1) / 2
    x = x if x is not None else (rect.x0 + 2 if align == "left" else (rect.x0 + rect.x1) / 2)
    for i, t in enumerate(lines):
        write(page, x, cy + gap * i, t, size, color, align=align, max_w=rect.width - 3)
    LOG.append(f"p{pn(page)}: 라벨 → {' '.join(lines)}")


def strip_label(page, rect, name, sub=None, size=9.5):
    """사진 위 흰 띠 라벨(이미지 속 오기 단지명 교체)."""
    rect = fitz.Rect(rect)
    page.draw_rect(rect, color=None, fill=(1, 1, 1), overlay=True, radius=0.15)
    if sub:
        write(page, rect.x0 + 4, rect.y0 + rect.height * 0.33, name, size, NAVY, max_w=rect.width - 8)
        write(page, rect.x0 + 4, rect.y0 + rect.height * 0.74, sub, size * 0.72, GRAY, F_REG, max_w=rect.width - 8)
    else:
        write(page, rect.x0 + 4, (rect.y0 + rect.y1) / 2, name, size, NAVY, max_w=rect.width - 8)
    LOG.append(f"p{pn(page)}: 단지명 → {name}" + (f" / {sub}" if sub else ""))


# ------------------------------------------------------------------ 수정 내용
def fix_part1(d, ev):
    P = lambda n: d[n - 1]

    # 8p 회사개요: 사원수·소재지 + AI 생성 가짜 서류 → 실제 사업자등록증·등기부등본
    p = P(8)
    panel_label(p, (542, 131, 814, 150), ["임직원 10명 (4대보험 가입자 명부 기준)"], 10.5, LIGHT, x=546)
    panel_label(p, (542, 189, 814, 227), ["울산광역시 울주군 청량읍 온산로 615-1 (본점)",
                                          "부산광역시 해운대구 아르피나 B1 (부산사무소)"], 10.5, LIGHT, x=546, gap=18.5)
    place_doc(p, (447, 254, 604, 492), ev["사업자등록증"], 0, label="사업자등록증 원본")
    place_doc(p, (632, 254, 804, 493), ev["법인등기부등본"], 0, label="법인등기부등본 원본")

    # 9·10p 4대보험·신용평가·납세 → 2026.10.02 발급 원본 / NICE 2026.06.19
    p = P(9)
    place_doc(p, (191, 199, 366, 520), ev["4대보험"], 0, label="4대보험 사업장 가입자 명부(2026.10.02)")
    place_doc(p, (392, 199, 608, 523), ev["NICE"], 2, label="NICE 기업신용평가 요약(BB-, 2026.06.19)")
    place_doc(p, (637, 198, 836, 520), ev["국세"], 0, label="국세 납세증명서(2026.10.02)")
    p = P(10)
    place_doc(p, (42, 183, 268, 507), ev["4대보험"], 0, label="4대보험 사업장 가입자 명부(2026.10.02)")
    place_doc(p, (294, 154, 550, 513), ev["NICE"], 2, label="NICE 기업신용평가 요약(BB-, 2026.06.19)")
    place_doc(p, (586, 182, 804, 509), ev["지방세"], 0, label="지방세 납세증명서(2026.10.02)")

    # 11p 재무: 자본금 2억·신용 BB-·현금흐름 A·부채비율 17.1%
    fix_p11(P(11))

    # 12p 과장표현·용어
    p = P(12)
    replace_text(p, "입예협 여러분과 함께할 준비가 되어있습니다.", "임예협 여러분과 함께할 준비가 되어있습니다.")
    replace_text(p, "최초 건설업 ", "자체 건설업 ")
    retext(p, (219, 207, 475, 266), "자체 건설업", 62, x=224, note="'최초' 입증불가 표현 삭제")

    # 13p ISO: AI 재현본(만료일 2025.05.03) → 글로벌시스템인증원 원본(한글판, 2025.08.12~2028.08.11)
    p = P(13)
    place_doc(p, (210, 236, 397, 503), ev["ISO"], 4, label="ISO 45001 인증서(한글)")
    place_doc(p, (427, 240, 604, 501), ev["ISO"], 2, label="ISO 14001 인증서(한글)")
    place_doc(p, (634, 241, 813, 503), ev["ISO"], 0, label="ISO 9001 인증서(한글)")

    # 08.수임실적(22~27번째 장): 본부장님 지시로 원본 유지. 정정안은 아래 fix_suim_later()에 보관(나중에 확인 후 적용)

    # 32p 행사리스트: 오기 단지명 전체 재기입
    p = P(32)
    lst = [["온양발리 한양립스 400세대", "남천헤리치자이 913세대", "힐스테이트 포항 1717세대", "사상중흥S클래스 1572세대", "레이카운티 4470세대"],
           ["사송 LH 신혼희망타운 420세대", "사송 더샵 3차 533세대", "사송 제일풍경채 430세대", "부산 드파인 센텀 750세대", "사송 우미린 780세대"],
           ["두산위브 오션시티 2205세대", "부산역 푸르지오 더원 450세대", "중산 한양립스 382세대", "대연 힐스테이트 480세대", None]]
    lcol = [(226, 372), (436, 582), (652, 792)]
    lrow = [398, 418, 438, 457, 476]
    for c, items in enumerate(lst):
        for r, t in enumerate(items):
            if t is None:
                continue
            x0, x1 = lcol[c]
            patch(p, (x0, lrow[r] - 7, x1, lrow[r] + 7))
            write(p, x0 + 2 + (8 if c == 1 else 0), lrow[r], t, 9.5, 0x333333, F_REG, max_w=x1 - x0 - 12)
    LOG.append("p32: 행사리스트 14개 단지명 재기입(래미안동래→레이카운티, 서송→사송, 우체시티 2813→오션시티 2205 등)")



def fix_suim_later(d):
    """[보류] 08.수임실적 단지명·세대수 정정안 — 본부장님 확인 전까지 호출하지 않음."""
    P = lambda n: d[n - 1]
    # 22p 대단지: 이미지 속 오기 단지명
    p = P(22)
    panel_label(p, (430, 267, 491, 300), ["힐스테이트", "포항"], 10, LIGHT, align="center", x=463.5, gap=15.5)
    panel_label(p, (748, 267, 808, 300), ["사송", "데시앙 1차"], 10, LIGHT, align="center", x=778, gap=15.5)
    patch(p, (392, 557, 642, 578))
    write(p, 517, 567.5, "부산 사상구 랜드마크 공식 주관사 선정", 11, DARK, F_REG, align="center")
    LOG.append("p22: 캡션 '공신'→'공식'")

    # 23p 2018-2021: 대표자 前 사업체 실적 명시 + 오기 단지명 12건
    p = P(23)
    names = [["양산 이지더원 랜드파크", "덕계 두산위브 1차", "영도 센트럴 에일린의뜰"],
             ["남양역 반도유보라", "양산 이지더원 리버포레", "일광자이 푸르지오"],
             ["양산 E편한세상 2차", "울산 동구 KCC 스위첸", "연산 이편한세상 더퍼스트"],
             ["빌리브 울산", "스마트리치 연산", "광안 에일린의뜰"]]
    cols = [(207, 342), (432, 549), (637, 768)]
    rows = [84.5, 208, 328, 449.5]
    for r, cy in enumerate(rows):
        for c, (x0, x1) in enumerate(cols):
            strip_label(p, (x0, cy - 8, x1, cy + 8), names[r][c])
    p.draw_rect(fitz.Rect(352, 27, 568, 47), color=rgb(GOLD), fill=rgb(NAVY), width=0.8, radius=0.5, overlay=True)
    write(p, 460, 37, "대표자 前 사업체 운영 실적 (법인 설립 전)", 9, LIGHT, align="center")
    patch(p, (262, 551, 742, 592))
    write_runs(p, 502, 572, [("2018~2021년 대표자 前 사업체로 ", 12, DARK, F_REG), ("12개 단지", 15, GOLD, F_BOLD),
                             (" 입주박람회 주관", 12, DARK, F_REG)], align="center")
    LOG.append("p23: '대표자 前 사업체 실적' 표기, 캡션 교체(세대수 합계 불일치 11,352 → 표기 삭제)")

    # 24p 2022: 제목 추가·오기 단지명·잘못 복사된 캡션
    p = P(24)
    write(p, 190, 36, "2022", 30, NAVY, F_SERIF)
    lab = {(0, 0): ["주례롯데캐슬", "골드스마트"], (0, 1): ["사하", "코오롱 하늘채"], (0, 2): ["기장", "희망타운"],
           (1, 0): ["문수로", "드림파크"], (1, 1): ["오토밸리", "한양립스포레스트"], (1, 2): ["대현시티", "프라디움"],
           (2, 1): ["이안", "오션마크W"], (2, 2): ["아르떼", "에코하임"]}
    pcol = [(279, 337, 283), (503, 562, 511), (743, 799, 749)]
    prow = [(100, 129), (246, 276), (393, 423)]
    for (r, c), ln in lab.items():
        x0, x1, lx = pcol[c]
        y0, y1 = prow[r]
        panel_label(p, (x0, y0, x1, y1), ln, 8.5, LIGHT, x=lx, gap=12.5)
    patch(p, (262, 510, 746, 569))
    write_runs(p, 504, 552.5, [("2022년 ", 12, DARK, F_REG), ("9개 단지", 15, GOLD, F_BOLD),
                               (", 총 4,206세대의 성공적인 사업 수행", 12, DARK, F_REG)], align="center")
    LOG.append("p24: 제목 '2022' 추가, 캡션 '2018~2021 11,352세대'(복사 오류) → '2022년 9개 단지 4,206세대'")

    # 25p 2023-2024
    p = P(25)
    panel_label(p, (607, 299, 702, 317), ["사송 더샵 3차"], 9.5, LIGHT, x=611)
    patch(p, (276, 566, 744, 598))
    write_runs(p, 497, 582, [("2023~2024년 ", 12, DARK, F_REG), ("12개 단지", 15, GOLD, F_BOLD),
                             (", 총 11,059세대의 성공적인 사업 수행", 12, DARK, F_REG)], align="center")
    LOG.append("p25: 캡션 세대수 10,189 → 11,059(카드 합계)")

    # 26p 2025: 오기 단지명 + 05/07 세대수 뒤바뀜(이름을 숫자에 맞춤)
    p = P(26)
    lab = {(0, 1): ["두산위브", "오션시티"], (0, 3): ["춘천", "중해마루"], (1, 0): ["에코델타", "이편한세상"],
           (1, 2): ["에코델타", "강서자이"], (1, 3): ["서면", "서한이다음"], (2, 0): ["울산", "유보라 신천매곡"],
           (2, 3): ["기장", "유림노르웨이숲"]}
    pcol = [(59, 106, 63), (261, 308, 265), (454, 506, 458), (640, 687, 644)]
    prow = [(121, 150), (259, 288), (398, 428)]
    for (r, c), ln in lab.items():
        x0, x1, lx = pcol[c]
        y0, y1 = prow[r]
        panel_label(p, (x0, y0, x1, y1), ln, 8, LIGHT, x=lx, gap=12)
    patch(p, (266, 537, 730, 572))
    write_runs(p, 500, 554.5, [("2025년 기준 ", 12, DARK, F_REG), ("12개 단지", 15, GOLD, F_BOLD),
                               (", 총 10,955세대의 성공적인 사업 수행", 12, DARK, F_REG)], align="center")
    LOG.append("p26: 캡션 세대수 10,189 → 10,955(카드 합계)")

    # 27p(우측 상단 표기 25): 본부장님 지시로 원본 유지 — 수정하지 않음


def fix_p11(page):
    W_, G_, SUB, LG, DESC = 0xffffff, 0xe3c48c, 0xa8b8ca, 0xc2ab85, 0x9dadbe
    edits = [
        ([("자본금 ", 55.0), ("5억", 55.0), (" · ", 55.0), ("자가 사옥", 55.0), (" 보유", 55.0)],
         [("자본금 ", 28, W_, 1), ("2억", 28, G_, 1), (" · ", 28, W_, 1), ("본사 사옥", 28, G_, 1), (" 운영", 28, W_, 1)]),
        ([("임대 사무실이 아닌 ", 95.8), ("자사 소유 사옥", 95.8), (", 그리고 공인 평가기관의 등급으로 증명합니다.", 95.8)],
         [("울산 본사·쇼룸을 ", 10.5, SUB, 0), ("직접 운영", 10.5, G_, 1), ("하고, 재무 건전성은 공인 평가기관 보고서로 증명합니다.", 10.5, SUB, 0)]),
        ([("엣지컴퍼니 자가 사옥", 489.2)], [("엣지컴퍼니 본사 사옥", 11.5, 0xf0e2c4, 1)]),
        ([("5", 190.4)], [("2", 27, 0xedd6a4, 1)]),
        ([("자가", 197.1)], [("본사", 27, 0xedd6a4, 1)]),
        ([("자가 사옥 보유", 234.2)], [("본사 · 쇼룸 운영", 11.5, W_, 1)]),
        ([("C R E D I T", 382.0)], [("F I N A N C E", 8, 0xc9a96a, 1)]),
        ([("B+", 392.9), (" ", 409.2), ("/ 현금흐름 A", 409.2)], [("A", 27, 0xedd6a4, 1), ("  현금흐름 등급", 12, LG, 1)]),
        ([("기업 신용등급", 430.0)], [("부채비율 17.1% · 신용 BB-", 11.5, W_, 1)]),
        ([("공인 평가기관 기업신용평가 등급.", 449.2)], [("NICE 기업신용평가 보고서(2026.06.19) 기준.", 9, DESC, 0)]),
        ([("자본금 5억 · 자가 사옥 · 신용등급 B+ — 박람회 한 번으로 사라지지 않는 주관사의 조건입니다.", 536.8)],
         [("현금흐름 A · 부채비율 17.1% · ISO 3종 — 박람회 한 번으로 사라지지 않는 주관사의 조건입니다.", 10.5, 0xe8eef5, 1)]),
    ]
    spans = [s for b in page.get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"]]
    plan = []
    for targets, pieces in edits:
        found = []
        for txt, y0 in targets:
            m = [s for s in spans if s["text"] == txt and abs(s["bbox"][1] - y0) < 1]
            assert len(m) == 1, (txt, y0, len(m))
            found.append(m[0])
        plan.append((found, pieces))
    for found, _ in plan:
        for s in found:
            page.add_redact_annot(fitz.Rect(s["bbox"]))
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
    for found, pieces in plan:
        x, y = found[0]["origin"]
        for txt, size, color, bold in pieces:
            f = F_BOLD if bold else F_REG
            tw = fitz.TextWriter(page.rect)
            tw.append((x, y), txt, font=f, fontsize=size)
            tw.write_text(page, color=rgb(color))
            x += f.text_length(txt, fontsize=size)
    LOG.append("p11: 자본금 2억·본사 사옥·현금흐름 A·부채비율 17.1%·신용 BB-")


def fix_part2(d):
    P = lambda n: d[n - 37]
    replace_text(P(44), "공동구매 품목별 최고의 브랜드와 제휴하여 퀄리티있는 업체를 소싱합니다.",
                 "공동구매 품목별 검증된 브랜드와 제휴하여 품질 좋은 업체를 소싱합니다.")
    replace_text(P(47), "1. 입주예정자 공식 카페 / (주)엣지컴퍼니 협력업체 밴드,홈페이지 내 참여희망업체 모집공고 공지",
                 "1. 임차예정자협의회 공식 카페 / (주)엣지컴퍼니 협력업체 밴드·홈페이지 내 참여희망업체 모집공고 공지")
    replace_text(P(68), "95% 이상 지역 최고업체들과의 협업!", "95% 이상 지역 우수업체들과의 협업!")
    replace_text(P(71), "완벽한 진행의 핵심입니다.", "빈틈없는 진행의 핵심입니다.")
    replace_text(P(82), "주관사 최초!! 실링팬 특가 이벤트 ACRO 시스템으로 제어하는 실링팬",
                 "정회원 전용 실링팬 특가 이벤트 · ACRO 시스템으로 제어하는 실링팬")
    replace_text(P(82), "국내 최저 높이 55cm 디자인", "저천장 대응 슬림 디자인")
    replace_text(P(82), "국내 최고 모터 평생 A/S 반영", "BLDC 모터 · 5년 무상 A/S")
    replace_text(P(89), "100%제거!", "집중 케어!")
    replace_text(P(92), "휴젠뜨 전국최저가 진행!", "휴젠뜨 박람회 특가 진행!")
    replace_text(P(92), "욕실컨디션 200% 만족! ALL 바른 환기가전", "욕실 컨디션을 바꾸는 올인원 환기가전")
    replace_text(P(110), "입주예정자분들 대상으로 조경감리 및 설명회 무", "임차예정자분들 대상으로 조경감리 및 설명회 무")
    replace_text(P(111), "완벽한 조경과 하자 관리,", "꼼꼼한 조경과 하자 관리,")
    # 이미지에 박힌 과장표현(표시광고법) 덧패치
    retext(P(44), (214, 95, 668, 112), "공동구매 품목별 검증된 브랜드와 제휴하여 품질 좋은 업체를 소싱합니다.", 13, x=216)
    retext(P(68), (312, 162, 479, 185), "지역 우수업체들과의 협업!", 13.5, x=315)
    retext(P(71), (228, 108, 432, 151), "빈틈없는 진행의", 31, x=234)
    retext(P(82), (219, 173, 622, 195), "정회원 전용 실링팬 특가 이벤트 · ACRO 시스템으로 제어하는 실링팬", 13.5, x=222)
    retext(P(82), (51, 294, 172, 321), ["정회원 50% 특별 할인", "프리미엄 실링팬"], 8, x=53, gap=13.7)
    retext(P(82), (51, 381, 172, 408), ["BLDC 모터 품질", "A/S 보장"], 8, x=53, gap=14)
    retext(P(89), (50, 278, 178, 293), "전문 장비를 사용하여 꼼꼼히 제거", 7.6, x=52)
    retext(P(89), (50, 368, 168, 385), "곰팡이/악취 집중 제거", 7.6, x=52)
    retext(P(89), (231, 273, 372, 287), "깨끗하게 제거해 드립니다.", 10.5, x=233)
    retext(P(89), (421, 531, 552, 562), "집중 제거!", 27, x=424)
    retext(P(92), (355, 101, 672, 154), "박람회 특가 진행!", 46, x=365)
    retext(P(92), (221, 156, 522, 176), "욕실 컨디션을 바꾸는 올인원 환기가전", 13.5, x=224)
    retext(P(111), (226, 66, 434, 92), "꼼꼼한 조경과 하자 관리,", 24, x=232.5)


def fix_part3(d):
    P = lambda n: d[n - 122]
    replace_text(P(133), "최저 소", "저소")
    replace_text(P(133), "최저 전력 소비", "저전력 소비")
    replace_text(P(138), "전국 최저", "박람회 특가")
    replace_text(P(138), "목욕 만족도 200%를 책임지는 휴젠뜨와 함께하세", "쾌적한 욕실을 책임지는 휴젠뜨와 함께하세")
    replace_text(P(146), "]는 세계 최고 권위 UL의 친환경 인증 프로그램으", "]는 UL의 대표적인 실내공기 친환경 인증 프로그램으")
    replace_text(P(146), "] 등급은 가장 까다로운 조건을 통과한 최고 제품에 ", "] 등급은 까다로운 기준을 통과한 제품에 ")
    replace_text(P(148), "위생적인 욕실환경 유지에 필수! 곰팡이/악취 100% 제", "위생적인 욕실환경 유지에 필수! 곰팡이/악취 집중 제")
    replace_text(P(148), "휴젠뜨 전국 최저가", "휴젠뜨 박람회 특가")
    replace_text(P(148), "욕실컨디션 200% 만족 아이템", "욕실 컨디션 개선 아이템")
    replace_text(P(148), "주관사 최초! 블루투스 탑재 실링팬 특가 혜택", "블루투스 탑재 ACRO 실링팬 특가 혜택")
    replace_text(P(149), "입주박람회장 입예협 부스 지원", "입주박람회장 임예협 부스 지원")
    replace_text(P(149), "입주예정자 협의회 부스 지원", "임차예정자협의회 부스 지원")
    replace_text(P(149), "입예협 업무지원", "임예협 업무지원")
    replace_text(P(149), "입주 전 완벽 점검, 안전과 만족 확보", "입주 전 꼼꼼한 점검, 안전과 만족 확보")
    retext(P(133), (49, 491, 84, 504), "저소음", 7.5, x=52)
    retext(P(133), (188, 491, 240, 504), "저전력 소비", 7.5, x=191.5)
    retext(P(138), (100, 530, 353, 551), "쾌적한 욕실을 책임지는 휴젠뜨와 함께하세요.", 12.5, x=104)
    retext(P(146), (289, 426, 487, 449), ["[ 그린가드 ]는 UL의 대표적인 실내공기 친환경 인증 프로그램으로",
                                          "[ 골드 ] 등급은 까다로운 기준을 통과한 제품에 부여됩니다."], 6.4, x=292, gap=11.5)
    retext(P(148), (560, 270, 799, 283), "위생적인 욕실환경 유지에 필수! 곰팡이/악취 집중 제거", 6.6, align="center")
    retext(P(148), (517, 393, 578, 404), "휴젠뜨 박람회 특가", 6.6, align="center")
    retext(P(148), (660, 393, 756, 404), "욕실 컨디션 개선 아이템", 6.6, align="center")
    retext(P(148), (639, 410, 777, 420), "블루투스 탑재 ACRO 실링팬 특가 혜택", 6.6, align="center")
    retext(P(149), (85, 146, 236, 171), "임예협 업무지원", 20, x=87, note="임차예정자협의회")
    retext(P(150), (128, 97, 285, 123), "임예협 업무지원", 23, x=131, note="임차예정자협의회")
    # 152p 주소: 사업자등록증 본점(울산 온산로 615-1) 기준
    p = P(152)
    panel_label(p, (205, 528, 372, 568), ["울산 본사", "울산 울주군 청량읍 온산로 615-1"], 9, LIGHT, x=209, gap=15)
    panel_label(p, (416, 528, 582, 568), ["부산 사무소", "부산 해운대구 아르피나 B1"], 9, LIGHT, x=420, gap=15)


def shrink(d, maxw=1600, q=74):
    """큰 JPEG만 가볍게 재압축(가로 1600px·품질 74) → 분할본 30MB 이하 유지."""
    for x in range(1, d.xref_length()):
        try:
            if d.xref_get_key(x, "Subtype")[1] != "/Image" or d.xref_get_key(x, "Filter")[1] != "/DCTDecode":
                continue
            raw = d.xref_stream_raw(x)
            if len(raw) < 60000:
                continue
            im = Image.open(io.BytesIO(raw))
            if im.mode not in ("RGB", "L"):
                continue
            if im.width > maxw:
                im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, "JPEG", quality=q, optimize=True, progressive=True)
            if buf.tell() >= len(raw):
                continue
            d.update_stream(x, buf.getvalue(), compress=False)
            d.xref_set_key(x, "Filter", "/DCTDecode")
            d.xref_set_key(x, "DecodeParms", "null")
            d.xref_set_key(x, "Width", str(im.width))
            d.xref_set_key(x, "Height", str(im.height))
        except Exception:
            pass


def main():
    evdir, s1, s2, s3, out = sys.argv[1:6]
    E = lambda n: fitz.open(os.path.join(evdir, n))
    ev = {"사업자등록증": E("사업자등록증.pdf"), "법인등기부등본": E("법인등기부등본.pdf"), "국세": E("국세_납세증명서.pdf"),
          "지방세": E("지방세_납세증명서.pdf"), "4대보험": E("4대보험_가입자명부.pdf"), "ISO": E("ISO_인증서.pdf"),
          "NICE": E("NICE_기업신용평가.pdf")}
    os.makedirs(out, exist_ok=True)
    merged = fitz.open()
    for src, fn, name, off in ((s1, lambda d: fix_part1(d, ev), "1-36", 0), (s2, fix_part2, "37-121", 36),
                               (s3, fix_part3, "122-152", 121)):
        OFF[0] = off
        d = fitz.open(src)
        fn(d)
        shrink(d)
        dst = os.path.join(out, f"엣지컴퍼니_통합제안서_{name}_수정.pdf")
        d.save(dst, garbage=3, deflate=True)
        print("saved", dst, f"{os.path.getsize(dst) / 1e6:.1f}MB")
        merged.insert_pdf(fitz.open(dst))
    dst = os.path.join(out, "엣지컴퍼니_통합제안서_전체_152p.pdf")
    merged.save(dst, garbage=4, deflate=True)
    print("saved", dst, f"{os.path.getsize(dst) / 1e6:.1f}MB", len(merged), "pages")
    with open(os.path.join(out, "수정내역.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG))
    print("\n".join(LOG))


if __name__ == "__main__":
    main()
