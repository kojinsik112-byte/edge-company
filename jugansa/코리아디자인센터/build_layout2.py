"""코리아디자인센터 B1 제2관 배치 시안 v2(본부장 10-20 2차) — 전시장 미확정 · 대략 시안 · 업로드 안 함.
규칙: 가구 · 가전 8 × 5m · 나머지 3.5 × 3m · 엣지조명 + 휴젠뜨(환기) 7 × 3m = 문 들어가서 바로 오른쪽 · 보험 · 접수처 = 박람회장 밖 입구 오른쪽
· 가구 · 가전 = 기역자(북측 벽 + 동측) · 가구 사이에 가전 끼움 · 가전끼리 붙이지 않음 · 동종 업체는 각각 따로(청소A · 줄눈A … 번갈아).
제2관 치수 = 약 40 × 18.4m(전용 717㎡ · 타사 배치도 표기로 추정) · 통로 2.2m."""
S, W, H, OX, OY = 20, 40, 18.4, 40, 110
G = {"furn": ("#dbeafe", "#2563eb"), "elec": ("#fee2e2", "#dc2626"), "build": ("#fef3c7", "#c08a2d"),
     "life": ("#dcfce7", "#16a34a"), "own": ("#f3e8c8", "#a8843f"), "ops": ("#eef1f5", "#64748b")}
TYPE = {"가구": "furn", "가전": "elec", "에어컨": "elec", "인덕션": "elec", "냉장고·붙박이장": "elec",
        "줄눈": "build", "코팅": "build", "탄성": "build", "필름": "build", "중문": "build", "인테리어": "build",
        "청소": "life", "새집증후군": "life", "매트": "life", "선반": "life", "벽걸이TV": "life", "음식물": "life",
        "이사": "life", "통신": "life", "렌탈": "life", "안전망": "life", "방충망": "life", "보험": "ops"}
B = []  # (종류, 라벨, x, y, w, h)
for i, nm in enumerate(["가구A", "가전A", "가구B", "가전B", "가구C"]):  # 북측 벽 · 기역자 윗변(가구 사이 가전)
    B.append((nm[:-1], nm, 8 * i, 0, 8, 5))
B.append(("own", "엣지컴퍼니 직영 3곳<br>엣지조명 · 휴젠뜨(환기) · 실링팬", 6.5, 15.4, 10.5, 3))  # 문 들어가서 바로 오른쪽(본부장 10-20: 실링팬 3.5m 추가)
slots = ([(0, 7.2, 3, 3.5), (0, 10.7, 3, 3.5)]                                     # 서측 벽
         + [(x0 + dx, y, 3.5, 3) for x0 in (6.25, 16.5, 26.75) for y in (7.2, 10.2) for dx in (0, 3.5)]  # 섬 3개(2 × 2)
         + [(37, y, 3, 3.5) for y in (7.2, 10.7, 14.2)]                              # 동측 벽 · 기역자 세로변
         + [(17 + 3.5 * k, 15.4, 3.5, 3) for k in range(5)])                         # 남측 벽
names = ["안전망A", "방충망A",
         "청소A", "줄눈A", "탄성A", "코팅A",  "새집증후군A", "청소B", "줄눈B", "탄성B",  "코팅B", "필름A", "매트A", "선반A",
         "에어컨A", "인덕션A", "냉장고·붙박이장A",
         "중문A", "벽걸이TV A", "인테리어A", "음식물A", "이사A"]
assert len(slots) == len(names) == 22
for (x, y, w, h), nm in zip(slots, names):
    B.append((nm.replace(" ", "")[:-1], nm, x, y, w, h))
OUT = [("ops", "접수 · 혜택 안내", 7, 19.6, 6, 2.4), ("보험", "보험A", 13.5, 19.6, 3.5, 2.4)]  # 박람회장 밖 · 입구 오른쪽
OVER = [("통신", "통신A", 22, 19.6, 3.5, 2.4), ("렌탈", "렌탈A", 26, 19.6, 3.5, 2.4)]  # 제2관 자리 부족 → 로비 또는 제3관(확인 필요)


def touch(a, b):  # 변이 맞닿는지(모서리만 닿는 것은 제외)
    ax0, ay0, aw, ah = a; bx0, by0, bw, bh = b
    ax1, ay1, bx1, by1 = ax0 + aw, ay0 + ah, bx0 + bw, by0 + bh
    ov_x = min(ax1, bx1) - max(ax0, bx0); ov_y = min(ay1, by1) - max(ay0, by0)
    return (abs(ax1 - bx0) < 1e-6 or abs(bx1 - ax0) < 1e-6) and ov_y > 1e-6 or (abs(ay1 - by0) < 1e-6 or abs(by1 - ay0) < 1e-6) and ov_x > 1e-6


for i, a in enumerate(B):
    for b in B[i + 1:]:
        if a[0] == b[0] and a[0] != "가구" and touch(a[2:], b[2:]):
            raise SystemExit(f"동종 업체가 붙음: {a[1]} · {b[1]}")
        if a[0] == "가전" == b[0] and touch(a[2:], b[2:]):
            raise SystemExit("가전끼리 붙음")
n_in = len(B) + 2                                # 직영 부스 = 3곳(조명 · 휴젠뜨 · 실링팬)
n_all = n_in + 1 + len(OVER)                     # + 보험(밖) + 자리 부족


def r(x, y, w, h, **k):
    a = " ".join(f'{kk.replace("_", "-")}="{v}"' for kk, v in k.items())
    return f'<rect x="{OX + x * S:.1f}" y="{OY + y * S:.1f}" width="{w * S:.1f}" height="{h * S:.1f}" {a}/>'


def t(x, y, s, size=12, w=700, fill="#15233b"):
    ls = s.split("<br>")
    return "".join(f'<text x="{OX + x * S:.1f}" y="{OY + y * S + (i - (len(ls) - 1) / 2) * (size + 2) + size * .35:.1f}" text-anchor="middle" '
                   f'font-size="{size}" font-weight="{w}" fill="{fill}">{l}</text>' for i, l in enumerate(ls))


sv = [f'<rect x="{OX}" y="{OY}" width="{W * S}" height="{H * S}" fill="#fbfaf7" stroke="#47637a" stroke-width="3"/>']
sv.append(f'<rect x="{OX + .5 * S}" y="{OY + H * S - 4}" width="{5.5 * S}" height="8" fill="#c8a35a"/>')  # 입구
for k, nm, x, y, w, h in B + OUT + OVER:
    g = "own" if k == "own" else TYPE.get(k, "ops")
    f, s_ = G[g]
    sv.append(r(x + .06, y + .06, w - .12, h - .12, rx=3, fill=f, stroke=s_, stroke_width=1.3))
    big = k in ("가구", "가전")
    lab = nm.replace("·", "·<br>") if (w < 3.6 and len(nm) > 5) else nm
    if k == "own":
        for j in (1, 2):
            sv.append(f'<line x1="{OX + (x + 3.5 * j) * S}" y1="{OY + (y + .3) * S}" x2="{OX + (x + 3.5 * j) * S}" y2="{OY + (y + h - .3) * S}" stroke="{s_}" stroke-opacity=".35" stroke-dasharray="3 3"/>')
        sv.append(t(x + w / 2, y + h / 2 - .35, lab, 11.5))
        sv.append(t(x + w / 2, y + h / 2 + 1.05, "10.5 × 3m", 10, 600, s_))
        continue
    sv.append(t(x + w / 2, y + h / 2 - (.45 if big else 0), lab, 15 if big else 10.5))
    if big:
        sv.append(t(x + w / 2, y + h / 2 + 1.0, "8 × 5m", 10.5, 600, s_))
sv.append(t(3.25, 19.3, "입구", 12, 800, "#8a6a2c"))
sv.append(f'<rect x="{OX + 6.5 * S}" y="{OY + 19.2 * S}" width="{11 * S}" height="{3.2 * S}" fill="none" stroke="#94a3b8" stroke-dasharray="5 4" rx="6"/>')
sv.append(f'<rect x="{OX + 21.5 * S}" y="{OY + 19.2 * S}" width="{8.5 * S}" height="{3.2 * S}" fill="none" stroke="#dc2626" stroke-dasharray="4 4" rx="6"/>')
sv.append(t(14.7, 23.4, "박람회장 밖 · 로비(입구 오른쪽)", 10.5, 600, "#64748b"))
sv.append(t(25.75, 23.4, "제2관 자리 부족 → 로비 또는 제3관", 10.5, 700, "#dc2626"))
for x, y, s in [(20, 6.1, "통로 2.2m"), (20, 14.3, "통로 2.2m"), (35.4, 11, "통로")]:
    sv.append(t(x, y, s, 9.5, 500, "#94a3b8"))
sv.append(t(20, -1.2, "약 40m", 12, 600, "#47637a"))
sv.append(t(41.7, 9.2, "약 18m", 12, 600, "#47637a"))
svg = (f'<svg viewBox="0 0 {W * S + 2 * OX + 20} {OY + 23.5 * S}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="배치 시안">'
       f'<text x="{OX}" y="40" font-size="20" font-weight="800" fill="#0d1e33">판교테크노밸리 중흥S클래스 입주박람회 · 부스 배치 시안 v2</text>'
       f'<text x="{OX}" y="66" font-size="13" fill="#475569">코리아디자인센터 B1 제2관(717㎡ · 약 40 × 18m 추정) · 업체 {n_all}곳(안 {n_in} + 밖 보험 1 + 자리 부족 {len(OVER)}) · 가구 · 가전 8 × 5m · 그 밖 3.5 × 3m · 전시장 미확정 대략 시안</text>'
       + "".join(sv) + "</svg>")
html = f"""<title>코리아디자인센터 배치 시안 v2</title>
<style>
:root{{--bg:#f3f1ec;--fg:#16202e;--sub:#5a6474;--card:#fff;--line:#ddd7cb}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#0b1522;--fg:#e9edf3;--sub:#9aa6b6;--card:#122135;--line:#24364e;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#0b1522;--fg:#e9edf3;--sub:#9aa6b6;--card:#122135;--line:#24364e;color-scheme:dark}}
body{{background:var(--bg);color:var(--fg);font-family:"Pretendard","Malgun Gothic",sans-serif;margin:0;padding:20px 16px 40px;line-height:1.55}}
.wrap{{max-width:1000px;margin:0 auto;display:flex;flex-direction:column;gap:14px}}
.plan{{background:#fff;border:1px solid var(--line);border-radius:10px;overflow-x:auto;padding:8px}}.plan svg{{display:block;min-width:760px;width:100%;height:auto}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px}}.card h2{{font-size:14px;margin:0 0 8px}}ul{{margin:0;padding-left:18px;font-size:14px}}
</style>
<div class="wrap"><div class="plan">{svg}</div>
<div class="card"><h2>배치 원칙</h2><ul>
<li>가구 · 가전 = 북측 벽 기역자 · 가구 사이에 가전을 끼움(가구A · 가전A · 가구B · 가전B · 가구C) · 가전끼리 붙지 않음.</li>
<li>엣지컴퍼니 직영 3곳(엣지조명 · 휴젠뜨 환기 · 실링팬) 10.5 × 3m = 문 들어가서 바로 오른쪽 · 보험 · 접수처 = 박람회장 밖 입구 오른쪽.</li>
<li>동종 업체는 각각 따로 · 청소A → 줄눈A → 탄성A → 코팅A → 새집증후군A → 청소B … 순서로 번갈아 배치(같은 업종끼리 맞닿지 않음 — 생성 시 자동 검사).</li>
</ul></div>
<div class="card"><h2>제2관 수용 한계(확인 필요)</h2><ul>
<li>이 규격(8 × 5m · 3.5 × 3m · 통로 2.2m)으로 제2관에 들어가는 것은 <b>가구 3 · 가전 2 · 일반 22 + 직영 3 = 안 {n_in}곳</b> · 밖 보험 1 · 최소안({n_all}곳) 중 <b>통신 · 렌탈 2곳은 자리가 모자람</b>(로비 또는 제3관).</li>
<li>가구 4 ~ 5 · 가전 3 · 업체 38곳까지 늘면 → 제3관 일부(499㎡)를 함께 쓰거나, 일반 부스를 3 × 3m로 줄여야 합니다.</li>
<li>치수 · 기둥 · 출입구는 대관 도면으로 다시 맞춥니다.</li></ul></div></div>
"""
open("코리아디자인센터_2관_배치시안_v2.html", "w").write(html)
print(n_in, n_all)
