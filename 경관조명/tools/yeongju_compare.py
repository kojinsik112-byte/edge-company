"""영주자이 105동 ㄷ자 경관 라인 — 시장 단가 비교 참고자료 (입예협 첨부용, A4 PDF).

선○○ 금액 = 타 단지(2026) 견적 사례의 항목·단가·제경비 산식을 본 현장 수량(ㄷ자 약 160m)에 적용한 '엣지컴퍼니 추정'.
          해당 업체가 본 현장에 낸 견적이 아님 → 문서에 명시. 업체명은 회장 지시로 '선○○' 표기.
엣지 금액 = yeongju_build.py 의 ㄷ자·12V 견적 그대로.
실행: python 경관조명/tools/yeongju_compare.py
"""
from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import yeongju_build as yb  # noqa: E402

OUT = Path.home() / "Desktop" / "경관조명 관련" / "영주자이 자료" / "입예협 첨부"
NAME = "(엣지컴퍼니) 105동 경관조명 시장단가 비교_261121"
L = 160  # ㄷ자 m

# ── 선○○ 사례 산식 (검단 350m 견적서: 측벽 267m + 옥탑 83m, 4개동) ──
def competitor(length: int) -> dict:
    bar = 75000 * length
    dimmer = round(16 * length / 350) * 88000
    smps = math.ceil(8 * length / 350) * 366000 + math.ceil(8 * length / 350) * 40000
    box = 2 * 385000
    misc = int(round(3200000 * length / 350, -4))
    mat_other = dimmer + smps + box + misc
    pro = math.ceil(12 * length / 350) * 300000
    rope = round(14 * length / 267) * 1100000
    labor = pro + rope
    tool = round(labor * 0.03)
    install = labor + tool
    sanjae, goyong, indirect = round(labor * 0.037), round(labor * 0.0101), round(labor * 0.125)
    admin = round((bar + mat_other + labor) * 0.06)
    profit = round((bar + mat_other + labor) * 0.15)
    overhead = sanjae + goyong + indirect + admin + profit
    total = bar + mat_other + install + overhead
    nego = round(total * 70000000 / 71824960)
    return dict(bar=bar, mat_other=mat_other, install=install, overhead=overhead, total=total, nego=nego,
                rope_n=round(14 * length / 267), pro_n=math.ceil(12 * length / 350))


def ours() -> dict:
    q = {x["key"]: x for x in yb.QUOTES}["1_하늘에새긴빛_ㄷ자_12V"]
    t = yb.calc(q)
    m = {n: qt * p for n, s, u, qt, p, b in q["재료비"]}
    bar = m["LED 경관 라인바"]
    return dict(bar=bar, mat_other=t["a"] - bar, install=t["b"], overhead=t["c"] + t["d"] + t["e"] - t["cut"],
                total=t["supply"], unit=[p for n, s, u, qt, p, b in q["재료비"] if n == "LED 경관 라인바"][0],
                rope_n=[qt for n, s, u, qt, p, b in q["노무비"] if n == "고공 로프작업"][0],
                pro_n=[qt for n, s, u, qt, p, b in q["노무비"] if n == "전기 전문공"][0])


def w(n):
    return f"{n:,}"


CSS = yb.CSS + """
.cmp { display: grid; grid-template-columns: 1fr 1fr 0.9fr; gap: 0; margin: 5mm 0 4mm; border: 0.8px solid #e2dccd; }
.cmp > div { padding: 4mm 5mm; }
.cmp .them { background: #fff; }
.cmp .us { background: #faf7f0; border-left: 3.5px solid #b8913a; }
.cmp .diff { background: #1d2430; color: #fff; }
.cmp .lb { font-size: 8pt; color: #6b7280; } .cmp .diff .lb { color: #c9b98f; }
.cmp .v { font-family: "Noto Serif KR", serif; font-size: 18pt; font-weight: 600; margin: 1mm 0; }
.cmp .s { font-size: 8pt; color: #6b7280; } .cmp .diff .s { color: #d9dee5; }
table.c2 { width: 100%; border-collapse: collapse; font-size: 8.8pt; margin-top: 2mm; }
table.c2 th { text-align: left; font-weight: 500; font-size: 7.8pt; color: #6b7280; padding: 1.6mm 1.8mm; border-bottom: 1.4px solid #1d2430; }
table.c2 td { padding: 2mm 1.8mm; border-bottom: 0.6px solid #ece6d9; vertical-align: top; }
table.c2 td.n, table.c2 th.n { text-align: right; white-space: nowrap; }
table.c2 td.us { background: #faf7f0; }
table.c2 tr.tot td { font-weight: 700; border-top: 1.4px solid #1d2430; }
.disc { margin-top: 4mm; padding: 2.5mm 4mm; background: #f6f8fa; font-size: 7.8pt; color: #4a5563; line-height: 1.65; }
@page { size: A4; margin: 12mm 13mm 10mm; }
.project { margin: 3.5mm 0 3mm; } .sect { margin-top: 4.5mm; } .cmp { margin: 3.5mm 0 2mm; }
table.c2 td { padding: 1.6mm 1.8mm; } table.c2 td:first-child { white-space: nowrap; }
.foot { margin-top: 4mm; }
"""


def build():
    c, o = competitor(L), ours()
    diff = c["nego"] - o["total"]
    rows = [
        ("라인바 제품", f"m당 {75000:,}원 × {L}m", w(c["bar"]), f"m당 {o['unit']:,}원 × {L}m", w(o["bar"])),
        ("전원·기타 자재", "SMPS·디머·전원함·전선 외 잡자재(1식)", w(c["mat_other"]), "방수 SMPS 28대·정션박스·전원함·간선·브래킷·커넥터", w(o["mat_other"])),
        ("설치비", f"로프 {c['rope_n']}팀·일, 전문공 {c['pro_n']}인, 공구손료", w(c["install"]), f"로프 {o['rope_n']}팀·일, 전문공 {o['pro_n']}인", w(o["install"])),
        ("제경비", "보험·간접노무비·일반관리비 6%·이윤 15%(제품비 포함)", w(c["overhead"]), "안전관리비·보험·일반관리비 6%·이윤 15%(재료비 제외)", w(o["overhead"])),
    ]
    trs = "".join(f'<tr><td><b>{a}</b></td><td>{b}</td><td class="n">{x}</td><td class="us">{d}</td><td class="n us">{y}</td></tr>' for a, b, x, d, y in rows)
    trs += (f'<tr class="tot"><td>합계</td><td>항목 합계 {w(c["total"])} → 사례 네고율(약 2.5%) 반영</td><td class="n">{w(c["nego"])}</td>'
            f'<td class="us">ㄷ자 약 {L}m · 부가세 별도</td><td class="n us">{w(o["total"])}</td></tr>')
    spec = [
        ("광원", "DC12V 3구 모듈", "DC12V 정전류 3구 모듈 — 공장에서 나사 고정·결선·밀봉한 완제품"),
        ("전원장치", "비방수 SMPS와 방수 SMPS 혼용", "방수 IP67·KC SMPS를 약 6m마다 분산 설치"),
        ("안전관리비", "별도 항목 없음", "로프 작업 안전관리비 반영(수직구명줄·추락방지·하부 통제)"),
        ("견적 구성", "전선 외 잡자재 「1식」 표기", "품목별 수량 × 단가 표기"),
        ("이윤 산정", "제품비+노무비의 15%", "노무비·경비·일반관리비의 15%(재료비 제외)"),
        ("하자보수", "AS 3년", "3년 — 같은 로트 예비 모듈 보관으로 교체 시 색 일치"),
    ]
    strs = "".join(f'<tr><td><b>{a}</b></td><td>{b}</td><td class="us">{d}</td></tr>' for a, b, d in spec)
    co = yb.COMPANY
    body = f'''<div class="mast"><div><div class="eb">PRICE COMPARISON</div><h1>시장 단가 비교</h1></div>
<div class="brand"><b>{co["상호"]}</b><span>{co["면허"]}</span></div></div><div class="rule2"></div>
<div class="project"><div class="eb">PROJECT</div><div class="pj">영주자이 시그니처 105동 외벽 경관조명</div>
<div class="th"><em>「하늘에 새긴 빛」</em> 측벽 ㄷ자 라인 약 {L}m</div></div>
<div class="cmp"><div class="them"><div class="lb">선○○ 단가 적용 (추정)</div><div class="v">₩ {w(c["nego"])}</div><div class="s">m당 약 {c["nego"] // L // 1000 / 10:.1f}만 원</div></div>
<div class="us"><div class="lb">엣지컴퍼니 제안</div><div class="v">₩ {w(o["total"])}</div><div class="s">m당 약 {o["total"] // L // 1000 / 10:.1f}만 원</div></div>
<div class="diff"><div class="lb">차이</div><div class="v">₩ {w(diff)}</div><div class="s">약 {diff / c["nego"]:.0%} 낮음</div></div></div>
<div class="sect"><div class="eb">BREAKDOWN</div><h3>금액 구성 비교 <span class="spec">부가세 별도 · 단위 원</span></h3>
<table class="c2"><tr><th>구분</th><th>선○○ 사례 산식</th><th class="n">선○○ 적용</th><th>엣지컴퍼니</th><th class="n">엣지 제안</th></tr>{trs}</table></div>
<div class="sect"><div class="eb">SPECIFICATION</div><h3>사양 · 조건 비교</h3>
<table class="c2"><tr><th style="width:16%">항목</th><th style="width:34%">선○○ (타 단지 견적 사례)</th><th>엣지컴퍼니</th></tr>{strs}</table></div>
<div class="disc">· 선○○ 금액은 2026년 타 단지 견적 사례의 항목·단가·제경비 산식을 본 현장 수량(ㄷ자 약 {L}m)에 적용한 엣지컴퍼니의 추정이며, 해당 업체가 본 현장에 제출한 견적이 아닙니다.<br>
· 정확한 비교는 각 업체로부터 같은 조건의 정식 견적을 받아 확인하시기 바랍니다.<br>
· 금액은 부가세 별도이며, 수량은 현장 실측 후 m당 단가로 정산합니다. 엣지컴퍼니 세부 내역은 별첨 견적서를 참고해 주십시오.</div>
<div class="foot">{co["상호"]} · {co["면허"]} · 사업자등록번호 {co["사업자등록번호"]} · ☎ {co["전화"]}</div>'''
    html = f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{NAME}</title><style>{CSS}</style></head><body>{body}</body></html>'
    OUT.mkdir(parents=True, exist_ok=True)
    hp = OUT / f"{NAME}.html"
    hp.write_text(html, encoding="utf-8")
    pdf = OUT / f"{NAME}.pdf"
    subprocess.run([yb.CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", hp.as_uri()],
                   check=True, capture_output=True, timeout=120)
    print(f"선○○ 항목합계 {w(c['total'])} / 네고반영 {w(c['nego'])} | 엣지 {w(o['total'])} | 차이 {w(diff)} ({diff / c['nego']:.1%})")
    print("OK ->", pdf)


if __name__ == "__main__":
    build()
