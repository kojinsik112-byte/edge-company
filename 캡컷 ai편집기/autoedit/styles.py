"""프리미엄 자막 스타일 엔진.

캡컷/브루 같은 유료 편집기 수준의 '움직이는 자막'을 ASS로 만든다.
- 말을 짧은 구절(한 줄)로 쪼개서 보여주고, 지금 말하는 단어를 색·크기로 강조
- 숫자·핵심 단어는 포인트 색으로 고정 강조 (AI 키워드 선정 가능)
- 구절이 바뀔 때 살짝 떠오르며 나타나는 애니메이션, 네온 글로우, 박스 배경 등

스타일은 STYLES 에 프리셋으로 정의한다. 글꼴이 PC에 없으면 맑은 고딕으로 대체한다.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set

from .transcribe import Caption, Word


# ───────────────────────────── 스타일 프리셋 ─────────────────────────────


@dataclass(frozen=True)
class SubStyle:
    key: str
    label: str
    desc: str
    font: str = "Malgun Gothic"
    bold: bool = True
    size: float = 0.066          # 가로 영상: 화면 높이 대비 글자 크기
    size_v: float = 0.082        # 세로 영상: 화면 폭 대비 글자 크기
    max_chars: int = 18          # 가로 영상 한 구절 최대 글자수
    max_chars_v: int = 10        # 세로 영상 한 구절 최대 글자수
    text: str = "#FFFFFF"        # 기본 글자색
    outline_color: str = "#000000"
    outline: float = 0.10        # 외곽선 두께 (글자 크기 대비)
    shadow: float = 0.0          # 그림자 거리 (글자 크기 대비)
    shadow_color: str = "#000000"
    shadow_alpha: int = 0x60     # 0=불투명, 255=투명
    box: bool = False            # 글자 뒤 박스 배경
    box_color: str = "#000000"
    box_alpha: int = 0x50
    active: Optional[str] = None  # 지금 말하는 단어 색 (None=강조 안 함)
    active_scale: int = 100      # 지금 말하는 단어 확대(%)
    keyword: Optional[str] = None  # 핵심 단어/숫자 강조색
    glow: Optional[str] = None   # 네온 글로우 색
    pop_in: bool = True          # 구절 등장 시 살짝 떠오르기
    fade_ms: int = 0             # 구절 페이드 인/아웃(ms)
    pos: float = 0.085           # 가로 영상: 아래에서부터 위치 (화면 높이 대비)
    pos_v: float = 0.30          # 세로 영상: 아래에서부터 위치 (폰 UI 피함)
    spacing: float = 0.0         # 자간 (글자 크기 대비)
    strip_punct: bool = True     # 마침표·쉼표 숨기기 (캡컷식 깔끔한 자막)
    preview_bg: str = "#2B3440"  # 미리보기 카드 배경


STYLES: Dict[str, SubStyle] = {
    s.key: s
    for s in [
        SubStyle(
            key="pop",
            label="팝",
            desc="지금 말하는 단어가 노랗게 톡 튀어나와요. 숏츠·릴스 1순위",
            font="Black Han Sans",
            bold=False,
            active="#FFE14D",
            active_scale=114,
            keyword="#FFE14D",
            outline=0.11,
            shadow=0.05,
        ),
        SubStyle(
            key="clean",
            label="클린",
            desc="흰 글씨 + 은은한 그림자. 강의·인터뷰·브이로그",
            font="Pretendard",
            size=0.058,
            size_v=0.072,
            max_chars=22,
            max_chars_v=12,
            outline=0.035,
            outline_color="#1A1A1A",
            shadow=0.04,
            shadow_alpha=0x70,
            keyword="#8FE3FF",
            pop_in=False,
            fade_ms=120,
        ),
        SubStyle(
            key="box",
            label="박스",
            desc="반투명 검정 박스 위 흰 글씨. 어떤 배경에서도 또렷",
            font="Pretendard",
            size=0.056,
            size_v=0.070,
            max_chars=22,
            max_chars_v=12,
            box=True,
            box_alpha=0x40,
            outline=0.28,           # 박스 모드에선 외곽선 = 박스 여백
            active="#5CF2C2",
            keyword="#5CF2C2",
        ),
        SubStyle(
            key="variety",
            label="예능",
            desc="노란 굵은 글씨 + 두꺼운 테두리. 예능 자막 느낌",
            font="Black Han Sans",
            bold=False,
            size=0.078,
            size_v=0.095,
            max_chars=14,
            max_chars_v=8,
            text="#FFE600",
            outline_color="#3B1F00",
            outline=0.13,
            shadow=0.09,
            shadow_color="#3B1F00",
            shadow_alpha=0x00,
            active="#FFFFFF",
            active_scale=118,
            keyword="#FF6B3D",
        ),
        SubStyle(
            key="neon",
            label="네온",
            desc="민트빛으로 빛나는 글자. 제품·조명·밤 분위기",
            font="Do Hyeon",
            bold=False,
            outline=0.06,
            outline_color="#04121A",
            glow="#22E3FF",
            active="#B6FFF6",
            active_scale=110,
            keyword="#FF5CF0",
            preview_bg="#0E1726",
        ),
        SubStyle(
            key="edge",
            label="엣지 브랜드",
            desc="엣지 네이비 박스 + 오렌지 포인트. 회사 공식 영상용",
            font="Pretendard",
            size=0.058,
            size_v=0.072,
            max_chars=20,
            max_chars_v=11,
            box=True,
            box_color="#13254A",
            box_alpha=0x10,
            outline=0.30,
            active="#FFA43B",
            keyword="#FFA43B",
        ),
        SubStyle(
            key="cinema",
            label="시네마",
            desc="작고 넓은 자간, 천천히 페이드. 감성·제품 무드",
            font="Pretendard",
            bold=False,
            size=0.046,
            size_v=0.058,
            max_chars=26,
            max_chars_v=14,
            outline=0.0,
            shadow=0.05,
            shadow_alpha=0x40,
            spacing=0.08,
            pop_in=False,
            fade_ms=300,
            pos=0.07,
        ),
    ]
}

DEFAULT_STYLE = "pop"


def get_style(key: Optional[str]) -> SubStyle:
    return STYLES.get(key or DEFAULT_STYLE, STYLES[DEFAULT_STYLE])


# ───────────────────────────── 글꼴 ─────────────────────────────

# 글꼴 이름 → 파일명(들). assets/fonts 또는 윈도우 글꼴 폴더에 있으면 사용.
FONT_FILES: Dict[str, Sequence[str]] = {
    "Black Han Sans": ("BlackHanSans-Regular.ttf",),
    "Do Hyeon": ("DoHyeon-Regular.ttf",),
    "Jua": ("Jua-Regular.ttf",),
    "Pretendard": ("Pretendard-Bold.otf", "Pretendard-Regular.otf", "PretendardVariable.ttf"),
    "Malgun Gothic": ("malgun.ttf", "malgunbd.ttf"),
}
FALLBACK_FONT = "Malgun Gothic"


def fonts_dir() -> Path:
    """동봉 글꼴 폴더 (캡컷 ai편집기/assets/fonts)."""
    return Path(__file__).resolve().parent.parent / "assets" / "fonts"


def _font_dirs() -> List[Path]:
    dirs = [fonts_dir()]
    windir = os.environ.get("WINDIR")
    if windir:
        dirs.append(Path(windir) / "Fonts")
    local = os.environ.get("LOCALAPPDATA")
    if local:
        dirs.append(Path(local) / "Microsoft" / "Windows" / "Fonts")
    return dirs


def font_available(name: str) -> bool:
    files = FONT_FILES.get(name)
    if not files:
        return True  # 모르는 글꼴은 시스템에 맡김
    return any((d / f).exists() for d in _font_dirs() for f in files)


def resolve_font(style: SubStyle) -> SubStyle:
    """원하는 글꼴이 없으면 맑은 고딕(굵게)으로 바꾼다."""
    if font_available(style.font):
        return style
    return replace(style, font=FALLBACK_FONT, bold=True)


# ───────────────────────────── 색/시간 유틸 ─────────────────────────────


def ass_color(hex_color: str, alpha: int = 0) -> str:
    """'#RRGGBB' → ASS '&HAABBGGRR'."""
    h = hex_color.lstrip("#")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H{alpha:02X}{b}{g}{r}".upper().replace("&H", "&H", 1)


def _c(hex_color: str) -> str:
    """인라인 색 태그용 '&HBBGGRR&'."""
    h = hex_color.lstrip("#")
    return f"&H{h[4:6]}{h[2:4]}{h[0:2]}&".upper()


def _t(seconds: float) -> str:
    if seconds < 0:
        seconds = 0.0
    cs = int(round(seconds * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def _esc(text: str) -> str:
    return text.replace("\\", "＼").replace("{", "(").replace("}", ")").replace("\n", " ")


# ───────────────────────────── 단어·구절 ─────────────────────────────

_PUNCT_TAIL = re.compile(r"[.,…·]+$")
_SENT_END = re.compile(r"[.?!…]$")
_NUMERIC = re.compile(r"\d")

EMPHASIS = {
    "color": "포인트색",
    "big": "크게",
    "marker": "형광펜",
    "red": "빨강",
}
MARKER_COLOR = "#FFE14D"
RED_COLOR = "#FF4B4B"
POSITIONS = ("bottom", "middle", "top")
ALIGNS = ("left", "center", "right")


def tokens_of(text: str) -> List[str]:
    """자막 글자를 단어(띄어쓰기 단위)로 나눈다. 줄바꿈도 단어 경계."""
    return text.split()


def line_breaks_of(text: str) -> Set[int]:
    """사람이 Enter로 넣은 줄바꿈 위치 = '이 번호 단어 뒤에서 줄바꿈'."""
    breaks: Set[int] = set()
    count = 0
    lines = [ln for ln in text.split("\n") if ln.strip()]
    for ln in lines[:-1]:
        count += len(ln.split())
        breaks.add(count - 1)
    return breaks


def estimate_words(cap: Caption) -> List[Word]:
    """단어 타임스탬프가 없으면 글자 수 비율로 나눠 추정한다."""
    tokens = tokens_of(cap.text)
    if not tokens:
        return []
    dur = max(0.05, cap.end - cap.start)
    weights = [max(1, len(t)) for t in tokens]
    total = sum(weights)
    out: List[Word] = []
    t = cap.start
    for tok, w in zip(tokens, weights):
        d = dur * w / total
        out.append(Word(start=t, end=t + d, text=tok))
        t += d
    return out


def words_for(cap: Caption) -> List[Word]:
    """자막 글자와 1:1로 맞는 단어 목록 (사람이 글자를 고쳐도 타이밍 유지).

    - 단어 수가 같으면(오타·띄어쓰기 일부 수정) 원래 타이밍에 새 글자를 얹는다.
    - 단어 수가 달라졌으면 글자 수 비율로 다시 나눈다.
    """
    tokens = tokens_of(cap.text)
    if cap.words and len(cap.words) == len(tokens):
        # 사람이 자막 시작/끝 시간을 조절했으면 단어 타이밍도 그 범위 안으로 맞춘다
        out = []
        for w, tok in zip(cap.words, tokens):
            s = min(max(w.start, cap.start), cap.end)
            e = min(max(w.end, s), cap.end)
            out.append(Word(s, e, tok, w.prob))
        return out
    return estimate_words(cap)


def auto_emphasis(captions: List[Caption], keywords: Optional[Set[str]] = None) -> None:
    """숫자·핵심 단어에 '포인트색' 강조를 자동으로 붙인다 (사람이 나중에 바꿀 수 있음).

    이미 강조가 지정된 자막(emph 가 None 이 아님)은 건드리지 않는다.
    """
    kw = {k.strip() for k in (keywords or set()) if len(k.strip()) >= 2}
    for cap in captions:
        if cap.emph is not None:
            continue
        emph: Dict[int, str] = {}
        for i, tok in enumerate(tokens_of(cap.text)):
            bare = _PUNCT_TAIL.sub("", tok)
            if _NUMERIC.search(bare) or any(k in bare for k in kw):
                emph[i] = "color"
            if len(emph) >= 2:
                break
        cap.emph = emph


@dataclass
class Phrase:
    words: List[Word]
    start: float
    end: float
    emph: Dict[int, str]
    breaks: Set[int]
    pos: Optional[str]
    align: Optional[str]


def make_phrases(captions: List[Caption], max_chars: int) -> List[Phrase]:
    """자막을 화면에 띄울 구절로 나눈다.

    - 사람이 줄바꿈(Enter)을 넣은 자막 → 사람이 정한 모양 그대로 한 화면에
    - 그 외 → 한 줄짜리 짧은 구절로 자동 분할 (캡컷식)
    """
    phrases: List[Phrase] = []
    for cap in captions:
        words = words_for(cap)
        if not words:
            continue
        emph = dict(cap.emph or {})
        if "\n" in cap.text.strip():
            phrases.append(
                Phrase(words, words[0].start, words[-1].end, emph,
                       line_breaks_of(cap.text), cap.pos, cap.align)
            )
            continue

        cur: List[int] = []
        n = 0

        def flush() -> None:
            nonlocal cur, n
            if cur:
                ws = [words[i] for i in cur]
                local = {k - cur[0]: v for k, v in emph.items() if k in cur}
                phrases.append(Phrase(ws, ws[0].start, ws[-1].end, local, set(), cap.pos, cap.align))
            cur, n = [], 0

        for i, w in enumerate(words):
            L = len(w.text)
            gap = (w.start - words[cur[-1]].end) if cur else 0.0
            if cur and (n + 1 + L > max_chars or gap > 0.7):
                flush()
            cur.append(i)
            n += L + (1 if n else 0)
            if _SENT_END.search(w.text) and n >= max_chars * 0.4:
                flush()
        flush()

    # 표시 시간: 다음 구절 시작 전까지(최대 0.6초 여유), 너무 짧으면 늘림
    for i, ph in enumerate(phrases):
        nxt = phrases[i + 1].start if i + 1 < len(phrases) else ph.end + 0.6
        ph.end = max(ph.end, min(nxt, ph.end + 0.6))
        if ph.end - ph.start < 0.35:
            ph.end = ph.start + 0.35 if nxt <= ph.start + 0.35 else ph.start + 0.35
    return phrases


# ───────────────────────────── ASS 생성 ─────────────────────────────


@dataclass
class Layout:
    """화면 전체 자막 배치 기본값 (자막마다 따로 지정하면 그게 우선)."""

    pos: str = "bottom"       # bottom / middle / top
    align: str = "center"     # left / center / right
    scale: int = 100          # 글자 크기 (%)
    offset: float = 0.0       # 위아래 미세조정 (화면 높이 %, +면 위로)

    @classmethod
    def from_dict(cls, d: Optional[dict]) -> "Layout":
        d = d or {}
        return cls(
            pos=d.get("pos") if d.get("pos") in POSITIONS else "bottom",
            align=d.get("align") if d.get("align") in ALIGNS else "center",
            scale=int(d.get("scale") or 100),
            offset=float(d.get("offset") or 0.0),
        )


def _render_text(
    ph: Phrase,
    st: SubStyle,
    active: Optional[int],
    *,
    mode: str = "main",  # main / glow / marker
    outline: float = 0.0,
) -> str:
    """구절 → ASS 텍스트. 지금 말하는 단어·강조 단어에 태그를 붙인다."""
    base = _c(st.text)
    accent = st.keyword or MARKER_COLOR
    parts: List[str] = []
    for i, w in enumerate(ph.words):
        text = w.text
        if st.strip_punct:
            text = _PUNCT_TAIL.sub("", text) or text
        text = _esc(text)
        kind = ph.emph.get(i)
        is_active = active is not None and i == active and bool(st.active)

        # 크기 태그는 모든 레이어가 똑같이 써야 형광펜 박스와 글자가 정확히 겹친다.
        scale = 130 if kind == "big" else 100
        target = scale
        if is_active and st.active_scale != 100:
            target = int(scale * st.active_scale / 100)
        size_tag = f"\\fscx{scale}\\fscy{scale}"
        if target != scale:
            size_tag += f"\\t(0,90,\\fscx{target}\\fscy{target})"
        reset = "\\fscx100\\fscy100"

        if mode == "glow":
            parts.append(f"{{{size_tag}}}{text}{{{reset}}}")
            continue
        if mode == "marker":
            if kind == "marker" and not st.box:
                parts.append(f"{{{size_tag}\\3a&H00&}}{text}{{{reset}\\3a&HFF&}}")
            else:
                parts.append(f"{{{size_tag}}}{text}{{{reset}}}")
            continue

        color = None
        extra = ""
        undo = ""
        if kind == "color" or kind == "big":
            color = accent
        elif kind == "red":
            color = RED_COLOR
        elif kind == "marker":
            if st.box:
                color = MARKER_COLOR
            else:
                color = "#111111"
                extra, undo = "\\bord0\\shad0", f"\\bord{outline:.1f}\\shad{st.shadow:.2f}"
        if is_active:
            color = "#111111" if kind == "marker" and not st.box else st.active
        tags = size_tag + (f"\\c{_c(color)}" if color else "") + extra
        parts.append(f"{{{tags}}}{text}{{{reset}\\c{base}{undo}}}")

    out = ""
    for i, p in enumerate(parts):
        out += p
        if i < len(parts) - 1:
            out += "\\N" if i in ph.breaks else " "
    return out


def _an(pos: str, align: str) -> int:
    row = {"bottom": 0, "middle": 3, "top": 6}[pos]
    col = {"left": 1, "center": 2, "right": 3}[align]
    return row + col


def build_ass(
    captions: List[Caption],
    style_key: Optional[str],
    width: int,
    height: int,
    *,
    keywords: Optional[Set[str]] = None,
    layout: Optional[Layout] = None,
) -> str:
    """자막 → 완성된 ASS 문서 문자열."""
    lay = layout or Layout()
    st = resolve_font(get_style(style_key))
    vertical = height > width
    fs = int(round((width * st.size_v) if vertical else (height * st.size)) * lay.scale / 100)
    max_chars = st.max_chars_v if vertical else st.max_chars
    if lay.scale != 100:
        max_chars = max(5, int(max_chars * 100 / lay.scale))
    margin_v = int(round(height * (st.pos_v if vertical else st.pos)))
    margin_lr = max(20, int(width * 0.06))
    outline = max(0.0, fs * st.outline)
    shadow = max(0.0, fs * st.shadow)
    st = replace(st, shadow=shadow)  # _render_text 가 복원할 때 쓰는 실제 픽셀값
    spacing = fs * st.spacing

    # 자동 강조(숫자·AI 키워드)는 사람이 아무 강조도 안 건드린 자막에만
    caps = [replace(c) for c in captions]
    auto_emphasis(caps, keywords)

    if st.box:
        # BorderStyle 4 = 줄 전체를 하나의 박스로 (단어별 색 바꿔도 박스가 안 끊김)
        border_style = 4
        outline_col = ass_color(st.box_color, 0xFF)  # 글자 테두리는 숨기고 박스만
        back_col = ass_color(st.box_color, st.box_alpha)
    else:
        border_style = 1
        outline_col = ass_color(st.outline_color)
        back_col = ass_color(st.shadow_color, st.shadow_alpha)

    bold = -1 if st.bold else 0
    header = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        "WrapStyle: 0\n"
        "ScaledBorderAndShadow: yes\n"
        "YCbCr Matrix: TV.709\n"
        f"PlayResX: {width}\n"
        f"PlayResY: {height}\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, "
        "Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
        "MarginR, MarginV, Encoding\n"
        f"Style: Main,{st.font},{fs},{ass_color(st.text)},{ass_color(st.text)},{outline_col},"
        f"{back_col},{bold},0,0,0,100,100,{spacing:.1f},0,{border_style},"
        f"{outline:.1f},{shadow:.1f},2,{margin_lr},{margin_lr},{margin_v},1\n"
        # 형광펜: 글자는 투명, 단어 뒤 박스만 노랗게 (강조 단어만 \3a 로 보이게)
        f"Style: Marker,{st.font},{fs},{ass_color('#000000', 0xFF)},{ass_color('#000000', 0xFF)},"
        f"{ass_color(MARKER_COLOR, 0xFF)},{ass_color('#000000', 0xFF)},{bold},0,0,0,100,100,"
        f"{spacing:.1f},0,3,{fs * 0.14:.1f},0,2,{margin_lr},{margin_lr},{margin_v},1\n"
    )
    if st.glow:
        header += (
            f"Style: Glow,{st.font},{fs},{ass_color(st.glow, 0xFF)},{ass_color(st.glow, 0xFF)},"
            f"{ass_color(st.glow, 0x30)},{ass_color(st.glow, 0xFF)},{bold},0,0,0,"
            f"100,100,{spacing:.1f},0,1,{fs * 0.16:.1f},0,2,{margin_lr},{margin_lr},{margin_v},1\n"
        )
    header += (
        "\n[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )

    rise = max(6, int(fs * 0.18))
    off = int(height * lay.offset / 100)
    lines: List[str] = [header]
    for ph in make_phrases(caps, max_chars):
        pos = ph.pos if ph.pos in POSITIONS else lay.pos
        align = ph.align if ph.align in ALIGNS else lay.align
        an = _an(pos, align)
        x = {"left": margin_lr, "center": width // 2, "right": width - margin_lr}[align]
        y = {
            "bottom": height - margin_v,
            "middle": height // 2,
            "top": int(height * 0.08) if not vertical else int(height * 0.16),
        }[pos] - off

        if st.active:
            segs = []
            for i, w in enumerate(ph.words):
                s = ph.start if i == 0 else w.start
                e = ph.words[i + 1].start if i + 1 < len(ph.words) else ph.end
                if e - s >= 0.02:
                    segs.append((s, e, i))
            if not segs:
                segs = [(ph.start, ph.end, None)]
        else:
            segs = [(ph.start, ph.end, None)]

        has_marker = any(v == "marker" for v in ph.emph.values()) and not st.box
        for k, (s, e, active) in enumerate(segs):
            first = k == 0
            last = k == len(segs) - 1
            lead = f"\\an{an}"
            if st.pop_in and first:
                lead += f"\\move({x},{y + rise},{x},{y},0,120)\\alpha&HFF&\\t(0,90,\\alpha&H00&)"
            else:
                lead += f"\\pos({x},{y})"
            if st.fade_ms and (first or last):
                lead += f"\\fad({st.fade_ms if first else 0},{st.fade_ms if last else 0})"
            body = _render_text(ph, st, active, outline=outline)
            lines.append(f"Dialogue: 2,{_t(s)},{_t(e)},Main,,0,0,0,,{{{lead}}}{body}\n")
            if has_marker:
                mlead = lead.replace("\\alpha&HFF&\\t(0,90,\\alpha&H00&)", "")
                mbody = _render_text(ph, st, active, mode="marker")
                lines.append(
                    f"Dialogue: 1,{_t(s)},{_t(e)},Marker,,0,0,0,,{{{mlead}\\3a&HFF&}}{mbody}\n"
                )
            if st.glow:
                gbody = _render_text(ph, st, active, mode="glow")
                lines.append(
                    f"Dialogue: 0,{_t(s)},{_t(e)},Glow,,0,0,0,,{{{lead}\\blur{max(4, fs // 9)}}}{gbody}\n"
                )
    return "".join(lines)


def write_styled_ass(
    captions: List[Caption],
    out_path: Path,
    style_key: Optional[str],
    width: int,
    height: int,
    *,
    keywords: Optional[Set[str]] = None,
    layout: Optional[Layout] = None,
) -> Path:
    out_path.write_text(
        build_ass(captions, style_key, width, height, keywords=keywords, layout=layout),
        encoding="utf-8",
    )
    return out_path


def sample_captions(text: str = "아크로 슬림 실링팬 소음은 단 24dB 입니다") -> List[Caption]:
    """미리보기용 예시 자막 (단어가 차례로 강조되도록 3초짜리)."""
    cap = Caption(start=0.0, end=3.0, text=text)
    cap.words = estimate_words(cap)
    return [cap]
