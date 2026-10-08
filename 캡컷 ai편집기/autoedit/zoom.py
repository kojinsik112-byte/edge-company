"""자동 줌인(펀치인) — 강조하는 순간 화면이 살짝 다가갔다가 돌아오는 유튜브식 효과.

대상: 단어 강조(크게·형광펜·빨강)나 효과음이 있는 자막, 또는 사람이 '줌 켬'으로 지정한 자막.
'줌 끔'으로 지정한 자막은 제외. 0.15초에 걸쳐 들어가고 0.25초에 걸쳐 빠진다.
자막은 이 효과 '다음에' 입히므로 글자는 확대되지 않는다.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from .transcribe import Caption

STRONG = ("big", "marker", "red")


def zoom_windows(captions: List[Caption], max_len: float = 3.5) -> List[Tuple[float, float]]:
    from .styles import words_for

    wins: List[Tuple[float, float]] = []
    for c in captions:
        flag = getattr(c, "zoom", None)
        if flag is False:
            continue
        kinds = set((c.emph or {}).values())
        if not (flag is True or kinds & set(STRONG) or c.sfx):
            continue
        start = c.start
        ws = words_for(c)
        idx = sorted(i for i, k in (c.emph or {}).items() if k in STRONG and i < len(ws))
        if idx:
            start = ws[idx[0]].start
        a = max(0.0, start - 0.05)
        b = min(c.end, a + max_len)
        if b - a >= 0.4:
            wins.append((a, b))
    # 붙어 있는 구간은 합친다 (계속 줌 상태 유지)
    wins.sort()
    merged: List[Tuple[float, float]] = []
    for a, b in wins:
        if merged and a - merged[-1][1] < 0.6:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        else:
            merged.append((a, b))
    return merged


def zoom_filter(captions: List[Caption], width: int, height: int, strength: float = 1.08) -> Optional[str]:
    """ffmpeg 필터 문자열 (scale+crop). 줌할 곳이 없으면 None."""
    wins = zoom_windows(captions)
    if not wins:
        return None
    k = strength - 1.0
    ramps = "+".join(
        f"clip((t-{a:.3f})/0.15,0,1)*clip(({b:.3f}-t)/0.25,0,1)" for a, b in wins
    )
    z = f"(1+{k:.3f}*min(1,{ramps}))"
    # 화면을 z배로 키운 뒤 원래 크기로 가운데를 잘라낸다 (매 프레임 계산)
    return (
        f"scale=w='trunc(iw*{z}/2)*2':h='trunc(ih*{z}/2)*2':eval=frame:flags=bicubic,"
        f"crop={width}:{height},setsar=1"
    )
