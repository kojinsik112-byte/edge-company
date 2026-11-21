"""영주자이 105동 경관 라인 — '더 낮은 금액, 더 많은 빛' 비교 참고자료 (입예협 첨부용, A4 1쪽).

선○○ = 경쟁사 견적 기준값 — 저장소 밖 로컬 파일(입예협 첨부/_비교기준_로컬.json)에서 읽음(경쟁사 자료는 GitHub에 올리지 않음).
엣지  = yeongju_build.py 의 ㄷ자·12V 견적(디밍·출장비 포함) + 같은 범위(두줄 134m) 환산 견적.
회장 방침(2026-11-21 최종): ㄷ자 2,650만 선 — 선○○보다 낮은 금액에, 장점(범위·사양·안전·투명성)까지 더한다.
실행: python 경관조명/tools/yeongju_compare.py
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import yeongju_build as yb  # noqa: E402

OUT = Path.home() / "Desktop" / "경관조명 관련" / "영주자이 자료" / "입예협 첨부"
NAME = "(엣지컴퍼니) 105동 경관조명 비교자료_261121"
_LOCAL = OUT / "_비교기준_로컬.json"  # 경쟁사 기준값 (로컬 전용)
if not _LOCAL.exists():
    raise SystemExit(f"경쟁사 기준값 파일이 없습니다: {_LOCAL}")
_CMP = json.loads(_LOCAL.read_text(encoding="utf-8"))
SUN = dict(m=_CMP["m"], total=_CMP["total"])


def ours(same_scope: bool = False) -> dict:
    q = copy.deepcopy({x["key"]: x for x in yb.QUOTES}["1_하늘에새긴빛_ㄷ자_12V"])
    m = 160
    if same_scope:  # 세로 2줄 × 약 67m, 상단 가로 없음
        m = 134
        qty = {"LED 경관 라인바": 134, "전원장치 SMPS": 24, "SMPS 방수 정션박스·브래킷": 24, "AC 세로 간선": 180, "디밍 신호선": 180,
               "고정 브래킷·앵커": 184, "방수 커넥터·연결선": 46}
        q["재료비"] = [(n, s, u, qty.get(n, qt), p, b) for n, s, u, qt, p, b in q["재료비"]]
        q["노무비"] = [(n, s, u, 6 if n == "고공 로프작업" else qt, p, b) for n, s, u, qt, p, b in q["노무비"]]
        q["경비"] = [(n, s, u, 6 if n == "안전관리비" else qt, p, b) for n, s, u, qt, p, b in q["경비"]]
    return dict(m=m, total=yb.calc(q)["supply"])


def w(n):
    return f"{int(n):,}"


CSS = yb.CSS + """
@page { size: A4; margin: 12mm 13mm 10mm; }
.project { margin: 3.5mm 0 3mm; } .sect { margin-top: 4.5mm; }
.cmp { display: grid; grid-template-columns: 1fr 1fr 1.05fr; margin: 3.5mm 0 2mm; border: 0.8px solid #e2dccd; }
.cmp > div { padding: 4mm 5mm; }
.cmp .them { background: #fff; } .cmp .us { background: #faf7f0; border-left: 3.5px solid #b8913a; }
.cmp .diff { background: #1d2430; color: #fff; }
.cmp .lb { font-size: 8pt; color: #6b7280; } .cmp .diff .lb { color: #c9b98f; }
.cmp .v { font-family: "Noto Serif KR", serif; font-size: 17pt; font-weight: 600; margin: 1mm 0; }
.cmp .diff .v { font-size: 13pt; line-height: 1.35; }
.cmp .s { font-size: 8pt; color: #6b7280; } .cmp .diff .s { color: #d9dee5; }
.val { display: grid; grid-template-columns: 1fr 1fr; gap: 2mm 6mm; margin-top: 2mm; }
.val div { font-size: 8.7pt; line-height: 1.5; padding: 2mm 0 2mm 7mm; position: relative; border-bottom: 0.5px dotted #e2dccd; }
.val div::before { content: attr(data-n); position: absolute; left: 0; top: 2mm; color: #b8913a; font-weight: 700; font-size: 8pt; }
.val b { display: block; font-size: 9.2pt; }
table.c2 { width: 100%; border-collapse: collapse; font-size: 8.6pt; margin-top: 2mm; }
table.c2 th { text-align: left; font-weight: 500; font-size: 7.8pt; color: #6b7280; padding: 1.5mm 1.8mm; border-bottom: 1.4px solid #1d2430; }
table.c2 td { padding: 1.5mm 1.8mm; border-bottom: 0.6px solid #ece6d9; vertical-align: top; }
table.c2 td:first-child { white-space: nowrap; }
table.c2 .n { text-align: right; white-space: nowrap; }
table.c2 .us { background: #faf7f0; }
.disc { margin-top: 3.5mm; padding: 2.5mm 4mm; background: #f6f8fa; font-size: 7.7pt; color: #4a5563; line-height: 1.6; }
.foot { margin-top: 3.5mm; }
.mast h1 { font-size: 21pt; letter-spacing: 3px; }
.cmp > div { padding: 3mm 4.5mm; }
.val div { padding: 1.2mm 0 1.2mm 7mm; } .val div::before { top: 1.2mm; }
.sect { margin-top: 3.2mm; } .sect h3 { margin: 0.5mm 0 1.4mm; }
table.c2 td { padding: 1.3mm 1.8mm; }
@page { size: A4; margin: 9mm 12mm 7mm; }
table.c2 { font-size: 8.2pt; } .val div { font-size: 8.3pt; } .val b { font-size: 8.9pt; }
.project { margin: 2.5mm 0 2mm; } .disc { margin-top: 2.5mm; } .foot { margin-top: 2.5mm; }
"""

VALUE = [
    ("ㄷ자 라인 160m", "상단 가로 9.2m 포함 — 두줄 134m보다 26m 더, 측벽 전체를 하나의 빛 프레임으로"),
    ("100×85 경관케이스", "더 넓은 발광면으로 멀리서도 굵고 또렷한 라인"),
    ("6m마다 분산한 방수 전원", "IP67·KC 전원장치를 나눠 달아 아래쪽까지 밝기가 고르고, 고장 시 일부 구간만 영향"),
    ("빛공해 대응 디밍", "천문타이머와 연동해 심야에는 자동으로 밝기를 낮춤"),
    ("안전과 투명한 견적", "로프 작업 안전관리비 반영, 모든 품목을 수량 × 단가로 표기"),
    ("면허 업체의 직접 책임", "전기공사업 면허 업체가 시공·하자보수 3년, 같은 로트 예비 모듈 보관"),
]

OURS_SPEC = [
    ("범위", "ㄷ자 라인 160m (상단 가로 9.2m 포함)"),
    ("라인바", "100×85 경관케이스 · DC12V 정전류 3구 · 공장 나사 고정·밀봉 · 13W/m"),
    ("전원장치", "방수 IP67·KC 디밍형 SMPS를 약 6m마다 분산"),
    ("빛공해 대응", "디밍 컨트롤러 — 천문타이머 연동 심야 자동 감광"),
    ("출장비", "장기 출장비(경북권) 160만 원 · 정문·정원·숲 동시 시공 시 추가 없음"),
    ("안전관리비", "로프 작업 안전관리비 반영"),
    ("견적 구성", "품목별 수량 × 단가 표기"),
]
SPEC = [(k, _CMP["spec"].get(k, "—"), v) for k, v in OURS_SPEC]


def build():
    s, o, o134 = SUN, ours(), ours(True)
    s_pm, o_pm = s["total"] / s["m"], o["total"] / o["m"]
    vals = "".join(f'<div data-n="{i + 1:02d}"><b>{a}</b>{b}</div>' for i, (a, b) in enumerate(VALUE))
    spec = "".join(f'<tr><td><b>{a}</b></td><td>{b}</td><td class="us">{d}</td></tr>' for a, b, d in SPEC)
    scope = (f'<tr><td><b>두줄 라인 134m</b> <span class="spec">세로 2줄 · 상단 가로 없음</span></td>'
             f'<td class="n">{w(s["total"])}</td><td class="n us">{w(o134["total"])}</td></tr>'
             f'<tr><td><b>ㄷ자 라인 160m</b> <span class="spec">상단 가로 9.2m 포함</span></td>'
             f'<td class="n">견적 없음</td><td class="n us">{w(o["total"])}</td></tr>')
    co = yb.COMPANY
    body = f'''<div class="mast"><div><div class="eb">VALUE COMPARISON</div><h1>더 낮은 금액, 더 많은 빛</h1></div>
<div class="brand"><b>{co["상호"]}</b><span>{co["면허"]} · ☎ {co["전화"]}</span></div></div><div class="rule2"></div>
<div class="project"><div class="eb">PROJECT</div><div class="pj">영주자이 시그니처 105동 외벽 경관조명</div>
<div class="th"><em>「하늘에 새긴 빛」</em> 측벽 경관 라인</div></div>
<div class="cmp"><div class="them"><div class="lb">선○○ 견적</div><div class="v">₩ {w(s["total"])}</div><div class="s">두줄 134m · m당 약 {round(s_pm / 1000):,}천 원</div></div>
<div class="us"><div class="lb">엣지컴퍼니 제안</div><div class="v">₩ {w(o["total"])}</div><div class="s">ㄷ자 160m · m당 약 {round(o_pm / 1000):,}천 원</div></div>
<div class="diff"><div class="lb">선○○보다 낮은 금액</div><div class="v">같은 11자 {round((s["total"] - o134["total"]) / 10000):,}만 원↓<br>ㄷ자 +26m {round((s["total"] - o["total"]) / 10000):,}만 원↓</div><div class="s">ㄷ자 m당 약 {(s_pm - o_pm) / s_pm:.0%} 낮음 · 상단 가로·디밍 포함</div></div></div>
<div class="sect"><div class="eb">WHAT WE ADD</div><h3>엣지컴퍼니가 더 드리는 것</h3><div class="val">{vals}</div></div>
<div class="sect"><div class="eb">SAME SCOPE</div><h3>같은 범위로 본 금액 <span class="spec">부가세 별도 · 단위 원</span></h3>
<table class="c2"><tr><th>범위</th><th class="n">선○○</th><th class="n">엣지컴퍼니</th></tr>{scope}</table></div>
<div class="sect"><div class="eb">SPECIFICATION</div><h3>사양 · 조건 비교</h3>
<table class="c2"><tr><th style="width:13%">항목</th><th style="width:38%">선○○</th><th>엣지컴퍼니</th></tr>{spec}</table></div>
<div class="disc">· 선○○ 금액·사양은 영주자이 105동 견적(두줄 라인 134m) 기준입니다. 엣지컴퍼니 두줄 134m 금액은 같은 단가 체계로 산출한 참고 금액이며, 기본 제안은 ㄷ자 160m입니다.<br>
· 금액은 부가세 별도, 수량은 현장 실측 후 m당 단가로 정산합니다. 세부 내역은 별첨 견적서를 참고해 주십시오.</div>'''
    html = f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{NAME}</title><style>{CSS}</style></head><body>{body}</body></html>'
    OUT.mkdir(parents=True, exist_ok=True)
    for old in list(OUT.glob("(엣지컴퍼니) 105동 경관조명 시장단가 비교_261121.*")) + list(OUT.glob("(엣지컴퍼니) 105동 경관조명 m당 단가 비교_261121.*")):
        old.unlink()
    hp = OUT / f"{NAME}.html"
    hp.write_text(html, encoding="utf-8")
    pdf = OUT / f"{NAME}.pdf"
    subprocess.run([yb.CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", hp.as_uri()],
                   check=True, capture_output=True, timeout=120)
    print(f"선○○ {w(s['total'])} (m당 {round(s_pm):,}) | 엣지 ㄷ자 {w(o['total'])} (m당 {round(o_pm):,}) | 엣지 두줄134 {w(o134['total'])}")
    print("OK ->", pdf)


if __name__ == "__main__":
    build()
