"""자막을 '한 칸 = 한 문장'으로 다시 나누기.

음성인식은 숨 쉬는 곳에서 자막을 끊어서, 문장 중간에서 끊기거나 두 문장이 한 칸에 섞인다.
실제 말한 단어 타이밍을 이어 붙인 뒤, 문장이 끝나는 곳(마침표·물음표 또는 '~다/~요' 같은
종결어미 + 잠깐 멈춤)에서 다시 자른다. 너무 긴 문장은 쉼표·멈춤에서 한 번 더 나눈다.

사람이 지정한 단어 강조·위치·정렬·효과음은 그대로 따라간다. 글자는 바꾸지 않는다.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

from .transcribe import Caption, Word

_SENT_END = re.compile(r"[.?!…][\"'”’)\]]*$")
_KO_END = re.compile(r"(다|요|죠|까|네|군|래|자|지|나|니)$")
# 문장 중간에서 끊어도 자연스러운 이음말
_JOIN = re.compile(r"(고|서|며|면|지만|는데|은데|니까|때문에|위해|해서|하고|하며|하면|되면|오셔서|셔서)$")


def _bare(t: str) -> str:
    return re.sub(r"[\"'”’)\]]+$", "", t)


def resegment(
    captions: List[Caption], max_chars: int = 40, min_chars: int = 6
) -> List[Caption]:
    from .styles import words_for

    # (단어, 강조, 이 단어가 원래 자막의 첫 단어면 그 자막)
    items: List[Tuple[Word, Optional[str], Optional[Caption]]] = []
    owner: List[int] = []   # 각 단어가 원래 몇 번째 자막이었는지
    sizes: List[int] = []
    for ci, c in enumerate(captions):
        ws = words_for(c)
        sizes.append(len(ws))
        for k, w in enumerate(ws):
            items.append((w, (c.emph or {}).get(k), c if k == 0 else None))
            owner.append(ci)
    if not items:
        return captions

    out: List[Caption] = []
    cur: List[Tuple[Word, Optional[str], Optional[Caption]]] = []

    def flush() -> None:
        nonlocal cur
        if not cur:
            return
        words = [w for w, _, _ in cur]
        emph: Dict[int, str] = {i: k for i, (_, k, _) in enumerate(cur) if k}
        src = next((c for _, _, c in cur if c is not None), None)
        text = " ".join(w.text for w in words)
        # 원래 자막 한 칸이 통째로 한 문장이면, 사람이 넣은 줄바꿈까지 그대로 살린다
        own = {owner[cur_start + j] for j in range(len(cur))}
        if len(own) == 1 and src is not None and sizes[next(iter(own))] == len(cur):
            text = src.text
        out.append(
            Caption(
                start=words[0].start,
                end=words[-1].end,
                text=text,
                words=words,
                emph=emph or None,  # 비어 있으면 자동 강조 대상
                pos=src.pos if src else None,
                align=src.align if src else None,
                sfx=src.sfx if src else None,
            )
        )
        cur = []

    def gap_after(i: int) -> float:
        """items 기준 i번째 단어 뒤 쉬는 시간."""
        return (items[i + 1][0].start - items[i][0].end) if i + 1 < len(items) else 99.0

    def split_long() -> None:
        """긴 문장: 이음말(~고·~서·~지만·~는데·~때문에…)·쉼표·긴 쉼 중 가운데에 가까운 곳에서 자른다."""
        nonlocal cur
        texts = [x[0].text for x in cur]
        total = len(" ".join(texts))
        best, best_score, acc = None, -1e9, 0
        base = cur_start
        for j in range(len(cur) - 1):
            acc += len(texts[j]) + 1
            t = _bare(texts[j])
            score = 0.0
            if texts[j].endswith(","):
                score += 3
            if _JOIN.search(t):
                score += 2
            score += min(gap_after(base + j), 1.0) * 3
            score -= abs(acc - total / 2) / max(total, 1) * 4  # 가운데에 가까울수록
            if acc >= min_chars and total - acc >= min_chars and score > best_score:
                best, best_score = j, score
        if best is None:
            return
        rest = cur[best + 1:]
        cur = cur[: best + 1]
        flush()
        cur = rest

    cur_start = 0
    for idx, item in enumerate(items):
        if not cur:
            cur_start = idx
        w = item[0]
        cur.append(item)
        gap = gap_after(idx)
        length = len(" ".join(x[0].text for x in cur))
        bare = _bare(w.text)
        # 마침표·물음표가 있으면 문장 끝. 없으면 '~다/~요' 종결어미 + 충분히 쉴 때만
        sentence_end = bool(_SENT_END.search(w.text)) or (bool(_KO_END.search(bare)) and gap > 0.8)
        if sentence_end and length >= min_chars:
            flush()
        elif gap > 1.2 and length >= min_chars:
            flush()
        elif length >= max_chars * 2.2:  # 아주 긴 문장만 이음말·쉼표에서
            before = len(cur)
            split_long()
            if len(cur) == before:  # 자를 곳이 없으면 그냥 여기서
                flush()
            else:
                cur_start = idx - len(cur) + 1
    flush()

    # 너무 짧은 꼬리 조각(예: '네.')은 앞 문장과 붙이지 않고 그대로 둔다 — 말의 리듬 유지
    for i, c in enumerate(out):
        nxt = out[i + 1].start if i + 1 < len(out) else c.end + 0.5
        c.end = max(c.end, min(nxt, c.end + 0.3))
    return out
