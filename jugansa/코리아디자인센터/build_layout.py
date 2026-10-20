"""코리아디자인센터 B1 제2관(717㎡ ≈ 40m × 18m) 업체 35개 · 44칸 배치도 — 본부장 10-20.
치수는 광주 송정 중흥S클래스(타사, 2·3관) 배치도 표기(상단 11M + 29M · 우측 41M · 하단 27M)에서 2관만 떼어 추정. 1m = S px."""
S = 20
W, H = 40, 18
OX, OY = 40, 110
# (라벨, 그룹, x, y, w, h) — m 단위, 칸 = 3m × 3m
G = {"furn": ("#dbeafe", "#2563eb"), "elec": ("#fee2e2", "#dc2626"), "build": ("#fef3c7", "#c08a2d"),
     "life": ("#dcfce7", "#16a34a"), "own": ("#f3e8c8", "#a8843f"), "ops": ("#eef1f5", "#64748b")}
B = []
x = 0
for nm, w, g in [("가구 1", 9, "furn"), ("가구 2", 9, "furn"), ("가구 3", 9, "furn"), ("인테리어", 3, "build"),
                 ("중문", 3, "build"), ("커튼 1", 3, "build"), ("커튼 2<br>직영", 3, "own")]:
    B.append((nm, g, x + 0.5, 0, w, 3)); x += w
for nm, y, h, g in [("가전 1", 3, 6, "elec"), ("가전 2", 9, 6, "elec"), ("조명<br>직영", 15, 3, "own")]:
    B.append((nm, g, 37, y, 3, h))
x = 10
for nm, w, g in [("가전 3", 6, "elec"), ("냉장고<br>붙박이장", 3, "elec"), ("에어컨", 3, "elec"), ("청정 환기", 3, "life"),
                 ("통신", 3, "life"), ("렌탈", 3, "life"), ("인덕션", 3, "elec"), ("보험", 3, "ops")]:
    B.append((nm, g, x, 15, w, 3)); x += w
isl = [["줄눈 1", "줄눈 2", "줄눈 3", "코팅 1"], ["코팅 2", "탄성 1", "탄성 2", "필름"],
       ["청소 1", "청소 2", "새집증후군", "음식물<br>처리기"], ["매트", "벽걸이 TV", "선반", "이사"]]
grp = {"줄눈": "build", "코팅": "build", "탄성": "build", "필름": "build"}
for k, (x0, y0) in enumerate([(7, 6), (7, 9), (22, 6), (22, 9)]):
    for j, nm in enumerate(isl[k]):
        B.append((nm, grp.get(nm.split()[0], "life"), x0 + 3 * j, y0, 3, 3))
B.append(("안전망", "life", 0.5, 6, 3, 3))
vend = [b for b in B]
n_v = len(vend); n_c = sum(int(b[4] * b[5] / 9) for b in B)
assert n_v == 35 and n_c == 44, (n_v, n_c)

def r(x, y, w, h, **k):
    a = " ".join(f'{kk.replace("_", "-")}="{v}"' for kk, v in k.items())
    return f'<rect x="{OX + x * S}" y="{OY + y * S}" width="{w * S}" height="{h * S}" {a}/>'

def t(x, y, s, size=12, w=600, fill="#15233b", anchor="middle"):
    lines = s.split("<br>")
    out = ""
    for i, ln in enumerate(lines):
        dy = (i - (len(lines) - 1) / 2) * (size + 2)
        out += f'<text x="{OX + x * S}" y="{OY + y * S + dy + size * 0.35}" text-anchor="{anchor}" font-size="{size}" font-weight="{w}" fill="{fill}">{ln}</text>'
    return out

sv = []
sv.append(f'<polygon points="{OX},{OY} {OX + W * S},{OY} {OX + W * S},{OY + H * S} {OX},{OY + H * S}" fill="#fbfaf7" stroke="#47637a" stroke-width="3"/>')
for nm, g, x, y, w, h in B:
    f, s = G[g]
    sv.append(r(x + .08, y + .08, w - .16, h - .16, rx=3, fill=f, stroke=s, stroke_width=1.3))
    sv.append(t(x + w / 2, y + h / 2, nm, 13 if w * h >= 18 else 11))
# 운영 구역
sv.append(r(0.5, 10, 6, 5, rx=4, fill="#ffffff", stroke="#94a3b8", stroke_width=1, stroke_dasharray="5 4"))
sv.append(t(3.5, 11.6, "상담 · 휴게석", 11, 600, "#475569"))
sv.append(t(3.5, 13.2, "테이블 6 · 의자 24", 10, 400, "#64748b"))
sv.append(r(0.5, 3.5, 6, 2, rx=4, fill="#0d1e33", stroke="#0d1e33"))
sv.append(t(3.5, 4.5, "접수 · 혜택 안내 데스크", 11, 700, "#f3e3bf"))
# 입구 (남측 · 로비)
sv.append(f'<rect x="{OX + 1 * S}" y="{OY + H * S - 4}" width="{7 * S}" height="8" fill="#c8a35a"/>')
sv.append(t(4.5, 19.1, "입구 · 로비 쪽(약 7m)", 12, 700, "#8a6a2c"))
sv.append(f'<path d="M{OX + 4.5 * S} {OY + H * S + 30} L{OX + 4.5 * S} {OY + H * S + 8}" stroke="#8a6a2c" stroke-width="2" marker-end="url(#ar)"/>')
# 통로 표기
for x, y, s in [(20, 4.5, "통로 3m"), (20, 13.5, "통로 3m"), (20.5, 9, "3m"), (35.5, 9, "3m")]:
    sv.append(t(x, y, s, 10, 500, "#94a3b8"))
# 치수
sv.append(t(20, -1.2, "약 40m", 12, 600, "#47637a"))
sv.append(t(41.6, 9, "약 18m", 12, 600, "#47637a"))
sv.append(t(26, 19.1, "제3관(대관 안 함) · 가벽", 11, 500, "#94a3b8"))
leg = [("furn", "가구"), ("elec", "가전 · 설비"), ("build", "시공(줄눈 · 코팅 · 탄성 · 필름 · 중문 · 커튼)"), ("life", "생활 · 서비스"), ("own", "엣지컴퍼니 직영"), ("ops", "기타")]
lx = 0
for g, nm in leg:
    f, s = G[g]
    sv.append(f'<rect x="{OX + lx}" y="{OY + H * S + 52}" width="14" height="14" rx="2" fill="{f}" stroke="{s}"/>'
              f'<text x="{OX + lx + 20}" y="{OY + H * S + 63}" font-size="12" fill="#334155">{nm}</text>')
    lx += 34 + len(nm) * 12.5
svg = (f'<svg viewBox="0 0 {W * S + 2 * OX + 20} {OY + H * S + 90}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="코리아디자인센터 제2관 배치도">'
       '<defs><marker id="ar" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M2 2L8 5L2 8" fill="none" stroke="#8a6a2c" stroke-width="1.6"/></marker></defs>'
       f'<text x="{OX}" y="40" font-size="20" font-weight="800" fill="#0d1e33">판교테크노밸리 중흥S클래스 입주박람회 · 부스 배치도(안)</text>'
       f'<text x="{OX}" y="66" font-size="13" fill="#475569">코리아디자인센터 B1 제2관 · 전용 717.36㎡(217평) · 업체 {n_v}개 · {n_c}칸(3m × 3m) · 부스 {n_c * 9}㎡(면적의 {n_c * 9 / 717:.0%}) · 테이블 · 의자 · 테이블보 렌탈</text>'
       + "".join(sv) + "</svg>")
html = """<title>코리아디자인센터 2관 배치도</title>
<style>
:root{--bg:#f3f1ec;--fg:#16202e;--sub:#5a6474;--card:#fff;--line:#ddd7cb}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0b1522;--fg:#e9edf3;--sub:#9aa6b6;--card:#122135;--line:#24364e;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0b1522;--fg:#e9edf3;--sub:#9aa6b6;--card:#122135;--line:#24364e;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:"Pretendard","Malgun Gothic",sans-serif;margin:0;padding:20px 16px 40px;line-height:1.55}
.wrap{max-width:1000px;margin:0 auto;display:flex;flex-direction:column;gap:14px}
.plan{background:#fff;border:1px solid var(--line);border-radius:10px;overflow-x:auto;padding:8px}
.plan svg{display:block;min-width:760px;width:100%;height:auto;font-family:"Pretendard","Malgun Gothic",sans-serif}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.card h2{font-size:14px;margin:0 0 8px}
table{width:100%;border-collapse:collapse;font-size:13.5px;font-variant-numeric:tabular-nums}
td,th{padding:6px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{color:var(--sub);font-weight:600;font-size:12.5px}
.scroll{overflow-x:auto}
ul{margin:0;padding-left:18px;font-size:14px}
.note{font-size:12.5px;color:var(--sub)}
</style>
<div class="wrap">
<div class="plan">SVG</div>
<div class="card"><h2>구역별 배치 원칙</h2><div class="scroll"><table>
<tr><th>구역</th><th>업체</th><th>이유</th></tr>
<tr><td>북측 벽</td><td>가구 3(각 3칸) · 인테리어 · 중문 · 커튼 2(엣지리브 직영 1)</td><td>큰 전시가 필요한 품목을 벽에 붙여 동선 끝까지 끌어당김</td></tr>
<tr><td>동측 벽</td><td>가전 2(각 2칸) · 조명(직영 · 아크로)</td><td>가전은 입구 반대편 끝 = 전 구역을 지나가게 하는 '앵커'</td></tr>
<tr><td>남측 벽</td><td>가전 1(2칸) · 냉장고/붙박이장 · 에어컨 · 청정환기 · 통신 · 렌탈 · 인덕션 · 보험</td><td>설비 · 계약형 품목을 한 줄로 · 출구 쪽 마지막 상담</td></tr>
<tr><td>중앙 섬 2개(양면)</td><td>줄눈 3 · 코팅 2 · 탄성 2 · 필름 · 청소 2 · 새집 · 음식물 · 매트 · 벽걸이 · 선반 · 이사</td><td>계약률 높은 1칸 품목 = 동선 중심 · 줄눈/코팅/탄성은 한 섬에 모아 비교 상담</td></tr>
<tr><td>입구 쪽(서측)</td><td>접수 · 혜택 안내 데스크 · 안전망 · 상담 · 휴게석</td><td>입장 즉시 발전지원 혜택 안내 → 입주민 체류 시간 확보</td></tr>
</table></div></div>
<div class="card"><h2>참고: 광주 송정 중흥S클래스 파크뷰(타사 · 2026.05.15 ~ 17)</h2><ul>
<li>840세대 · 제2관 + 제3관(1,216㎡) · 업체 약 75개(배치도 판독 · ±5) = 100세대당 약 9개 — 엣지컴퍼니 에코델타 실적(100세대당 8 ~ 9개)과 같은 밀도.</li>
<li>317세대 · 업체 35개면 제2관(717㎡) 하나로 충분 — 송정은 75개라 두 관이 필요했던 것.</li>
</ul></div>
<div class="card"><h2>확인할 것</h2><ul>
<li>제2관 실제 가로 · 세로 · 기둥 위치 · 입구 위치 — 치수는 타사 배치도(광주 송정, 2·3관) 표기로 추정했습니다.</li>
<li>대관비 표 '대관료 2,500 · 수도광열비 800 · 계 3,300'의 <b>단위(천원/일인지)와 대상(2관 단독인지, 2·3관 합계인지)</b>.</li>
<li>렌탈 수량(안): 업체 칸당 테이블 2 · 의자 3 ~ 4 + 테이블보 → 테이블 약 90 · 의자 약 150 + 상담 · 휴게석 테이블 6 · 의자 24.</li>
</ul><p class="note">통로 3m(주통로) · 섬 사이 3m · 소방 통로는 대관 측 기준으로 다시 맞춥니다.</p></div>
</div>
""".replace("SVG", svg)
open("코리아디자인센터_2관_배치도.html", "w").write(html)
print(n_v, n_c)
