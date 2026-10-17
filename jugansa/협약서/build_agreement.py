# -*- coding: utf-8 -*-
"""엣지컴퍼니 입주박람회 주관 협약서 — Word(.docx) 표준 양식 (본부장 10-17).

원칙(본부장 지시): 기존 'e편한세상 에코델타 MOU체결서'(26조) 초안을 그대로 두고 살짝만 바꾼다. 3쪽 이내. 조항을 늘리지 않는다.
바꾼 곳(초안 대비)
- 머리글 · 제2조 : 단지명 · 세대수를 【 】 칸으로.
- 제5조 : 기간 = 협약일 ~ 입주 후 1년(주관 창구 운영과 맞춤) · 보증기간 잔존 시 효력 유지(드파인 센텀 협약 문구).
- 제13조 ② : 결제 방식에 따른 가격 인상 금지(카드 · 현금 동일가) — 제안서와 같게.
- 제15조 ① : 하자보수 72시간 → 24시간 1차 회신 · 48시간 처리 원칙(제안서와 같게).
- 제26조 특약 : 발전지원금 【 】만원 상당 = 혜택 패키지(A · B · C는 예시 · 협의회가 골라서) + 하자 예치금 · 이행보증 · 박람회 장소 등 빈칸.
사용: python3 build_agreement.py → 엣지컴퍼니_입주박람회_주관사_협약서_양식.docx
"""
import os
import re

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "엣지컴퍼니_입주박람회_주관사_협약서_양식.docx")

NAVY = RGBColor(0x0D, 0x1E, 0x33)
GOLD = RGBColor(0x9A, 0x7B, 0x3F)
GRAY = RGBColor(0x5B, 0x66, 0x76)
FONT = "맑은 고딕"
FILL = "FBF4E3"

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
    for root in (doc.element.body, doc.sections[0].header._element, doc.sections[0].footer._element):
        for el in root.iter():
            tag = el.tag.split("}")[1] if "}" in el.tag else el.tag
            if tag in _ORD:
                _sort(el, tag)
    z = doc.settings.element.find(qn("w:zoom"))
    if z is not None and z.get(qn("w:percent")) is None:
        z.set(qn("w:percent"), "100")


def set_font(run, size=10, bold=False, color=None):
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.append(rf)
    for k in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(k), FONT)


def add_runs(p, text, size=10, bold=False, color=None):
    for part in re.split(r"(【[^】]*】)", text):
        if not part:
            continue
        if part.startswith("【"):
            r = p.add_run(part)
            set_font(r, size=size, bold=True, color=GOLD)
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear")
            shd.set(qn("w:color"), "auto")
            shd.set(qn("w:fill"), FILL)
            r._element.get_or_add_rPr().append(shd)
        else:
            r = p.add_run(part)
            set_font(r, size=size, bold=bold, color=color)


def para(doc, text="", size=10, bold=False, color=None, align=None, before=0, after=2, line=1.3, indent=0, hang=0, keep=False):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before, pf.space_after, pf.line_spacing = Pt(before), Pt(after), line
    if indent:
        pf.left_indent = Cm(indent)
    if hang:
        pf.first_line_indent = Cm(-hang)
    if align is not None:
        p.alignment = align
    if keep:
        pf.keep_with_next = True
    if text:
        add_runs(p, text, size=size, bold=bold, color=color)
    return p


def rule(doc, color="C8A86A", size=12, after=6):
    p = para(doc, after=after)
    bdr = OxmlElement("w:pBdr")
    b = OxmlElement("w:bottom")
    b.set(qn("w:val"), "single")
    b.set(qn("w:sz"), str(size))
    b.set(qn("w:space"), "1")
    b.set(qn("w:color"), color)
    bdr.append(b)
    p._element.get_or_add_pPr().append(bdr)


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


def article(doc, no, title, items):
    """items: str | [str | (str, [호...])] — 초안과 같은 ①②③ · 1. 2. 표기."""
    p = para(doc, before=5, after=1, keep=True)
    r = p.add_run(f"제{no}조({title})")
    set_font(r, size=10, bold=True, color=NAVY)
    if isinstance(items, str):
        items = [items]
    circ = "①②③④⑤⑥⑦⑧⑨⑩"
    for i, it in enumerate(items):
        sub = None
        if isinstance(it, tuple):
            it, sub = it
        prefix = (circ[i] + " ") if len(items) > 1 else ""
        add_runs(para(doc, after=1, indent=0.3 if prefix else 0, hang=0.3 if prefix else 0), prefix + it)
        for j, s in enumerate(sub or [], 1):
            add_runs(para(doc, after=0.5, indent=0.8, hang=0.4, size=9.5), f"{j}. {s}", size=9.5)


def build():
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.top_margin, sec.bottom_margin = Cm(1.8), Cm(1.6)
    sec.left_margin, sec.right_margin = Cm(2.0), Cm(2.0)
    sec.header_distance, sec.footer_distance = Cm(0.8), Cm(0.8)
    st = doc.styles["Normal"]
    st.font.name, st.font.size = FONT, Pt(10)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)

    hp = sec.header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_font(hp.add_run("공동구매 및 입주박람회 기획 · 진행 위탁 협약서  ·  주식회사 엣지컴퍼니"), size=8, color=GRAY)
    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_font(fp.add_run("- "), size=8.5, color=GRAY)
    page_number(fp)
    set_font(fp.add_run(" -"), size=8.5, color=GRAY)

    # 제목 (초안 제목 그대로)
    p = para(doc, before=6, after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_font(p.add_run("공동구매 및 입주박람회 기획 · 진행 위탁 협약서"), size=19, bold=True, color=NAVY)
    p = para(doc, after=4, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_font(p.add_run("입주박람회 주관사 협약 (MOU 체결서)"), size=10.5, color=GRAY)
    rule(doc, after=8)

    add_runs(para(doc, after=8, line=1.45),
             "【단지명】 입주예정자협의회(이하 ‘협의회’)와 주식회사 엣지컴퍼니(이하 ‘주관사’)는 다음과 같이 공동구매 및 입주박람회 기획 · 진행 위탁(이하 ‘위탁업무’) 협약을 체결한다.")

    article(doc, 1, "목적", "본 협약의 목적은 협의회와 주관사 간의 위탁업무에 관한 전반적인 사항을 규정함에 있다.")
    article(doc, 2, "업무범위", [
        "협의회가 주관사에게 위탁한 【단지명】(이하 ‘아파트’ · 【세대수】세대)의 공동구매, 입주박람회 기획 및 진행.",
        "주관사가 제출한 제안서 상에 명시된 업무.",
    ])
    article(doc, 3, "보수 및 비용", "협의회는 본 협약 이행에 대한 보수를 주관사에 지급하지 않으며, 비용 일체는 주관사가 부담하는 것으로 한다.")
    article(doc, 4, "위탁업무의 처리", [
        "주관사는 위탁업무에 대해 신의 · 성실의 의무를 다하여야 한다.",
        "주관사는 제안서 상에 명시된 위탁업무에 대해 적극적으로 임해야 한다.",
        "주관사가 협의회의 협조를 원하는 경우 협의회는 성공적인 위탁업무 완료를 위하여 이에 적극 협조하여야 한다.",
        "위탁업무 처리 과정에서 주관사의 명백한 귀책사유가 발생되었을 경우 주관사는 사후 조치 및 보완에 대해 적극적으로 임해야 한다.",
        "주관사는 정당한 사유 없이 협의회의 위탁업무를 거부할 수 없다.",
    ])
    article(doc, 5, "협약 기간", [
        "본 협약의 기간은 협약일로부터 아파트 입주 후 1년이 되는 날까지로 한다. 다만, 기간 종료 전에 공동구매에 참여한 회원에 대하여는 본 협약의 효력은 해당 회원의 공동구매 물품 하자보증기간이 끝날 때까지 유효한 것으로 본다.",
        "아파트의 최초 입주자대표회의 구성일이 제1항의 종료일보다 이전일 경우 협의회의 권리 · 의무는 입주자대표회의가 승계할 수 있다.",
    ])
    article(doc, 6, "협약의 해지", [
        ("해지 조건 — 협의회, 주관사는 다음 각 호 중 어느 하나에 해당하는 사유가 발생하는 경우 협약의 전부를 해지할 수 있다.", [
            "현행 법령 및 협의회의 규정상의 제한 사유에 해당하는 경우",
            "주관사의 과실로 인하여 협의회 또는 회원에게 중대한 손해가 발생한 경우",
            "협의회와 주관사의 협의 하에 본 협약을 파기하는 경우",
            "본 협약서의 각 조항을 위배하였을 경우",
        ]),
        "시정 요청 — 해지 사유의 발생으로 협의회가 협약을 해지코자 하는 경우에는 사전에 주관사에게 일정 기한을 정하여 서면으로 시정을 요구하여야 하며, 동 기간 동안 시정이 이루어지지 않을 경우에는 본 협약을 해지할 수 있다.",
        "협의회가 불가피한 사유로 협약을 해지코자 하는 경우에는 주관사와 협의하여야 한다.",
        "본 협약의 해지는 그 의사표시를 기재한 서면이 상대방에게 도달한 날로부터 15일 후에 그 효력이 발생한다.",
    ])
    article(doc, 7, "물품의 공급", [
        ("주관사는 다음 각 호와 같이 협의회가 필수적으로 공급 요청한 물품에 대해 반드시 공급을 하여야 한다.", [
            "인테리어 : 중문, 방충망, 안전망, 방범창, LED조명, 시스템선반, 커튼, 블라인드",
            "홈케어 : 단열필름, 새집증후군, 입주청소, 줄눈, 탄성코트 등",
            "생활 : 가전, 가구, 에어컨, 시스템에어컨, 음식물처리기, 전기렌지",
            "기타 : 이사, 도배, 목공, 필름, 대리석시공, 렌탈서비스, 유리막코팅 등",
        ]),
        "주관사는 협의회와 협상을 통하여 추가로 결정된 물품들에 대해 공급할 수 있다.",
        "물품 공급을 위하여 참여하는 공급업체에 대해서는 주관사와 공급업체 간 물품 공급에 대한 계약 또는 협약(특약이행각서)을 맺어야 한다.",
    ])
    article(doc, 8, "공급업체의 선정", [
        ("주관사는 공급업체 선정에 있어 자사의 기준에 따라 공정하고 투명하게 선정하여야 한다.", [
            "개별업체 제안 접수 시 협의회와 공유 가능한 이메일을 통해 접수를 받기로 한다.",
        ]),
        ("공급업체 선정에 있어 다음 각 호 중 어느 하나라도 해당되는 경우 배제하여야 한다.", [
            "단순 유통 마진을 취하기 위하여 재하도급을 하는 업체",
            "타 단지의 공동구매 참여 경력에 있어 입주민과 분쟁이나 불만 사례가 상당수 접수된 업체",
            "주관사가 관리 · 감독할 수 없는 업체",
        ]),
    ])
    article(doc, 9, "공급업체의 교체", [
        ("주관사가 선정한 공급업체에 대해 다음의 사유가 발생되었을 경우 즉각 교체하여야 한다.", [
            "공급업체에 대한 협의회의 불만에 대해 시정 조치를 요구하였으나 이에 응하지 않을 경우",
            "공급업체에 대한 회원들의 불만이 지속적 또는 상당수 발생하는 업체",
            "위탁업무를 수행함에 있어 협의회가 부적격하다고 판단하는 업체",
            "실제 공급한 물품의 모델, 규격, 사양, 수량, 가격, 재료 등에 있어 홍보 물품과 상이한 업체",
            "계약서, 제안서, 제안요청서 등 협의회가 요구하는 사항을 이행하지 않거나 시정하지 않는 업체",
        ]),
    ])
    article(doc, 10, "거래의 방식", "공동구매 물품에 대해서는 회원과 공급업체 간의 직거래 방식을 원칙으로 한다.")
    article(doc, 11, "납품 및 시공", [
        "공급업체와 회원 간의 계약 체결 시 시공(납품) 예정일을 고지하여야 한다.",
        "공급업체의 시공(납품) 예정일 미고지 및 일방적 변경이 있어서는 안 되며, 이로 인한 회원의 계약 취소 요청이 있을 경우 이에 반드시 응해야 한다. 이때 계약금은 전액 환불하여야 한다.",
        "시공(납품) 예정일 연기에 대해 공급업체와 회원 간 사전 협의 및 동의가 있을 경우에는 제2항의 예외로 인정한다.",
    ])
    article(doc, 12, "물품의 홍보", [
        "공급업체가 협의회 또는 주관사가 정한 기준을 위배한 홍보 행위를 하였을 경우 이에 따른 제재를 가한다.",
        "물품 구매에 따른 특약 사항은 홍보 시에 반드시 언급 또는 표기를 해야 한다.",
    ])
    article(doc, 13, "대금의 결제", [
        "계약금은 공급가의 10%를 초과할 수 없다. 단, 전액 선결제를 요하는 물품에 대해서는 예외로 한다.",
        "대금에 대해서는 신용(체크)카드 결제가 가능해야 하며, 현금 거래 시 세금계산서(현금영수증) 발급이 가능하여야 한다. 결제 방식을 이유로 사전에 제시한 금액의 인상을 요구하여서는 안 된다(카드 · 현금 동일가).",
        "잔금의 결제는 구매자의 검수가 완료된 이후가 되어야 한다.",
        "공급업체가 물품 공급 대금을 계좌이체로 받을 경우 사전에 협의회에 제출 및 확인된 계좌에 대해서만 허용한다.",
    ])
    article(doc, 14, "대금의 취소 · 환불", [
        "계약 및 구매 물품의 취소 및 환불에 대해서는 협의회, 공급업체, 공정거래위원회 고시 소비자분쟁해결기준 및 주관사가 제안서에 첨부한 계약 취소 · 환불 규정을 따르도록 한다.",
        "공급업체의 귀책으로 인한 구매자의 대금 환불 요청 시 제품 제작에 소요된 비용 등을 감하여서는 아니 된다(구매자의 단순 변심 등에 의한 경우는 제외로 한다).",
        "본 조의 문제로 발생되는 분쟁에 대해서 주관사는 적극 개입하여 해결해야 한다.",
    ])
    article(doc, 15, "하자보수 처리 및 보증", [
        "하자보수의 처리는 접수 후 24시간 이내 1차 회신, 48시간 이내 처리를 원칙으로 하며 구매자의 동의에 따라 연장 가능하다.",
        "공급업체는 구매자의 하자보수에 대한 보증 요청 시 실시하여야 한다.",
        "하자보수 처리 시 방문시간은 고객이 원하는 시간으로 진행한다.",
    ])
    article(doc, 16, "민원서비스 제공", "주관사는 회원들을 대상으로 공동구매에 대한 전반적인 사항 등의 민원서비스를 제공하여야 한다.")
    article(doc, 17, "입주박람회 개최", "주관사는 수분양자들을 대상으로 1회 이상의 입주박람회를 개최하여야 한다.")
    article(doc, 18, "책임", [
        ("주관사는 위탁사업을 진행함에 있어 다음 각 호의 책임을 가지며, 각 호에 대한 상세 책임 내용에 대해서는 제안서를 따른다.", [
            "공급업체의 관리 및 감독의 책임", "위탁사업 계약의 책임", "하자보수의 책임", "분쟁 해결의 책임",
            "입주박람회 개최의 책임", "청렴결백의 의무", "하도급업체와의 상생협력",
        ]),
    ])
    article(doc, 19, "제안서 · 제안요청서 준수", "주관사는 본 협약 체결 전 협의회가 입찰을 위해 공고한 제안요청서와 주관사가 제출한 제안서의 내용을 준수해야 한다.")
    article(doc, 20, "권리 · 의무의 양도 금지", "주관사는 본 협약과 관련된 권리나 의무를 협의회의 서면 승인 없이는 제3자에게 양도할 수 없다.")
    article(doc, 21, "신의 · 성실의 의무", "협의회와 주관사는 신의 · 성실의 원칙에 입각하여 상호 협조와 신뢰로써 본 협약을 성실히 준수토록 하여 공동 발전을 위하여 노력한다.")
    article(doc, 22, "손해배상", [
        ("다음 각 호의 사유로 협의회에게 손해가 발생되어 협의회가 손해배상을 청구하는 경우 주관사는 지체 없이 이에 응해야 한다.", [
            "주관사의 고의 또는 과실로 인하여 위탁업무의 하자가 발생되었을 경우",
            "본 협약서 상의 조건 위반으로 협의회에게 손해가 발생하거나 객관적으로 확실시되는 경우",
        ]),
    ])
    article(doc, 23, "비밀유지", [
        "주관사는 회원의 개인정보를 비밀로 취급하여야 하며 협의회의 승인 없이 제3자에게 열람 또는 누출시킬 수 없다.",
        "주관사가 위탁업무 수행상 필요하거나 법적으로 공개가 요구되는 경우에는 제1항의 예외로 인정한다.",
        "본 조의 위반으로 협의회 또는 회원에게 손해가 발생되는 경우 이를 보상하여야 한다.",
        "협약 종료 시 협의회 또는 회원이 제공한 개인정보 등은 즉시 폐기하여야 한다.",
    ])
    article(doc, 24, "분쟁해결", "본 협약에 명시되지 않은 사항 또는 본 협약의 이행에 대한 해석에 이의가 있을 때는 상호 간의 합의에 따라 원만히 해결하며, "
                               "이에 대한 합의가 이루어지지 않을 때는 관할 법원을 협의회의 소재지 관할 법원으로 하여 분쟁을 해결하기로 한다.")
    article(doc, 25, "기타사항", [
        "본 협약의 이행에 있어 협의회가 인정한 불가피한 사유가 발생되었을 경우에는 협의회와 주관사가 충분히 협의하여 조정할 수 있다.",
        "본 협약의 성립을 증명하기 위해 협약서를 2부 작성하여 기명 날인 후 각 1부씩 보관한다.",
        "본 협약은 쌍방의 서명 또는 날인일로부터 효력을 발생한다.",
    ])

    # 제26조 특약 — 초안의 번호 목록 형식 그대로 · 값만 【 】
    p = para(doc, before=5, after=1, keep=True)
    set_font(p.add_run("제26조(특약 사항)"), size=10, bold=True, color=NAVY)
    add_runs(para(doc, after=2, size=9.5, color=GRAY), "주관사는 아래 특약사항을 성실히 이행한다. 다만, 협의회가 요청할 경우 협의 하에 동액 상당의 다른 서비스로 대체할 수 있다.", size=9.5, color=GRAY)
    for i, t in enumerate([
        "발전지원금 【금액】만원 상당(VAT 포함) — 세대 혜택 패키지로 집행 · A · B · C는 예시이며 협의회가 원하는 항목을 골라 주관사가 직접 구매 · 제공(집행 내역 공개 · 공구가 전가 없음)",
        "에스크로(하자 예치금) 【금액】원 거치 — 입주 완료까지 · 엣지컴퍼니 자산 예치 · 예치금 반환 시 하자보수이행증권 발부",
        "이행(하자)보증보험증권 — 협의회 피보험자 · 보증기간 【12】개월 이상 · 금액 【 】원(협약 확정액)",
        "입주박람회 — 【연월】 금 · 토 · 일 【3】일 · 장소 【행사장】(협의회와 답사 후 확정) · 온라인 박람회(폐쇄몰) 병행",
        "백화점 상품권 세대당 【5 · 10】만원(세대 현물 직접 지급) · 사전점검 대행 최대 50% 할인 · 평형별 무료 실측 · 항공 VR · 3D 홈스타일링",
        "공용부 하자 점검 · 열화상 드론 · 라돈 검출기 대여 · 도면 분석보고서 · 온라인 위임장 · 사전점검 당일 현장 지원",
        "시행 · 시공사 미팅 및 지원 요청에 대한 전문 인력 투입 · 협의 동석 · 건의 관리표 보고",
        "경관조명 진단 · 개선안(동 파사드 · 문주 · 놀이터 · 산책로) · 입주 기념 점등식 · 단지 내 드론촬영 【2】회",
        "주관 콜센터 · A/S 한 창구 운영(24시간 1차 회신 · 48시간 하자보수 · 미응답 시 선보상) — 입주 후 1년",
        "【 】",
    ], 1):
        add_runs(para(doc, after=1, indent=0.6, hang=0.45, size=9.5), f"{i}. {t}", size=9.5)

    # 날짜 · 서명 (초안 배치 그대로)
    p = para(doc, before=12, after=8, align=WD_ALIGN_PARAGRAPH.CENTER, keep=True)
    add_runs(p, "【20    】년  【   】월  【   】일", size=11, bold=True)
    t = doc.add_table(rows=1, cols=2)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for i, (who, rows) in enumerate([
        ("“협의회”", [("단 체 명", "【단지명】 입주예정자협의회"), ("카페 주소", "【카페 주소】"), ("대      표", "입주자 협의회 대표  【성명】          (인)")]),
        ("“주관사”", [("사업자번호", "508-81-42798"), ("상      호", "주식회사 엣지컴퍼니"), ("주      소", "울산광역시 울주군 청량읍 온산로 615-1, 2층"), ("대      표", "고 진 식          (인)")]),
    ]):
        c = t.rows[0].cells[i]
        c.width = Cm(8.5)
        q = c.paragraphs[0]
        q.paragraph_format.space_after = Pt(4)
        set_font(q.add_run(who), size=10.5, bold=True, color=NAVY)
        for k, v in rows:
            q = c.add_paragraph()
            q.paragraph_format.space_after = Pt(2)
            q.paragraph_format.line_spacing = 1.4
            set_font(q.add_run(k + " : "), size=9.5, bold=True, color=GRAY)
            add_runs(q, v, size=10)
    trpr = t.rows[0]._tr.get_or_add_trPr()
    trpr.append(OxmlElement("w:cantSplit"))

    fix_order(doc)
    doc.save(OUT)
    return OUT


if __name__ == "__main__":
    print(build())
