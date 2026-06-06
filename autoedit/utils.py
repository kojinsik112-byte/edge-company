"""공용 유틸리티 — 로깅, 시간 포맷, 구간 연산."""

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from typing import List, Tuple

logger = logging.getLogger("autoedit")


def setup_logging(verbose: bool = False) -> None:
    """콘솔 로깅을 설정한다."""
    level = logging.DEBUG if verbose else logging.INFO
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)s  %(levelname)-7s %(message)s", "%H:%M:%S"))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(level)


def fmt_timestamp(seconds: float, sep: str = ",") -> str:
    """초 단위를 SRT/ASS 타임스탬프(HH:MM:SS,mmm)로 변환한다."""
    if seconds < 0:
        seconds = 0.0
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def fmt_duration(seconds: float) -> str:
    """사람이 읽기 좋은 길이 표기(예: 1m 23s)."""
    seconds = max(0.0, seconds)
    m, s = divmod(int(round(seconds)), 60)
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


@dataclass
class Segment:
    """시작/끝(초)으로 정의되는 시간 구간."""

    start: float
    end: float

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)


def merge_intervals(intervals: List[Tuple[float, float]], gap: float = 0.0) -> List[Tuple[float, float]]:
    """겹치거나 `gap` 이내로 인접한 구간들을 병합한다."""
    if not intervals:
        return []
    ordered = sorted(intervals, key=lambda x: x[0])
    merged = [list(ordered[0])]
    for start, end in ordered[1:]:
        if start <= merged[-1][1] + gap:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return [(a, b) for a, b in merged]


def invert_intervals(
    intervals: List[Tuple[float, float]], total: float
) -> List[Tuple[float, float]]:
    """[0, total] 범위에서 주어진 구간들의 여집합(보충 구간)을 구한다."""
    keep: List[Tuple[float, float]] = []
    cursor = 0.0
    for start, end in sorted(intervals, key=lambda x: x[0]):
        if start > cursor:
            keep.append((cursor, min(start, total)))
        cursor = max(cursor, end)
        if cursor >= total:
            break
    if cursor < total:
        keep.append((cursor, total))
    return [(a, b) for a, b in keep if b - a > 1e-3]
