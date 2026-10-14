# -*- coding: utf-8 -*-
"""협력사 ㈜더에이치엠컴퍼니 — 조합·유상옵션 수행실적 1쪽 (요약제안서 네이비·골드 기본틀과 같은 디자인).

조합 행사·유상옵션 실적이 필요한 입찰에 별도 첨부용. 엣지컴퍼니 단독 실적이 아니므로
제목·각주에 '협력사'를 반드시 표기한다(공고 '실적 과장·명의대여' 무효 사유 대비, 본부장 10-14).

사용: python build_hm.py [사진폴더] [출력폴더]
  사진폴더 = hm01.jpg … (협력사 실적표 이미지에서 잘라낸 단지 사진, 깃 제외)
"""
import html
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..", "요약제안서", "assets", "fonts")
IMG = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(HERE, "img")
OUT = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else HERE
NAME = "엣지컴퍼니_협력사_조합유상옵션_수행실적"
PARTNER = "㈜더에이치엠컴퍼니"

# (연월, 단지명, 세대수, [구분], 사진번호) — 협력사 실적표 원문 그대로. 세대수 None = 확인 필요
RECORDS = [
    ("2027.06", "창원 푸르지오 파크베뉴", 570, ["입주박람회"], 1),
    ("2026.09", "창원 센트럴 아이파크", 1509, ["입주박람회 1·2차", "현장박람회"], 2),
    ("2026.08", "반포 래미안 트리니원", 2091, ["입주박람회 1·2차", "현장박람회"], 3),
    ("2026.03", "영등포 자이 디그니티", 707, ["유상옵션", "입주박람회", "현장박람회"], 4),
    ("2026.01", "철산 자이 브리에르", 1490, ["유상옵션", "입주박람회", "현장박람회"], 5),
    ("2025.04", "창원자이 시그니처", 789, ["유상옵션", "입주박람회", "현장박람회"], 6),
    ("2025.04", "장위자이 레디언트", 2840, ["유상옵션", "입주박람회", "현장박람회"], 7),
    ("2024.10", "광명 호반써밋 그랜드에비뉴", 1051, ["유상옵션", "현장박람회"], 8),
    ("2023.02", "흑석자이", 1772, ["공동구매", "현장박람회"], 9),
    ("2022.12", "남천(삼익타워) 자이", 913, ["입주박람회", "현장박람회"], 10),
    ("2021.05", "서초그랑자이", 1445, ["유상옵션", "현장박람회"], 11),
    ("2021.04", "의왕더샵캐슬", 941, ["입주박람회"], 12),
    ("2021.02", "마포프레스티지자이", 1694, ["공동구매", "현장박람회"], 13),
    ("2020.11", "래미안목동아델리체", 1497, ["입주박람회"], 14),
    ("2019.02", "백련산파크자이", 678, ["유상옵션", "현장박람회"], 15),
    ("2019.02", "래미안길음센터피스", 2352, ["입주박람회", "현장박람회"], 16),
    ("2018.11", "답십리파크자이", 802, ["유상옵션", "입주박람회", "현장박람회"], 17),
    ("2018.05", "서울숲리버뷰자이", 1034, ["입주박람회", "현장박람회"], 18),
    # 본부장 10-14 추가 — 연월·세대수·사진 받으면 채움
    (None, "전주 기자촌", None, ["유상옵션"], None),
    (None, "두산 우암1구역", None, ["조합 주관", "유상옵션"], None),
]


def t(s):
    s = html.escape(s, quote=False)
    return re.sub(r"\[\[(.+?)\]\]", r"<em>\1</em>", s)


def tile(r):
    ym, nm, hh, tags, ph = r
    img = (f'<div class="im" style="background-image:url(\'file://{IMG}/hm{ph:02d}.jpg\')"></div>' if ph
           else '<div class="im ph">사진 확인 필요</div>')
    chips = "".join(f'<i class="{"op" if "옵션" in g else ""}">{t(g)}</i>' for g in ["조합"] + [g for g in tags if g != "조합 주관"]
                    if True)
    head = f'{ym} · ' if ym else '<span class="todo">연월 확인</span> · '
    hhs = f'{hh:,}세대' if hh else '<span class="todo">세대수 확인</span>'
    return f'<div class="tl">{img}<div class="cp"><b>{t(nm)}</b><span class="d">{head}{hhs}</span><p>{chips}</p></div></div>'


def build():
    known = [r for r in RECORDS if r[2]]
    total = sum(r[2] for r in known)
    opt = sum(1 for r in RECORDS if "유상옵션" in r[3])
    big = sum(1 for r in known if r[2] >= 1000)
    css = f"""
@font-face{{font-family:'Gelasio';font-weight:700;src:url('file://{BASE}/gelasio-latin-700-normal.woff2') format('woff2')}}
@page{{size:297mm 210mm;margin:0}}
:root{{--bg:#0D1E33;--gold:#EBCB8F;--gold2:#C8A86A;--ink:#F4F6F9;--sub:#B4BECA;--mute:#8595A8;--line:rgba(255,255,255,.13);
--sans:'Pretendard','Malgun Gothic',sans-serif;--serif:Georgia,'Gelasio',serif}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:#0D1E33}}
body{{font-family:var(--sans);color:var(--ink);-webkit-print-color-adjust:exact;print-color-adjust:exact;word-break:keep-all}}
em{{font-style:normal;color:var(--gold)}}
.page{{width:297mm;height:210mm;position:relative;overflow:hidden;background:var(--bg);display:flex;flex-direction:column;padding:34px 44px 0}}
.hd{{display:flex;justify-content:space-between;align-items:center;height:28px}}
.hd .l{{display:flex;align-items:center;gap:16px}}
.logo{{font-family:var(--serif);font-weight:700;font-size:27px;color:var(--gold);line-height:1}}
.sec{{font-size:13px;font-weight:700;letter-spacing:.34em;color:var(--gold2)}}
.hd .r{{font-size:12.5px;color:var(--mute)}}
.tw{{display:flex;justify-content:space-between;align-items:flex-end;gap:24px;margin-top:10px}}
h1{{font-size:33px;font-weight:800;line-height:1.2}}
.lead{{font-size:16px;color:var(--sub);margin-top:6px;line-height:1.45}}
.st{{display:flex;gap:10px}}
.st div{{border:1px solid rgba(200,168,106,.45);background:rgba(200,168,106,.08);border-radius:10px;padding:7px 14px;text-align:center;min-width:112px;white-space:nowrap}}
.st b{{display:block;font-size:24px;font-weight:800;color:var(--gold);line-height:1.1}}
.st span{{font-size:11.5px;color:var(--sub);letter-spacing:.04em}}
.rule{{height:1.5px;margin:12px 0 12px;background:linear-gradient(90deg,var(--gold2),rgba(200,168,106,.35) 55%,rgba(200,168,106,0))}}
.grid{{flex:1;min-height:0;display:grid;grid-template-columns:repeat(5,1fr);grid-auto-rows:1fr;gap:9px}}
.tl{{display:flex;flex-direction:column;border:1px solid var(--line);border-radius:9px;overflow:hidden;background:rgba(255,255,255,.04);min-height:0}}
.im{{flex:1;min-height:0;background-size:cover;background-position:center}}
.im.ph{{display:flex;align-items:center;justify-content:center;font-size:12px;color:var(--gold2);border-bottom:1px dashed var(--gold2);background:rgba(200,168,106,.06)}}
.cp{{padding:5px 8px 6px;height:62px;flex:none}}
.cp b{{display:block;font-size:13px;font-weight:700;line-height:1.25;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.cp .d{{display:block;font-size:11px;color:var(--sub);margin-top:1px;font-variant-numeric:tabular-nums}}
.cp p{{display:flex;flex-wrap:nowrap;overflow:hidden;gap:3px;margin-top:4px}}
.cp i{{font-style:normal;font-size:9px;font-weight:700;padding:1px 5px;border-radius:3px;border:1px solid rgba(255,255,255,.22);color:var(--sub);white-space:nowrap}}
.cp i:first-child{{border-color:var(--gold2);color:var(--gold)}}
.cp i.op{{background:var(--gold2);border-color:var(--gold2);color:#0D1E33}}
.todo{{background:#FDE68A;color:#0D1E33;padding:0 4px;border-radius:2px;font-weight:700}}
.nt{{font-size:11.5px;color:var(--mute);margin-top:8px}}
.ft{{height:36px;display:flex;justify-content:space-between;align-items:center;font-size:12px;color:var(--mute)}}
"""
    body = f"""<div class="page">
<div class="hd"><div class="l"><span class="logo">EG</span><span class="sec">협력사 수행실적</span></div><span class="r">재개발·재건축 조합 · 유상옵션</span></div>
<div class="tw"><div><h1>{t("조합 · [[유상옵션]] 수행실적")}</h1>
<div class="lead">협력사 {PARTNER} — 서울·수도권·창원 재개발·재건축 조합의 입주박람회와 유상옵션 현장을 맡아 왔습니다.</div></div>
<div class="st"><div><b>{len(RECORDS)}</b><span>조합 현장</span></div><div><b>{opt}</b><span>유상옵션 현장</span></div><div><b>{big}</b><span>1,000세대 이상</span></div><div><b>{total:,}</b><span>세대(확인분)</span></div></div></div>
<div class="rule"></div>
<div class="grid">{''.join(tile(r) for r in RECORDS)}</div>
<div class="nt">※ 협력사 {PARTNER} 수행 실적입니다(엣지컴퍼니 단독 실적 아님). 연월·구분은 협력사 실적표 기준이며, 2026년 이후 연월은 진행 예정 일정입니다.</div>
<div class="ft"><span>주식회사 엣지컴퍼니 · 대표이사 고진식</span><span>EDGE COMPANY</span></div>
</div>"""
    doc = f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{NAME}</title><style>{css}</style></head><body>{body}</body></html>'
    os.makedirs(OUT, exist_ok=True)
    h = os.path.join(OUT, NAME + ".html")
    open(h, "w", encoding="utf-8").write(doc)
    ch = os.environ.get("CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    pdf = os.path.join(OUT, NAME + ".pdf")
    subprocess.run([ch, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    "--allow-file-access-from-files", f"--print-to-pdf={pdf}", "file://" + h],
                   check=True, capture_output=True)
    todo = sum(1 for r in RECORDS if not r[0] or not r[2])
    print(pdf, f"[확인 필요 {todo}단지]" if todo else "")


if __name__ == "__main__":
    build()
