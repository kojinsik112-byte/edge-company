"""영주자이 시그니처 윈터 라이팅 제안서 빌더 (16:9 PDF).

입력: 다운로드\\영주자이 AI 시안\\(테마별 폴더 4개, 회장 ChatGPT 연출 이미지 21장)
     표지(선택): 바탕화면\\경관조명 관련\\영주자이 자료\\제안서\\표지.png|jpg  — 있으면 맨 앞에 붙임
출력: 바탕화면\\경관조명 관련\\영주자이 자료\\제안서\\영주자이_윈터라이팅_제안서.pdf
     + 수정 사진\\(오타·문구·정문 제목 통일본 21장)
금액은 yeongju_build.py 의 견적 데이터에서 그대로 가져온다(견적서와 숫자 불일치 방지).
실행: python 경관조명/tools/yeongju_proposal.py
"""
from __future__ import annotations

import html
import subprocess
import sys
from pathlib import Path

import cv2
import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import yeongju_build as yb  # noqa: E402

BASE = Path.home() / "Desktop" / "경관조명 관련"
SRC = next(p for p in [BASE / "영주자이 AI 시안", Path.home() / "Downloads" / "영주자이 AI 시안"] if p.exists())
OUT = Path.home() / "Desktop" / "경관조명 관련" / "영주자이 자료" / "제안서"
IMG = OUT / "img"
FIXED = OUT / "수정 사진"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SERIF = "C:/Windows/Fonts/NotoSerifKR-VF.ttf"
LICENSE = "전기공사업 등록 제 울산-00821호"
COVER_SRC = next((p for p in [Path.home() / "Downloads" / "영주자이의 밤, 빛의 풍경.png", BASE / "영주자이의 밤, 빛의 풍경.png",
                              BASE / "영주자이 AI 시안" / "영주자이의 밤, 빛의 풍경.png"] if p.exists()), None)  # 회장 제공 표지
FINAL_NAME = "(엣지컴퍼니) 영주자이시그니처 경관조명 통합 제안서_261121.pdf"

# ───────────── 1. 사진 수정 ─────────────
FIX_TITLE = {"별빛의 초대 게이트 조명 제안서", "별빛의 초대, 영주자이 입구-2", "별빛이 머무는 정문 야경-1",
             "우측 시점의 별빛 입구-4", "자이 게이트의 별빛 조명-3"}
FIX_LICENSE = {"별빛이 머무는 정문 야경-1", "왼쪽 산책로에서 본 요정의 숲-5", "요정의 숲 야간 조경 제안", "요정의 숲, 빛나는 중정-4"}
FIX_RIGHT = {"105 빌딩, 하늘에 새긴 빛-3", "105타워에 새긴 황금빛-2", "하늘에 새긴 105의 빛-1", "하늘에 새긴 빛"}


def _font(size, weight):
    f = ImageFont.truetype(SERIF, size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


def retext(im: Image.Image, box, text, kind, anchor="left", weight="Regular"):
    a = np.array(im).astype(np.uint8)
    x0, y0, x1, y1 = box
    reg = a[y0:y1, x0:x1].astype(int)
    r, g, b = reg[..., 0], reg[..., 1], reg[..., 2]
    lum = reg.mean(axis=2)
    if kind == "gold":
        mask = (r > 120) & (r - b > 40)
    else:  # white
        mask = (lum > 120) & ((reg.max(axis=2) - reg.min(axis=2)) < 55)
    ys, xs = np.where(mask)
    if len(xs) < 30:
        print("   ! 글자 못 찾음", text)
        return im
    bx0, by0, bx1, by1 = xs.min() + x0, ys.min() + y0, xs.max() + x0, ys.max() + y0
    col = tuple(int(v) for v in reg[mask][lum[mask] > np.percentile(lum[mask], 70)].mean(axis=0))
    m = np.zeros(a.shape[:2], np.uint8)
    m[y0:y1, x0:x1][mask] = 255
    m = cv2.dilate(m, np.ones((5, 5), np.uint8), iterations=2)
    a = cv2.inpaint(a, m, 5, cv2.INPAINT_TELEA)
    th = by1 - by0
    best = None
    for s in range(12, 80):
        f = _font(s, weight)
        l, t, rr, bb = f.getbbox(text)
        if kind == "gold":
            score = abs((bb - t) - th)
        else:
            score = abs((rr - l) - (bx1 - bx0))
        if best is None or score < best[0]:
            best = (score, f, l, t, rr - l)
    _, f, l, t, w = best
    out = Image.fromarray(a)
    d = ImageDraw.Draw(out)
    x = {"left": bx0 - l, "right": bx1 - w - l, "center": (bx0 + bx1) // 2 - w // 2 - l}[anchor]
    d.text((x, by0 - t), text, font=f, fill=col)
    return out


def prepare_images() -> dict:
    IMG.mkdir(parents=True, exist_ok=True)
    out = {}
    for p in sorted(SRC.rglob("*.png")):
        im = Image.open(p).convert("RGB")
        if im.size != (1672, 941):
            im = im.resize((1672, 941))
        stem = p.stem
        if stem in FIX_TITLE:
            im = retext(im, (60, 62, 335, 124), "겨울빛의 문", "gold", weight="Medium")
        if stem in FIX_LICENSE:
            im = retext(im, (60, 862, 640, 914), LICENSE, "white")
        if stem in FIX_RIGHT:
            im = retext(im, (1380, 862, 1666, 914), "설치 예상 이미지", "white", anchor="right")
        theme = p.parent.name.replace("머무리는", "머무는")
        (FIXED / theme).mkdir(parents=True, exist_ok=True)
        im.save(FIXED / theme / f"{stem}.png")
        key = f"{theme}|{stem}"
        fn = f"p{len(out) + 1:02d}.jpg"
        im.save(IMG / fn, quality=86)
        out[key] = fn
        print(" ", key, "→", fn, "(수정)" if stem in FIX_TITLE | FIX_LICENSE | FIX_RIGHT else "")
    return out


def prepare_cover():
    """회장 표지: 정문 라벨 '별빛의 초대' → '겨울빛의 문' 통일 후 제안서\표지.png 로 저장."""
    dst = OUT / "표지.png"
    if COVER_SRC:
        im = Image.open(COVER_SRC).convert("RGB")
        im = retext(im, (200, 788, 420, 838), "겨울빛의 문", "white", anchor="center")
        im.save(dst)
    return dst if dst.exists() else None


# ───────────── 2. 품목 사진 잘라내기 ─────────────
CROPS = {
    "gate_icicle": ("겨울빛의 문|자이 게이트의 별빛 조명-3", (880, 170, 1500, 450)),
    "gate_motif": ("겨울빛의 문|자이 게이트의 별빛 조명-3", (560, 250, 840, 440)),
    "gate_cone": ("겨울빛의 문|자이 게이트의 별빛 조명-3", (250, 310, 640, 800)),
    "gate_pine": ("겨울빛의 문|자이 게이트의 별빛 조명-3", (90, 60, 260, 680)),
    "gate_neon": ("겨울빛의 문|자이 게이트의 별빛 조명-3", (220, 120, 520, 230)),
    "gdn_deer": ("별빛이 머무는 정원|나무 곁의 별빛 정원-4", (860, 360, 1270, 610)),
    "gdn_rabbit": ("별빛이 머무는 정원|나무 곁의 별빛 정원-4", (340, 570, 500, 800)),
    "gdn_star": ("별빛이 머무는 정원|나무 곁의 별빛 정원-4", (500, 430, 790, 700)),
    "gdn_sphere": ("별빛이 머무는 정원|나무 곁의 별빛 정원-4", (950, 545, 1150, 730)),
    "gdn_stake": ("별빛이 머무는 정원|나무 곁의 별빛 정원-4", (800, 670, 960, 850)),
    "gdn_hang": ("별빛이 머무는 정원|나무 곁의 별빛 정원-4", (280, 140, 900, 420)),
    "fst_canopy": ("요정의 숲|왼편에서 바라본 요정의 숲", (40, 60, 980, 560)),
    "fst_purple": ("요정의 숲|왼편에서 바라본 요정의 숲", (840, 220, 1220, 620)),
    "fst_up": ("요정의 숲|왼편에서 바라본 요정의 숲", (260, 560, 520, 840)),
    "sky_line": ("하늘에 새긴 빛|105타워에 새긴 황금빛-2", (780, 80, 1220, 880)),
}


def make_crops(files: dict):
    for name, (key, box) in CROPS.items():
        Image.open(IMG / files[key]).crop(box).save(IMG / f"{name}.jpg", quality=90)


# ───────────── 3. 페이지 데이터 ─────────────
THEMES = [
    dict(no="①", name="하늘에 새긴 빛", folder="하늘에 새긴 빛", hero="하늘에 새긴 빛",
         gallery=["하늘에 새긴 105의 빛-1", "105타워에 새긴 황금빛-2", "105 빌딩, 하늘에 새긴 빛-3"],
         where="105동 측벽 · 지상 27층 · 높이 79.3m", kind="상시 경관조명",
         concept="27층을 따라 오르는 한 줄의 황금빛. 단지 밖에서도 영주자이를 알아보게 하는 밤의 표식입니다.",
         points=["3000K 따뜻한 단색, 깜빡임 없는 정적 점등", "2층 바닥부터 옥상까지 끊김 없는 세로 라인", "기본안 1줄 · 프리미엄안 측벽을 감싸는 ∩ 프레임"],
         note="※ 연출 이미지는 프리미엄안(∩ 프레임) 기준입니다.",
         items=[("sky_line", "LED 경관 라인바", "알루미늄 100×85 · 광확산 커버 · 3000K · 층고 맞춤 2.9m 모듈", "기본 75.5m / 프리미엄 약 160m"),
                (None, "분산 전원장치", "12V · 방수 IP67 · KC · 측벽 약 6m마다 설치", "기본 13대 / 프리미엄 28대"),
                (None, "옥상 전원함", "천문 타이머 · 누전차단기 · 서지보호기", "1조")]),
    dict(no="②", name="겨울빛의 문", folder="겨울빛의 문", hero="겨울빛의 문",
         gallery=["별빛이 머무는 정문 야경-1", "별빛의 초대, 영주자이 입구-2", "자이 게이트의 별빛 조명-3", "우측 시점의 별빛 입구-4"],
         where="정문 문주 · 길이 약 28.6m · 높이 6.85m", kind="시즌 장식",
         concept="단지에 들어서는 순간 겨울이 시작되는 문. 지붕 띠를 따라 고드름 빛이 내려앉습니다.",
         points=["지붕 띠 전면에 전구색 고드름 커튼", "로고 벽에 눈꽃·별, 화단에 원뿔 트리", "석재·유리·SUS 마감 무타공 시공"],
         note="",
         items=[("gate_icicle", "고드름 커튼 라이트", "전구색 · 드롭 0.2~0.6m · 하단 보조 와이어 고정", "32m"),
                ("gate_motif", "눈꽃·별 모티브", "Ø35~80cm · 전구색·백색 · 투명 와이어 행잉", "4개"),
                ("gate_cone", "원뿔 트리", "H2.5m · H1.8m · 별 장식 · 지면 고정", "2개"),
                ("gate_pine", "소나무 기둥 감기", "전구색 은하수 · 못·스테이플 미사용", "5그루"),
                ("gate_neon", "네온 라인", "전구색 · 좌측 돌출부 하단 모서리", "4m")]),
    dict(no="③", name="별빛이 머무는 정원", folder="별빛이 머무는 정원", hero="별빛이 머무는 정원 야경-2",
         gallery=["초승달 아래 별빛 정원-1", "별빛이 머무는 정원, 새로운 각도-3", "나무 곁의 별빛 정원-4"],
         where="잔디 정원 · 스테인리스 조형물 주변", kind="시즌 장식",
         concept="사슴과 토끼가 쉬어 가는 별빛 정원. 큰 나무 가지에는 별이 매달립니다.",
         points=["와이어 프레임 조형물로 낮에도 정원과 어울림", "기존 나무 조명·조형물은 그대로 살림", "잔디 앵커 고정, 보행로 무배선"],
         note="",
         items=[("gdn_deer", "LED 사슴", "H1.5m · H1.1m · 와이어 프레임", "2점"),
                ("gdn_rabbit", "LED 토끼", "H0.5m · 와이어 프레임", "2점"),
                ("gdn_star", "대형 별 조형물", "H1.2m · 이중 라인", "1점"),
                ("gdn_sphere", "빛 구슬", "Ø60cm · Ø40cm", "2개"),
                ("gdn_stake", "꽂이형 반짝이 별", "Ø40cm · 지주 포함", "6개"),
                ("gdn_hang", "나무 행잉 라이트", "별·물방울 드롭 · 길이 0.6~1.2m", "9개")]),
    dict(no="④", name="요정의 숲", folder="요정의 숲", hero="요정의 숲",
         gallery=["요정의 숲 빛나는 정원 전경-2", "오른쪽 산책로의 요정의 숲-3", "요정의 숲, 빛나는 중정-4", "왼편에서 바라본 요정의 숲"],
         where="소나무 숲 · 쉼터 파고라 주변", kind="시즌 장식",
         concept="푸른 빛으로 물든 소나무 사이를 걷는 산책. 정원이 하나의 숲 속 이야기가 됩니다.",
         points=["소나무 수관을 블루·그린·퍼플·화이트로 감쌈", "나무 밑 색 업라이트로 기둥에 깊이감", "화단 경계 조명·파고라 등 기존 시설 유지"],
         note="",
         items=[("fst_canopy", "수관 은하수 · 대형 소나무", "H7~8m · 블루·그린·퍼플·화이트", "3그루"),
                ("fst_purple", "수관 은하수 · 중형 소나무", "H4~5m · 같은 색 구성", "4그루"),
                ("fst_up", "RGB 수목 업라이트", "스파이크형 · IP65 · 색 선택", "4개")]),
]

ICON = {
    "분산 전원장치": '<svg viewBox="0 0 64 64"><rect x="14" y="10" width="36" height="44" rx="4" fill="none" stroke="#b8913a" stroke-width="3"/><path d="M34 18 L26 34 H34 L30 46 L40 28 H32 Z" fill="#b8913a"/></svg>',
    "옥상 전원함": '<svg viewBox="0 0 64 64"><rect x="10" y="14" width="44" height="38" rx="3" fill="none" stroke="#b8913a" stroke-width="3"/><circle cx="32" cy="33" r="9" fill="none" stroke="#b8913a" stroke-width="3"/><path d="M32 27 V33 L37 36" stroke="#b8913a" stroke-width="3" fill="none"/></svg>',
}


def won(n):
    return f"{n:,}"


def page(inner, cls="pg"):
    return f'<section class="{cls}">{inner}</section>'


def header(no, name, sub):
    return (f'<div class="hd"><span class="no">{no}</span><span class="nm">{html.escape(name)}</span>'
            f'<span class="sub">{html.escape(sub)}</span><span class="brand">㈜엣지컴퍼니</span></div>')


def build_html(files: dict, cover: Path | None) -> str:
    q = {qd["key"]: yb.calc(qd) for qd in yb.QUOTES}
    qx = {qd["key"]: yb.calc(qd["철거"]) if qd.get("철거") else None for qd in yb.QUOTES}
    k1, k1p = "1_하늘에새긴빛_1줄_12V", "1B_하늘에새긴빛_프레임_12V"
    others = ["2_겨울빛의문_정문문주", "3_별빛이머무는정원", "4_요정의숲"]
    base = q[k1]["supply"] + sum(q[k]["supply"] for k in others)
    prem = q[k1p]["supply"] + sum(q[k]["supply"] for k in others)
    tear = sum(qx[k]["supply"] for k in others)
    P = []
    if cover:
        P.append(page(f'<img class="full" src="{cover.as_uri()}">', "pg img"))

    # 개요
    cards = ""
    for t in THEMES:
        cards += (f'<div class="card"><img src="img/{files[t["folder"] + "|" + t["hero"]]}">'
                  f'<div class="cb"><div class="cn">{t["no"]} {html.escape(t["name"])}</div>'
                  f'<div class="cw">{html.escape(t["where"])} · {t["kind"]}</div>'
                  f'<div class="cc">{html.escape(t["concept"])}</div></div></div>')
    P.append(page(f'''<div class="intro"><div class="eyebrow">YEONGJU Xi SIGNATURE · WINTER LIGHTING</div>
<h1>빛으로 완성하는 네 가지 겨울 풍경</h1>
<p class="lead">영주자이 시그니처의 랜드마크 동, 정문, 정원, 소나무 숲을 하나의 이야기로 잇는 야간 경관 제안입니다.
상시 경관조명 1곳과 겨울 시즌 장식 3곳으로 구성했습니다.</p>
<div class="cards">{cards}</div></div>'''))

    for t in THEMES:
        P.append(page(f'<img class="full" src="img/{files[t["folder"] + "|" + t["hero"]]}">', "pg img"))
        g = t["gallery"]
        cols = "g3" if len(g) == 3 else "g4"
        tiles = "".join(f'<figure><img src="img/{files[t["folder"] + "|" + s]}"><figcaption>{html.escape(s.rsplit("-", 1)[0] if s[-2:-1] == "-" else s)}</figcaption></figure>' for s in g)
        P.append(page(header(t["no"], t["name"], "다른 시점에서 본 연출") + f'<div class="gal {cols}">{tiles}</div>'))
        items = ""
        for crop, nm, spec, qty in t["items"]:
            vis = f'<img src="img/{crop}.jpg">' if crop else f'<div class="ico">{ICON[nm]}</div>'
            items += f'<div class="it">{vis}<div class="itb"><div class="itn">{html.escape(nm)}</div><div class="its">{html.escape(spec)}</div><div class="itq">{html.escape(qty)}</div></div></div>'
        pts = "".join(f"<li>{html.escape(x)}</li>" for x in t["points"])
        note = f'<p class="note">{html.escape(t["note"])}</p>' if t["note"] else ""
        n = len(t["items"])
        grid = "i3" if n <= 3 else ("i5" if n == 5 else "i6")
        P.append(page(header(t["no"], t["name"], "디자인 계획") + f'''<div class="plan">
<div class="pl"><div class="tag">{t["kind"]}</div><h2>{html.escape(t["name"])}</h2><div class="where">{html.escape(t["where"])}</div>
<p class="concept">{html.escape(t["concept"])}</p><ul>{pts}</ul>{note}</div>
<div class="pr {grid}">{items}</div></div>'''))

    # 105동 시공 방식 (도식)
    svg = ['<svg viewBox="0 0 420 560" class="sch">',
           '<rect x="120" y="40" width="150" height="480" fill="#eef1f4" stroke="#9aa3b2"/>',
           '<rect x="175" y="10" width="60" height="30" fill="#e3e7ec" stroke="#9aa3b2"/>',
           '<text x="195" y="30" font-size="11" fill="#5b6573">옥탑</text>']
    for k in range(27):
        y = 520 - 18 - k * 17.4
        svg.append(f'<line x1="120" y1="{y:.1f}" x2="270" y2="{y:.1f}" stroke="#dfe4ea"/>')
    svg.append('<rect x="120" y="502" width="150" height="18" fill="#d9dee5"/><text x="150" y="515" font-size="10" fill="#5b6573">1층 필로티 · 설치 제외</text>')
    svg.append('<line x1="266" y1="40" x2="266" y2="502" stroke="#e0b25a" stroke-width="7" stroke-linecap="round"/>')
    for k in range(13):
        y = 58 + k * 34
        svg.append(f'<rect x="284" y="{y}" width="16" height="12" rx="2" fill="#1d2430"/><line x1="284" y1="{y + 6}" x2="270" y2="{y + 6}" stroke="#1d2430"/>')
    svg.append('<rect x="290" y="16" width="44" height="22" rx="3" fill="#b8913a"/><text x="296" y="31" font-size="10" fill="#fff">전원함</text>')
    svg.append('<line x1="312" y1="38" x2="312" y2="470" stroke="#1d2430" stroke-dasharray="4 4"/>')
    svg.append('<line x1="96" y1="40" x2="96" y2="520" stroke="#9aa3b2"/><text x="60" y="285" font-size="12" fill="#5b6573" transform="rotate(-90 70 285)">높이 79.3m · 27층</text>')
    svg.append('<text x="318" y="130" font-size="12" fill="#1d2430">전원장치</text><text x="318" y="145" font-size="12" fill="#1d2430">약 6m마다</text>')
    svg.append('<text x="318" y="300" font-size="11" fill="#b8913a">라인바 2.9m 모듈</text><text x="318" y="314" font-size="11" fill="#b8913a">(층고 맞춤)</text>')
    svg.append('</svg>')
    P.append(page(header("①", "하늘에 새긴 빛", "경관바 시공 방식") + f'''<div class="tech"><div class="tl">{"".join(svg)}</div>
<div class="tr"><h2>오래 가도록 설계한 세로 라인</h2><ul class="big">
<li><b>공장 완제품</b> — 12V 정전류 3구 모듈을 알루미늄 케이스에 나사로 고정하고 결선·밀봉·점등 검사까지 마친 상태로 들여옵니다.</li>
<li><b>층고 맞춤 2.9m 모듈</b> — 이음이 층 바닥선과 맞아 눈에 덜 띄고, 승강기 운반과 로프 작업이 안전한 길이입니다.</li>
<li><b>분산 전원</b> — 방수 전원장치를 약 6m(바 2개)마다 두고, 한 줄 병렬 50개 이하로 배선해 아래쪽까지 밝기를 고르게 유지합니다.</li>
<li><b>범용 3구 모듈</b> — 오랫동안 같은 규격 부품을 구할 수 있어 고장 시 모듈 단위로 수리합니다.</li>
<li><b>날씨 대응</b> — 늘어남을 흡수하는 플로팅 커버, 하단 물빠짐 구멍, 영하 30℃ 동작 사양.</li>
<li><b>균일한 색</b> — 3000K 단색, 전량 같은 생산 로트로 위아래 색 차이를 줄입니다.</li>
<li><b>하자보수 3년</b> — 같은 로트 예비 모듈을 보관해 교체 시에도 색을 맞춥니다.</li></ul></div></div>'''))

    # 견적 요약
    def row(nm, desc, t, x, cls=""):
        xs = won(x["supply"]) if x else "—"
        return f'<tr class="{cls}"><td>{nm}</td><td>{desc}</td><td class="n">{won(t["supply"])}</td><td class="n">{won(t["total"])}</td><td class="n">{xs}</td></tr>'
    rows = (row("① 하늘에 새긴 빛 <span class='b'>기본</span>", "105동 측벽 세로 1줄 75.5m · 상시", q[k1], None)
            + row("&nbsp;&nbsp;&nbsp;└ 프리미엄", "측벽 ∩ 프레임 약 160m · 상시", q[k1p], None, "sub")
            + row("② 겨울빛의 문", "정문 문주 · 시즌", q[others[0]], qx[others[0]])
            + row("③ 별빛이 머무는 정원", "잔디 정원 · 시즌", q[others[1]], qx[others[1]])
            + row("④ 요정의 숲", "소나무 숲 · 시즌", q[others[2]], qx[others[2]]))
    P.append(page(header("₩", "견적 요약", "부가세 별도 기준 · 단위 원") + f'''<div class="est"><table>
<tr><th>테마</th><th>내용</th><th class="n">공급가액</th><th class="n">부가세 포함</th><th class="n">철거(선택)</th></tr>{rows}
<tr class="tot"><td colspan="2">합계 — ① 기본안</td><td class="n">{won(base)}</td><td class="n">{won(base + base // 10)}</td><td class="n">{won(tear)}</td></tr>
<tr class="tot2"><td colspan="2">합계 — ① 프리미엄안</td><td class="n">{won(prem)}</td><td class="n">{won(prem + prem // 10)}</td><td class="n">{won(tear)}</td></tr></table>
<ul class="fine"><li>수량은 현장 실측 후 단가 기준으로 정산합니다. 세부 내역은 뒤쪽 부록 견적서를 참고해 주십시오.</li>
<li>1차 전원(가까운 분전반 → 전원함)은 발주처 제공 조건이며, 전기요금·경관심의·인허가는 제외입니다.</li>
<li>시즌 장식(②③④)의 철거는 선택 항목이며, 점등 기간 중 불량 조명은 무상 교체합니다.</li></ul></div>'''))

    # 시공·품질·회사
    reg = (OUT.parent.parent / "00_운영" / "회사서류")
    certs = "".join(f'<img src="{p.as_uri()}">' for p in sorted(reg.glob("*.jpg")))
    P.append(page(header("✓", "시공 · 품질 · 회사", "") + f'''<div class="qa"><div class="qa1">
<h3>시공 일정</h3><p>발주 후 자재 입고 약 3주 → 현장 시공 105동 4일 · 정문 2일 · 정원 1일 · 숲 2일 (기상에 따라 변동)</p>
<h3>시공 원칙</h3><ul><li>석재·유리·SUS 마감 무타공, 수목은 못·스테이플 없이 감기</li><li>기존 경관조명·로고 사인·정원 시설은 그대로 유지</li><li>손이 닿는 1층 필로티 구간은 설치하지 않음</li></ul>
<h3>안전 · 품질</h3><ul><li>로프 작업 안전관리비 반영 (수직구명줄·추락방지·하부 통제)</li><li>전원함 누전차단기·서지보호기, 전 구간 절연저항 시험 후 점등</li><li>하자보수: 경관바·전원장치 3년 / 시즌 장식 점등 기간 무상 교체</li></ul></div>
<div class="qa2"><h3>㈜엣지컴퍼니</h3><p class="co">{LICENSE}<br>한국전기공사협회 회원 제00362호<br>대표 고진식 · ☎ 1533-3210</p><div class="certs">{certs}</div>
<p class="note">전기공사업 면허를 가진 회사가 설계·생산·시공·하자보수를 직접 맡습니다.</p></div></div>'''))

    P.append(page('''<div class="thanks"><div class="eyebrow">YEONGJU Xi SIGNATURE · WINTER LIGHTING</div><h1>감사합니다</h1>
<p>㈜엣지컴퍼니 · 전기공사업 등록 제 울산-00821호 · ☎ 1533-3210</p></div>'''))
    return HTML_HEAD + "".join(P) + "</body></html>"


HTML_HEAD = """<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>영주자이 경관조명 통합 제안서</title><style>
@page { size: 338.67mm 190.5mm; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #fff; }
body { font-family: "Noto Sans KR", "Malgun Gothic", sans-serif; color: #1d2430; }
.pg { width: 1280px; height: 720px; position: relative; overflow: hidden; page-break-after: always; background: #fbfaf7; padding: 44px 56px; }
.pg.img { padding: 0; background: #0b1020; }
.full { width: 100%; height: 100%; object-fit: cover; display: block; }
.eyebrow { font-size: 13px; letter-spacing: 4px; color: #b8913a; }
h1 { font-family: "Noto Serif KR", serif; font-weight: 600; font-size: 40px; margin: 10px 0 12px; }
h2 { font-family: "Noto Serif KR", serif; font-weight: 600; font-size: 28px; margin: 4px 0 6px; }
h3 { font-size: 16px; margin: 16px 0 6px; color: #b8913a; }
.lead { font-size: 16px; line-height: 1.7; color: #4a5563; max-width: 900px; margin: 0 0 22px; }
.cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; }
.card { background: #fff; border: 1px solid #e6e1d6; }
.card img { width: 100%; height: 250px; object-fit: cover; display: block; }
.cb { padding: 12px 14px 14px; }
.cn { font-family: "Noto Serif KR", serif; font-size: 21px; font-weight: 600; }
.cw { font-size: 12px; color: #b8913a; margin: 4px 0 8px; }
.cc { font-size: 14px; line-height: 1.65; color: #4a5563; }
.hd { display: flex; align-items: baseline; gap: 14px; border-bottom: 1px solid #e0d8c6; padding-bottom: 12px; margin-bottom: 20px; }
.hd .no { font-family: "Noto Serif KR", serif; font-size: 28px; color: #b8913a; }
.hd .nm { font-family: "Noto Serif KR", serif; font-size: 26px; font-weight: 600; }
.hd .sub { font-size: 14px; color: #6b7280; }
.hd .brand { margin-left: auto; font-size: 13px; color: #9aa3b2; }
.gal { display: grid; gap: 16px; justify-content: center; }
.gal.g4 { grid-template-columns: 484px 484px; grid-template-rows: 272px 272px; }
.gal.g3 { grid-template-columns: 777px 375px; grid-template-rows: 211px 211px; margin-top: 30px; }
.gal.g3 figure:first-child { grid-row: 1 / 3; }
figure { margin: 0; position: relative; overflow: hidden; background: #0b1020; }
figure img { width: 100%; height: 100%; object-fit: cover; display: block; }
figcaption { position: absolute; left: 0; right: 0; bottom: 0; padding: 8px 12px; font-size: 13px; color: #fff; background: linear-gradient(transparent, rgba(0,0,0,.65)); }
.plan { display: grid; grid-template-columns: 330px 1fr; gap: 30px; height: 560px; }
.tag { display: inline-block; font-size: 12px; color: #fff; background: #b8913a; padding: 2px 10px; border-radius: 2px; }
.where { font-size: 13px; color: #6b7280; margin-bottom: 14px; }
.concept { font-size: 15px; line-height: 1.75; margin: 0 0 14px; }
.pl ul { padding-left: 18px; margin: 0; } .pl li { font-size: 14px; line-height: 1.6; margin: 6px 0; color: #374151; }
.note { font-size: 12px; color: #8a6d2f; margin-top: 12px; }
.pr { display: grid; gap: 14px; align-content: start; }
.pr.i3 { grid-template-columns: repeat(3, 1fr); } .pr.i5 { grid-template-columns: repeat(3, 1fr); } .pr.i6 { grid-template-columns: repeat(3, 1fr); }
.it { background: #fff; border: 1px solid #e6e1d6; display: flex; flex-direction: column; }
.it img, .it .ico { width: 100%; height: 150px; object-fit: cover; display: block; background: #0b1020; }
.pr.i3 .it img, .pr.i3 .it .ico { height: 300px; }
.it .ico { display: flex; align-items: center; justify-content: center; background: #f3efe6; }
.it .ico svg { width: 90px; height: 90px; }
.itb { padding: 10px 12px 12px; }
.itn { font-weight: 700; font-size: 15px; } .its { font-size: 12px; color: #6b7280; line-height: 1.5; margin: 4px 0 6px; }
.itq { font-family: "Noto Serif KR", serif; font-size: 16px; color: #b8913a; font-weight: 600; }
.tech { display: grid; grid-template-columns: 420px 1fr; gap: 40px; height: 560px; }
.sch { width: 440px; height: 580px; margin-top: -10px; }
.big li { font-size: 15px; line-height: 1.7; margin: 8px 0; color: #374151; } .big b { color: #1d2430; }
.est table { width: 100%; border-collapse: collapse; font-size: 15px; background: #fff; }
.est th, .est td { border-bottom: 1px solid #e6e1d6; padding: 11px 12px; text-align: left; }
.est th { background: #f3efe6; font-size: 13px; color: #6b7280; }
.est td.n, .est th.n { text-align: right; white-space: nowrap; }
.est tr.sub td { color: #6b7280; font-size: 14px; }
.est .b { font-size: 11px; color: #fff; background: #b8913a; padding: 1px 6px; border-radius: 2px; margin-left: 6px; }
.est tr.tot td { font-weight: 700; border-top: 2px solid #1d2430; background: #fbf6ea; }
.est tr.tot2 td { font-weight: 700; color: #6b7280; }
.fine { font-size: 13px; color: #6b7280; line-height: 1.7; margin-top: 18px; padding-left: 18px; }
.qa { display: grid; grid-template-columns: 1.15fr 1fr; gap: 40px; }
.qa p, .qa li { font-size: 14px; line-height: 1.65; color: #374151; } .qa ul { padding-left: 18px; margin: 0; }
.co { font-size: 15px !important; }
.certs { display: flex; gap: 14px; margin-top: 10px; } .certs img { height: 250px; border: 1px solid #e6e1d6; }
.thanks { height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; }
.thanks h1 { font-size: 56px; } .thanks p { color: #6b7280; }
</style></head><body>"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    print("1) 사진 수정")
    files = prepare_images()
    print("2) 품목 사진")
    make_crops(files)
    cover = prepare_cover()
    print("3) HTML", "(표지 포함)" if cover else "(표지 없음 — 표지.png 넣으면 맨 앞에 붙음)")
    hp = OUT / "제안서_본문.html"
    hp.write_text(build_html(files, cover), encoding="utf-8")
    body = OUT / "_본문.pdf"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={body}", hp.as_uri()],
                   check=True, capture_output=True, timeout=300)
    print("4) 부록 견적서 병합")
    doc = fitz.open(body)
    qdir = OUT.parent / "견적서"
    for name in ["견적서_1_하늘에새긴빛_1줄_12V.pdf", "견적서_1B_하늘에새긴빛_프레임_12V.pdf", "견적서_2_겨울빛의문_정문문주.pdf",
                 "견적서_3_별빛이머무는정원.pdf", "견적서_4_요정의숲.pdf"]:
        doc.insert_pdf(fitz.open(qdir / name))
    final = OUT / FINAL_NAME
    old = OUT / "영주자이_윈터라이팅_제안서.pdf"
    if old.exists():
        old.unlink()
    doc.save(final, garbage=3, deflate=True)
    doc.close()
    body.unlink()
    print("OK ->", final, "pages", fitz.open(final).page_count, f"{final.stat().st_size / 1e6:.1f}MB")


if __name__ == "__main__":
    main()
