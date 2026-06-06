"""추임새(filler) 제거.

"어", "음", "아" 같은 의미 없는 추임새만으로 이루어진 자막 구간을 찾아내
① 영상에서 해당 시간대를 잘라내고 ② 자막에서도 제거한다.
의미 있는 단어("그", "저", "아니" 등)는 건드리지 않도록 보수적으로 판정한다.
"""

from __future__ import annotations

import re
from typing import List, Tuple

from .transcribe import Caption
from .utils import merge_intervals

# 추임새로 취급할 글자들 (이 글자들로만 이루어진 짧은 발화 = 추임새)
FILLER_CHARS = set("어아음으흠엄에웅오")

# 문장부호/공백 제거용
_STRIP_RE = re.compile(r"[\s.,!?~…·\-\"'’”]+")


def is_filler(text: str) -> bool:
    """자막 한 토막이 추임새만으로 이루어졌는지 판정한다.

    예) "어", "음...", "어어", "아" → True
        "아니요", "그래서", "저는" → False (실제 단어 포함)
    """
    cleaned = _STRIP_RE.sub("", text)
    if not cleaned:
        return False
    if len(cleaned) > 4:  # 너무 길면 실제 발화로 간주
        return False
    return all(ch in FILLER_CHARS for ch in cleaned)


def find_filler_ranges(
    captions: List[Caption], pad: float = 0.05
) -> List[Tuple[float, float]]:
    """추임새 자막들의 시간 구간 목록을 반환한다."""
    ranges = [
        (max(0.0, c.start - pad), c.end + pad)
        for c in captions
        if is_filler(c.text)
    ]
    return merge_intervals(ranges)


def _shift(t: float, removed: List[Tuple[float, float]]) -> float:
    """제거된 구간들을 고려해 시간 t를 새 타임라인으로 옮긴다."""
    offset = 0.0
    for s, e in removed:
        if e <= t:
            offset += e - s
        elif s < t < e:
            offset += t - s  # (유지되는 자막은 보통 여기에 안 걸림)
        else:
            break
    return max(0.0, t - offset)


def remap_captions(
    captions: List[Caption], removed: List[Tuple[float, float]]
) -> List[Caption]:
    """추임새 자막을 빼고, 남은 자막들의 시간을 새 타임라인에 맞게 당긴다."""
    removed = merge_intervals(removed)
    out: List[Caption] = []
    for c in captions:
        if is_filler(c.text):
            continue
        out.append(
            Caption(
                start=_shift(c.start, removed),
                end=_shift(c.end, removed),
                text=c.text,
            )
        )
    return out
