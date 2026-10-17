# -*- coding: utf-8 -*-
"""엣지컴퍼니 입주박람회 주관사 협약서 — Word(.docx) 표준 양식 (본부장 10-17 지시).

근거
- 기존 협약서(드파인 센텀 2023.12 · 에코델타 센터포인트 2023.04 · 디에트르 2025.08 MOU체결서)의 조문 뼈대:
  목적 · 업무범위 · 보수 및 비용 · 위탁업무의 처리 · 계약 기간 · 계약의 해지 · 개인정보 · 분쟁해결 · 기타 · 특약사항.
- 현재 제안서(오산 · 분당 기본틀)의 약속을 조문으로: 4단계 공개 심사 · 가격 검수 · 최저가 차액 10배 · 계약금 10% 상한 ·
  취소 · 환불 규정 · 한 창구 A/S(24시간 회신 · 48시간 하자보수) · 선보상 · 하자 예치금 · 특약이행각서 · 패널티 3단계 ·
  발전지원(혜택 패키지, 협의회 선택) · 협의회 업무 지원 · 보고 · 개인정보 · 재위탁 금지.
- 단지마다 다른 값(단지명 · 세대수 · 금액 · 일정)은 【 】 칸(연한 금색 바탕)으로 두어 Word에서 바로 고친다.

사용: python3 build_agreement.py  → 엣지컴퍼니_입주박람회_주관사_협약서_양식.docx
"""
import os

from docx import Document
from docx.enum.section import WD_ORIENT  # noqa: F401
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "엣지컴퍼니_입주박람회_주관사_협약서_양식.docx")

NAVY = RGBColor(0x0D, 0x1E, 0x33)
GOLD = RGBColor(0x9A, 0x7B, 0x3F)
GRAY = RGBColor(0x5B, 0x66, 0x76)
FONT = "맑은 고딕"
FILL = "FBF4E3"   # 【 】 칸 바탕(연한 금색)
HEAD = "0D1E33"   # 표 머리글 바탕(남색)
SOFT = "F3F5F8"   # 표 항목 칸 바탕


# OOXML 자식 요소 순서(스키마) — python-docx가 먼저 넣은 요소 뒤에 덧붙이면 Word 검증에 걸리므로 정렬한다
_ORD = {
    "tcPr": ["cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd", "noWrap", "tcMar", "textDirection", "tcFitText", "vAlign", "hideMark"],
    "tblPr": ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize", "tblStyleColBandSize", "tblW", "jc", "tblCellSpacing", "tblInd", "tblBorders", "shd", "tblLayout", "tblCellMar", "tblLook"],
    "pPr": ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl", "numPr", "suppressLineNumbers", "pBdr", "shd", "tabs", "suppressAutoHyphens", "kinsoku", "wordWrap", "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd", "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc", "textDirection", "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr", "sectPr", "pPrChange"],
}


def _sort(el, kind):
    order = _ORD[kind]
    kids = list(el)
    kids.sort(key=lambda k: order.index(k.tag.split("}")[1]) if k.tag.split("}")[1] in order else 99)
    for k in kids:
        el.remove(k)
    for k in kids:
        el.append(k)


def fix_order(doc):
    body = doc.element.body
    for el in body.iter():
        tag = el.tag.split("}")[1] if "}" in el.tag else el.tag
        if tag in _ORD:
            _sort(el, tag)
    for part in (doc.sections[0].header, doc.sections[0].footer):
        for el in part._element.iter():
            tag = el.tag.split("}")[1] if "}" in el.tag else el.tag
            if tag in _ORD:
                _sort(el, tag)
    z = doc.settings.element.find(qn("w:zoom"))
    if z is not None and z.get(qn("w:percent")) is None:
        z.set(qn("w:percent"), "100")

# ------------------------------------------------------------------ 기본 도구
def set_font(run, size=10.5, bold=False, color=None, italic=False):
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if color is not None:
        run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.append(rf)
    for k in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(k), FONT)


def shade(cell, fill):
    tcpr = cell._element.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcpr.append(shd)


def cell_margins(cell, top=60, bottom=60, left=110, right=110):
    tcpr = cell._element.get_or_add_tcPr()
    mar = OxmlElement("w:tcMar")
    for k, v in (("top", top), ("bottom", bottom), ("start", left), ("end", right)):
        e = OxmlElement(f"w:{k}")
        e.set(qn("w:w"), str(v))
        e.set(qn("w:type"), "dxa")
        mar.append(e)
    tcpr.append(mar)


def table_borders(table, color="C9CED6", size=6, inside=True):
    tbl = table._element
    tblpr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for k in ("top", "left", "bottom", "right") + (("insideH", "insideV") if inside else ()):
        e = OxmlElement(f"w:{k}")
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), str(size))
        e.set(qn("w:space"), "0")
        e.set(qn("w:color"), color)
        borders.append(e)
    tblpr.append(borders)


def para(doc_or_cell, text="", size=10.5, bold=False, color=None, align=None, before=0, after=4, line=1.45, indent=0, keep=False):
    p = doc_or_cell.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line
    if indent:
        pf.left_indent = Cm(indent)
    if align:
        p.alignment = align
    if keep:
        pf.keep_with_next = True
    if text:
        add_runs(p, text, size=size, bold=bold, color=color)
    return p


def add_runs(p, text, size=10.5, bold=False, color=None):
    """【 】 안은 채움 칸(금색 바탕 · 굵게), **굵게** 표기 지원."""
    import re
    parts = re.split(r"(【[^】]*】|\*\*[^*]+\*\*)", text)
    for part in parts:
        if not part:
            continue
        if part.startswith("【"):
            r = p.add_run(part)
            set_font(r, size=size, bold=True, color=GOLD)
            rpr = r._element.get_or_add_rPr()
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear")
            shd.set(qn("w:color"), "auto")
            shd.set(qn("w:fill"), FILL)
            rpr.append(shd)
        elif part.startswith("**"):
            r = p.add_run(part[2:-2])
            set_font(r, size=size, bold=True, color=color)
        else:
            r = p.add_run(part)
            set_font(r, size=size, bold=bold, color=color)


def rule(doc, color="C8A86A", size=12, after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.space_before = Pt(0)
    ppr = p._element.get_or_add_pPr()
    bdr = OxmlElement("w:pBdr")
    b = OxmlElement("w:bottom")
    b.set(qn("w:val"), "single")
    b.set(qn("w:sz"), str(size))
    b.set(qn("w:space"), "1")
    b.set(qn("w:color"), color)
    bdr.append(b)
    ppr.append(bdr)
    return p


def page_number(paragraph):
    r = paragraph.add_run()
    set_font(r, size=8.5, color=GRAY)
    for tag, text in (("begin", None), (None, "PAGE"), ("end", None)):
        if tag:
            e = OxmlElement("w:fldChar")
            e.set(qn("w:fldCharType"), tag)
        else:
            e = OxmlElement("w:instrText")
            e.set(qn("xml:space"), "preserve")
            e.text = text
        r._element.append(e)


# ------------------------------------------------------------------ 문서 조립 단위
def chapter(doc, label, title):
    p = para(doc, before=14, after=2, keep=True)
    r = p.add_run(label + "  ")
    set_font(r, size=9, bold=True, color=GOLD)
    r = p.add_run(title)
    set_font(r, size=13, bold=True, color=NAVY)
    rule(doc, color="0D1E33", size=8, after=4)


def article(doc, no, title, items, note=None):
    """items: str(단일 항) 또는 [str, ...](①② 항) · 항 안 리스트는 (str, [호, ...]) 로 1. 2. 호를 붙인다."""
    p = para(doc, before=8, after=2, keep=True)
    r = p.add_run(f"제{no}조")
    set_font(r, size=10.5, bold=True, color=NAVY)
    r = p.add_run(f" ({title})")
    set_font(r, size=10.5, bold=True)
    if isinstance(items, str):
        items = [items]
    circ = "①②③④⑤⑥⑦⑧⑨⑩"
    for i, it in enumerate(items):
        sub = None
        if isinstance(it, tuple):
            it, sub = it
        p = para(doc, after=2, indent=0.35)
        p.paragraph_format.first_line_indent = Cm(-0.35)
        prefix = (circ[i] + " ") if len(items) > 1 else ""
        add_runs(p, prefix + it)
        if sub:
            for j, s in enumerate(sub, 1):
                q = para(doc, after=1, indent=0.95, size=10)
                q.paragraph_format.first_line_indent = Cm(-0.45)
                add_runs(q, f"{j}. {s}", size=10)
    if note:
        q = para(doc, after=2, indent=0.35, size=9, color=GRAY)
        add_runs(q, "※ " + note, size=9, color=GRAY)


def kv_table(doc, rows, widths=(3.2, 13.8), head=None):
    t = doc.add_table(rows=0, cols=2)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    table_borders(t)
    if head:
        row = t.add_row()
        c = row.cells[0].merge(row.cells[1])
        shade(c, HEAD)
        cell_margins(c)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(head)
        set_font(r, size=10, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF))
    for k, v in rows:
        row = t.add_row()
        a, b = row.cells
        a.width, b.width = Cm(widths[0]), Cm(widths[1])
        shade(a, SOFT)
        cell_margins(a)
        cell_margins(b)
        p = a.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(k)
        set_font(r, size=9.5, bold=True, color=NAVY)
        p = b.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        add_runs(p, v, size=10)
    return t


def grid_table(doc, header, rows, widths, size=9.5):
    t = doc.add_table(rows=1, cols=len(header))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    table_borders(t)
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]
        c.width = Cm(widths[i])
        shade(c, HEAD)
        cell_margins(c, 50, 50)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        set_font(r, size=size, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF))
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            c = cells[i]
            c.width = Cm(widths[i])
            cell_margins(c, 50, 50)
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            if i == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                shade(c, SOFT)
            add_runs(p, v, size=size, bold=(i == 0))
    return t


# ------------------------------------------------------------------ 본문
def build():
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.top_margin, sec.bottom_margin = Cm(2.2), Cm(2.0)
    sec.left_margin, sec.right_margin = Cm(2.0), Cm(2.0)
    sec.header_distance, sec.footer_distance = Cm(1.0), Cm(1.0)

    # 기본 글꼴
    st = doc.styles["Normal"]
    st.font.name = FONT
    st.font.size = Pt(10.5)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)

    # 머리글 · 바닥글
    hp = sec.header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = hp.add_run("입주박람회 주관사 협약서  ·  주식회사 엣지컴퍼니")
    set_font(r, size=8.5, color=GRAY)
    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = fp.add_run("- ")
    set_font(r, size=8.5, color=GRAY)
    page_number(fp)
    r = fp.add_run(" -")
    set_font(r, size=8.5, color=GRAY)

    # ---- 표지 머리
    p = para(doc, before=28, after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
    r = p.add_run("AGREEMENT  ·  주식회사 엣지컴퍼니")
    set_font(r, size=9, bold=True, color=GOLD)
    p = para(doc, after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
    r = p.add_run("입주박람회 주관사 협약서")
    set_font(r, size=24, bold=True, color=NAVY)
    p = para(doc, after=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    r = p.add_run("공동구매 및 입주박람회 기획 · 진행 위탁 협약")
    set_font(r, size=12, color=GRAY)
    rule(doc, after=12)

    p = para(doc, after=10, line=1.6)
    add_runs(p, "【단지명】 입주예정자협의회(이하 ‘협의회’)와 주식회사 엣지컴퍼니(이하 ‘주관사’)는 【단지명】(이하 ‘아파트’) "
                "입주예정자의 공동구매 및 입주박람회 기획 · 진행 위탁(이하 ‘위탁업무’)에 관하여 다음과 같이 협약을 체결한다.")

    kv_table(doc, [
        ("협 약 명", "【단지명】 입주박람회 주관사 협약"),
        ("아 파 트", "【단지명】 · 【세대수】세대 · 【주소】 · 입주 예정 【입주 연월】"),
        ("협 의 회", "【단지명】 입주예정자협의회 · 대표 【성명】 · 공식 카페 【카페 주소】"),
        ("주 관 사", "주식회사 엣지컴퍼니 · 대표이사 고진식 · 사업자등록번호 508-81-42798 · 울산광역시 울주군 청량읍 온산로 615-1"),
        ("근      거", "주관사 선정 공고(【공고일】) · 주관사 제안서(【제출일】) · 선정 통지(【선정일】)"),
        ("협약 기간", "협약 체결일부터 아파트 입주 후 1년이 되는 날까지(제5조)"),
    ], head="협약 개요")

    # ---- 제1장 총칙 (기존 1 ~ 6조)
    chapter(doc, "제 1 장", "총칙")
    article(doc, 1, "목적", "이 협약은 협의회와 주관사 간의 위탁업무에 관한 전반적인 사항을 정하여, 아파트 입주예정자가 공정한 가격과 확실한 사후관리로 "
                            "입주를 준비할 수 있도록 함을 목적으로 한다.")
    article(doc, 2, "업무 범위", [
        ("협의회가 주관사에 위탁하는 업무는 다음 각 호와 같다.", [
            "아파트의 공동구매 및 입주박람회의 기획 · 진행",
            "공동구매 품목 수요조사 · 참여업체 모집 · 심사 · 계약 및 납품 · 시공 일정 관리",
            "공동구매 단가의 검수(시중가 · 온라인 최저가 비교) 및 사전 공개",
            "주관 콜센터 등 A/S · 하자 · 민원 창구 운영과 참여업체 하자보수 관리",
            "사전점검 · 정당계약 · 입주 행사 등 협의회 행사 지원 및 공식 카페 홍보 콘텐츠 제작",
            "주관사가 제출한 제안서에 명시된 업무",
        ]),
        "제안서의 내용은 이 협약의 조건으로 하며, 제안서와 이 협약이 다를 때에는 이 협약이 우선한다.",
    ])
    article(doc, 3, "보수 및 비용", [
        "협의회는 이 협약 이행에 대한 보수를 주관사에 지급하지 않으며, 비용 일체는 주관사가 부담한다.",
        "주관사는 참여업체로부터 받는 박람회 참가비를 정액으로 정하고, 이를 공동구매 단가와 연동하지 않는다.",
        "주관사는 협의회 또는 회원에게 어떠한 명목으로도 비용을 청구하지 않는다.",
    ])
    article(doc, 4, "위탁업무의 처리", [
        "주관사는 위탁업무에 대하여 신의 · 성실의 의무를 다하여야 한다.",
        "주관사는 제안서에 명시된 위탁업무에 적극적으로 임하여야 한다.",
        "주관사가 협의회의 협조를 원하는 경우 협의회는 성공적인 위탁업무 완료를 위하여 수요조사 · 공지 게시 · 참여업체 심사 · 행사 일정 조정에 협조한다.",
        "위탁업무 처리 과정에서 주관사의 명백한 귀책사유가 발생한 경우 주관사는 사후 조치 및 보완에 적극적으로 임하여야 한다.",
        "주관사는 정당한 사유 없이 협의회의 위탁업무를 거부할 수 없다.",
        "주관사는 협의회 정례회의마다 업무 진행 상황을 보고하고, 박람회 종료 후 30일 이내에 결과보고서를, 협약 종료 시 A/S 처리 현황을 담은 최종 보고서를 제출한다.",
    ])
    article(doc, 5, "협약 기간", [
        "이 협약의 기간은 협약 체결일부터 아파트 입주 후 1년이 되는 날(【연월일】)까지로 한다.",
        "협약 기간 종료 전에 공동구매 계약을 체결한 회원에 대하여는 해당 계약의 이행 · 보증 기간이 끝날 때까지 이 협약의 효력이 유지된다.",
        "아파트의 입주자대표회의가 제1항의 종료일 전에 구성된 경우 협의회의 권리 · 의무는 협의회가 정하는 바에 따라 입주자대표회의가 승계할 수 있다.",
    ])
    article(doc, 6, "협약의 해지", [
        ("협의회 또는 주관사는 다음 각 호의 어느 하나에 해당하는 사유가 발생한 경우 이 협약의 전부를 해지할 수 있다.", [
            "현행 법령 및 협의회 규정상의 제한 사유에 해당하는 경우",
            "주관사의 과실로 인하여 협의회 또는 회원에게 중대한 손해가 발생한 경우",
            "협의회와 주관사의 협의하에 이 협약을 파기하는 경우",
            "이 협약의 각 조항을 위배한 경우 · 제안서에 허위 사실이 확인된 경우",
        ]),
        "해지 사유의 발생으로 협의회가 협약을 해지하고자 하는 경우 사전에 주관사에 일정 기한을 정하여 서면으로 시정을 요구하여야 하며, 그 기간 안에 시정되지 않으면 해지할 수 있다.",
        "협의회가 불가피한 사유로 협약을 해지하고자 하는 경우에는 주관사와 협의하여야 한다.",
        "협약의 해지는 그 의사표시를 적은 서면이 상대방에게 도달한 날부터 15일 후에 효력이 발생한다.",
        "해지된 경우에도 이미 체결된 회원의 공동구매 계약은 유효하며, 주관사는 협의회가 지정하는 업체에 하자보수 · A/S 업무를 인계할 때까지 그 책임을 진다.",
    ])

    # ---- 제2장 공동구매 (기존 7 ~ 14조)
    chapter(doc, "제 2 장", "공동구매 · 참여업체 · 가격")
    article(doc, 7, "물품의 공급", [
        ("주관사는 다음 각 호와 같이 협의회가 필수로 공급을 요청한 품목을 공급하여야 한다.", [
            "인테리어 : 중문, 방충망(미세 · 안전), 방범창, LED조명, 시스템선반, 커튼, 블라인드",
            "홈케어 : 단열필름, 새집증후군, 입주청소, 줄눈, 탄성코트, 유리막코팅 등",
            "생활 : 가전, 가구, 시스템에어컨, 음식물처리기, 인덕션, 렌탈서비스",
            "기타 : 포장이사, 사전점검 대행, 【협의회 추가 품목】",
        ]),
        "주관사는 협의회와 협의하여 추가로 결정된 품목을 공급할 수 있으며, 품목 수와 품목당 업체 수는 회원 수요조사 결과와 협의회 승인으로 정한다.",
        "분양 당시 유상옵션 · 기본 제공 품목과 겹치는 품목은 수요조사로 확인한 뒤 남은 수요에 한하여 모집한다.",
        "물품 공급에 참여하는 참여업체에 대하여는 주관사와 참여업체 간에 물품 공급 · 하자보수에 관한 계약 또는 각서를 맺어야 한다.",
    ])
    article(doc, 8, "참여업체의 선정", [
        "주관사는 참여업체를 공개 모집하고, 서류 심사 → 현장 · 제품 확인 → 단가 검수 → 협의회 최종 승인의 4단계 공개 심사로 선정한다. 최종 확정은 협의회가 한다.",
        "개별 업체의 제안 접수는 협의회와 공유할 수 있는 이메일로 받는다.",
        "시공 품목은 아파트 인근 지역 업체를 우선 선정하여 신속한 A/S가 가능하도록 한다.",
        "참여업체는 참여 전에 【별첨 3】 특약이행각서와 하자보수 이행각서를 제출하여야 하며, 제출하지 않은 업체는 박람회에 참여할 수 없다.",
        ("다음 각 호의 어느 하나에 해당하는 업체는 선정에서 배제한다.", [
            "단순 유통 마진을 취하기 위하여 재하도급하는 업체",
            "타 단지 공동구매 참여 과정에서 입주민과의 분쟁 · 불만 사례가 상당수 접수된 업체",
            "주관사가 관리 · 감독할 수 없는 업체",
        ]),
    ])
    article(doc, 9, "참여업체의 교체와 제재", [
        ("주관사가 선정한 참여업체에 다음 각 호의 사유가 발생한 경우 즉시 교체하여야 한다.", [
            "협의회의 불만에 대한 시정 조치 요구에 응하지 않는 경우",
            "회원의 불만이 지속적 또는 상당수 발생하는 경우",
            "위탁업무 수행에 있어 협의회가 부적격하다고 판단하는 경우",
            "실제 공급한 물품의 모델 · 규격 · 사양 · 수량 · 가격 · 재료가 홍보 물품과 다른 경우",
            "계약서 · 제안서 · 제안요청서 등 협의회가 요구하는 사항을 이행하지 않거나 시정하지 않는 경우",
        ]),
        "불이행 참여업체에는 1단계 홍보정지, 2단계 계약 총액의 10% 배상, 3단계 참여 자격 박탈 및 협의회 승인을 받은 계약 이관의 제재를 차례로 부과한다.",
    ])
    article(doc, 10, "거래의 방식과 가격", [
        "공동구매 물품의 거래는 회원과 참여업체 간의 직거래를 원칙으로 한다.",
        "주관사는 박람회 전에 품목별 공동구매 단가 · 할인율 · 모델코드를 시중가 · 온라인 최저가와 같은 조건의 총액(제품 · 설치 · 철거 · 배송 · A/S 포함)으로 비교하여 협의회의 검수를 받고, 검수를 마친 단가를 회원에게 사전 공개한다.",
        "박람회장 · 온라인 박람회의 가격은 사전 공개한 단가와 같아야 하며, 현장에서 가격을 올리거나 바꿀 수 없다. 결제 방식에 따른 단가 차이를 두지 않는다.",
        "공동구매 품목과 브랜드 · 모델명이 같은 새 제품이 계약 후 7일 이내에 아파트 인근(【지역 범위】) 오프라인 매장에서 더 낮은 정상 판매가로 판매된 사실이 확인되면 참여업체는 차액의 10배를 보상하고 판매가를 조정한다. 온라인 · 홈쇼핑 판매, 시공 품목, 카드 청구할인 · 사은품 · 결합할인, 전시 · 리퍼, 법인 특판, 한정 수량 행사가는 비교 대상에서 제외한다.",
    ])
    article(doc, 11, "납품 및 시공", [
        "참여업체는 회원과 계약을 체결할 때 시공(납품) 예정일을 고지하여야 한다.",
        "참여업체는 시공(납품) 예정일을 고지하지 않거나 일방적으로 변경할 수 없으며, 이로 인한 회원의 계약 취소 요청이 있으면 반드시 응하고 납부 금액 전액을 환불하여야 한다.",
        "시공(납품) 예정일의 연기에 대하여 참여업체와 회원 간 사전 협의 · 동의가 있는 경우에는 제2항의 예외로 한다.",
        "주관사는 참여업체의 납품 · 시공 · 설치 일정을 관리하고, 회원에게 사전 해피콜로 일정을 확인한다.",
    ])
    article(doc, 12, "물품의 홍보", [
        "참여업체가 협의회 또는 주관사가 정한 기준을 위배한 홍보 행위를 한 경우 제9조의 제재를 가한다.",
        "물품 구매에 따른 특약 사항(무상 A/S 기간 · 취소 기한 · 제외 조건)은 홍보 시 반드시 표기하여야 한다.",
        "협의회 공식 카페 · 공지 채널에 게시하는 안내문 · 카드뉴스 · 영상은 주관사가 제작하되 게시 전에 협의회의 승인을 받으며, 주관사는 협의회의 사전 동의 없이 아파트 · 협의회의 명칭을 외부 홍보에 사용하지 않는다.",
    ])
    article(doc, 13, "대금의 결제", [
        "계약금은 공급가의 【10】%를 초과할 수 없다. 다만 전액 선결제를 요하는 품목(렌탈 · 보험 · 통신 등 본사 규정 품목)은 계약 전 서면 고지를 조건으로 예외로 한다.",
        "대금은 신용(체크)카드 결제가 가능하여야 하며, 현금 거래 시 세금계산서 또는 현금영수증을 발급하여야 한다. 결제 방식을 이유로 사전에 제시한 금액의 인상을 요구할 수 없다.",
        "잔금의 결제는 시공 · 설치가 끝나고 회원의 검수가 완료된 이후에 하며, 하자 · 미시공 부분이 있으면 그 보수가 끝난 후 지급할 수 있다.",
        "참여업체가 대금을 계좌이체로 받을 경우 사전에 협의회에 제출 · 확인된 계좌에 한하여 허용한다.",
    ])
    article(doc, 14, "대금의 취소 · 환불", [
        "계약 및 구매 물품의 취소 · 환불은 【별첨 2】 계약 취소 · 환불 규정에 따르고, 규정에 없는 사항은 공정거래위원회 고시 소비자분쟁해결기준을 따른다. 주관사는 이 규정을 모든 공동구매 계약서에 첨부하고 박람회장 · 온라인 박람회에 게시한다.",
        "품목별 취소 가능 기한 안에 취소하면 납부한 금액 전액을 환불하고, 참여업체 귀책으로 해지하는 경우에는 기한과 관계없이 전액을 환불한다. 참여업체 귀책에 따른 환불에서는 제품 제작에 든 비용 등을 공제할 수 없다.",
        "환불금은 취소 확정일부터 3영업일 이내에 지급하고 카드 결제분은 같은 기한 안에 승인 취소하며, 주관사는 환불 완료 여부를 회원에게 확인(해피콜)한다.",
        "참여업체가 환불을 지연 · 거부하면 주관사는 사실 확인 후 회원에게 먼저 보상하고 참여업체와는 별도로 정산한다. 이 조로 발생하는 분쟁에 주관사는 적극 개입하여 해결한다.",
    ])

    # ---- 제3장 하자보수 · 민원 · 박람회 (기존 15 ~ 17조)
    chapter(doc, "제 3 장", "하자보수 · 민원 · 입주박람회")
    article(doc, 15, "하자보수 처리 및 보증", [
        "하자보수는 접수 후 24시간 이내에 1차 회신하고 48시간 이내 처리를 원칙으로 하며, 회원의 동의에 따라 연장할 수 있다. 방문 시간은 회원이 원하는 시간으로 한다.",
        "참여업체의 무상 A/S 기간은 최소 2년(업체 · 품목별 상이)으로 하고 그 기간을 공동구매 계약서에 명시하며, 참여업체는 회원의 보증 요청 시 하자보수를 실시하여야 한다.",
        "참여업체가 하자보수에 응하지 않으면 주관사가 사실 확인 후 회원에게 먼저 보상(선보상)하고 참여업체와는 별도로 정산한다. 참여업체가 폐업 · 도산하거나 연락이 끊긴 경우 주관사는 동종업체로 사후관리를 이관하고 그 A/S 비용을 전액 부담한다.",
        "주관사는 선보상 재원으로 하자 예치금 금 【금액】원을 주관사 자산으로 【예치 방법 · 예치처】에 예치하고 참여업체로부터 예치금 · 보증금을 받지 않으며, 사용 내역을 협의회에 공개한다. 예치 · 지급 · 반환은 【별첨 4】 예치금 약정에 따른다.",
        "주관사는 협의회를 피보험자로 하는 협약이행보증증권 · 하자보증증권(보증 기간 【12】개월 이상 · 보증 금액 금 【금액】원)을 협약 체결일부터 【 】일 이내에 발급하여 제출한다. 증권의 종류 · 금액 · 기간은 협의회와 협의하여 정하며, 협의회가 요구하지 않는 경우 제4항의 예치금으로 갈음할 수 있다.",
    ], note="보증 금액 · 기간은 공고 조건과 보증보험 발급 한도를 확인한 뒤 적는다. 발급 전에는 금액을 약속하지 않는다.")
    article(doc, 16, "민원 서비스의 제공", [
        "주관사는 회원을 대상으로 공동구매에 관한 전반적인 문의 · A/S · 하자 · 민원을 한 창구(주관 콜센터 【전화】 · 협의회 공식 카페 신문고 · 카카오채널)에서 접수한다.",
        "주관 창구는 협약 기간(입주 후 1년) 동안 운영하며, 접수 · 처리 · 지연 사유를 기록하여 협의회에 정기 보고한다.",
        "시행 · 시공사(건설사) 하자는 주관사가 접수를 대행하고 회신을 추적하여 보고하며, 공동구매 납품 · 시공 하자와 책임을 구분하여 처리한다.",
    ])
    article(doc, 17, "입주박람회 개최", [
        "주관사는 수분양자를 대상으로 1회 이상의 입주박람회를 개최하여야 한다. 시기는 입주 【2 ~ 3】개월 전, 금 · 토 · 일 【3】일을 원칙으로 하되 일정 · 장소 · 부스 배치는 사전점검 일정에 맞추어 협의회와 협의하여 확정한다.",
        "주관사는 안내데스크 · 협의회 부스 · 카페테리아 · 어린이 놀이방 · 수유실 · 휴게 공간 등 편의시설과 운영 인력을 갖추고, 개최 전에 안전계획(미아 방지 · 대피로 · 부스 전기 점검 · 혼잡 시 입장 조절 · 구급 · 보안)을 협의회에 제출한다.",
        "주관사는 협의회가 요청하면 박람회 기간에 맞추어 행사주최자배상책임보험에 가입하고 증권 사본을 제출한다.",
        "박람회에 오지 못하는 회원을 위하여 회원만 입장하는 온라인 박람회(폐쇄몰)를 운영하며, 온라인 박람회의 가격 · 조건은 박람회장과 같다.",
    ])

    # ---- 제4장 책임 · 의무 (기존 18 ~ 23조)
    chapter(doc, "제 4 장", "책임과 의무")
    article(doc, 18, "책임", [
        ("주관사는 위탁사업을 진행함에 있어 다음 각 호의 책임을 가지며, 각 호의 상세 내용은 제안서를 따른다.", [
            "참여업체의 관리 및 감독의 책임", "위탁사업 계약의 책임", "하자보수의 책임", "분쟁 해결의 책임",
            "입주박람회 개최의 책임", "청렴결백의 의무", "참여업체와의 상생협력",
        ]),
    ])
    article(doc, 19, "제안요청서 · 제안서 준수", "주관사는 이 협약 체결 전 협의회가 입찰을 위하여 공고한 제안요청서(공고)와 주관사가 제출한 제안서의 내용을 준수하여야 한다. "
                                           "제안서의 조건은 PT · 협약에서 바꾸거나 줄이지 않으며, ‘(안)’으로 제안한 항목은 참여업체 확정 후 협의회 승인으로 확정한다.")
    article(doc, 20, "권리 · 의무의 양도 및 재위탁 금지", [
        "주관사는 이 협약과 관련된 권리나 의무를 협의회의 서면 승인 없이 제3자에게 양도할 수 없다.",
        "주관사는 위탁업무의 전부 또는 주요 부분을 제3자에게 재위탁하지 않는다. 다만 자문 · 촬영 등 전문 업무의 외부 협력은 재위탁으로 보지 않는다.",
    ])
    article(doc, 21, "신의 · 성실 및 청렴", [
        "협의회와 주관사는 신의 · 성실의 원칙에 입각하여 상호 협조와 신뢰로써 이 협약을 성실히 준수하고 공동 발전을 위하여 노력한다.",
        "주관사는 참여업체와 담합하거나 참여업체 · 회원으로부터 금품 · 향응을 받지 않으며, 참여업체 선정에서 특정 업체를 부당하게 우대하지 않는다.",
    ])
    article(doc, 22, "손해배상", [
        ("다음 각 호의 사유로 협의회에 손해가 발생하여 협의회가 손해배상을 청구하는 경우 주관사는 지체 없이 이에 응하여야 한다.", [
            "주관사의 고의 또는 과실로 인하여 위탁업무의 하자가 발생한 경우",
            "이 협약의 조건 위반으로 협의회에 손해가 발생하거나 객관적으로 확실시되는 경우",
        ]),
        "천재지변 등 불가항력으로 인한 경우에는 그러하지 아니하며, 양 당사자는 협의하여 일정 · 조건을 조정한다.",
    ])
    article(doc, 23, "비밀유지 · 개인정보 보호", [
        "주관사는 회원의 개인정보를 비밀로 취급하여야 하며, 협의회의 승인 없이 제3자에게 열람 · 제공 · 누설할 수 없다.",
        "주관사가 위탁업무 수행상 필요하거나 법령에 따라 공개가 요구되는 경우에는 제1항의 예외로 하되, 그 사실을 협의회에 알린다.",
        "회원의 개인정보는 박람회 · 공동구매 운영 목적 외에 사용하지 않으며, 참여업체에 제공하는 정보는 계약 이행에 필요한 범위로 한정한다.",
        "이 조의 위반으로 협의회 또는 회원에게 손해가 발생한 경우 주관사는 이를 배상한다.",
        "협약 종료 시 협의회 또는 회원이 제공한 개인정보 등은 즉시 파기하고, 파기 결과를 협의회에 통지한다.",
    ])

    # ---- 제5장 기타 (기존 24 ~ 26조)
    chapter(doc, "제 5 장", "기타")
    article(doc, 24, "분쟁 해결", "이 협약에 명시되지 않은 사항 또는 이 협약의 이행에 대한 해석에 이의가 있을 때에는 상호 간의 합의에 따라 원만히 해결하며, "
                                "합의가 이루어지지 않을 때에는 협의회의 소재지를 관할하는 법원을 관할 법원으로 하여 분쟁을 해결한다.")
    article(doc, 25, "기타 사항", [
        "이 협약의 이행에 있어 협의회가 인정한 불가피한 사유가 발생한 경우에는 협의회와 주관사가 충분히 협의하여 조정할 수 있다.",
        "이 협약의 변경은 양 당사자가 서면으로 합의한 경우에만 효력이 있다. 다만 【별표 1】의 지원 항목은 같은 금액 범위 안에서 협의회 정례회의 의결과 주관사의 서면 확인으로 바꿀 수 있다.",
        "이 협약의 성립을 증명하기 위하여 협약서 2부를 작성하여 기명 날인한 후 각 1부씩 보관한다.",
        "이 협약은 쌍방의 서명 또는 날인일부터 효력이 발생한다.",
    ])
    article(doc, 26, "특약 사항", [
        "주관사는 협약 기간 동안 금 【금액】원 상당(【세대수】세대 · 세대당 약 【금액】원)의 발전지원을 제공한다. 지원 항목은 【별표 1】의 예시(A 입주민 특화서비스 · B 협의회 업무지원 · C 단지지원 컨설팅) 중에서 협의회가 고르거나, 같은 금액 범위 안에서 협의회가 필요한 항목으로 바꾸어 정하며, 확정 항목은 【별표 1】에 적는다.",
        "지원 항목은 주관사가 직접 구매 · 제공(전기 · 조명은 직접 시공)하고 집행 내역을 협의회에 공개한다. 지원 비용은 주관사가 부담하며 참여업체 참가비 · 공동구매 단가에 전가하지 않는다.",
        "방문 선물 · 사은품 · 경품 · 정회원 혜택은 제1항의 범위 안에서 협의회와 협의하여 배분하고, 참여업체가 제공하는 박람회 상품권 · 현장 할인은 협의회 승인 후 확정한다.",
        "그 밖의 특약은 【별표 1】에 적으며, 별표는 이 협약의 일부로서 본문과 같은 효력을 가진다.",
    ], note="공고가 공용부 기증 · 기금을 제한하는 단지는 세대 혜택 · 협의회 업무 지원 항목으로만 구성한다.")

    # ---- 서명란 (날짜 + 서명표를 한 표로 묶어 쪽이 갈리지 않게)
    p = para(doc, before=16, after=10, align=WD_ALIGN_PARAGRAPH.CENTER, keep=True)
    add_runs(p, "【20    】년  【   】월  【   】일", size=12, bold=True)
    t = doc.add_table(rows=1, cols=2)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    table_borders(t, color="0D1E33", size=8, inside=True)
    row = t.rows[0]
    for i, (who, rows) in enumerate([
        ("협 의 회", [("단 체 명", "【단지명】 입주예정자협의회"), ("주      소", "【주소】"), ("카페 주소", "【카페 주소】"), ("대      표", "【성명】                    (인)")]),
        ("주 관 사", [("상      호", "주식회사 엣지컴퍼니"), ("사업자번호", "508-81-42798"), ("주      소", "울산광역시 울주군 청량읍 온산로 615-1, 2층"), ("대 표 이 사", "고 진 식                    (인)")]),
    ]):
        c = row.cells[i]
        c.width = Cm(8.5)
        cell_margins(c, 120, 120, 160, 160)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(f"“{who}”")
        set_font(r, size=11, bold=True, color=NAVY)
        for k, v in rows:
            q = c.add_paragraph()
            q.paragraph_format.space_after = Pt(3)
            q.paragraph_format.line_spacing = 1.5
            r = q.add_run(k + " : ")
            set_font(r, size=10, bold=True, color=GRAY)
            add_runs(q, v, size=10.5)
    for tr in t.rows:  # 행이 쪽에 걸쳐 갈리지 않게
        trpr = tr._tr.get_or_add_trPr()
        cs = OxmlElement("w:cantSplit")
        trpr.append(cs)

    # ---- 별표 1 (새 쪽)
    p = doc.add_paragraph()
    p.add_run().add_break(WD_BREAK.PAGE)
    p = para(doc, after=2)
    r = p.add_run("별표 1")
    set_font(r, size=9, bold=True, color=GOLD)
    p = para(doc, after=4)
    r = p.add_run("특약사항 · 발전지원(세대 혜택 패키지) 확정 항목")
    set_font(r, size=15, bold=True, color=NAVY)
    rule(doc, color="0D1E33", size=8, after=8)
    p = para(doc, after=8, size=10, color=GRAY)
    add_runs(p, "주관사는 아래 특약사항을 성실히 이행한다. 지원 항목은 협의회가 고른 것을 적고, 협의회가 요청하면 같은 금액 범위 안에서 다른 항목으로 바꿀 수 있다(제26조 · 제25조 제2항). "
                "‘(안)’ 항목은 참여업체 확정 후 협의회 승인으로 확정한다.", size=10, color=GRAY)

    kv_table(doc, [
        ("발전지원 총액", "금 【금액】원 상당 (【세대수】세대 · 세대당 약 【금액】원) · 주관사 부담 · 공동구매 단가 전가 없음"),
        ("집행 방법", "협의회가 고른 항목을 주관사가 직접 구매 · 제공 · 시공 · 집행 내역 공개 · 현금 지급 없음"),
        ("확정 시점", "항목 · 수량 · 일정은 【확정 시점(예: 협약 후 30일 이내 · 정례회의)】까지 협의회가 정한다"),
    ], head="지원 조건")
    para(doc, after=4)

    grid_table(doc, ["구분", "지원 항목(예시 · 협의회가 선택)", "확정 내용 · 수량 · 시기", "비고"], [
        ("A", "백화점 상품권 세대당 【5 · 10】만원(세대 현물 직접 지급)", "【 】", "【 】"),
        ("A", "사전점검 대행 최대 50% 할인 · 이벤트 당첨 세대 동행", "【 】", "【 】"),
        ("A", "타입별 실측 · 샘플하우스 · 항공 VR 촬영 · 3D 홈스타일링", "【 】", "【 】"),
        ("A", "방문 선물 · 사은품 · 경품 · 정회원 혜택(같은 범위 안 배분)", "【 】", "(안)"),
        ("B", "공용부 구조 · 시공 품질 점검(열화상 드론 · 라돈 측정) · 하자 분석 보고서", "【 】", "【 】"),
        ("B", "사전점검 당일 추가 지원 · 온라인 위임장 · 도면 분석보고서", "【 】", "【 】"),
        ("B", "시행 · 시공사 협상 미팅 동석 · 민원 의견 전달 · 세스코 특수해충 점검", "【 】", "【 】"),
        ("C", "동 파사드 · 문주 · 놀이터 · 산책로 경관조명 진단 및 개선안", "【 】", "진단 · 자료 제공"),
        ("C", "커뮤니티 · 공용부 조명 개선안 · 전기차 충전 인프라 검토 · 입주 기념 점등식", "【 】", "【 】"),
        ("기타", "【협의회 지정 항목】", "【 】", "【 】"),
    ], widths=(1.4, 7.2, 5.6, 2.8))
    para(doc, after=8)

    grid_table(doc, ["번호", "특약 내용", "기한 · 조건"], [
        ("1", "하자 예치금 금 【금액】원 예치 · 입주 【완료 시 · 기간】까지 유지 · 사용 내역 공개", "【 】"),
        ("2", "협약이행 · 하자보증 증권(협의회 피보험자 · 【12】개월 이상 · 금 【금액】원) 제출", "협약 후 【 】일 이내"),
        ("3", "입주박람회 【연월】 · 【요일 · 일수】 · 장소 【행사장】(협의회와 답사 후 확정)", "【 】"),
        ("4", "온라인 박람회(폐쇄몰) · 카카오 상담 운영 · 박람회장과 같은 가격", "박람회 기간 ~ 【 】"),
        ("5", "행사주최자배상책임보험 가입(협의회 요청 시) · 증권 사본 제출", "박람회 전"),
        ("6", "주관 콜센터 · A/S 창구 운영(24시간 1차 회신 · 48시간 하자보수 원칙)", "입주 후 1년"),
        ("7", "월별 업무 타임테이블에 따른 정례회의 보고 · 박람회 결과보고서 · 최종 보고서", "제4조 제6항"),
        ("8", "【 】", "【 】"),
    ], widths=(1.2, 11.6, 4.2))
    para(doc, after=10)

    p = para(doc, after=2, keep=True)
    r = p.add_run("별첨 (이 협약의 일부)")
    set_font(r, size=11, bold=True, color=NAVY)
    for s in ["별첨 1. 입주박람회 주관사 제안서 및 제출서류 일체(【제출일】)",
              "별첨 2. 공동구매 계약 취소 · 환불 규정(제1 ~ 10조 · 별표 품목별 취소 가능 기한)",
              "별첨 3. 참여업체 특약이행각서 양식(9개 조항) 및 하자보수 이행각서 양식",
              "별첨 4. 하자 예치금 약정서(예치 · 지급 · 반환 절차)",
              "별첨 5. 주관사 사업자등록증 · 법인등기부등본 · 사용인감계"]:
        q = para(doc, after=1, indent=0.5, size=10, keep=True)
        add_runs(q, s, size=10)

    fix_order(doc)
    doc.save(OUT)
    return OUT


if __name__ == "__main__":
    print(build())
