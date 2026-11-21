"""영주자이 시그니처 경관조명 견적서 빌더.

데이터(아래 QUOTES) 한 곳만 고치면 → 발송용 엑셀·PDF 3종 + 내부용 원가마진 엑셀이 다시 만들어진다.
원가계산 방식: 재료비 + 노무비 + 경비(산재·고용 포함) + 일반관리비 6% + 이윤 15%(노무비+경비+일반관리비 기준, 재료비 제외)
공급가액 천원 미만 절사, 부가세 10% 별도.

실행:  python 경관조명/tools/yeongju_build.py
출력:  바탕화면\\경관조명 관련\\영주자이 자료\\견적서\\
"""
from __future__ import annotations

import html
import subprocess
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

OUT = Path.home() / "Desktop" / "경관조명 관련" / "영주자이 자료" / "견적서"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DATE = "2026년 11월 21일"

COMPANY = {
    "상호": "㈜엣지컴퍼니",
    "대표": "고진식",
    "사업자등록번호": "508-81-42798",
    "면허": "전기공사업 등록 제 울산-00821호",
    "주소": "울산광역시 울주군 온산읍 온산로 615-1",
    "전화": "1533-3210",
}

RATE_SANJAE, RATE_GOYONG, RATE_ADMIN, RATE_PROFIT = 0.037, 0.0101, 0.06, 0.15

# (품명, 규격, 단위, 수량, 판매단가, 단가근거[내부용])
QUOTES = [
    {
        "key": "1_105동수직조명",
        "title": "105동 외벽 수직 경관조명",
        "건명": "영주자이 시그니처 105동 외벽 수직 경관조명 설치공사",
        "재료비": [
            ("LED 경관 라인바", "알루미늄 경관케이스 100×85×1000 / 광확산 UV PC / DC24V 13W/m / 3000K / IP66", "m", 80, 75000, "선세이브 검단 소비자가 75,000원/m 동일"),
            ("전원장치 SMPS 방수형", "DC24V 400W / KC", "EA", 4, 200000, "추정(방수형 SMPS 시세)"),
            ("전원함", "옥외 방수함 / 천문타이머 / 누전차단기", "조", 1, 385000, "선세이브 검단 단가 동일"),
            ("DC 급전선", "F-CV 4㎟ 2C / 20m 간격 4개소 급전", "m", 140, 5000, "추정"),
            ("고정 브래킷·앵커", "SUS304 / 0.5m 간격", "EA", 160, 3000, "추정"),
            ("방수 커넥터·연결선", "IP68", "EA", 80, 5000, "추정"),
        ],
        "노무비": [
            ("고공 로프작업", "2~3인 1팀 / 수직 라인 설치", "팀·일", 4, 1100000, "선세이브 검단 동일(14팀/4개동)"),
            ("전기 전문공", "옥상 전원·결선·절연저항 시험", "인", 3, 300000, "선세이브·부산광고 동일"),
        ],
        "경비": [
            ("안전관리비", "로프 수직구명줄·추락방지·하부 통제", "일", 4, 100000, "추정(선세이브는 미계상)"),
        ],
        "철거": None,
        "특기": [
            "수량은 105동 지상 27층 기준 수직 1줄 약 80m로 산정했으며, 입면 실측 후 m당 단가로 정산합니다.",
            "1차 전원(분전반 → 옥상 전원함 인입)은 발주처 제공 조건입니다.",
            "경관심의·인허가 및 전기요금은 견적에서 제외합니다.",
            "하자보수: 라인바·전원장치 3년.",
            "공정: 발주 후 자재 입고 약 3주, 현장 시공 4일(기상에 따라 변동).",
            "결제: 계약금 50% / 준공 후 50%.",
        ],
    },
    {
        "key": "2_정문문주",
        "title": "정문 문주 윈터라이팅",
        "건명": "영주자이 시그니처 정문 문주 윈터라이팅 설치",
        "재료비": [
            ("LED 은하수(상업용)", "IP65 / 전구색·백색 트윙클 혼합 / 선 색상 문주 마감색 맞춤(투명·검정) / 상부 띠 전면·양측면 37.6㎡", "m", 420, 2500, "추정 — 도면 산출 376m + 예비 10%"),
            ("LED 고드름 라이트", "백색 / 드롭 0.3~0.6m / 상부 띠 하단", "m", 40, 6000, "추정"),
            ("LED 눈꽃 모티브(대)", "900×900 / 전구색 / 3D 아크릴", "EA", 1, 250000, "추정 — 범어자이 자재비 역산"),
            ("LED 눈꽃 모티브(중)", "600×600 / 백색", "EA", 2, 100000, "추정"),
            ("LED 별 모티브", "450×450 / 전구색", "EA", 2, 80000, "추정"),
            ("LED 스노우폴", "1000mm 8본 1세트 / 백색", "세트", 3, 50000, "추정"),
            ("고정 와이어망·결속재", "비천공 고정(석재·유리 무타공)", "㎡", 38, 5000, "추정"),
            ("전원함", "옥외 방수함 / 타이머 / 누전차단기", "조", 1, 385000, "선세이브 검단 단가 동일"),
            ("연장선·방수 분배기", "옥외용", "m", 60, 3000, "추정"),
        ],
        "노무비": [
            ("설치 전문공", "3인 × 2일", "인", 6, 300000, "부산광고·선세이브 동일 30만/인"),
        ],
        "경비": [
            ("고소작업차(스카이)", "설치 2일", "대·일", 2, 500000, "부산광고 크레인 50만/대 동일"),
            ("안전관리비", "작업구역 통제·신호수", "일", 2, 50000, "추정"),
        ],
        "철거": {
            "노무비": [("철거 전문공", "3인 × 1일", "인", 3, 300000, "설치 단가 동일")],
            "경비": [("고소작업차(스카이)", "철거 1일", "대·일", 1, 500000, "설치 단가 동일")],
        },
        "특기": [
            "도면(주문주 및 경비실#1, A-861·862) 치수 기준 산출이며, 현장 실측 후 정산합니다.",
            "석재·유리·SUS 마감에 타공하지 않는 비천공 방식으로 고정합니다.",
            "은하수 선 색상을 문주 마감색에 맞춰, 소등 시(주간)에는 눈에 잘 띄지 않습니다.",
            "기존 경관조명과 단지 로고 사인은 그대로 유지합니다.",
            "점등 기간 중 불량 모티브·은하수는 무상 교체합니다.",
            "1차 전원(가까운 분전반 → 전원함)은 발주처 제공 조건이며, 전기요금은 제외합니다.",
            "철거는 선택 항목이며 아래 별도 금액입니다.",
            "결제: 계약금 50% / 설치 완료 후 50%.",
        ],
    },
    {
        "key": "3_공원트리",
        "title": "단지 내 공원 트리조명",
        "건명": "영주자이 시그니처 단지 내 공원 트리조명 설치",
        "재료비": [
            ("대형 크리스마스 트리", "H3.0m / LED 전구색 내장 / 오너먼트 장식 / 옥외용", "EA", 1, 1200000, "추정"),
            ("트리 고정 세트", "받침·지선 와이어·모래주머니", "조", 1, 100000, "추정"),
            ("수목 은하수 감기", "H3~4m 수목 1그루(기둥+수관, 은하수 약 100m)", "그루", 8, 250000, "추정 — 그루 수 실측 후 정산"),
            ("관목 은하수 망", "회양목 등 / 전구색·백색·그린", "㎡", 30, 8000, "추정"),
            ("전원함", "옥외 방수함 / 타이머 / 누전차단기", "조", 1, 385000, "선세이브 검단 단가 동일"),
            ("연장선·방수 분배기", "옥외용", "m", 100, 3000, "추정"),
        ],
        "노무비": [
            ("설치 전문공", "3인 × 2일", "인", 6, 300000, "부산광고·선세이브 동일 30만/인"),
        ],
        "경비": [
            ("고소작업대", "수목 상부 작업 1일", "대·일", 1, 500000, "부산광고 크레인 단가 동일"),
            ("안전관리비", "보행자 통제", "일", 2, 50000, "추정"),
        ],
        "철거": {
            "노무비": [("철거 전문공", "3인 × 1일", "인", 3, 300000, "설치 단가 동일")],
            "경비": [("고소작업대", "철거 1일", "대·일", 1, 500000, "설치 단가 동일")],
        },
        "특기": [
            "수목 8그루·관목 30㎡ 기준이며, 현장 실측 후 그루·㎡ 단가로 정산합니다.",
            "수목에 못·스테이플을 쓰지 않는 감기 방식으로 수목 손상이 없습니다.",
            "트리 설치 위치는 발주처와 협의합니다.",
            "점등 기간 중 불량 조명은 무상 교체합니다.",
            "1차 전원은 발주처 제공 조건이며, 전기요금은 제외합니다.",
            "철거는 선택 항목이며 아래 별도 금액입니다.",
            "결제: 계약금 50% / 설치 완료 후 50%.",
        ],
    },
]


def r0(x: float) -> int:
    return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def calc(block: dict) -> dict:
    a = sum(q * p for _, _, _, q, p, _ in block.get("재료비", []))
    b = sum(q * p for _, _, _, q, p, _ in block.get("노무비", []))
    c_items = sum(q * p for _, _, _, q, p, _ in block.get("경비", []))
    sanjae, goyong = r0(b * RATE_SANJAE), r0(b * RATE_GOYONG)
    c = c_items + sanjae + goyong
    d = r0((a + b + c) * RATE_ADMIN)
    e = r0((b + c + d) * RATE_PROFIT)
    raw = a + b + c + d + e
    supply = raw // 1000 * 1000
    vat = supply // 10
    return dict(a=a, b=b, c=c, sanjae=sanjae, goyong=goyong, d=d, e=e, raw=raw,
                cut=raw - supply, supply=supply, vat=vat, total=supply + vat)


DIG = "영일이삼사오육칠팔구"


def korean_won(n: int) -> str:
    if n == 0:
        return "영"
    units, small = ["", "만", "억", "조"], ["", "십", "백", "천"]
    out, i = [], 0
    while n:
        n, chunk = divmod(n, 10000)
        if chunk:
            s, j = "", 0
            while chunk:
                chunk, d = divmod(chunk, 10)
                if d:
                    s = ("" if d == 1 and j else DIG[d]) + small[j] + s
                j += 1
            out.insert(0, s + units[i])
        i += 1
    return "".join(out)


# ───────────────────────── HTML / PDF ─────────────────────────
CSS = """
@page { size: A4; margin: 14mm 12mm; }
* { box-sizing: border-box; }
body { font-family: "Malgun Gothic", "맑은 고딕", sans-serif; color: #1d2430; font-size: 10.5pt; margin: 0; }
h1 { text-align: center; letter-spacing: 18px; font-size: 24pt; margin: 4mm 0 6mm; }
.top { display: flex; gap: 4mm; }
.top > div { flex: 1; border: 1.2px solid #1d2430; padding: 3mm 4mm; }
.top .l p { margin: 1.6mm 0; }
.to { font-size: 12.5pt; font-weight: 700; border-bottom: 1px solid #1d2430; padding-bottom: 1mm; }
.co table { width: 100%; border-collapse: collapse; font-size: 9.5pt; }
.co td { padding: 1mm 1.5mm; border-bottom: 1px solid #e3e7ec; }
.co td:first-child { width: 26mm; color: #5b6573; }
.sum { margin: 5mm 0 3mm; border: 1.2px solid #1d2430; background: #f6f8fa; padding: 3mm 4mm; font-size: 12pt; font-weight: 700; }
.sum span { font-weight: 400; font-size: 10pt; color: #5b6573; }
table.q { width: 100%; border-collapse: collapse; font-size: 9.3pt; }
table.q th, table.q td { border: 1px solid #b9c0c9; padding: 1.4mm 1.6mm; vertical-align: middle; }
table.q th { background: #eef1f4; }
table.q td.n { text-align: right; white-space: nowrap; }
table.q td.c { text-align: center; white-space: nowrap; }
tr.sec td { background: #f6f8fa; font-weight: 700; }
tr.tot td { font-weight: 700; background: #eef1f4; }
tr.grand td { font-weight: 700; font-size: 11pt; border-top: 2px solid #1d2430; }
.spec { color: #5b6573; font-size: 8.6pt; }
h3 { font-size: 11pt; margin: 5mm 0 2mm; }
ol { margin: 0; padding-left: 5mm; font-size: 9.3pt; } li { margin: 0.8mm 0; }
.foot { margin-top: 5mm; text-align: right; font-size: 10pt; }
"""


def rows_html(items, label):
    h = [f'<tr class="sec"><td colspan="6">{label}</td></tr>']
    for name, spec, unit, q, p, _ in items:
        h.append(
            f'<tr><td>{html.escape(name)}<div class="spec">{html.escape(spec)}</div></td>'
            f'<td class="c">{unit}</td><td class="n">{q:,}</td><td class="n">{p:,}</td>'
            f'<td class="n">{q * p:,}</td><td></td></tr>')
    return h


def cost_table(block, t, with_total_label="공급가액"):
    h = ['<table class="q"><tr><th style="width:46%">품명 / 규격</th><th>단위</th><th>수량</th>'
         '<th>단가</th><th>금액</th><th style="width:9%">비고</th></tr>']
    if block.get("재료비"):
        h += rows_html(block["재료비"], "1. 재료비")
        h.append(f'<tr class="tot"><td colspan="4">재료비 소계</td><td class="n">{t["a"]:,}</td><td></td></tr>')
    h += rows_html(block["노무비"], "2. 노무비")
    h.append(f'<tr class="tot"><td colspan="4">노무비 소계</td><td class="n">{t["b"]:,}</td><td></td></tr>')
    h += rows_html(block["경비"], "3. 경비")
    h.append(f'<tr><td>산재보험료<div class="spec">노무비 × 3.7%</div></td><td class="c">식</td><td class="n">1</td>'
             f'<td class="n">{t["sanjae"]:,}</td><td class="n">{t["sanjae"]:,}</td><td></td></tr>')
    h.append(f'<tr><td>고용보험료<div class="spec">노무비 × 1.01%</div></td><td class="c">식</td><td class="n">1</td>'
             f'<td class="n">{t["goyong"]:,}</td><td class="n">{t["goyong"]:,}</td><td></td></tr>')
    h.append(f'<tr class="tot"><td colspan="4">경비 소계</td><td class="n">{t["c"]:,}</td><td></td></tr>')
    h.append(f'<tr><td colspan="4">일반관리비 <span class="spec">(재료비+노무비+경비) × 6%</span></td><td class="n">{t["d"]:,}</td><td></td></tr>')
    h.append(f'<tr><td colspan="4">이윤 <span class="spec">(노무비+경비+일반관리비) × 15%</span></td><td class="n">{t["e"]:,}</td><td></td></tr>')
    if t["cut"]:
        h.append(f'<tr><td colspan="4">단수정리 <span class="spec">천원 미만 절사</span></td><td class="n">-{t["cut"]:,}</td><td></td></tr>')
    h.append(f'<tr class="grand"><td colspan="4">{with_total_label} (부가세 별도)</td><td class="n">{t["supply"]:,}</td><td></td></tr>')
    h.append(f'<tr><td colspan="4">부가세 10%</td><td class="n">{t["vat"]:,}</td><td></td></tr>')
    h.append(f'<tr class="grand"><td colspan="4">합계 (부가세 포함)</td><td class="n">{t["total"]:,}</td><td></td></tr>')
    h.append("</table>")
    return "\n".join(h)


def quote_html(qd: dict) -> str:
    t = calc(qd)
    co = "".join(f"<tr><td>{k}</td><td>{html.escape(v)}</td></tr>" for k, v in COMPANY.items())
    body = [
        f"<h1>견 적 서</h1>",
        '<div class="top"><div class="l">',
        f"<p>견적일 : {DATE}</p>",
        '<p class="to">수 신 : &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 귀중</p>',
        f"<p>건 명 : <b>{html.escape(qd['건명'])}</b></p>",
        "<p>아래와 같이 견적합니다.</p><p>견적 유효기간 : 견적일로부터 15일</p>",
        f'</div><div class="co"><table>{co}<tr><td>공급자</td><td>{COMPANY["상호"]} 대표 {COMPANY["대표"]} (인)</td></tr></table></div></div>',
        f'<div class="sum">총 금액 : 금 {korean_won(t["supply"])}원정 (₩{t["supply"]:,}) <span>부가세 별도 · 부가세 포함 ₩{t["total"]:,}</span></div>',
        cost_table(qd, t),
    ]
    if qd.get("철거"):
        tt = calc(qd["철거"])
        body += ["<h3>선택 항목 — 시즌 종료 후 철거</h3>", cost_table(qd["철거"], tt, "철거 공급가액")]
    body += ["<h3>특기사항</h3><ol>" + "".join(f"<li>{html.escape(s)}</li>" for s in qd["특기"]) + "</ol>",
             f'<div class="foot">{COMPANY["상호"]} · {COMPANY["면허"]} · ☎ {COMPANY["전화"]}</div>']
    return (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>견적서 {qd["title"]}</title>'
            f"<style>{CSS}</style></head><body>{''.join(body)}</body></html>")


def to_pdf(html_path: Path, pdf_path: Path) -> None:
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf_path}", html_path.as_uri()],
                   check=True, capture_output=True, timeout=120)


# ───────────────────────── Excel ─────────────────────────
THIN = Side(style="thin", color="B9C0C9")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
HEAD = PatternFill("solid", fgColor="EEF1F4")
SEC = PatternFill("solid", fgColor="F6F8FA")
WON = '#,##0'


def write_sheet(ws, qd, internal: bool):
    ws["A1"] = f"견적서 — {qd['건명']}"
    ws["A1"].font = Font(bold=True, size=14)
    ws["A2"] = f"견적일 {DATE} · 공급자 {COMPANY['상호']} ({COMPANY['면허']})"
    cols = ["구분", "품명", "규격", "단위", "수량", "단가", "금액"]
    if internal:
        cols += ["원가 단가(회장 입력)", "원가 금액", "마진", "마진율", "단가 근거"]
    ws.append([])
    ws.append(cols)
    hr = ws.max_row
    for c in ws[hr]:
        c.font, c.fill, c.border = Font(bold=True), HEAD, BOX
    refs = {}

    def section(label, items, key):
        start = ws.max_row + 1
        for name, spec, unit, q, p, basis in items:
            r = ws.max_row + 1
            row = [label, name, spec, unit, q, p, f"=E{r}*F{r}"]
            if internal:
                row += [None, f"=IF(H{r}=\"\",\"\",E{r}*H{r})", f"=IF(H{r}=\"\",\"\",G{r}-I{r})",
                        f"=IF(H{r}=\"\",\"\",J{r}/G{r})", basis]
            ws.append(row)
        end = ws.max_row
        r = end + 1
        ws.append(["", f"{label} 소계", "", "", "", "", f"=SUM(G{start}:G{end})"])
        for c in ws[r]:
            c.font, c.fill = Font(bold=True), SEC
        refs[key] = f"G{r}"
        return start, end

    blocks = [qd] + ([qd["철거"]] if qd.get("철거") else [])
    for bi, blk in enumerate(blocks):
        p = "" if bi == 0 else "철거·"
        if bi:
            ws.append([])
            ws.append(["선택 항목 — 시즌 종료 후 철거"])
            ws.cell(ws.max_row, 1).font = Font(bold=True)
        if blk.get("재료비"):
            section(p + "재료비", blk["재료비"], "a")
        else:
            refs["a"] = None
        section(p + "노무비", blk["노무비"], "b")
        es, ee = section(p + "경비", blk["경비"], "c0")
        b, a = refs["b"], refs["a"] or "0"
        lines = [
            ("산재보험료 (노무비×3.7%)", f"=ROUND({b}*{RATE_SANJAE},0)"),
            ("고용보험료 (노무비×1.01%)", f"=ROUND({b}*{RATE_GOYONG},0)"),
        ]
        rs = ws.max_row + 1
        for lab, f in lines:
            ws.append(["", lab, "", "", "", "", f])
        cr = ws.max_row + 1
        ws.append(["", "경비 합계", "", "", "", "", f"={refs['c0']}+G{rs}+G{rs + 1}"])
        dr = cr + 1
        ws.append(["", "일반관리비 (재료비+노무비+경비)×6%", "", "", "", "", f"=ROUND(({a}+{b}+G{cr})*{RATE_ADMIN},0)"])
        er = dr + 1
        ws.append(["", "이윤 (노무비+경비+일반관리비)×15%", "", "", "", "", f"=ROUND(({b}+G{cr}+G{dr})*{RATE_PROFIT},0)"])
        sr = er + 1
        ws.append(["", f"{p}공급가액 (천원 미만 절사, 부가세 별도)", "", "", "", "", f"=ROUNDDOWN({a}+{b}+G{cr}+G{dr}+G{er},-3)"])
        ws.append(["", "부가세 10%", "", "", "", "", f"=ROUNDDOWN(G{sr}*0.1,0)"])
        ws.append(["", f"{p}합계 (부가세 포함)", "", "", "", "", f"=G{sr}+G{sr + 1}"])
        for r in (cr, sr, sr + 2):
            for c in ws[r]:
                c.font = Font(bold=True)
        if internal and blk.get("재료비") is not None:
            pass
    ws.append([])
    ws.append(["특기사항"])
    ws.cell(ws.max_row, 1).font = Font(bold=True)
    for i, s in enumerate(qd["특기"], 1):
        ws.append([f"{i}.", s])
    for row in ws.iter_rows(min_row=hr):
        for c in row:
            if c.column in (5, 6, 7, 8, 9, 10):
                c.number_format = WON
            if c.column == 11:
                c.number_format = "0.0%"
            c.alignment = Alignment(vertical="center", wrap_text=c.column in (2, 3, 12))
    widths = {"A": 10, "B": 30, "C": 46, "D": 7, "E": 8, "F": 12, "G": 14, "H": 16, "I": 13, "J": 13, "K": 9, "L": 34}
    for k, v in widths.items():
        ws.column_dimensions[k].width = v


def build_xlsx(path: Path, internal: bool):
    wb = Workbook()
    ws0 = wb.active
    ws0.title = "총괄"
    ws0.append([f"영주자이 시그니처 경관조명 견적 총괄 ({DATE})"])
    ws0["A1"].font = Font(bold=True, size=14)
    ws0.append([])
    ws0.append(["공종", "공급가액(부가세 별도)", "합계(부가세 포함)", "선택: 철거 공급가액"])
    for c in ws0[3]:
        c.font, c.fill, c.border = Font(bold=True), HEAD, BOX
    for qd in QUOTES:
        t = calc(qd)
        tt = calc(qd["철거"])["supply"] if qd.get("철거") else 0
        ws0.append([qd["title"], t["supply"], t["total"], tt or "—"])
    n = ws0.max_row
    ws0.append(["합계", f"=SUM(B4:B{n})", f"=SUM(C4:C{n})", f"=SUM(D4:D{n})"])
    for c in ws0[ws0.max_row]:
        c.font = Font(bold=True)
    for row in ws0.iter_rows(min_row=4):
        for c in row[1:]:
            c.number_format = WON
    ws0.append([])
    ws0.append(["※ 총괄표 금액은 작성 시점 값입니다. 각 시트 단가를 고치면 시트 합계는 자동으로 다시 계산됩니다."])
    for k, v in {"A": 26, "B": 22, "C": 22, "D": 22}.items():
        ws0.column_dimensions[k].width = v
    for qd in QUOTES:
        write_sheet(wb.create_sheet(qd["key"]), qd, internal)
    wb.save(path)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "_html").mkdir(exist_ok=True)
    for qd in QUOTES:
        hp = OUT / "_html" / f"견적서_{qd['key']}.html"
        hp.write_text(quote_html(qd), encoding="utf-8")
        to_pdf(hp, OUT / f"견적서_{qd['key']}.pdf")
        t = calc(qd)
        extra = f" / 철거 {calc(qd['철거'])['supply']:,}" if qd.get("철거") else ""
        print(f"{qd['title']}: 공급가액 {t['supply']:,} (VAT포함 {t['total']:,}){extra}")
    build_xlsx(OUT / "영주자이_견적서_발송용.xlsx", internal=False)
    build_xlsx(OUT / "영주자이_원가마진_내부용.xlsx", internal=True)
    print("OK ->", OUT)


if __name__ == "__main__":
    main()
