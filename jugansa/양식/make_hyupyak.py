"""입주박람회 주관 협약서(표준) + 주관 실적 확인서 — 편집 가능한 .docx 양식.
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

def hyupyak(out):
    d = base()
    title(d, "입주박람회 주관사 협약서", "공동구매 · 입주박람회 위탁 운영 및 사후관리에 관한 협약")
    para(d, "○○○○ 입주예정자협의회(이하 \"협의회\")와 주식회사 엣지컴퍼니(이하 \"주관사\")는 아래 단지의 입주박람회와 "
            "공동구매를 입주예정자의 이익을 최우선으로 투명하고 공정하게 운영하기 위하여 다음과 같이 협약(이하 \"이 협약\")을 체결한다.", after=6)
    table(d, [["단 지 명", "", "소 재 지", ""], ["세 대 수", "            세대", "입주 예정", "      년      월 ~      월"],
              ["시행 · 시공사", "", "선정 근거", "      년    월    일 공고 · □ 공개 입찰  □ 기타"],
              ["협의회 대표", "회장                (연락처               )", "주관사 담당", "주관사업 총괄 본부장 윤현욱"]], [2.6, 5.7, 2.6, 5.7])

    chapter(d, "제1장  총칙")
    article(d, 1, "목적", ["이 협약은 협의회가 주관사에 입주박람회와 공동구매 운영을 위탁하고, 주관사가 입주예정자에게 검증된 업체·투명한 가격·"
                          "책임 있는 시공과 A/S를 제공하기 위하여 양 당사자의 권리·의무와 업무 절차를 정함을 목적으로 한다."])
    article(d, 2, "용어의 정의", ["① \"입주예정자\"란 위 단지의 분양(임대) 계약자와 그 가족을 말한다.",
                               "② \"참여 업체\"란 공개 심사를 거쳐 박람회·공동구매에 참여하도록 선정된 품목별 업체를 말한다.",
                               "③ \"공동구매 계약\"이란 입주예정자와 참여 업체 사이에 체결되는 개별 공급·시공 계약을 말한다.",
                               "④ \"사전 공개 단가\"란 박람회 전에 협의회와 확정하여 입주예정자에게 공개하는 품목별 판매가를 말한다."])
    article(d, 3, "협약 기간", ["① 이 협약의 기간은 체결일부터 공동구매 품목 중 무상 A/S 기간이 가장 긴 품목의 만료일까지로 한다.",
                              "② 박람회·공동구매 운영 업무는 입주 지정기간 종료일까지로 하고, 그 이후에는 A/S 통합 창구와 민원 처리 업무를 수행한다."])
    article(d, 4, "협약의 구성", ["이 협약은 본문과 다음 부속서로 구성되며, 부속서는 본문과 같은 효력을 가진다. 본문과 부속서가 다르면 본문이 우선한다.",
                                "[부속서 1] 업무 범위 및 일정 · [부속서 2] 업체 선정 및 가격 검수 기준 · [부속서 3] 계약 취소·환불 및 A/S 처리 기준 · "
                                "[부속서 4] 입주민 혜택 합의서"])

    chapter(d, "제2장  업무와 역할")
    article(d, 5, "주관사의 업무", [
        "① 박람회 기획·운영: 행사장 대관, 부스 배치, 안내·주차·안전 인력 배치, 동선·비상구 계획, 홍보물 제작.",
        "② 참여 업체 모집과 심사 자료 준비: 사업자·면허·보험·시공 실적·A/S 체계를 확인한 자료를 협의회에 제출한다.",
        "③ 사전 공개 단가 확정과 가격 검수: 시중가·온라인 최저가와 비교한 자료를 협의회에 제출한다.",
        "④ 계약·시공·A/S 통합 창구 운영과 입주예정자 민원 처리.",
        "⑤ 사전점검·실측 일정 조율 등 입주 준비 지원.",
        "⑥ 업무 보고: 부속서 1에서 정한 시기마다 진행 상황과 결과를 협의회에 서면(전자우편 포함)으로 보고한다."])
    article(d, 6, "협의회의 역할", ["① 입주예정자 대상 공지·안내와 행사 일정 협의.",
                                  "② 참여 업체 선정 심사 참여와 사전 공개 단가 승인.",
                                  "③ 주관사 업무 수행에 필요한 범위의 자료 제공과 협조(개인정보는 제13조에 따른다).",
                                  "④ 협의회는 박람회 개최와 관련된 비용을 부담하지 않는다."])
    article(d, 7, "전담 조직", ["주관사는 이 단지 전담 책임자(PM)와 분야별 담당자를 지정하여 협의회에 서면으로 알리고, 교체할 때에는 사전에 협의회와 협의한다."])

    chapter(d, "제3장  박람회와 공동구매 운영")
    article(d, 8, "행사 일정 및 장소", ["① 행사 기간 :      년    월    일 ~    월    일 (   일간)     ② 장소 :",
                                    "③ 일정·장소·운영 시간은 양 당사자가 협의하여 확정하고, 변경할 때에는 서면으로 합의한다.",
                                    "④ 천재지변, 감염병, 행사장 사정 등 불가항력으로 행사를 할 수 없을 때에는 양 당사자가 협의하여 일정을 다시 정한다."])
    article(d, 9, "참여 업체 선정", ["① 참여 업체는 부속서 2의 기준에 따라 공개 심사로 선정하며, 주관사는 협의회의 승인 없이 업체를 추가하거나 바꾸지 않는다.",
                                   "② 주관사가 직접 공급·시공하는 품목이 있으면 심사 전에 그 사실을 협의회에 알린다.",
                                   "③ 참여 업체가 계약 의무를 위반하면 주관사는 협의회와 협의하여 참여 제한 등 필요한 조치를 한다."])
    article(d, 10, "가격과 단가 공개", ["① 판매가는 사전 공개 단가를 원칙으로 하며, 결제 방법(카드·현금 등)에 따라 차등하지 않는다.",
                                     "② 공동구매 후 동일 조건의 제품이 시중에서 사전 공개 단가보다 낮게 확인되면, 주관사는 부속서 2에서 정한 방법으로 처리한다.",
                                     "③ 입주민 혜택에 드는 비용은 공동구매 단가에 전가하지 않는다."])
    article(d, 11, "홍보와 표시", ["① 주관사가 제작하는 홍보물은 게시 전에 협의회의 확인을 받는다.",
                                 "② 주관사와 참여 업체는 사실과 다르거나 과장된 표현(최고·유일 등 입증할 수 없는 표현)을 사용하지 않는다."])

    chapter(d, "제4장  입주예정자 보호")
    article(d, 12, "계약 취소·환불과 A/S", ["① 품목별 취소·환불 기준과 A/S 처리 기준은 부속서 3에 따른다.",
                                          "② 시공 하자가 발생하면 주관사는 해당 업체에 보수를 요청하고, 업체가 정해진 기간 안에 이행하지 않으면 주관사가 책임지고 처리한다.",
                                          "③ 참여 업체의 폐업 등으로 A/S가 어려워진 경우에도 주관사는 대체 업체를 지정하여 남은 A/S 기간 동안 처리한다."])
    article(d, 13, "개인정보 보호", ["① 주관사는 입주예정자의 개인정보를 행사 안내·계약·시공·A/S 목적으로만 처리하고, 「개인정보 보호법」에 따른 동의를 받는다.",
                                   "② 참여 업체에 개인정보를 제공할 때에는 필요한 범위로 한정하고, 목적 달성 후 지체 없이 파기하도록 관리·감독한다."])
    article(d, 14, "안전 관리와 보험", ["① 주관사는 행사장 안전 계획(인력·동선·비상구·응급 대응)을 세워 행사 전 협의회에 알린다.",
                                     "② 주관사는 행사 기간·장소에 맞춰 행사주최자배상책임보험에 가입하고, 협의회가 요청하면 가입증명서를 제출한다."])

    chapter(d, "제5장  공정성과 책임")
    article(d, 15, "금지 행위", ["① 주관사와 참여 업체는 협의회 임원·운영위원과 그 가족 개인에게 금품·향응·편의를 제공하지 않는다.",
                               "② 협의회 임원·운영위원은 업체 선정과 관련하여 개인적 이익을 요구하거나 받지 않는다.",
                               "③ 이를 위반한 사실이 확인되면 상대방은 즉시 이 협약을 해지할 수 있다."])
    article(d, 16, "이해관계 고지", ["주관사는 시행사·시공사·분양대행사·옵션 업체와의 이해관계(지분·하도급·협력 등록 등)를 협약 전에 서면으로 고지하고, 협약 기간 중 새로 생기면 지체 없이 알린다."])
    article(d, 17, "비밀 유지", ["양 당사자는 협약 과정에서 알게 된 상대방의 영업상 비밀과 입주예정자 정보를 협약 기간과 그 종료 후에도 제3자에게 누설하지 않는다."])
    article(d, 18, "손해배상", ["어느 한쪽이 고의 또는 과실로 이 협약을 위반하여 상대방이나 입주예정자에게 손해를 입힌 경우 그 손해를 배상한다. "
                              "다만 불가항력으로 인한 경우는 제외한다."])
    article(d, 19, "이행 담보", ["협의회가 요청하면 주관사는 이 협약의 이행을 담보하기 위한 방법(이행보증증권 등)과 금액을 협의회와 협의하여 정한다."])

    chapter(d, "제6장  해지와 기타")
    article(d, 20, "협약 해지", ["① 어느 한쪽이 이 협약을 위반하고 서면 시정 요구를 받은 날부터 14일 이내에 시정하지 않으면 상대방은 서면으로 협약을 해지할 수 있다.",
                               "② 해지 전에 체결된 공동구매 계약과 그에 따른 시공·A/S 의무는 해지 후에도 유지된다."])
    article(d, 21, "권리·의무의 양도 금지", ["양 당사자는 상대방의 서면 동의 없이 이 협약상 권리·의무를 제3자에게 양도하거나 재위탁하지 않는다."])
    article(d, 22, "통지", ["이 협약에 따른 통지는 전문에 적은 연락처로 서면(전자우편·문자 포함)으로 하며, 연락처가 바뀌면 지체 없이 알린다."])
    article(d, 23, "분쟁 해결", ["이 협약에 관한 분쟁은 상호 협의로 해결하고, 협의가 이루어지지 않으면 협의회 소재지 관할 법원을 관할 법원으로 한다."])
    article(d, 24, "기타", ["① 이 협약에 정하지 않은 사항은 관계 법령과 일반 관례에 따르되, 양 당사자가 협의하여 서면으로 정한다.",
                          "② 이 협약서는 2부를 작성하여 양 당사자가 기명날인한 후 각 1부씩 보관하며, 주관사는 이를 주관 실적 증빙으로 영구 보관한다."])
    para(d, "20    년      월      일", 11, True, WD_ALIGN_PARAGRAPH.CENTER, before=8, after=8)
    sign_block(d, "[ 협 의 회 ]", "[ 주 관 사 ]")

    d.add_page_break()
    title(d, "[부속서 1]  업무 범위 및 일정")
    grid(d, [["단계", "시기(안)", "주관사 업무", "협의회 보고 · 승인"],
             ["① 협약·준비", "협약 후 1개월", "전담 PM 지정 · 연간 일정표 · 수요조사 설계", "일정표 승인"],
             ["② 업체 모집·심사", "박람회 4~6개월 전", "품목 선정 · 업체 공개 모집 · 서류·현장 확인 자료", "심사 참여 · 선정 승인"],
             ["③ 단가 확정", "박람회 2~3개월 전", "시중가·온라인 최저가 비교표 · 사전 공개 단가안", "단가 승인 · 공지"],
             ["④ 박람회", "입주 2~3개월 전", "행사 운영 · 안전 관리 · 계약 창구", "현장 참관"],
             ["⑤ 시공·입주", "입주 지정기간", "시공 일정 관리 · 하자 접수 · 민원 처리", "주간 현황 보고"],
             ["⑥ 사후관리", "A/S 기간 종료까지", "A/S 통합 창구 · 처리 결과 회신", "분기 보고"],
             ["⑦ 결과 보고", "행사 후 30일 이내", "방문 세대 · 품목별 계약 건수 · 민원 처리 현황", "결과 보고서 수령"]],
         [2.6, 3.0, 6.6, 4.4])
    para(d, "※ 시기는 입주 일정에 따라 협의회와 협의하여 조정한다.", 9, color=RGBColor(0x55, 0x5B, 0x66))

    title(d, "[부속서 2]  업체 선정 및 가격 검수 기준")
    grid(d, [["구분", "기준"],
             ["참가 자격", "사업자등록 · 해당 품목 면허(필요 시) · 영업배상책임보험 등 · 최근 시공 실적 · A/S 인력·기간 명시"],
             ["심사 방법", "서류 심사 + 가격·품질 비교 + 협의회 심사(필요 시 업체 발표) · 결과는 협의회 공지"],
             ["가격 검수", "동일 모델·규격 기준 시중가·온라인 최저가 비교표 제출 · 박람회 전 사전 공개 단가 확정"],
             ["가격 사후 확인", "공동구매 후 동일 조건 최저가가 사전 공개 단가보다 낮게 확인되면 차액 처리 방법을 협의회와 정함(        )"],
             ["업체 관리", "계약 위반·민원 반복 업체는 협의회와 협의하여 참여 제한"]], [3.4, 13.2])

    title(d, "[부속서 3]  계약 취소·환불 및 A/S 처리 기준")
    grid(d, [["구분", "기준"],
             ["취소·환불", "품목별 취소 기한(예: 시공일 7일 전 · 15일 전) 안에 취소하면 계약금 전액 환불 · 맞춤 제작 품목은 제작 지시 전까지"],
             ["하자 접수", "주관사 통합 창구(전화 · 문자 · 온라인)로 접수 · 접수 후 24시간 이내 업체 배정"],
             ["처리 기한", "현장 확인 3일 이내 · 보수 완료 7일 이내(부품 수급 등 사유가 있으면 일정 안내)"],
             ["미이행 시", "업체가 기한 안에 처리하지 않으면 주관사가 대체 업체로 처리하고 비용은 해당 업체에 청구"],
             ["무상 A/S 기간", "품목별 계약서에 명시 · 업체 폐업 시에도 남은 기간 주관사가 처리"]], [3.4, 13.2])

    title(d, "[부속서 4]  입주민 혜택 합의서")
    grid(d, [["혜택 항목", "내용 · 규모", "대상", "제공 시기 · 방법"],
             ["", "", "", ""], ["", "", "", ""], ["", "", "", ""], ["", "", "", ""]], [3.6, 6.0, 2.6, 4.4])
    para(d, "※ 혜택 비용은 주관사가 부담하며 공동구매 단가에 전가하지 않는다. 항목·규모를 바꿀 때에는 양 당사자가 서면으로 합의한다.",
         9, color=RGBColor(0x55, 0x5B, 0x66), after=8)
    para(d, "협의회 대표            (서명)          주관사 대표이사 고진식            (인)", 10.5, True, WD_ALIGN_PARAGRAPH.CENTER, before=6)
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
