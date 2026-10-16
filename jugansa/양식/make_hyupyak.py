"""입주박람회 주관 협약서(표준 — 에코델타 센터포인트 2024.03 체결본 구조 + 입예협 요청 조항) + 주관 실적 확인서 — 편집 가능한 .docx 양식.
사용: python make_hyupyak.py <출력폴더>
- 협약서: 앞으로 주관 단지와 체결할 표준 협약서(빈칸 채워 2부 작성·서명).
- 실적 확인서: 협약서를 보관하지 않은 과거 단지용. 당시 협의회 대표가 '지금 날짜'로 서명하는 사실 확인서.
  과거 날짜로 협약서를 새로 만들어 제출하지 않는다(사문서 소급 작성 = 입찰 무효·형사 위험)."""
import os, sys
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

CO = dict(name="주식회사 엣지컴퍼니", ceo="고진식", brn="508-81-42798",
          addr="울산광역시 울주군 청량읍 온산로 615-1, 2·3층", tel="010-7273-9901 (주관사업 총괄 본부장)")
FONT = "맑은 고딕"
NAVY = RGBColor(0x0D, 0x1E, 0x33)

def base():
    d = Document()
    for s in d.sections:
        s.top_margin = s.bottom_margin = Cm(2.0); s.left_margin = s.right_margin = Cm(2.2)
    st = d.styles["Normal"]; st.font.name = FONT; st.font.size = Pt(10.5)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    st.paragraph_format.space_after = Pt(3); st.paragraph_format.line_spacing = 1.25
    return d

def para(d, text="", size=None, bold=False, align=None, color=None, after=None, before=None):
    p = d.add_paragraph(); r = p.add_run(text); r.bold = bold
    if size: r.font.size = Pt(size)
    if color: r.font.color.rgb = color
    if align: p.alignment = align
    if after is not None: p.paragraph_format.space_after = Pt(after)
    if before is not None: p.paragraph_format.space_before = Pt(before)
    return p

def title(d, t, sub=None):
    para(d, t, 20, True, WD_ALIGN_PARAGRAPH.CENTER, NAVY, after=2)
    if sub: para(d, sub, 10, False, WD_ALIGN_PARAGRAPH.CENTER, RGBColor(0x55, 0x5B, 0x66), after=10)

def table(d, rows, widths, head=False):
    t = d.add_table(rows=len(rows), cols=len(rows[0])); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            c = t.cell(i, j); c.width = Cm(widths[j]); c.text = ""
            r = c.paragraphs[0].add_run(v); r.font.size = Pt(10)
            if (head and i == 0) or (not head and j % 2 == 0 and len(row) > 1 and v):
                r.bold = True
    d.add_paragraph().paragraph_format.space_after = Pt(2)
    return t

def article(d, no, head, lines):
    para(d, f"제{no}조 ({head})", 11, True, before=6, after=2)
    for ln in lines: para(d, ln, after=1)

def sign_block(d, left_title, right_title):
    t = d.add_table(rows=6, cols=2); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    L = [left_title, "단 체 명 :", "대 표 자 :                      (서명 또는 인)", "직    위 :", "연 락 처 :", "주    소 :"]
    R = [right_title, f"상    호 : {CO['name']}", f"대 표 자 : 대표이사 {CO['ceo']}        (인)",
         f"사업자등록번호 : {CO['brn']}", f"연 락 처 : {CO['tel']}", f"주    소 : {CO['addr']}"]
    for i in range(6):
        for j, v in enumerate((L[i], R[i])):
            c = t.cell(i, j); c.width = Cm(8.3); c.text = ""
            r = c.paragraphs[0].add_run(v); r.font.size = Pt(9.5); r.bold = (i == 0)

def shade(cell, hexcolor):
    from docx.oxml import OxmlElement
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), hexcolor); tcPr.append(sh)

def grid(d, rows, widths, head=True, size=9.5):
    t = d.add_table(rows=len(rows), cols=len(rows[0])); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            c = t.cell(i, j); c.width = Cm(widths[j]); c.text = ""
            r = c.paragraphs[0].add_run(v); r.font.size = Pt(size)
            if head and i == 0:
                r.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF); shade(c, "0D1E33")
                c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    d.add_paragraph().paragraph_format.space_after = Pt(2)

def chapter(d, t):
    p = para(d, t, 12.5, True, color=NAVY, before=10, after=4)
    from docx.oxml import OxmlElement
    pPr = p._p.get_or_add_pPr(); bd = OxmlElement("w:pBdr"); bt = OxmlElement("w:bottom")
    for k, v in (("val", "single"), ("sz", "8"), ("space", "1"), ("color", "C8A86A")): bt.set(qn("w:" + k), v)
    bd.append(bt); pPr.append(bd)

def items(d, lines, size=None):
    for ln in lines: para(d, ln, size, after=1)

def hyupyak(out):
    """에코델타 센터포인트 MOU(2024.03.15, 실제 체결본 구조) + 입예협 요청 2개 조항(해석 우선 · 3회 불이행 해지) + 당사 보강."""
    d = base()
    title(d, "공동구매 및 입주박람회 기획 · 진행 위탁 협약서", "입주예정자협의회 ↔ 주관사")
    para(d, "(                              ) 입주예정자협의회(이하 \"협의회\")와 주식회사 엣지컴퍼니(이하 \"주관사\")는 "
            "공동구매 및 입주박람회 기획 · 진행 위탁(이하 \"위탁업무\")에 관하여 다음과 같이 협약(이하 \"이 협약\")을 체결한다.", after=6)
    table(d, [["단 지 명", "", "소 재 지", ""], ["세 대 수", "            세대", "입주 예정", "      년      월 ~      월"],
              ["시행 · 시공사", "", "선정 근거", "      년    월    일 공고 · 공개 입찰"]], [2.6, 5.7, 2.6, 5.7])

    chapter(d, "제1장  총칙")
    article(d, 1, "목적", ["이 협약은 협의회와 주관사 사이의 위탁업무에 관한 권리 · 의무와 업무 처리 기준을 정함을 목적으로 한다."])
    article(d, 2, "업무 범위", ["① 협의회가 주관사에 위탁한 위 단지(이하 \"아파트\")의 공동구매, 입주박람회 기획 및 진행.",
                              "② 주관사가 입찰 때 제출한 제안서와 협의회의 공고(제안요청서)에 명시된 업무.",
                              "③ 사전점검 · 입주 준비 지원, 공동구매 품목의 계약 · 시공 · A/S 관리와 회원 민원 처리."])
    article(d, 3, "보수 및 비용", ["협의회는 이 협약 이행에 대한 보수를 주관사에 지급하지 않으며, 위탁업무에 드는 비용 일체는 주관사가 부담한다."])
    article(d, 4, "협약 기간", ["① 이 협약의 기간은 협약일부터 (□ 12개월  □ 입주 지정기간 종료 후    개월  □         )까지로 한다.",
                              "② 아파트의 최초 입주자대표회의 구성일이 ①항의 종료일보다 늦으면 입주자대표회의 구성일을 종료일로 한다.",
                              "③ 협약 기간이 끝난 뒤에도 공동구매 품목의 하자보수 · A/S 책임은 품목별 보증기간까지 유지된다."])
    article(d, 5, "협약의 해석", ["① 이 협약의 내용에 대한 해석이 서로 다를 경우 협의회의 해석을 우선하며, 주관사는 이에 이의를 제기하지 않는다.",
                                "② 다만 ①항의 해석은 관계 법령과 이 협약의 명시적 문언에 반하지 않는 범위에서 적용한다."])

    chapter(d, "제2장  위탁업무의 처리")
    article(d, 6, "위탁업무의 처리", ["① 주관사는 신의 · 성실의 원칙에 따라 위탁업무를 처리하고, 제안서에 명시한 업무에 적극적으로 임한다.",
                                    "② 주관사가 협조를 요청하면 협의회는 위탁업무의 원활한 수행을 위하여 이에 협조한다.",
                                    "③ 주관사의 귀책사유가 발생한 경우 주관사는 사후 조치와 보완을 지체 없이 이행한다.",
                                    "④ 주관사는 정당한 사유 없이 협의회의 위탁업무 요청을 거부할 수 없다.",
                                    "⑤ 주관사는 이 단지 전담 책임자(PM)를 지정하여 협의회에 서면으로 알리고, 교체할 때에는 사전에 협의한다."])
    article(d, 7, "제안서 · 제안요청서 준수", ["주관사는 협의회가 입찰 때 공고한 제안요청서와 주관사가 제출한 제안서의 내용을 준수하며, 제안서는 이 협약의 일부로 본다."])
    article(d, 8, "입주박람회 개최", ["① 주관사는 수분양자를 대상으로 1회 이상 입주박람회를 개최한다.",
                                    "② 일정 · 장소 · 운영 시간은 협의회와 협의하여 정하며, 행사 기간 :     년   월   일 ~   월   일 · 장소 :",
                                    "③ 주관사는 행사장 안전 계획(인력 · 동선 · 비상구)을 세우고, 행사 기간에 맞춰 행사주최자배상책임보험에 가입하여 협의회가 요청하면 가입증명서를 제출한다.",
                                    "④ 주관사는 행사 종료 후 30일 이내에 방문 세대 · 품목별 계약 건수 · 민원 처리 현황을 협의회에 보고한다."])
    article(d, 9, "민원 서비스", ["① 주관사는 회원을 대상으로 공동구매 전반에 관한 통합 민원 창구(전화 · 문자 · 온라인)를 운영한다.",
                                "② 민원은 접수 후 24시간 이내에 담당 업체를 배정하고, 처리 결과를 회원과 협의회에 알린다."])

    chapter(d, "제3장  물품 공급과 공급업체")
    article(d, 10, "물품의 공급", ["① 주관사는 협의회가 공급을 요청한 다음 품목을 공급한다.",
                                 "   1. 인테리어 : 중문, 방충망, 안전망, 방범창, LED 조명, 시스템 선반, 커튼, 블라인드",
                                 "   2. 홈케어 : 단열필름, 새집증후군, 입주청소, 줄눈, 탄성코트 등",
                                 "   3. 생활 : 가전, 가구, 에어컨, 시스템에어컨, 음식물처리기, 전기레인지",
                                 "   4. 기타 : 이사, 도배, 목공, 필름, 대리석 시공, 렌탈 서비스, 유리막 코팅 등",
                                 "② 주관사는 협의회와 협의하여 추가로 정한 품목을 공급할 수 있다.",
                                 "③ 주관사는 공급업체와 물품 공급 · 시공 · A/S에 관한 계약 또는 협약을 맺고, 이 협약의 기준을 지키도록 관리 · 감독한다."])
    article(d, 11, "공급업체의 선정", ["① 주관사는 공정하고 투명한 기준으로 공급업체를 선정하고, 선정 결과를 협의회와 공유한다.",
                                     "② 개별 업체의 제안은 협의회와 공유할 수 있는 이메일로 접수한다.",
                                     "③ 다음 각 호에 해당하는 업체는 선정에서 제외한다.",
                                     "   1. 단순 유통 마진을 취하기 위하여 재하도급하는 업체",
                                     "   2. 다른 단지 공동구매에서 입주민과의 분쟁이나 불만이 다수 접수된 업체",
                                     "   3. 주관사가 관리 · 감독할 수 없는 업체",
                                     "④ 주관사가 직접 공급 · 시공하는 품목이 있으면 선정 전에 그 사실을 협의회에 알린다."])
    article(d, 12, "공급업체의 교체", ["주관사는 공급업체에 다음 각 호의 사유가 생기면 협의회와 협의하여 즉시 교체한다.",
                                     "   1. 협의회의 시정 요구에 응하지 않는 경우",
                                     "   2. 회원의 불만이 지속적으로 또는 다수 발생하는 경우",
                                     "   3. 위탁업무 수행에 협의회가 부적격하다고 판단하는 경우",
                                     "   4. 실제 공급한 물품의 모델 · 규격 · 사양 · 수량 · 가격 · 재료가 홍보 내용과 다른 경우",
                                     "   5. 이 협약, 제안서, 제안요청서에서 정한 사항을 이행하지 않거나 시정하지 않는 경우"])
    article(d, 13, "가격과 홍보", ["① 판매가는 박람회 전에 협의회와 확정하여 공개한 단가(이하 \"사전 공개 단가\")를 원칙으로 하며, 주관사는 시중가 · 온라인 최저가와 비교한 자료를 협의회에 제출한다.",
                                 "② 결제 수단(카드 · 현금 등)에 따라 판매가를 차등하지 않으며, 부가가치세 처리를 이유로 사전에 제시한 금액의 인상을 요구하지 않는다.",
                                 "③ 공급업체가 협의회 또는 주관사가 정한 기준을 위반한 홍보를 하면 제재하며, 물품 구매에 따른 특약 사항은 홍보 때 반드시 표기한다.",
                                 "④ 사실과 다르거나 입증할 수 없는 과장 표현(최고 · 유일 등)은 사용하지 않는다."])

    chapter(d, "제4장  거래 · 대금 · 시공 · 하자")
    article(d, 14, "거래의 방식", ["공동구매 물품은 회원과 공급업체 사이의 직거래를 원칙으로 한다."])
    article(d, 15, "대금의 결제", ["① 계약금은 공급가의 10%를 넘을 수 없다. 다만 전액 선결제가 필요한 물품은 협의회와 협의하여 예외로 할 수 있다.",
                                 "② 대금은 신용 · 체크카드 결제가 가능해야 하며, 현금 거래 시 세금계산서 또는 현금영수증을 발급한다.",
                                 "③ 잔금은 구매자의 검수가 끝난 뒤에 결제한다.",
                                 "④ 공급업체가 대금을 계좌이체로 받을 때에는 사전에 협의회에 제출 · 확인된 계좌만 허용한다."])
    article(d, 16, "납품 및 시공", ["① 공급업체는 계약 체결 때 시공(납품) 예정일을 고지한다.",
                                  "② 시공(납품) 예정일을 고지하지 않거나 일방적으로 변경하여 회원이 계약 취소를 요청하면 공급업체는 이에 응하고 계약금 전액을 환불한다.",
                                  "③ 공급업체와 회원이 사전에 협의 · 동의하여 일정을 연기한 경우에는 ②항의 예외로 한다."])
    article(d, 17, "취소 · 환불", ["① 계약 취소와 환불은 협의회와 협의한 품목별 취소 · 환불 규정과 공정거래위원회 「소비자분쟁해결기준」에 따른다.",
                                 "② 공급업체의 귀책으로 환불할 때에는 제작에 든 비용 등을 공제하지 않는다. 단, 구매자의 단순 변심 등은 제외한다.",
                                 "③ 이 조와 관련한 분쟁에는 주관사가 적극 개입하여 해결한다."])
    article(d, 18, "하자보수 처리 및 보증", ["① 하자보수는 접수 후 72시간(업무시간 08:00~21:00 기준) 이내에 처리하며, 구매자가 동의하면 연장할 수 있다.",
                                          "② 방문 시간은 구매자가 원하는 시간으로 한다.",
                                          "③ 공급업체는 구매자가 요청하면 하자보수 보증을 한다.",
                                          "④ 공급업체가 기한 안에 처리하지 않거나 폐업 등으로 처리할 수 없으면 주관사가 대체 업체를 지정하여 남은 보증기간 동안 처리한다."])

    chapter(d, "제5장  책임 · 청렴 · 정보 보호")
    article(d, 19, "주관사의 책임", ["주관사는 위탁업무를 수행하면서 다음 각 호의 책임을 지며, 상세 내용은 제안서에 따른다.",
                                   "   1. 공급업체 관리 · 감독   2. 위탁업무 이행   3. 하자보수   4. 분쟁 해결",
                                   "   5. 입주박람회 개최   6. 청렴의 의무   7. 공급업체와의 상생 협력"])
    article(d, 20, "청렴 의무", ["① 주관사와 공급업체는 협의회 임원 · 운영위원과 그 가족 개인에게 금품 · 향응 · 편의를 제공하지 않는다.",
                               "② 협의회 임원 · 운영위원은 공급업체 선정과 관련하여 개인적 이익을 요구하거나 받지 않는다.",
                               "③ 주관사는 시행사 · 시공사 · 분양대행사 · 옵션 업체와의 이해관계를 협약 전에 서면으로 고지한다."])
    article(d, 21, "비밀 유지 및 개인정보 보호", ["① 주관사는 회원의 개인정보를 비밀로 취급하고, 협의회의 승인 없이 제3자에게 열람 · 제공하지 않는다. 다만 위탁업무 수행에 필요하거나 법령상 요구되는 경우는 예외로 한다.",
                                             "② 주관사는 「개인정보 보호법」에 따라 동의를 받고, 공급업체에는 필요한 범위만 제공하며 그 관리를 감독한다.",
                                             "③ 이 조를 위반하여 협의회나 회원에게 손해가 생기면 주관사가 배상한다.",
                                             "④ 협약이 끝나면 협의회 또는 회원이 제공한 개인정보를 지체 없이 파기한다."])
    article(d, 22, "손해배상", ["다음 각 호의 사유로 협의회에 손해가 발생하여 협의회가 배상을 청구하면 주관사는 지체 없이 이에 응한다.",
                              "   1. 주관사의 고의 또는 과실로 위탁업무에 하자가 발생한 경우",
                              "   2. 이 협약의 조건을 위반하여 협의회에 손해가 발생하거나 발생이 객관적으로 확실한 경우"])
    article(d, 23, "이행 담보", ["협의회가 요청하면 주관사는 이 협약의 이행을 담보하는 방법(이행보증증권 등)과 금액을 협의회와 협의하여 정한다."])

    chapter(d, "제6장  해지와 기타")
    article(d, 24, "협약의 해지", ["① 협의회 또는 주관사는 다음 각 호의 어느 하나에 해당하면 이 협약의 전부를 해지할 수 있다.",
                                 "   1. 관계 법령이나 협의회 규약상의 제한 사유에 해당하는 경우",
                                 "   2. 주관사의 과실로 협의회 또는 회원에게 중대한 손해가 발생한 경우",
                                 "   3. 양 당사자가 합의하여 협약을 종료하는 경우",
                                 "   4. 이 협약의 조항을 위반한 경우",
                                 "② 해지 사유가 생기면 해지하려는 쪽은 상대방에게 기한을 정하여 서면으로 시정을 요구하고, 그 기간에 시정되지 않으면 해지할 수 있다.",
                                 "③ 협의회가 서면(전자우편 포함)으로 요청하거나 시정을 요구한 사항을 주관사가 3회 이상 이행하지 않으면, 협의회는 ②항의 절차 없이 이 협약을 해지할 수 있다.",
                                 "④ 협의회가 불가피한 사유로 해지하려는 경우에는 주관사와 협의한다.",
                                 "⑤ 해지는 그 의사를 적은 서면이 상대방에게 도달한 날부터 15일 후에 효력이 생긴다.",
                                 "⑥ 해지 전에 체결된 회원의 공동구매 계약과 그에 따른 시공 · 하자보수 의무는 해지 후에도 유지된다."])
    article(d, 25, "권리 · 의무의 양도 금지", ["주관사는 협의회의 서면 승인 없이 이 협약상 권리나 의무를 제3자에게 양도하거나 재위탁하지 않는다."])
    article(d, 26, "신의 · 성실의 의무", ["협의회와 주관사는 신의 · 성실의 원칙에 따라 상호 협조와 신뢰로 이 협약을 성실히 지킨다."])
    article(d, 27, "분쟁 해결", ["이 협약에 정하지 않은 사항이나 이행에 관한 분쟁은 상호 합의로 원만히 해결하며, 합의가 이루어지지 않으면 협의회 소재지 관할 법원을 관할 법원으로 한다."])
    article(d, 28, "기타", ["① 이 협약의 이행 중 협의회가 인정하는 불가피한 사유가 생기면 양 당사자가 충분히 협의하여 조정할 수 있다.",
                          "② 이 협약을 증명하기 위하여 2부를 작성하여 기명날인한 후 각 1부씩 보관하며, 주관사는 이를 주관 실적 증빙으로 영구 보관한다.",
                          "③ 이 협약은 양 당사자가 서명 또는 날인한 날부터 효력이 생긴다."])
    article(d, 29, "특약 사항", ["다음은 주관사 제안서에서 확정된 내용으로, 이 협약과 같은 효력을 가진다. (제안서 · 협의 결과만 적는다)"])
    grid(d, [["번호", "특약 내용", "시기 · 횟수", "비고"]] + [[str(i), "", "", ""] for i in range(1, 9)], [1.4, 9.0, 3.4, 2.8])
    para(d, "20    년      월      일", 11, True, WD_ALIGN_PARAGRAPH.CENTER, before=8, after=8)
    sign_block(d, "[ 협 의 회 ]", "[ 주 관 사 ]")
    d.save(os.path.join(out, "엣지컴퍼니_입주박람회_주관사_협약서_표준양식.docx"))

def hwagin(out):
    d = base()
    title(d, "입주박람회 주관 실적 확인서", "(협약서 원본 미보관 단지 — 당시 협의회 대표 사실 확인)")
    para(d, "■ 주관사", 11, True, after=2)
    table(d, [["상    호", CO["name"], "대 표 자", f"대표이사 {CO['ceo']}"],
              ["사업자등록번호", CO["brn"], "소 재 지", CO["addr"]]], [2.8, 5.5, 2.3, 6.0])
    para(d, "■ 행사 내용", 11, True, after=2)
    table(d, [["단 지 명", "", "소 재 지", ""], ["세 대 수", "            세대", "입주 연월", "      년      월"],
              ["행사 기간", "      년    월    일 ~    월    일", "행사 장소", ""],
              ["선정 방식", "□ 공개 입찰  □ 협의회 지정  □ 기타", "협약 체결", "      년    월경  □ 서면  □ 기타"],
              ["방문 세대(선택)", "약          세대", "참여 업체(선택)", "약          개 업체"]], [2.8, 5.5, 2.3, 6.0])
    para(d, "위 단지 입주예정자협의회는 위 기간에 주식회사 엣지컴퍼니를 입주박람회 주관사로 선정·협약하여 "
            "입주박람회와 공동구매를 진행하였음을 확인합니다.", before=4, after=2)
    para(d, "※ 협약서 원본은 행사 종료 후 보관하지 않아 이 확인서로 협약 사실을 확인합니다. 이 확인서는 아래 작성일에 작성되었습니다.",
         9.5, color=RGBColor(0x55, 0x5B, 0x66), after=2)
    para(d, "※ 확인자는 이 확인서와 연락처가 입찰 심사 기관(입주예정자협의회)에 실적 증빙으로 제출되고, "
            "사실 확인을 위한 연락에 쓰이는 것에 동의합니다.   □ 동의함", 9.5, color=RGBColor(0x55, 0x5B, 0x66), after=8)
    para(d, "작성일 :  20    년      월      일", 11, True, WD_ALIGN_PARAGRAPH.CENTER, before=6, after=8)
    t = d.add_table(rows=5, cols=2); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    rows = [("[ 확 인 자 ]", ""), ("단 체 명 (당시)", "                    입주예정자협의회"),
            ("직위 (당시) / 성명", "                        /                    (서명 또는 인)"),
            ("연 락 처", ""), ("현재 직위 (해당 시)", "□ 입주자대표회의 (        )   □ 해당 없음")]
    for i, (a, b) in enumerate(rows):
        for j, v in enumerate((a, b)):
            c = t.cell(i, j); c.width = Cm([4.5, 12.1][j]); c.text = ""
            r = c.paragraphs[0].add_run(v); r.font.size = Pt(10); r.bold = (j == 0)
    d.save(os.path.join(out, "엣지컴퍼니_입주박람회_주관실적_확인서_양식.docx"))

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True); hyupyak(out); hwagin(out); print("ok", out)
