"""AI 자동 연출 — '어떤 편집이에요?'에 맞춰 문장 정리·강조·효과음·배경음악을 한 번에.

1) 문장 정리: 한 칸 = 한 문장 (AI 키가 있으면 AI가 문장을 나누고 오타·띄어쓰기·문장부호까지,
   없으면 sentences.resegment 규칙으로)
2) 강조: 숫자·가격·핵심어에 포인트색/크게/형광펜
3) 효과음: 편집 종류에 맞는 소리를 '중요한 문장'에만, 너무 잦지 않게 (최소 4초 간격)
4) 배경음악: 편집 종류에 맞는 분위기

사람이 이미 고른 효과음·강조는 덮어쓰지 않는다(빈 곳만 채움). 전부 되돌리기 가능.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .transcribe import Caption, Word
from .utils import logger


@dataclass(frozen=True)
class Genre:
    key: str
    label: str
    desc: str
    bgm: str                       # bgm.MOODS 키
    sfx_density: float             # 0~1, 효과음을 얼마나 자주
    intro: Optional[str]           # 첫 문장
    outro: Optional[str]           # 끝인사
    number: Optional[str]          # 숫자·스펙
    price: Optional[str]           # 가격·할인·혜택·무료
    question: Optional[str]        # 질문
    exclaim: Optional[str]         # 느낌표·강한 말
    style: str = "pop"             # 어울리는 자막 디자인


GENRES: Dict[str, Genre] = {g.key: g for g in [
    Genre("promo", "제품 홍보", "제품 장점·스펙·가격을 또렷하게", "bright", 0.55,
          "rise", "tada", "ding", "coin", "notify", "pop", "pop"),
    Genre("info", "정보 · 설명", "강의·인터뷰처럼 차분하게, 효과음은 꼭 필요한 곳만", "calm", 0.25,
          None, "correct", "ding", "ding", None, None, "clean"),
    Genre("event", "박람회 · 행사 안내", "혜택·일정·장소를 신나게 알리기", "event", 0.6,
          "tada", "clap", "notify", "coin", "notify", "pop", "box"),
    Genre("fun", "예능 · 숏츠", "리액션 많이, 효과음 자주", "energetic", 0.85,
          "rise", "clap", "ding", "coin", "boing", "pop", "variety"),
    Genre("vlog", "브이로그 · 일상", "가볍고 따뜻하게", "calm", 0.35,
          "sparkle", "clap", None, "coin", "bubble", "pop", "clean"),
    Genre("lux", "고급 · 인테리어 무드", "효과음 최소, 고급스러운 음악", "lux", 0.15,
          "sparkle", None, None, None, None, None, "cinema"),
]}

_NUM = re.compile(r"\d")
_PRICE = re.compile(r"(\d[\d,.]*\s*(원|만원|천원|%|퍼센트)|할인|무료|증정|사은품|혜택|이벤트|공짜|특가)")
_OUTRO = re.compile(r"(감사합니다|고맙습니다|뵙겠습니다|안녕히|구독|좋아요|다음에\s*(또|만나))")
_STRONG = re.compile(r"(!|최초|드디어|무려|진짜|완전|대박|꼭)")


@dataclass
class Plan:
    captions: List[Caption]
    bgm: str
    style: str
    used_ai: bool
    notes: List[str] = field(default_factory=list)


def _first_index(tokens: List[str], pat: re.Pattern) -> Optional[int]:
    for i, t in enumerate(tokens):
        if pat.search(t):
            return i
    return None


def rule_direct(
    captions: List[Caption], genre: Genre, *, do_sfx=True, do_emph=True, vocab: Optional[List[str]] = None
) -> List[Caption]:
    """규칙 기반 연출: 문장 성격(첫인사·숫자·가격·질문·끝인사)을 보고 효과음·강조를 단다."""
    from .styles import auto_emphasis

    if do_emph:
        auto_emphasis(captions, set(vocab or []))
    last_t = -99.0
    outro_done = False
    min_gap = 4.0 + (1 - genre.sfx_density) * 8      # 차분한 편집일수록 드물게
    n = len(captions)
    for i, c in enumerate(captions):
        toks = c.text.split()
        kind: Optional[str] = None
        emph_at: Optional[int] = None
        emph_kind = "big"
        if (i >= n - 3 and _OUTRO.search(c.text)) or i == n - 1:
            if outro_done:
                continue
            kind = genre.outro
            outro_done = True
        elif i == 0:
            kind = genre.intro
        elif _PRICE.search(c.text):
            kind = genre.price
            emph_at = _first_index(toks, _PRICE)
            emph_kind = "marker" if genre.key in ("event", "promo", "fun") else "color"
        elif _NUM.search(c.text):
            kind = genre.number
            emph_at = _first_index(toks, _NUM)
        elif c.text.rstrip().endswith("?"):
            kind = genre.question
        elif _STRONG.search(c.text):
            kind = genre.exclaim
            emph_at = _first_index(toks, _STRONG)
            emph_kind = "red" if genre.key == "fun" else "color"
        if do_emph and emph_at is not None:
            c.emph = dict(c.emph or {})
            if c.emph.get(emph_at) in (None, "color"):
                c.emph[emph_at] = emph_kind
        if do_sfx and kind and not c.sfx:
            is_edge = i in (0, n - 1)
            if is_edge or c.start - last_t >= min_gap:
                c.sfx = kind
                last_t = c.start
    return captions


# ───────────────────────────── AI (Claude) ─────────────────────────────

_SYSTEM = """당신은 한국 최고의 유튜브/숏츠 자막 편집 감독입니다.
음성인식으로 받아 적은 '단어 목록'(번호·글자)을 받습니다. 다음을 해 주세요.

1) sentences: 자막을 '한 칸 = 완결된 한 문장'으로 다시 나눈다. (방송국 자막 기준)
   - 각 칸은 원래 단어 번호 범위(from, to)로 지정한다. 범위는 겹치지 않고 순서대로, 빠짐없이 모든 단어를 덮는다.
   - ★ 한 칸은 반드시 문장이 끝나는 곳에서 끝난다: '~습니다/~요/~죠/~다/~까' 같은 종결어미 + 마침표·물음표·느낌표.
     '~했는데', '~하시고', '~가셔서', '우리 집에'처럼 문장이 이어지는 곳에서는 절대 칸을 나누지 않는다.
     말하는 사람이 '~하시고, ~하신 다음에, ~해 주시면 됩니다'처럼 길게 이어 말하면 그 전체가 한 칸이다.
   - 한 칸은 화면 2줄 분량(약 45자) 안으로. 말하는 사람이 연결어미로 길게 이어 말해서 더 길어지면,
     방송 자막처럼 '뜻은 그대로, 어미만' 바꿔 완결된 문장 여러 개로 나눈다.
     예) '계약도 해 주시고 했는데, 오늘 점검에 가셔서 하자를 잘 판단하신 다음에,'
       → '계약도 해 주셨는데요.' / '오늘 점검에 가셔서 하자를 잘 판단해 주세요.'
     ★ 어떤 칸도 쉼표나 연결어미(~는데, ~하고, ~해서, ~다음에)로 끝나면 안 된다. 모든 칸은 . ? ! 로 끝난다.
   - 조사·어미가 명백히 틀린 곳은 바로잡는다 (예: '우리 집에 하자' → '우리 집의 하자').
   - text 는 그 범위 단어들을 '바르게 고친' 글:
     · 음성인식 오타 교정 (용어 사전·고유명사 힌트를 우선. 예: 영주자인 시그니처 → 영주자이시그니처)
     · 표준 맞춤법 (되서→돼서, 할께요→할게요, 몇일→며칠 등)과 띄어쓰기 (입주시기→입주 시기)
     · 표기 통일 (AS→A/S, 퍼센트→%, 숫자는 아라비아 숫자)
     · 문장부호: 끝은 . ? ! 중 하나, 문장 안 쉼표는 꼭 필요한 곳만
     · 말버릇·더듬은 반복('어', '음', '그', '자', 같은 말 두 번)은 빼도 된다
     말한 내용·어순·말투(존댓말 등)는 바꾸지 않는다. 없던 말을 지어내지 않는다.
   - emphasis: 그 칸에서 시청자가 꼭 봐야 할 단어(제품명·숫자·가격·핵심 장점) 0~2개.
     word 는 고친 text 를 띄어쓰기로 나눈 순번(0부터), kind 는 color(포인트색)/big(크게)/marker(형광펜)/red(경고·반전).
   - sfx: 이 칸에 어울리는 효과음 이름 또는 빈 문자열. 편집 종류에 맞게, 중요한 칸에만(전체의 20~40%), 연달아 넣지 말 것.
2) bgm: 편집 전체에 어울리는 배경음악 분위기 하나.

과장 표현을 새로 만들지 마세요(표시광고법). 원래 말한 내용만 다듬습니다."""


def ai_direct(
    captions: List[Caption], genre: Genre, vocab: List[str], cfg, sfx_names: Dict[str, str], moods: Dict[str, str]
) -> Tuple[List[Caption], str, List[str]]:
    """AI 연출. 실패하면 SmartEditUnavailable."""
    from .smart_edit import SmartEditUnavailable, _resolve_api_key
    from .styles import estimate_words, words_for

    try:
        import anthropic  # type: ignore
        from pydantic import BaseModel  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise SmartEditUnavailable("anthropic 패키지가 필요합니다") from exc
    key = _resolve_api_key(cfg)
    if not key:
        raise SmartEditUnavailable("Anthropic API 키가 없습니다 (api_key.txt)")

    class Emph(BaseModel):
        word: int
        kind: str

    class Sent(BaseModel):
        start_word: int
        end_word: int
        text: str
        emphasis: List[Emph]
        sfx: str

    class Result(BaseModel):
        sentences: List[Sent]
        bgm: str

    words: List[Word] = []
    for c in captions:
        words.extend(words_for(c))
    listing = " ".join(f"[{i}]{w.text}" for i, w in enumerate(words))
    sfx_menu = ", ".join(f"{k}({v})" for k, v in sfx_names.items())
    mood_menu = ", ".join(f"{k}({v})" for k, v in moods.items())
    prompt = (
        f"편집 종류: {genre.label} — {genre.desc}\n"
        f"효과음 목록: {sfx_menu}\n배경음악 분위기 목록: {mood_menu}\n"
        f"용어 사전·고유명사 힌트: {', '.join(vocab or [])}\n\n단어 목록:\n{listing}"
    )
    client = anthropic.Anthropic(api_key=key)
    logger.info("AI 자동 연출 중... (%s, %d단어)", cfg.model, len(words))
    try:
        resp = client.messages.parse(
            model=cfg.model, max_tokens=16000, system=_SYSTEM,
            messages=[{"role": "user", "content": prompt.replace("start_word", "from")}],
            output_format=Result,
        )
    except Exception as exc:  # noqa: BLE001
        raise SmartEditUnavailable(f"AI 호출 실패: {exc}") from exc
    res = resp.parsed_output
    if res is None or not res.sentences:
        raise SmartEditUnavailable("AI 응답을 해석하지 못했습니다")

    out: List[Caption] = []
    n = len(words)
    for s in res.sentences:
        a, b = max(0, s.start_word), min(n - 1, s.end_word)
        if b < a or not s.text.strip():
            continue
        rng = words[a:b + 1]
        text = " ".join(s.text.split())
        toks = text.split()
        cap = Caption(rng[0].start, rng[-1].end, text)
        # 고친 글의 단어 수가 같으면 원래 타이밍 그대로, 다르면 범위 안에서 나눔
        cap.words = [Word(w.start, w.end, t, w.prob) for w, t in zip(rng, toks)] if len(rng) == len(toks) else estimate_words(cap)
        cap.emph = {e.word: e.kind for e in s.emphasis if 0 <= e.word < len(toks) and e.kind in ("color", "big", "marker", "red")}
        cap.sfx = s.sfx if s.sfx in sfx_names else None
        out.append(cap)
    # 원래 자막의 위치·정렬 지정은 시간이 겹치는 첫 칸에 이어 준다
    for c in captions:
        if c.pos or c.align:
            for o in out:
                if o.start <= c.start < o.end + 0.01:
                    o.pos, o.align = o.pos or c.pos, o.align or c.align
                    break
    bgm = res.bgm if res.bgm in moods else genre.bgm
    return out, bgm, [f"AI가 {len(captions)}줄 → {len(out)}문장으로 정리"]


def direct(
    captions: List[Caption],
    genre_key: str,
    *,
    vocab: Optional[List[str]] = None,
    smart_cfg=None,
    tidy: bool = True,
    do_sfx: bool = True,
    do_emph: bool = True,
    try_ai: bool = True,
) -> Plan:
    from .bgm import MOODS
    from .sentences import resegment
    from .sfx import SFX_LIST
    from .smart_edit import SmartEditUnavailable

    genre = GENRES.get(genre_key, GENRES["promo"])
    notes: List[str] = []
    if try_ai and smart_cfg is not None:
        try:
            caps, bgm, n = ai_direct(
                captions, genre, vocab or [], smart_cfg,
                {k: v[0] for k, v in SFX_LIST.items()}, {k: v[0] for k, v in MOODS.items()},
            )
            if not do_sfx:
                for c in caps:
                    c.sfx = None
            if not do_emph:
                for c in caps:
                    c.emph = {}
            return Plan(caps, bgm, genre.style, True, n)
        except SmartEditUnavailable as exc:
            notes.append(f"AI 없이 진행: {exc}")
    caps = resegment(captions) if tidy else [Caption(c.start, c.end, c.text, c.words, c.emph, c.pos, c.align, c.sfx) for c in captions]
    if tidy:
        notes.append(f"{len(captions)}줄 → {len(caps)}문장으로 정리 (규칙)")
    rule_direct(caps, genre, do_sfx=do_sfx, do_emph=do_emph, vocab=vocab)
    return Plan(caps, genre.bgm, genre.style, False, notes)
