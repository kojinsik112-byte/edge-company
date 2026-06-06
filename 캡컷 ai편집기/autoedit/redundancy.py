"""반복(재촬영 NG) 구간 감지.

같은 말을 다시 한 경우(예: 말이 막혀 다시 녹화), 앞에 나온 것을 잘라내고
마지막에 제대로 말한 것만 남긴다. 연속/근접한 자막들의 텍스트 유사도로 판단한다.
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import List, Set

from .transcribe import Caption

_NORM_RE = re.compile(r"[\s.,!?~…·\"'’”\-]+")


def _norm(text: str) -> str:
    return _NORM_RE.sub("", text)


def find_duplicate_indices(
    captions: List[Caption],
    *,
    ratio: float = 0.75,
    window_s: float = 25.0,
    min_len: int = 6,
) -> Set[int]:
    """반복(재촬영)으로 보이는 '앞쪽' 자막들의 인덱스를 찾는다.

    어떤 자막이 곧이어(window_s 이내) 거의 같은 내용으로 다시 나오면,
    먼저 말한 쪽(NG 테이크)을 버리고 나중 것을 남긴다.
    """
    drop: Set[int] = set()
    norms = [_norm(c.text) for c in captions]
    n = len(captions)
    for i in range(n):
        if i in drop:
            continue
        a = norms[i]
        if len(a) < min_len:
            continue
        for j in range(i + 1, n):
            if captions[j].start - captions[i].start > window_s:
                break
            if j in drop:
                continue
            b = norms[j]
            if len(b) < min_len:
                continue
            similar = (
                SequenceMatcher(None, a, b).ratio() >= ratio
                or a in b
                or (b in a and len(b) >= min_len + 2)
            )
            if similar:
                drop.add(i)  # 먼저 말한 NG 테이크를 버린다
                break
    return drop
