# -*- coding: utf-8 -*-
"""엣지컴퍼니 회사 제안서(지명원) v6 — 기본틀 통합제안서(152p, sha256 497001c5…) 위 덧패치.

특정 입찰용이 아닌 범용 회사 제안서(지명원). 건설사·시행사·입주예정자협의회 어디에 내도
허위·과장·개인정보 문제가 없도록 고친다(2·3파트 과장표현은 본부장 10-02 지시로 원본 유지).

사용: python jimyeong_v6.py <기본틀_152p.pdf> <증빙폴더> <사진폴더(assets_ins)> <출력.pdf>
  - 증빙폴더: 전기공사업_등록증.pdf · ISO_인증서.pdf · SGI_계약보증보험증권_세종스마트시티_20260907.pdf
  - 출력 PDF·증빙·사진은 개인정보 포함 → 깃 금지. 이 스크립트만 둔다.
원칙: 이미지 속 글자는 배경색 패치 + Pretendard 재기입, 증빙은 원본 그대로(흰 바탕·비율 유지),
제품·서류를 AI로 만들지 않는다. 저장은 garbage=3(4 금지 — 글자 깨짐 이력).
쪽 번호는 기본틀 PDF 기준(1부터). 마지막에 중복·허위 쪽(7·10·27·30)을 뺀다(번호 없는 쪽만 → 슬라이드 번호 영향 없음).
"""
import io
import os
import sys

import numpy as np
import pymupdf as fitz
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fix_all as F  # noqa: E402

R, B, S = F.F_REG, F.F_BOLD, F.F_SERIF
NAVY, GOLD, DARK, GRAY, LIGHT = F.NAVY, F.GOLD, F.DARK, F.GRAY, F.LIGHT
DELETE = [7, 10, 27, 30]  # 기본틀 PDF 쪽(1부터)
LOG = []
BASE = None   # 원본(수정 전) 문서 — 그림 복사용
EV = {}
ASSET = ""


def log(pno, msg):
    LOG.append(f"p{pno}: {msg}")


rgb = F.rgb


# ------------------------------------------------------------------ 도구
def clear_text(page, rect):
    """rect 안 텍스트층만 지움(그림·도형 유지)."""
    page.add_redact_annot(fitz.Rect(rect))
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE,
                          text=fitz.PDF_REDACT_TEXT_REMOVE)


def burn(page, rects):
    """개인정보 가림을 그림 픽셀에 굳힘: 겹치는 이미지 픽셀을 지우고(추출해도 안 보임) 텍스트층도 지움."""
    for r in rects:
        page.add_redact_annot(fitz.Rect(r))
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS, graphics=fitz.PDF_REDACT_LINE_ART_NONE,
                          text=fitz.PDF_REDACT_TEXT_REMOVE)


def clear_all_text(page):
    clear_text(page, page.rect)


def hidden_replace(page, old, new):
    """숨은 텍스트층(그림 아래) 문구 교체 — 화면은 그대로, 검색·복사 값만 바뀜."""
    hits = [s for b in page.get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"]
            if old in s["text"]]
    if not hits:
        return False
    for s in hits:
        clear_text(page, fitz.Rect(s["bbox"]))
        tw = fitz.TextWriter(page.rect)
        tw.append(s["origin"], s["text"].replace(old, new), font=R, fontsize=s["size"])
        tw.write_text(page, render_mode=3)


def fill(page, rect, color):
    page.draw_rect(fitz.Rect(rect), color=None, fill=rgb(color) if isinstance(color, int) else color,
                   overlay=True)


def _smooth(v, k):
    if k <= 1 or len(v) <= k:
        return v
    pad = np.pad(v, ((k // 2, k - 1 - k // 2), (0, 0)), mode="edge")
    ker = np.ones(k) / k
    return np.stack([np.convolve(pad[:, c], ker, mode="valid") for c in range(3)], 1)


def bg_fill(page, rect, ring=2.5, z=2.0, smooth=0, mode="all", feather=None):
    """rect 둘레 색으로 안쪽을 매끈하게 메움(가장자리 4변 보간 = 이음새 없음). 그림 1장으로 굳힘.
    mode='tb' = 위·아래 변만 보간(카드 안처럼 좌우 테두리를 끌어오면 안 될 때).
    feather = {'t':pt,'b':pt,'l':pt,'r':pt} — 그 변을 원본 쪽으로 서서히 투명하게(경계선 없앰)."""
    rect = fitz.Rect(rect)
    clip = fitz.Rect(rect.x0 - ring, rect.y0 - ring, rect.x1 + ring, rect.y1 + ring) & page.rect
    pix = page.get_pixmap(matrix=fitz.Matrix(z, z), clip=clip, alpha=False)
    a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).astype(float)
    r = max(2, int(ring * z))
    top, bot = np.median(a[:r], 0), np.median(a[-r:], 0)
    lef, rig = np.median(a[:, :r], 1), np.median(a[:, -r:], 1)
    if smooth:
        k = int(smooth * z)
        top, bot, lef, rig = (_smooth(v, k) for v in (top, bot, lef, rig))
    H, W = a.shape[:2]
    s = np.linspace(0, 1, W)[None, :, None]
    t = np.linspace(0, 1, H)[:, None, None]
    A = (1 - t) * top[None] + t * bot[None]
    if mode == "tb":
        out = np.clip(A, 0, 255).astype(np.uint8)
    else:
        Bm = (1 - s) * lef[:, None] + s * rig[:, None]
        c00, c10, c01, c11 = top[0], top[-1], bot[0], bot[-1]
        C = (1 - s) * (1 - t) * c00 + s * (1 - t) * c10 + (1 - s) * t * c01 + s * t * c11
        out = np.clip(A + Bm - C, 0, 255).astype(np.uint8)
    if feather:
        al = np.ones((H, W))
        yy = np.arange(H)[:, None] * np.ones((1, W))
        xx = np.ones((H, 1)) * np.arange(W)[None, :]
        for side, d in feather.items():
            n = max(1.0, d * z)
            dist = {"t": yy, "b": H - 1 - yy, "l": xx, "r": W - 1 - xx}[side]
            al = np.minimum(al, np.clip(dist / n, 0, 1))
        al = al * al * (3 - 2 * al)  # smoothstep
        im = Image.fromarray(np.dstack([out, (al * 255).astype(np.uint8)]), "RGBA")
    else:
        im = Image.fromarray(out)
    buf = io.BytesIO()
    im.save(buf, "PNG")
    page.insert_image(clip, stream=buf.getvalue(), overlay=True)


def vgrad(page, rect, top_rect, bot_rect, feather=None, z=2.0, span=None, colors=None):
    """rect를 원본 두 띠(top_rect·bot_rect)의 중앙값 색 사이 세로 그라데이션으로 메움(가로 줄무늬 없음).
    span=(y0,y1) = 색 보간 기준 세로 구간(여러 rect가 같은 그라데이션을 공유)."""
    def med(r):
        pix = page.get_pixmap(matrix=fitz.Matrix(z, z), clip=fitz.Rect(r), alpha=False)
        return np.median(np.frombuffer(pix.samples, np.uint8).reshape(-1, 3), 0)
    c0, c1 = colors if colors else (med(top_rect), med(bot_rect))
    rect = fitz.Rect(rect)
    H, W = int(rect.height * z), int(rect.width * z)
    y0, y1 = span or (rect.y0, rect.y1)
    t = np.clip((np.linspace(rect.y0, rect.y1, H) - y0) / (y1 - y0), 0, 1)[:, None, None]
    out = np.clip((1 - t) * c0 + t * c1, 0, 255) * np.ones((1, W, 1))
    out = out.astype(np.uint8)
    if feather:
        al = np.ones((H, W))
        yy = np.arange(H)[:, None] * np.ones((1, W))
        xx = np.ones((H, 1)) * np.arange(W)[None, :]
        for side, d in feather.items():
            dist = {"t": yy, "b": H - 1 - yy, "l": xx, "r": W - 1 - xx}[side]
            al = np.minimum(al, np.clip(dist / max(1.0, d * z), 0, 1))
        al = al * al * (3 - 2 * al)
        im = Image.fromarray(np.dstack([out, (al * 255).astype(np.uint8)]), "RGBA")
    else:
        im = Image.fromarray(out)
    buf = io.BytesIO()
    im.save(buf, "PNG")
    page.insert_image(rect, stream=buf.getvalue(), overlay=True)


def drop_spans(page, rect, fonts=("MalgunGothic",)):
    """rect 안 숨은 원본 텍스트층(맑은고딕 OCR 층)만 지움 — 새로 쓴 Pretendard 글자는 남김."""
    hits = [s for b in page.get_text("dict", clip=fitz.Rect(rect))["blocks"] for l in b.get("lines", [])
            for s in l["spans"] if s["font"].startswith(fonts) and s["text"].strip()]
    for s in hits:
        page.add_redact_annot(fitz.Rect(s["bbox"]))
    if hits:
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE,
                              text=fitz.PDF_REDACT_TEXT_REMOVE)
    return len(hits)


def wb(page, x, base, text, size, color, font=None, align="left", max_w=None, hidden=False):
    """기준선(base) 기준 쓰기."""
    font = font or B
    w = font.text_length(text, fontsize=size)
    if max_w and w > max_w:
        size *= max_w / w
        w = font.text_length(text, fontsize=size)
    if align == "center":
        x -= w / 2
    elif align == "right":
        x -= w
    tw = fitz.TextWriter(page.rect)
    tw.append((x, base), text, font=font, fontsize=size)
    tw.write_text(page, color=rgb(color))
    return w


def W(page, x, y, text, size, color, font=None, align="left", max_w=None):
    """y = 글자 세로 중앙."""
    return F.write(page, x, y, text, size, color, font or B, align=align, max_w=max_w)


def runs(page, x, y, rr, align="left"):
    F.write_runs(page, x, y, rr, align=align)


def lines(page, x, cy, items, size, color, font=None, gap=None, align="left", max_w=None):
    gap = gap or size * 1.35
    y0 = cy - gap * (len(items) - 1) / 2
    for i, t in enumerate(items):
        W(page, x, y0 + gap * i, t, size, color, font, align=align, max_w=max_w)


def rt(page, rect, items, size, color=None, font=None, x=None, align="left", gap=None, fill_color=None,
       smooth=False, max_w=None):
    """이미지 속 문구 교체: 텍스트층 지움 → 배경 패치(샘플 색 또는 지정색) → 같은 색 재기입."""
    rect = fitz.Rect(rect)
    color = color if color is not None else F.ink(page, rect)
    clear_text(page, rect)
    if smooth:
        bg_fill(page, rect)
    elif fill_color is not None:
        fill(page, rect, fill_color)
    else:
        F.patch(page, rect)
    if isinstance(items, str):
        items = [items]
    if x is None:
        x = (rect.x0 + rect.x1) / 2 if align == "center" else rect.x0 + 1
    mw = max_w or (rect.width - 2 if align == "center" else rect.x1 - x)
    lines(page, x, (rect.y0 + rect.y1) / 2, items, size, color, font, gap=gap, align=align, max_w=mw)


def copy_from(src_page, src_rect, dst_page, dst_rect, z=6):
    """원본 쪽 그림 일부를 그대로 복사(같은 서체 숫자·로고·액자)."""
    pix = src_page.get_pixmap(matrix=fitz.Matrix(z, z), clip=fitz.Rect(src_rect), alpha=False)
    dst_page.insert_image(fitz.Rect(dst_rect), stream=pix.tobytes("png"), overlay=True)


def ink_cols(page, rect, bg, thr=110, z=8):
    """rect 안 글자 픽셀이 있는 x 구간들(pt)."""
    rect = fitz.Rect(rect)
    pix = page.get_pixmap(matrix=fitz.Matrix(z, z), clip=rect, alpha=False)
    a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).astype(int)
    bgc = np.array([(bg >> 16) & 255, (bg >> 8) & 255, bg & 255])
    m = (np.abs(a - bgc).sum(2) > thr).any(0)
    spans, on = [], None
    for i, v in enumerate(list(m) + [False]):
        if v and on is None:
            on = i
        elif not v and on is not None:
            spans.append((rect.x0 + on / z, rect.x0 + i / z))
            on = None
    return [s for s in spans if s[1] - s[0] > 1.0]


def img_bytes(path, target_ar=None, maxw=1600, q=86, crop_box=None):
    im = Image.open(path).convert("RGB")
    if crop_box:
        im = im.crop(crop_box)
    if target_ar:
        ar = im.width / im.height
        if ar > target_ar:  # 너무 넓음 → 좌우 자름
            nw = int(im.height * target_ar)
            x0 = (im.width - nw) // 2
            im = im.crop((x0, 0, x0 + nw, im.height))
        else:
            nh = int(im.width / target_ar)
            y0 = (im.height - nh) // 2
            im = im.crop((0, y0, im.width, y0 + nh))
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q, optimize=True)
    return buf.getvalue()


def photo(page, rect, name, crop_box=None):
    rect = fitz.Rect(rect)
    page.insert_image(rect, stream=img_bytes(os.path.join(ASSET, name), rect.width / rect.height,
                                             crop_box=crop_box), overlay=True)


def doc_png(doc, pno, dpi=170, masks=()):
    """증빙 PDF 한 쪽 → 여백 자른 JPEG + 비율. masks = 증빙 좌표(pt) 흰 가림(픽셀로 굳힘)."""
    pix = doc[pno].get_pixmap(dpi=dpi, alpha=False)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    k = dpi / 72
    if masks:
        from PIL import ImageDraw
        dr = ImageDraw.Draw(im)
        for m in masks:
            dr.rectangle([m[0] * k, m[1] * k, m[2] * k, m[3] * k], fill=(255, 255, 255))
    g = im.convert("L").point(lambda v: 255 if v < 235 else 0)
    bb = g.getbbox()
    if bb:
        mm = int(dpi * 0.08)
        im = im.crop((max(0, bb[0] - mm), max(0, bb[1] - mm), min(im.width, bb[2] + mm), min(im.height, bb[3] + mm)))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=85, optimize=True)
    return buf.getvalue(), im.width / im.height


def place(page, opening, data_ar, pad=3, white=True):
    """증빙을 개구부 안에 비율 유지로 전부 보이게(남는 곳 흰 여백)."""
    data, ar = data_ar
    o = fitz.Rect(opening)
    if white:
        page.draw_rect(o, color=None, fill=(1, 1, 1), overlay=True)
    box = o + (pad, pad, -pad, -pad)
    if box.width / box.height > ar:
        w = box.height * ar
        t = fitz.Rect(box.x0 + (box.width - w) / 2, box.y0, box.x0 + (box.width + w) / 2, box.y1)
    else:
        h = box.width / ar
        t = fitz.Rect(box.x0, box.y0 + (box.height - h) / 2, box.x1, box.y0 + (box.height + h) / 2)
    page.insert_image(t, stream=data, overlay=True)
    return t


def pill(page, rect, text, size, fg=0xFFFFFF, bg=NAVY, border=None, font=None, r=0.5):
    rect = fitz.Rect(rect)
    page.draw_rect(rect, color=rgb(border) if border else None, fill=rgb(bg), width=0.8, radius=r, overlay=True)
    W(page, (rect.x0 + rect.x1) / 2, (rect.y0 + rect.y1) / 2, text, size, fg, font or B, align="center",
      max_w=rect.width - 6)


def elec():
    return doc_png(EV["elec"], 0)


# ------------------------------------------------------------------ 1파트: 회사소개
def p3(d):
    p = d[2]
    hidden_replace(p, "임예협 업무지원", "입예협 업무지원")
    sib = F.ink(BASE[2], fitz.Rect(656, 230, 726, 245))  # 형제 항목 '6. 하자체크 지원' 글자색
    rt(p, (636, 183, 716, 201), "입예협 업무지원", 12.2, color=sib, font=B, x=638.5)
    log(3, "목차 09-3 '업체별 업무지원'(텍스트층 '임예협') → '입예협 업무지원'")


def p5(d):
    p = d[4]
    # POINT 1·2와 같은 2줄(흰색 + 금색) · 같은 크기(21pt)
    clear_text(p, (95, 482, 250, 534))
    bg_fill(p, (95, 482, 246, 534))
    W(p, 165, 496.5, "최대 10년", 21, 0xF4F1EA, B, align="center")
    W(p, 165, 519.5, "사후관리", 21, 0xE2C27F, B, align="center")
    log(5, "POINT 3 '10년 안심보장' → '최대 10년 사후관리'(보장 범위 미확정)")


def p6(d):
    p = d[5]
    clear_text(p, (300, 190, 400, 232))  # 숨은 '엣지컴퍼니 사옥'
    tw = fitz.TextWriter(p.rect)
    tw.append((304.6, 207), "엣지컴퍼니 본사 · 쇼룸", font=R, fontsize=12)
    tw.write_text(p, render_mode=3)
    # AI 빌딩 자리 → 패널 바탕색 세로 그라데이션(원본 위·아래 크림색 띠 샘플) + 회사 개요 카드.
    # 본사 외관 사진(hq_tower)은 간판 미세 글자가 깨져 AI 합성으로 보여 쓰지 않음(본부장 확인 전).
    top_s, bot_s = (470, 158, 780, 165), (215, 488, 840, 493)
    vgrad(p, (213, 206, 843, 487), top_s, bot_s, feather={"t": 3, "b": 4, "l": 5}, span=(166, 487))
    vgrad(p, (408, 166, 843, 210), top_s, bot_s, feather={"t": 4, "l": 6}, span=(166, 487))
    c = fitz.Rect(230, 222, 828, 470)
    p.draw_rect(c, color=rgb(0xC3A37D), fill=rgb(NAVY), width=1, radius=0.05, overlay=True)
    logo = os.path.join(ASSET, "logo_lockup_rev.png")
    if os.path.exists(logo):
        p.insert_image(fitz.Rect(254, 250, 254 + 196, 250 + 52), filename=logo, keep_proportion=True, overlay=True)
    W(p, 256, 330, "울산 본사 · 쇼룸", 19, 0xE3C48C, B)
    W(p, 256, 356, "울산광역시 울주군 청량읍 온산로 615-1, 2·3층", 10.5, 0xDDE3EC, R, max_w=228)
    W(p, 256, 376, "대표이사 고진식", 10, 0xA8B8CA, R)
    W(p, 256, 394, "주관사업 총괄 본부장 윤현욱 · 010-7273-9901", 10, 0xA8B8CA, R, max_w=228)
    W(p, 256, 440, "ISO 9001 · 14001 · 45001 인증 (2025.08)", 10, 0xC9A96A, B, max_w=228)
    p.draw_line((498, 246), (498, 446), color=rgb(0x2C3E5C), width=0.8, overlay=True)
    tiles = [("2022.02", "법인 설립"), ("제 울산-00821호", "전기공사업 등록"),
             ("임직원 14명", "정규직 10 + 인턴 4 (2026.10)"), ("직영 4 · 협력 8", "전국 12개 거점")]
    for i, (big, sub) in enumerate(tiles):
        x0, y0 = 518 + (i % 2) * 152, 244 + (i // 2) * 104
        tr = fitz.Rect(x0, y0, x0 + 142, y0 + 92)
        p.draw_rect(tr, color=rgb(0x2C3E5C), fill=rgb(0x10284F), width=0.8, radius=0.08, overlay=True)
        W(p, tr.x0 + 71, y0 + 38, big, 16, 0xE3C48C, B, align="center", max_w=130)
        W(p, tr.x0 + 71, y0 + 64, sub, 9.5, 0xDDE3EC, R, align="center", max_w=130)
    log(6, "AI 빌딩(외벽 DEFELICE·스타벅스·신세계 간판, '사옥') → 패널 바탕 + 회사 개요 카드(울산 본사·쇼룸 주소 · 2022.02 설립 · "
           "전기공사업 제 울산-00821호 · 임직원 14명 · 직영 4·협력 8 · ISO 3종). 본사 외관 사진은 AI 합성 의심으로 미사용")


def p8(d):
    p = d[7]
    burn(p, [(505.2, 398.3, 575.2, 428.6)])
    # 사업자등록증 '세금계산서 발행정보'(담당자 개인 휴대폰·메일) 가림
    fill(p, (505.2, 398.3, 575.2, 428.6), (1, 1, 1))
    W(p, 540.2, 413.4, "(발행정보 가림)", 4.2, 0x9AA0A6, R, align="center")
    # 회사구분
    rt(p, (543, 157, 805, 179), "전시 · 박람회 · 행사 대행  /  전기공사업", 12, color=0xF2F2F2, font=R, x=545)
    # 소재지(fix_all 텍스트) 보강
    for s in [s for b in p.get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"]
              if "온산로" in s["text"] or "아르피나" in s["text"]]:
        clear_text(p, fitz.Rect(s["bbox"]))
    fill(p, (542, 189, 814, 227), F.sample_bg(p, fitz.Rect(542, 189, 814, 227)))
    W(p, 546, 198.75, "울산광역시 울주군 청량읍 온산로 615-1, 2·3층 (본사 · 쇼룸)", 10.5, LIGHT, B, max_w=265)
    W(p, 546, 217.25, "부산광역시 해운대구 아르피나 B1 (부산 지사)", 10.5, LIGHT, B, max_w=265)
    # 과장표현 '최고의'
    rt(p, (208, 217, 398, 251), "든든한 입주파트너", 27, color=0xA77E48, font=B, x=303, align="center")
    rt(p, (264, 559, 600, 581), "전문성과 책임감으로 신뢰를 지킵니다.", 11.2, color=0xDDE1E8, font=R, x=266)
    # 대표 연락처
    W(p, 812, 549, "주관사업 총괄 본부장 윤현욱", 9.5, 0xD9B97A, B, align="right")
    W(p, 812, 568, "010-7273-9901 · edgecompany1@naver.com", 9.5, 0xDDE1E8, R, align="right")
    log(8, "사업자등록증 발행정보(담당자 HP·개인 메일) 가림 / 회사구분 '건설업무 대행'→'행사 대행 / 전기공사업' / "
           "'최고의 입주파트너'→'든든한 입주파트너' / 하단 '최고의 가치'→'신뢰를 지킵니다' / 소재지 2·3층·부산 지사 / 대표 연락처 추가")


def p9(d):
    p = d[8]
    # 숨은 텍스트층에 남은 다른 장 문구('직접 면허 보유!'·'한국 면허등록 업체 자문'·'건설업') 삭제(화면 변화 없음)
    drop_spans(p, (280, 90, 810, 200))
    drop_spans(p, (280, 488, 670, 518))
    c = F.sample_bg(p, fitz.Rect(402.5, 488.3, 439.2, 492.8), ring=0.6)
    burn(p, [(210.2, 317.4, 267.4, 379.5), (402.4, 488.2, 439.3, 498.5)])
    # 4대보험 명부: 주민번호 열·성명 열 전체 가림(10행)
    g = (0.90, 0.90, 0.90)
    fill(p, (210.2, 317.4, 242.2, 379.5), g)
    fill(p, (243.2, 317.4, 267.4, 379.5), g)
    p.draw_line((242.7, 317.4), (242.7, 379.5), color=(0.1, 0.1, 0.1), width=0.35, overlay=True)
    W(p, 226.2, 348.5, "가림", 4.5, 0x777777, R, align="center")
    W(p, 255.3, 348.5, "가림", 4.5, 0x777777, R, align="center")
    W(p, 238.5, 385.6, "※ 개인정보 보호를 위해 주민번호·성명 가림 · 가입자 10명", 3.6, 0x555555, R, align="center")
    # NICE 주요 주주 성명 → 직위
    fill(p, (402.4, 488.2, 439.3, 492.9), c)
    fill(p, (402.4, 493.6, 439.3, 498.5), c)
    p.draw_line((402.4, 493.25), (439.3, 493.25), color=(0.25, 0.25, 0.25), width=0.3, overlay=True)
    W(p, 420.8, 490.6, "대표이사", 3.4, 0x1A1A1A, R, align="center")
    W(p, 420.8, 496.0, "기타 주주(1인)", 3.4, 0x1A1A1A, R, align="center")
    # 유효기간 주석
    W(p, 590, 592, "※ 증빙은 2026.10.02 발급본(NICE 2026.06.19) 기준 · 제출 시 최신 발급본을 별도 첨부합니다.",
      7.2, 0x5A5F6A, R, align="center")
    log(9, "4대보험 명부 주민번호·성명 열 전체 가림(픽셀) + 주석 / NICE 주요 주주 성명 → '대표이사·기타 주주' / 증빙 기준일 주석")


def p11(d):
    p = d[10]
    spans = [s for b in p.get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"]]

    def find(t, y=None):
        m = [s for s in spans if s["text"] == t and (y is None or abs(s["bbox"][1] - y) < 1.5)]
        assert len(m) == 1, (t, len(m))
        return m[0]

    T = {k: find(k) for k in ["본사\xa0사옥", "\xa0운영", "엣지컴퍼니\xa0본사\xa0사옥", "사옥",
                              "사옥에서 본사·쇼룸을 직접 운영합니다.", "하자 예치금·이행보증의 재원이 되는 실체입니",
                              "다.", "삼성전자 MOU"]}
    for s in T.values():
        p.add_redact_annot(fitz.Rect(s["bbox"]))
    p.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)

    def put(s, pieces):
        x, y = s["origin"]
        for t, size, col, f in pieces:
            tw = fitz.TextWriter(p.rect)
            tw.append((x, y), t, font=f, fontsize=size)
            tw.write_text(p, color=rgb(col))
            x += f.text_length(t, fontsize=size)

    put(T["본사\xa0사옥"], [("본사 · 쇼룸", 28, 0xE3C48C, B), (" 운영", 28, 0xFFFFFF, B)])
    put(T["엣지컴퍼니\xa0본사\xa0사옥"], [("엣지컴퍼니 울산 본사", 11.5, 0xF0E2C4, B)])
    tw = fitz.TextWriter(p.rect)  # '본사'(27pt) 바로 뒤에 붙임(원본 '사옥' 자리는 간격이 넓음)
    tw.append((652.4 + 4, T["사옥"]["origin"][1]), "· 쇼룸", font=B, fontsize=12)
    tw.write_text(p, color=rgb(0xC2AB85))
    put(T["사옥에서 본사·쇼룸을 직접 운영합니다."], [("울산 온산로 615-1, 2·3층에서 직접 운영합니다.", 9, 0x9DADBE, R)])
    put(T["하자 예치금·이행보증의 재원이 되는 실체입니"], [("협약 시 하자 예치금·보증증권 제출의 재원입니다.", 9, 0x9DADBE, R)])
    put(T["삼성전자 MOU"], [("삼성 측 업무제휴", 8.1, 0xE3C48C, B)])
    log(11, "'본사 사옥'→'본사 · 쇼룸'(NICE상 임차) · OFFICE 카드·사진 캡션 정리 · CAPITAL 설명 '이행보증의 재원'→'협약 시 … 제출의 재원' · "
            "칩 '삼성전자 MOU'→'삼성 측 업무제휴'")


def p12(d):
    p = d[11]
    hidden_replace(p, "임예협 여러분과", "입주민 여러분과")
    clear_text(p, (210, 170, 480, 290))
    bg_fill(p, (217, 203, 482, 332))
    W(p, 222, 236, "전기공사업", 50, 0xA57526, B)
    runs(p, 222, 288, [("등록 ", 44, 0x061C5D, B), ("보유", 40, 0x061C5D, R)])
    W(p, 223, 322, "제 울산-00821호 · 2022.05.04 등록 · 2026.07.15 재교부", 9.6, 0x4A4F5A, R)
    t = place(p, (523, 137, 787, 545), elec(), pad=6)
    log(12, f"'주관사 자체 건설업 면허 보유!' + AI '건설업 면허' 액자 → '주관사 전기공사업 등록 보유'(제 울산-00821호) + 전기공사업 등록증 실물 {tuple(round(v) for v in t)}")


def p14(d):
    p = d[13]
    clear_text(p, (200, 60, 849, 600))
    bg_fill(p, (250, 56, 800, 138), smooth=30)
    runs(p, 524, 104, [("외주가 아닌 ", 40, 0x0B1E3F, B), ("전기공사업", 40, 0xB0874A, B), (" 직접 등록", 40, 0x0B1E3F, B)],
         align="center")
    bg_fill(p, (340, 143, 712, 170), smooth=20)
    W(p, 526, 156, "제 울산-00821호 · 2022.05.04 등록 · 2026.07.15 재교부", 13, 0x3A3F4A, R, align="center")
    bg_fill(p, (205, 196, 849, 566), smooth=40)
    # 액자(금색 이중 테두리) + 실물 등록증
    fr = fitz.Rect(250, 205, 470, 515)
    p.draw_rect(fr + (3, 3, 3, 3), color=None, fill=(0.80, 0.78, 0.74), overlay=True)  # 그림자
    p.draw_rect(fr, color=rgb(0xB8913F), fill=rgb(0xD9B465), width=0, overlay=True)
    p.draw_rect(fr + (5, 5, -5, -5), color=rgb(0x8C6A2A), fill=(1, 1, 1), width=0.8, overlay=True)
    place(p, fr + (6, 6, -6, -6), elec(), pad=4, white=False)
    pill(p, (290, 520, 430, 542), "전기공사업 등록증", 12, fg=0xF3E2BE, bg=0x0B1E3F, border=0xC3A37D)
    # 등록 사항 카드
    c = fitz.Rect(500, 210, 815, 515)
    p.draw_rect(c, color=rgb(0xC3A37D), fill=rgb(0x0B1E3F), width=1, radius=0.04, overlay=True)
    W(p, 522, 238, "등록 사항", 17, 0xE3C48C, B)
    rows = [("등록번호", "제 울산-00821호"), ("상호", "주식회사 엣지컴퍼니"), ("대표자", "고진식"),
            ("최초 등록", "2022년 05월 04일"), ("재교부", "2026년 07월 15일"), ("등록관청", "울산광역시장"),
            ("영업소", "울산 울주군 청량읍 온산로 615-1, 2·3층")]
    y = 270
    for k, v in rows:
        W(p, 522, y, k, 10.5, 0xC9A96A, B)
        W(p, 590, y, v, 10.5, 0xF2F2F2, R, max_w=215)
        p.draw_line((522, y + 11), (795, y + 11), color=rgb(0x2C3E5C), width=0.5, overlay=True)
        y += 27
    W(p, 522, 470, "전기 분야 공사는 등록 업체인 당사가 직접 시공합니다.", 9.5, 0xD8DEE8, R, max_w=280)
    W(p, 522, 488, "「전기공사업법」 제4조제1항에 따른 등록 · 울산광역시장 발급", 8.5, 0x9DADBE, R, max_w=280)
    log(14, "'외주가 아닌 직접 면허 보유!'·'한국 면허등록 업체 자문' + 견본 4장(전기공사업 2024-000000·홍길동/위촉장/건설업/소독업) "
            "→ '외주가 아닌 전기공사업 직접 등록' + 전기공사업 등록증 실물 1장 + 등록 사항 카드")


def p15(d):
    p = d[14]
    iso = EV["iso"]
    frames = [((200.5, 223, 385.5, 499), elec(), "전기공사업 등록증", 290.5),
              ((403.5, 223, 589, 499), doc_png(iso, 0), "ISO 9001 품질경영", 495.5),
              ((606.5, 223, 795, 499), doc_png(iso, 4), "ISO 45001 안전보건", 701)]
    for op, data, cap, cx in frames:
        o = fitz.Rect(op)
        p.draw_rect(fitz.Rect(o.x0, o.y0, o.x1, 507.5), color=None, fill=(1, 1, 1), overlay=True)
        place(p, o, data, pad=4, white=False)
        r = fitz.Rect(cx - 64, 503.5, cx + 64, 518.5)
        fill(p, r, F.sample_bg(p, fitz.Rect(cx - 64, 505, cx + 64, 517), ring=0.8))
        W(p, cx, 511, cap, 12.5, 0xFFFFFF, B, align="center", max_w=125)
    log(15, "견본 3장(건설업등록증·소방시설업등록증·전기공사업 서울-00-12345, 대표 홍길동) → 전기공사업 등록증 실물 · ISO 9001 · ISO 45001 실물, 캡션 교체")


def p16(d):
    p = d[15]
    src = BASE[15]
    m1 = doc_png_img(os.path.join(ASSET, "g02_mou1.jpg"))
    m2 = doc_png_img(os.path.join(ASSET, "g02_mou2.jpg"))
    # 1번 액자 개구부에 실물 1쪽 → 2번 액자(원본 그림)를 다시 위에 → 2번 개구부에 실물 2쪽
    place(p, (246, 208, 452.5, 505.5), m1, pad=3)
    copy_from(src, (417, 242, 640, 539), p, (417, 242, 640, 539), z=4)
    place(p, (423.5, 249.5, 632, 532), m2, pad=3)
    clear_text(p, (250, 115, 650, 170))
    bg_fill(p, (258, 120, 645, 166))
    runs(p, 262, 142, [("삼성 측 ", 46, 0x0B1E3F, B), ("업무제휴", 46, 0xB0874A, B)])
    rt(p, (448, 545, 598, 562), "삼성 측 업무제휴 계약서 (2022)", 11.5, color=0xFFFFFF, font=B, align="center",
       fill_color=F.sample_bg(p, fitz.Rect(448, 545, 598, 562), ring=0.6))
    rt(p, (700, 213, 832, 306), ["2022.03", "업무제휴", "계약 체결"], 20, color=0xFFFFFF, font=B, align="center",
       x=766, gap=27, fill_color=F.sample_bg(p, fitz.Rect(700, 213, 832, 306), ring=1.5))
    log(16, "'삼성전자 MOU 체결'(제목·캡션) → '삼성 측 업무제휴' / AI 재현 계약서 2장 → 업무제휴 계약서 실물 스캔 2쪽 / "
            "말풍선 'LX하우시스, 에몬스 체결 준비중'(미확인) → '2022.03 업무제휴 계약 체결'")


def doc_png_img(path):
    im = Image.open(path).convert("RGB")
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=88)
    return buf.getvalue(), im.width / im.height


def p17(d):
    p = d[16]
    rt(p, (258, 72, 520, 106), "협력사 연계 종합 건물관리 지원", 24, color=0x3A3F4A, font=R, x=260)
    clear_text(p, (476, 318, 566, 404))
    bg_fill(p, (485, 322, 557, 402), smooth=12)
    lines(p, 521, 362, ["협력사", "연계", "관리 지원"], 15, 0xF3E2BE, B, gap=20, align="center")
    rt(p, (598, 293, 662, 316), "시설관리", 15, color=0x1E2433, font=B, align="center", x=630)
    log(17, "'종합건물관리 전문업체'·중앙 '관리통합전문 주식회사 BCS'(타사, 제휴 근거 없음) → '협력사 연계 종합 건물관리 지원'·'협력사 연계 관리 지원' / "
            "'위탁관리'(주택관리업 오인) → '시설관리'")


def p18(d):
    p = d[17]
    teams = [((246, 340), 452, "2명", "건설사·협의회 영업"), ((380, 470), 478, "3명", "박람회 기획·운영"),
             ((510, 601), 478, "3명", "이벤트·홍보 진행"), ((644, 737), 502, "4명", "협력사·민원 지원")]
    burn(p, [(x0 + 2, 401, x1 - 2, yb - 2) for (x0, x1), yb, n, duty in teams])
    for (x0, x1), yb, n, duty in teams:
        bg_fill(p, (x0, 398, x1, yb), smooth=25)
        cx = (x0 + x1) / 2
        W(p, cx, 422, n, 22, 0xE3C48C, B, align="center")
        W(p, cx, 446, duty, 9.5, 0xD8DEE8, R, align="center", max_w=x1 - x0 - 6)
    W(p, 612, 220, "임직원 14명", 15, 0xE3C48C, B)
    W(p, 612, 240, "정규직 10명 + 인턴 4명 · 2026.10 기준", 9, 0xC8D0DC, R)
    log(18, "조직도 팀원 실명 12명(4대보험 명부와 불일치) 삭제 → 팀별 인원·직무(2·3·3·4명) + '임직원 14명(정규직 10 + 인턴 4)'. 대표이사·총괄 본부장은 유지")


def p19(d):
    p = d[18]
    lab_c = 0x1F2A44
    # 슬라이드 번호 15 → 16(번호 중복)
    rt(p, (771, 13.5, 788, 24.5), "16", 11, color=0xF2F2F2, font=B, align="center",
       x=779.5, fill_color=F.sample_bg(p, fitz.Rect(700, 13, 740, 25), ring=0.5))
    # 지사 라벨: 직영 4(금색) + 협력 8
    bg_fill(p, (213, 252, 362, 272), smooth=20)  # 아산(대전 지사가 충청권 커버) 라벨·선 삭제
    rt(p, (214, 289, 266, 305.5), "청주 지사", 12.5, color=0xA9802F, font=B, x=216.4)
    rt(p, (214, 307, 266, 322.5), "대전 지사", 12.5, color=0xA9802F, font=B, x=216.4)
    rt(p, (549, 346, 600, 361.5), "울산 본사", 12.5, color=0xA9802F, font=B, x=551)
    rt(p, (549, 384.5, 600, 400), "부산 지사", 12.5, color=0xA9802F, font=B, x=551)
    # 견본 등록증 썸네일 16장 삭제 → 직영·협력 안내
    bg_fill(p, (648, 136, 830, 458))
    bg_fill(p, (205, 458, 830, 575))
    c = fitz.Rect(655, 145, 826, 452)
    p.draw_rect(c, color=rgb(0xC3A37D), fill=rgb(0x0B1E3F), width=0.8, radius=0.05, overlay=True)
    W(p, 670, 166, "직영 4곳", 15, 0xE3C48C, B)
    items = [("울산 본사 · 쇼룸", "울주군 청량읍 온산로 615-1, 2·3층"), ("부산 지사", "해운대구 아르피나 B1"),
             ("청주 지사", "흥덕구 직지대로 642"), ("대전 지사", "디펠리체 204호 · 충청권 거점")]
    y = 198
    for a, b in items:
        W(p, 670, y, a, 11, 0xF2F2F2, B)
        W(p, 670, y + 16, b, 8.6, 0xA8B8CA, R, max_w=148)
        y += 62
    c2 = fitz.Rect(214, 470, 826, 562)
    p.draw_rect(c2, color=rgb(0xC3A37D), fill=(1, 1, 1), width=0.8, radius=0.08, overlay=True)
    W(p, 232, 492, "협력 8곳", 15, 0xA9802F, B)
    W(p, 312, 492, "서울 · 경인 · 강원 · 전북 · 전남 · 경북 · 대구 · 양산", 12, 0x1F2A44, B)
    runs(p, 232, 530, [("직영 4곳 + 협력 8곳 = ", 13, 0x1F2A44, R), ("전국 12개 지사망", 13, 0xA9802F, B),
                       ("   (지도의 금색 = 직영)", 9.5, 0x6B7280, R)])
    log(19, "지사 13곳(아산·세종 포함, 청주 없음, 견본 '등록증' 썸네일 16장) → 직영 4(울산 본사·부산·청주·대전) + 협력 8 = 12곳, "
            "썸네일 삭제·직영/협력 안내 카드 / 슬라이드 번호 15(중복) → 16")


def p20(d):
    p = d[19]
    rt(p, (262, 561, 350, 575), "직영 4 · 협력 8 거점", 7.6, font=R, x=264.5)
    r = fitz.Rect(218, 508, 330, 526)
    p.draw_rect(r, color=None, fill=rgb(0x0B1E3F), fill_opacity=0.85, overlay=True)
    W(p, 274, 517, "울산 본사 · 쇼룸", 10, 0xE3C48C, B, align="center")
    log(20, "띠 '전국 주요 거점지사 운영' → '직영 4 · 협력 8 거점' / 본사 사진에 '울산 본사 · 쇼룸' 표기")


def p21(d):
    p = d[20]
    clear_text(p, (300, 220, 700, 245))
    fill(p, (312, 224, 686, 240), 0x051331)
    W(p, 498.9, 231.9, "레이카운티 4,470세대 입주박람회 주관 (2023.11)", 12.4, 0xB7BCD0, R, align="center")
    clear_text(p, (390, 550, 600, 573))
    fill(p, (396, 553, 587, 570), 0x041130)
    W(p, 491.1, 561.5, "두산위브더제니스 오션시티 2,813세대 입주박람회 주관 (2025.12 · BEXCO)", 12.4, 0xDADDEC, R,
      align="center", max_w=420)
    runs(p, 481, 378.5, [("1,000세대 이상 주관 ", 8.6, 0x2B2F38, R), ("10개 단지 · 19,563세대", 8.6, 0xA9802F, B),
                         ("   |   누적 수임 ", 8.6, 0x2B2F38, R), ("8년 · 67개 단지 · 56,361세대", 8.6, 0x0B1E3F, B),
                         (" (전신 실적·입주 예정 포함)", 7.4, 0x6B7280, R)], align="center")
    log(21, "레이카운티 캡션 '지역 업체 섭외 서포트…' → '4,470세대 입주박람회 주관(2023.11)' / 오션시티 캡션 '공식 모델하우스 울산 행사 업체 선정' → "
            "'2,813세대 입주박람회 주관(2025.12 · BEXCO)' / 주관 10개 단지 19,563세대 · 누적 수임 67개 단지 56,361세대 요약 줄 추가")


# ------------------------------------------------------------------ 08.수임실적(PDF 22~29)
def fix_last_digit(p, rect, bg_hex):
    """숫자 마지막 자리를 같은 숫자 첫 자리 '2' 그림으로 교체(원본 서체 그대로)."""
    cols = ink_cols(BASE[p.number], rect, bg_hex)
    (a0, a1) = cols[0]
    if len(cols) == 4:
        l0, l1 = cols[3]
    else:  # 마지막 두 자리가 붙어 있으면 자리 폭(첫 자리 폭)으로 나눔
        assert len(cols) == 3, (p.number + 1, cols)
        l1 = cols[2][1]
        l0 = l1 - (a1 - a0) - 0.3
    r = fitz.Rect(rect)
    fill(p, (l0 - 0.6, r.y0, max(l1, l0 + (a1 - a0)) + 0.8, r.y1), bg_hex)
    copy_from(BASE[p.number], (a0 - 0.3, r.y0, a1 + 0.3, r.y1), p, (l0 - 0.3, r.y0, l0 + (a1 - a0) + 0.3, r.y1), z=8)


def p22(d):
    p = d[21]
    clear_all_text(p)
    fix_last_digit(p, (428.5, 150.5, 493, 177.5), 0x0D1D34)
    fill(p, (744, 108, 816, 141), 0x0D1E34)
    W(p, 779.6, 116.6, "양산 이지더원", 11.8, 0xD1CDC2, R, align="center", max_w=68)
    W(p, 779.6, 131.8, "2차 그랜드파크", 11.8, 0xD1CDC2, R, align="center", max_w=68)
    fill(p, (426, 267, 492, 301), 0x0D1D34)
    W(p, 458.4, 276, "힐스테이트", 11.8, 0xD7D1C9, R, align="center")
    W(p, 458.4, 292, "포항", 11.8, 0xD7D1C9, R, align="center")
    fill(p, (746, 267, 811, 301), 0x0D1D34)
    W(p, 778.2, 276, "사송 더샵", 11.8, 0xD7D1C5, R, align="center")
    W(p, 778.2, 292, "데시앙 1차", 11.8, 0xD7D1C5, R, align="center")
    fill(p, (420, 427, 497, 478), 0x0D1D35)
    for t, y in (("두산위브", 436.3), ("더제니스", 452.5), ("센트럴사하", 469)):
        W(p, 458.7, y, t, 11.8, 0xD8D1C0, R, align="center")
    fill(p, (390, 559, 612, 578), 0xFEFEFE)
    W(p, 498.0, 568.8, "부산 사상구 랜드마크 공식 주관사 선정", 12, 0x33373C, R, align="center")
    log(22, "양정자이 SK뷰 2276 → 2272(NICE) / '랜드마크'→'2차 그랜드파크' / '평창'→'포항' / '시흥 센트럴 1차'→'사송 더샵 데시앙 1차' / "
            "'두산위브 더 제 니스' 줄바꿈 / 캡션 '공신'→'공식'")


def p23(d):
    p = d[22]
    clear_all_text(p)
    fill(p, (40, 24, 100, 63), 0x081B33)
    copy_from(BASE[24], (44, 27, 93, 58.5), p, (44.5, 27.5, 94, 59.3))
    p.draw_rect(fitz.Rect(352, 27, 568, 47), color=rgb(GOLD), fill=rgb(NAVY), width=0.8, radius=0.5, overlay=True)
    W(p, 460, 37, "전신(前身) 사업체 실적 · 법인 설립(2022.02) 이전", 9, LIGHT, B, align="center")
    lab = [((211, 76, 342, 93), "양산 이지더원 2차 그랜드파크"), ((432, 76, 548, 93), "양산 두산위브 1차"),
           ((637, 76, 767, 93), "영도 센트럴 에일린의뜰"), ((211, 199.5, 342, 216.5), "남양산 반도유보라"),
           ((432, 199.5, 548, 216.5), "양산 이지더원 리버포레"), ((637, 199.5, 767, 216.5), "일광자이푸르지오 2단지"),
           ((211, 320, 342, 337), "양산 e편한세상 2차"), ((432, 320, 548, 337), "울산 KCC스위첸 웰츠타워"),
           ((637, 320, 767, 337), "e편한세상 연산 더퍼스트"), ((211, 441, 342, 458), "빌리브 울산"),
           ((432, 441, 548, 458), "스마트리치 연산")]
    for r, n in lab:
        F.strip_label(p, r, n, size=10.5)
    fill(p, (347, 222, 390, 261), 0x152A42)
    W(p, 367.6, 236, "—", 20, 0xE2CBA6, S, align="center")
    fill(p, (348, 467, 389, 487.5), 0x152A40)
    wb(p, 367.6, 485, "567", 20, 0xE3CCAA, S, align="center", max_w=30)
    fill(p, (553, 467, 592, 488), 0x1C2C41)
    wb(p, 572.5, 485.8, "380", 20, 0xE3CCAA, S, align="center", max_w=30)
    fill(p, (260, 553, 741, 590), 0xFCFCFC)
    runs(p, 501.4, 571.6, [("2018~2021년 전신(前身) 사업체로 ", 13, DARK, R), ("12개 단지", 17, GOLD, B),
                           (" 입주박람회 수임", 13, DARK, R)], align="center")
    log(23, "'전신(前身) 사업체 실적' 배지 / 로고 'FG'→'EG' / 단지명 11곳 정정(왕산·덕계동·안산·송산 동탄·유성 등 → SPEC) / "
            "반도유보라 세대수 삭제(확인 불가) / 빌리브 울산 512→567 / 스마트리치 연산 338→380 / 캡션 '11,352세대'(합계 불일치) → '12개 단지 입주박람회 수임'")


def p24(d):
    p = d[23]
    clear_all_text(p)
    W(p, 192, 40.3, "2022", 31, NAVY, S)
    C = 0xC9D5E2
    specs = [((278, 98, 337, 129), 284, ["주례롯데캐슬", "골드스마트"], 13.5, 0x102446),
             ((503, 86, 563, 131), 508.5, ["사하", "코오롱하늘채", "리버뷰"], 13, 0x0F2746),
             ((742, 86, 800, 131), 747.8, ["웨이브리즈", "기장 신혼", "희망타운"], 13, 0x0D2443),
             ((278, 246, 337, 278), 284, ["문수로", "드림파크"], 14.5, 0x082445),
             ((503, 233, 563, 280), 508.5, ["오토밸리", "한양립스", "포레스트"], 13, 0x092545),
             ((742, 233, 800, 280), 747.8, ["울산", "대현시티", "프라디움"], 13, 0x0C2546)]
    for r, x, ln, gap, bg in specs:
        fill(p, r, bg)
        r = fitz.Rect(r)
        lines(p, x, (r.y0 + r.y1) / 2, ln, 9.5, C, R, gap=gap, max_w=r.x1 - x - 1)
    fill(p, (743, 397, 790, 411.5), 0x0B2543)
    W(p, 747.8, 404.4, "아르떼", 9.5, C, R)
    fill(p, (258, 532, 749, 568), 0xFEFEFE)
    runs(p, 504.9, 551, [("2022년 ", 13, DARK, R), ("9개 단지", 17, GOLD, B),
                         (", 총 4,206세대의 성공적인 사업 수행", 13, DARK, R)], align="center")
    log(24, "제목 '2022' 추가 / 단지명 7곳 정정(조치원대첩→주례롯데캐슬 골드스마트, 서하→사하 코오롱하늘채 리버뷰, 기장 힐스테이트→웨이브리즈, "
            "대공원파크→드림파크, 한화포레나포항→한양립스 포레스트, 대명사티→울산 대현시티 프라디움, 아르테→아르떼) / "
            "캡션 '2018~2021 12개 단지 11,352세대'(복사 오류) → '2022년 9개 단지 4,206세대'")


def p25(d):
    p = d[24]
    clear_all_text(p)
    NC, NUM = 0xC8D0DC, 0xD1AE80

    def name2(r, x, a, b, bg):
        fill(p, r, bg)
        r = fitz.Rect(r)
        cy = (r.y0 + r.y1) / 2
        W(p, x, cy - 5, a, 9, NC, B, max_w=r.x1 - x - 1)
        W(p, x, cy + 5.5, b, 9, NC, B, max_w=r.x1 - x - 1)

    def num(r, right, base, t, bg):
        fill(p, r, bg)
        wb(p, right, base, t, 19, NUM, S, align="right")

    name2((411, 167, 504, 186.5), 416, "e편한세상 송도", "더퍼스트비치", 0x021D31)
    num((505, 168.5, 541, 185.5), 539.8, 184, "1302", 0x021D31)
    name2((196, 299, 300, 316.5), 199.5, "사송역 우미린", "포레스트", 0x061A30)
    num((301, 299, 338, 316.5), 334, 314.5, "688", 0x061A30)
    fill(p, (611, 299, 700, 316.5), 0x081A2F)
    W(p, 615, 307.75, "사송 더샵 3차", 10, NC, B)
    fill(p, (196, 418.5, 252, 430.5), 0x021B32)
    W(p, 199.5, 425.4, "해운대역", 9, NC, B)
    num((301, 420.5, 338, 439), 333.2, 437, "351", 0x021B32)
    num((506, 420.5, 539.5, 439), 537.2, 437, "452", 0x001A35)
    name2((611, 418.5, 700, 441.5), 615, "사송 LH 신혼", "희망타운 2차", 0x011A36)
    num((700, 420.5, 735, 439), 732.2, 437, "479", 0x011A36)
    name2((196, 536, 300, 555.5), 199.5, "온양발리 한양립스", "더 퍼스트", 0x051C33)
    num((300, 536.5, 338, 555.5), 333.5, 553.2, "442", 0x051C33)
    fill(p, (411, 536, 504, 555.5), 0x031D36)
    W(p, 416, 545.75, "힐스테이트 대연 센트럴", 10, NC, B, max_w=86)
    num((505, 536.5, 540, 555.5), 537.5, 553, "449", 0x031D36)
    name2((611, 536, 700, 555.5), 615, "연산포레", "서희스타힐스", 0x162135)
    num((700, 536.5, 735, 555.5), 732.2, 553.2, "612", 0x162135)
    fill(p, (255, 567, 737.5, 598), 0xF8F7F7)
    runs(p, 492.6, 582.4, [("2023~2024년 ", 13, DARK, R), ("12개 단지", 17, GOLD, B),
                           (", 총 11,441세대의 성공적인 사업 수행", 13, DARK, R)], align="center")
    log(25, "송도 1312→'e편한세상 송도 더퍼스트비치' 1,302 / 사송 우미린 780→'사송역 우미린 포레스트' 688 / '서송'→'사송' / "
            "부산역→'해운대역 푸르지오 더원' 351 / 제일풍경채 430→452 / 신혼희망타운 420→'2차' 479 / 온양발리 400→'더 퍼스트' 442 / "
            "11번 '중산 한양립스 382'→'힐스테이트 대연 센트럴 449'(SPEC안 오토밸리 376은 2022 장과 중복) / "
            "12번 '엘쿠르 더퍼스트 219'(2025 장과 중복)→'연산포레 서희스타힐스 612' / 캡션 10,189 → 11,441세대")


def p26(d):
    p = d[25]
    clear_all_text(p)
    NC, NUM = 0xB7BDCA, 0xD5B07D
    fix_last_digit(p, (64, 161.5, 103, 181.5), 0x011932)

    def name(r, x, ln, bg):
        fill(p, r, bg)
        r = fitz.Rect(r)
        lines(p, x, (r.y0 + r.y1) / 2 - 1, ln, 9, NC, R, gap=12, max_w=r.x1 - x - 1)

    name((259, 120, 306, 158), 264, ["두산위브", "더제니스", "오션시티"], 0x021A32)
    fill(p, (260, 161, 306, 182.5), 0x021A32)
    wb(p, 265.5, 180.2, "2813", 21, NUM, S, max_w=38)
    name((636, 120, 684, 158), 641, ["춘천", "중해마루힐", "포레스트"], 0x011A33)
    name((58, 258.5, 105.5, 297), 64, ["e편한세상", "에코델타", "센터포인트"], 0x001A35)
    name((259, 258.5, 306, 297), 264, ["에코델타시티", "푸르지오 린"], 0x011A33)
    name((451, 258.5, 503, 297), 456.5, ["강서자이", "에코델타"], 0x011A30)
    name((636, 258.5, 684, 297), 641, ["서면", "서한이다음"], 0x011B34)
    name((58, 397.5, 105.5, 437), 64, ["울산 유보라", "신천매곡"], 0x011A34)
    name((259, 397.5, 306, 437), 264, ["양산 5차", "비스타동원", "솔라스타"], 0x021A33)
    name((636, 397.5, 684, 437), 641, ["기장역 유림", "노르웨이숲", "센트럴"], 0x011A33)
    fill(p, (639, 439, 684, 462.5), 0x011A33)
    wb(p, 641, 460, "219", 21, NUM, S, max_w=38)
    fill(p, (262, 540, 717.5, 575), 0xF9F9F9)
    runs(p, 494.9, 557.6, [("2025년 기준 ", 13, DARK, R), ("12개 단지", 17, GOLD, B),
                           (", 총 11,613세대의 성공적인 사업 수행", 13, DARK, R)], align="center")
    log(26, "양정자이 2276→2272(NICE) / '두산위브 센트럴사하 2205'→'두산위브더제니스 오션시티 2,813'(NICE) / 춘천 휴에이드→중해마루힐 포레스트 / "
            "05·07 이름·세대수 뒤바뀜 정정(센터포인트 953 · 강서자이 856) / 푸르지오 린 / 삼한아르테→서한이다음 / 우정신경파크뷰→유보라 신천매곡 / "
            "덕계 동원비스타 5차→양산 5차 비스타동원 솔라스타 / 지웰 유림노르웨이숲 165→기장역 유림노르웨이숲 센트럴 219 / 캡션 10,189 → 11,613세대")


def p28(d):
    p = d[27]
    clear_all_text(p)
    bg_fill(p, (266, 103, 503, 146))
    W(p, 269.5, 124.6, "5개 단지 연속 수임", 32, 0xAC8753, B)
    rows = [197.6, 240.6, 284.2, 327.5, 370.8, 414.0, 457.9]
    new = ["사송 더샵 데시앙 1차 1,712세대", "사송 LH 신혼희망타운 2차 479세대", "사송 더샵 3차 533세대",
           "사송 제일풍경채 452세대", "사송역 우미린 포레스트 688세대"]
    for y, t in zip(rows, new):
        bg_fill(p, (246, y - 11, 482, y + 11))
        W(p, 249.2, y, t, 15.5, 0x20222C, R)
    bg_fill(p, (198, 396, 483, 477))
    W(p, 249.2, 420, "※ 5개 단지 · 3,864세대 (1차는 전신 사업체 실적)", 11, 0x6B7280, R)
    fill(p, (250, 541, 508, 558), 0x00142D)
    W(p, 253.2, 549.4, "전문성, 신뢰, 책임감을 바탕으로 최선의 가치를 제공합니다.", 12, 0xB3B7C2, R, max_w=252)
    log(28, "'90% 주관완료!' → '5개 단지 연속 수임' / '사송 데시앙 3차 672'(중복)·'사송 롯데캐슬(미확정)' 삭제 / 단지명 공식 표기 / "
            "'최고의 가치' → '최선의 가치'")


def p29(d):
    p = d[28]
    clear_all_text(p)
    fill(p, (252, 108, 569, 160), F.sample_bg(p, fitz.Rect(300, 105, 520, 108), ring=1.0))
    W(p, 254, 136.5, "5개 단지 연속 수임", 32, 0xC6A675, B)
    rows = [212.9, 264.0, 316.0, 367.4, 419.2, 470.4, 521.8]
    C = 0xC4C9D0

    def row(i, t):
        y = rows[i]
        bg_fill(p, (247, y - 10, 470, y + 10))
        W(p, 250, y, t, 14.8, C, R)

    row(0, "e편한세상 에코델타 센터포인트")
    row(2, "에코델타시티 푸르지오 린")
    star = BASE[28]
    bg_fill(p, (190, 394, 472, 444))
    copy_from(star, (193, 447, 236, 491), p, (193, 397.2, 236, 441.2))
    W(p, 250, rows[4], "디에트르 더 퍼스트", 14.8, C, R)
    bg_fill(p, (188, 446, 474, 546))
    log(29, "'90% 주관진행중!' → '5개 단지 연속 수임' / '중흥S클래스(미확정)'·'대방 엘리움(미확정)' 삭제 / 센터포인트·푸르지오 린·디에트르 더 퍼스트 공식 표기")


def p32(d):
    p = d[31]
    lst = [["온양발리 한양립스 더 퍼스트 442세대", "남천자이 913세대", "힐스테이트 포항 1717세대", "사상중흥S클래스 1572세대", "레이카운티 4470세대"],
           ["사송 LH 신혼희망타운 2차 479세대", "사송 더샵 3차 533세대", "사송 제일풍경채 452세대", "부산 드파인 센텀 750세대", "사송역 우미린 포레스트 688세대"],
           ["두산위브더제니스 오션시티 2813세대", "해운대역 푸르지오 더원 351세대", "연산포레 서희스타힐스 612세대", "힐스테이트 대연 센트럴 449세대", None]]
    lcol = [(226, 372), (436, 582), (652, 792)]
    lrow = [398, 418, 438, 457, 476]
    for c, items in enumerate(lst):
        for r, t in enumerate(items):
            if t is None:
                continue
            x0, x1 = lcol[c]
            clear_text(p, (x0, lrow[r] - 7, x1, lrow[r] + 7))
            F.patch(p, (x0, lrow[r] - 7, x1, lrow[r] + 7))
            W(p, x0 + 2 + (8 if c == 1 else 0), lrow[r], t, 8.8, 0x333333, R, max_w=x1 - x0 - 12)
    # AI 재생성 사진 6장(깨진 간판·아동 얼굴) → 본부장 제공 실사진
    slots = [((185.5, 140.5, 393.5, 246), "n60_brief_hs.jpg"), ((397.5, 140.5, 611.5, 246), "n60_brief_def.jpg"),
             ((615.5, 140.5, 821, 246), "n60_expo.jpg"), ((185.5, 250, 393.5, 356), "n03_draw.jpg"),
             ((397.5, 250, 611.5, 356), "n60_kids_cinema_c.jpg"), ((615.5, 250, 821, 356), "n03_crowd.jpg")]
    burn(p, [r for r, n in slots])
    for r, n in slots:
        photo(p, r, n)
    rt(p, (442, 541, 477, 559), "최선의", 13.2, color=0xE8E8E8, font=R, x=443)
    log(32, "행사리스트 표 9칸 SPEC·NICE 정정(오션시티 2205→2813 등) · 중산 한양립스(2022 행사)→연산포레 서희스타힐스 612 / "
            "AI 재생성 사진 6장(깨진 간판·아동 얼굴) → 실사진 6장 / '최고의 가치'→'최선의 가치'")


def p36(d):
    p = d[35]
    photo(p, (193, 180.5, 816.5, 512.5), "g14_plaque.jpg")
    log(36, "AI 감사패 진열장 이미지 → 실제 본사 감사패 진열장 사진(g14_plaque)")


# ------------------------------------------------------------------ 2·3파트(사실 관계만, 과장표현은 유지)
def p54(d):
    p = d[53]
    clear_text(p, (200, 140, 470, 165))
    bg_fill(p, (203, 142, 470, 162), smooth=20)
    runs(p, 206, 152, [("협약 시 ", 11.5, 0x6B6B6B, R), ("이행(지급)보증증권 제출", 11.5, 0xA9802F, B),
                       (" · 최대 10억 범위, 금액은 협약 때 확정", 11.5, 0x6B6B6B, R)])
    clear_text(p, (250, 268, 430, 312))
    bg_fill(p, (250, 270, 428, 310), smooth=20)
    W(p, 339, 289.5, "최대 10억원", 34, 0x0B1E3F, B, align="center")
    sgi = doc_png(EV["sgi"], 0, masks=[(186, 149, 262, 164), (150, 710, 292, 722), (165, 724, 280, 737)])
    place(p, (543, 183, 802, 552), sgi, pad=3)
    W(p, 672.5, 566, "보증증권 발급 이력 · SGI서울보증 계약보증보험증권(2026.09 · 타 용역 · 가입금액 7억 400만원)", 7,
      0x4A4F5A, R, align="center", max_w=300)
    log(54, "'이행 보증보험 가입!'(가입 이력 없음) → '협약 시 이행(지급)보증증권 제출 · 최대 10억 범위, 금액은 협약 때 확정' / '2년 10억원' → '최대 10억원' / "
            "견본 SGI 이행보증증권(2021.03, 법인 설립 전 날짜) → 실제 SGI 계약보증보험증권(증권번호 뒷자리·모집인 정보 가림) + '발급 이력' 캡션")


def p65(d):
    p = d[64]
    pill(p, (380, 243, 448, 258), "양식 예시", 8.5, fg=0xFFFFFF, bg=0x6B7280)
    fill(p, (482, 364, 645, 600), F.sample_bg(p, fitz.Rect(470, 380, 480, 560), ring=1.0))
    W(p, 560, 452, "하자 예치금은", 11, 0x0B1E3F, B, align="center")
    W(p, 560, 468, "협약 시 금액을 정해", 11, 0x0B1E3F, B, align="center")
    W(p, 560, 484, "예치합니다.", 11, 0x0B1E3F, B, align="center")
    rt(p, (540, 338, 708, 359), " ", 12, color=0x333333)
    runs(p, 543, 348.5, [("협약 시 ", 12, 0x3A3F4A, R), ("예치금으로 진행", 12, 0xB0874A, B), ("합니다", 12, 0x3A3F4A, R)])
    rt(p, (676, 398, 776, 488), ["협약 시", "하자 예치금", "설정", "(금액 협의)"], 15, color=0xFFFFFF, font=B,
       align="center", x=726, gap=19, fill_color=F.sample_bg(p, fitz.Rect(690, 400, 760, 486), ring=1.0))
    log(65, "'협약식과 동시에 1억 예치금 거치'·'예치금으로 진행하고 있습니다'(근거 없음) → '협약 시 하자 예치금 설정(금액 협의)' / "
            "하자보수이행각서 '양식 예시' 표기 / 예치금 계약서 이미지(실물 미확인) 삭제")


def p71(d):
    p = d[70]
    rt(p, (328, 240, 522, 288), ["행사 기간 사고·화재·상해에 대비해 영업(주최자)배상",
                                 "책임보험에 가입할 예정이며, 협약 시 증권 사본을", "제출합니다."], 8.6, color=0x3A3F4A, font=R, x=331, gap=14)
    log(71, "'영업배상 책임보험으로 안전사고에 대비합니다'(가입 이력 없음, 현재형) → '가입할 예정 · 협약 시 증권 사본 제출'")


def p93(d):
    p = d[92]
    hidden_replace(p, "MOU협력", "협력")
    log(93, "텍스트층 '화재 보험사 MOU협력'(MOU 실물 미확인) → '화재 보험사 협력'(화면 문구 'MD대면'은 그대로)")


def p97(d):
    p = d[96]
    for s in [s for b in p.get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"] if "건설면허" in s["text"]]:
        clear_text(p, fitz.Rect(s["bbox"]))
    rt(p, (357, 287, 437, 311), ["건축 분야", "특급기술자 지원"], 7.2, color=0x2B2F38, font=B, align="center", x=397, gap=10.5)
    log(97, "'건설업체(텍스트층 건설면허) 특급기술 인력지원' → '건축 분야 특급기술자 지원'(건설업 등록 없음)")


def p98(d):
    p = d[97]
    for s in [s for b in p.get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"] if "건설면허" in s["text"]]:
        clear_text(p, fitz.Rect(s["bbox"]))
    rt(p, (378, 320, 500, 335), "건축 분야 특급기술자 지원", 9.2, color=0x2B2F38, font=B, align="center", x=439)
    log(98, "'건설업체(텍스트층 건설면허) 특급기술 인력지원' → '건축 분야 특급기술자 지원'")


def p111(d):
    p = d[110]
    burn(p, [(240, 210, 410, 296)])
    fill(p, (240, 210, 410, 296), F.sample_bg(p, fitz.Rect(240, 210, 410, 296), ring=1.0))
    W(p, 400, 230, "조경 설계 · 감리 · 자문 협력사", 10.5, 0x0B1E3F, B, align="right")
    W(p, 400, 248, "Landscape architecture Design Group P&S", 7.5, 0x6B7280, R, align="right")
    W(p, 400, 278, "담당자 연락처는 협약 단계에서 안내합니다.", 7.5, 0x6B7280, R, align="right")
    log(111, "협력사 대표 명함(성명·휴대폰·메일·주소) 가림 → '조경 설계·감리·자문 협력사' 표기")


def p128(d):
    p = d[127]
    bg_fill(p, (248, 232, 410, 304))
    W(p, 329, 258, "조식 전문업체", 21, 0x0B1E3F, B, align="center")
    W(p, 329, 284, "컨택 · 운영 컨설팅 지원", 12, 0xA9802F, B, align="center")
    body = [((286, 404, 361, 452), ["업체별 메뉴 개발", "역량을 비교·검토해", "영양 균형 잡힌 식단을", "제안받습니다."]),
            ((421, 404, 494, 444), ["배송·보관 체계를", "사전에 확인해 신선한", "운영을 지원합니다."]),
            ((421, 492, 490, 533), ["식자재 구매 조건을", "비교해 합리적인", "단가를 협의합니다."])]
    for r, ln in body:
        rt(p, r, ln, 5.9, color=0x6B6B6B, font=R, gap=9.2)
    log(128, "'아워홈 OURHOME' 로고·수치(130명 연구원·업계 No.1·1,500여 협력사, 제휴 근거 없음) 삭제 → '조식 전문업체 컨택 · 운영 컨설팅 지원'")


def p147(d):
    p = d[146]
    hidden_replace(p, "임예협 업무지원", "입예협 업무지원")
    rt(p, (276, 453, 358, 473), "입예협 업무지원", 12.3, font=R, x=278)
    log(147, "'03 임예협 업무지원' → '입예협 업무지원'")


def p149(d):
    p = d[148]
    rt(p, (100, 278, 188, 291), "총회 및 협의회 활동지원", 6.9, color=0x222222, font=B, align="center", x=144)
    rt(p, (212, 278, 400, 291), "법무 검토 후 장소대관 · 현수막 · 도우미 지원", 6.9, color=0x444444, font=R, align="center", x=306)
    log(149, "05 '승진(총회) 및 편의회 활동지원 — … 상품권 등 제공'(금품 오해) → '총회 및 협의회 활동지원 — 법무 검토 후 장소대관·현수막·도우미 지원'")


def p150(d):
    p = d[149]
    rt(p, (78, 230, 172, 243), "총회 및 협의회 활동지원", 6.9, color=0x222222, font=B, align="center", x=125)
    rt(p, (208, 230, 382, 243), "법무 검토 후 장소대관 · 현수막 · 도우미 지원", 6.9, color=0x444444, font=R, align="center", x=295)
    rt(p, (505, 77, 562, 91), "법률 자문 연계", 7.2, color=0x222222, font=B, align="center", x=533.5)
    rt(p, (640, 77, 766, 91), "하자 소송 시 법률 자문 연계 지원", 7.2, color=0x444444, font=R, align="center", x=703)
    log(150, "05 상품권 제공 삭제(149쪽과 동일) / 08 '법무법인 협업 — 하자 소송 전문 대형 로펌 협업진행'(계약 근거 없음) → '법률 자문 연계 — 하자 소송 시 법률 자문 연계 지원'")


def p152(d):
    p = d[151]
    cols = [((205, 527, 345, 569), 209, "울산 본사 · 쇼룸", "울산 울주군 청량읍 온산로 615-1, 2·3층"),
            ((415, 527, 582, 569), 419, "부산 지사", "부산 해운대구 아르피나 B1"),
            ((640, 527, 822, 569), 643, "대전 지사", "디펠리체 204호 · 충청권 거점")]
    for r, x, a, b in cols:
        clear_text(p, r)
        fill(p, r, F.sample_bg(p, fitz.Rect(r), ring=1.0))
        W(p, x, 539, a, 10.5, 0xE3B97A, B)
        W(p, x, 557, b, 9.5, 0xD5DAE3, R, max_w=fitz.Rect(r).x1 - x - 3)
    runs(p, 573, 462, [("주관사업 총괄 본부장 윤현욱", 11, 0x0B1E3F, B), ("   010-7273-9901 · edgecompany1@naver.com", 11, 0x3A3F4A, R)],
         align="center")
    log(152, "주소 띠 '부산본사 / 울산지사 상남1길 28(구 주소) / 대전지사 롯데시네마 226호' → '울산 본사 · 쇼룸 온산로 615-1 2·3층 / 부산 지사 / 대전 지사 디펠리체 204호 · 충청권 거점'(본부장 10-15 정정: 디펠리체 204호 유지) + 대표 연락처")


FIXES = [p3, p5, p6, p8, p9, p11, p12, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24, p25, p26, p28, p29,
         p32, p36, p54, p65, p71, p93, p97, p98, p111, p128, p147, p149, p150, p152]


def main():
    global BASE, ASSET
    src, evd, ASSET, out = sys.argv[1:5]
    BASE = fitz.open(src)
    EV.update(elec=fitz.open(os.path.join(evd, "전기공사업_등록증.pdf")), iso=fitz.open(os.path.join(evd, "ISO_인증서.pdf")),
              sgi=fitz.open(os.path.join(evd, "SGI_계약보증보험증권_세종스마트시티_20260907.pdf")))
    d = fitz.open(src)
    only = os.environ.get("ONLY")
    for fx in FIXES:
        if only and fx.__name__ not in only.split(","):
            continue
        fx(d)
    d.delete_pages([n - 1 for n in DELETE])
    LOG.append(f"쪽 삭제(기본틀 PDF 쪽): {DELETE} — 7(2파트 38번 장이 1파트에 잘못 들어간 유튜브 '1.5만'·가짜 플레이 버튼), "
               "10(8번 장 중복·명부 개인정보), 27('25' 표기 2025 중복 장·허위 단지·소재지), 30('한 해 1만 세대 주관'·'최초 돌파'·'압도적 1위' 근거 없음)")
    d.set_metadata({"title": "엣지컴퍼니 회사 제안서(지명원) v6", "author": "주식회사 엣지컴퍼니"})
    d.save(out, garbage=3, deflate=True)
    print("saved", out, len(d), "pages", f"{os.path.getsize(out) / 1e6:.1f}MB")
    print("\n".join(LOG))


if __name__ == "__main__":
    main()
