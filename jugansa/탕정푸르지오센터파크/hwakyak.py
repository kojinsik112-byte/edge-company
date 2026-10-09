# -*- coding: utf-8 -*-
"""대표이사 실적 확약서 (1,000세대 이상 입주박람회 주관 실적) + 별첨 2 입예협 카페 공지 캡처.

실적은 증빙이 있는 것만 넣는다: NICE 연혁 7건 + 카페 공지(주관사 명의 게시)로 확인되는 2건.
송도 더퍼스트비치는 카페에서 '협력업체'로만 확인돼 제외(본부장 10-09).
캡처는 입주민 닉네임(동·호수)을 픽셀로 가린 뒤 넣는다. 캡처 원본·결과 PDF·HTML은 깃 제외.

사용: python hwakyak.py <탕정|철산> <capture_dir> [YYYY.MM.DD]
  capture_dir 안에: sasang_1.png, sasang_2.png, daesung.png (원본 캡처)
"""
import html
import os
import pathlib
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "요약제안서")]
from build import find_chrome  # noqa: E402

e = html.escape

CLIENTS = {
    "탕정": ("아산 탕정 푸르지오 센터파크 입주예정자협의회", "아산 탕정 푸르지오 센터파크 입주예정자협의회 주관사 입찰 선정 공고",
             "5항 17)", "6항 5) · 8항 4)", "엣지컴퍼니_탕정푸르지오센터파크_실적확약서"),
    "철산": ("철산역 자이(조합) 입주예정자협의회", "철산역 자이 입주예정자협의회 주관사 입찰 공고",
             "입찰 참가 자격", "공고 제재 조항", "엣지컴퍼니_철산역자이_실적확약서"),
}

# (주관 시기, 단지명, 지역, 세대수, 근거)
RECS = [
    ("2022.12 ~ 2023.06", "부산사상 중흥S-클래스 그랜드센트럴", "부산 사상", 1572, "입예협 카페 공지 (별첨 2-①②)"),
    ("2023.03", "힐스테이트 포항", "경북 포항", 1717, "NICE 연혁"),
    ("2023.11", "레이카운티", "부산", 4470, "NICE 연혁"),
    ("2024.06", "두산위브더제니스 센트럴사하", "부산", 1643, "NICE 연혁"),
    ("2024.11 ~ 2025.12", "에코델타 대성베르힐", "부산 에코델타시티", 1120, "입예협 카페 공지 (별첨 2-③)"),
    ("2024.12", "양정자이더샵SK VIEW 1·2단지", "부산", 2272, "NICE 연혁"),
    ("2025.07", "춘천 학곡지구 중해마루힐 포레스트", "강원 춘천", 1114, "NICE 연혁"),
    ("2026.01", "두산위브더제니스 오션시티", "부산", 2813, "NICE 연혁"),
    ("2026.07", "창원 센트럴 아이파크", "경남 창원", 1540, "NICE 연혁"),
]

# 캡처: (파일, 제목, 카페 주소, 확인 내용, 가림 박스[(x0,y0,x1,y1)] — 원본 픽셀 좌표)
CAPS = [
    ("sasang_2.png", "① 부산사상 중흥S-클래스 입주민 소통 카페 · 엣지컴퍼니 게시판 (2쪽)",
     "cafe.naver.com/f-e/cafes/30121620/menus/111 (게시판명 (주)엣지컴퍼니&오케이시스템 · 오케이시스템은 당사 협력사)",
     "작성자 '주관사엣지컴퍼니' — 2022.12.14 박람회 수요조사 이벤트 · 2023.01.16 입주 설명회 · 2023.02.20 박람회 날짜·장소·혜택 안내 · 2023.03.01 박람회 혜택 안내",
     [(56, 274, 118, 292), (558, 336, 648, 362)]),
    ("sasang_1.png", "② 부산사상 중흥S-클래스 입주민 소통 카페 · 엣지컴퍼니 게시판 (1쪽)",
     "cafe.naver.com/f-e/cafes/30121620/menus/111",
     "작성자 '주관사엣지컴퍼니' 공지 — 2023.03 · 2023.05 · 2023.06 입주박람회 일정·장소·혜택 안내(1·2차 박람회)",
     [(34, 181, 106, 199), (380, 218, 434, 266), (380, 374, 434, 654)]),
    ("daesung.png", "③ [인증]에코델타시티 대성베르힐 입주자 모임 · 주관사 공지사항",
     "cafe.naver.com/f-e/cafes/30960655/menus/126",
     "작성자 '주관사 엣지컴퍼니' — 2024.11.08 주관사 인사 · 2024.12.07 주관사 선정 기념 이벤트 · 2025.11.26 입주박람회 개최 · 2025.12.02 박람회 성료 및 주관사 업무 안내",
     [(38, 252, 102, 270), (376, 290, 434, 312)]),
]

CSS = r"""
@page{size:A4;margin:13mm 17mm 11mm}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Pretendard','Malgun Gothic','맑은 고딕',sans-serif;color:#1B2433;font-size:10.5pt;line-height:1.65;
  word-break:keep-all;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.pg{page-break-after:always}.pg:last-child{page-break-after:auto}
h1{text-align:center;font-size:24pt;letter-spacing:.45em;font-weight:800;color:#0D1E33;margin:6pt 0 4pt}
.sub{text-align:center;color:#5B6676;font-size:10.5pt;margin-bottom:10pt}
.info{width:100%;border-collapse:collapse;font-size:10pt}
.info th{width:16%;background:#F1EDE4;text-align:left;padding:5pt 9pt;border:.6pt solid #D5CCB9}
.info td{padding:5pt 9pt;border:.6pt solid #D5CCB9}
p.body{margin:10pt 0 6pt;font-size:10.8pt;line-height:1.85}
.t{width:100%;border-collapse:collapse;font-size:9.6pt}
.t th{background:#0D1E33;color:#fff;padding:4.5pt 5pt;border:.6pt solid #0D1E33}
.t td{padding:2.6pt 5pt;border:.6pt solid #C9CED6;text-align:center}
.t td.l{text-align:left}.t td.r{text-align:right;font-variant-numeric:tabular-nums}
.t tr.sum td{background:#F1EDE4;font-weight:800}
ol{margin:8pt 0 0 16pt;font-size:10.2pt;line-height:1.7}
.note{font-size:9pt;color:#5B6676;margin-top:5pt}
.sign{margin-top:14pt;text-align:center;font-size:11pt;line-height:2}
.sign .d{margin-bottom:6pt;letter-spacing:.08em}
.sign b{font-size:13pt;letter-spacing:.1em}
.to{margin-top:12pt;font-size:13pt;font-weight:800;text-align:left}
h2{font-size:13pt;font-weight:800;color:#0D1E33;padding-left:8pt;border-left:3.5pt solid #C8A86A;margin-bottom:6pt}
.cap{margin-top:10pt}.cap h3{font-size:10.5pt;margin-bottom:2pt}
.cap .u{font-size:8.6pt;color:#5B6676}.cap .k{font-size:9pt;margin:2pt 0 5pt}
.cap img{display:block;max-width:100%;max-height:205mm;margin:0 auto;border:.6pt solid #C9CED6}
"""


def mask(src, boxes, out):
    im = Image.open(src).convert("RGB")
    d = ImageDraw.Draw(im)
    for b in boxes:
        d.rectangle(b, fill=(150, 156, 166))
    im.save(out)


def main():
    key = sys.argv[1]
    cdir = sys.argv[2]
    date = sys.argv[3] if len(sys.argv) > 3 else "2026.10.   "
    client, notice, item, penalty, name = CLIENTS[key]
    y, m, dd = (date.split(".") + ["", "", ""])[:3]
    out_dir = os.path.join(HERE, "assets_ins")
    os.makedirs(out_dir, exist_ok=True)
    rows = "".join(f'<tr><td>{i}</td><td>{e(a)}</td><td class="l">{e(b)}</td><td>{e(c)}</td><td class="r">{n:,}</td><td class="l">{e(s)}</td></tr>'
                   for i, (a, b, c, n, s) in enumerate(RECS, 1))
    tot = sum(r[3] for r in RECS)
    p1 = f"""<section class="pg">
<h1>실 적 확 약 서</h1><div class="sub">1,000세대 이상 공동주택 입주박람회 주관 실적</div>
<table class="info"><tr><th>상호</th><td>주식회사 엣지컴퍼니</td><th>대표이사</th><td>고진식</td></tr>
<tr><th>소재지</th><td colspan="3">울산광역시 울주군 청량읍 온산로 615-1, 2층, 3층</td></tr>
<tr><th>제출처</th><td colspan="3">{e(client)}</td></tr></table>
<p class="body">당사는 「{e(notice)}」 {e(item)}에 따라, 1,000세대 이상 공동주택 단지의 입주박람회 주관 실적을 아래와 같이 제출하며 기재 내용이 사실임을 확약합니다.</p>
<table class="t"><tr><th>연번</th><th>주관 시기</th><th>단지명</th><th>지역</th><th>세대수</th><th>근거</th></tr>{rows}
<tr class="sum"><td colspan="4">합계 {len(RECS)}개 단지</td><td class="r">{tot:,}</td><td></td></tr></table>
<div class="note">※ 근거: NICE 기업신용평가보고서(평가일 2026.06.19) '연혁' · 각 단지 입주예정자협의회 공식 카페의 주관사 명의 공지(별첨 2). 세대수는 단지 공식 총세대수.</div>
<ol><li>위 실적은 당사가 입주박람회 주관사로서 직접 수행한 것입니다.</li>
<li>귀 협의회가 요청하면 계약서, 실적 확인서, 정산 자료 등 증빙을 지체 없이 제출하겠습니다.</li>
<li>기재 내용이 사실과 다른 것으로 밝혀지면 공고 {e(penalty)}에 따른 선정 무효·계약 해지 등 모든 조치를 이의 없이 받아들이겠습니다.</li></ol>
<div class="sign"><div class="d">{y}년 &nbsp;{m}월 &nbsp;{dd}일</div>
주식회사 엣지컴퍼니<br><b>대표이사 &nbsp;고 진 식</b> &nbsp;(인)</div>
<div class="to">{e(client)} 귀중</div></section>"""
    caps = ""
    for f, title, url, what, boxes in CAPS:
        src = os.path.join(cdir, f)
        dst = os.path.join(out_dir, "cafe_" + f)
        mask(src, boxes, dst)
        caps += (f'<section class="pg"><h2>별첨 2. 입주예정자협의회 카페 주관사 공지 캡처</h2><div class="cap"><h3>{e(title)}</h3>'
                 f'<div class="u">{e(url)} · 입주민 닉네임(동·호수)은 개인정보 보호를 위해 가림</div><div class="k">{e(what)}</div>'
                 f'<img src="assets_ins/cafe_{f}"></div></section>')
    doc = f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>실적 확약서</title><style>{CSS}</style></head><body>{p1}{caps}</body></html>'
    hp = os.path.join(HERE, name + ".html")
    pathlib.Path(hp).write_text(doc, encoding="utf-8")
    pp = os.path.join(HERE, name + ".pdf")
    subprocess.run([find_chrome(), "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=8000", f"--print-to-pdf={pp}", pathlib.Path(hp).as_uri()],
                   check=True, capture_output=True)
    print(pp)


if __name__ == "__main__":
    main()
