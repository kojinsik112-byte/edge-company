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
# ── 105동 경관바: 배치(1줄/프레임) × 전압(24V/12V) 4종을 같은 규칙으로 생성 ──
V = {
    "24V": dict(mod="24V 정전류 3구 모듈(고전압 LED형)", smps="DC24V 240W / 방수 IP67 / KC / -40℃ 동작", per="약 12m(바 3~4개)", price=150000,
                n={"1줄": 7, "프레임": 15}, grp={"1줄": "측벽 약 12m당 1대(부하 63%)", "프레임": "세로 2줄 각 7대 + 상단 가로 1대"}),
    "12V": dict(mod="12V 정전류 3구 모듈", smps="DC12V 150W / 방수 IP67 / KC / -40℃ 동작", per="약 6m(바 2개)", price=130000,
                n={"1줄": 13, "프레임": 28}, grp={"1줄": "측벽 약 6m당 1대(부하 50%)", "프레임": "세로 2줄 각 13대 + 상단 가로 2대"}),
}
L = {
    "1줄": dict(m=76, br=104, con=26, ac=90, rope=4, pro=3, desc="측벽 1줄",
               scope="105동 지상 27층(건물 높이 79.3m, 대지종횡단면도 A-019 기준) 측벽에 2층 바닥부터 옥상까지 수직 1줄 75.5m(견적 76m)로 산정했으며, 입면 실측 후 m당 단가로 정산합니다."),
    "프레임": dict(m=160, br=224, con=56, ac=200, rope=8, pro=4, desc="측벽 ∩ 프레임",
                scope="105동 지상 27층(건물 높이 79.3m, 대지종횡단면도 A-019 기준) 측벽 양쪽 모서리 세로 2줄(각 75.5m, 2층 바닥~옥상) + 상단 가로 약 9.2m = 160m로 산정했으며, 입면 실측 후 m당 단가로 정산합니다."),
}


def bldg105(layout: str, volt: str, alt: bool) -> dict:
    v, l = V[volt], L[layout]
    return {
        "key": f"1{'B' if layout == '프레임' else ''}_하늘에새긴빛_{layout}_{volt}",
        "alt": alt,
        "title": f"① 하늘에 새긴 빛 — 105동 경관바 ({layout}·{volt})",
        "건명": f"영주자이 시그니처 105동 외벽 경관조명 설치공사 「하늘에 새긴 빛」 ({l['desc']}, {volt})",
        "재료비": [
            ("LED 경관 라인바", f"알루미늄 경관케이스 100×85 / 광확산 UV PC(플로팅 커버) / 내부 {v['mod']} 나사 고정(공장 조립·밀봉) / 13W/m / 3000K 단색 / IP66 / 층고 맞춤 2.9m 모듈", "m", l["m"], 75000, "선세이브 검단 소비자가 75,000원/m 동일"),
            ("전원장치 SMPS", f"{v['smps']} / {v['grp'][layout]}", "EA", v["n"][layout], v["price"], "추정(방수형 SMPS 시세)"),
            ("SMPS 방수 정션박스·브래킷", "IP67 / SUS 브래킷 / 측벽 고정", "조", v["n"][layout], 30000, "추정"),
            ("전원함", "옥상 방수함 / 천문타이머 / 누전차단기 / 서지보호기(SPD)" + (" / 3회로" if layout == "프레임" else ""), "조", 1, 385000, "선세이브 검단 단가 동일"),
            ("AC 세로 간선", "F-CV 2.5㎟ 3C / 옥상 전원함 → 측벽 분산 SMPS", "m", l["ac"], 4000, "추정"),
            ("고정 브래킷·앵커", "SUS304 / 모듈당 4개소", "EA", l["br"], 3000, f"추정 — 2.9m 모듈 {l['br'] // 4}개"),
            ("방수 커넥터·연결선", "IP68 / 모듈 이음부", "EA", l["con"], 8000, "추정"),
        ],
        "노무비": [
            ("고공 로프작업", "2~3인 1팀 / 수직 라인 설치", "팀·일", l["rope"], 1100000, "선세이브 검단 동일(20m당 1팀·일)"),
            ("전기 전문공", "옥상 전원함·결선·절연저항 시험·점등 조정", "인", l["pro"], 300000, "선세이브·부산광고 동일"),
        ],
        "경비": [
            ("안전관리비", "로프 수직구명줄·추락방지·하부 통제", "일", l["rope"], 100000, "추정(선세이브는 미계상)"),
        ],
        "철거": None,
        "특기": [
            l["scope"],
            "3000K 단색 정적 점등이며, 색 변화·깜빡임 연출은 없습니다.",
            f"LED는 {v['mod']}을 공장에서 나사로 고정·결선·밀봉한 완제품이라 세로 설치에도 처지지 않으며, 범용 부품이라 장기 수리가 쉽습니다.",
            f"전원장치(방수 IP67)는 측벽에 {v['per']}마다 나눠 설치해 아래쪽까지 밝기가 고르게 유지됩니다.",
            "모듈은 층고에 맞춘 2.9m(최상단 3.0m)로 제작해 이음이 층 바닥선과 일치하며, 승강기 운반과 로프 작업이 안전한 길이입니다.",
            "광확산 커버는 온도에 따른 늘어남을 흡수하는 플로팅 구조로 고정합니다.",
            "손이 닿는 1층 필로티 구간은 파손·감전 예방을 위해 설치하지 않습니다.",
            "1차 전원(분전반 → 옥상 전원함 인입)은 발주처 제공 조건입니다.",
            "경관심의·인허가 및 전기요금은 견적에서 제외합니다.",
            "하자보수: 라인바·전원장치 3년.",
            f"공정: 발주 후 자재 입고 약 3주, 현장 시공 {l['rope']}일(기상에 따라 변동).",
            "결제: 계약금 50% / 준공 후 50%.",
        ],
    }


QUOTES = [
    bldg105("1줄", "12V", False),
    bldg105("1줄", "24V", True),
    bldg105("프레임", "12V", True),
    bldg105("프레임", "24V", True),
    {
        "key": "2_겨울빛의문_정문문주",
        "title": "② 겨울빛의 문 — 정문 문주",
        "건명": "영주자이 시그니처 정문 문주 윈터라이팅 설치 「겨울빛의 문」",
        "재료비": [
            ("LED 고드름 커튼 라이트", "전구색 / 드롭 0.2~0.6m 혼합 / 투명선 / IP65 / 상부 띠 전면 28.6m + 좌측 돌출부 3m", "m", 32, 12000, "추정"),
            ("고드름 걸이·하단 보조 와이어", "상부 띠 위에서 걸어 내림, 하단 2m마다 고정(무타공)", "m", 32, 3000, "추정"),
            ("LED 네온 라인", "전구색 / IP67 / 좌측 돌출부 하단 모서리, 클립 고정", "m", 4, 38000, "추정 — 네온플렉스+채널"),
            ("LED 눈꽃 모티브(대)", "Ø80cm / 전구색", "EA", 1, 200000, "추정"),
            ("LED 눈꽃 모티브(중)", "Ø55cm / 전구색", "EA", 1, 100000, "추정"),
            ("LED 눈꽃 모티브(소)", "Ø45cm / 백색", "EA", 1, 80000, "추정"),
            ("LED 반짝이 별", "Ø35cm / 전구색", "EA", 1, 50000, "추정"),
            ("와이어 원뿔 트리(대)", "H2.5m / 별 장식 / 전구색 / 지면 고정핀", "EA", 1, 350000, "추정"),
            ("와이어 원뿔 트리(소)", "H1.8m / 별 장식 / 전구색 / 지면 고정핀", "EA", 1, 250000, "추정"),
            ("수목 기둥 은하수 감기", "소나무 기둥 H4~6m / 1그루 은하수 약 60m / 전구색", "그루", 5, 180000, "추정 — 연출 이미지 5그루"),
            ("모티브 행잉 와이어·고정재", "투명 와이어 행잉(석재 무타공)", "조", 4, 10000, "추정"),
            ("전원함", "옥외 방수함 / 타이머 / 누전차단기", "조", 1, 385000, "선세이브 검단 단가 동일"),
            ("연장선·방수 분배기", "옥외용", "m", 100, 3000, "추정"),
        ],
        "노무비": [
            ("설치 전문공", "3인 × 2일 (1일차 고드름·라인·벽 모티브 / 2일차 트리·수목 감기)", "인", 6, 300000, "부산광고·선세이브 동일 30만/인"),
        ],
        "경비": [
            ("고소작업차(스카이)", "설치 2일", "대·일", 2, 500000, "부산광고 크레인 50만/대 동일"),
            ("안전관리비", "작업구역 통제·신호수", "일", 2, 50000, "추정"),
        ],
        "철거": {
            "노무비": [("철거 전문공", "3인 × 1일", "인", 3, 300000, "설치 단가 동일")],
            "경비": [("고소작업차(스카이)", "철거 1일", "대·일", 1, 500000, "설치 단가 동일"),
                     ("안전관리비", "작업구역 통제", "일", 1, 50000, "추정")],
        },
        "특기": [
            "도면(주문주 및 경비실#1, A-861·862) 치수 기준 산출이며, 현장 실측 후 정산합니다.",
            "고드름 라이트는 상부 띠 위에서 걸어 내리고 하단을 2m마다 보조 와이어로 잡아 바람에 흔들리지 않게 합니다.",
            "석재·유리·SUS 마감에 타공하지 않으며, 벽면 모티브는 투명 와이어로 행잉합니다.",
            "소나무는 못·스테이플 없이 감아 수피를 상하게 하지 않습니다.",
            "기존 경관조명·단지 로고 사인·주차장 출입구 조명은 그대로 유지합니다.",
            "점등 기간 중 불량 조명은 무상 교체합니다.",
            "1차 전원(가까운 분전반 → 전원함)은 발주처 제공 조건이며, 전기요금은 제외합니다.",
            "철거는 선택 항목이며, 위 「선택 항목」 금액으로 따로 표시했습니다.",
            "결제: 계약금 50% / 설치 완료 후 50%.",
        ],
    },
    {
        "key": "3_별빛이머무는정원",
        "title": "③ 별빛이 머무는 정원 — 잔디 정원",
        "건명": "영주자이 시그니처 단지 내 잔디 정원 윈터라이팅 설치 「별빛이 머무는 정원」",
        "재료비": [
            ("LED 사슴 조형물 — 서 있는 수사슴", "H1.5m / 와이어 프레임 / 전구색 LED / 옥외용", "EA", 1, 400000, "추정"),
            ("LED 사슴 조형물 — 아기사슴", "H1.1m / 와이어 프레임 / 전구색 LED / 옥외용", "EA", 1, 250000, "추정"),
            ("LED 토끼 조형물", "H0.5m / 와이어 프레임 / 전구색 LED / 옥외용", "EA", 2, 80000, "추정"),
            ("대형 별 조형물", "H1.2m / 이중 라인 / 전구색 / 지면 고정", "EA", 1, 250000, "추정"),
            ("LED 빛 구슬(와이어 볼)", "Ø60cm / 전구색", "EA", 1, 150000, "추정"),
            ("LED 빛 구슬(와이어 볼)", "Ø40cm / 전구색", "EA", 1, 90000, "추정"),
            ("바닥 꽂이형 LED 반짝이 별", "Ø40cm / 지주 포함 / 전구색", "EA", 6, 50000, "추정 — 연출 이미지 6개"),
            ("나무 행잉 라이트", "별 드롭 2 + 물방울 드롭 7 / 길이 0.6~1.2m / 전구색", "EA", 9, 30000, "추정 — 연출 이미지 9개"),
            ("조형물 고정 앵커", "잔디용 L앵커·와이어", "조", 6, 20000, "추정 — 사슴 2·토끼 2·별 1·구슬"),
            ("옥외 방수 연장선·분배기", "잔디 고정핀 포함", "m", 120, 3000, "추정"),
            ("전원함", "옥외 방수함 / 타이머 / 누전차단기", "조", 1, 385000, "선세이브 검단 단가 동일"),
        ],
        "노무비": [
            ("설치 전문공", "4인 × 1일 (조형물 조립·배치·행잉·배선)", "인", 4, 300000, "부산광고·선세이브 동일 30만/인"),
        ],
        "경비": [
            ("안전관리비", "보행자 통제", "일", 1, 50000, "추정"),
        ],
        "철거": {
            "노무비": [("철거 전문공", "2인 × 1일", "인", 2, 300000, "설치 단가 동일")],
            "경비": [("안전관리비", "보행자 통제", "일", 1, 50000, "추정")],
        },
        "특기": [
            "잔디 정원에 사슴 2점·토끼 2점·대형 별 1점·빛 구슬 2개·꽂이형 반짝이 별 6개를 배치하고, 큰 나무 가지에 행잉 라이트 9개를 매답니다. 세부 위치는 현장에서 협의합니다.",
            "큰 나무의 기존 은하수 조명과 보행등·스테인리스 조형물 등 기존 시설은 그대로 유지하며 견적에서 제외합니다.",
            "행잉 라이트는 끈 결속으로 매달아 수목을 상하게 하지 않습니다.",
            "잔디용 앵커·고정핀으로 고정하고 경계석에는 타공하지 않으며, 전선은 보행로를 가로지르지 않게 배선합니다.",
            "점등 기간 중 불량 조명은 무상 교체합니다.",
            "1차 전원은 발주처 제공 조건이며, 전기요금은 제외합니다.",
            "철거는 선택 항목이며, 위 「선택 항목」 금액으로 따로 표시했습니다.",
            "결제: 계약금 50% / 설치 완료 후 50%.",
        ],
    },
    {
        "key": "4_요정의숲",
        "title": "④ 요정의 숲 — 소나무 숲",
        "건명": "영주자이 시그니처 단지 내 소나무 숲 윈터라이팅 설치 「요정의 숲」",
        "재료비": [
            ("수관 은하수 — 대형 소나무", "H7~8m / 블루·그린·퍼플·화이트 혼합 / 투명선 / 1그루 약 200m", "그루", 3, 550000, "추정"),
            ("수관 은하수 — 중형 소나무", "H4~5m / 블루·그린·퍼플·화이트 혼합 / 투명선 / 1그루 약 100m", "그루", 4, 300000, "추정"),
            ("RGB 수목 업라이트", "스파이크형 투광등 / IP65 / 색 선택 리모컨", "EA", 4, 120000, "추정"),
            ("전원함", "옥외 방수함 / 타이머 / 누전차단기", "조", 1, 385000, "선세이브 검단 단가 동일"),
            ("옥외 방수 연장선·분배기", "화단 내 배선", "m", 150, 3000, "추정"),
        ],
        "노무비": [
            ("설치 전문공", "4인 × 2일 (수관 감기·업라이트·배선)", "인", 8, 300000, "부산광고·선세이브 동일 30만/인"),
        ],
        "경비": [
            ("고소작업대", "대형 소나무 수관 작업 2일", "대·일", 2, 500000, "부산광고 크레인 단가 동일"),
            ("안전관리비", "보행자 통제", "일", 2, 50000, "추정"),
        ],
        "철거": {
            "노무비": [("철거 전문공", "3인 × 1일", "인", 3, 300000, "설치 단가 동일")],
            "경비": [("고소작업대", "철거 1일", "대·일", 1, 500000, "설치 단가 동일"),
                     ("안전관리비", "보행자 통제", "일", 1, 50000, "추정")],
        },
        "특기": [
            "소나무 7그루(대형 3·중형 4)의 수관을 블루·그린·퍼플·화이트 은하수로 감싸고, 대형 나무 밑에 색 업라이트 4개를 설치합니다. 그루 수·크기는 현장 실측 후 그루 단가로 정산합니다.",
            "수목에 못·스테이플을 쓰지 않고 감아 수피와 가지를 상하게 하지 않습니다.",
            "화단 경계 조명·정원등·쉼터 파고라 등 기존 시설은 그대로 유지하며 견적에서 제외합니다.",
            "점등 기간 중 불량 조명은 무상 교체합니다.",
            "1차 전원은 발주처 제공 조건이며, 전기요금은 제외합니다.",
            "철거는 선택 항목이며, 위 「선택 항목」 금액으로 따로 표시했습니다.",
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
@page { size: A4; margin: 15mm 14mm 14mm; }
* { box-sizing: border-box; }
body { font-family: "Noto Sans KR", "Malgun Gothic", sans-serif; color: #1d2430; font-size: 9.4pt; margin: 0; line-height: 1.45; }
.eb { font-size: 7.4pt; letter-spacing: 3.2px; color: #b8913a; font-weight: 500; }
.mast { display: flex; justify-content: space-between; align-items: flex-end; padding-bottom: 3.5mm; border-bottom: 1.6px solid #b8913a; }
.mast h1 { font-family: "Noto Serif KR", serif; font-weight: 600; font-size: 25pt; letter-spacing: 9px; margin: 1mm 0 0; }
.mast .brand { text-align: right; }
.mast .brand b { font-family: "Noto Serif KR", serif; font-size: 14pt; font-weight: 600; display: block; }
.mast .brand span { font-size: 7.8pt; color: #6b7280; }
.rule2 { border-top: 0.6px solid #1d2430; margin-top: 0.8mm; }
.project { margin: 5mm 0 4mm; }
.project .pj { font-size: 9.5pt; color: #4a5563; margin-top: 1mm; }
.project .th { font-family: "Noto Serif KR", serif; font-size: 15pt; font-weight: 600; margin-top: 0.5mm; }
.project .th em { font-style: normal; color: #b8913a; }
.info { display: grid; grid-template-columns: 1fr 1fr; gap: 6mm; }
.info table { width: 100%; border-collapse: collapse; font-size: 8.8pt; }
.info td { padding: 1.3mm 0; border-bottom: 0.6px solid #e6e0d2; vertical-align: top; }
.info td.k { width: 23mm; color: #8a7a55; font-size: 8pt; letter-spacing: 0.5px; }
.info .to { font-size: 10.5pt; font-weight: 700; }
.sup { position: relative; }
.seal { position: absolute; right: 2mm; top: 3mm; width: 15mm; height: 15mm; border: 1px dashed #c9a85c; border-radius: 50%; color: #c9a85c; font-size: 8pt; display: flex; align-items: center; justify-content: center; }
.amount { margin: 5mm 0 4mm; display: flex; justify-content: space-between; align-items: center; background: #faf7f0; border-left: 3.5px solid #b8913a; padding: 3.5mm 5mm; }
.amount .lb { font-size: 8.6pt; color: #6b7280; }
.amount .kr { font-size: 9.6pt; margin-top: 0.8mm; }
.amount .big { font-family: "Noto Serif KR", serif; font-size: 21pt; font-weight: 600; text-align: right; }
.amount .vat { font-size: 8pt; color: #6b7280; text-align: right; }
table.q { width: 100%; border-collapse: collapse; font-size: 8.8pt; }
table.q th { text-align: left; font-weight: 500; font-size: 7.8pt; letter-spacing: 1px; color: #6b7280; padding: 1.6mm 1.8mm; border-bottom: 1.4px solid #1d2430; }
table.q td { padding: 1.7mm 1.8mm; border-bottom: 0.6px solid #ece6d9; vertical-align: top; }
table.q .n { text-align: right; white-space: nowrap; }
table.q .c { text-align: center; white-space: nowrap; }
tr.sec td { color: #b8913a; font-weight: 700; font-size: 8pt; letter-spacing: 1.2px; padding-top: 3.2mm; border-bottom: 0.8px solid #d9cfb8; }
tr.sec td span { color: #9aa3b2; font-weight: 400; letter-spacing: 2px; margin-left: 2mm; font-size: 7pt; }
tr.tot td { background: #faf7f0; font-weight: 600; }
tr.calc td { color: #374151; }
tr.grand td { font-weight: 700; font-size: 10pt; border-top: 1.4px solid #1d2430; border-bottom: none; padding-top: 2.4mm; }
tr.grand2 td { font-family: "Noto Serif KR", serif; font-weight: 600; font-size: 11pt; background: #faf7f0; }
.spec { color: #7b8391; font-size: 7.6pt; margin-top: 0.4mm; }
.sect { margin-top: 6mm; }
.sect h3 { font-family: "Noto Serif KR", serif; font-size: 11.5pt; font-weight: 600; margin: 0.8mm 0 2mm; }
ol.terms { margin: 0; padding: 0; list-style: none; counter-reset: t; font-size: 8.6pt; }
ol.terms li { counter-increment: t; position: relative; padding: 1mm 0 1mm 7mm; border-bottom: 0.5px dotted #e2dccd; }
ol.terms li::before { content: counter(t, decimal-leading-zero); position: absolute; left: 0; top: 1mm; color: #b8913a; font-weight: 600; font-size: 7.8pt; }
.sign { margin-top: 7mm; text-align: right; font-size: 9.4pt; line-height: 1.9; page-break-inside: avoid; }
.sign b { font-family: "Noto Serif KR", serif; font-size: 12pt; }
.foot { margin-top: 6mm; padding-top: 2mm; border-top: 0.6px solid #e2dccd; font-size: 7.4pt; color: #8b94a3; text-align: center; letter-spacing: 0.3px; }
"""


def rows_html(items, label, en):
    h = [f'<tr class="sec"><td colspan="5">{label}<span>{en}</span></td></tr>']
    for name, spec, unit, q, p, _ in items:
        h.append(
            f'<tr><td>{html.escape(name)}<div class="spec">{html.escape(spec)}</div></td>'
            f'<td class="c">{unit}</td><td class="n">{q:,}</td><td class="n">{p:,}</td>'
            f'<td class="n">{q * p:,}</td></tr>')
    return h


def cost_table(block, t, with_total_label="공급가액"):
    h = ['<table class="q"><tr><th style="width:50%">품명 · 규격</th><th class="c">단위</th><th class="n">수량</th>'
         '<th class="n">단가</th><th class="n">금액</th></tr>']
    if block.get("재료비"):
        h += rows_html(block["재료비"], "재료비", "MATERIALS")
        h.append(f'<tr class="tot"><td colspan="4">재료비 소계</td><td class="n">{t["a"]:,}</td></tr>')
    h += rows_html(block["노무비"], "노무비", "LABOR")
    h.append(f'<tr class="tot"><td colspan="4">노무비 소계</td><td class="n">{t["b"]:,}</td></tr>')
    h += rows_html(block["경비"], "경비", "EXPENSES")
    h.append(f'<tr><td>산재보험료<div class="spec">노무비 × 3.7%</div></td><td class="c">식</td><td class="n">1</td>'
             f'<td class="n">{t["sanjae"]:,}</td><td class="n">{t["sanjae"]:,}</td></tr>')
    h.append(f'<tr><td>고용보험료<div class="spec">노무비 × 1.01%</div></td><td class="c">식</td><td class="n">1</td>'
             f'<td class="n">{t["goyong"]:,}</td><td class="n">{t["goyong"]:,}</td></tr>')
    h.append(f'<tr class="tot"><td colspan="4">경비 소계</td><td class="n">{t["c"]:,}</td></tr>')
    h.append('<tr class="sec"><td colspan="5">원가 집계<span>SUMMARY</span></td></tr>')
    h.append(f'<tr class="calc"><td colspan="4">일반관리비 <span class="spec">(재료비+노무비+경비) × 6%</span></td><td class="n">{t["d"]:,}</td></tr>')
    h.append(f'<tr class="calc"><td colspan="4">이윤 <span class="spec">(노무비+경비+일반관리비) × 15%</span></td><td class="n">{t["e"]:,}</td></tr>')
    if t["cut"]:
        h.append(f'<tr class="calc"><td colspan="4">단수정리 <span class="spec">천원 미만 절사</span></td><td class="n">-{t["cut"]:,}</td></tr>')
    h.append(f'<tr class="grand"><td colspan="4">{with_total_label} <span class="spec">부가세 별도</span></td><td class="n">{t["supply"]:,}</td></tr>')
    h.append(f'<tr class="calc"><td colspan="4">부가가치세 10%</td><td class="n">{t["vat"]:,}</td></tr>')
    h.append(f'<tr class="grand2"><td colspan="4">합계 <span class="spec">부가세 포함</span></td><td class="n">{t["total"]:,}</td></tr>')
    h.append("</table>")
    return "\n".join(h)


def quote_html(qd: dict) -> str:
    t = calc(qd)
    title = qd["title"]
    theme, _, sub = title.partition(" — ")
    theme_name = theme[2:] if theme[:1] in "①②③④" else theme
    sup = "".join(f'<tr><td class="k">{k}</td><td>{html.escape(v)}</td></tr>' for k, v in COMPANY.items())
    body = [
        '<div class="mast"><div><div class="eb">QUOTATION</div><h1>견 적 서</h1></div>'
        f'<div class="brand"><b>{COMPANY["상호"]}</b><span>{COMPANY["면허"]}</span></div></div><div class="rule2"></div>',
        '<div class="project"><div class="eb">PROJECT</div><div class="pj">영주자이 시그니처 경관조명</div>'
        f'<div class="th"><em>「{html.escape(theme_name)}」</em> {html.escape(sub)}</div></div>',
        '<div class="info"><table>'
        '<tr><td class="k">수신</td><td class="to">&nbsp;</td></tr>'
        f'<tr><td class="k">건명</td><td>{html.escape(qd["건명"])}</td></tr>'
        f'<tr><td class="k">견적일</td><td>{DATE}</td></tr>'
        '<tr><td class="k">유효기간</td><td>견적일로부터 15일</td></tr></table>'
        f'<div class="sup"><table>{sup}</table><div class="seal">인</div></div></div>',
        '<div class="amount"><div><div class="lb">견적 금액 · 부가세 별도</div>'
        f'<div class="kr">금 {korean_won(t["supply"])}원정</div></div>'
        f'<div><div class="big">₩ {t["supply"]:,}</div><div class="vat">부가세 포함 ₩ {t["total"]:,}</div></div></div>',
        cost_table(qd, t),
    ]
    if qd.get("철거"):
        tt = calc(qd["철거"])
        body += ['<div class="sect"><div class="eb">OPTION</div><h3>선택 항목 — 시즌 종료 후 철거</h3>',
                 cost_table(qd["철거"], tt, "철거 공급가액"), "</div>"]
    body += ['<div class="sect"><div class="eb">TERMS</div><h3>견적 조건</h3><ol class="terms">'
             + "".join(f"<li>{html.escape(x)}</li>" for x in qd["특기"]) + "</ol></div>",
             f'<div class="sign">위와 같이 견적합니다.<br>{DATE}<br><b>{COMPANY["상호"]}</b> 대표이사 {COMPANY["대표"]} (인)</div>',
             f'<div class="foot">{COMPANY["상호"]} · {COMPANY["면허"]} · 사업자등록번호 {COMPANY["사업자등록번호"]} · '
             f'{COMPANY["주소"]} · ☎ {COMPANY["전화"]}</div>']
    return (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>견적서 {html.escape(title)}</title>'
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
    def row(qd):
        t = calc(qd)
        tt = calc(qd["철거"])["supply"] if qd.get("철거") else 0
        ws0.append([qd["title"], t["supply"], t["total"], tt or "—"])

    for qd in QUOTES:
        if not qd.get("alt"):
            row(qd)
    n = ws0.max_row
    ws0.append(["합계 (기본안)", f"=SUM(B4:B{n})", f"=SUM(C4:C{n})", f"=SUM(D4:D{n})"])
    for c in ws0[ws0.max_row]:
        c.font = Font(bold=True)
    alts = [qd for qd in QUOTES if qd.get("alt")]
    if alts:
        ws0.append([])
        ws0.append(["대안 (합계 미포함 — 105동 1줄·12V 대신 선택 시)"])
        ws0.cell(ws0.max_row, 1).font = Font(bold=True)
        for qd in alts:
            row(qd)
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
